"""Tests for ratings.database — uses in-memory SQLite."""

import unittest

from ratings.database import RatingsDatabase


class TestRatingsDatabase(unittest.TestCase):

    def setUp(self):
        self.db = RatingsDatabase(":memory:")

    def tearDown(self):
        self.db.close()

    def test_insert_and_retrieve(self):
        row_id = self.db.insert(3)
        ratings = self.db.get_all()
        self.assertEqual(len(ratings), 1)
        self.assertEqual(ratings[0]["id"], row_id)
        self.assertEqual(ratings[0]["rating"], 3)
        self.assertEqual(ratings[0]["source"], "gesture")

    def test_insert_with_source(self):
        self.db.insert(5, source="api")
        ratings = self.db.get_all()
        self.assertEqual(ratings[0]["source"], "api")

    def test_invalid_rating_rejected(self):
        with self.assertRaises(Exception):
            self.db.insert(0)
        with self.assertRaises(Exception):
            self.db.insert(6)

    def test_get_all_order_and_pagination(self):
        for i in range(1, 6):
            self.db.insert(i)
        # Newest first
        all_ratings = self.db.get_all()
        self.assertEqual(len(all_ratings), 5)
        self.assertEqual(all_ratings[0]["rating"], 5)
        self.assertEqual(all_ratings[-1]["rating"], 1)
        # Pagination
        page = self.db.get_all(limit=2, offset=1)
        self.assertEqual(len(page), 2)
        self.assertEqual(page[0]["rating"], 4)

    def test_summary_empty(self):
        summary = self.db.get_summary()
        self.assertEqual(summary["count"], 0)
        self.assertIsNone(summary["average"])

    def test_summary_with_data(self):
        self.db.insert(2)
        self.db.insert(4)
        summary = self.db.get_summary()
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["average"], 3.0)
        self.assertEqual(summary["min"], 2)
        self.assertEqual(summary["max"], 4)

    def test_timestamp_is_iso_format(self):
        self.db.insert(1)
        ratings = self.db.get_all()
        ts = ratings[0]["timestamp"]
        self.assertIn("T", ts)
        self.assertTrue(ts.endswith("+00:00"))


if __name__ == "__main__":
    unittest.main()
