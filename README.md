# Build Business Tools with AI

Companion code for the Medium series **Build Business Tools with AI** — real, working examples of business tools built by writing a structured prompt (**3Q + TCREI**) and letting AI generate the code.

No local development environment is required. Every example runs in **Google Colab**, so anyone — including non-developers — can reproduce the results with a browser and a Google account.

## Episodes

| # | Episode | What it builds | Live demo | Article |
|---|---|---|---|---|
| 001 | [The Interactive Dashboard](./001_interactive_dash_board) | An interactive manufacturing-quality dashboard over a SQLite database — trend charts, Cpk/Ppk capability metrics, histograms, and a summary table | [▶ Try it](https://quality-dashboard-demo.streamlit.app/) | _coming soon_ |

More episodes will be added as the series continues.

## How this repository is organized

Each numbered folder is one episode of the series and contains everything needed to reproduce it:

| File | What it is |
|---|---|
| `*.ipynb` | The Colab notebook with the final working code generated from the prompt |
| `TCREI_prompt.txt` | The exact TCREI prompt used to generate the code |
| `*.db` (when needed) | A sample SQLite database so the example runs end to end |
| `streamlit_app.py` (when available) | A Streamlit port of the tool, deployed as the episode's live demo |
| `hf_space/` (when available) | A Gradio port packaged for Hugging Face Spaces |

## The 3Q + TCREI approach

The series uses the **3Q + TCREI** framework introduced in the articles: three questions to frame what you actually need, followed by a **TCREI**-structured prompt:

- **T — Task**: what the tool should do, stated concretely
- **C — Context**: who will use it and in what situation
- **R — References**: the data, schemas, rules, and constraints the AI needs
- **E — Evaluate**: how you will verify the result is correct
- **I — Iterate**: refine the prompt and repeat until it passes your evaluation

Each folder's `TCREI_prompt.txt` is the real prompt used for that episode — read it side by side with the notebook to see how the prompt maps to the generated code.

## Running an example

1. Open the episode's `.ipynb` notebook in [Google Colab](https://colab.research.google.com/) (File → Upload notebook, or open it directly from GitHub).
2. If the episode includes a `.db` file, upload it to your Google Drive at the path referenced in the notebook (by default `My Drive/Colab Notebooks/data/`).
3. Run the notebook cell and follow the Gradio link it prints.

Each episode folder has its own README with episode-specific instructions. If you just want to try the tool without running any code, use the **Live demo** link in the episodes table above.

## About the data

All databases in this repository contain **synthetic sample data** generated for demonstration purposes. They do not contain real production or business data.
