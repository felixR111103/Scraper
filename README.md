# Bookfinder — Books to Scrape Project

## Purpose

Bookfinder is an educational web-scraping and frontend project created for the NOVA SBE AI Fundamentals course. It has two main parts:

1. A Python scraper that collects book information from [Books to Scrape](https://books.toscrape.com/).
2. A browser-based catalogue that lets a user explore the collected information.

The scraper visits the website's catalogue and individual product pages. It extracts structured information about each book and saves the results locally in data/books.json. The frontend loads this file and presents the books as searchable cards.

The project demonstrates the complete path from collecting data on the web to storing, processing, and presenting it in an interface.

## Data collection

### Source

All book data comes from [Books to Scrape](https://books.toscrape.com/), a demonstration website designed for practising web scraping. The current data was collected on 18 November 2026.

### Collection process

The scraper is implemented in `scraper.py`. It uses:

- `requests` to download catalogue and product pages;
- `BeautifulSoup` to parse their HTML;
- the catalogue's pagination links to move between pages; and
- each catalogue entry's product link to retrieve detailed book information.

For every book, the scraper collects:

- UPC and title;
- category and description;
- rating;
- price excluding tax, price including tax, and tax;
- availability and numerical stock count;
- number of reviews;
- product and cover-image URLs; and
- the UTC time at which the record was collected.

The scraper explicitly decodes the website as UTF-8 so that punctuation and accented characters are preserved. It uses a descriptive user-agent and waits 0.25 seconds between requests by default. It also supports limits for small test runs, so the whole catalogue does not need to be downloaded during development.

## Data persistence

The primary dataset is stored in `data/books.json`. JSON was chosen because it:

- preserves a clear field/value structure for every book;
- can be written directly by Python;
- can be loaded directly by JavaScript in the browser; and
- keeps the project simple without requiring a database or backend server.

The complete file currently contains 1,000 book records. The scraper can also write CSV or JSON Lines when the output filename ends in `.csv` or `.jsonl`.

The data is a snapshot rather than a live connection. Running the scraper again replaces the chosen output with newly collected data. Each record contains a `scraped_at` timestamp so that the age of the data is visible.

## User interaction

The frontend is contained in `index.html`. After the project is served locally, a user can:

- search by title, UPC, category, or description;
- filter books by category;
- select a minimum rating;
- sort by title, price, rating, or available stock;
- view the cover, description, price, rating, and availability;
- expand a book card to see all collected fields; and
- follow a link to the original product page.

The interface is responsive and adjusts its layout for desktop and smaller screens. It is a static frontend: searches and filters run locally in the browser and do not change the stored dataset.

## Setup and use

### Requirements

- Python 3.10 or newer
- A current web browser
- An internet connection when running the scraper

The Python dependencies are listed in `requirements.txt`:

- `beautifulsoup4==4.14.2`
- `requests==2.32.5`

### 1. Create and activate a virtual environment

From the project folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install the dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Run the scraper

To collect the complete catalogue and save it to the default location:

```bash
python3 scraper.py
```

For a quicker five-book test:

```bash
python3 scraper.py --max-books 5 --output data/sample_5.json
```

To collect three catalogue pages and write CSV:

```bash
python3 scraper.py --max-pages 3 --output data/three_pages.csv
```

Useful configuration options are:

| Option | Purpose |
|---|---|
| `--max-books N` | Stop after collecting `N` books |
| `--max-pages N` | Stop after collecting `N` catalogue pages |
| `--output PATH` | Select the output path and JSON, JSONL, or CSV format |
| `--delay SECONDS` | Change the delay between requests |
| `--timeout SECONDS` | Change the HTTP request timeout |
| `--verbose` | Display progress while scraping |

`--max-books` and `--max-pages` cannot be used together.

### 4. Run the frontend

Start a local web server from the project folder:

```bash
python3 -m http.server 8000
```

Then open [http://localhost:8000/](http://localhost:8000/) in a browser.

The frontend should not be opened by double-clicking `index.html`, because browser security rules may prevent it from loading `data/books.json` directly from the filesystem.

### 5. Run the automated tests

```bash
python3 -m unittest discover -s tests
```

The tests check URL extraction, book-field parsing, price normalization, and stock-count parsing.

No API keys, passwords, or environment variables are required.

## Learning

This was the first time I managed to build a scraper that actually worked from beginning to end. In the earlier Job Hunt Builder project, I struggled with this because I did not fully understand how all the different parts were connected. This time, I worked more step by step. I first brainstormed with ChatGPT about what the final project could look like and then started by building a small version of the scraper. Once I knew that the basic setup worked, I gradually expanded it until it could collect all 1,000 books. Starting small made the process much less overwhelming and helped me understand what was happening at each stage.

I also had to decide where to save the scraped information. At first, I considered using Supabase, but I realized that it would have made the project more complicated than necessary. Since the dataset is relatively small, saving it locally in data/books.json was enough. This taught me that a database is not always needed and that the simplest solution can sometimes be the best one.

My biggest learning was understanding how the different parts of the project work together. The scraper collects information from the website, the JSON file stores it in a structured way, and the frontend reads that file and displays the information to the user. I had understood these parts separately before, but this project helped me see the full process much more clearly. I now feel more confident that I could build a similar project again.

One challenge was keeping track of the different files and understanding which ones were actually important. I had a picture in my mind of how the project should work, but translating that picture into code and a clear folder structure took some time. During the project, I learned how to organize the files better, recognize which files were essential, and remove files that were no longer needed. I also learned how to upload the project to Git so that another person can access it and understand how it works.

## Limitations and assistance

### Current limitations

- The data is a static snapshot and can become outdated until the scraper is run again.
- The scraper depends on the current HTML structure of Books to Scrape. Changes to that structure may require updated selectors.
- Two records in the complete dataset have no description.
- Categories such as `Default` and `Add a comment` come from the source website but are not meaningful genres.
- Tax and review fields contain only zeroes in the current source data.
- The dataset contains product information but does not include authors, ISBNs, publishers, or publication dates.
- The frontend has no backend, user accounts, saved favourites, or automatic refresh process.
- Network failures are reported, but interrupted full scrapes do not currently resume from a checkpoint.

### External resources and assistance

The project uses the open-source Python packages `requests` and `beautifulsoup4`. Python's standard-library modules are used for command-line arguments, CSV and JSON output, timestamps, logging, regular expressions, and tests. The source website is Books to Scrape.

AI assistance was mainly used for translating ideas I had from basic English into coding language. For this, I mainly used ChatGPT in VS Code. Additionally, AI also helped me draft or review parts of the project and its documentation. All generated suggestions were reviewed, adapted, and tested before inclusion. Moreover, during the tutorials I asked Ricardo several times for help when I was unsure how to tackle certain issues in the code or push to the correct repository. This helped me a lot in understanding the connections between the files.

## Project structure

```text
.
├── data/
│   ├── books.json          # Complete generated catalogue
│   ├── demo_3.json         # Three-record demonstration dataset
│   ├── sample_5.json       # Five-record test dataset
│   └── three_pages.csv     # Three-page CSV sample
├── tests/
│   └── test_scraper.py     # Automated parser tests
├── .gitignore
├── AUDIT.md                # Publication audit and remaining limitations
├── index.html              # Bookfinder frontend
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
└── scraper.py              # Scraper and output logic
```

## Responsible use

Books to Scrape is intentionally provided for scraping practice. When adapting this project to another website, first review that site's terms, robots policy, and applicable data-protection rules. Use an identifiable user-agent, limit the request rate, and collect only data that you are permitted to use.
