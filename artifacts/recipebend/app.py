import os
import requests as http_requests
from flask import Flask, request, jsonify, send_from_directory
from recipe_scrapers import scrape_html

app = Flask(__name__, static_folder="static", template_folder="templates")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.route("/extract", methods=["POST"])
def extract():
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    url = data["url"].strip()
    if not url:
        return jsonify({"error": "URL cannot be empty"}), 400

    try:
        response = http_requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = response.text
        scraper = scrape_html(html, org_url=url, wild_mode=True)

        def safe(fn):
            try:
                result = fn()
                return result if result is not None else None
            except Exception:
                return None

        title = safe(scraper.title)
        servings = safe(scraper.yields)
        total_time = safe(scraper.total_time)
        ingredients = safe(scraper.ingredients) or []
        steps = safe(scraper.instructions_list) or []

        if not steps:
            raw = safe(scraper.instructions)
            if raw:
                steps = [s.strip() for s in raw.split("\n") if s.strip()]

        return jsonify({
            "title": title,
            "servings": servings,
            "total_time": total_time,
            "ingredients": ingredients,
            "steps": steps,
            "source_url": url,
        })

    except Exception as e:
        return jsonify({"error": f"Failed to extract recipe: {str(e)}"}), 422


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
