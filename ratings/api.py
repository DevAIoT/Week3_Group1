"""Flask REST API for ratings."""

import csv
import io

from flask import Flask, jsonify, request, Response


def create_app(db):
    """Application factory. Pass a RatingsDatabase instance."""
    app = Flask(__name__)

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

    return app
