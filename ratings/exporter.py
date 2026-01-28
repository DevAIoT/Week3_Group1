"""CLI utility for offline CSV export of ratings."""

import csv
import sys

from ratings.database import RatingsDatabase


def export_to_csv(db_path, output_path):
    """Export all ratings from the database to a CSV file."""
    db = RatingsDatabase(db_path)
    ratings = db.get_all(limit=100_000, offset=0)
    db.close()

    if not ratings:
        print("No ratings found.")
        return

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "rating", "timestamp", "source"])
        writer.writeheader()
        writer.writerows(ratings)

    print(f"Exported {len(ratings)} ratings to {output_path}")


if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else "ratings.db"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "ratings.csv"
    export_to_csv(db_file, out_file)
