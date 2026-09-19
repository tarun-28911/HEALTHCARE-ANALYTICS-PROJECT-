import pandas as pd
import os


def generate_sample_data():

    base_path = os.path.join(os.path.dirname(__file__), "data")

    patients = pd.read_csv(os.path.join(base_path, "patients.csv"))
    visits = pd.read_csv(os.path.join(base_path, "visits.csv"))
    admissions = pd.read_csv(os.path.join(base_path, "admissions.csv"))
    doctors = pd.read_csv(os.path.join(base_path, "doctors.csv"))
    lab_tests = pd.read_csv(os.path.join(base_path, "lab_tests.csv"))
    prescriptions = pd.read_csv(os.path.join(base_path, "prescriptions.csv"))
    staff = pd.read_csv(os.path.join(base_path, "staff.csv"))

    return (
        patients,
        visits,
        admissions,
        doctors,
        lab_tests,
        prescriptions,
        staff
    )