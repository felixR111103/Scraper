"""Small Supabase REST client for storing scraper results.

The secret key stays in .env and is never sent to the browser or logged.
"""

from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable

import requests

if TYPE_CHECKING:
    from scraper import Book


class SupabaseError(RuntimeError):
    """Raised for invalid configuration or a failed Supabase request."""


def load_env_file(path: Path = Path(".env")) -> None:
    """Load simple KEY=VALUE entries without overwriting existing environment values."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if name:
            os.environ.setdefault(name, value)


def chunks(items: list[dict[str, Any]], size: int = 200) -> Iterable[list[dict[str, Any]]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]


class SupabaseStore:
    def __init__(self, url: str, key: str, timeout: float = 30.0) -> None:
        if not url or not key:
            raise SupabaseError("SUPABASE_URL and SUPABASE_SECRET_KEY are required")
        if key.startswith("sb_publishable_"):
            raise SupabaseError(
                "A publishable key cannot upload scraper data. Use the server-side secret key."
            )
        self.base_url = url.rstrip("/") + "/rest/v1"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "apikey": key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "nova-sbe-books-scraper/1.0",
            }
        )
        # Legacy service_role keys are JWTs and also use the Bearer header.
        # New sb_secret_ keys must be sent only through the apikey header.
        if key.startswith("eyJ"):
            self.session.headers["Authorization"] = f"Bearer {key}"

    @classmethod
    def from_env(cls, env_file: Path = Path(".env")) -> "SupabaseStore":
        load_env_file(env_file)
        url = os.environ.get("SUPABASE_URL", "").strip()
        key = (
            os.environ.get("SUPABASE_SECRET_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_KEY")
            or ""
        ).strip()
        if not url or not key:
            raise SupabaseError(
                "Save SUPABASE_URL and SUPABASE_SECRET_KEY in .env before using --supabase"
            )
        return cls(url, key)

    def request(
        self,
        method: str,
        resource: str,
        *,
        params: dict[str, str] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        response = self.session.request(
            method,
            f"{self.base_url}/{resource.lstrip('/')}",
            params=params,
            json=json,
            headers=headers,
            timeout=self.timeout,
        )
        if not response.ok:
            message = response.text[:500]
            if response.status_code == 404 and "schema cache" in message.lower():
                message += " Run supabase/schema.sql in the Supabase SQL Editor first."
            raise SupabaseError(f"Supabase returned HTTP {response.status_code}: {message}")
        if not response.content:
            return None
        return response.json()

    def check_schema(self) -> None:
        self.request("GET", "categories", params={"select": "id", "limit": "1"})
        self.request("GET", "scrape_runs", params={"select": "id", "limit": "1"})

    def upsert_many(
        self, table: str, records: list[dict[str, Any]], conflict_column: str
    ) -> list[dict[str, Any]]:
        returned: list[dict[str, Any]] = []
        for batch in chunks(records):
            result = self.request(
                "POST",
                table,
                params={"on_conflict": conflict_column},
                json=batch,
                headers={"Prefer": "resolution=merge-duplicates,return=representation"},
            )
            returned.extend(result or [])
        return returned

    def upload_books(
        self,
        books: list[Book],
        *,
        max_books: int | None = None,
        max_pages: int | None = None,
    ) -> str:
        """Upsert book metadata and append one observation for every book."""
        self.check_schema()
        run = self.request(
            "POST",
            "scrape_runs",
            json={
                "status": "running",
                "requested_max_books": max_books,
                "requested_max_pages": max_pages,
            },
            headers={"Prefer": "return=representation"},
        )[0]
        run_id = run["id"]

        try:
            categories = self.upsert_many(
                "categories", [{"name": name} for name in sorted({b.category for b in books})], "name"
            )
            category_ids = {row["name"]: row["id"] for row in categories}

            book_rows = [
                {
                    "upc": book.upc,
                    "category_id": category_ids[book.category],
                    "title": book.title,
                    "description": book.description,
                    "product_url": book.product_url,
                    "image_url": book.image_url,
                }
                for book in books
            ]
            stored_books = self.upsert_many("books", book_rows, "upc")
            book_ids = {row["upc"]: row["id"] for row in stored_books}

            observations = []
            for book in books:
                record = asdict(book)
                observations.append(
                    {
                        "book_id": book_ids[book.upc],
                        "scrape_run_id": run_id,
                        "scraped_at": record["scraped_at"],
                        "price_excl_tax_gbp": record["price_excl_tax_gbp"],
                        "price_incl_tax_gbp": record["price_incl_tax_gbp"],
                        "tax_gbp": record["tax_gbp"],
                        "availability_text": record["availability_text"],
                        "stock_count": record["stock_count"],
                        "rating": record["rating"],
                        "number_of_reviews": record["number_of_reviews"],
                    }
                )
            for batch in chunks(observations):
                self.request(
                    "POST",
                    "book_observations",
                    json=batch,
                    headers={"Prefer": "return=minimal"},
                )

            self.request(
                "PATCH",
                "scrape_runs",
                params={"id": f"eq.{run_id}"},
                json={
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "books_found": len(books),
                },
                headers={"Prefer": "return=minimal"},
            )
        except Exception as error:
            try:
                self.request(
                    "PATCH",
                    "scrape_runs",
                    params={"id": f"eq.{run_id}"},
                    json={
                        "status": "failed",
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                        "books_found": 0,
                        "error_message": str(error)[:1000],
                    },
                    headers={"Prefer": "return=minimal"},
                )
            except SupabaseError:
                pass
            raise
        return run_id

