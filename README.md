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

## Planned architecture

1. Scrape and validate small samples.
2. Expand to multiple pages and then the full catalogue.
3. Create normalized Supabase tables for books, categories, scrape runs, and
   time-series observations (price, tax, stock, and rating).
4. Upsert stable book metadata by UPC and append one observation per scrape run.
5. Build a frontend that reads current values and price/stock history.
