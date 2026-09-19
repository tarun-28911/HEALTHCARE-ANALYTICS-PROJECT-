"""
Healthcare Analytics Dashboard
Rebuilt from the Jupyter notebook analysis (patients, visits, admissions,
doctors, lab_tests, prescriptions, staff) into an interactive Streamlit app.
"""

import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------
# PAGE CONFIG & STYLE
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .kpi-label {
        font-size: 15px;
        color: #6b7280;
        margin: 0 0 4px 0;
        font-weight: 500;
    }
    .kpi-value {
        font-size: 34px;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1f2937;
        margin-top: 26px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CHART_PALETTES = {
    "gender": px.colors.qualitative.Set2,
    "age": px.colors.sequential.Viridis,
    "age_group": px.colors.qualitative.Pastel,
    "city": px.colors.sequential.Teal,
    "insurance": px.colors.qualitative.Bold,
    "visit_type": px.colors.qualitative.Prism,
    "diagnosis": px.colors.sequential.Sunset,
    "revenue": px.colors.sequential.Plasma,
    "los": px.colors.sequential.Blues,
    "admission_type": px.colors.qualitative.Safe,
    "ward": px.colors.qualitative.Vivid,
    "discharge": px.colors.qualitative.Set3,
    "specialty": px.colors.qualitative.Alphabet,
    "lab_test": px.colors.sequential.Agsunset,
    "lab_result": {"Normal": "#1CC88A", "High": "#E74C3C", "Low": "#F6A609"},
    "trend": px.colors.qualitative.D3,
}


def smart_parse_dates(series):
    """Try dayfirst=True and dayfirst=False, keep whichever parses more rows.
    Falls back to pandas' own format inference if both mostly fail."""
    if series.isna().all():
        return series
    candidates = []
    for dayfirst in (True, False):
        parsed = pd.to_datetime(series, dayfirst=dayfirst, errors="coerce")
        candidates.append((parsed.notna().sum(), parsed))
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_count, best = candidates[0]
    if best_count == 0:
        # last resort: let pandas infer without dayfirst hints
        best = pd.to_datetime(series, errors="coerce")
    return best


def kpi_card(label, value, color=None):
    st.markdown(
        f"""
        <div>
            <p class="kpi-label">{label}</p>
            <p class="kpi-value">{value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------
REQUIRED_FILES = {
    "patients": ["patient"],
    "visits": ["visit"],
    "admissions": ["admission"],
    "doctors": ["doctor"],
    "lab_tests": ["lab"],
    "prescriptions": ["prescription"],
    "staff": ["staff"],
}


@st.cache_data(show_spinner=False)
def read_csv_bytes(name, data_bytes):
    return pd.read_csv(io.BytesIO(data_bytes))


def match_uploaded_files(uploaded_files):
    """Match uploaded files to the expected dataset names by filename keywords."""
    matched = {}
    for f in uploaded_files:
        fname = f.name.lower()
        for key, keywords in REQUIRED_FILES.items():
            if key in matched:
                continue
            if any(kw in fname for kw in keywords):
                matched[key] = read_csv_bytes(key, f.getvalue())
                break
    return matched


@st.cache_data(show_spinner=False)
def clean_data(raw):
    """Replicate the cleaning/feature-engineering steps from the notebook."""
    patients = raw["patients"].copy()
    visits = raw["visits"].copy()
    admissions = raw["admissions"].copy()
    doctors = raw["doctors"].copy()
    lab_tests = raw["lab_tests"].copy()
    prescriptions = raw["prescriptions"].copy()
    staff = raw.get("staff")

    # ---- patients ----
    if "Gender" in patients:
        patients["Gender"] = (
            patients["Gender"].astype("string").str.strip().str.title()
        )
        patients["Gender"] = patients["Gender"].fillna("Unknown")
    if "Patient_Name" in patients:
        patients["Patient_Name"] = patients["Patient_Name"].fillna("Unknown")
    if "Age" in patients:
        patients["Age"] = pd.to_numeric(patients["Age"], errors="coerce")
        patients["Age"] = patients["Age"].fillna(patients["Age"].median())
    if "Registration_Date" in patients:
        patients["Registration_Date"] = smart_parse_dates(patients["Registration_Date"])
    if "Age" in patients:
        patients["Age_Group"] = pd.cut(
            patients["Age"],
            bins=[0, 18, 35, 50, 65, 150],
            labels=["0-18", "19-35", "36-50", "51-65", "65+"],
        )
    if "Patient_ID" in patients:
        patients["Patient_ID"] = patients["Patient_ID"].astype("string")

    # ---- visits ----
    for col in ["Visit_Type", "Diagnosis"]:
        if col in visits:
            visits[col] = visits[col].astype("string").str.strip().str.title()
    if "Patient_ID" in visits:
        visits["Patient_ID"] = visits["Patient_ID"].astype("string")
    if "Doctor_ID" in visits:
        visits["Doctor_ID"] = visits["Doctor_ID"].astype("string").str.strip()
    if "Visit_Date" in visits:
        visits["Visit_Date"] = smart_parse_dates(visits["Visit_Date"])
        visits["Visit_Year"] = visits["Visit_Date"].dt.year
        visits["Visit_Month"] = visits["Visit_Date"].dt.month
        visits["Month_Name"] = visits["Visit_Date"].dt.month_name()
        visits["Day_Name"] = visits["Visit_Date"].dt.day_name()
        visits["Visit_Hour"] = (
            visits["Visit_Date"].dt.hour if visits["Visit_Date"].dt.hour.nunique() > 1 else np.nan
        )

    # ---- admissions ----
    for col in ["Admission_Date", "Discharge_Date"]:
        if col in admissions:
            admissions[col] = smart_parse_dates(admissions[col])

    # ---- doctors ----
    if "Doctor_ID" in doctors:
        doctors["Doctor_ID"] = doctors["Doctor_ID"].astype("string").str.strip()

    # ---- lab_tests ----
    if "Test_Date" in lab_tests:
        lab_tests["Test_Date"] = smart_parse_dates(lab_tests["Test_Date"])
    if {"Result_Value", "Reference_Low", "Reference_High"}.issubset(lab_tests.columns):
        lab_tests["Result_Status"] = np.select(
            [
                lab_tests["Result_Value"] < lab_tests["Reference_Low"],
                lab_tests["Result_Value"] > lab_tests["Reference_High"],
            ],
            ["Low", "High"],
            default="Normal",
        )
    if "Abnormal_Flag" not in lab_tests.columns and "Result_Status" in lab_tests.columns:
        lab_tests["Abnormal_Flag"] = (lab_tests["Result_Status"] != "Normal").astype(int)

    # ---- prescriptions ----
    if {"Days_Supply", "Unit_Cost"}.issubset(prescriptions.columns):
        prescriptions["Total_Cost"] = prescriptions["Days_Supply"] * prescriptions["Unit_Cost"]

    # ---- merges ----
    patient_visits = visits.merge(patients, on="Patient_ID", how="left") if "Patient_ID" in visits and "Patient_ID" in patients else visits.copy()
    if "Doctor_ID" in patient_visits.columns and "Doctor_ID" in doctors.columns:
        patient_visits = patient_visits.merge(doctors, on="Doctor_ID", how="left")

    lab_summary = pd.DataFrame()
    if "Visit_ID" in lab_tests.columns:
        agg = {"Total_Tests": ("Lab_Test_ID", "count")}
        if "Abnormal_Flag" in lab_tests.columns:
            agg["Abnormal_Tests"] = ("Abnormal_Flag", "sum")
        if "Result_Value" in lab_tests.columns:
            agg["Average_Result"] = ("Result_Value", "mean")
        lab_summary = lab_tests.groupby("Visit_ID").agg(**agg).reset_index()

    prescription_summary = pd.DataFrame()
    if "Visit_ID" in prescriptions.columns:
        prescription_summary = (
            prescriptions.groupby("Visit_ID")
            .agg(Total_Prescriptions=("Prescription_ID", "count"))
            .reset_index()
        )

    master = visits.merge(patients, on="Patient_ID", how="left") if "Patient_ID" in visits and "Patient_ID" in patients else visits.copy()
    if "Doctor_ID" in master.columns and "Doctor_ID" in doctors.columns:
        master = master.merge(doctors, on="Doctor_ID", how="left")
    if not lab_summary.empty:
        master = master.merge(lab_summary, on="Visit_ID", how="left")
        for c in ["Total_Tests", "Abnormal_Tests"]:
            if c in master.columns:
                master[c] = master[c].fillna(0)
    if not prescription_summary.empty:
        master = master.merge(prescription_summary, on="Visit_ID", how="left")
        if "Total_Prescriptions" in master.columns:
            master["Total_Prescriptions"] = master["Total_Prescriptions"].fillna(0)

    return {
        "patients": patients,
        "visits": visits,
        "admissions": admissions,
        "doctors": doctors,
        "lab_tests": lab_tests,
        "prescriptions": prescriptions,
        "staff": staff,
        "patient_visits": patient_visits,
        "master": master,
    }


# ----------------------------------------------------------------------
# DATA SOURCE — auto-loaded, no upload UI
# ----------------------------------------------------------------------
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@st.cache_data(show_spinner=False)
def load_local_csvs(data_dir):
    """Look for the 7 CSVs in a local ./data folder next to this script."""
    found = {}
    if not os.path.isdir(data_dir):
        return found
    for fname in os.listdir(data_dir):
        if not fname.lower().endswith(".csv"):
            continue
        lower = fname.lower()
        for key, keywords in REQUIRED_FILES.items():
            if key in found:
                continue
            if any(kw in lower for kw in keywords):
                found[key] = pd.read_csv(os.path.join(data_dir, fname))
                break
    return found


raw = load_local_csvs(DATA_DIR)
if not raw or "patients" not in raw or "visits" not in raw:
    from sample_data import generate_sample_data
    raw = generate_sample_data()

data = clean_data(raw)
patients, visits, admissions, doctors = data["patients"], data["visits"], data["admissions"], data["doctors"]
lab_tests, prescriptions, staff = data["lab_tests"], data["prescriptions"], data["staff"]
patient_visits, master = data["patient_visits"], data["master"]

# ----------------------------------------------------------------------
# SIDEBAR — FILTERS
# ----------------------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="padding-bottom: 6px;">
        <span style="font-size: 26px;">🏥</span>
        <span style="font-size: 20px; font-weight: 700; color: #1f2937;"> Healthcare Analytics</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.caption("Filter the dashboard below")
st.sidebar.markdown("---")

if "Visit_Date" in visits.columns and visits["Visit_Date"].notna().any():
    min_date = visits["Visit_Date"].min().date()
    max_date = visits["Visit_Date"].max().date()
    n_bad_dates = visits["Visit_Date"].isna().sum()
    if n_bad_dates > 0:
        st.sidebar.caption(f"⚠️ {n_bad_dates} of {len(visits)} visit dates couldn't be parsed and are excluded.")
else:
    min_date = max_date = pd.Timestamp.today().date()
    st.sidebar.error(
        "⚠️ Couldn't parse any dates in the visits file's Visit_Date column — "
        "check that column exists and contains valid dates. Filters below won't "
        "match your data until this is fixed."
    )

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

month_opts = (
    list(pd.Series(pd.date_range(min_date, max_date, freq="MS")).dt.strftime("%B %Y"))
    if "Visit_Date" in visits.columns and visits["Visit_Date"].notna().any()
    else []
)
month_sel = st.sidebar.multiselect("Month", month_opts, default=month_opts)

granularity = "Monthly"
GRAN_MAP = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}

# ----------------------------------------------------------------------
# APPLY FILTERS
# ----------------------------------------------------------------------
def in_date_range(df, col):
    if col not in df.columns:
        return pd.Series(True, index=df.index)
    return (df[col].dt.date >= start_date) & (df[col].dt.date <= end_date)


mask_v = in_date_range(visits, "Visit_Date")
if month_opts and len(month_sel) < len(month_opts) and "Visit_Date" in visits.columns:
    mask_v &= visits["Visit_Date"].dt.strftime("%B %Y").isin(month_sel)

f_visits = visits[mask_v].copy()
visit_ids = set(f_visits["Visit_ID"]) if "Visit_ID" in f_visits.columns else set()
patient_ids_in_scope = set(f_visits["Patient_ID"]) if "Patient_ID" in f_visits.columns else set()

f_patients = patients[patients["Patient_ID"].isin(patient_ids_in_scope)] if "Patient_ID" in patients.columns else patients
f_admissions = admissions[in_date_range(admissions, "Admission_Date")]
f_lab_tests = lab_tests[lab_tests["Visit_ID"].isin(visit_ids)] if "Visit_ID" in lab_tests.columns else lab_tests[in_date_range(lab_tests, "Test_Date")]
f_prescriptions = prescriptions[prescriptions["Visit_ID"].isin(visit_ids)] if "Visit_ID" in prescriptions.columns and visit_ids else prescriptions
f_master = master[master["Visit_ID"].isin(visit_ids)] if "Visit_ID" in master.columns else master
f_patient_visits = patient_visits[patient_visits["Visit_ID"].isin(visit_ids)] if "Visit_ID" in patient_visits.columns else patient_visits

if f_visits.empty:
    st.warning("No data matches the current filters. Try widening the date range or filters.")
    st.stop()

# ----------------------------------------------------------------------
# HEADER + KPIs
# ----------------------------------------------------------------------
st.markdown(
    """
    <div style="padding-bottom: 4px;">
        <span style="font-size: 40px;">🏥</span>
        <span style="font-size: 38px; font-weight: 800; color: #1f2937;"> Healthcare Analytics Dashboard</span>
    </div>
    <p style="color: #6b7280; font-size: 16px; margin-top: 0;">
        End-to-end operational &amp; financial insights across patients, visits, admissions and labs
    </p>
    """,
    unsafe_allow_html=True,
)
st.caption(f"📅 {start_date.strftime('%d %b %Y')} → {end_date.strftime('%d %b %Y')}  ·  {len(f_visits):,} visits in scope")

total_patients = f_patients["Patient_ID"].nunique() if "Patient_ID" in f_patients.columns else 0
total_visits = f_visits["Visit_ID"].nunique() if "Visit_ID" in f_visits.columns else len(f_visits)
total_admissions = f_admissions["Admission_ID"].nunique() if "Admission_ID" in f_admissions.columns else len(f_admissions)
total_revenue = f_visits["Bill_Amount"].sum() if "Bill_Amount" in f_visits.columns else 0
avg_bill = f_visits["Bill_Amount"].mean() if "Bill_Amount" in f_visits.columns else 0
avg_los = f_visits["Length_of_Stay"].mean() if "Length_of_Stay" in f_visits.columns else 0
total_lab_tests = f_lab_tests["Lab_Test_ID"].nunique() if "Lab_Test_ID" in f_lab_tests.columns else len(f_lab_tests)
abnormal_rate = f_lab_tests["Abnormal_Flag"].mean() * 100 if "Abnormal_Flag" in f_lab_tests.columns and len(f_lab_tests) else 0
total_med_cost = f_prescriptions["Total_Cost"].sum() if "Total_Cost" in f_prescriptions.columns else 0
total_doctors = doctors["Doctor_ID"].nunique() if "Doctor_ID" in doctors.columns else 0

kpis = [
    ("Total Patients", f"{total_patients:,}"),
    ("Total Doctors", f"{total_doctors:,}"),
    ("Total Visits", f"{total_visits:,}"),
    ("Total Admissions", f"{total_admissions:,}"),
    ("Total Revenue", f"${total_revenue:,.0f}"),
    ("Average Bill", f"${avg_bill:,.0f}"),
    ("Avg Length of Stay", f"{avg_los:,.1f} days"),
    ("Total Lab Tests", f"{total_lab_tests:,}"),
    ("Abnormal Test Rate", f"{abnormal_rate:,.1f}%"),
    ("Total Medication Cost", f"${total_med_cost:,.0f}"),
]

cols = st.columns(5)
for i, (label, value) in enumerate(kpis):
    with cols[i % 5]:
        kpi_card(label, value)
    if i % 5 == 4 and i != len(kpis) - 1:
        cols = st.columns(5)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------
tab_overview, tab_patients, tab_revenue, tab_admissions, tab_doctors_labs, tab_trends = st.tabs(
    ["📊 Overview", "🧑‍🤝‍🧑 Patients", "💰 Revenue & Visits", "🏨 Admissions", "🩺 Doctors & Labs", "📈 Trends & Correlations"]
)

# ---- OVERVIEW ----
with tab_overview:
    section("Visit Type Breakdown")
    c1, c2 = st.columns(2)
    with c1:
        if "Visit_Type" in f_visits.columns:
            vc = f_visits["Visit_Type"].value_counts().reset_index()
            vc.columns = ["Visit_Type", "Count"]
            fig = px.bar(vc, x="Visit_Type", y="Count", color="Visit_Type",
                         color_discrete_sequence=CHART_PALETTES["visit_type"],
                         text="Count", title="Visits by Visit Type")
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True, key="chart_1")
    with c2:
        if "Diagnosis" in f_visits.columns:
            dc = f_visits["Diagnosis"].value_counts().head(10).sort_values(ascending=True).reset_index()
            dc.columns = ["Diagnosis", "Count"]
            fig = px.bar(dc, x="Count", y="Diagnosis", orientation="h",
                         color="Count", color_continuous_scale=CHART_PALETTES["diagnosis"],
                         text="Count", title="Top 10 Diagnoses by Visits")
            st.plotly_chart(fig, use_container_width=True, key="chart_2")

    section("Admissions & Discharges")
    c3, c4 = st.columns(2)
    with c3:
        if "Admission_Type" in f_admissions.columns:
            ac = f_admissions["Admission_Type"].value_counts().reset_index()
            ac.columns = ["Admission_Type", "Count"]
            fig = px.bar(ac, x="Admission_Type", y="Count", color="Admission_Type",
                         color_discrete_sequence=CHART_PALETTES["admission_type"],
                         text="Count", title="Admissions by Type")
            st.plotly_chart(fig, use_container_width=True, key="chart_3")
    with c4:
        if "Discharge_Status" in f_admissions.columns:
            dsc = f_admissions["Discharge_Status"].value_counts().reset_index()
            dsc.columns = ["Discharge_Status", "Count"]
            fig = px.bar(dsc, x="Discharge_Status", y="Count", color="Discharge_Status",
                         color_discrete_sequence=CHART_PALETTES["discharge"],
                         text="Count", title="Discharge Status Distribution")
            st.plotly_chart(fig, use_container_width=True, key="chart_4")

# ---- PATIENTS ----
with tab_patients:
    section("Demographics")
    c1, c2 = st.columns(2)
    with c1:
        if "Gender" in f_patients.columns:
            gc = f_patients["Gender"].value_counts().reset_index()
            gc.columns = ["Gender", "Count"]
            fig = px.bar(gc, x="Gender", y="Count", color="Gender", text="Count",
                         color_discrete_sequence=CHART_PALETTES["gender"],
                         title="Patient Distribution by Gender")
            st.plotly_chart(fig, use_container_width=True, key="chart_5")
    with c2:
        if "Age" in f_patients.columns:
            median_age = f_patients["Age"].median()
            fig = px.histogram(f_patients, x="Age", nbins=20,
                                color_discrete_sequence=[CHART_PALETTES["age"][3]],
                                title="Patient Age Distribution")
            fig.add_vline(x=median_age, line_dash="dash", line_color="red",
                          annotation_text=f"Median: {median_age:.1f}")
            st.plotly_chart(fig, use_container_width=True, key="chart_6")

    c3, c4 = st.columns(2)
    with c3:
        if "Age_Group" in f_patients.columns:
            agc = f_patients["Age_Group"].value_counts().reset_index()
            agc.columns = ["Age_Group", "Count"]
            fig = px.bar(agc, x="Count", y="Age_Group", orientation="h", color="Age_Group",
                         color_discrete_sequence=CHART_PALETTES["age_group"],
                         text="Count", title="Patient Distribution by Age Group")
            st.plotly_chart(fig, use_container_width=True, key="chart_7")
    with c4:
        if "Insurance" in f_patients.columns:
            ic = f_patients["Insurance"].value_counts().reset_index()
            ic.columns = ["Insurance", "Count"]
            fig = px.bar(ic, x="Insurance", y="Count", color="Insurance", text="Count",
                         color_discrete_sequence=CHART_PALETTES["insurance"],
                         title="Patient Distribution by Insurance Type")
            st.plotly_chart(fig, use_container_width=True, key="chart_8")

    section("Top Cities")
    if "City" in f_patients.columns:
        top_cities = f_patients["City"].value_counts().head(10).sort_values(ascending=True).reset_index()
        top_cities.columns = ["City", "Count"]
        fig = px.bar(top_cities, x="Count", y="City", orientation="h", color="Count",
                     color_continuous_scale=CHART_PALETTES["city"],
                     text="Count", title="Top 10 Cities by Patient Count")
        st.plotly_chart(fig, use_container_width=True, key="chart_9")

# ---- REVENUE & VISITS ----
with tab_revenue:
    section("Revenue Summary")
    if "Bill_Amount" in f_visits.columns:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue", f"${f_visits['Bill_Amount'].sum():,.0f}")
        c2.metric("Average Bill", f"${f_visits['Bill_Amount'].mean():,.0f}")
        c3.metric("Median Bill", f"${f_visits['Bill_Amount'].median():,.0f}")
        c4.metric("Max Bill", f"${f_visits['Bill_Amount'].max():,.0f}")

    if {"Visit_Type", "Bill_Amount"}.issubset(f_visits.columns):
        revenue_by_visit = (
            f_visits.groupby("Visit_Type")["Bill_Amount"]
            .agg(["sum", "mean", "count"])
            .sort_values("sum", ascending=True)
            .reset_index()
        )
        fig = px.bar(revenue_by_visit, x="sum", y="Visit_Type", orientation="h",
                     color="sum", color_continuous_scale=CHART_PALETTES["revenue"],
                     text="sum", title="Revenue by Visit Type")
        fig.update_traces(texttemplate="%{text:,.0f}")
        st.plotly_chart(fig, use_container_width=True, key="chart_10")
        with st.expander("See revenue table (sum / mean / count)"):
            st.dataframe(revenue_by_visit.rename(columns={"sum": "Total Revenue", "mean": "Avg Bill", "count": "Visits"}),
                         use_container_width=True)

    section("Length of Stay")
    c5, c6 = st.columns(2)
    with c5:
        if "Length_of_Stay" in f_visits.columns:
            median_los = f_visits["Length_of_Stay"].median()
            fig = px.histogram(f_visits, x="Length_of_Stay", nbins=20,
                                color_discrete_sequence=[CHART_PALETTES["los"][4]],
                                title="Distribution of Length of Stay")
            fig.add_vline(x=median_los, line_dash="dash", line_color="red",
                          annotation_text=f"Median: {median_los:.1f} days")
            st.plotly_chart(fig, use_container_width=True, key="chart_11")
    with c6:
        if {"Length_of_Stay", "Bill_Amount"}.issubset(f_visits.columns):
            scatter_df = f_visits.dropna(subset=["Length_of_Stay", "Bill_Amount"])
            fig = px.scatter(scatter_df, x="Length_of_Stay", y="Bill_Amount", opacity=0.4,
                              color_discrete_sequence=["#6C63FF"],
                              title="Length of Stay vs Bill Amount")
            if len(scatter_df) >= 2:
                x_vals = scatter_df["Length_of_Stay"].to_numpy(dtype=float)
                y_vals = scatter_df["Bill_Amount"].to_numpy(dtype=float)
                slope, intercept = np.polyfit(x_vals, y_vals, 1)
                x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                y_line = slope * x_line + intercept
                fig.add_trace(go.Scatter(
                    x=x_line, y=y_line, mode="lines",
                    line=dict(color="#1f2937", width=2.5),
                    name="Trend",
                ))
            st.plotly_chart(fig, use_container_width=True, key="chart_12")

    section("Outliers")
    if "Bill_Amount" in f_visits.columns:
        c7, c8 = st.columns(2)
        with c7:
            fig = px.box(f_visits, y="Bill_Amount", color_discrete_sequence=["#FF6B6B"],
                         title="Bill Amount Distribution & Outliers")
            st.plotly_chart(fig, use_container_width=True, key="chart_13")
        with c8:
            if "Length_of_Stay" in f_visits.columns:
                fig = px.box(f_visits, y="Length_of_Stay", color_discrete_sequence=["#36B9CC"],
                             title="Length of Stay Distribution & Outliers")
                st.plotly_chart(fig, use_container_width=True, key="chart_14")

        Q1, Q3 = f_visits["Bill_Amount"].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        n_outliers = f_visits[(f_visits["Bill_Amount"] < lower) | (f_visits["Bill_Amount"] > upper)].shape[0]
        st.caption(f"📌 {n_outliers} visits flagged as Bill Amount outliers (IQR method).")

# ---- ADMISSIONS ----
with tab_admissions:
    section("Wards & Admission Types")
    c1, c2 = st.columns(2)
    with c1:
        if "Ward" in f_admissions.columns:
            wc = f_admissions["Ward"].value_counts().sort_values(ascending=True).reset_index()
            wc.columns = ["Ward", "Count"]
            fig = px.bar(wc, x="Count", y="Ward", orientation="h", color="Count",
                         color_continuous_scale=CHART_PALETTES["ward"] if isinstance(CHART_PALETTES["ward"], list) else None,
                         color_discrete_sequence=CHART_PALETTES["ward"],
                         text="Count", title="Admissions by Ward")
            st.plotly_chart(fig, use_container_width=True, key="chart_15")
    with c2:
        if "Admission_Type" in f_admissions.columns:
            atc = f_admissions["Admission_Type"].value_counts().reset_index()
            atc.columns = ["Admission_Type", "Count"]
            fig = px.pie(atc, names="Admission_Type", values="Count",
                         color_discrete_sequence=CHART_PALETTES["admission_type"],
                         title="Admission Type Share", hole=0.4)
            st.plotly_chart(fig, use_container_width=True, key="chart_16")

    section("Discharge Status")
    if "Discharge_Status" in f_admissions.columns:
        dsc = f_admissions["Discharge_Status"].value_counts().reset_index()
        dsc.columns = ["Discharge_Status", "Count"]
        fig = px.bar(dsc, x="Discharge_Status", y="Count", color="Discharge_Status", text="Count",
                     color_discrete_sequence=CHART_PALETTES["discharge"],
                     title="Discharge Status Distribution")
        st.plotly_chart(fig, use_container_width=True, key="chart_17")

# ---- DOCTORS & LABS ----
with tab_doctors_labs:
    section("Doctors")
    if "Specialty" in doctors.columns:
        spc = doctors["Specialty"].value_counts().reset_index()
        spc.columns = ["Specialty", "Count"]
        fig = px.bar(spc, x="Specialty", y="Count", color="Specialty", text="Count",
                     color_discrete_sequence=CHART_PALETTES["specialty"],
                     title="Doctors by Specialty")
        st.plotly_chart(fig, use_container_width=True, key="chart_18")

    section("Lab Tests")
    c1, c2 = st.columns(2)
    with c1:
        if "Test_Name" in f_lab_tests.columns:
            tc = f_lab_tests["Test_Name"].value_counts().sort_values(ascending=True).reset_index()
            tc.columns = ["Test_Name", "Count"]
            fig = px.bar(tc, x="Count", y="Test_Name", orientation="h", color="Count",
                         color_continuous_scale=CHART_PALETTES["lab_test"],
                         text="Count", title="Laboratory Tests by Type")
            st.plotly_chart(fig, use_container_width=True, key="chart_19")
    with c2:
        if "Result_Status" in f_lab_tests.columns:
            rc = f_lab_tests["Result_Status"].value_counts().reset_index()
            rc.columns = ["Result_Status", "Count"]
            fig = px.bar(rc, x="Result_Status", y="Count", color="Result_Status", text="Count",
                         color_discrete_map=CHART_PALETTES["lab_result"],
                         title="Lab Result Status Distribution")
            st.plotly_chart(fig, use_container_width=True, key="chart_20")

    section("Prescriptions")
    if "Drug_Name" in f_prescriptions.columns:
        drc = f_prescriptions["Drug_Name"].value_counts().head(10).sort_values(ascending=True).reset_index()
        drc.columns = ["Drug_Name", "Count"]
        fig = px.bar(drc, x="Count", y="Drug_Name", orientation="h", color="Count",
                     color_continuous_scale="Magma", text="Count",
                     title="Top 10 Prescribed Drugs")
        st.plotly_chart(fig, use_container_width=True, key="chart_21")

# ---- TRENDS & CORRELATIONS ----
with tab_trends:
    section(f"{granularity} Visit & Revenue Trend")
    if "Visit_Date" in f_visits.columns:
        trend = (
            f_visits.set_index("Visit_Date")
            .resample(GRAN_MAP[granularity])
            .agg(Visits=("Visit_ID", "count"), Revenue=("Bill_Amount", "sum"))
            .reset_index()
        )
        c1, c2 = st.columns(2)
        with c1:
            fig = px.line(trend, x="Visit_Date", y="Visits", markers=True,
                          color_discrete_sequence=[CHART_PALETTES["trend"][0]],
                          title=f"{granularity} Visit Trend")
            st.plotly_chart(fig, use_container_width=True, key="chart_22")
        with c2:
            fig = px.line(trend, x="Visit_Date", y="Revenue", markers=True,
                          color_discrete_sequence=[CHART_PALETTES["trend"][1]],
                          title=f"{granularity} Revenue Trend")
            st.plotly_chart(fig, use_container_width=True, key="chart_23")

    section("Revenue by Diagnosis")
    if {"Diagnosis", "Bill_Amount"}.issubset(f_visits.columns):
        diag_rev = (
            f_visits.groupby("Diagnosis")
            .agg(Visits=("Visit_ID", "count"), Revenue=("Bill_Amount", "sum"), Average_Bill=("Bill_Amount", "mean"))
            .sort_values("Revenue", ascending=False)
            .reset_index()
        )
        st.dataframe(diag_rev.head(15), use_container_width=True)
        top15 = diag_rev.head(15).sort_values("Revenue", ascending=True)
        fig = px.bar(top15, x="Revenue", y="Diagnosis", orientation="h", color="Revenue",
                     color_continuous_scale="Turbo", title="Top Diagnoses by Revenue")
        st.plotly_chart(fig, use_container_width=True, key="chart_24")

    section("Correlation Heatmap")
    numeric_cols = [c for c in ["Age", "Bill_Amount", "Length_of_Stay"] if c in f_patient_visits.columns]
    if len(numeric_cols) >= 2:
        corr = f_patient_visits[numeric_cols].corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                         title="Correlation: Age, Bill Amount, Length of Stay", zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True, key="chart_25")

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#9ca3af; font-size:13px; padding: 8px 0 20px 0;">
        Built with <b>Python</b> · <b>Pandas</b> · <b>Streamlit</b> · <b>Plotly</b><br>
        End-to-end pipeline: data cleaning → feature engineering → interactive visualization
    </div>
    """,
    unsafe_allow_html=True,
)