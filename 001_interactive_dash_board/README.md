# 001 — The Interactive Dashboard

An interactive manufacturing-quality dashboard built entirely from a single TCREI prompt. It runs in Google Colab with a Gradio UI: pick a date and a product, click **Generate**, and get 21 days of inspection trends, Cpk/Ppk process-capability charts, distribution histograms, and a summary table.

## Files

| File | Description |
|---|---|
| `medium_001_The_Interactive_Dashboard.ipynb` | The Colab notebook (final working code) |
| `TCREI_prompt.txt` | The exact TCREI prompt used to generate the code |
| `quality_data_small.db` | Sample SQLite database with synthetic inspection data (~80 MB) |

## How to run

1. Upload `quality_data_small.db` to your Google Drive at:
   `My Drive/Colab Notebooks/data/quality_data_small.db`
   (or edit `DB_PATH` in the notebook to match your own location)
2. Open `medium_001_The_Interactive_Dashboard.ipynb` in [Google Colab](https://colab.research.google.com/).
3. Run the cell. Authorize the Google Drive mount when prompted.
4. Open the Gradio link printed in the output, pick a date and product, and click **Generate**.

## Dates with data

The sample database covers three products, each with data in these windows:

| Product | 2020 | 2021 |
|---|---|---|
| 805 | 2020-05-20 → 2020-07-10 | 2021-01-04 → 2021-04-02 |
| 535 | 2020-01-03 → 2020-03-30 | 2021-01-04 → 2021-04-02 |
| 905 | 2020-08-20 → 2020-11-20 | 2021-01-04 → 2021-03-31 |

The notebook's default (product **805**, date **2020-06-15**) works out of the box.

## What the dashboard shows

- **Trends** — daily mean and standard deviation of dimension and thickness over a 21-day window centered on the selected date
- **Capability** — daily Cpk and rolling 5-day Ppk for both characteristics
- **Distributions** — histograms of the selected day's measurements against specification limits
- **Summary table** — selected-date Cpk, overall 21-day Ppk, and out-of-spec counts

Records with zero or negative dimension/thickness are treated as equipment noise and excluded, as specified in the prompt. Dimension limits are derived from the product code (nominal ±10%); the thickness upper limit is 0.7.

## Data note

`quality_data_small.db` contains **synthetic data** generated for this article. Table layout: one table per product per year (`DS_PRDT_<product>_<yy>`) with `ins_date`, `dimension`, `thickness`, and related fields.
