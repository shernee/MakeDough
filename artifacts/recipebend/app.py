import os
import json
import requests as http_requests
from flask import Flask, request, jsonify, send_from_directory
from recipe_scrapers import scrape_html
from openai import OpenAI

app = Flask(__name__, static_folder="static", template_folder="templates")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SYSTEM_PROMPT = """You are a precise recipe modification assistant. Given a recipe and a user request, you modify only the ingredients and amounts — never rewrite steps.

Rules:
1. Apply the user's requested changes to ingredient names and quantities only.
2. If a change affects timing or temperature in a specific step, flag that step number in the "flags" array with a short note — do NOT rewrite the step text.
3. Include substitution prep notes inline within the ingredient string itself, e.g. "1 cup milk + 1 tsp lemon juice, sit 5 min — replaces buttermilk".
4. Flag ingredients that do not scale linearly (baking powder, baking soda, salt, leavening agents) with a note in the "flags" array explaining why.
5. The "steps" array in your output must be identical to the original steps — copy them unchanged.
6. Return ONLY valid JSON — no markdown fences, no preamble, no explanation outside the JSON.

Output structure (exactly this, no extra keys):
{
  "title": "string",
  "servings": "string",
  "ingredients": ["string", ...],
  "steps": ["string", ...],
  "changes_summary": "string — one paragraph summarising what changed and why",
  "flags": ["string", ...]
}"""


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


@app.route("/modify", methods=["POST"])
def modify():
    data = request.get_json(silent=True)
    if not data or "recipe" not in data or "request" not in data:
        return jsonify({"error": "Missing 'recipe' or 'request' in request body"}), 400

    recipe = data["recipe"]
    user_request = data["request"].strip()
    if not user_request:
        return jsonify({"error": "Modification request cannot be empty"}), 400

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return jsonify({"error": "OPENROUTER_API_KEY is not configured"}), 500

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    user_message = (
        f"Recipe:\n{json.dumps(recipe, indent=2)}\n\n"
        f"Modification request: {user_request}"
    )

    try:
        completion = client.chat.completions.create(
            model="google/gemma-4-31b-it",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )

        raw = completion.choices[0].message.content.strip()

        # Strip markdown fences if the model included them anyway
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        modified = json.loads(raw)

        required_keys = {"title", "servings", "ingredients", "steps", "changes_summary", "flags"}
        missing = required_keys - set(modified.keys())
        if missing:
            return jsonify({"error": f"Model response missing keys: {missing}"}), 502

        return jsonify(modified)

    except json.JSONDecodeError as e:
        return jsonify({"error": f"Model returned invalid JSON: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Modification failed: {str(e)}"}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
