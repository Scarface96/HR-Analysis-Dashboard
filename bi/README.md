# 📊 HR Analytics: Tableau & Power BI kit

Everything needed to rebuild this project as a Power BI dashboard in under an hour: model-ready data, ready-to-paste DAX measures, a matching colour theme, a page-by-page layout, and the exact numbers your finished dashboard should show.

> **Interactive web version:** [scarface96.github.io/HR-Analysis-Dashboard](https://scarface96.github.io/HR-Analysis-Dashboard/). The kit uses the same cleaned data, so the numbers will match.

> **Tableau version:** already built, see [`HR Analytics Dashboard.twb`](../HR%20Analytics%20Dashboard.twb). This kit adds the Power BI version.

## What's in this folder

| File | What it is |
|---|---|
| `data/fact_employee.csv` | one row per employee (1,470): attrition, department, role, demographics, pay, tenure, travel, overtime, satisfaction scores with labels, and sort keys for the age, income and tenure bands |
| `powerbi/measures.dax` | Every DAX measure, with its number format |
| `powerbi/theme.json` | Report theme in the portfolio's teal-and-amber colours |
| `kpis.json` | Headline numbers, for checking your build |
| `build_bi.py` | Regenerates everything here from the repo's own cleaning code: `python -m bi.build_bi` |

## Dashboard design

Canvas 1280 × 720. Light page background, white cards, teal for the main series, amber to highlight, red only for bad news.

### Page 1: Workforce overview
*Who works here, and how many leave?*

- KPI cards: Employees · Attrition Count · Attrition Rate · Active Employees · Avg Age
- Bar chart: Attrition Rate by department, constant line at Company Attrition Rate
- Bar chart: Attrition Count by job_role, sorted descending
- Column chart: Attrition Rate by age_band; donut: Employees by gender

### Page 2: Attrition drivers
*What separates leavers from stayers?*

- Clustered bars: Attrition Rate by over_time, travel_frequency, income_band, tenure_band
- Matrix heatmap: rows job_satisfaction_label, columns department, values Attrition Rate
- Card: Replacement Cost (est.) with the assumption in the subtitle

### Page 3: Employee detail
*Drill into any group*

- Table: employee_number, department, job_role, age, monthly_income, years_at_company, over_time, attrition
- Slicers: department, job_role, attrition, over_time

## Build it in Power BI

1. **Get data → Text/CSV** and load each file in `bi/data/`. Check that date columns come in as *Date* and IDs as *Whole number* or *Text*.
2. **Column tools → Sort by column**: `age_band` by `age_band_order`, `income_band` by `income_band_order`, `tenure_band` by `tenure_band_order`.
3. **Home → Enter data**, name the table `_Measures`, load it, then add each measure from `powerbi/measures.dax` and set the format given above it.
4. **View → Themes → Browse for themes** → `powerbi/theme.json`.
5. Build the pages above. Add a title text box on each page with the question it answers.
6. Check your cards against **Check your numbers** below.
7. Save as `HR Analytics.pbix` in the repo root.

## Check your numbers

Your finished dashboard (no filters applied) should show:

| Measure | Value |
|---|---|
| Employees | 1,470 |
| Employees who left | 237 |
| Attrition rate | 16.1% |
| Active employees | 1,233 |
| Average age | 36.9 |
| Average monthly income | 6,503 |
| Highest-attrition department | Sales (20.6%) |
| Attrition with overtime | 30.5% |
| Attrition without overtime | 10.4% |
| Estimated replacement cost (half a year's salary) | 6,807,246 |

If a number is off, the usual causes are a relationship pointing the wrong way, a date column loaded as text, or a missing join.

## Notes on the data

- Set **Sort by column** for the bands (Column tools → Sort by column): `age_band` by `age_band_order`, `income_band` by `income_band_order`, `tenure_band` by `tenure_band_order`. Otherwise they sort alphabetically.

## Publish and show it off

- **Power BI:** *Publish to web* needs a work or school account. Without one, add a screenshot of each page to `docs/images/` and link the `.pbix` from the README.
- Take a 1280 × 720 screenshot of page 1 and put it at the top of the main README, so it's the first thing a recruiter sees.
