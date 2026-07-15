---
title: Manufacturing Quality Dashboard
emoji: 📊
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.20.0
app_file: app.py
pinned: false
short_description: Interactive quality dashboard built from a single AI prompt
---

# Manufacturing Quality Dashboard

Live demo for episode 001 of the Medium series **Build Business Tools with AI** — an interactive manufacturing-quality dashboard generated from a single 3Q + TCREI prompt.

Pick a date and a product, click **Generate**, and get:

- **Trends** — daily mean/std of dimension and thickness over a 21-day window
- **Capability** — daily Cpk and rolling 5-day Ppk
- **Distributions** — the selected day's measurements against spec limits
- **Summary table** — Cpk, overall Ppk, and out-of-spec counts

The default selection (product **805**, date **2020-06-15**) works as-is.

All data is **synthetic sample data** generated for the article. Source code, the original Colab notebook, and the exact TCREI prompt are on GitHub: `medium_Build_Business_Tools_with_AI`.
