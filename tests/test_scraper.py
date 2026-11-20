import unittest

from scraper import BooksScraper, clean_money, parse_book_page, parse_catalogue_page, parse_stock_count


CATALOGUE_HTML = """
<article class="product_pod"><h3><a href="catalogue/first_1/index.html">First</a></h3></article>
<article class="product_pod"><h3><a href="catalogue/second_2/index.html">Second</a></h3></article>
<li class="next"><a href="catalogue/page-2.html">next</a></li>
"""

BOOK_HTML = """
<ul class="breadcrumb"><li><a href="/">Home</a></li><li><a href="../category/books_1/index.html">Books</a></li><li><a href="../category/books/poetry_23/index.html">Poetry</a></li></ul>
<div class="product_main"><h1>A Test Book</h1><p class="star-rating Four"></p></div>
<div class="item active"><img src="../../media/cache/test.jpg"></div>
<div id="product_description"></div><p>A useful description.</p>
<table class="table table-striped">
  <tr><th>UPC</th><td>abc123</td></tr>
  <tr><th>Price (excl. tax)</th><td>£10.50</td></tr>
  <tr><th>Price (incl. tax)</th><td>£10.50</td></tr>
  <tr><th>Tax</th><td>£0.00</td></tr>
  <tr><th>Availability</th><td>In stock (7 available)</td></tr>
  <tr><th>Number of reviews</th><td>3</td></tr>
</table>
"""


class ParserTests(unittest.TestCase):
    def test_catalogue_links_are_absolute(self):
        urls, next_url = parse_catalogue_page(CATALOGUE_HTML, "https://books.toscrape.com/")
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], "https://books.toscrape.com/catalogue/first_1/index.html")
        self.assertEqual(next_url, "https://books.toscrape.com/catalogue/page-2.html")

    def test_book_page_fields(self):
        book = parse_book_page(
            BOOK_HTML,
            "https://books.toscrape.com/catalogue/a-test-book_1/index.html",
            scraped_at="2026-01-01T00:00:00+00:00",
        )
        self.assertEqual(book.upc, "abc123")
        self.assertEqual(book.category, "Poetry")
        self.assertEqual(book.rating, 4)
        self.assertEqual(book.stock_count, 7)
        self.assertEqual(book.price_incl_tax_gbp, "10.50")
        self.assertTrue(book.image_url.startswith("https://books.toscrape.com/"))

    def test_value_parsers(self):
        self.assertEqual(clean_money("£1,234.50"), "1234.50")
        self.assertEqual(parse_stock_count("In stock (22 available)"), 22)
        self.assertEqual(parse_stock_count("Out of stock"), 0)

    def test_fetch_decodes_source_as_utf8(self):
        class FakeResponse:
            encoding = "latin-1"
            content = "Café — poetry".encode("utf-8")

            def raise_for_status(self):
                return None

            @property
            def text(self):
                return self.content.decode(self.encoding)

        class FakeSession:
            def get(self, url, timeout):
                return FakeResponse()

        scraper = BooksScraper(delay=0)
        scraper.session = FakeSession()
        self.assertEqual(scraper.fetch("https://example.test/book"), "Café — poetry")


if __name__ == "__main__":
    unittest.main()

