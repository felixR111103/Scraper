import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from supabase_store import SupabaseError, SupabaseStore, chunks, load_env_file


class SupabaseStoreTests(unittest.TestCase):
    def test_new_secret_key_uses_only_apikey_header(self):
        store = SupabaseStore("https://example.supabase.co", "sb_secret_test")
        self.assertEqual(store.session.headers["apikey"], "sb_secret_test")
        self.assertNotIn("Authorization", store.session.headers)

    def test_publishable_key_is_rejected_for_uploads(self):
        with self.assertRaisesRegex(SupabaseError, "publishable key"):
            SupabaseStore("https://example.supabase.co", "sb_publishable_test")

    def test_legacy_service_key_uses_bearer_header(self):
        store = SupabaseStore("https://example.supabase.co", "eyJtest")
        self.assertEqual(store.session.headers["Authorization"], "Bearer eyJtest")

    def test_load_env_file_and_chunking(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text("TEST_SCRAPER_SETTING='saved'\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                load_env_file(env_file)
                self.assertEqual(os.environ["TEST_SCRAPER_SETTING"], "saved")
        self.assertEqual(list(chunks([{"id": 1}, {"id": 2}, {"id": 3}], 2)), [[{"id": 1}, {"id": 2}], [{"id": 3}]])


if __name__ == "__main__":
    unittest.main()
