# Books to Scrape project

This project scrapes the educational sandbox at
[Books to Scrape](https://books.toscrape.com/) and always saves each completed run to
Supabase. You can also request a local JSON, JSON Lines, or CSV export; every record
includes a UTC `scraped_at` timestamp for price and availability history.

## Setup

Python 3.11 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run progressively

Start with five books:

```bash
python scraper.py --max-books 5 --verbose
```

Then scrape three catalogue pages (up to 60 books):

```bash
python scraper.py --max-pages 3 --output data/three_pages.csv --verbose
```

Finally, omit both limits to scrape all available pages:

```bash
python scraper.py --output data/all_books.jsonl --verbose
```

Every run requires valid Supabase credentials and the database schema. The scraper
checks them before fetching the site. The local export is optional; use `--output`
only when you also want a file copy. The default 0.25-second delay is intentionally
gentle. Adjust it with `--delay`, but keep a delay for larger runs. Run
`python scraper.py --help` for all options.

## Tests

The parser tests use local HTML fixtures and make no network requests:

```bash
python -m unittest discover -s tests -v
```

## Supabase

1. Open **SQL Editor** in your Supabase project, paste the contents of
   `supabase/schema.sql`, and click **Run** once.
2. Copy `.env.example` to `.env` and fill in the project URL and the backend
   **secret** key. Never put the secret key in browser JavaScript or commit `.env`.
3. Start with five books (the upload to Supabase is automatic):

```bash
python scraper.py --max-books 5 --verbose
```

After verifying the four tables, expand to three pages and then the full catalogue:

```bash
python scraper.py --max-pages 3 --output data/books.json --verbose
python scraper.py --verbose
```

### Connect the Bookfinder interface

The `demo.html` page reads from Supabase's read-only `current_books` view. It is configured for this project. To use another Supabase project, update the `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` constants in `demo.html`. A publishable key (or legacy anon key) is intended for browser use; never use `SUPABASE_SECRET_KEY` in the page.

Apply `supabase/schema.sql` and run the scraper normally; every run is saved to Supabase.

The existing SQL schema enables row-level security and grants browser users read access to catalogue records. The page fetches rows in batches of 500 and keeps its search, category, rating, and sorting controls in the browser.

## Planned architecture

1. Scrape and validate small samples.
2. Expand to multiple pages and then the full catalogue.
3. Create normalized Supabase tables for books, categories, scrape runs, and
   time-series observations (price, tax, stock, and rating). **Implemented.**
4. Upsert stable book metadata by UPC and append one observation per scrape run.
   **Implemented; awaiting live database verification.**
5. Build a frontend that reads current values and price/stock history. **Current-value Bookfinder frontend implemented; price/stock history display remains planned.**
