import json
from pathlib import Path

def appointments(clinic_id):
    data = json.loads(Path(__file__).with_name('clinics.json').read_text())
    return data[clinic_id]['appointments']

def patient_home_url(clinic_id):
    data = json.loads(Path(__file__).with_name('clinics.json').read_text())
    return data[clinic_id]['patient_home_url']
