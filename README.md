# Books to Scrape project

This project starts with an isolated Python scraper for the educational sandbox at
[Books to Scrape](https://books.toscrape.com/). It collects full product details and
writes JSON, JSON Lines, or CSV files. The output includes a UTC `scraped_at`
timestamp so it can later feed a price and availability history table in Supabase.

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
python scraper.py --max-books 5 --output data/sample_5.json --verbose
```

Then scrape three catalogue pages (up to 60 books):

```bash
python scraper.py --max-pages 3 --output data/three_pages.csv --verbose
```

Finally, omit both limits to scrape all available pages:

```bash
python scraper.py --output data/all_books.jsonl --verbose
```

The default 0.25-second delay is intentionally gentle. Adjust it with `--delay`,
but keep a delay for larger runs. Run `python scraper.py --help` for all options.

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
3. Test the integration with five books:

```bash
python scraper.py --max-books 5 --supabase --output data/sample_5.json --verbose
```

After verifying the four tables, expand to three pages and then the full catalogue:

```bash
python scraper.py --max-pages 3 --supabase --output data/books.json --verbose
python scraper.py --supabase --output data/books.json --verbose
```

### Connect the Bookfinder interface

The `demo.html` page reads from Supabase's read-only `current_books` view. Before opening or publishing the page:

1. The page is configured with this project's `SUPABASE_URL` and publishable key in `demo.html`. If you point it at a different Supabase project, update those two constants. A publishable key (or legacy anon key) is intended for browser use; never use `SUPABASE_SECRET_KEY` in the page.
2. Run the scraper with `--supabase` so the catalogue is present in the database.

The existing SQL schema enables row-level security and grants browser users read access to catalogue records. The page fetches rows in batches of 500 and keeps its search, category, rating, and sorting controls in the browser.

## Planned architecture

1. Scrape and validate small samples.
2. Expand to multiple pages and then the full catalogue.
3. Create normalized Supabase tables for books, categories, scrape runs, and
   time-series observations (price, tax, stock, and rating). **Implemented.**
4. Upsert stable book metadata by UPC and append one observation per scrape run.
   **Implemented; awaiting live database verification.**
5. Build a frontend that reads current values and price/stock history. **Current-value Bookfinder frontend implemented; price/stock history display remains planned.**
