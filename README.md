# Finance Analytics Dashboard 💰📊

A portfolio-grade personal finance analytics tool built in Python. Load a
transactions spreadsheet, clean it automatically, run a full battery of
financial analytics, generate ten different charts, and produce a polished,
color-formatted Excel report — all from a simple console dashboard.

The repository ships **with sample data, generated charts, and a generated
report already included**, so you can explore the output immediately without
running anything. Re-running the pipeline regenerates all of it from scratch
using a fresh (deterministic) sample dataset.

---

## Features

- **Automatic data cleaning**: removes empty rows and duplicates, validates
  dates, fixes negative amounts, fills missing values, and logs every issue
  it finds.
- **Full financial analytics**: totals, averages, min/max, category
  breakdowns, monthly trends with growth rates, and payment-method analysis.
- **10 charts**: income/expense line charts, category pie charts, category
  bar charts, a histogram, a boxplot, a scatter plot, and a category × month
  heatmap.
- **Polished Excel report** (`reports/Finance_Report.xlsx`) with 5 sheets:
  `Summary`, `Transactions`, `Monthly Analysis`, `Categories`, `Charts` —
  including colored headers, borders, currency/percentage formatting, and
  conditional formatting (red for large expenses / negative profit, green
  for positive profit).
- **Interactive console dashboard** with a simple numbered menu.
- **Sample data generator** producing 650+ realistic, randomized
  transactions.
- **Logging** to `logs/app.log`.
- **15+ automated tests** with `pytest`.

---

## 🌐 Live interactive dashboard (GitHub Pages)

This repository includes a **static, interactive website** in `docs/` —
built with plain HTML/CSS/JS + [Plotly.js](https://plotly.com/javascript/)
— that anyone can open in a browser and click around: hoverable charts, a
category toggle (income/expense), a searchable and sortable transactions
table with filters and pagination. No installation, no terminal, no
Python required to view it.

**To turn it on for your fork/repo:**

1. Push this project to GitHub (see below if you haven't yet).
2. In your repository, go to **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Under **Branch**, select `main` and folder **`/docs`**, then **Save**.
5. Wait a minute, then GitHub shows the live URL at the top of that page —
   usually `https://<your-username>.github.io/<repo-name>/`.

That's it — the page is fully static and reads its data from
`docs/data/dashboard_data.json`, which is regenerated automatically
whenever you run the pipeline (see [Usage](#usage) below). Commit and push
that file after regenerating it to update the live site.

### Previewing it locally before pushing

```bash
cd docs
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

---

## Tech stack

- Python 3.12+
- pandas
- openpyxl
- matplotlib
- numpy
- pathlib
- logging
- pytest
- black

---

## Project structure

```
finance_analytics/
│
├── data/
│   └── transactions.xlsx        # sample input data (already included)
│
├── reports/
│   └── Finance_Report.xlsx      # generated Excel report (already included)
│
├── charts/
│   └── *.png                    # 10 generated charts (already included)
│
├── docs/                        # interactive website (GitHub Pages)
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── data/
│       └── dashboard_data.json  # data consumed by the website (already included)
│
├── src/
│   ├── loader.py                # reads the Excel input file
│   ├── cleaner.py                # cleans and validates the data
│   ├── analyzer.py               # computes all financial statistics
│   ├── charts.py                 # generates all 10 charts
│   ├── excel_report.py           # builds the formatted Excel report
│   ├── web_export.py             # exports analysis results to docs/data/*.json
│   ├── dashboard.py               # interactive console menu
│   ├── generate_sample_data.py   # creates the sample transactions.xlsx
│   └── main.py                    # entry point
│
├── tests/
│   ├── test_loader.py
│   ├── test_cleaner.py
│   ├── test_analyzer.py
│   ├── test_excel_report.py
│   ├── test_web_export.py
│   └── test_generate_sample_data.py
│
├── logs/
│   └── app.log                    # runtime log file
│
├── requirements.txt
├── pytest.ini
├── README.md
└── .gitignore
```

---

## Installation

```bash
git clone <your-repo-url>
cd finance_analytics
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

The project already contains sample data, charts and a generated report, so
you can open `reports/Finance_Report.xlsx` right away. To regenerate
everything (or run against your own data), use one of the two modes below.

### Interactive dashboard

```bash
python src/main.py
```

```
====================================
   Finance Analytics Dashboard
====================================
1. Load data
2. Clean data
3. Run analysis
4. Generate charts
5. Build Excel report
6. Show key KPIs
7. Exit
------------------------------------
```

### One-shot automatic run (no menu)

```bash
python src/main.py --auto
```

This loads `data/transactions.xlsx` (generating it automatically on first
run if it doesn't exist), cleans it, runs the full analysis, regenerates all
charts in `charts/`, rebuilds `reports/Finance_Report.xlsx`, refreshes
`docs/data/dashboard_data.json` for the [live website](#-live-interactive-dashboard-github-pages),
and prints the key KPIs to the console.

From the interactive menu, option **5 (Build Excel report)** also refreshes
the website's data file.

### Using your own data

Replace `data/transactions.xlsx` with your own file using the same columns:

| Date | Type | Category | Description | Amount | Payment Method | Month |
|------|------|----------|--------------|--------|-----------------|-------|
| 2026-01-02 | Expense | Food | McDonald's | 5600 | Card | January |
| 2026-01-05 | Income | Salary | January salary | 450000 | Bank | January |

Then run `python src/main.py --auto` (or use the menu).

### Regenerating just the sample data

```bash
python src/generate_sample_data.py
```

---

## Running the tests

```bash
pytest
```

Test coverage includes: Excel loading (valid file, missing file, missing
columns), data cleaning (duplicates, empty rows, negative amounts, invalid
dates, month recomputation), analytics (totals, category breakdowns,
monthly profit, payment methods, full pipeline), Excel report generation
(file creation, sheet presence, row counts), and sample data generation.

---




## License

This project is provided as-is for portfolio and educational purposes.
