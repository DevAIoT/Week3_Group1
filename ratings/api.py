"""Flask REST API for ratings."""

import csv
import io
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request, Response
from flask_cors import CORS


def create_app(db):
    """Application factory. Pass a RatingsDatabase instance."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for dashboard requests

    @app.route("/api/ratings", methods=["GET"])
    def list_ratings():
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        ratings = db.get_all(limit=limit, offset=offset)
        return jsonify(ratings)

    @app.route("/api/ratings", methods=["POST"])
    def create_rating():
        data = request.get_json()
        if not data or "rating" not in data:
            return jsonify({"error": "Missing 'rating' field"}), 400
        rating = data["rating"]
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be an integer 1-5"}), 400
        row_id = db.insert(rating, source="api")
        return jsonify({"id": row_id, "rating": rating}), 201

    @app.route("/api/ratings/summary", methods=["GET"])
    def summary():
        return jsonify(db.get_summary())

    @app.route("/api/ratings/export", methods=["GET"])
    def export_csv():
        ratings = db.get_all(limit=10_000, offset=0)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "rating", "timestamp", "source"])
        writer.writeheader()
        writer.writerows(ratings)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=ratings.csv"},
        )

    @app.route("/api/ratings/timeline", methods=["GET"])
    def timeline():
        """Get ratings grouped by time period."""
        period = request.args.get('period', 'hour')
        hours_map = {'hour': 24, 'day': 7*24, 'week': 4*7*24}
        hours = hours_map.get(period, 24)

        # Get ratings from the last N hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Get all ratings for timeline
        all_ratings = db.get_all(limit=10000, offset=0)

        # Filter by time and group by hour buckets
        timeline_data = {}
        for rating in all_ratings:
            rating_time = datetime.fromisoformat(rating['timestamp'])
            if rating_time >= cutoff_time:
                # Round to hour bucket
                hour_bucket = rating_time.replace(minute=0, second=0, microsecond=0)
                bucket_key = hour_bucket.isoformat()

                if bucket_key not in timeline_data:
                    timeline_data[bucket_key] = {'count': 0, 'sum': 0}

                timeline_data[bucket_key]['count'] += 1
                timeline_data[bucket_key]['sum'] += rating['rating']

        # Convert to list format
        result = []
        for timestamp, data in sorted(timeline_data.items()):
            result.append({
                'timestamp': timestamp,
                'count': data['count'],
                'average': round(data['sum'] / data['count'], 2) if data['count'] > 0 else 0
            })

        return jsonify(result)

    @app.route("/api/ratings/distribution", methods=["GET"])
    def distribution():
        """Get rating counts grouped by rating value (1-5)."""
        all_ratings = db.get_all(limit=100000, offset=0)
        dist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for r in all_ratings:
            key = str(r["rating"])
            if key in dist:
                dist[key] += 1
        return jsonify(dist)

    @app.route("/api/ratings/source-breakdown", methods=["GET"])
    def source_breakdown():
        """Get rating counts grouped by source."""
        all_ratings = db.get_all(limit=100000, offset=0)
        sources = {}
        for r in all_ratings:
            src = r.get("source", "unknown")
            sources[src] = sources.get(src, 0) + 1
        result = [{"source": s, "count": c} for s, c in sources.items()]
        return jsonify(result)

    return app
