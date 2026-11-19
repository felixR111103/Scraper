# Books to Scrape

This repository has one scraper and one frontend. The scraper writes the book catalogue to a local JSON file; the frontend reads that file.

## The files you need

| File or folder | Purpose |
|---|---|
| `scraper.py` | Scrapes the book website, sorts the results by title, and writes `data/books.json`. |
| `index.html` | The Bookfinder frontend. It reads `data/books.json` and provides search, filters, sorting, and book details. |
| `data/books.json` | Generated catalogue data. It appears after you run the scraper. |
| `requirements.txt` | Python libraries needed by the scraper. |
| `README.md` | This setup guide. |

These files are supporting:

- `tests/` contains automated checks; it is not needed to open the frontend.
- `.gitignore` and `data/.gitkeep` are Git housekeeping files.

There is no separate demo page anymore: `index.html` is the actual frontend.

## Run it on your computer

Open Terminal in the repository folder, then run:

```bash
python3 -m pip install -r requirements.txt
python3 scraper.py
python3 -m http.server 8000
```

Keep the Terminal window open while using the site. Open:

[http://localhost:8000/](http://localhost:8000/)

The first command installs the scraper's dependencies. The second scrapes and creates the sorted `data/books.json`. The third serves the project so the browser can load that JSON file. Do not open `index.html` by double-clicking it; browsers do not reliably allow it to fetch the JSON file from disk.

To try a smaller scrape first:

```bash
python3 scraper.py --max-books 5
```

The frontend shows each book's cover, description, category, price, rating, availability, stock, reviews, and original product link. It can search by title, UPC, category, or description, filter by category or minimum rating, and sort by title, price, rating, or stock. Expand **All scraped information** on a card for the remaining scraped fields.

## Hosted frontend

GitHub Pages is not enabled for this repository, so there is no hosted frontend URL yet. To host it, GitHub Pages must be enabled and the generated `data/books.json` must be included in the published site beside the `data/` folder. The repository is public, so a GitHub Pages site would also be public.
