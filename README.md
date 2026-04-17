# Makedough

Makedough is a web app that extracts recipes from any URL and lets you iteratively modify them using AI — adjusting ingredients for dietary needs, scaling servings, or swapping units — without hunting through unit converters and substitution guides.

## Features

- **Recipe extraction** — paste any recipe URL and instantly pull out the title, ingredients, steps, servings, and cook time
- **AI modification** — describe what you want changed in plain English (e.g. "make it gluten-free" or "scale to 6 servings") and the AI updates only the ingredients, with inline substitution notes
- **Iterative rounds** — each modification builds on the last; the full history is tracked and sent as context so the AI stays consistent
- **Side-by-side view** — original and current ingredient lists shown together so you can see exactly what changed
- **Shortcut chips** — one-click buttons for common dietary restrictions (gluten-free, dairy-free, vegetarian, vegan, nut-free), scale presets (⅓×–3×), and volume ↔ weight unit toggle
- **Custom scaling** — enter any multiplier for precise scaling (e.g. 1.5× or 0.75×)
- **Attribution** — displays the original recipe author and source site

## Tech Stack

- **Backend:** Python 3.11, Flask, [recipe-scrapers](https://github.com/hhursev/recipe-scrapers)
- **AI:** OpenRouter API (`google/gemma-4-31b-it`) via the OpenAI Python SDK
- **Frontend:** Vanilla HTML, [Alpine.js](https://alpinejs.dev/) (CDN, no build step)
- **HTTP:** Python `requests` for fetching recipe pages

## How to Run

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set the API key**

   Create an environment variable named `OPENROUTER_API_KEY` with your [OpenRouter](https://openrouter.ai/) API key.

3. **Start the server**

   ```bash
   cd artifacts/makedough
   python app.py
   ```

4. **Open the app**

   Navigate to `http://localhost:5000` in your browser.
