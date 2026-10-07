# 👥 HR Analytics Dashboard

An interactive **Tableau** dashboard that analyses employee attrition — who is leaving the company, from which departments, and what patterns sit behind it.

![Tableau](https://img.shields.io/badge/Tableau-E97627?style=flat-square&logo=tableau&logoColor=white)
![Excel](https://img.shields.io/badge/Excel-217346?style=flat-square&logo=microsoft-excel&logoColor=white)

## 📋 Overview

Losing employees is expensive. This dashboard helps HR teams understand attrition at a glance and spot the groups most at risk, using a dataset of **1,470 employees** with **39 attributes** each.

## 📈 Visuals

The first image is the dashboard preview stored in the workbook. Charts built with Python (pandas + matplotlib) from the data files in this repo.

<p align="center"><img src="docs/images/tableau_preview.png" alt="Preview of the Tableau HR Analytics dashboard" width="384"></p>
<p align="center"><sub>Dashboard preview saved inside the Tableau workbook (top-left section)</sub></p>

<p align="center"><img src="docs/images/attrition_department.png" alt="Attrition rate by department" width="85%"></p>

<p align="center"><img src="docs/images/attrition_age.png" alt="Attrition rate by age band" width="85%"></p>

## 🗂️ Dataset

`HR Data.xlsx` — one row per employee, including:

- **Demographics:** age, age band, gender, marital status, education field
- **Role:** department (R&D, Sales, HR), job role, job level, business travel, overtime
- **Pay:** monthly income, hourly/daily rate, salary hike, stock option level
- **Experience:** total working years, years at company, years in current role, years since last promotion
- **Satisfaction:** job, environment and relationship satisfaction, work-life balance, performance rating
- **Attrition:** whether the employee left (237 of 1,470 did — about **16%**)

## 📊 Dashboard Views

| View | What it shows |
|------|---------------|
| **KPI** | Headline numbers such as employee count, attrition count, attrition rate, active employees and average age |
| **Department Attrition** | Attrition split by department |
| **No. of Employees by Age Group** | Workforce age distribution |
| **Job Satisfaction Rating** | Breakdown of job satisfaction ratings |
| **Education Attrition** | Attrition by education field |
| **Attrition Rate by Gender for Different Age Groups** | Gender × age breakdown of attrition |
| **Attrition by Gender** | Overall attrition split by gender |

## 📁 Repository Contents

```
├── HR Analytics Dashboard.twb   # Tableau workbook
├── HR Data.xlsx                 # Employee dataset
└── README.md
```

## 🚀 How to Use

1. Download both files into the same folder.
2. Open `HR Analytics Dashboard.twb` in **Tableau Desktop** or **[Tableau Public](https://public.tableau.com/app/discover)**.
3. If Tableau asks for the data source, point it to `HR Data.xlsx`.

## 🛠️ Skills Demonstrated

Calculated fields (age bands, attrition labels) · KPI cards · dashboard design · HR analytics · data storytelling

---

👤 **Tony Mulunda** — [GitHub @Scarface96](https://github.com/Scarface96)
