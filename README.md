# ScrapyProjects

A curated collection of **Scrapy learning and production-style scraping projects**, ranging from beginner spiders (quotes, world data) to real-world e-commerce crawlers (Arabic and English sites).

This repository is designed as a practical portfolio for:
- Learning Scrapy fundamentals.
- Practicing spider architecture across multiple domains.
- Reusing project templates (`items`, `pipelines`, `middlewares`, `settings`).
- Running and extending independent crawlers quickly.

---

## Repository Highlights

- **13 standalone Scrapy projects** (each with its own `scrapy.cfg`).
- Covers multiple use cases: demo crawling, pagination, API-like extraction, and product catalog scraping.
- Includes sample outputs (`.json`, `.csv`, `.xlsx`) in several project folders.
- Contains a separate `00_scripts/` folder for one-off scraping scripts.

---

## Project Index

| # | Project Folder | Focus |
|---|---|---|
| 01 | `01_drones_scraper` | Product scraping demo (drones) |
| 02 | `02_pwdemo` | Playwright/Scrapy demo spider |
| 03 | `03_quotes_proj` | Intro quotes scraping project |
| 04 | `04_whisky_scraper` | Whisky product/process spiders |
| 05 | `05_worldometers` | Country/world data extraction |
| 06 | `06_tinydeal` | Offers scraping workflow |
| 07 | `07_imdb` | IMDb top/best movies crawl |
| 08 | `08_bukhamsen` | E-commerce product scraping |
| 09 | `09_ma3rof` | Large-scale product collection workflow |
| 10 | `10_makeupstationsa` | Arabic e-commerce scraping |
| 11 | `11_almanea` | Arabic retail crawler |
| 12 | `12_smartshopping` | Product data extraction |
| 13 | `13_europa` | Jobs/opportunities spider |

> `z_not-mine/` contains external or reference experiments and is not part of the core curated set.

---

## Educational Progression: How Projects Differ

The projects are intentionally varied so learners can compare approaches and level-up progressively:

| Project | What Makes It Different | Educational Value |
|---|---|---|
| `01_drones_scraper` | Simple product scraping flow with straightforward selectors and export. | Best first step to understand spider lifecycle and item output. |
| `02_pwdemo` | Demonstrates browser-assisted crawling patterns (Playwright + Scrapy context). | Introduces JS-heavy site handling and when pure HTTP parsing is not enough. |
| `03_quotes_proj` | Minimal, clean beginner crawler. | Teaches core concepts: requests, parsing, pagination basics, and JSON output. |
| `04_whisky_scraper` | Multiple spiders for related tasks (catalog + processing variants). | Shows how to separate responsibilities across spiders in one project. |
| `05_worldometers` | Structured table/data extraction rather than e-commerce products. | Good for practicing consistent schema extraction from semi-tabular pages. |
| `06_tinydeal` | Offer/deal-specific scraping with listing behavior. | Demonstrates adapting parsing logic for promotional/price-driven pages. |
| `07_imdb` | Ranking/list-style crawl focused on media metadata. | Useful for selector robustness and normalized data fields (rank, title, year, rating). |
| `08_bukhamsen` | Real e-commerce data with richer product attributes and local artifacts. | Teaches practical product schema design and data post-processing concerns. |
| `09_ma3rof` | Includes larger-volume workflow artifacts and intermediate work files. | Introduces scaling mindset: batching, checkpoint-style exports, and long-run organization. |
| `10_makeupstationsa` | Arabic-language retail target and market-specific formatting. | Helps practice multilingual scraping challenges (labels, numerals, text normalization). |
| `11_almanea` | Another Arabic retail crawler with different site structure/patterns. | Encourages transferable spider architecture across similar domains with different HTML. |
| `12_smartshopping` | Product-focused extraction with its own schema/settings behavior. | Reinforces project-level customization and reusable Scrapy conventions. |
| `13_europa` | Jobs/opportunities domain rather than product catalogs. | Expands learners beyond e-commerce into listings with different fields and navigation logic. |

### Suggested Learning Path

1. Start with `03_quotes_proj` and `01_drones_scraper` (fundamentals).
2. Move to `05_worldometers` and `07_imdb` (structured/ranked data extraction).
3. Practice commerce workflows in `06_tinydeal`, `08_bukhamsen`, `10_makeupstationsa`, `11_almanea`, `12_smartshopping`.
4. Explore complexity/scaling using `09_ma3rof`.
5. Finish with `02_pwdemo` and `13_europa` to broaden techniques (dynamic pages + non-product domains).

---

## Quick Start

### 1) Prerequisites

- Python **3.9+** recommended
- `pip`
- Virtual environment tooling (`venv`)

### 2) Create environment and install Scrapy

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install scrapy
```

> Some projects may require additional dependencies depending on target site behavior (e.g., JS rendering).

### 3) Run any project

Each project is self-contained. Move into a project folder, list spiders, then crawl:

```bash
cd 03_quotes_proj
scrapy list
scrapy crawl quotes_spider -O quotes.json
```

---

## Typical Scrapy Project Structure

Most project folders follow this pattern:

```text
project_name/
├── scrapy.cfg
└── project_package/
    ├── __init__.py
    ├── items.py
    ├── middlewares.py
    ├── pipelines.py
    ├── settings.py
    └── spiders/
        ├── __init__.py
        └── *.py
```

---

## Common Commands

From inside a specific project directory:

```bash
# Show available spiders
scrapy list

# Run a spider
scrapy crawl <spider_name>

# Export output directly
scrapy crawl <spider_name> -O output.json
scrapy crawl <spider_name> -O output.csv
```

---

## Notes & Best Practices

- Respect target websites' Terms of Service and robots policies.
- Add download delays and proper headers for polite crawling.
- Keep selectors and parsing logic site-specific and maintainable.
- Prefer incremental improvements per project instead of coupling projects together.

---

## Contributing

Contributions are welcome. Suggested contribution types:

- Improve spider robustness (pagination, retries, validation).
- Add clear project-level READMEs for individual crawlers.
- Improve exported schema consistency across e-commerce projects.
- Add tests/utilities for parsing functions.

---

## License

No explicit license file is currently provided in this repository. If you plan to reuse or redistribute code, add an appropriate license first.
