# Books to Scrape project

This project scrapes book information from [Books to Scrape](https://books.toscrape.com/), saves it as a sorted local JSON file, and uses that file as the data source for the Bookfinder interface.

## Setup

Python 3.11 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Scrape books into local data

Run the scraper from the project folder:

```bash
python scraper.py
```

By default, this fetches the catalogue, extracts each book's details, sorts the records alphabetically by title, and writes them to `data/books.json`. You can limit the run while trying it out:

```bash
python scraper.py --max-books 5 --verbose
```

The local JSON includes title, category, description, rating, prices and tax, availability and stock count, review count, product and image URLs, UPC, and the UTC scrape time. Use `--output` to choose another JSON, JSONL, or CSV file.

## View the interface using the local data

The interface reads `data/books.json` directly. After running the scraper, start a small local web server from the project folder:

```bash
python -m http.server 8000
```

Then open [http://localhost:8000/demo.html](http://localhost:8000/demo.html). Do not open `demo.html` as a `file://` URL; browsers block its data-file request in that mode.

The interface displays book covers, descriptions, categories, prices, ratings, availability, and reviews. It supports searching by title, UPC, category, or description, filtering by category and minimum rating, and sorting by title, price, rating, or stock. Expand **All scraped information** on a book card to see the remaining scraped fields.

For a hosted website, publish `demo.html` and the generated `data/books.json` together, preserving the `data/` folder path. The live interface needs the JSON file in the same website deployment.

## Optional Supabase upload

Supabase is optional and separate from the local-file interface. If configured, the scraper can also upload a run by adding `--supabase`:

```bash
python scraper.py --max-books 5 --supabase
```

This requires `SUPABASE_URL`, a backend secret key in `.env`, and the schema in `supabase/schema.sql`. Never put the secret key in browser code. The Bookfinder interface reads the local JSON file, not Supabase.

## Tests

Parser tests use local HTML fixtures and make no network requests:

```bash
python -m unittest discover -s tests -v
```
