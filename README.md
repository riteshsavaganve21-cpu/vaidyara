# VAIDYARA — starter web app

A Flask + SQLite learning prototype for the VAIDYARA mini project.

## Run in VS Code
1. Install Python 3.11+ and VS Code.
2. Extract this ZIP to a folder and open that folder in VS Code.
3. Open Terminal → New Terminal.
4. Create and activate a virtual environment:

**Windows PowerShell**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

5. Install dependencies:
```bash
python -m pip install -r requirements.txt
```
6. Start the app:
```bash
python app.py
```
7. Open `http://127.0.0.1:5000` in your browser.

## Prototype limitations — important
- This is a local demo, not a production healthcare system.
- Medicine entries are illustrative interface-test records, **not a certified or complete database**.
- No pediatric dose formulas are applied. The formula text previously supplied needs verification and must not be used as a real-world dosing authority.
- Image upload works, but medicine image recognition/OCR is not implemented; the app explicitly refuses to guess.
- GPS map uses Leaflet/OpenStreetMap tiles. Nearby pharmacy search and verified pharmacy data are not implemented yet.
- Doctor and pharmacist accounts remain pending verification; a secure administrator verification workflow still needs to be built before professional use.
- Allergy and interaction checks are safety-review reminders only, not a clinical decision engine.
- Do not enter real patient-identifying or medical information into this demo.
- Before any real use, add verified India-appropriate medicine references, clinical validation, security/privacy review, audit controls, backups, and professional oversight.

## Features included
- Role-specific registration/login for patient, pharmacist, doctor.
- Separate pending-verification page for professional accounts.
- Sky-blue dashboard styling and responsive layout.
- Medicine search with clearly labelled sample records.
- Guidance form for age, weight, symptoms, allergies, conditions, current medicines.
- Automatic per-user history for searches, guidance submissions, and package uploads.
- Upload a medicine package photo (JPG/PNG/WEBP, max 5 MB) without pretending to identify it.
- Interactive map area for user location display; browser location permission is required.
- Password hashing and session login.

## Next development stages
1. Admin-backed professional verification.
2. Connect a curated, versioned medicine reference dataset and source citations.
3. Implement safe OCR for package text; require confirmation and never infer from a pill image alone.
4. Add verified duplicate-ingredient and interaction checks.
5. Build validated clinical rules only after qualified professional review.
6. Add nearby-pharmacy data provider, consent, privacy controls, deployment hardening.
