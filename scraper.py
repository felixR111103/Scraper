#!/usr/bin/env python3
"""Standalone scraper for https://books.toscrape.com/.

Examples:
    python scraper.py --max-books 5 --output data/sample_5.json
    python scraper.py --max-pages 3 --output data/three_pages.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://books.toscrape.com/"
RATING_VALUES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
USER_AGENT = "nova-sbe-ai-fundamentals-books-scraper/1.0 (educational project)"


@dataclass(frozen=True)
class Book:
    upc: str
    title: str
    category: str
    description: str | None
    rating: int
    price_excl_tax_gbp: str
    price_incl_tax_gbp: str
    tax_gbp: str
    availability_text: str
    stock_count: int
    number_of_reviews: int
    product_url: str
    image_url: str
    scraped_at: str


class ScrapeError(RuntimeError):
    """Raised when a page does not contain the expected data."""


def clean_money(value: str) -> str:
    """Return a normalized decimal string from a pound-denominated value."""
    match = re.search(r"\d+(?:\.\d+)?", value.replace(",", ""))
    if not match:
        raise ScrapeError(f"Could not parse money value: {value!r}")
    return f"{Decimal(match.group()):.2f}"


def parse_stock_count(value: str) -> int:
    match = re.search(r"\((\d+)\s+available\)", value)
    return int(match.group(1)) if match else 0


def require_text(node: Tag | None, field: str) -> str:
    if node is None:
        raise ScrapeError(f"Missing required field: {field}")
    return node.get_text(" ", strip=True)


def parse_catalogue_page(html: str, page_url: str) -> tuple[list[str], str | None]:
    """Extract product URLs and the optional next-page URL."""
    soup = BeautifulSoup(html, "html.parser")
    product_urls = [
        urljoin(page_url, anchor["href"])
        for anchor in soup.select("article.product_pod h3 a[href]")
    ]
    next_anchor = soup.select_one("li.next a[href]")
    next_url = urljoin(page_url, next_anchor["href"]) if next_anchor else None
    return product_urls, next_url


def parse_book_page(html: str, product_url: str, scraped_at: str | None = None) -> Book:
    """Parse one product detail page into a validated Book record."""
    soup = BeautifulSoup(html, "html.parser")
    table: dict[str, str] = {}
    for row in soup.select("table.table.table-striped tr"):
        key = require_text(row.select_one("th"), "product information key")
        value = require_text(row.select_one("td"), f"product information value for {key}")
        table[key] = value

    title = require_text(soup.select_one("div.product_main h1"), "title")
    category_crumbs = soup.select("ul.breadcrumb li a")
    if not category_crumbs:
        raise ScrapeError("Missing required field: category")
    category = category_crumbs[-1].get_text(" ", strip=True)

    rating_node = soup.select_one("div.product_main p.star-rating")
    rating = 0
    if rating_node:
        rating = next(
            (number for name, number in RATING_VALUES.items() if name in rating_node.get("class", [])),
            0,
        )

    description_heading = soup.find(id="product_description")
    description_node = description_heading.find_next_sibling("p") if description_heading else None
    description = description_node.get_text(" ", strip=True) if description_node else None

    image = soup.select_one("div.item.active img[src]")
    if image is None:
        raise ScrapeError("Missing required field: image_url")

    required_table_fields = {
        "UPC",
        "Price (excl. tax)",
        "Price (incl. tax)",
        "Tax",
        "Availability",
        "Number of reviews",
    }
    missing = required_table_fields - table.keys()
    if missing:
        raise ScrapeError(f"Missing product information fields: {sorted(missing)}")

    return Book(
        upc=table["UPC"],
        title=title,
        category=category,
        description=description,
        rating=rating,
        price_excl_tax_gbp=clean_money(table["Price (excl. tax)"]),
        price_incl_tax_gbp=clean_money(table["Price (incl. tax)"]),
        tax_gbp=clean_money(table["Tax"]),
        availability_text=table["Availability"],
        stock_count=parse_stock_count(table["Availability"]),
        number_of_reviews=int(table["Number of reviews"]),
        product_url=product_url,
        image_url=urljoin(product_url, image["src"]),
        scraped_at=scraped_at or datetime.now(timezone.utc).isoformat(),
    )


class BooksScraper:
    def __init__(self, delay: float = 0.25, timeout: float = 20.0) -> None:
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def fetch(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def scrape(self, max_books: int | None = None, max_pages: int | None = None) -> list[Book]:
        books: list[Book] = []
        page_url: str | None = BASE_URL
        page_number = 0

        while page_url and (max_pages is None or page_number < max_pages):
            page_number += 1
            logging.info("Fetching catalogue page %d: %s", page_number, page_url)
            product_urls, next_url = parse_catalogue_page(self.fetch(page_url), page_url)

            for product_url in product_urls:
                if max_books is not None and len(books) >= max_books:
                    return books
                if self.delay:
                    time.sleep(self.delay)
                logging.info("Fetching book %d: %s", len(books) + 1, product_url)
                books.append(parse_book_page(self.fetch(product_url), product_url))

            page_url = next_url
            if page_url and self.delay:
                time.sleep(self.delay)

        return books


def write_books(books: Iterable[Book], output: Path) -> int:
    records = sorted((asdict(book) for book in books), key=lambda record: record["title"].casefold())
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.suffix.lower() == ".csv":
        if not records:
            raise ValueError("Cannot write an empty CSV without column information")
        with output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
    elif output.suffix.lower() == ".jsonl":
        with output.open("w", encoding="utf-8") as file:
            for record in records:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
    elif output.suffix.lower() == ".json":
        output.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        raise ValueError("Output must end in .json, .jsonl, or .csv")
    return len(records)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrape book data from books.toscrape.com")
    limits = parser.add_mutually_exclusive_group()
    limits.add_argument("--max-books", type=positive_int, help="Stop after this many books")
    limits.add_argument("--max-pages", type=positive_int, help="Stop after this many 20-book pages")
    parser.add_argument("--output", type=Path, default=Path("data/books.json"))
    parser.add_argument("--delay", type=non_negative_float, default=0.25, help="Delay between requests")
    parser.add_argument("--timeout", type=non_negative_float, default=20.0, help="Request timeout")
    parser.add_argument("--verbose", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )
    scraper = BooksScraper(delay=args.delay, timeout=args.timeout)
    try:
        books = scraper.scrape(max_books=args.max_books, max_pages=args.max_pages)
        count = write_books(books, args.output)
    except (requests.RequestException, ScrapeError, OSError, ValueError) as error:
        logging.error("Scrape failed: %s", error)
        return 1
    print(f"Saved {count} books to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

