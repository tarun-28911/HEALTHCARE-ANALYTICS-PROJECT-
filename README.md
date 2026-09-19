# Healthcare Analytics Project — Patient, Visit & Hospital Operations Analysis

## 📌 Project Overview

This project analyzes a healthcare dataset to understand **patient demographics, hospital visits, admissions, diagnoses, billing, laboratory testing, prescriptions, doctors, and staff operations**.

The project follows an end-to-end analytics workflow:

**Raw Data → Data Cleaning & Transformation → Exploratory Data Analysis → Visualization → KPI Analysis → Business Insights → Dashboard-ready Dataset**

The analysis was performed in **Python** using Pandas, NumPy, Matplotlib, and Seaborn.

> **Note:** The data used in this portfolio project is synthetic/anonymized-style data for learning and demonstration purposes. It should not be treated as real clinical or financial healthcare data.

---

## 🎯 Business Objective

Healthcare organizations generate data across multiple operational areas. The objective of this project is to convert that raw data into useful information that can help stakeholders understand:

- How many patients and visits are being handled
- Which visit types generate the most billing
- Which diagnoses occur most frequently
- How patient demand varies by city, age group, gender, and insurance
- How admissions are distributed across admission types and wards
- Laboratory testing volume and abnormal-result patterns
- Prescription and medication-cost activity
- Length of stay and billing behavior
- Monthly visit and revenue trends
- Operational KPIs across patients, visits, admissions, doctors, staff, labs, and prescriptions

---

## 🗂️ Dataset Structure

The project works with seven CSV datasets:

| Dataset | Purpose |
|---|---|
| `patients.csv` | Patient demographics, city, insurance, registration date |
| `visits.csv` | Visits, visit type, diagnosis, bill amount, length of stay |
| `admissions.csv` | Admission type, ward, discharge status |
| `doctors.csv` | Doctor information and specialty |
| `lab_tests.csv` | Laboratory tests, results, reference ranges, abnormal flags |
| `prescriptions.csv` | Medicines, dosage, days supplied, unit cost |
| `staff.csv` | Department, role, shift, experience and salary |

---

## 🛠️ Tools & Technologies

- **Python**
- **Pandas** — data loading, cleaning, transformation, grouping and aggregation
- **NumPy** — numerical calculations
- **Matplotlib** — visualization
- **Seaborn** — statistical/data visualization
- **Jupyter Notebook** — analysis environment

---

## 🔄 Project Workflow

### 1. Data Loading

The seven CSV files are loaded into separate Pandas DataFrames.

### 2. Data Quality Checks

I checked:

- Dataset shape
- Column names
- Data types
- Missing values
- Missing-value percentages
- Duplicate records
- Unique categorical values
- Descriptive statistics

### 3. Data Cleaning

Examples of transformations performed:

- Standardized categorical text using `.str.strip()` and `.str.title()`
- Converted date columns to datetime using `pd.to_datetime()`
- Converted numeric columns using `pd.to_numeric(..., errors="coerce")`
- Handled missing values with business-readable placeholders where appropriate
- Standardized ID data types before merging datasets
- Created age groups using `pd.cut()`
- Created laboratory result status using reference ranges
- Aggregated laboratory and prescription information at visit level

### 4. Data Integration

A visit-level master dataset was created by combining:

- Visits
- Patients
- Doctors
- Laboratory summaries
- Prescription summaries

The analysis used common identifiers such as `Patient_ID`, `Doctor_ID`, and `Visit_ID`.

### 5. Exploratory Data Analysis

The analysis covered:

- Patient demographics
- Age distribution
- Age groups
- Gender
- City distribution
- Insurance type
- Visit type
- Diagnosis frequency
- Revenue by visit type
- Length of stay
- Admission type
- Ward distribution
- Discharge status
- Doctor specialties
- Laboratory test volume
- Laboratory result status
- Prescription activity
- Monthly visits
- Monthly revenue
- Diagnosis-level revenue
- Correlation and outlier analysis

---

## 📊 Key Project KPIs

Based on the analyzed notebook:

| KPI | Value |
|---|---:|
| Total Patients | 50,000 |
| Total Visits | 180,000 |
| Total Admissions | 50,000 |
| Total Doctors | 5,000 |
| Total Staff | 10,000 |
| Total Lab Tests | 250,000 |
| Total Prescriptions | 220,000 |
| Total Visit Billing | ₹1,892,730,347.98 |
| Average Bill | ₹10,515.17 |
| Average Length of Stay | 7.49 days |
| Abnormal Lab Test Rate | 22.094% |
| Total Medication Cost | ₹4,018,389,711.14 |

---

## 🔎 Selected Findings

### Patient profile

The patient dataset contains **50,000 patients**. The data covers seven cities: Bengaluru, Chennai, Mumbai, Pune, Hyderabad, Kolkata and Delhi.

Insurance categories include:

- Corporate
- Self Pay
- Government
- Private

Gender values were standardized from inconsistent formats such as `female`, `FEMALE`, and values containing extra spaces into consistent categories.

### Visit activity

There are **180,000 visits** distributed across:

- Inpatient
- Emergency
- Outpatient
- Follow-Up

The counts are relatively close across the four visit types.

### Diagnoses

Eight diagnosis categories were standardized:

- Routine Check
- Heart Disease
- Asthma
- Migraine
- Fracture
- Hypertension
- Infection
- Diabetes

`Routine Check` has the highest visit count in the analyzed data with **22,912 visits**.

### Revenue

Total visit billing is approximately **₹1.89 billion**, with an average bill of approximately **₹10,515**.

Among visit types, **Inpatient** has the highest total billing in the analysis, followed closely by Emergency, Outpatient and Follow-Up.

### Length of stay

Average length of stay is approximately **7.49 days**, with values ranging from 0 to 15 days.

The project also examines the relationship between length of stay and bill amount rather than assuming that longer stay automatically means higher billing.

### Laboratory analysis

The project contains **250,000 laboratory test records** across nine test types.

A result-status field was created using the test result and reference range:

- Low
- Normal
- High

The notebook reports an abnormal-test rate of **22.094%** based on the `Abnormal_Flag` field.

### Admissions

There are **50,000 admissions**.

Admission types include:

- Elective
- Transfer
- Emergency

The project also analyzes ward distribution and discharge status.

### Workforce

The staff dataset contains **10,000 staff records**, covering departments such as:

- Administration
- Emergency
- Nursing
- Pharmacy
- Surgery
- Diagnostics

Roles include Manager, Coordinator, Assistant, Nurse, Technician and Pharmacist.

---

## 📈 Visualizations Created

The notebook includes visual analysis such as:

- Patient distribution by gender
- Patient age distribution
- Patients by age group
- Patient count by city
- Patient distribution by insurance
- Visits by visit type
- Top diagnoses
- Revenue by visit type
- Length-of-stay distribution
- Bill amount vs length of stay
- Admissions by admission type
- Admissions by ward
- Discharge status distribution
- Doctor specialties
- Laboratory test volume
- Laboratory result status
- Monthly visit trend
- Monthly healthcare revenue trend
- Diagnosis-level revenue
- Correlation heatmap
- Bill amount outlier analysis
- Length-of-stay outlier analysis

---

## 💼 Business Value

The analysis can support stakeholder questions around:

**Patient Management**
- Who are the patients being served?
- Which cities and demographic groups contribute to demand?
- What insurance categories are represented?

**Hospital Operations**
- What types of visits are most common?
- How many admissions are occurring?
- How is demand distributed across wards?

**Financial Analysis**
- What is the total billing?
- What is the average bill?
- Which visit types and diagnoses contribute to revenue?

**Clinical/Diagnostic Operations**
- What tests are being performed most often?
- What proportion of test results are abnormal?
- Which diagnoses and visit patterns require further investigation?

**Resource Planning**
- What is the average length of stay?
- What is the distribution of staff across departments, roles and shifts?
- Where could operational monitoring be useful?

---

## 📁 Suggested GitHub Repository Structure

```text
healthcare-analytics-python/
│
├── Healthcare_Analytics_Project.ipynb
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── patients.csv
│   ├── visits.csv
│   ├── admissions.csv
│   ├── doctors.csv
│   ├── lab_tests.csv
│   ├── prescriptions.csv
│   └── staff.csv
│
└── dashboard/
    └── app.py
```

For GitHub, do **not** upload real patient-identifiable information. Use synthetic/anonymized data only.

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd healthcare-analytics-python
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Jupyter Notebook

```bash
jupyter notebook
```

Open:

```text
Healthcare_Analytics_Project.ipynb
```

---

## 📦 Requirements

```text
pandas
numpy
matplotlib
seaborn
jupyter
```

---

## 🧠 Interview / Stakeholder Story

A simple way to explain the project:

> "I worked on a healthcare analytics project where the goal was to turn raw healthcare operational data into meaningful business insights. I worked with seven datasets covering patients, visits, admissions, doctors, lab tests, prescriptions and staff.
>
> I first performed data-quality checks for missing values, duplicates, inconsistent categories and incorrect data types. I standardized categorical fields, converted date columns, handled missing values and created useful derived fields such as age groups and laboratory result status.
>
> After cleaning, I integrated the datasets using patient, doctor and visit identifiers. I then performed exploratory data analysis to understand patient demographics, visit patterns, diagnoses, hospital admissions, billing, laboratory activity and operational metrics.
>
> Some of the main KPIs were 50,000 patients, 180,000 visits, 50,000 admissions and approximately ₹1.89 billion in visit billing. I also calculated an average bill of about ₹10,515 and an average length of stay of about 7.49 days.
>
> Finally, I converted the analysis into visual insights so that a stakeholder can quickly understand patient demand, revenue patterns, diagnostic activity and operational performance. The main value of the project is not just the charts, but the complete process of converting raw data into decision-support information."

---

## 👤 Author

**Tarun Sahani**  
Data Analyst Portfolio Project  
Python | Pandas | NumPy | Matplotlib | Seaborn

