from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3, os, json, re
from datetime import datetime
from functools import wraps
import medicine_catalog as mc
import medicine_database as mdb
import nearby_service as ns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "vaidyara.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("VAIDYARA_SECRET_KEY", "change-this-demo-secret-before-deployment")
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

# Educational DEMO records only. These are not a certified clinical database.

# Disease → Medicine mapping (demo/educational only, not a clinical database)
DISEASE_MEDICINE_MAP = {
    "fever": {
        "medicines": ["Paracetamol", "Ibuprofen"],
        "description": "Fever is a temporary rise in body temperature, usually caused by an infection.",
        "tips": "Rest well, stay hydrated, and avoid heavy clothing. Seek medical attention if fever exceeds 103°F (39.4°C) or lasts more than 3 days.",
    },
    "headache": {
        "medicines": ["Paracetamol", "Ibuprofen"],
        "description": "Headache can result from tension, dehydration, stress, or other underlying causes.",
        "tips": "Rest in a quiet, dark room, stay hydrated, and avoid screen exposure. Consult a doctor if headaches are severe or frequent.",
    },
    "cold": {
        "medicines": ["Cetirizine", "Paracetamol"],
        "description": "Common cold is a viral infection of the upper respiratory tract.",
        "tips": "Drink warm fluids, rest, and use steam inhalation. Antibiotics do not help for viral colds.",
    },
    "flu": {
        "medicines": ["Paracetamol", "Ibuprofen", "Cetirizine"],
        "description": "Influenza (flu) is a contagious respiratory illness caused by influenza viruses.",
        "tips": "Rest, stay hydrated, and isolate to avoid spreading. Seek medical care if symptoms are severe or you are in a high-risk group.",
    },
    "allergy": {
        "medicines": ["Cetirizine"],
        "description": "Allergies occur when the immune system reacts to a foreign substance like pollen, pet dander, or food.",
        "tips": "Identify and avoid triggers where possible. Consult a doctor if symptoms are severe or affect breathing.",
    },
    "allergies": {
        "medicines": ["Cetirizine"],
        "description": "Allergies occur when the immune system reacts to a foreign substance like pollen, pet dander, or food.",
        "tips": "Identify and avoid triggers where possible. Consult a doctor if symptoms are severe or affect breathing.",
    },
    "pain": {
        "medicines": ["Paracetamol", "Ibuprofen"],
        "description": "General pain can range from mild to severe and may arise from many causes.",
        "tips": "Rest the affected area and apply ice or heat as appropriate. Consult a doctor if pain is severe, persistent, or unexplained.",
    },
    "body pain": {
        "medicines": ["Paracetamol", "Ibuprofen"],
        "description": "Body aches are commonly associated with flu, overexertion, or viral infections.",
        "tips": "Rest, stay hydrated, and apply warm compresses. See a doctor if body pain is severe or accompanied by high fever.",
    },
    "toothache": {
        "medicines": ["Ibuprofen", "Paracetamol"],
        "description": "Toothache is pain in or around a tooth, usually caused by decay, infection, or injury.",
        "tips": "Rinse with warm salt water and avoid very hot or cold foods. Visit a dentist as soon as possible — do not use medicines as a substitute for dental care.",
    },
    "throat infection": {
        "medicines": ["Amoxicillin", "Paracetamol"],
        "description": "Throat infection (pharyngitis/tonsillitis) is often caused by bacteria or viruses.",
        "tips": "Gargle with warm salt water, stay hydrated, and rest. Antibiotics are only appropriate if a doctor confirms a bacterial cause.",
    },
    "ear infection": {
        "medicines": ["Amoxicillin", "Ibuprofen"],
        "description": "Ear infections are common in children but can occur in adults, often following a cold.",
        "tips": "Apply a warm compress to ease pain. Always consult a doctor before using any antibiotic for an ear infection.",
    },
    "skin infection": {
        "medicines": ["Amoxicillin"],
        "description": "Skin infections can be bacterial, fungal, or viral and vary widely in severity.",
        "tips": "Keep the area clean and dry. Seek medical assessment — antibiotics are only appropriate when a qualified professional confirms a bacterial infection.",
    },
    "urinary tract infection": {
        "medicines": ["Amoxicillin"],
        "description": "UTIs are infections of the bladder, urethra, or kidneys, more common in women.",
        "tips": "Drink plenty of water and urinate frequently. Always see a doctor for proper diagnosis and prescription before taking antibiotics.",
    },
    "uti": {
        "medicines": ["Amoxicillin"],
        "description": "UTIs are infections of the bladder, urethra, or kidneys, more common in women.",
        "tips": "Drink plenty of water and urinate frequently. Always see a doctor for proper diagnosis and prescription before taking antibiotics.",
    },
    "inflammation": {
        "medicines": ["Ibuprofen"],
        "description": "Inflammation is the body's natural response to injury or infection.",
        "tips": "Rest the affected area, apply ice, and elevate if applicable. Seek medical care if inflammation is severe or does not improve.",
    },
    "muscle pain": {
        "medicines": ["Ibuprofen", "Paracetamol"],
        "description": "Muscle pain (myalgia) can be caused by overuse, tension, injury, or illness.",
        "tips": "Apply ice for the first 48 hours, then heat. Gentle stretching may help. See a doctor if pain is severe or does not resolve.",
    },
    "joint pain": {
        "medicines": ["Ibuprofen", "Paracetamol"],
        "description": "Joint pain can result from arthritis, injury, or inflammation.",
        "tips": "Rest the joint, use ice or heat, and avoid strenuous activity. Consult a doctor for persistent or severe joint pain.",
    },
    "runny nose": {
        "medicines": ["Cetirizine"],
        "description": "Runny nose is commonly caused by colds, allergies, or sinusitis.",
        "tips": "Stay hydrated, use steam inhalation, and blow gently. See a doctor if symptoms persist more than 10 days.",
    },
    "sneezing": {
        "medicines": ["Cetirizine"],
        "description": "Frequent sneezing is often triggered by allergens, dust, or cold viruses.",
        "tips": "Identify and avoid triggers. Keep your environment clean and dust-free.",
    },
    "itching": {
        "medicines": ["Cetirizine"],
        "description": "Itching (pruritus) can be caused by allergies, dry skin, insect bites, or skin conditions.",
        "tips": "Avoid scratching to prevent skin damage. Apply a soothing lotion and consult a doctor if itching is widespread or severe.",
    },
    "rash": {
        "medicines": ["Cetirizine"],
        "description": "Skin rashes can be caused by allergies, infections, or autoimmune conditions.",
        "tips": "Avoid scratching and irritants. Seek medical assessment, especially if the rash is spreading, painful, or accompanied by fever.",
    },
    "bacterial infection": {
        "medicines": ["Amoxicillin"],
        "description": "Bacterial infections are caused by harmful bacteria entering the body.",
        "tips": "Always consult a doctor for diagnosis and appropriate antibiotic prescription. Never self-medicate with antibiotics.",
    },
}

MEDICINES = [
    {"name":"Paracetamol", "ingredient":"Paracetamol (acetaminophen)", "category":"Pain/fever relief",
     "details":"First-line analgesic and antipyretic for mild-to-moderate pain and fever.",
     "warnings":"Excess intake can cause severe liver damage. Do not exceed 4000 mg/day for adults.",
     "source":"British National Formulary (BNF), WHO Model List of Essential Medicines."},
    {"name":"Cetirizine", "ingredient":"Cetirizine hydrochloride", "category":"Antihistamine",
     "details":"Second-generation H1-receptor antagonist for allergic rhinitis, urticaria, and itchy skin.",
     "warnings":"May cause mild drowsiness. Avoid alcohol. Adjust dose in kidney impairment.",
     "source":"British National Formulary (BNF), EAACI Allergy Guidelines."},
    {"name":"Amoxicillin", "ingredient":"Amoxicillin trihydrate", "category":"Antibiotic (Penicillin class)",
     "details":"Broad-spectrum antibiotic for confirmed bacterial ear, throat, urinary, and chest infections.",
     "warnings":"STRICTLY CONTRAINDICATED in penicillin allergy. Complete full prescribed course.",
     "source":"WHO AWaRe Antibiotics, NICE Guidelines."},
    {"name":"Ibuprofen", "ingredient":"Ibuprofen", "category":"NSAID pain reliever",
     "details":"Anti-inflammatory pain reliever for headache, dental pain, and musculoskeletal aches.",
     "warnings":"Take with food. Contraindicated in peptic ulcers, severe kidney disease, and 3rd trimester pregnancy. Caution in asthma.",
     "source":"British National Formulary (BNF), FDA Drug Label."},
    {"name":"Dextromethorphan", "ingredient":"Dextromethorphan hydrobromide", "category":"Cough Suppressant (Antitussive)",
     "details":"Centrally acting cough suppressant for temporary relief of non-productive dry coughs.",
     "warnings":"Do not use for productive chesty cough. Do not combine with MAOIs or SSRIs (serotonin syndrome risk). Not for children under 6.",
     "source":"British National Formulary (BNF), FDA OTC Monograph."},
    {"name":"Guaifenesin", "ingredient":"Guaifenesin", "category":"Expectorant",
     "details":"Mucolytic expectorant to thin and loosen thick bronchial secretions in productive chesty coughs.",
     "warnings":"Drink plenty of water to enhance efficacy. Consult doctor if cough lasts > 7 days.",
     "source":"British National Formulary (BNF), NHS Chesty Cough Guidance."},
    {"name":"Oral Rehydration Salts (ORS)", "ingredient":"Sodium chloride, glucose, potassium chloride, trisodium citrate", "category":"Electrolyte / Fluid Replacement",
     "details":"Essential oral fluid and electrolyte solution to prevent and treat dehydration from diarrhoea and vomiting.",
     "warnings":"Reconstitute in exact amount of clean drinking water indicated on packet. Discard after 24 hours.",
     "source":"WHO / UNICEF Guidelines on Clinical Management of Diarrhoea."},
    {"name":"Antacid", "ingredient":"Magnesium hydroxide, aluminum hydroxide, simethicone", "category":"Antacid / Antiflatulent",
     "details":"Fast-acting gastric acid neutralizer and antiflatulent for heartburn, indigestion, and acid reflux.",
     "warnings":"Separate from other oral medications by at least 2 hours to avoid binding interactions.",
     "source":"British National Formulary (BNF), FDA Antacid Monograph."},
    {"name":"Omeprazole", "ingredient":"Omeprazole", "category":"Proton Pump Inhibitor (PPI)",
     "details":"Gastric acid inhibitor for gastritis, GERD, and peptic ulcer disease.",
     "warnings":"Swallow whole 30–60 min before breakfast. Do not chew. Inform doctor if symptoms persist past 2 weeks.",
     "source":"NICE Dyspepsia Guideline CG184, BNF."},
    {"name":"Loperamide", "ingredient":"Loperamide hydrochloride", "category":"Antidiarrhoeal",
     "details":"Anti-motility agent for acute non-infectious diarrhoea in adults.",
     "warnings":"Do not use if blood is present in stools or fever is high. Not recommended for children under 12.",
     "source":"British National Formulary (BNF), WHO Diarrhoea Guidelines."},
    {"name":"Calamine Lotion", "ingredient":"Calamine (zinc oxide and ferric oxide)", "category":"Topical Antipruritic",
     "details":"Soothing topical lotion for itching, hives, insect bites, and contact dermatitis.",
     "warnings":"For external use only. Do not apply to open wounds or weeping skin lesions.",
     "source":"British National Formulary (BNF), NHS Skin Care."},
    {"name":"Saline Nasal Spray", "ingredient":"Isotonic sodium chloride 0.9%", "category":"Nasal Cleanser / Moisturizer",
     "details":"Non-medicated isotonic nasal irrigation to flush allergens and relieve nasal dryness and congestion.",
     "warnings":"Keep applicator tip clean. Do not share container between individuals.",
     "source":"EAACI Rhinitis Guidelines, BNF."}
]

# ─── MEDICINE DETAIL (clinical pharmacology database) ─────────────────────────
MEDICINES_DETAIL = {
    "Paracetamol": {
        "drug_class": "Analgesic / Antipyretic",
        "purpose": "Relieves mild to moderate pain and reduces fever.",
        "how_it_works": "Acts on the heat-regulating centre in the hypothalamus to lower body temperature and centrally inhibits prostaglandin synthesis.",
        "common_doses": "Adults: 500–1000 mg every 4–6 hours as needed (maximum 4000 mg in 24 hours). Children: strictly weight-based (10–15 mg/kg per dose).",
        "side_effects": ["Nausea (rare at standard dose)", "Allergic skin rash (rare)", "Severe hepatotoxicity / liver injury in overdose"],
        "precautions": ["Never exceed maximum recommended daily dose", "Avoid alcohol while taking paracetamol", "Carefully check all other cold/flu products for hidden paracetamol content"],
        "contraindications": ["Severe active hepatic impairment or liver disease", "Known hypersensitivity to paracetamol / acetaminophen"],
        "interactions": ["Warfarin — prolonged regular high-dose use may elevate INR and bleeding risk", "Alcohol — substantially increases risk of hepatotoxicity"],
        "allergens": ["paracetamol", "acetaminophen"],
        "age_notes": {"child": "Standard paediatric antipyretic; must use weight-based liquid formulation", "elderly": "Generally safe; consider lower daily maximum (2000–3000 mg/day) if frail or renal/hepatic impairment"},
        "references": ["British National Formulary (BNF)", "WHO Model List of Essential Medicines", "FDA Prescribing Information"]
    },
    "Ibuprofen": {
        "drug_class": "NSAID (Non-Steroidal Anti-Inflammatory Drug)",
        "purpose": "Relieves pain, reduces systemic inflammation, and lowers fever.",
        "how_it_works": "Inhibits cyclooxygenase enzymes (COX-1 and COX-2), reducing synthesis of pro-inflammatory prostaglandins.",
        "common_doses": "Adults: 200–400 mg every 4–6 hours with or after food (maximum OTC dose 1200 mg/day). Always take with food or milk.",
        "side_effects": ["Epigastric pain and dyspepsia", "Nausea or heartburn", "Gastric ulceration or gastrointestinal bleeding", "Fluid retention", "Elevated blood pressure"],
        "precautions": ["Always administer with food or milk to reduce gastric irritation", "Avoid prolonged use without medical supervision", "Use with extreme caution in asthmatic patients (bronchospasm risk)"],
        "contraindications": ["Active or history of peptic ulcer disease or GI bleeding", "Known hypersensitivity to aspirin or other NSAIDs", "Severe heart failure or severe renal failure", "Third trimester of pregnancy"],
        "interactions": ["Warfarin / Anticoagulants — dramatically increased gastrointestinal bleeding risk", "Aspirin — increased GI toxicity and reduced cardioprotection", "ACE Inhibitors / Diuretics — diminished antihypertensive effect and risk of acute kidney injury", "SSRIs — additive risk of upper GI bleeding"],
        "allergens": ["ibuprofen", "nsaid", "aspirin"],
        "age_notes": {"child": "Use weight-based paediatric suspension; not approved under 3 months or < 5 kg", "elderly": "High vulnerability to GI ulceration, renal failure, and heart failure exacerbation; use lowest dose with PPI if unavoidable"},
        "references": ["British National Formulary (BNF)", "FDA Drug Safety Communication", "NICE Musculoskeletal Pain Guidelines"]
    },
    "Cetirizine": {
        "drug_class": "Second-generation H1 Antihistamine",
        "purpose": "Relieves allergy symptoms including sneezing, runny nose, watery/itchy eyes, hives, and pruritus.",
        "how_it_works": "Selectively antagonizes peripheral histamine H1 receptors, blocking the allergic cascade with minimal CNS penetration.",
        "common_doses": "Adults and adolescents over 12: 10 mg once daily. Children 6–12 years: 5 mg twice daily or 10 mg once daily. Children 2–6 years: 2.5 mg twice daily.",
        "side_effects": ["Mild drowsiness (in sensitive individuals)", "Dry mouth", "Headache", "Fatigue", "Mild gastrointestinal upset"],
        "precautions": ["May impair alertness — exercise caution when driving or operating machinery until individual tolerance is known", "Reduce dosage in moderate-to-severe renal impairment", "Avoid concurrent alcohol"],
        "contraindications": ["Known hypersensitivity to cetirizine, hydroxyzine, or piperazine derivatives", "End-stage renal disease (CrCl < 10 mL/min) unless adjusted"],
        "interactions": ["Alcohol — additive central nervous system depression", "Sedatives / hypnotics / opioids — enhanced sedation"],
        "allergens": ["cetirizine", "hydroxyzine"],
        "age_notes": {"child": "Approved for children aged 2 years and older with appropriate paediatric dosing", "elderly": "Sedation and urinary retention risk; dose reduction recommended in elderly patients with reduced renal clearance"},
        "references": ["British National Formulary (BNF)", "EAACI Allergic Rhinitis Guidelines", "FDA Drug Label"]
    },
    "Amoxicillin": {
        "drug_class": "Penicillin-class Antibiotic (Beta-lactam)",
        "purpose": "Treats susceptible bacterial infections (strep throat, bacterial otitis media, lower respiratory infections, UTIs).",
        "how_it_works": "Inhibits bacterial cell wall peptidoglycan synthesis by binding to penicillin-binding proteins, causing bacterial lysis.",
        "common_doses": "Adults: 250–500 mg every 8 hours or 500–875 mg every 12 hours for 5–10 days. Always complete the entire prescribed course.",
        "side_effects": ["Diarrhoea and soft stools", "Nausea and vomiting", "Erythematous maculopapular rash", "Oral or vaginal candidiasis (thrush)", "Severe anaphylaxis (in allergic individuals)"],
        "precautions": ["Mandatory to complete full course to prevent bacterial resistance", "Requires genuine physician prescription — ineffective against viral colds/flu", "Discontinue immediately if allergic rash or wheezing develops"],
        "contraindications": ["STRICTLY CONTRAINDICATED in known allergy to penicillin, amoxicillin, or any beta-lactam antibiotic", "History of amoxicillin-associated jaundice or hepatic dysfunction"],
        "interactions": ["Warfarin — may enhance anticoagulant effect and increase INR", "Methotrexate — reduces methotrexate excretion, increasing toxicity risk", "Allopurinol — increased incidence of skin rash"],
        "allergens": ["penicillin", "amoxicillin", "beta-lactam", "ampicillin"],
        "age_notes": {"child": "Standard first-line paediatric antibiotic for bacterial ear/throat infections; prescribed strictly by weight (mg/kg)", "elderly": "Renal function monitoring recommended; dosage interval may need extension if GFR is decreased"},
        "references": ["WHO AWaRe Antibiotic Book", "British National Formulary (BNF)", "NICE Antimicrobial Prescribing Guidelines"]
    },
    "Dextromethorphan": {
        "drug_class": "Antitussive (Cough Suppressant)",
        "purpose": "Temporary symptomatic relief of dry, hacking, non-productive cough caused by minor throat and bronchial irritation.",
        "how_it_works": "Acts centrally on the cough center in the medulla oblongata to increase the cough threshold without impairing ciliary activity.",
        "common_doses": "Adults and children 12+: 10–20 mg every 4 hours or 30 mg every 6–8 hours as needed (max 120 mg/day).",
        "side_effects": ["Mild drowsiness or dizziness", "Nausea or stomach upset", "Constipation", "Excitation or confusion (in high doses)"],
        "precautions": ["Do not use for productive chesty cough with excessive phlegm (can lead to mucus retention)", "Do not use in persistent chronic cough related to asthma or smoking", "Check labels for combination ingredients"],
        "contraindications": ["Concurrent use with or within 14 days of MAOI antidepressants (severe fatal Serotonin Syndrome risk)", "Severe respiratory depression or asthma exacerbation", "Children under 6 years of age"],
        "interactions": ["MAOIs and SSRIs (fluoxetine, paroxetine) — critical risk of Serotonin Syndrome", "CNS depressants and alcohol — marked additive sedation"],
        "allergens": ["dextromethorphan"],
        "age_notes": {"child": "NOT recommended in children under 6 years (FDA/AAP alert). Use with caution in 6–12 under medical direction", "elderly": "Increased vulnerability to dizziness, fall risk, and confusion"},
        "references": ["British National Formulary (BNF)", "FDA Nonprescription Drug Advisory", "NHS Cough Guidance"]
    },
    "Guaifenesin": {
        "drug_class": "Expectorant",
        "purpose": "Helps thin and loosen mucus/phlegm in the respiratory tract, making chesty coughs more productive and easier to clear.",
        "how_it_works": "Increases bronchial secretion volume and reduces mucus viscosity, facilitating ciliary removal of accumulated secretions.",
        "common_doses": "Adults and adolescents 12+: 200–400 mg every 4 hours with a full glass of water (maximum 2400 mg/day).",
        "side_effects": ["Mild gastrointestinal discomfort or nausea", "Headache", "Dizziness", "Skin rash (rare)"],
        "precautions": ["Drink plenty of water throughout the day to support mucus thinning", "Consult doctor if cough persists beyond 7 days or is accompanied by high fever, rash, or persistent headache"],
        "contraindications": ["Known hypersensitivity to guaifenesin"],
        "interactions": ["No clinically significant drug-drug interactions documented"],
        "allergens": ["guaifenesin"],
        "age_notes": {"child": "Use paediatric formulations only for children over 6 years under guidance", "elderly": "Generally well tolerated; ensure adequate hydration"},
        "references": ["British National Formulary (BNF)", "FDA Expectorant Monograph", "NICE Acute Cough Guidelines"]
    },
    "Oral Rehydration Salts (ORS)": {
        "drug_class": "Electrolyte and Fluid Replacement",
        "purpose": "Prevents and treats dehydration and electrolyte loss caused by acute diarrhoea, gastroenteritis, or vomiting.",
        "how_it_works": "Exploits coupled sodium-glucose cotransport across the intestinal brush border membrane to drive passive water reabsorption.",
        "common_doses": "Reconstitute packet in exact volume of clean drinking water indicated on packaging (typically 200 mL or 1 Litre). Sip small amounts frequently after each loose stool.",
        "side_effects": ["Nausea or vomiting if swallowed too quickly in large gulps", "Hypernatraemia if prepared with inadequate water volume"],
        "precautions": ["Must be mixed with pure water only — never boil after mixing and never mix with milk, soup, or fruit juice", "Discard any unused mixed solution after 24 hours"],
        "contraindications": ["Severe intractable vomiting requiring intravenous fluid resuscitation", "Intestinal obstruction, ileus, or bowel perforation", "Severe acute kidney injury with anuria"],
        "interactions": ["No pharmacological drug interactions; compatible with all oral therapies"],
        "allergens": ["glucose", "dextrose", "electrolytes"],
        "age_notes": {"child": "First-line life-saving therapy in paediatric diarrhoea; administer frequent small spoonfuls", "elderly": "Essential in elderly patients to prevent rapid dehydration, electrolyte imbalance, and pre-renal acute kidney injury"},
        "references": ["WHO/UNICEF Clinical Management of Acute Diarrhoea", "British National Formulary (BNF)", "NICE Clinical Guideline CG84"]
    },
    "Antacid": {
        "drug_class": "Antacid & Antiflatulent",
        "purpose": "Provides rapid symptomatic relief from heartburn, acid indigestion, sour stomach, and gas/bloating.",
        "how_it_works": "Chemically neutralizes hydrochloric acid in gastric secretions and reduces surface tension of gas bubbles.",
        "common_doses": "10–20 mL liquid suspension or 1–2 chewable tablets chewed thoroughly 1 hour after meals and at bedtime as needed.",
        "side_effects": ["Diarrhoea (magnesium salts)", "Constipation (aluminum salts)", "Belching or flatulence", "Alkalinization of urine"],
        "precautions": ["Separate administration from other oral medications by at least 2 hours to prevent drug binding and absorption failure", "Avoid long-term high-dose use in renal impairment"],
        "contraindications": ["Severe renal failure (risk of aluminum/magnesium systemic toxicity)", "Severe hypophosphataemia"],
        "interactions": ["Fluoroquinolones, Tetracyclines, Iron salts, Levothyroxine — chelation drastically reduces their absorption; space by at least 2 hours"],
        "allergens": ["antacid", "magnesium", "aluminum"],
        "age_notes": {"child": "Not recommended for young children unless specifically prescribed by a paediatrician", "elderly": "Safe for episodic heartburn; maintain 2-hour spacing from cardiac and blood pressure medications"},
        "references": ["British National Formulary (BNF)", "FDA Antacid Monograph", "NICE Dyspepsia Guidelines"]
    },
    "Omeprazole": {
        "drug_class": "Proton Pump Inhibitor (PPI)",
        "purpose": "Suppresses gastric acid secretion for treatment and healing of gastritis, GERD (acid reflux), and peptic ulcers.",
        "how_it_works": "Irreversibly inhibits the H+/K+ ATPase enzyme system in gastric parietal cells, blocking basal and stimulated acid production.",
        "common_doses": "Adults: 20 mg once daily taken in the morning 30–60 minutes before breakfast with a glass of water. Swallow whole; do not crush or chew.",
        "side_effects": ["Headache", "Abdominal discomfort or mild nausea", "Diarrhoea or constipation", "Flatulence", "Long-term use: hypomagnesaemia, vitamin B12 deficiency"],
        "precautions": ["Swallow capsule or tablet whole — enteric coating must not be compromised", "If heartburn persists longer than 2 weeks of OTC use, seek comprehensive clinical evaluation", "May mask symptoms of gastric malignancy"],
        "contraindications": ["Known hypersensitivity to omeprazole or any proton pump inhibitor (pantoprazole, esomeprazole, rabeprazole)"],
        "interactions": ["Clopidogrel — omeprazole competitively inhibits CYP2C19, potentially reducing clopidogrel antiplatelet activation", "Methotrexate — PPIs can increase methotrexate serum concentrations", "Ketoconazole / Itraconazole — reduced antifungal absorption due to elevated gastric pH"],
        "allergens": ["omeprazole", "ppi", "proton pump inhibitor"],
        "age_notes": {"child": "Use only under direct paediatric medical supervision", "elderly": "Use lowest effective dose; prolonged use may increase osteoporosis/fracture risk and C. difficile infection risk"},
        "references": ["British National Formulary (BNF)", "NICE Gastro-oesophageal Reflux Guideline CG184", "FDA Drug Label"]
    },
    "Loperamide": {
        "drug_class": "Antidiarrhoeal (Peripheral Opioid-receptor Agonist)",
        "purpose": "Symptomatic control of acute, non-infectious, non-bloody diarrhoea in adults and adolescents over 12.",
        "how_it_works": "Binds to mu-opioid receptors in the circular muscle layers of the intestinal wall, slowing peristalsis and enhancing fluid reabsorption.",
        "common_doses": "Adults: 4 mg initially followed by 2 mg after each unformed stool (maximum 16 mg/day). Discontinue as soon as stools become formed or after 48 hours.",
        "side_effects": ["Constipation", "Abdominal cramping and bloating", "Dizziness", "Drowsiness", "Dry mouth"],
        "precautions": ["DO NOT use if fever is present (> 38.5°C) or if blood/mucus is visible in stools (dysentery/invasive infection)", "Discontinue immediately if constipation, abdominal distension, or ileus develops", "Always maintain aggressive oral hydration"],
        "contraindications": ["Invasive bacterial enterocolitis (Salmonella, Shigella, Campylobacter, C. difficile)", "Acute active ulcerative colitis", "Children under 12 years of age"],
        "interactions": ["P-glycoprotein inhibitors (quinidine, ritonavir, ketoconazole) — can elevate loperamide plasma levels", "QT-prolonging agents — risk of serious ventricular arrhythmias in excessive supra-therapeutic doses"],
        "allergens": ["loperamide"],
        "age_notes": {"child": "STRICTLY CONTRAINDICATED in children under 12 years due to risk of toxic megacolon and paralytic ileus", "elderly": "Monitor closely for constipation and ensure hydration with ORS"},
        "references": ["British National Formulary (BNF)", "WHO Guidelines on Diarrhoeal Disease", "FDA Safety Communication on Loperamide"]
    },
    "Calamine Lotion": {
        "drug_class": "Topical Antipruritic & Soothing Agent",
        "purpose": "Provides topical soothing, astringent relief from itching, hives, insect bites, sunburn, and mild allergic rashes.",
        "how_it_works": "Formulation of zinc oxide and iron(III) oxide evaporates on the skin surface, producing a cooling antipruritic effect and mild protective barrier.",
        "common_doses": "Shake bottle well. Apply generously to the affected itchy skin with clean cotton wool 3–4 times daily as required.",
        "side_effects": ["Mild localized skin dryness", "Rare localized contact irritation"],
        "precautions": ["Strictly for external cutaneous use only", "Do not apply on open broken skin, raw weeping wounds, or blistering burns", "Avoid contact with eyes, nose, and mouth"],
        "contraindications": ["Known hypersensitivity to zinc oxide or calamine"],
        "interactions": ["No systemic drug interactions when applied topically"],
        "allergens": ["calamine", "zinc oxide"],
        "age_notes": {"child": "Safe for infants, children, and adolescents of all ages", "elderly": "Safe and effective for pruritus without systemic drug interaction risks"},
        "references": ["British National Formulary (BNF)", "NHS Skin Health Guidance", "WHO Model Formulary"]
    },
    "Saline Nasal Spray": {
        "drug_class": "Nasal Cleanser & Decongestant (Non-Medicated)",
        "purpose": "Cleanses nasal passages, thins thick mucus, and flushes out airborne pollen, dust, and allergen particles.",
        "how_it_works": "Isotonic 0.9% sodium chloride solution mechanically irrigates the nasal mucosal epithelium, improving mucociliary clearance.",
        "common_doses": "1–2 sprays into each nostril 2–4 times daily or as needed before applying medicated nasal sprays.",
        "side_effects": ["Transient mild nasal stinging or reflex sneezing upon initial use"],
        "precautions": ["Wipe nozzle clean after each use and keep protective cap on", "Do not share bottle between family members to prevent viral cross-contamination"],
        "contraindications": ["None — safe physiological saline solution"],
        "interactions": ["None — completely non-medicated; safe with all prescription medications"],
        "allergens": ["sodium chloride", "saline"],
        "age_notes": {"child": "Completely safe for infants, toddlers, and children; excellent natural aid for nasal congestion", "elderly": "Safe with zero cardiovascular or hypertension interaction risks"},
        "references": ["British National Formulary (BNF)", "EAACI Pediatric Allergic Rhinitis Guidelines", "NICE Clinical Knowledge Summaries"]
    }
}

# ─── COMPREHENSIVE CONDITION DATABASE ─────────────────────────────────────────
CONDITION_DATABASE = {
    "fever": {
        "name": "Fever (Pyrexia)", "emoji": "🌡️",
        "explanation": "A temporary elevation in core body temperature above 38°C (100.4°F), representing an active systemic immune defense mechanism against infection.",
        "causes": ["Viral upper or lower respiratory infections", "Bacterial infections", "Vaccine immune responses", "Heat exhaustion", "Inflammatory conditions"],
        "symptoms": ["Elevated body temperature (> 38°C)", "Chills, rigor, and shivering", "Profuse sweating", "Generalized headache and muscle aches", "Loss of appetite", "Lethargy and dehydration"],
        "risk_factors": ["Infants and children under 5", "Older adults (> 65)", "Immunocompromised states", "Recent post-operative recovery"],
        "complications": ["Febrile seizures in young children", "Severe systemic dehydration", "Delirium or hallucinations in hyperpyrexia", "Sepsis if underlying bacterial cause is untreated"],
        "tests": ["Core temperature measurement with calibrated clinical thermometer", "Complete blood count (CBC)", "Urine dipstick / culture if urinary symptoms present", "Blood cultures if high bacteremic suspicion"],
        "prevention": ["Rigorous hand hygiene with soap and water", "Staying up to date on seasonal immunizations", "Avoiding close contact with actively infected individuals", "Proper food and water safety"],
        "home_care": ["Prioritize absolute bed rest to minimize metabolic demands", "Drink abundant fluids — water, oral rehydration solution, diluted clear broths", "Apply lukewarm damp compress to forehead and neck (avoid cold water or alcohol rubs)", "Wear light, breathable cotton clothing and avoid bundling in heavy blankets", "Keep bedroom well ventilated at a comfortable temperature (20–22°C)"],
        "medicines": ["Paracetamol", "Ibuprofen"],
        "medicine_reasons": {
            "Paracetamol": "First-line analgesic and antipyretic that acts on the hypothalamic thermoregulatory center to safely lower fever with minimal gastric irritation.",
            "Ibuprofen": "Anti-inflammatory NSAID providing dual fever reduction and relief of severe muscle and joint aching (must be taken with food)."
        },
        "when_to_see_doctor": ["Fever exceeding 39.4°C (103°F) or not responding to antipyretics", "Fever persisting longer than 3 continuous days", "Fever in an infant under 3 months of age (urgent evaluation)", "Fever accompanied by stiff neck, confusion, photophobia, or non-blanching petechial rash"],
        "emergency_signs": ["Body temperature reaching 40°C (104°F) or higher", "Convulsions or febrile seizure", "Inability to maintain consciousness, extreme lethargy, or confusion", "Laboured or rapid breathing with chest in-drawing", "Inability to keep any oral fluids down with signs of severe dehydration"],
        "allergy_note": None,
        "references": ["WHO Guidelines on the Management of Fever", "NICE Clinical Guideline CG160: Fever in Under 5s", "British National Formulary (BNF)"]
    },
    "headache": {
        "name": "Headache / Migraine", "emoji": "🤕",
        "explanation": "Pain located in the cranium, forehead, or cervical region, most commonly tension-type headache or migraine involving neurovascular activation.",
        "causes": ["Cervical and scalp muscle tension from stress or poor posture", "Dehydration and missed meals", "Sleep deprivation or irregular sleep cycles", "Prolonged screen eye strain", "Caffeine withdrawal or vasodilation triggers", "Neurovascular trigeminal nerve sensitization (migraine)"],
        "symptoms": ["Bilateral tight, band-like pressing pain around forehead and temples (tension headache)", "Unilateral throbbing or pulsating moderate-to-severe headache (migraine)", "Photophobia (light sensitivity) and phonophobia (sound sensitivity)", "Nausea, vomiting, or stomach awareness", "Visual aura (flickering zigzag lights or blind spots before migraine onset)"],
        "risk_factors": ["Chronic emotional or physical stress", "Sedentary computer work", "Female sex and hormonal fluctuations", "Family history of migraine", "Irregular sleep and dehydration"],
        "complications": ["Chronic daily headache", "Medication-overuse (rebound) headache from analgesic overuse > 15 days/month", "Substantial impairment in occupational and social functioning"],
        "tests": ["Detailed clinical neurological examination", "Blood pressure measurement", "Fundoscopic examination of optic discs", "Brain MRI or CT neuroimaging if red flags or atypical features exist"],
        "prevention": ["Maintain consistent daily hydration (at least 2 litres of water daily)", "Keep regular sleep-wake schedules even on weekends", "Take frequent ergonomic screen breaks (20-20-20 rule)", "Identify and avoid personal dietary migraine triggers (aged cheese, MSG, artificial sweeteners, nitrates)", "Engage in regular aerobic exercise and stress management"],
        "home_care": ["Rest in a quiet, dark, well-ventilated room", "Apply a cool gel pack or cold compress across the forehead or a warm pad to the back of the neck", "Sip cool water slowly to rehydrate", "Perform gentle neck, shoulder, and temple stretches or self-massage", "Practice slow, rhythmic diaphragmatic breathing to release muscular tension"],
        "medicines": ["Paracetamol", "Ibuprofen"],
        "medicine_reasons": {
            "Paracetamol": "First-line, gastric-safe analgesic for tension headache and mild migraine attacks.",
            "Ibuprofen": "NSAID with superior efficacy for vascular and inflammatory components of throbbing tension headaches and migraines."
        },
        "when_to_see_doctor": ["Sudden severe headache reaching peak intensity within seconds ('thunderclap' headache)", "Headache accompanied by fever, stiff neck, confusion, or rash", "New onset headache in individuals over 50 years of age", "Headache triggered by coughing, bending, or physical exertion", "Headache progressively worsening over days or weeks"],
        "emergency_signs": ["Sudden explosive severe headache unlike any previous episode", "Headache with focal neurological deficits (facial droop, arm weakness, slurred speech)", "Loss of consciousness, syncope, or seizure", "Headache following recent head trauma", "Headache with high fever, neck stiffness, and confusion"],
        "allergy_note": "Certain headaches can be precipitated by allergic rhinitis congestion or food sensitivity (histamines, sulfites, nitrates).",
        "references": ["NICE Clinical Guideline CG150: Headaches in Over 12s", "International Headache Society (IHS) ICHD-3 Classification", "British National Formulary (BNF)"]
    },
    "skin_allergy": {
        "name": "Skin Allergy (Urticaria / Hives / Allergic Dermatitis)", "emoji": "🔴",
        "explanation": "An immune-mediated cutaneous reaction triggered by mast-cell histamine degranulation, producing pruritic erythematous wheals (hives/urticaria) or contact dermatitis.",
        "causes": ["Ingested food allergens (peanuts, tree nuts, shellfish, milk, eggs, wheat)", "Adverse drug reactions (penicillin, NSAIDs, sulfa drugs)", "Contact allergens (nickel, latex, fragrances, cosmetics, harsh detergents)", "Insect bites or stings", "Airborne environmental allergens (pollen, animal dander, dust mites)"],
        "symptoms": ["Intensely itchy, raised, erythematous wheals or plaques (urticaria/hives)", "Transient skin swelling that shifts locations over hours", "Red, dry, scaling, or papular skin rash", "Localized burning, stinging, or heat sensation in the skin", "Facial, lip, or eyelid swelling (angioedema)"],
        "risk_factors": ["Personal or family history of atopic disease (eczema, asthma, allergic rhinitis)", "Known food or drug sensitivities", "Frequent handling of chemical irritants or latex", "Recent viral illness predisposing to acute urticaria"],
        "complications": ["Progression to systemic anaphylaxis (life-threatening airway or vascular collapse)", "Secondary bacterial impetiginization / cellulitis from intense skin scratching", "Chronic spontaneous urticaria persisting > 6 weeks"],
        "tests": ["Allergy skin prick testing (SPT) performed by an allergist", "Serum allergen-specific IgE blood testing (ImmunoCAP / RAST)", "Patch testing for suspected allergic contact dermatitis", "Clinical challenge testing in a specialized hospital allergy clinic"],
        "prevention": ["Strictly identify and avoid known allergic triggers and cross-reactive substances", "Carefully read all packaged food and cosmetic ingredient labels", "Wear protective nitrile gloves when handling detergents, solvents, or chemicals", "Use hypoallergenic, fragrance-free laundry detergents and cleansers", "Carry an emergency adrenaline auto-injector (EpiPen) if previously prescribed for anaphylaxis"],
        "home_care": ["Apply a cool, clean, damp cloth or ice pack wrapped in a towel to itchy areas for 10–15 minutes", "Apply soothing Calamine lotion topically to relieve itching without scratching", "Take lukewarm baths or showers — avoid hot water which triggers further histamine release", "Wear loose-fitting, smooth, lightweight cotton clothing to prevent friction", "Keep fingernails cut short and clean to prevent excoriation and secondary infection", "Avoid perfumed soaps, synthetic fabrics, and abrasive sponges"],
        "medicines": ["Cetirizine", "Calamine Lotion"],
        "medicine_reasons": {
            "Cetirizine": "Second-generation H1 antihistamine that directly blocks peripheral histamine receptors to halt itching, wheals, and erythema with minimal sedation.",
            "Calamine Lotion": "Topical antipruritic formulation of zinc oxide providing rapid surface cooling and soothing relief to irritated, inflamed skin."
        },
        "when_to_see_doctor": ["Rash spreading rapidly over extensive body surface areas", "Hives accompanied by facial, lip, tongue, or eyelid swelling (angioedema)", "Rash persisting for more than 48 hours without improvement", "Signs of secondary bacterial skin infection (increasing warmth, pus, tender red streaks)", "Rash accompanied by fever, joint pain, or constitutional illness"],
        "emergency_signs": ["Difficulty breathing, audible wheezing, or stridor", "Swelling of the throat, tongue, or lips with voice changes or difficulty swallowing", "Dizziness, lightheadedness, confusion, or fainting (anaphylactic shock)", "Sudden widespread hives accompanied by abdominal cramps and vomiting"],
        "allergy_note": "A confirmed diagnosis requires formal testing by a certified allergist. Do not assume or self-diagnose an allergy without clinical verification.",
        "references": ["EAACI / GA2LEN / EDF Guidelines for the Definition, Diagnosis, and Treatment of Urticaria", "British Association of Dermatologists (BAD) Urticaria Guidelines", "NICE Clinical Guideline CG134: Anaphylaxis"]
    },
    "cough_bronchitis": {
        "name": "Cough / Acute Bronchitis / Respiratory Infection", "emoji": "🫁",
        "explanation": "A protective respiratory reflex and inflammatory response of the tracheobronchial tree, commonly triggered by viral respiratory tract infections, post-nasal drip, or bronchial irritation.",
        "causes": ["Viral respiratory pathogens (rhinovirus, coronavirus, influenza, RSV)", "Acute bronchitis following an upper respiratory cold", "Post-nasal drip from allergic rhinitis or sinusitis", "Exposure to environmental air pollutants, cigarette smoke, or chemical fumes", "Gastroesophageal reflux (acid irritating laryngeal receptors)"],
        "symptoms": ["Dry, tickly, hacking non-productive cough", "Chesty productive cough with clear, white, or yellowish bronchial mucus", "Throat irritation, soreness, or tickling sensation", "Sternal chest discomfort or soreness from repeated coughing effort", "Mild low-grade fever and general malaise", "Post-tussive fatigue and sleep disruption"],
        "risk_factors": ["Active or passive tobacco smoke exposure", "Recent viral cold or influenza episode", "Underlying asthma, COPD, or chronic airway hyperreactivity", "Workplace dust, chemical, or grain exposure", "Autumn and winter seasonal peak"],
        "complications": ["Secondary bacterial pneumonia or bronchopneumonia", "Intercostal muscle strain or rib fracture from violent paroxysmal coughing", "Exacerbation of underlying bronchial asthma", "Sleep deprivation and chronic exhaustion"],
        "tests": ["Clinical chest examination and auscultation with a stethoscope", "Pulse oximetry to verify normal arterial oxygen saturation (> 95%)", "Chest X-ray if pneumonia, focal chest signs, or persistent cough > 3 weeks", "Sputum microbiology culture if bacterial lower respiratory infection is suspected"],
        "prevention": ["Avoid all forms of active and passive tobacco smoke exposure", "Practice regular handwashing before touching nose or mouth", "Stay current with annual influenza and pneumococcal immunizations", "Wear protective particulate masks in dusty, smoky, or polluted environments", "Maintain indoor air humidity using a clean humidifier in dry seasons"],
        "home_care": ["Maintain high fluid intake with warm water, clear broths, and decaffeinated herbal teas to thin respiratory secretions", "Consume warm water with 1–2 teaspoons of honey and fresh lemon juice (soothing demulcent for adults and children over 1 year)", "Inhale warm steam from a bowl of hot water or take a warm steamy shower to loosen chest congestion", "Elevate the head of your bed with an extra pillow to prevent nocturnal post-nasal pooling and coughing fits", "Rest your voice and avoid throat clearing, which exacerbates mucosal irritation", "Keep indoor air clean, warm, and smoke-free"],
        "medicines": ["Dextromethorphan", "Guaifenesin", "Paracetamol"],
        "medicine_reasons": {
            "Dextromethorphan": "Centrally acting antitussive indicated specifically for dry, irritating, non-productive coughs that interrupt rest and sleep.",
            "Guaifenesin": "Expectorant indicated for productive chesty coughs to thin and liquefy tenacious bronchial mucus for easier expectoration.",
            "Paracetamol": "Analgesic to alleviate associated throat soreness, sternal chest wall soreness from coughing, and low-grade fever."
        },
        "when_to_see_doctor": ["Cough persisting longer than 3 weeks without improvement", "Coughing up blood or rust-coloured sputum (haemoptysis)", "Shortness of breath, new wheezing, or difficulty catching your breath", "High fever above 38.5°C or fever that returns after initial recovery", "Unexplained weight loss, drenching night sweats, or profound fatigue"],
        "emergency_signs": ["Severe respiratory distress, grunting, or gasping for air", "Bluish tint around lips, face, or nailbeds (cyanosis)", "Inability to speak complete sentences without pausing for breath", "Sudden sharp, stabbing chest pain during inspiration", "Coughing up substantial amounts of fresh red blood"],
        "allergy_note": "Persistent dry nocturnal cough may be a manifestation of cough-variant asthma or allergic post-nasal drip.",
        "references": ["NICE Clinical Guideline NG120: Cough (Acute): Antimicrobial Prescribing", "British Thoracic Society (BTS) Cough Guidelines", "British National Formulary (BNF)"]
    },
    "stomach_problems": {
        "name": "Stomach Disorders (Gastritis / Dyspepsia / Acid Reflux)", "emoji": "🫄",
        "explanation": "Disorders of the upper gastrointestinal tract characterized by mucosal inflammation (gastritis), acid regurgitation (GERD), or functional indigestion (dyspepsia).",
        "causes": ["Excess gastric hydrochloric acid production and reflux into the esophagus", "Gastric mucosal barrier disruption from NSAIDs (ibuprofen, aspirin) or steroids", "Helicobacter pylori bacterial colonisation of the stomach lining", "Dietary irritants (spicy, greasy, deep-fried, acidic foods, caffeine, alcohol)", "Elevated physical or psychological stress causing hypersecretion", "Hiatal hernia or impaired lower esophageal sphincter tone"],
        "symptoms": ["Epigastric burning, gnawing ache, or soreness in the upper abdomen", "Heartburn (substernal retrosternal burning radiating toward throat)", "Acid regurgitation or unpleasant sour/bitter fluid in mouth", "Postprandial bloating, abdominal distension, and excessive belching", "Early satiety (feeling uncomfortably full after small amounts of food)", "Mild nausea, waterbrash, or loss of appetite"],
        "risk_factors": ["Frequent unmonitored use of NSAID pain relievers", "High intake of coffee, tea, carbonated sodas, alcohol, or spicy cuisine", "Cigarette smoking (reduces lower esophageal sphincter pressure)", "Obesity and pregnancy (increased intra-abdominal pressure)", "Irregular, hurried eating habits or eating immediately before sleeping"],
        "complications": ["Peptic ulcer disease (gastric or duodenal ulcers with potential perforation)", "Upper gastrointestinal hemorrhage (hematemesis or melena)", "Reflux esophagitis, esophageal stricture, or Barrett's esophagus", "Iron deficiency anemia from occult mucosal microbleeding"],
        "tests": ["Helicobacter pylori stool antigen test or urea breath test", "Upper gastrointestinal endoscopy (esophagogastroduodenoscopy - EGD)", "Complete blood count (CBC) to screen for occult blood loss and anemia", "Abdominal ultrasound to exclude biliary or gallbladder pathology"],
        "prevention": ["Eat smaller, balanced meals at regular times; avoid large, heavy feasts", "Avoid lying down for at least 2 to 3 hours following a meal", "Avoid known dietary triggers (deep-fried foods, citrus, tomatoes, chocolate, mint, caffeine, alcohol)", "Avoid unnecessary or prolonged use of NSAID pain relievers", "Manage chronic stress through mindfulness, yoga, and adequate rest", "Quit smoking and maintain a healthy body mass index"],
        "home_care": ["Consume mild, non-irritating, bland foods (oatmeal, ripe bananas, plain rice, applesauce, boiled potatoes)", "Sip room-temperature water throughout the day; avoid chugging large quantities of liquid with meals", "Elevate the head of your bed by 15–20 cm (6–8 inches) using bed risers to prevent nocturnal acid reflux", "Wear loose, comfortable clothing that does not compress the waist or abdomen", "Engage in gentle post-meal walking to promote natural gastric motility (avoid rigorous bending or lifting)", "Avoid eating snacks or meals within 3 hours of bedtime"],
        "medicines": ["Antacid", "Omeprazole"],
        "medicine_reasons": {
            "Antacid": "Provides rapid chemical neutralization of existing gastric acid within minutes to relieve acute heartburn, indigestion, and gas.",
            "Omeprazole": "Proton pump inhibitor (PPI) that profoundly reduces gastric acid secretion at its cellular source, promoting mucosal healing for gastritis and reflux."
        },
        "when_to_see_doctor": ["Heartburn or upper stomach pain persisting more than 2 weeks despite OTC measures", "Difficulty, pain, or food getting stuck when swallowing (dysphagia)", "Unexplained, unintentional weight loss", "Persistent or recurrent vomiting", "New onset of dyspeptic symptoms in individuals over 55 years of age"],
        "emergency_signs": ["Vomiting bright red blood or material resembling dark coffee grounds", "Passing black, tarry, foul-smelling stools (melena)", "Sudden, excruciating, rigid abdominal pain ('board-like' abdomen suggesting perforation)", "Severe crushing retrosternal chest pain radiating to arm, neck, or jaw (rule out acute coronary syndrome immediately)", "Dizziness, fainting, or signs of shock accompanying abdominal distress"],
        "allergy_note": "Certain upper GI symptoms can occasionally reflect eosinophilic esophagitis or food intolerance (e.g., celiac disease, lactose intolerance).",
        "references": ["NICE Clinical Guideline CG184: Gastro-oesophageal Reflux Disease and Dyspepsia in Adults", "American College of Gastroenterology (ACG) Guidelines for GERD", "British National Formulary (BNF)"]
    },
    "gastroenteritis": {
        "name": "Gastroenteritis (Stomach Flu / Diarrhoea & Vomiting)", "emoji": "🤢",
        "explanation": "Acute inflammation of the gastrointestinal mucosa, typically viral or bacterial, causing rapid onset of watery diarrhoea, nausea, vomiting, and abdominal cramping.",
        "causes": ["Viral enteropathogens (Norovirus, Rotavirus, Adenovirus)", "Bacterial foodborne pathogens (Campylobacter, Salmonella, pathogenic E. coli)", "Parasitic infections (Giardia, Cryptosporidium)", "Consumption of contaminated food or untreated water", "Person-to-person fecal-oral transmission"],
        "symptoms": ["Frequent, watery, loose stools (diarrhoea)", "Nausea and forceful vomiting", "Diffuse, colicky abdominal cramps and pain", "Low-grade fever and chills", "Headache, muscle aches, and profound weakness", "Signs of dehydration (dry mouth, dark urine, postural dizziness)"],
        "risk_factors": ["Young children and infants (high dehydration vulnerability)", "Frail elderly individuals", "Recent travel to areas with inadequate sanitation", "Eating undercooked poultry, unpasteurized dairy, or raw shellfish", "Immunocompromised status"],
        "complications": ["Severe dehydration and hypovolemic shock", "Dangerous electrolyte imbalances (hypokalaemia, hyponatraemia)", "Acute pre-renal kidney failure", "Post-infectious irritable bowel syndrome (IBS)"],
        "tests": ["Stool microscopy, culture, and sensitivity (MCS) if fever > 38.5°C or bloody diarrhoea", "Serum urea, creatinine, and electrolytes (U&Es) if severe dehydration", "Clinical assessment of hydration status (mucous membranes, skin turgor, capillary refill)"],
        "prevention": ["Wash hands thoroughly with soap and warm water for at least 20 seconds, especially after using the bathroom and before handling food", "Cook poultry, meats, and seafood to safe internal temperatures", "Drink only bottled or boiled water when traveling in developing regions", "Disinfect contaminated surfaces with chlorine-based disinfectants (especially norovirus outbreaks)", "Rotavirus vaccination in infants"],
        "home_care": ["Immediately begin oral rehydration with Oral Rehydration Salts (ORS) solution, sipping small amounts every 5–10 minutes", "Avoid chugging large volumes of fluid at once, which triggers the vomiting reflex", "Once vomiting subsides for 4–6 hours, introduce gentle bland foods (BRAT: bananas, rice, applesauce, toast)", "Avoid dairy products, high-fat foods, spicy dishes, caffeine, and fruit juices high in sorbitol", "Rest in bed and maintain strict isolation and handwashing until 48 hours symptom-free"],
        "medicines": ["Oral Rehydration Salts (ORS)", "Loperamide", "Paracetamol"],
        "medicine_reasons": {
            "Oral Rehydration Salts (ORS)": "First-line, life-saving oral electrolyte-glucose therapy to prevent and reverse dehydration and electrolyte depletion.",
            "Loperamide": "Peripheral anti-motility agent for short-term symptomatic reduction of stool frequency in adults with mild-to-moderate non-bacterial, non-bloody diarrhoea.",
            "Paracetamol": "Antipyretic and mild analgesic to alleviate accompanying fever, headache, and abdominal cramping discomfort."
        },
        "when_to_see_doctor": ["Diarrhoea persisting longer than 48 hours in adults or 24 hours in children", "Inability to retain any oral fluids for more than 12–24 hours", "Signs of clinical dehydration (sunken eyes, no urination for > 8 hours, extreme thirst, postural faintness)", "High fever above 38.5°C", "Severe localized right lower quadrant or persistent focal abdominal pain"],
        "emergency_signs": ["Visible red blood, maroon clots, or black tar in vomit or diarrhoea stools", "Severe confusion, lethargy, or unresponsiveness", "Rapid heart rate, cold clammy extremities, and low blood pressure (shock)", "Anuria (complete absence of urine output for over 12 hours)"],
        "allergy_note": "True acute food allergy causes symptoms within minutes to 2 hours of ingestion and is commonly accompanied by urticaria or facial swelling, whereas food poisoning develops hours later.",
        "references": ["WHO Guidelines on the Clinical Management of Acute Diarrhoea", "NICE Clinical Guideline CG84: Diarrhoea and Vomiting Caused by Gastroenteritis", "British National Formulary (BNF)"]
    },
    "common_cold": {
        "name": "Common Cold (Viral Rhinitis)", "emoji": "🤧",
        "explanation": "A contagious, self-limiting viral infection of the upper respiratory mucosa (nose and nasopharynx), typically caused by rhinoviruses.",
        "causes": ["Rhinovirus (over 100 serotypes)", "Coronaviruses", "Adenoviruses", "Respiratory syncytial virus (RSV)", "Droplet inhalation or contact with contaminated fomites"],
        "symptoms": ["Clear rhinorrhea (runny nose) progressing to thickened mucus", "Nasal congestion and mouth breathing", "Paroxysmal sneezing", "Scratchy, irritated, or sore throat", "Mild, dry, tickly cough", "Low-grade fever, mild headache, and malaise"],
        "risk_factors": ["Young school-aged children with frequent peer exposure", "Weakened immune system or chronic sleep deficits", "Cold dry autumn and winter weather", "High-stress levels"],
        "complications": ["Secondary bacterial acute otitis media (ear infection)", "Acute bacterial rhinosinusitis", "Exacerbation of pre-existing asthma or chronic bronchitis"],
        "tests": ["Clinical assessment based on characteristic upper respiratory symptoms; no routine lab tests indicated", "Throat swab if group A streptococcal pharyngitis is suspected"],
        "prevention": ["Frequent hand hygiene with soap and water or alcohol gel", "Avoid touching eyes, nose, and mouth with unwashed hands", "Disinfect frequently touched communal surfaces (doorknobs, keyboards, phones)", "Maintain good sleep, nutrition, and hydration"],
        "home_care": ["Prioritize adequate physical rest and sleep", "Drink plentiful warm fluids (water, herbal teas, warm lemon water, chicken broth)", "Perform saline nasal rinses or apply saline nasal spray to clear congestion naturally", "Inhale warm steam or take a steamy shower to relieve blocked nasal passages", "Gargle with warm salt water (1/2 teaspoon salt in a glass of warm water) to soothe throat irritation", "Use a clean bedside humidifier to moisten dry winter air"],
        "medicines": ["Cetirizine", "Paracetamol", "Saline Nasal Spray"],
        "medicine_reasons": {
            "Cetirizine": "H1 antihistamine to reduce histamine-mediated rhinorrhea, sneezing, and ocular irritation.",
            "Paracetamol": "Analgesic and antipyretic to relieve headache, sore throat discomfort, and low-grade fever.",
            "Saline Nasal Spray": "Non-medicated isotonic nasal irrigation to naturally flush viral particles and thin thick nasal secretions."
        },
        "when_to_see_doctor": ["Symptoms failing to improve after 10 to 14 days", "Fever rising above 38.5°C or persisting > 3 days", "Severe unilateral facial pain or maxillary pressure suggesting bacterial sinusitis", "Worsening shortness of breath or persistent chest wheezing", "Symptoms improving initially then sharply worsening ('double sickening')"],
        "emergency_signs": ["Severe respiratory distress or difficulty drawing breath", "Stridor or loud whistling respiration", "Severe chest pain during breathing", "Confusion or inability to stay awake"],
        "allergy_note": "Persistent symptoms without fever, especially with prominent itching and clear watery rhinorrhea, frequently represent allergic rhinitis rather than a viral cold.",
        "references": ["CDC Guidelines on Common Cold and Runny Nose", "NICE Clinical Knowledge Summaries: Common Cold", "British National Formulary (BNF)"]
    },
    "influenza": {
        "name": "Influenza (Flu)", "emoji": "🤒",
        "explanation": "An acute, highly contagious respiratory viral infection caused by Influenza A or B viruses, distinguished from the common cold by its sudden explosive onset and prominent systemic toxicity.",
        "causes": ["Influenza A virus", "Influenza B virus", "Aerosolized respiratory droplet transmission", "Direct contact with infected respiratory secretions"],
        "symptoms": ["Sudden onset high fever (38.5–40°C) with prominent chills", "Profound, generalized myalgia (muscle and body aches)", "Intense, throbbing frontal headache", "Extreme physical exhaustion, weakness, and prostration", "Dry, painful, non-productive cough", "Sore throat and nasal congestion", "Decreased appetite"],
        "risk_factors": ["Adults aged 65 and older", "Children under 5 years of age", "Pregnant women", "Individuals with chronic medical conditions (asthma, heart disease, diabetes, renal disease)", "Healthcare personnel"],
        "complications": ["Primary viral pneumonia or secondary bacterial pneumonia (Staph aureus, Strep pneumoniae)", "Acute bronchitis and croup", "Myocarditis or pericarditis", "Exacerbation of underlying cardiopulmonary disease"],
        "tests": ["Clinical diagnostic pattern during known community influenza activity", "Rapid Influenza Diagnostic Test (RIDT) or PCR nasopharyngeal swab", "Chest X-ray if lower respiratory crackles or hypoxaemia are present"],
        "prevention": ["Annual seasonal influenza vaccination", "Thorough and frequent handwashing", "Respiratory etiquette: covering coughs and sneezes into elbows", "Isolating at home while symptomatic until fever-free for at least 24 hours without medication"],
        "home_care": ["Enforce strict bed rest — allow the body to dedicate energy to immune defence", "Maintain aggressive fluid intake (water, electrolyte solutions, hot soups, warm teas)", "Apply a cool, damp compress to forehead for comfort during high fever", "Eat small, light, nutrient-dense meals when appetite allows", "Isolate in a separate room to prevent household transmission", "Avoid all smoke exposure and alcohol"],
        "medicines": ["Paracetamol", "Ibuprofen", "Cetirizine"],
        "medicine_reasons": {
            "Paracetamol": "First-line antipyretic and analgesic to safely combat high fever and systemic body aches.",
            "Ibuprofen": "Anti-inflammatory agent providing potent relief from agonizing back and muscle aches (take with food).",
            "Cetirizine": "Antihistamine to manage accompanying nasal congestion, sneezing, and watery eyes."
        },
        "when_to_see_doctor": ["Patients in high-risk categories (elderly, pregnant, immunocompromised, chronic lung/heart disease)", "Fever persisting longer than 4 to 5 days", "Chest pain, shortness of breath, or productive sputum", "Symptoms resolving initially then returning with higher fever and severe cough ('double sickening')"],
        "emergency_signs": ["Difficulty breathing or shortness of breath at rest", "Chest pressure, pain, or tightness", "Sudden dizziness, confusion, or unsteadiness", "Severe, persistent vomiting with inability to drink fluids", "Cyanosis (bluish lips or skin)"],
        "allergy_note": None,
        "references": ["WHO Influenza Guidelines and Surveillance", "CDC Influenza Clinical Guidance", "British National Formulary (BNF)"]
    },
    "allergic_rhinitis": {
        "name": "Allergic Rhinitis (Hay Fever)", "emoji": "🌿",
        "explanation": "Type I IgE-mediated hypersensitivity inflammation of the nasal mucosal lining triggered by inhaled environmental aeroallergens.",
        "causes": ["Seasonal tree, grass, and weed pollens", "Perennial house dust mites (Dermatophagoides pteronyssinus)", "Domestic pet dander (cats, dogs)", "Indoor and outdoor airborne mould spores", "Occupational airborne dusts and chemicals"],
        "symptoms": ["Repetitive bouts of paroxysmal sneezing", "Clear, profuse, watery rhinorrhea", "Severe itching of the nose, palate, throat, and ears", "Nasal congestion, obstruction, and mouth breathing", "Allergic conjunctivitis: bilateral red, watery, itchy, puffy eyes", "Dark under-eye circles ('allergic shiners') and post-nasal drip cough"],
        "risk_factors": ["Personal or family history of atopic triad (asthma, eczema, allergic rhinitis)", "High indoor humidity promoting dust mites and moulds", "Exposure to environmental tobacco smoke during childhood", "Living in high-pollen agricultural or urban pollution areas"],
        "complications": ["Chronic rhinosinusitis and secondary sinus infections", "Exacerbation of bronchial asthma and airway hyperreactivity", "Eustachian tube dysfunction and serous otitis media", "Chronic sleep disturbance, daytime somnolence, and impaired concentration"],
        "tests": ["Skin prick allergy testing (SPT) with standard inhalant allergen panels", "Serum allergen-specific IgE quantification (ImmunoCAP)", "Nasal endoscopy if nasal polyps or structural deviation suspected"],
        "prevention": ["Monitor daily pollen counts; keep windows closed during morning and evening pollen peaks", "Use high-efficiency particulate air (HEPA) filters in bedroom air purifiers and vacuum cleaners", "Encase mattresses, duvets, and pillows in impermeable allergen-proof barrier covers", "Wash bed linen weekly at 60°C to eliminate house dust mites", "Shower and change clothes immediately after returning indoors from high-pollen environments", "Wear wraparound sunglasses outdoors to block ocular pollen deposition"],
        "home_care": ["Perform daily nasal irrigation with isotonic saline spray or a neti pot to flush inhaled aeroallergens from nasal mucosa", "Apply a cool, damp compress over closed eyelids to relieve ocular itching instead of rubbing", "Keep pets out of bedrooms and off upholstered furniture", "Wipe down smooth indoor surfaces with damp microfibre cloths rather than dry dusting"],
        "medicines": ["Cetirizine", "Saline Nasal Spray"],
        "medicine_reasons": {
            "Cetirizine": "Second-generation H1 antihistamine that rapidly halts histamine-mediated sneezing, watery rhinorrhea, and ocular pruritus without causing major sedation.",
            "Saline Nasal Spray": "Natural isotonic saline cleanser to mechanically clear entrapped pollen, dander, and dust from the mucosal surface safely."
        },
        "when_to_see_doctor": ["Symptoms poorly controlled despite regular OTC antihistamine and saline use", "Severe nasal obstruction preventing restorative sleep or daily activities", "Development of purulent unilateral nasal discharge or facial pain", "Frequent recurrent ear infections or worsening asthma symptoms", "Evaluation for prescription intranasal corticosteroid sprays or allergen immunotherapy"],
        "emergency_signs": ["Sudden acute bronchospasm, audible wheezing, or difficulty breathing", "Swelling of the lips, tongue, or pharynx (anaphylaxis)"],
        "allergy_note": "Environmental allergen avoidance combined with targeted non-sedating antihistamines represents standard evidence-based first-line therapy.",
        "references": ["Allergic Rhinitis and its Impact on Asthma (ARIA) Guidelines", "British Society for Allergy and Clinical Immunology (BSACI) Rhinitis Guideline", "NICE Clinical Knowledge Summaries: Allergic Rhinitis"]
    },
    "throat_infection": {
        "name": "Throat Infection (Pharyngitis / Tonsillitis)", "emoji": "😮",
        "explanation": "Acute inflammation of the pharynx, tonsils, or fauces, most commonly caused by viral pathogens, but occasionally by Group A Streptococcus requiring antibiotic review.",
        "causes": ["Viral pathogens (rhinovirus, adenovirus, Epstein-Barr virus/glandular fever, influenza)", "Group A Beta-Hemolytic Streptococcus (GABHS / Strep throat)", "Mouth breathing, dry air, or vocal strain", "Post-nasal drip from allergic rhinitis"],
        "symptoms": ["Severe pharyngeal pain and soreness, especially when swallowing (odynophagia)", "Erythematous, swollen tonsils, potentially with white exudates or pus spots", "Tender, enlarged anterior cervical lymph nodes in the neck", "Fever and chills", "Referred ear pain, headache, and halitosis (bad breath)"],
        "risk_factors": ["School-age children and adolescents (peak strep throat incidence: 5–15 years)", "Close contact environments (schools, dormitories, military barracks)", "Sharing eating utensils, drinking cups, or toothbrushes", "Smoking and passive smoke exposure"],
        "complications": ["Peritonsillar abscess (Quinsy) requiring urgent drainage", "Acute rheumatic fever and rheumatic heart disease (post-streptococcal complication)", "Post-streptococcal glomerulonephritis", "Spread of infection to deep cervical tissue spaces"],
        "tests": ["Centor or FeverPAIN clinical scoring criteria to estimate bacterial likelihood", "Rapid Antigen Detection Test (RADT) throat swab", "Throat swab microbiology culture and antibiotic sensitivity", "Heterophile antibody test (Monospot) if infectious mononucleosis (glandular fever) is suspected"],
        "prevention": ["Practice strict hand hygiene and use separate eating utensils", "Discard and replace toothbrushes after recovering from throat infections", "Avoid sharing drinks, vape devices, or cigarettes", "Maintain distance from actively coughing individuals"],
        "home_care": ["Gargle with warm salt water (1/2 teaspoon table salt in 240 mL warm water) every 3–4 hours to reduce mucosal edema and pain", "Drink warm soothing liquids (honey and warm water, clear broths, herbal teas)", "Sip cold water or suck on ice chips to numb localized pharyngeal inflammation", "Rest your voice and avoid whispering or shouting, which strains laryngeal structures", "Use a bedside cool-mist humidifier to prevent mucosal drying overnight"],
        "medicines": ["Paracetamol", "Amoxicillin"],
        "medicine_reasons": {
            "Paracetamol": "First-line analgesic to alleviate intense throat pain and lower fever, enabling the patient to swallow fluids and stay hydrated.",
            "Amoxicillin": "Broad-spectrum penicillin antibiotic indicated ONLY if a certified physician confirms a Group A Streptococcal bacterial infection."
        },
        "when_to_see_doctor": ["Severe throat pain lasting longer than 5 to 7 days", "High FeverPAIN / Centor score (fever, purulent tonsillar exudates, tender cervical lymph nodes, absence of cough)", "Difficulty opening the mouth fully (trismus)", "Severe unilateral swelling with uvular deviation (suspected peritonsillar abscess)", "Fine sandpaper-like red skin rash accompanying sore throat (scarlet fever)"],
        "emergency_signs": ["Difficulty breathing or stridor (high-pitched whistling breath sounds)", "Inability to swallow saliva resulting in drooling", "Severe neck swelling or inability to move the neck", "Muffled 'hot potato' voice accompanied by severe unilateral pharyngeal pain"],
        "allergy_note": "Patients with a known penicillin allergy must NEVER be prescribed or take Amoxicillin. Doctors must select non-beta-lactam alternative antibiotics (such as erythromycin or clarithromycin).",
        "references": ["NICE Guideline NG84: Sore Throat (Acute): Antimicrobial Prescribing", "Infectious Diseases Society of America (IDSA) Strep Throat Guidelines", "British National Formulary (BNF)"]
    },
    "ear_infection": {
        "name": "Ear Infection (Acute Otitis Media)", "emoji": "👂",
        "explanation": "Acute infection and inflammation of the middle ear cleft, commonly developing when a viral cold blocks the Eustachian tube, trapping fluid behind the tympanic membrane.",
        "causes": ["Secondary bacterial colonization (Streptococcus pneumoniae, Haemophilus influenzae)", "Primary viral upper respiratory pathogens", "Eustachian tube mucosal swelling and dysfunction"],
        "symptoms": ["Otalgia: sharp, throbbing, or deep aching ear pain", "Temporary muffled hearing or conductive hearing loss", "Sensation of ear fullness, pressure, or popping", "Fever and general irritability", "Otorrhea (drainage of clear fluid, mucus, or pus if eardrum perforates)", "Ear pulling or tugging in infants and toddlers"],
        "risk_factors": ["Children aged 6 months to 2 years (shorter, more horizontal Eustachian tubes)", "Group daycare attendance", "Pacifier use past 6 months of age", "Exposure to second-hand cigarette smoke", "Lack of exclusive breastfeeding in early infancy"],
        "complications": ["Spontaneous tympanic membrane perforation (usually heals spontaneously)", "Chronic suppurative otitis media and persistent conductive hearing deficit", "Acute mastoiditis (infection spreading to mastoid bone behind ear)", "Labyrinthitis or facial nerve palsy (rare)"],
        "tests": ["Pneumatic otoscopy to inspect eardrum erythema, bulging, and reduced mobility", "Tympanometry to assess middle ear pressure and compliance", "Audiometric hearing assessment if infections are recurrent or chronic"],
        "prevention": ["Protect children from all environmental tobacco smoke exposure", "Maintain up-to-date pneumococcal conjugate (PCV) and influenza vaccinations", "Encourage breastfeeding during early infancy", "Hold babies upright during bottle feeding (never feed infants lying flat on their backs)"],
        "home_care": ["Apply a warm (not hot) damp washcloth or wrapped warm compress against the outer ear for 10–15 minutes to soothe pain", "Rest in a slightly elevated, semi-reclined head posture to encourage middle ear fluid drainage", "Keep the affected ear clean and completely dry — do not submerge in bath water", "NEVER insert cotton buds, keys, or any foreign objects into the ear canal"],
        "medicines": ["Paracetamol", "Ibuprofen", "Amoxicillin"],
        "medicine_reasons": {
            "Paracetamol": "First-line safe analgesic to relieve acute middle ear pain and manage fever.",
            "Ibuprofen": "Anti-inflammatory NSAID providing potent pain relief for deep throbbing otalgia (administer with food).",
            "Amoxicillin": "First-line antibiotic indicated when clinical evaluation by a physician confirms severe bacterial otitis media."
        },
        "when_to_see_doctor": ["Ear pain failing to resolve within 48 to 72 hours", "Fluid, pus, or blood discharging from the ear canal", "Infants under 6 months old with any suspected ear pain or unexplained fever", "Marked hearing reduction persisting after pain has subsided", "Bilateral ear pain in young children"],
        "emergency_signs": ["Redness, tender swelling, or tenderness over the mastoid bone directly behind the ear", "Drooping or weakness of one side of the face (facial nerve involvement)", "Severe dizziness, vertigo, and loss of balance", "Stiff neck, lethargy, or high fever with ear symptoms"],
        "allergy_note": "Patients with confirmed penicillin allergy must NOT receive Amoxicillin; physicians prescribe macrolides or alternative classes.",
        "references": ["American Academy of Pediatrics (AAP) Clinical Practice Guideline: Acute Otitis Media", "NICE Clinical Guideline: Otitis Media (Acute): Antimicrobial Prescribing", "British National Formulary (BNF)"]
    },
    "uti": {
        "name": "Urinary Tract Infection (UTI / Cystitis)", "emoji": "🫧",
        "explanation": "Bacterial colonization and infection of the urinary tract mucosa, most frequently ascending infection of the bladder (acute cystitis).",
        "causes": ["Uropathogenic Escherichia coli (E. coli, ~80% of cases) originating from the bowel flora", "Other enteric bacteria (Klebsiella, Proteus, Enterococcus)", "Ascending bacterial spread along the short female urethra", "Sexual intercourse introducing periurethral bacteria"],
        "symptoms": ["Dysuria: sharp, burning, or scalding pain during urination", "Urinary frequency (needing to urinate every few minutes)", "Urinary urgency (sudden, intense, irresistible need to void)", "Suprapubic pelvic aching, heaviness, or pressure", "Cloudy, turbid, dark, or foul-smelling urine", "Microscopic or visible blood in the urine (hematuria)"],
        "risk_factors": ["Female anatomy (short urethra located close to anus)", "Sexual activity and diaphragm/spermicide use", "Post-menopausal estrogen deficiency (altered vaginal microbiome)", "Urinary catheterisation", "Diabetes mellitus", "Incomplete bladder emptying or anatomical urinary abnormalities"],
        "complications": ["Ascending pyelonephritis (kidney infection with renal parenchymal inflammation)", "Recurrent chronic UTIs (> 3 episodes/year)", "Urosepsis (life-threatening systemic bloodstream infection)"],
        "tests": ["Urine dipstick analysis (positive nitrites and leukocyte esterase)", "Midstream clean-catch urine microscopy, culture, and sensitivity (MC&S)", "Renal and bladder ultrasound in recurrent or complicated male/paediatric cases"],
        "prevention": ["Drink generous amounts of clean water daily (1.5 to 2.5 litres) to continuously flush the urinary tract", "Urinate promptly following sexual intercourse to clear introduced bacteria", "Always wipe strictly from front to back after using the toilet (for women)", "Avoid delaying urination when the urge is felt; empty bladder completely", "Avoid harsh feminine hygiene sprays, perfumed bubble baths, and douching", "Wear breathable, loose-fitting cotton underwear"],
        "home_care": ["Substantially increase daily water intake to promote frequent dilute urinary flushing", "Apply a warm heating pad or hot water bottle to the lower abdomen or suprapubic region to ease cramping", "Avoid bladder irritants including coffee, strong black tea, alcohol, carbonated drinks, and acidic citrus juices", "Rest comfortably and ensure immediate access to a toilet"],
        "medicines": ["Paracetamol", "Amoxicillin"],
        "medicine_reasons": {
            "Paracetamol": "Analgesic to relieve uncomfortable suprapubic pelvic cramping and burning during urination.",
            "Amoxicillin": "Antibiotic prescribed strictly upon confirmed bacterial diagnosis (where local antibiogram sensitivity permits)."
        },
        "when_to_see_doctor": ["Any suspected UTI — formal medical evaluation and targeted antibiotic prescription are essential", "Symptoms not improving within 48 hours of starting prescribed antibiotics", "Visible blood in the urine (hematuria)", "Any male patient or pregnant woman experiencing urinary symptoms (always considered complicated)", "Recurrent episodes (> 2 within 6 months)"],
        "emergency_signs": ["High fever (> 38.5°C) accompanied by shaking chills and rigors", "Unilateral or bilateral flank, lower back, or kidney angle tenderness (pyelonephritis)", "Persistent nausea and vomiting with inability to take oral fluids or medications", "Severe confusion, drowsiness, or delirium (especially in elderly patients)"],
        "allergy_note": "Patients allergic to penicillin cannot take Amoxicillin and require alternative first-line agents like Nitrofurantoin, Trimethoprim, or Cefalexin as determined by culture sensitivity.",
        "references": ["NICE Clinical Guideline NG109: Urinary Tract Infection (Lower): Antimicrobial Prescribing", "European Association of Urology (EAU) Guidelines on Urological Infections", "British National Formulary (BNF)"]
    },
    "asthma": {
        "name": "Asthma / Bronchial Hyperreactivity", "emoji": "💨",
        "explanation": "A chronic inflammatory airway disorder characterized by episodic, reversible bronchial smooth muscle constriction, mucosal edema, and mucus hypersecretion.",
        "causes": ["Inhaled allergen exposure (pollen, dust mites, pet dander, moulds)", "Viral upper respiratory infections (rhinovirus, RSV)", "Inhalation of cold, dry air or sudden weather shifts", "Physical exercise without adequate warm-up (exercise-induced bronchoconstriction)", "Air pollutants, chemical fumes, and tobacco smoke", "Certain medications: NSAIDs (aspirin, ibuprofen) and non-selective beta-blockers"],
        "symptoms": ["Expiratory wheezing (musical whistling breath sound)", "Shortness of breath (dyspnea) especially with exertion or at night", "Persistent chest tightness or feeling like a band is around the thorax", "Nocturnal or early-morning dry coughing fits", "Tachypnea (rapid breathing)"],
        "risk_factors": ["Personal history of eczema, allergic rhinitis, or atopy", "Family history of asthma or allergic disease in first-degree relatives", "Childhood exposure to environmental tobacco smoke", "Occupational exposure to chemical irritants, flour, or resins", "Obesity"],
        "complications": ["Severe acute asthma exacerbation (status asthmaticus)", "Respiratory failure requiring intensive care and mechanical ventilation", "Permanent airway remodeling and fixed airflow obstruction", "Severe restriction of sports and physical activities"],
        "tests": ["Spirometry with pre- and post-bronchodilator reversibility testing (FEV1/FVC)", "Peak Expiratory Flow (PEF) diurnal variability monitoring", "Fractional exhaled nitric oxide (FeNO) to assess eosinophilic airway inflammation", "Skin prick or specific IgE allergy testing to identify triggers"],
        "prevention": ["Strictly adhere to daily prescribed preventer/controller inhalers (inhaled corticosteroids)", "Identify and systematically avoid personal allergic and environmental triggers", "Obtain annual influenza and pneumococcal immunizations", "Always carry a rescue/reliever inhaler (e.g. Salbutamol / Albuterol)", "Have an individualized written Personal Asthma Action Plan (PAAP)"],
        "home_care": ["Follow the personal written Asthma Action Plan", "Sit upright comfortably during mild shortness of breath — avoid lying flat", "Practice slow, calm, pursed-lip breathing to reduce work of breathing", "Ensure indoor environment is completely smoke-free and well-ventilated", "Avoid cold air exposure by wearing a scarf over mouth and nose in winter"],
        "medicines": ["Cetirizine"],
        "medicine_reasons": {
            "Cetirizine": "Second-generation H1 antihistamine to suppress allergic triggers and co-existing allergic rhinitis which can provoke asthma flares."
        },
        "when_to_see_doctor": ["Symptoms occurring more than twice a week during normal activities", "Waking up at night due to coughing or wheezing more than once a month", "Needing to use reliever/rescue inhaler more than twice weekly", "Peak flow readings dropping into the yellow zone (50–80% of personal best)"],
        "emergency_signs": ["Severe breathlessness: unable to speak full sentences in one breath", "Reliever inhaler giving little or no relief, or relief lasting under 2 hours", "Chest in-drawing / retractions (sucking in of skin between ribs or at base of neck)", "Lips, tongue, or fingertips turning pale, grey, or blue (cyanosis)", "Peak flow reading below 50% of personal best (red medical emergency zone)"],
        "allergy_note": "CRITICAL: Patients with asthma must exercise extreme caution with NSAIDs (Ibuprofen, Aspirin). 10–20% of adult asthmatics suffer from Aspirin-Exacerbated Respiratory Disease (AERD), where NSAIDs trigger severe bronchospasm.",
        "references": ["Global Initiative for Asthma (GINA) Global Strategy for Asthma Management", "British Thoracic Society (BTS) / SIGN British Guideline on the Management of Asthma", "NICE Guideline NG80: Asthma: Diagnosis, Monitoring and Chronic Management"]
    },
    "back_pain": {
        "name": "Back Pain / Musculoskeletal Strain", "emoji": "🦴",
        "explanation": "Acute or subacute discomfort located in the lumbosacral or cervical region, most commonly arising from paraspinal muscle or ligamentous strain.",
        "causes": ["Improper lifting technique or lifting excessive weights without knee flexion", "Poor ergonomic sitting posture and sedentary desk work", "Acute muscle spasm or lumbar ligamentous strain", "Intervertebral disc bulge or herniation with nerve root impingement (sciatica)", "Degenerative spinal osteoarthritis or spondylosis"],
        "symptoms": ["Dull, aching, or sharp localized pain in the lower back or lumbar area", "Stiffness and reduced spinal range of motion when bending or twisting", "Paraspinal muscle tightness, tenderness, and palpable spasms", "Pain radiating into the buttock, posterior thigh, or calf (sciatica)", "Pain exacerbated by prolonged sitting, standing, or walking"],
        "risk_factors": ["Sedentary lifestyle with weak abdominal core and gluteal musculature", "Jobs requiring heavy manual handling or repetitive twisting", "Obesity and poor postural ergonomics", "Psychological distress, job dissatisfaction, or chronic stress", "Tobacco smoking (impairs intervertebral disc microcirculation)"],
        "complications": ["Transition into chronic disabling back pain lasting > 12 weeks", "Persistent nerve root radiculopathy with lower extremity motor weakness", "Workplace absenteeism and psychological depression"],
        "tests": ["Comprehensive musculoskeletal and neurological examination (straight leg raise, reflex testing, dermatome sensation, motor power)", "Lumbar spine MRI if radiculopathy or red flag symptoms are present", "Lumbar spine X-ray only if trauma, structural deformity, or osteoporosis is suspected"],
        "prevention": ["Maintain strong core and paraspinal muscles with regular low-impact exercises (walking, swimming, pilates)", "Use correct manual handling: bend knees, keep load close to chest, and avoid twisting spine", "Optimize workplace desk ergonomics (chair lumbar support, feet flat on floor, monitor at eye level)", "Avoid prolonged static sitting — stand up and stretch every 30–45 minutes", "Maintain a healthy body weight and stop smoking"],
        "home_care": ["Stay gently active — strictly avoid prolonged bed rest (more than 24–48 hours worsens back stiffness)", "Apply an ice pack wrapped in a towel for 15–20 minutes at a time during the initial 48 hours to curb acute inflammation", "After 48 hours, switch to moist heat pads or warm baths to relax tight, spastic muscles", "Sleep on a firm, supportive mattress; place a pillow between knees when sleeping on side", "Perform gentle knee-to-chest and cat-cow lumbar mobilization stretches as tolerated"],
        "medicines": ["Ibuprofen", "Paracetamol"],
        "medicine_reasons": {
            "Ibuprofen": "Anti-inflammatory NSAID to target localized spinal muscle, tendon, and ligamentous inflammation (take with food).",
            "Paracetamol": "Mild analgesic suitable as an adjunct or for individuals who cannot tolerate NSAIDs due to stomach or renal restrictions."
        },
        "when_to_see_doctor": ["Back pain not improving after 2 to 4 weeks of self-care", "Pain radiating down the leg past the knee with numbness or tingling", "Pain triggered by a major fall or motor vehicle collision", "Back pain in individuals with a history of cancer, osteoporosis, or immunosuppression", "Unexplained fever or unintended weight loss accompanying back pain"],
        "emergency_signs": ["RED FLAG (Cauda Equina Syndrome): Loss of bowel or bladder control (incontinence or urinary retention)", "RED FLAG: 'Saddle anesthesia' (numbness around the anus, genitals, and buttocks)", "RED FLAG: Progressive bilateral weakness in the legs or inability to lift the foot ('foot drop')"],
        "allergy_note": None,
        "references": ["NICE Guideline NG59: Low Back Pain and Sciatica in Over 16s", "WHO Guideline on Low Back Pain", "British National Formulary (BNF)"]
    },
    "food_allergy": {
        "name": "Food Allergy", "emoji": "🥜",
        "explanation": "An immune-mediated hypersensitivity reaction (typically IgE-driven) triggered rapidly following the ingestion of specific food proteins.",
        "causes": ["Peanuts and tree nuts (walnuts, almonds, cashews)", "Crustacean shellfish and molluscs", "Cow's milk dairy proteins", "Hen's eggs", "Wheat and gluten", "Soybeans and sesame"],
        "symptoms": ["Pruritus, tingling, or itching inside the mouth and on lips", "Urticarial wheals (hives), flushing, or generalized skin rash", "Angioedema (swelling of lips, face, tongue, or eyelids)", "Gastrointestinal distress: nausea, vomiting, colicky abdominal cramps, diarrhoea", "Tightness in throat, hoarse voice, or difficulty swallowing", "Wheezing, shortness of breath, and lightheadedness"],
        "risk_factors": ["Pre-existing atopic eczema in infancy", "Family history of severe food allergy or anaphylaxis", "Known asthma (substantially increases anaphylaxis fatality risk)"],
        "complications": ["Systemic anaphylactic shock (life-threatening airway and cardiovascular collapse)", "Nutritional deficiencies from overly restrictive unguided diets", "Severe psychological anxiety regarding food and dining out"],
        "tests": ["Skin prick allergy testing (SPT) with verified food extracts", "Serum allergen-specific IgE blood assays", "Supervised oral food challenge in a hospital allergy facility"],
        "prevention": ["Completely avoid known trigger foods and all culinary items prepared in shared cooking facilities", "Rigidly inspect ingredient labels for allergen warnings ('may contain nuts', 'processed in a facility that handles shellfish')", "Inform restaurant chefs, servers, and flight attendants of food allergies", "Carry two prescribed adrenaline auto-injectors (e.g. EpiPens) at all times"],
        "home_care": ["Immediately eliminate and distance yourself from the suspected trigger food", "Take an oral antihistamine if symptoms are strictly limited to mild localized oral itching or mild hives", "Rest quietly and monitor vital signs closely", "Have someone stay with you to observe for any delayed systemic progression", "Never attempt to 'build tolerance' by eating small amounts of an allergenic food at home"],
        "medicines": ["Cetirizine"],
        "medicine_reasons": {
            "Cetirizine": "Oral H1 antihistamine to alleviate mild cutaneous itching, hives, and mucosal swelling from minor allergic exposure."
        },
        "when_to_see_doctor": ["Any suspected new food allergic reaction requires comprehensive formal allergy evaluation", "To obtain a formal prescription and demonstration for an adrenaline auto-injector", "For registered dietitian consultation to ensure nutritional adequacy while eliminating food groups"],
        "emergency_signs": ["EMERGENCY (Anaphylaxis): Throat closing, tongue swelling, or hoarse voice", "EMERGENCY: Audible wheezing, persistent coughing, or severe difficulty breathing", "EMERGENCY: Sudden dizziness, collapse, confusion, or pallor", "EMERGENCY: Use your adrenaline auto-injector immediately and dial 108 / 112 emergency services"],
        "allergy_note": "A confirmed diagnosis requires specialist allergy clinic evaluation. Do not assume or self-diagnose an allergy without clinical verification.",
        "references": ["BSACI Guidelines for the Management of Food Allergy", "EAACI Guidelines on Food Allergy and Anaphylaxis", "NICE Clinical Guideline CG116: Food Allergy in Under 19s"]
    },
    "drug_allergy": {
        "name": "Medicine (Drug) Allergy", "emoji": "💊",
        "explanation": "An immunologically mediated adverse drug reaction to a pharmacological agent, distinct from predictable drug side effects or pharmacological toxicity.",
        "causes": ["Beta-lactam antibiotics (penicillin, amoxicillin, cephalosporins)", "Non-Steroidal Anti-Inflammatory Drugs (aspirin, ibuprofen, naproxen)", "Sulfonamide antibiotics and non-antibiotic sulfas", "Anticonvulsants and antiepileptic medications", "Neuromuscular blocking agents and radiocontrast media"],
        "symptoms": ["Morbilliform or urticarial skin eruption (hives or red papular rash)", "Intense generalized cutaneous pruritus (itching)", "Facial, periorbital, or lip angioedema", "Drug-induced fever developing days after starting therapy", "Wheezing or bronchospasm", "Severe anaphylaxis (acute cardiovascular collapse)"],
        "risk_factors": ["Previous documented allergic reaction to the same or chemically related drug class", "Frequent or repeated intermittent courses of antibiotics", "High-dose or parenteral (intravenous) drug administration", "Underlying systemic autoimmune diseases"],
        "complications": ["Systemic anaphylaxis", "Severe cutaneous adverse reactions (SCARs): Stevens-Johnson Syndrome (SJS) and Toxic Epidermal Necrolysis (TEN)", "Drug Reaction with Eosinophilia and Systemic Symptoms (DRESS)", "Drug-induced acute interstitial nephritis or hepatitis"],
        "tests": ["Detailed clinical chronological drug allergy history", "Skin prick and intradermal testing for penicillin determinants (specialist clinic only)", "Drug-specific IgE serum testing where validated", "Supervised graded drug provocation challenge under resuscitation facilities"],
        "prevention": ["Always prominently report all known drug allergies to every physician, dentist, nurse, and pharmacist", "Wear medical alert identification jewellery (bracelet or necklace) detailing confirmed drug allergies", "Carry an updated list of allergic drugs and prohibited related classes in your wallet and phone", "Ensure confirmed drug allergies are recorded in hospital and clinic electronic health records"],
        "home_care": ["Immediately stop taking the suspected medication (seek urgent clinical advice if stopping a critical prescription)", "Take a non-sedating antihistamine if symptoms are strictly limited to a mild, localized itchy rash", "Keep the suspect medicine packet, label, and batch number to show attending clinicians", "Drink plenty of water to help clear eliminated metabolites"],
        "medicines": ["Cetirizine"],
        "medicine_reasons": {
            "Cetirizine": "H1 antihistamine to alleviate mild drug-induced pruritus and urticarial skin wheals."
        },
        "when_to_see_doctor": ["Any unexpected rash, fever, or swelling developing during a course of medication requires clinical review", "To obtain documented formal allergy testing and verify safe alternative antibiotic or analgesic classes", "To update national or regional adverse drug reaction monitoring databases"],
        "emergency_signs": ["Difficulty breathing, wheezing, or feeling of throat constriction", "Swelling of the tongue, lips, mouth, or vocal cords", "Dizziness, fainting, rapid weak pulse, or clammy skin", "Blistering, peeling, or detachment of skin or mucous membranes (lips, eyes, genitals)"],
        "allergy_note": "A confirmed diagnosis requires specialist allergy clinic evaluation. Do not assume or self-diagnose an allergy without clinical verification.",
        "references": ["NICE Clinical Guideline CG183: Drug Allergy: Diagnosis and Management", "BSACI Guidelines for the Management of Drug Allergy", "British National Formulary (BNF)"]
    },
    "general_health_evaluation": {
        "name": "General Health Evaluation & Symptom Review", "emoji": "🩺",
        "explanation": "A comprehensive clinical review for non-specific, constitutional, or multi-system symptoms that require professional in-person medical evaluation and objective diagnostics.",
        "causes": ["Early or resolving viral infections", "Metabolic, endocrine, or nutritional imbalances", "Physical fatigue, overexertion, and psychological stress", "Side effects from concurrent medications", "Underlying systemic conditions requiring clinical assessment"],
        "symptoms": ["General malaise and fatigue", "Non-specific body aches or mild discomfort", "Appetite changes or mild digestive awareness", "Unspecified constitutional symptoms"],
        "risk_factors": ["Chronic emotional or physical stress", "Inadequate sleep or poor nutrition", "Polypharmacy without recent medication review"],
        "complications": ["Delay in diagnosing underlying conditions if persistent symptoms are neglected"],
        "tests": ["Comprehensive physical examination by a general practitioner", "Basic blood tests (Complete Blood Count, Basic Metabolic Panel, Liver Function)", "Vital signs assessment (blood pressure, heart rate, temperature, oxygen saturation)"],
        "prevention": ["Maintain a balanced diet rich in whole foods, vegetables, and lean proteins", "Ensure 7 to 9 hours of restorative sleep nightly", "Stay consistently hydrated throughout the day", "Schedule regular preventive health check-ups with your family doctor"],
        "home_care": ["Prioritize restorative rest and manage daily physical exertion", "Drink sufficient clean water and clear fluids throughout the day", "Eat regular, light, easily digestible meals", "Keep a symptom diary recording when symptoms appear, their severity, and potential triggers", "Avoid starting new OTC medications without consulting a healthcare professional"],
        "medicines": ["Paracetamol"],
        "medicine_reasons": {
            "Paracetamol": "Mild analgesic and antipyretic to relieve generalized non-specific body aching and malaise."
        },
        "when_to_see_doctor": ["Symptoms persisting for more than 7 to 10 days without clear explanation", "Unintended weight loss, night sweats, or recurring fevers", "Any new or changing symptoms causing functional impairment", "Whenever you feel uncertain about your health condition"],
        "emergency_signs": ["Severe chest pain, pressure, or shortness of breath", "Sudden weakness, numbness, or difficulty speaking", "Sudden severe headache or loss of consciousness", "Coughing up blood or passing bloody stools"],
        "allergy_note": None,
        "references": ["WHO Guidelines on Primary Health Care", "NICE Clinical Knowledge Summaries", "British National Formulary (BNF)"]
    }
}

# ─── SYMPTOM TO CONDITION MAPPING ─────────────────────────────────────────────
SYMPTOM_CONDITION_MAP = [
    # Fever
    (["fever", "high temperature", "temperature", "chills", "sweating", "pyrexia", "hot body", "febrile", "shivering"], ["fever"]),
    # Headache
    (["headache", "head pain", "migraine", "throbbing head", "temple pain", "head ache", "head throbbing"], ["headache"]),
    # Skin allergy / rash / itching
    (["rash", "hives", "urticaria", "itchy skin", "skin rash", "skin allergy", "allergic rash", "red spots", "itching", "itch", "welts", "dermatitis", "eczema", "skin itching"], ["skin_allergy"]),
    # Cough / Bronchitis
    (["cough", "coughing", "dry cough", "chesty cough", "phlegm", "mucus", "bronchitis", "chest congestion", "throat tickle", "hacking cough"], ["cough_bronchitis"]),
    # Stomach problems / Gastritis / Acidity / Heartburn / Indigestion
    (["stomach problem", "stomach problems", "stomach pain", "stomach ache", "tummy ache", "belly pain", "acidity", "acid reflux", "heartburn", "gerd", "gastritis", "indigestion", "dyspepsia", "bloating", "burning stomach", "stomach burning", "sour stomach", "gas", "acid"], ["stomach_problems"]),
    # Gastroenteritis / Diarrhoea / Vomiting / Food poisoning
    (["diarrhea", "diarrhoea", "loose stool", "loose stools", "loose motion", "loose motions", "vomiting", "nausea", "food poisoning", "gastro", "gastroenteritis", "stomach flu", "vomit"], ["gastroenteritis"]),
    # Common cold / nasal congestion
    (["cold", "common cold", "runny nose", "blocked nose", "stuffy nose", "sneezing", "nasal congestion", "congestion"], ["common_cold"]),
    # Allergic rhinitis / hay fever
    (["hay fever", "allergic rhinitis", "pollen allergy", "dust allergy", "pet allergy", "itchy eyes", "watery eyes"], ["allergic_rhinitis"]),
    # Throat infection / sore throat
    (["sore throat", "throat pain", "throat infection", "tonsillitis", "tonsil", "tonsils", "painful swallowing", "throat sore", "pharyngitis", "strep"], ["throat_infection"]),
    # Ear infection
    (["ear pain", "earache", "ear ache", "ear infection", "ear discharge", "otitis"], ["ear_infection"]),
    # Urinary tract infection
    (["burning urination", "frequent urination", "painful urination", "urinary", "uti", "cystitis", "bladder infection", "urine infection", "burning urine"], ["uti"]),
    # Flu
    (["flu", "influenza", "body ache", "body pain", "muscle ache", "extreme tiredness", "fatigue", "malaise"], ["influenza"]),
    # Asthma / Wheezing
    (["wheezing", "asthma", "chest tightness", "shortness of breath", "breathless", "wheeze"], ["asthma"]),
    # Back pain
    (["back pain", "lower back", "backache", "spine pain", "sciatica", "joint pain", "muscle pain"], ["back_pain"]),
    # Food allergy
    (["food allergy", "allergic to food", "nut allergy", "shellfish allergy", "peanut allergy", "dairy allergy"], ["food_allergy"]),
    # Drug allergy
    (["medicine allergy", "drug allergy", "allergic to medicine", "reaction to medicine", "allergic to antibiotic", "penicillin allergy"], ["drug_allergy"]),
]

# ─── EMERGENCY KEYWORDS ───────────────────────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "can't breathe", "cannot breathe", "difficulty breathing", "breathing difficulty",
    "shortness of breath", "unable to breathe", "can not breathe", "choking",
    "throat swelling", "swollen throat", "throat closing", "throat tightening", "throat swollen",
    "anaphylaxis", "anaphylactic", "airway closing",
    "fainting", "fainted", "passed out", "unconscious", "loss of consciousness", "syncope",
    "chest pain", "severe chest pain", "heart attack", "crushing chest",
    "lips swelling", "tongue swelling", "face swelling", "swollen face", "lips swollen", "tongue swollen",
    "face swollen", "blue lips", "cyanosis", "coughing blood", "vomiting blood", "black stool", "melena"
]

# ─── ALLERGEN CATEGORIES ─────────────────────────────────────────────────────
COMMON_ALLERGENS = {
    "food": ["peanut", "nut", "shellfish", "seafood", "dairy", "milk", "egg", "wheat", "gluten", "soy", "fish", "sesame", "cashew", "almond"],
    "medicine": ["penicillin", "amoxicillin", "aspirin", "ibuprofen", "nsaid", "sulfa", "sulfonamide", "codeine", "morphine", "cetirizine", "paracetamol", "antibiotic", "cephalosporin"],
    "environmental": ["pollen", "dust", "dust mite", "mold", "mould", "pet dander", "cat", "dog", "grass", "latex", "cockroach"],
    "insect": ["bee", "wasp", "insect bite", "hornet", "ant sting"]
}

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────
def check_emergency(text):
    text_l = text.lower()
    triggered = [kw for kw in EMERGENCY_KEYWORDS if kw in text_l]
    if triggered:
        return {
            "triggered_by": list(set(triggered)),
            "message": "One or more reported symptoms (such as respiratory difficulty, severe swelling, chest pain, or loss of consciousness) may indicate an ACUTE EMERGENCY or SEVERE SYSTEMIC ALLERGIC REACTION (ANAPHYLAXIS).",
            "action": "DIAL EMERGENCY MEDICAL SERVICES (108 / 112) OR GO TO THE NEAREST HOSPITAL EMERGENCY DEPARTMENT IMMEDIATELY. DO NOT DELAY OR WAIT FOR AT-HOME MEDICINES TO ACT."
        }
    return None

def _matches_phrase(phrase, text):
    # Word boundary matching for phrase
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return bool(re.search(pattern, text, re.IGNORECASE))

def detect_conditions_from_text(symptoms_text, conditions_text):
    combined = (symptoms_text + " " + conditions_text).lower()
    found = []
    # 1. Match from map
    for keywords, conds in SYMPTOM_CONDITION_MAP:
        if any(_matches_phrase(kw, combined) for kw in keywords):
            for c in conds:
                if c not in found:
                    found.append(c)

    # 2. Heuristic word-boundary checks for direct terms
    if any(_matches_phrase(w, combined) for w in ["cough", "coughing", "phlegm", "bronchitis"]) and "cough_bronchitis" not in found:
        found.append("cough_bronchitis")
    if any(_matches_phrase(w, combined) for w in ["stomach", "acidity", "indigestion", "heartburn", "gastric", "reflux", "belly", "tummy", "acid"]) and "stomach_problems" not in found:
        found.append("stomach_problems")
    if any(_matches_phrase(w, combined) for w in ["diarrhea", "diarrhoea", "loose stool", "loose stools", "loose motion", "loose motions", "vomit", "vomiting", "food poisoning"]) and "gastroenteritis" not in found:
        found.append("gastroenteritis")
    if any(_matches_phrase(w, combined) for w in ["rash", "rashes", "itch", "itching", "itchy", "hive", "hives", "allergy", "allergic", "urticaria", "eczema", "dermatitis"]) and "skin_allergy" not in found:
        found.append("skin_allergy")
    if any(_matches_phrase(w, combined) for w in ["headache", "headaches", "migraine", "migraines"]) and "headache" not in found:
        found.append("headache")
    if any(_matches_phrase(w, combined) for w in ["fever", "fevers", "temperature", "chills", "pyrexia", "shivering"]) and "fever" not in found:
        found.append("fever")
    if any(_matches_phrase(w, combined) for w in ["throat", "tonsil", "tonsillitis", "pharyngitis", "sore throat"]) and "throat_infection" not in found:
        found.append("throat_infection")
    if any(_matches_phrase(w, combined) for w in ["ear", "ears", "earache", "otitis"]) and "ear_infection" not in found:
        found.append("ear_infection")
    if any(_matches_phrase(w, combined) for w in ["urine", "urination", "uti", "bladder", "cystitis"]) and "uti" not in found:
        found.append("uti")

    # 3. Fallback: if user typed something but nothing matched, provide general health evaluation
    if not found:
        if len(symptoms_text.strip()) > 0 or len(conditions_text.strip()) > 0:
            found.append("general_health_evaluation")

    return found

def analyze_allergy_profile(allergies_text, symptoms_text, conditions_text):
    all_text = (allergies_text + " " + symptoms_text + " " + conditions_text).lower()
    allergies_lower = allergies_text.lower()
    identified = {cat: [] for cat in COMMON_ALLERGENS}

    for cat, allergens in COMMON_ALLERGENS.items():
        for a in allergens:
            if a in all_text and a not in identified[cat]:
                identified[cat].append(a)

    # Cross-reference with all medicines in MEDICINES_DETAIL
    medicines_to_avoid = []
    for med_name, detail in MEDICINES_DETAIL.items():
        for allergen in detail.get("allergens", []):
            if allergen in allergies_lower:
                medicines_to_avoid.append({
                    "name": med_name,
                    "allergen": allergen,
                    "reason": f"Patient reported an allergy to '{allergen}', which is an active ingredient or pharmacologically cross-reactive substance in {med_name}."
                })
                break

    # Detect allergic symptom keywords
    allergy_symptom_words = ["sneezing", "itching", "itchy", "rash", "hives", "urticaria", "runny nose", "watery eyes", "itchy eyes", "swelling", "wheals"]
    symptoms_detected = [w for w in allergy_symptom_words if w in symptoms_text.lower()]
    has_allergy_symptoms = len(symptoms_detected) > 0

    return {
        "identified": identified,
        "has_any": any(len(v) > 0 for v in identified.values()),
        "medicines_to_avoid": medicines_to_avoid,
        "has_allergy_symptoms": has_allergy_symptoms,
        "allergy_symptoms_detected": list(set(symptoms_detected)),
        "disclaimer": "Allergy identification here is based on patient inputs and keyword recognition. A confirmed clinical diagnosis requires formal diagnostic testing (such as skin prick testing or specific IgE blood assays) by a qualified allergist."
    }

def build_medicine_analysis(med_name, condition_reasons, age, weight, conditions_text, current_meds_lower, allergies_lower):
    detail = MEDICINES_DETAIL.get(med_name, {})
    warnings = []
    is_contraindicated = False
    contraindication_reason = None

    # 1. Allergy check
    for allergen in detail.get("allergens", []):
        if allergen in allergies_lower:
            is_contraindicated = True
            contraindication_reason = f"⛔ CONTRAINDICATED (ALLERGY RISK): Patient reported an allergy to '{allergen}', which is a component of {med_name}. DO NOT take this medication without certified specialist allergist clearance."
            break

    # 2. Age-specific checks
    if age is not None:
        if age < 12:
            child_note = detail.get("age_notes", {}).get("child", "")
            if child_note:
                warnings.append(f"👶 Paediatric Safety Note: {child_note}")
            if med_name == "Dextromethorphan" and age < 6:
                is_contraindicated = True
                contraindication_reason = "⛔ CONTRAINDICATED: OTC cough suppressants containing dextromethorphan are not recommended for children under 6 years of age (FDA/AAP alert)."
            if med_name == "Loperamide":
                is_contraindicated = True
                contraindication_reason = "⛔ CONTRAINDICATED: Loperamide is strictly contraindicated in children under 12 years of age due to risks of paralytic ileus and toxic megacolon."
        elif age >= 65:
            elderly_note = detail.get("age_notes", {}).get("elderly", "")
            if elderly_note:
                warnings.append(f"👴 Geriatric Safety Note: {elderly_note}")

    # 3. Weight-specific check
    if weight is not None:
        if age is not None and age < 18:
            warnings.append(f"⚖️ Weight-based Dosing: Patient weight is {weight} kg. Paediatric dosages must be calculated strictly in milligrams per kilogram (mg/kg) by a doctor or pharmacist.")

    # 4. Condition-specific contraindications & cautions
    cond = conditions_text.lower()
    if med_name == "Ibuprofen":
        if "asthma" in cond:
            warnings.append("⚠️ ASTHMA ALERT: NSAIDs (such as Ibuprofen) can trigger bronchospasm and severe asthma exacerbations in susceptible asthmatics (AERD). Avoid unless specifically cleared by your pulmonologist.")
        if any(w in cond for w in ["ulcer", "peptic", "gastric", "gerd", "stomach"]):
            warnings.append("⚠️ GI ULCER ALERT: Ibuprofen directly irritates the gastric mucosa and increases peptic ulceration and GI bleeding risk. Use with extreme caution and always take with food.")
        if any(w in cond for w in ["hypertension", "blood pressure", "heart", "cardiac"]):
            warnings.append("⚠️ CARDIOVASCULAR ALERT: NSAIDs cause fluid retention and may elevate systemic blood pressure or blunt antihypertensive medications.")
        if any(w in cond for w in ["kidney", "renal"]):
            is_contraindicated = True
            contraindication_reason = "⛔ CONTRAINDICATED / CAUTION: Ibuprofen inhibits renal prostaglandins, reducing renal blood flow and risking acute kidney injury in patients with pre-existing renal impairment."
        if any(w in cond for w in ["pregnant", "pregnancy"]):
            is_contraindicated = True
            contraindication_reason = "⛔ CONTRAINDICATED IN PREGNANCY: NSAIDs must be avoided during pregnancy (especially in the third trimester due to risk of premature ductus arteriosus closure)."

    if med_name == "Paracetamol":
        if any(w in cond for w in ["liver", "hepatic", "hepatitis", "cirrhosis"]):
            warnings.append("⚠️ HEPATIC CAUTION: Paracetamol undergoes hepatic metabolism; dosage must be strictly limited (< 2000 mg/day) or avoided under clinical liver monitoring.")
        if "alcohol" in cond:
            warnings.append("⚠️ ALCOHOL INTERACTION: Regular alcohol intake significantly raises paracetamol hepatotoxicity risks.")

    if med_name == "Amoxicillin":
        if any(w in cond for w in ["kidney", "renal"]):
            warnings.append("⚠️ RENAL ADJUSTMENT: Amoxicillin is cleared renally; dose interval adjustments are required in renal impairment.")

    # 5. Drug-Drug Interactions
    interactions_found = []
    for interaction in detail.get("interactions", []):
        drug_key = interaction.lower().split("(")[0].split("—")[0].split("-")[0].strip()
        if drug_key and len(drug_key) > 3 and drug_key in current_meds_lower:
            interactions_found.append(interaction)
    if interactions_found:
        warnings.append("⚠️ DRUG INTERACTION ALERT: Potential interaction with your current medicine(s): " + " | ".join(interactions_found))

    # Resolve why relevant
    why_relevant = condition_reasons.get(med_name, detail.get("purpose", "Symptomatic management of reported condition."))

    return {
        "name": med_name,
        "detail": detail,
        "why_relevant": why_relevant,
        "is_contraindicated": is_contraindicated,
        "contraindication_reason": contraindication_reason,
        "personalized_warnings": warnings
    }

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL, role TEXT NOT NULL,
            professional_verified INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, event_type TEXT NOT NULL,
            summary TEXT NOT NULL, details TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS patient_profiles (
            user_id INTEGER PRIMARY KEY, age INTEGER, weight REAL,
            allergies TEXT, conditions TEXT, current_medicines TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS pharmacist_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pharmacist_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            patient_age INTEGER,
            patient_weight REAL,
            allergies TEXT,
            conditions TEXT,
            current_medicines TEXT,
            prescribed_medicines TEXT NOT NULL,
            prescriber_name TEXT,
            clinical_notes TEXT,
            safety_alerts TEXT,
            dispensing_status TEXT NOT NULL,
            pharmacist_notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(pharmacist_id) REFERENCES users(id)
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS doctor_prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            prescription_code TEXT UNIQUE NOT NULL,
            patient_name TEXT NOT NULL,
            patient_age INTEGER,
            patient_gender TEXT,
            patient_weight REAL,
            vitals TEXT,
            primary_diagnosis TEXT NOT NULL,
            icd_code TEXT,
            clinical_notes TEXT,
            allergies TEXT,
            chronic_conditions TEXT,
            medicines TEXT NOT NULL,
            safety_review TEXT,
            followup_date TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(doctor_id) REFERENCES users(id)
        )""")
        db.execute("UPDATE users SET professional_verified = 1 WHERE professional_verified = 0")
        db.commit()
        mdb.init_medicine_table(db)

def check_clinical_rx_safety(med_items, age=None, weight=None, allergies="", conditions="", current_meds=""):
    """
    Evaluates prescription safety across:
    1. Drug-Drug Interactions (among prescribed drugs and against current_meds)
    2. Allergy Contraindications
    3. Disease/Organ Contraindications & Cautions
    4. Duplicate Therapy / Class Redundancy
    5. Age & Weight Pediatric/Geriatric Precautions
    """
    alerts = {
        "drug_interactions": [],
        "allergy_contraindications": [],
        "condition_contraindications": [],
        "duplicate_therapy": [],
        "age_weight_cautions": [],
        "monitoring_cautions": []
    }
    
    parsed_drugs = []
    for item in med_items:
        if isinstance(item, dict):
            raw_name = item.get("name", "")
            form = item.get("form", "Tablet")
            strength = item.get("strength", "")
            freq = item.get("frequency", "")
            duration = item.get("duration", "")
            instructions = item.get("instructions", "")
        else:
            raw_name = str(item)
            form, strength, freq, duration, instructions = "Tablet", "", "", "", ""
        
        clean_name = raw_name.strip()
        if not clean_name:
            continue
        parsed_drugs.append({
            "raw": raw_name,
            "name": clean_name,
            "form": form,
            "strength": strength,
            "frequency": freq,
            "duration": duration,
            "instructions": instructions
        })

    if not parsed_drugs:
        return alerts

    allergies_l = (allergies or "").lower()
    conditions_l = (conditions or "").lower()
    current_meds_l = (current_meds or "").lower()

    INTERACTION_RULES = [
        (("ibuprofen", "aspirin"), "High", "Co-administration increases risk of severe gastrointestinal ulceration and gastrointestinal bleeding, while blunting aspirin's cardioprotective antiplatelet effect."),
        (("ibuprofen", "warfarin"), "Severe", "NSAIDs displace warfarin from plasma proteins and inhibit platelets, greatly multiplying haemorrhage risk."),
        (("ibuprofen", "naproxen"), "High", "Concurrent use of two systemic NSAIDs increases toxicity (ulcers, renal injury) with no added therapeutic benefit."),
        (("ibuprofen", "diclofenac"), "High", "Dual NSAID therapy increases risk of severe gastric ulceration and acute kidney injury."),
        (("amoxicillin", "methotrexate"), "High", "Amoxicillin reduces renal clearance of methotrexate, risking severe bone marrow toxicity."),
        (("paracetamol", "alcohol"), "Moderate", "Chronic alcohol intake accelerates CYP2E1 metabolism, producing toxic NAPQI and heightening hepatotoxicity risks."),
        (("cetirizine", "alcohol"), "Moderate", "Additive CNS depression, severe drowsiness, and impaired psychomotor reflexes."),
        (("metformin", "contrast"), "Severe", "Risk of contrast-induced acute kidney injury triggering life-threatening lactic acidosis."),
        (("pantoprazole", "clopidogrel"), "Moderate", "May reduce antiplatelet efficacy of clopidogrel through CYP2C19 competition."),
        (("omeprazole", "clopidogrel"), "Moderate", "Omeprazole inhibits CYP2C19 activation of clopidogrel, lowering its protective cardiac effect."),
        (("atorvastatin", "clarithromycin"), "High", "Strong CYP3A4 inhibition elevates statin blood levels, drastically increasing rhabdomyolysis risk."),
        (("ciprofloxacin", "theophylline"), "High", "Ciprofloxacin inhibits theophylline clearance, risking seizures and arrhythmias."),
    ]

    all_active_names = [d["name"].lower() for d in parsed_drugs]
    combined_drugs_text = " ".join(all_active_names) + " " + current_meds_l

    for (pair, severity, consequence) in INTERACTION_RULES:
        d1, d2 = pair[0], pair[1]
        has_d1 = d1 in combined_drugs_text
        has_d2 = d2 in combined_drugs_text
        if has_d1 and has_d2:
            alerts["drug_interactions"].append({
                "drugs": f"{d1.title()} + {d2.title()}",
                "severity": severity,
                "message": consequence
            })

    ALLERGY_MAP = {
        "amoxicillin": ["penicillin", "amoxicillin", "beta-lactam", "ampicillin"],
        "ibuprofen": ["nsaid", "ibuprofen", "aspirin", "advil", "motrin"],
        "paracetamol": ["paracetamol", "acetaminophen", "tylenol", "crocin", "dolo"],
        "aspirin": ["aspirin", "salicylate", "nsaid"],
        "ciprofloxacin": ["fluoroquinolone", "ciprofloxacin", "quinolone"],
        "azithromycin": ["macrolide", "azithromycin", "erythromycin"],
        "cetirizine": ["cetirizine", "hydroxyzine", "antihistamine"],
        "sulfa": ["sulfa", "sulfamethoxazole", "bactrim"]
    }
    for drug in parsed_drugs:
        d_name_l = drug["name"].lower()
        for med_key, triggers in ALLERGY_MAP.items():
            if med_key in d_name_l:
                for trig in triggers:
                    if trig in allergies_l:
                        alerts["allergy_contraindications"].append({
                            "drug": drug["name"],
                            "allergen": trig.title(),
                            "severity": "CRITICAL / CONTRAINDICATED",
                            "message": f"Patient has documented allergy to '{trig.title()}'. Prescribing {drug['name']} carries imminent risk of anaphylaxis or severe hypersensitivity."
                        })
                        break

    for drug in parsed_drugs:
        d_name_l = drug["name"].lower()
        if any(w in d_name_l for w in ["ibuprofen", "diclofenac", "naproxen"]):
            if "asthma" in conditions_l:
                alerts["condition_contraindications"].append({
                    "drug": drug["name"], "condition": "Asthma", "severity": "High Alert",
                    "message": "NSAIDs can trigger severe acute bronchospasm in aspirin-exacerbated respiratory disease (AERD)."
                })
            if any(w in conditions_l for w in ["ulcer", "gastric", "peptic", "gerd", "bleed"]):
                alerts["condition_contraindications"].append({
                    "drug": drug["name"], "condition": "Peptic Ulcer / GI Bleeding", "severity": "CONTRAINDICATED",
                    "message": "Direct mucosal injury and platelet inhibition; severe risk of gastrointestinal haemorrhage or perforation."
                })
            if any(w in conditions_l for w in ["kidney", "renal", "ckd"]):
                alerts["condition_contraindications"].append({
                    "drug": drug["name"], "condition": "Renal Impairment", "severity": "CONTRAINDICATED",
                    "message": "Inhibits renal vasodilatory prostaglandins, risking acute kidney injury."
                })
            if any(w in conditions_l for w in ["hypertension", "heart failure", "cardiac"]):
                alerts["condition_contraindications"].append({
                    "drug": drug["name"], "condition": "Cardiovascular Disease / Hypertension", "severity": "Caution",
                    "message": "Sodium and fluid retention; may blunt antihypertensives and exacerbate heart failure."
                })
            if any(w in conditions_l for w in ["pregnant", "pregnancy"]):
                alerts["condition_contraindications"].append({
                    "drug": drug["name"], "condition": "Pregnancy (3rd Trimester)", "severity": "CONTRAINDICATED",
                    "message": "Risk of premature closure of fetal ductus arteriosus and pulmonary hypertension."
                })

        if "paracetamol" in d_name_l:
            if any(w in conditions_l for w in ["liver", "hepatic", "cirrhosis", "hepatitis"]):
                alerts["condition_contraindications"].append({
                    "drug": drug["name"], "condition": "Hepatic Impairment", "severity": "Caution / Dose Limit",
                    "message": "Maximum daily dose must be restricted to < 2000mg under clinical monitoring."
                })

        if "amoxicillin" in d_name_l or "ciprofloxacin" in d_name_l:
            if any(w in conditions_l for w in ["kidney", "renal", "ckd"]):
                alerts["condition_contraindications"].append({
                    "drug": drug["name"], "condition": "Renal Impairment", "severity": "Dose Adjustment Required",
                    "message": "Requires dose reduction and extended interval according to estimated GFR."
                })

        if "metformin" in d_name_l:
            if any(w in conditions_l for w in ["kidney", "renal", "ckd"]):
                alerts["condition_contraindications"].append({
                    "drug": drug["name"], "condition": "Renal Impairment (eGFR < 30)", "severity": "CONTRAINDICATED",
                    "message": "High risk of life-threatening metformin-associated lactic acidosis (MALA)."
                })

    CLASS_MAPPINGS = {
        "NSAID": ["ibuprofen", "naproxen", "diclofenac", "aceclofenac", "indomethacin", "celecoxib", "etoricoxib"],
        "Antihistamine": ["cetirizine", "levocetirizine", "fexofenadine", "loratadine", "chlorpheniramine"],
        "Proton Pump Inhibitor": ["pantoprazole", "omeprazole", "rabeprazole", "esomeprazole", "lansoprazole"],
        "Paracetamol Formulation": ["paracetamol", "acetaminophen", "dolo", "crocin", "calpol"],
        "Fluoroquinolone Antibiotic": ["ciprofloxacin", "levofloxacin", "moxifloxacin", "ofloxacin"]
    }
    for class_name, members in CLASS_MAPPINGS.items():
        matched = [d["name"] for d in parsed_drugs if any(m in d["name"].lower() for m in members)]
        if len(matched) > 1:
            alerts["duplicate_therapy"].append({
                "class": class_name,
                "medicines": matched,
                "severity": "DUPLICATE THERAPY ALERT",
                "message": f"Multiple agents from the {class_name} class prescribed simultaneously ({', '.join(matched)}). Review for therapeutic redundancy."
            })

    if age is not None:
        if age < 12:
            alerts["age_weight_cautions"].append({
                "type": "Pediatric Safety",
                "message": f"Pediatric patient (Age {age}): Verify weight-based dosing strictly in mg/kg/dose. Avoid adult tablet formulations without pediatric suspension."
            })
            for drug in parsed_drugs:
                if "aspirin" in drug["name"].lower():
                    alerts["age_weight_cautions"].append({
                        "type": "Pediatric Contraindication",
                        "message": "Aspirin is strictly contraindicated in children/adolescents due to high risk of Reye's syndrome."
                    })
        elif age >= 65:
            alerts["age_weight_cautions"].append({
                "type": "Geriatric Safety (Beers Criteria)",
                "message": f"Geriatric patient (Age {age}): Age-related decline in renal clearance and increased drug sensitivity. Start with lowest therapeutic doses."
            })

    return alerts

def log_history(user_id, event_type, summary, details=None):
    with connect_db() as db:
        db.execute("INSERT INTO history(user_id,event_type,summary,details,created_at) VALUES(?,?,?,?,?)",
                   (user_id, event_type, summary, json.dumps(details or {}, ensure_ascii=False),
                    datetime.now().astimezone().isoformat(timespec="seconds")))
        db.commit()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def role_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Please log in to continue.", "info")
                return redirect(url_for("login"))
            user = current_user()
            if not user:
                session.clear()
                flash("Please log in to continue.", "info")
                return redirect(url_for("login"))
            if user["role"] not in allowed_roles:
                flash(f"Access restricted to {', '.join(allowed_roles)} account.", "error")
                if user["role"] == "doctor":
                    return redirect(url_for("doctor_dashboard"))
                elif user["role"] == "pharmacist":
                    return redirect(url_for("pharmacist_dashboard"))
                else:
                    return redirect(url_for("dashboard"))
            return view(*args, **kwargs)
        return wrapped
    return decorator

def current_user():
    if not session.get("user_id"):
        return None
    with connect_db() as db:
        return db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

@app.context_processor
def inject_user():
    return {"current_user": current_user()}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        role = request.form.get("role","patient")
        if role not in {"patient", "pharmacist", "doctor"}:
            role = "patient"
        if not name or not email or len(password) < 8:
            flash("Enter your name, a valid email, and a password of at least 8 characters.", "error")
            return render_template("register.html")
        verified = 1
        try:
            with connect_db() as db:
                cur = db.execute("INSERT INTO users(name,email,password_hash,role,professional_verified,created_at) VALUES(?,?,?,?,?,?)",
                                 (name,email,generate_password_hash(password),role,verified,
                                  datetime.now().astimezone().isoformat(timespec="seconds")))
                user_id = cur.lastrowid
                db.execute("INSERT OR IGNORE INTO patient_profiles(user_id) VALUES(?)", (user_id,))
                db.commit()
            flash(f"Account created successfully as {role.title()}! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email already has an account. Please log in.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        with connect_db() as db:
            user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['name']}!", "success")
            if user["role"] == "doctor":
                return redirect(url_for("doctor_dashboard"))
            elif user["role"] == "pharmacist":
                return redirect(url_for("pharmacist_dashboard"))
            else:
                return redirect(url_for("dashboard"))
        flash("Email or password was not correct.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    if user["role"] == "doctor":
        return redirect(url_for("doctor_dashboard"))
    elif user["role"] == "pharmacist":
        return redirect(url_for("pharmacist_dashboard"))
    with connect_db() as db:
        profile = db.execute("SELECT * FROM patient_profiles WHERE user_id=?", (user["id"],)).fetchone()
    return render_template("dashboard_patient.html", profile=profile, medicines=MEDICINES)

@app.route("/medicine")
@login_required
def medicine():
    slug = request.args.get("name") or request.args.get("slug") or request.args.get("id")
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    page_str = request.args.get("page", "1").strip()
    try:
        page = max(1, int(page_str))
    except Exception:
        page = 1

    # 1. Monograph View Mode (single medicine)
    if slug:
        med = mdb.get_medicine_by_slug_or_id(slug)
        if not med:
            med = mdb.fetch_and_store_external(slug)
        if med:
            log_history(session["user_id"], "Medicine Monograph View", f"Viewed monograph: {med['name']}",
                        {"name": med["name"], "generic": med["generic_name"], "category": med["category"]})
            return render_template("medicine.html",
                                   mode="monograph",
                                   medicine=med,
                                   query=query,
                                   category=category,
                                   categories=mdb.get_all_categories())
        else:
            flash(f"Clinical record for '{slug}' not found. Please search by generic or brand name.", "info")
            return redirect(url_for("medicine", q=slug))

    # 2. Search & Directory Mode
    search_res = mdb.search_medicines_db(query=query, category=category, page=page, per_page=9)

    # Dynamic openFDA lookup if unlisted medicine query returned 0 matches
    if query and not search_res["found"]:
        external_med = mdb.fetch_and_store_external(query)
        if external_med:
            search_res = mdb.search_medicines_db(query=query, category=category, page=page, per_page=9)
            search_res["is_external"] = True

    if query:
        log_history(session["user_id"], "Medicine Search", f"Search: {query}",
                    {"query": query, "category": category, "total_matches": search_res["total_count"]})

    return render_template("medicine.html",
                           mode="search",
                           results=search_res,
                           query=query,
                           category=category,
                           categories=search_res["categories"])

@app.route("/guidance", methods=["GET", "POST"])
@login_required
def guidance():
    result = None
    if request.method == "POST":
        age_str    = request.form.get("age", "").strip()
        weight_str = request.form.get("weight", "").strip()
        symptoms   = request.form.get("symptoms", "").strip()
        proposed   = request.form.get("medicine", "").strip()
        allergies  = request.form.get("allergies", "").strip()
        conditions = request.form.get("conditions", "").strip()
        current_meds = request.form.get("current_medicines", "").strip()

        try:
            age = int(age_str) if age_str.isdigit() else None
        except Exception:
            age = None
        try:
            weight = float(weight_str) if weight_str else None
        except Exception:
            weight = None

        sym_l  = symptoms.lower()
        all_l  = allergies.lower()
        con_l  = conditions.lower()
        med_l  = current_meds.lower()

        # 1. Emergency detection
        emergency = check_emergency(sym_l + " " + con_l)

        # 2. Identify conditions from symptoms and conditions
        detected_keys = detect_conditions_from_text(sym_l, con_l)
        if not detected_keys and proposed:
            detected_keys = detect_conditions_from_text(proposed.lower(), "")

        # 3. Assemble condition details, medicines, and medicine reasons
        condition_details = []
        all_med_names = set()
        condition_reasons = {}
        for key in detected_keys:
            if key in CONDITION_DATABASE:
                cond_data = dict(CONDITION_DATABASE[key])
                condition_details.append(cond_data)
                for med_name in cond_data.get("medicines", []):
                    all_med_names.add(med_name)
                condition_reasons.update(cond_data.get("medicine_reasons", {}))

        # Also support explicitly proposed medicine if user provided one
        if proposed:
            found_med = next((m["name"] for m in MEDICINES if proposed.lower() in m["name"].lower() or proposed.lower() in m["ingredient"].lower()), None)
            if found_med:
                all_med_names.add(found_med)
                if found_med not in condition_reasons:
                    condition_reasons[found_med] = f"Specifically requested for safety review by patient: {proposed}."
            else:
                all_med_names.add(proposed.title())
                condition_reasons[proposed.title()] = f"Product entered by patient for review: {proposed}. Requires physical label verification by a pharmacist."

        # 4. Allergy analysis
        allergy_info = analyze_allergy_profile(all_l, sym_l, con_l)

        # 5. Medicine safety analysis & options
        medicine_analyses = []
        medicine_options = []
        medicine_categories = set()
        for med_name in sorted(all_med_names):
            analysis = build_medicine_analysis(med_name, condition_reasons, age, weight, con_l, med_l, all_l)
            medicine_analyses.append(analysis)
            cat = analysis["detail"].get("drug_class", "Therapeutic Agent")
            medicine_categories.add(cat)
            medicine_options.append({
                "name": med_name,
                "drug_class": cat,
                "purpose": analysis["detail"].get("purpose", "Symptomatic relief"),
                "why_relevant": analysis["why_relevant"],
                "is_contraindicated": analysis["is_contraindicated"],
                "contraindication_reason": analysis["contraindication_reason"]
            })

        # 6. Aggregate home-care measures (de-duplicated)
        home_care_measures = []
        for cond in condition_details:
            for tip in cond.get("home_care", []):
                if tip not in home_care_measures:
                    home_care_measures.append(tip)
        if not home_care_measures:
            home_care_measures = [
                "Ensure adequate physical rest to support natural immune defenses",
                "Maintain optimal hydration with water, herbal teas, and clear broths",
                "Eat small, easily digestible balanced meals",
                "Monitor vital signs (temperature, pulse, respiratory rate) regularly"
            ]

        # 7. Aggregate prevention measures & doctor consultation triggers
        prevention_measures = []
        when_to_see_doctor = []
        emergency_warning_signs = []
        for cond in condition_details:
            for p in cond.get("prevention", []):
                if p not in prevention_measures:
                    prevention_measures.append(p)
            for w in cond.get("when_to_see_doctor", []):
                if w not in when_to_see_doctor:
                    when_to_see_doctor.append(w)
            for e in cond.get("emergency_signs", []):
                if e not in emergency_warning_signs:
                    emergency_warning_signs.append(e)

        # 8. Aggregate medical references
        references = []
        for cond in condition_details:
            for ref in cond.get("references", []):
                if ref not in references:
                    references.append(ref)
        for med in medicine_analyses:
            for ref in med["detail"].get("references", []):
                if ref not in references:
                    references.append(ref)
        if not references:
            references = ["World Health Organization (WHO) Guidelines", "British National Formulary (BNF)", "NICE Clinical Guidelines"]

        # 9. Personalized Safety Warnings aggregation
        safety_warnings = {
            "age_warning": None,
            "weight_note": None,
            "condition_warnings": [],
            "drug_interaction_warnings": [],
            "emergency_warning_signs": emergency_warning_signs
        }
        if age is not None:
            if age < 12:
                safety_warnings["age_warning"] = f"👶 Paediatric Patient (Age: {age} years): Children require weight-based paediatric formulations (liquid suspensions/syrups). Never administer adult tablets or aspirin to children without a paediatrician's prescription."
            elif age >= 65:
                safety_warnings["age_warning"] = f"👴 Geriatric Patient (Age: {age} years): Older adults have altered drug clearance, increased renal vulnerability, and heightened sensitivity to NSAID gastric ulceration and antihistamine sedation."
        if weight is not None:
            safety_warnings["weight_note"] = f"⚖️ Patient Body Weight ({weight} kg): Clinical dosages for paediatric patients, antibiotics, and intravenous fluids are strictly calculated per kilogram of body weight (mg/kg). Verify exact milligram doses with your dispensing pharmacist."

        for med in medicine_analyses:
            for w in med["personalized_warnings"]:
                if "interaction" in w.lower():
                    if w not in safety_warnings["drug_interaction_warnings"]:
                        safety_warnings["drug_interaction_warnings"].append(f"{med['name']}: {w}")
                else:
                    if w not in safety_warnings["condition_warnings"]:
                        safety_warnings["condition_warnings"].append(f"{med['name']}: {w}")

        result = {
            "emergency": emergency,
            "patient": {
                "age": age, "weight": weight, "allergies": allergies,
                "conditions": conditions, "current_meds": current_meds
            },
            "symptoms": symptoms,
            "proposed": proposed,
            # The 8 Sections:
            "condition_analysis": condition_details,
            "medicine_options": medicine_options,
            "medicine_categories": sorted(list(medicine_categories)),
            "medicine_information": medicine_analyses,
            "allergy_information": allergy_info,
            "natural_and_home_care": home_care_measures,
            "safety_warnings": safety_warnings,
            "prevention": prevention_measures,
            "when_to_see_doctor": when_to_see_doctor,
            "medical_references": references,
            "role": current_user()["role"]
        }

        # Log to user history
        log_history(session["user_id"], "Medicine Guidance Review",
                    f"Symptoms: {symptoms[:80] or 'General review'}",
                    {"age": age_str, "weight": weight_str, "symptoms": symptoms,
                     "allergies": allergies, "conditions": conditions,
                     "current_medicines": current_meds, "proposed": proposed,
                     "detected_conditions": [c["name"] for c in condition_details],
                     "suggested_medicines": [m["name"] for m in medicine_options],
                     "emergency": bool(emergency), "demo_only": True})

        with connect_db() as db:
            db.execute("UPDATE patient_profiles SET age=?,weight=?,allergies=?,conditions=?,current_medicines=? WHERE user_id=?",
                       (int(age_str) if age_str.isdigit() else None,
                        float(weight_str) if weight_str else None,
                        allergies, conditions, current_meds, session["user_id"]))
            db.commit()

    return render_template("guidance.html", result=result)

@app.route("/history")
@login_required
def history():
    user = current_user()
    if user["role"] == "doctor":
        return redirect(url_for("doctor_history"))
    elif user["role"] == "pharmacist":
        return redirect(url_for("pharmacist_history"))
    with connect_db() as db:
        rows = db.execute("SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT 100",
                          (user["id"],)).fetchall()
    return render_template("history.html", rows=rows)

# ═══════════════════════════════════════════════════════════════
# QUALIFIED PHARMACIST MODULE ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route("/pharmacist/dashboard")
@role_required("pharmacist")
def pharmacist_dashboard():
    user = current_user()
    with connect_db() as db:
        recent_reviews = db.execute(
            "SELECT * FROM pharmacist_reviews WHERE pharmacist_id=? ORDER BY id DESC LIMIT 10",
            (user["id"],)
        ).fetchall()
        total_reviews = db.execute(
            "SELECT COUNT(*) as cnt FROM pharmacist_reviews WHERE pharmacist_id=?",
            (user["id"],)
        ).fetchone()["cnt"]
        assessments_count = db.execute(
            "SELECT COUNT(*) as cnt FROM history WHERE user_id=? AND event_type LIKE '%Assessment%'",
            (user["id"],)
        ).fetchone()["cnt"]
        safety_flags_count = db.execute(
            "SELECT COUNT(*) as cnt FROM pharmacist_reviews WHERE pharmacist_id=? AND dispensing_status != 'Approved & Dispensed'",
            (user["id"],)
        ).fetchone()["cnt"]
    return render_template(
        "dashboard_pharmacist.html",
        recent_reviews=recent_reviews,
        total_reviews=total_reviews,
        assessments_count=assessments_count,
        safety_flags_count=safety_flags_count
    )

@app.route("/pharmacist/review", methods=["GET", "POST"])
@role_required("pharmacist")
def pharmacist_review():
    user = current_user()
    safety_report = None
    req_data = {}
    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        patient_age = request.form.get("patient_age", "").strip()
        patient_weight = request.form.get("patient_weight", "").strip()
        prescriber_name = request.form.get("prescriber_name", "").strip()
        clinical_diagnosis = request.form.get("clinical_diagnosis", "").strip()
        prescribed_meds = request.form.get("prescribed_medicines", "").strip()
        allergies = request.form.get("allergies", "").strip()
        conditions = request.form.get("conditions", "").strip()
        current_medicines = request.form.get("current_medicines", "").strip()
        dispensing_status = request.form.get("dispensing_status", "Approved & Dispensed").strip()
        pharmacist_notes = request.form.get("pharmacist_notes", "").strip()

        age_int = int(patient_age) if patient_age.isdigit() else None
        weight_flt = float(patient_weight) if patient_weight else None

        med_lines = [m.strip() for m in re.split(r"[\n,;]+", prescribed_meds) if m.strip()]
        alerts = check_clinical_rx_safety(
            med_lines,
            age=age_int,
            weight=weight_flt,
            allergies=allergies,
            conditions=conditions,
            current_meds=current_medicines
        )

        safety_report = {
            "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "alerts": alerts,
            "prescribed_meds": med_lines
        }
        req_data = request.form

        with connect_db() as db:
            db.execute("""INSERT INTO pharmacist_reviews (
                pharmacist_id, patient_name, patient_age, patient_weight,
                allergies, conditions, current_medicines, prescribed_medicines,
                prescriber_name, clinical_notes, safety_alerts, dispensing_status,
                pharmacist_notes, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                user["id"], patient_name, age_int, weight_flt,
                allergies, conditions, current_medicines, prescribed_meds,
                prescriber_name, clinical_diagnosis, json.dumps(alerts, ensure_ascii=False),
                dispensing_status, pharmacist_notes,
                datetime.now().astimezone().isoformat(timespec="seconds")
            ))
            db.commit()

        log_history(
            user["id"],
            "Prescription Review & Dispensing Check",
            f"Patient: {patient_name} ({patient_age}y) — Dispensing: {dispensing_status}",
            {
                "patient": patient_name,
                "prescriber": prescriber_name,
                "medications": prescribed_meds,
                "dispensing_status": dispensing_status,
                "alerts_found": {k: len(v) for k, v in alerts.items()},
                "notes": pharmacist_notes
            }
        )
        flash("Prescription review validated and logged to dispensary records.", "success")

    return render_template("pharmacist_review.html", safety_report=safety_report, req_data=req_data)

@app.route("/pharmacist/assessment", methods=["GET", "POST"])
@role_required("pharmacist")
def pharmacist_assessment():
    user = current_user()
    result = None
    req_data = {}
    if request.method == "POST":
        req_data = request.form
        age_str = request.form.get("age", "").strip()
        weight_str = request.form.get("weight", "").strip()
        symptoms = request.form.get("symptoms", "").strip()
        proposed = request.form.get("medicine", "").strip()
        allergies = request.form.get("allergies", "").strip()
        conditions = request.form.get("conditions", "").strip()
        current_meds = request.form.get("current_medicines", "").strip()

        age = int(age_str) if age_str.isdigit() else None
        weight = float(weight_str) if weight_str else None
        sym_l = symptoms.lower()
        all_l = allergies.lower()
        con_l = conditions.lower()
        med_l = current_meds.lower()

        emergency = check_emergency(sym_l + " " + con_l)
        detected_keys = detect_conditions_from_text(sym_l, con_l)
        if not detected_keys and proposed:
            detected_keys = detect_conditions_from_text(proposed.lower(), "")

        condition_details = []
        all_med_names = set()
        condition_reasons = {}
        for key in detected_keys:
            if key in CONDITION_DATABASE:
                cond_data = dict(CONDITION_DATABASE[key])
                condition_details.append(cond_data)
                for med_name in cond_data.get("medicines", []):
                    all_med_names.add(med_name)
                condition_reasons.update(cond_data.get("medicine_reasons", {}))

        if proposed:
            found_med = next((m["name"] for m in MEDICINES if proposed.lower() in m["name"].lower() or proposed.lower() in m["ingredient"].lower()), None)
            if found_med:
                all_med_names.add(found_med)
                condition_reasons[found_med] = f"Proposed for OTC evaluation: {proposed}."
            else:
                all_med_names.add(proposed.title())
                condition_reasons[proposed.title()] = f"Requested product: {proposed}."

        allergy_info = analyze_allergy_profile(all_l, sym_l, con_l)

        medicine_analyses = []
        medicine_options = []
        for med_name in sorted(all_med_names):
            analysis = build_medicine_analysis(med_name, condition_reasons, age, weight, con_l, med_l, all_l)
            medicine_analyses.append(analysis)
            medicine_options.append({
                "name": med_name,
                "drug_class": analysis["detail"].get("drug_class", "Therapeutic Agent"),
                "purpose": analysis["detail"].get("purpose", "Symptomatic relief"),
                "why_relevant": analysis["why_relevant"],
                "is_contraindicated": analysis["is_contraindicated"],
                "contraindication_reason": analysis["contraindication_reason"]
            })

        safety_warnings = {
            "allergy_warnings": [],
            "condition_warnings": [],
            "drug_interaction_warnings": []
        }
        for a in allergy_info["allergic_to_user_meds"]:
            safety_warnings["allergy_warnings"].append(a)
        for med in medicine_analyses:
            for w in med["personalized_warnings"]:
                if "interaction" in w.lower():
                    safety_warnings["drug_interaction_warnings"].append(f"{med['name']}: {w}")
                else:
                    safety_warnings["condition_warnings"].append(f"{med['name']}: {w}")

        result = {
            "emergency": emergency,
            "patient": {"age": age, "weight": weight, "allergies": allergies, "conditions": conditions, "current_meds": current_meds},
            "medicine_options": medicine_options,
            "safety_warnings": safety_warnings
        }

        log_history(
            user["id"],
            "Pharmacist Patient Assessment",
            f"Walk-in patient ({age_str}y) symptoms: {symptoms[:60]}",
            {"age": age_str, "weight": weight_str, "symptoms": symptoms, "allergies": allergies, "emergency": bool(emergency)}
        )
        flash("Patient clinical assessment generated and saved to dispensary log.", "success")

    return render_template("pharmacist_assessment.html", result=result, req_data=req_data)

@app.route("/pharmacist/history")
@role_required("pharmacist")
def pharmacist_history():
    user = current_user()
    with connect_db() as db:
        rows = db.execute("SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT 100", (user["id"],)).fetchall()
    return render_template("pharmacist_history.html", rows=rows)

# ═══════════════════════════════════════════════════════════════
# DOCTOR MODULE ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route("/doctor/dashboard")
@role_required("doctor")
def doctor_dashboard():
    user = current_user()
    with connect_db() as db:
        recent_prescriptions = db.execute(
            "SELECT * FROM doctor_prescriptions WHERE doctor_id=? ORDER BY id DESC LIMIT 10",
            (user["id"],)
        ).fetchall()
        total_prescriptions = db.execute(
            "SELECT COUNT(*) as cnt FROM doctor_prescriptions WHERE doctor_id=?",
            (user["id"],)
        ).fetchone()["cnt"]
        consultations_count = db.execute(
            "SELECT COUNT(*) as cnt FROM history WHERE user_id=? AND (event_type LIKE '%Prescription%' OR event_type LIKE '%Consultation%')",
            (user["id"],)
        ).fetchone()["cnt"]
        safety_cleared_count = total_prescriptions
    return render_template(
        "dashboard_doctor.html",
        recent_prescriptions=recent_prescriptions,
        total_prescriptions=total_prescriptions,
        consultations_count=consultations_count,
        safety_cleared_count=safety_cleared_count
    )

@app.route("/doctor/prescribe", methods=["GET", "POST"])
@role_required("doctor")
def doctor_prescribe():
    user = current_user()
    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        patient_age = request.form.get("patient_age", "").strip()
        patient_gender = request.form.get("patient_gender", "Other")
        patient_weight = request.form.get("patient_weight", "").strip()
        vital_bp = request.form.get("vital_bp", "").strip()
        vital_pulse = request.form.get("vital_pulse", "").strip()
        vital_temp = request.form.get("vital_temp", "").strip()
        vital_spo2 = request.form.get("vital_spo2", "").strip()
        primary_diagnosis = request.form.get("primary_diagnosis", "").strip()
        icd_code = request.form.get("icd_code", "").strip()
        clinical_notes = request.form.get("clinical_notes", "").strip()
        allergies = request.form.get("allergies", "").strip()
        conditions = request.form.get("conditions", "").strip()
        lifestyle_advice = request.form.get("lifestyle_advice", "").strip()
        followup_date = request.form.get("followup_date", "").strip()

        med_names = request.form.getlist("med_name[]")
        med_forms = request.form.getlist("med_form[]")
        med_strengths = request.form.getlist("med_strength[]")
        med_freqs = request.form.getlist("med_frequency[]")
        med_durations = request.form.getlist("med_duration[]")
        med_instructions = request.form.getlist("med_instructions[]")

        medicines_list = []
        for i in range(len(med_names)):
            m_name = med_names[i].strip() if i < len(med_names) else ""
            if not m_name:
                continue
            medicines_list.append({
                "name": m_name,
                "form": med_forms[i] if i < len(med_forms) else "Tablet",
                "strength": med_strengths[i] if i < len(med_strengths) else "",
                "frequency": med_freqs[i] if i < len(med_freqs) else "BD",
                "duration": med_durations[i] if i < len(med_durations) else "",
                "instructions": med_instructions[i] if i < len(med_instructions) else "After meals"
            })

        age_int = int(patient_age) if patient_age.isdigit() else None
        weight_flt = float(patient_weight) if patient_weight else None
        vitals_dict = {"bp": vital_bp, "pulse": vital_pulse, "temp": vital_temp, "spo2": vital_spo2}

        alerts = check_clinical_rx_safety(
            medicines_list,
            age=age_int,
            weight=weight_flt,
            allergies=allergies,
            conditions=conditions,
            current_meds=""
        )

        import random
        rx_code = f"RX-{datetime.now().strftime('%Y')}-{random.randint(10000, 99999)}"

        with connect_db() as db:
            cur = db.execute("""INSERT INTO doctor_prescriptions (
                doctor_id, prescription_code, patient_name, patient_age, patient_gender,
                patient_weight, vitals, primary_diagnosis, icd_code, clinical_notes,
                allergies, chronic_conditions, medicines, safety_review, followup_date, created_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                user["id"], rx_code, patient_name, age_int, patient_gender,
                weight_flt, json.dumps(vitals_dict, ensure_ascii=False),
                primary_diagnosis, icd_code, clinical_notes + (" | Advice: " + lifestyle_advice if lifestyle_advice else ""),
                allergies, conditions, json.dumps(medicines_list, ensure_ascii=False),
                json.dumps(alerts, ensure_ascii=False), followup_date,
                datetime.now().astimezone().isoformat(timespec="seconds")
            ))
            rx_id = cur.lastrowid
            db.commit()

        log_history(
            user["id"],
            "Digital Prescription Issued",
            f"Rx {rx_code}: {patient_name} ({patient_age}y) — Diagnosis: {primary_diagnosis}",
            {
                "rx_code": rx_code,
                "patient": patient_name,
                "diagnosis": primary_diagnosis,
                "medications_count": len(medicines_list),
                "followup": followup_date
            }
        )
        flash(f"Prescription {rx_code} generated and validated successfully!", "success")
        return redirect(url_for("doctor_prescription_detail", rx_id=rx_id))

    return render_template("doctor_prescribe.html")

@app.route("/doctor/prescription/<int:rx_id>")
@role_required("doctor", "pharmacist")
def doctor_prescription_detail(rx_id):
    with connect_db() as db:
        rx = db.execute("SELECT * FROM doctor_prescriptions WHERE id=?", (rx_id,)).fetchone()
        if not rx:
            flash("Prescription record not found.", "error")
            return redirect(url_for("doctor_dashboard"))
        doctor = db.execute("SELECT * FROM users WHERE id=?", (rx["doctor_id"],)).fetchone()

    try:
        medicines_list = json.loads(rx["medicines"])
    except Exception:
        medicines_list = []
    try:
        vitals = json.loads(rx["vitals"]) if rx["vitals"] else {}
    except Exception:
        vitals = {}
    try:
        safety_review = json.loads(rx["safety_review"]) if rx["safety_review"] else {}
    except Exception:
        safety_review = {}

    lifestyle_advice = ""
    if rx["clinical_notes"] and " | Advice: " in rx["clinical_notes"]:
        parts = rx["clinical_notes"].split(" | Advice: ")
        lifestyle_advice = parts[1]

    return render_template(
        "doctor_prescription_detail.html",
        rx=rx,
        doctor=doctor,
        medicines_list=medicines_list,
        vitals=vitals,
        safety_review=safety_review,
        lifestyle_advice=lifestyle_advice
    )

@app.route("/doctor/consultations")
@role_required("doctor")
def doctor_consultations():
    user = current_user()
    query = request.args.get("q", "").strip()
    with connect_db() as db:
        if query:
            q_like = f"%{query}%"
            prescriptions = db.execute(
                "SELECT * FROM doctor_prescriptions WHERE doctor_id=? AND (patient_name LIKE ? OR primary_diagnosis LIKE ? OR prescription_code LIKE ?) ORDER BY id DESC",
                (user["id"], q_like, q_like, q_like)
            ).fetchall()
        else:
            prescriptions = db.execute(
                "SELECT * FROM doctor_prescriptions WHERE doctor_id=? ORDER BY id DESC LIMIT 100",
                (user["id"],)
            ).fetchall()
    return render_template("doctor_consultations.html", prescriptions=prescriptions, query=query)

@app.route("/doctor/history")
@role_required("doctor")
def doctor_history():
    user = current_user()
    with connect_db() as db:
        rows = db.execute("SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT 100", (user["id"],)).fetchall()
    return render_template("doctor_history.html", rows=rows)

@app.route("/scan", methods=["POST"])
@login_required
def scan():
    image = request.files.get("medicine_image")
    if not image or not image.filename:
        flash("Choose a medicine-package image first.", "error")
        return redirect(url_for("dashboard"))
    filename = secure_filename(image.filename)
    ext = filename.rsplit(".",1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        flash("Please upload a JPG, PNG, or WEBP package image.", "error")
        return redirect(url_for("dashboard"))
    safe_name = f"user{session['user_id']}_{int(datetime.now().timestamp())}_{filename}"
    image.save(os.path.join(UPLOAD_DIR, safe_name))
    message = "The prototype has received the image but does not yet identify medicines from pictures. No medicine was guessed."
    log_history(session["user_id"], "Package scan", "Medicine package image uploaded",
                {"filename": safe_name, "result": "not identified", "message": message})
    flash(message + " Please use Medicine Information search or ask a qualified professional.", "info")
    return redirect(url_for("dashboard"))

@app.route("/disease", methods=["GET", "POST"])
@login_required
def disease():
    user = current_user()
    result = None
    query = ""
    search_type = request.values.get("search_type", "medicine")

    if request.method == "POST":
        query = (request.form.get("query") or request.form.get("disease") or "").strip()
        search_type = request.form.get("search_type", "medicine")
    else:
        query = (request.args.get("q") or "").strip()
        if request.args.get("type"):
            search_type = request.args.get("type")

    if query:
        if search_type == "disease":
            dis_res = mc.search_disease(query)
            if dis_res["found"]:
                result = {
                    "mode": "disease",
                    "found": True,
                    "query": query,
                    "diseases": dis_res["diseases"],
                    "source": "WHO Guidelines, NICE Clinical Guidelines & British National Formulary (BNF)"
                }
                log_history(user["id"], "Disease lookup", f"Disease: {query}",
                            {"query": query, "matched": [d["name"] for d in dis_res["diseases"]]})
            else:
                result = {
                    "mode": "disease",
                    "found": False,
                    "query": query,
                    "suggestions": dis_res.get("suggestions", []),
                    "message": dis_res.get("message", "Condition not found in catalog. Please check the spelling or consult a doctor.")
                }
                log_history(user["id"], "Disease lookup", f"Not found: {query}", {"query": query, "matched": []})
        else: # medicine mode (default)
            med_res = mc.search_medicine(query, search_external=True)
            if med_res["found"]:
                result = {
                    "mode": "medicine",
                    "found": True,
                    "query": query,
                    "medicines": med_res["medicines"],
                    "source": med_res.get("source", "VAIDYARA Clinical Formulary & DailyMed / FDA Monographs"),
                    "is_external": med_res.get("is_external", False)
                }
                log_history(user["id"], "Medicine lookup", f"Medicine: {query}",
                            {"query": query, "matched": [m["name"] for m in med_res["medicines"]], "external": med_res.get("is_external", False)})
            else:
                result = {
                    "mode": "medicine",
                    "found": False,
                    "query": query,
                    "suggestions": med_res.get("suggestions", []),
                    "message": med_res.get("message", "Medicine information not available. Please verify the medicine name or consult a qualified pharmacist.")
                }
                log_history(user["id"], "Medicine lookup", f"Not found: {query}", {"query": query, "matched": []})

    popular_medicines = [
        "Paracetamol", "Ibuprofen", "Amoxicillin", "Augmentin", "Lipitor (Atorvastatin)",
        "Metformin", "Omeprazole", "Cetirizine (Zyrtec)", "Amlodipine", "Lisinopril",
        "Azithromycin", "Levothyroxine", "Salbutamol (Ventolin)", "Oral Rehydration Salts (ORS)",
        "Dextromethorphan", "Aspirin", "Clopidogrel (Plavix)", "Losartan", "Metoprolol"
    ]
    popular_diseases = [
        "Fever", "Headache", "Hypertension", "Type 2 Diabetes", "High Cholesterol",
        "Asthma", "Acute Cough & Bronchitis", "GERD & Acid Reflux", "Allergic Rhinitis (Hay Fever)",
        "Skin Allergy (Hives)", "Throat Infection", "Urinary Tract Infection", "Gastroenteritis",
        "Hypothyroidism", "Depression & Anxiety"
    ]

    return render_template("disease.html",
                           result=result,
                           query=query,
                           search_type=search_type,
                           popular_medicines=popular_medicines,
                           popular_diseases=popular_diseases)

@app.route("/api/medicine")
@login_required
def api_medicine():
    query = request.args.get("q", "").strip()
    matches = mdb.get_autocomplete(query, limit=12)
    return jsonify(matches)

@app.route("/map")
@login_required
def map_view():
    user = current_user()
    return render_template("map.html", current_user=user)

@app.route("/api/nearby_places")
@login_required
def api_nearby_places():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    radius = request.args.get("radius", 3000)
    category = request.args.get("category", "all")

    if not lat or not lon:
        return jsonify({"success": False, "error": "Missing GPS coordinates (lat, lon)", "places": []}), 400

    try:
        lat_f = float(lat)
        lon_f = float(lon)
        radius_i = int(radius)
    except ValueError:
        return jsonify({"success": False, "error": "Invalid GPS coordinate format", "places": []}), 400

    result = ns.get_nearby_places(lat_f, lon_f, radius=radius_i, category=category)
    
    if session.get("user_id"):
        log_history(session["user_id"], "Nearby Healthcare Map",
                    f"Searched healthcare within {radius_i}m of ({lat_f:.3f}, {lon_f:.3f})",
                    {"lat": lat_f, "lon": lon_f, "radius": radius_i, "places_found": result.get("total_count", 0)})

    return jsonify(result)

@app.errorhandler(413)
def too_large(_):
    flash("Image is too large. Maximum size is 5 MB.", "error")
    return redirect(url_for("dashboard"))

@app.route("/health")
def health():
    return jsonify({"status":"ok", "project":"Vaidyara demo"})

init_db()

if __name__ == "__main__":
    app.run(debug=True)
