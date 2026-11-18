"""
medicine_database.py
Comprehensive Medicine Database and Dynamic Retrieval Module for VAIDYARA.
Provides verified clinical monographs covering all 22 required clinical points,
SQLite persistence in vaidyara.db, separation of Generic vs Brand-name alternatives,
dynamic openFDA integration with local caching, pagination, and autocomplete.
"""
import os
import re
import json
import math
import sqlite3
import difflib
import urllib.request
import urllib.parse
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(__file__), "vaidyara.db")


# Pre-compiled clinical registry with all 22 required clinical fields
BASE_MEDICINES_DATA = [
  {
    "name": "Metformin",
    "brand_names": [
      "Glycomet",
      "Glucophage",
      "Formin",
      "Riomet",
      "Fortamet",
      "Cetapin",
      "Glumetza"
    ],
    "generic_name": "Metformin hydrochloride",
    "active_ingredients": "Metformin hydrochloride",
    "image": "",
    "category": "Endocrine & Metabolic / Antidiabetic",
    "therapeutic_class": "Biguanide Antihyperglycemic Agent",
    "used_for": "First-line oral treatment for glycemic control in Type 2 Diabetes Mellitus; management of polycystic ovary syndrome (PCOS) and gestational diabetes under specialist care.",
    "prescribed_for": [
      "Type 2 Diabetes Mellitus",
      "Prediabetes in High-Risk Individuals",
      "Polycystic Ovary Syndrome (PCOS) Insulin Resistance",
      "Antipsychotic-Induced Weight Gain Mitigation"
    ],
    "how_it_works": "Decreases hepatic gluconeogenesis (glucose output), reduces intestinal absorption of glucose, and improves peripheral insulin sensitivity by activating AMP-activated protein kinase (AMPK) without stimulating pancreatic insulin secretion, thereby carrying minimal intrinsic hypoglycemia risk.",
    "common_side_effects": [
      "Diarrhea and loose stools",
      "Nausea and abdominal cramping",
      "Flatulence and bloating",
      "Metallic taste in mouth",
      "Reduced serum vitamin B12 absorption with prolonged therapy"
    ],
    "serious_side_effects": [
      "Lactic acidosis (FDA Boxed Warning: rare but life-threatening emergency characterized by malaise, myalgia, respiratory distress, somnolence, and hypothermia)",
      "Severe megaloblastic anemia secondary to profound vitamin B12 deficiency"
    ],
    "contraindications": [
      "Severe renal impairment (eGFR < 30 mL/min/1.73 m\u00b2)",
      "Acute or chronic metabolic acidosis, including diabetic ketoacidosis (DKA)",
      "Severe congestive heart failure requiring pharmacological management",
      "Severe hepatic insufficiency or acute alcohol intoxication",
      "Withhold 48 hours before and after iodinated radiocontrast procedures"
    ],
    "drug_interactions": [
      "Iodinated Radiologic Contrast Media: Multiplies risk of acute renal failure and fatal lactic acidosis",
      "Excess Alcohol: Potentiates metformin's effect on lactate metabolism",
      "Cationic Drugs (Cimetidine, Dolutegravir): Compete for renal tubular transport, increasing metformin blood levels",
      "Carbonic Anhydrase Inhibitors (Topiramate, Acetazolamide): Increase lactic acidosis risk"
    ],
    "food_alcohol_interactions": [
      "Always administer with meals to minimize gastrointestinal discomfort and diarrhea",
      "Strictly avoid binge drinking or chronic alcohol abuse, which sharply heightens lactic acidosis risk."
    ],
    "allergy_precautions": "Contraindicated in patients with hypersensitivity to metformin hydrochloride or any product formulation excipients.",
    "age_precautions": {
      "children": "Immediate-release formulation is approved in children >= 10 years of age with Type 2 diabetes. Extended-release formulations are not approved for pediatric patients < 18 years.",
      "older_adults": "Geriatric patients are vulnerable to age-related decline in renal clearance. Baseline and annual eGFR monitoring is mandatory. Avoid initiating if eGFR is 30\u201345 mL/min."
    },
    "pregnancy_breastfeeding": "Category B. Crosses the placenta. Frequently used for gestational diabetes under endocrinologist guidance. Excreted into breast milk in small amounts; generally acceptable with infant monitoring.",
    "kidney_liver_precautions": "Strictly contraindicated if eGFR < 30 mL/min/1.73 m\u00b2. Dose reduction (maximum 1000 mg/day) required if eGFR is 30\u201345 mL/min. Avoid in hepatic impairment due to reduced lactate clearance.",
    "monitoring_requirements": "eGFR and serum creatinine at baseline and at least annually; Glycated Hemoglobin (HbA1c) every 3 months until stable then every 6 months; Serum Vitamin B12 and CBC every 1\u20132 years.",
    "precautions": [
      "FDA Boxed Warning for Lactic Acidosis",
      "Temporarily suspend medication prior to surgery requiring general anesthesia or radiocontrast procedures",
      "Educate patient on early signs of lactic acidosis"
    ],
    "storage": "Store between 20\u00b0C and 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from excessive heat and direct light.",
    "dosage_forms": [
      "Immediate-Release Oral Tablet",
      "Extended-Release (XR/ER) Tablet",
      "Oral Solution"
    ],
    "strengths": [
      "500 mg",
      "850 mg",
      "1000 mg",
      "500 mg XR",
      "750 mg XR",
      "1000 mg XR",
      "500 mg/5 mL solution"
    ],
    "manufacturer": "Bristol-Myers Squibb / Teva / USV / Torrent / Viatris",
    "sources": [
      "FDA Boxed Warning & Prescribing Information",
      "American Diabetes Association (ADA) Standards of Care",
      "DailyMed National Library of Medicine",
      "British National Formulary (BNF)"
    ],
    "last_updated": "2026-08-10",
    "administration": "Take orally with or immediately after meals (e.g., breakfast and dinner) to reduce gastrointestinal side effects such as nausea and diarrhea. Extended-release tablets must be swallowed whole; do not chew, crush, or divide. Drink plenty of fluids throughout the day.",
    "overdose_guidance": "Metformin overdose rarely causes hypoglycemia unless combined with sulfonylureas or insulin, but presents a severe risk of life-threatening Lactic Acidosis. Manifestations include malaise, myalgia, respiratory distress, somnolence, hypothermia, hypotension, and severe metabolic acidosis with an elevated anion gap. Immediate emergency hospitalization is required. Hemodialysis is the treatment of choice to rapidly remove metformin and correct metabolic acidosis.",
    "slug": "metformin"
  },
  {
    "name": "Empagliflozin",
    "brand_names": [
      "Jardiance"
    ],
    "generic_name": "Empagliflozin",
    "active_ingredients": "Empagliflozin",
    "image": "",
    "category": "Endocrine & Cardiovascular / SGLT2 Inhibitor",
    "therapeutic_class": "Sodium-Glucose Cotransporter-2 (SGLT2) Inhibitor",
    "used_for": "Glycemic control in Type 2 Diabetes; reduction of cardiovascular death in adults with T2D and established CVD; reduction of cardiovascular death and hospitalization in Heart Failure (HFrEF/HFpEF); slowing progression of Chronic Kidney Disease (CKD).",
    "prescribed_for": [
      "Type 2 Diabetes Mellitus with High CV Risk",
      "Heart Failure with Reduced or Preserved Ejection Fraction",
      "Chronic Kidney Disease Progression Delay"
    ],
    "how_it_works": "Inhibits SGLT2 in the proximal renal tubules, reducing renal reabsorption of filtered glucose and lowering the renal threshold for glucose, promoting urinary glucose and sodium excretion (glycosuria and natriuresis), reducing intravascular volume and glomerular hyperfiltration.",
    "common_side_effects": [
      "Genital mycotic infections (vulvovaginal candidiasis, balanitis)",
      "Urinary tract infections",
      "Increased urination and mild osmotic diuresis",
      "Thirst and mild volume depletion"
    ],
    "serious_side_effects": [
      "Euglycemic Diabetic Ketoacidosis (euDKA \u2014 ketoacidosis with near-normal blood glucose)",
      "Necrotizing fasciitis of the perineum (Fournier's Gangrene \u2014 surgical emergency)",
      "Urosepsis and acute pyelonephritis",
      "Symptomatic hypotension and acute kidney injury from volume contraction"
    ],
    "contraindications": [
      "Dialysis or end-stage kidney disease (ineffective for glycemic control; however renal/HF protection studied down to eGFR 20 mL/min)",
      "Known serious hypersensitivity to empagliflozin",
      "Type 1 Diabetes Mellitus (high euDKA risk)"
    ],
    "drug_interactions": [
      "Loop and Thiazide Diuretics: Additive volume depletion and hypotension risk",
      "Insulin and Sulfonylureas: Heightened hypoglycemia risk (dose reduction of secretagogues required)",
      "Lithium: Empagliflozin increases urinary lithium clearance, reducing lithium serum levels"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without food once daily in the morning. Avoid excessive alcohol consumption, which substantially elevates ketoacidosis risk."
    ],
    "allergy_precautions": "Contraindicated in patients with angioedema or severe anaphylaxis to SGLT2 inhibitors.",
    "age_precautions": {
      "children": "Approved in pediatric patients >= 10 years of age for Type 2 diabetes control.",
      "older_adults": "Higher incidence of volume depletion, orthostatic hypotension, and renal impairment. Assess fluid status prior to initiation."
    },
    "pregnancy_breastfeeding": "Not recommended during the second and third trimesters of pregnancy due to potential risk to fetal renal development. Discontinue while breastfeeding.",
    "kidney_liver_precautions": "Glycemic efficacy declines when eGFR < 45 mL/min/1.73 m\u00b2. Indicated for HF and CKD down to eGFR 20 mL/min/1.73 m\u00b2. No dose adjustment in mild-to-moderate hepatic impairment.",
    "monitoring_requirements": "Renal function (eGFR, serum creatinine) prior to initiation and periodically; blood pressure and volume status; signs of perineal necrotizing infection.",
    "precautions": [
      "Withhold at least 3 days prior to major surgery to avoid postoperative euglycemic DKA",
      "Instruct patients on genital hygiene and prompt reporting of burning urination"
    ],
    "storage": "Store at 25\u00b0C (77\u00b0F); excursions permitted between 15\u00b0C and 30\u00b0C.",
    "dosage_forms": [
      "Film-Coated Oral Tablet"
    ],
    "strengths": [
      "10 mg",
      "25 mg"
    ],
    "manufacturer": "Boehringer Ingelheim / Eli Lilly",
    "sources": [
      "FDA Prescribing Information",
      "ADA/EASD Consensus Guidelines",
      "KDIGO Clinical Guidelines",
      "DailyMed"
    ],
    "last_updated": "2026-08-14",
    "administration": "Take orally once daily in the morning, with or without food. Swallow tablet whole with water. Maintain adequate daily fluid intake to prevent volume depletion and dehydration.",
    "overdose_guidance": "Overdose causes osmotic diuresis, volume depletion, and dehydration. Evaluate for Euglycemic Diabetic Ketoacidosis (euDKA). Provide IV fluid resuscitation and supportive care. Hemodialysis removal has not been studied.",
    "slug": "empagliflozin"
  },
  {
    "name": "Paracetamol",
    "brand_names": [
      "Dolo 650",
      "Crocin",
      "Calpol",
      "Pacimol",
      "Sumo L",
      "Tylenol",
      "Panadol",
      "Febrex"
    ],
    "generic_name": "Acetaminophen / Paracetamol",
    "active_ingredients": "Paracetamol (N-acetyl-p-aminophenol)",
    "image": "",
    "category": "Analgesic & Antipyretic",
    "therapeutic_class": "Non-opioid Analgesic / Aniline Derivative",
    "used_for": "First-line safe relief of mild to moderate pain (headache, toothache, muscle aches, sore throat) and reduction of fever in infectious illnesses, including dengue, viral fevers, and influenza.",
    "prescribed_for": [
      "Fever (Pyrexia) in Adults and Children",
      "Dengue Fever Symptomatic Care (Safe Choice - Avoids Bleeding)",
      "Tension Headache",
      "Osteoarthritis Pain",
      "Post-vaccination Fever",
      "Mild-to-Moderate Musculoskeletal Pain"
    ],
    "how_it_works": "Inhibits central prostaglandin synthesis in the brain and modulates serotonergic inhibitory pain pathways; acts on the hypothalamic thermoregulatory center to induce peripheral vasodilation and heat dissipation. Lacks peripheral anti-inflammatory action and does not inhibit platelets or damage gastric mucosa.",
    "common_side_effects": [
      "Mild nausea",
      "Stomach upset (infrequent at recommended doses)",
      "Mild pruritus or transient rash in hypersensitive individuals"
    ],
    "serious_side_effects": [
      "Acute hepatic necrosis and fulminant liver failure (in intentional or unintentional overdose due to toxic metabolite NAPQI accumulation)",
      "Severe cutaneous adverse reactions (Stevens-Johnson syndrome, TEN, AGEP)",
      "Renal tubular damage with chronic toxic intake"
    ],
    "contraindications": [
      "Severe active hepatic impairment or severe acute liver failure",
      "Known severe hypersensitivity to paracetamol / acetaminophen"
    ],
    "drug_interactions": [
      "Warfarin: Prolonged daily maximum intake (> 2000 mg/day for > 4 days) can elevate INR and bleeding risk",
      "Isoniazid, Carbamazepine, Phenytoin: Increase CYP2E1 induction and hepatotoxicity risk",
      "Chronic Alcohol Abuse: Induces CYP2E1 and depletes hepatic glutathione, drastically raising liver toxicity threshold"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without food. Avoid chronic or heavy alcohol consumption due to multiplied hepatotoxic risk."
    ],
    "allergy_precautions": "Discontinue at the first appearance of skin rash, mucosal lesions, or any sign of hypersensitivity.",
    "age_precautions": {
      "children": "Safe first-line agent in infants and children. Dosing MUST be calculated by body weight (10\u201315 mg/kg per dose every 4\u20136 hours; maximum 60 mg/kg/day). Never exceed recommended concentrations.",
      "older_adults": "Safe first-line analgesic. Limit maximum daily dose to 2000\u20133000 mg/day in frail elderly or patients weighing under 50 kg."
    },
    "pregnancy_breastfeeding": "Category B. The analgesic and antipyretic of choice in all trimesters of pregnancy at lowest effective dose for shortest duration. Compatible with breastfeeding.",
    "kidney_liver_precautions": "Use with caution in hepatic insufficiency and chronic alcoholism (max 2000 mg/day). In severe renal impairment (eGFR < 10 mL/min), lengthen dosing interval to every 8 hours.",
    "monitoring_requirements": "Liver function tests (ALT/AST) and INR in patients receiving prolonged high-dose therapy or with underlying hepatic disease.",
    "precautions": [
      "Do not exceed 4000 mg/day in adults from all sources combined",
      "Always check OTC combination cough, cold, and flu medicines for hidden acetaminophen to prevent accidental overdose"
    ],
    "storage": "Store below 25\u00b0C (77\u00b0F). Protect from direct light and moisture.",
    "dosage_forms": [
      "Oral Tablet",
      "Dispersible Tablet",
      "Oral Suspension",
      "Infant Drops",
      "Suppository",
      "Intravenous Infusion"
    ],
    "strengths": [
      "500 mg",
      "650 mg",
      "120 mg/5 mL",
      "250 mg/5 mL",
      "1000 mg IV"
    ],
    "manufacturer": "GSK / Johnson & Johnson / Micro Labs / Haleon / Generic manufacturers",
    "sources": [
      "WHO Model List of Essential Medicines",
      "British National Formulary (BNF)",
      "FDA Prescribing Information",
      "DailyMed"
    ],
    "last_updated": "2026-08-10",
    "administration": "Take orally with a full glass of water. Can be taken with or without food; taking with food may reduce gastric irritation if sensitive. Do not exceed 4,000 mg (4 grams) in 24 hours from all prescription and over-the-counter sources combined.",
    "overdose_guidance": "Acute Paracetamol overdose causes severe, potentially fatal hepatic necrosis (centrilobular necrosis). Early symptoms include nausea, vomiting, diaphoresis, and general malaise. If an overdose is suspected, immediately transfer to an emergency medical facility. N-acetylcysteine (NAC) is the specific antidote; it is most effective when administered within 8 hours of ingestion. Serum paracetamol levels should be measured at 4 hours post-ingestion to plot on the Rumack-Matthew nomogram.",
    "slug": "paracetamol"
  },
  {
    "name": "Ibuprofen",
    "brand_names": [
      "Brufen",
      "Combiflam (Ibuprofen)",
      "Advil",
      "Motrin",
      "Ibugesic",
      "Nurofen"
    ],
    "generic_name": "Ibuprofen",
    "active_ingredients": "Ibuprofen",
    "image": "",
    "category": "NSAID (Non-Steroidal Anti-Inflammatory Drug)",
    "therapeutic_class": "Propionic Acid Derivative NSAID",
    "used_for": "Relief of inflammatory pain, dysmenorrhea, dental pain, migraine, osteoarthritis, rheumatoid arthritis, and fever. STRICTLY AVOID IN DENGUE FEVER due to hemorrhage risk.",
    "prescribed_for": [
      "Osteoarthritis and Rheumatoid Arthritis",
      "Headache and Migraine",
      "Dysmenorrhea (Menstrual Cramps)",
      "Musculoskeletal and Soft Tissue Injury",
      "Dental Pain",
      "Fever (Non-Dengue)"
    ],
    "how_it_works": "Reversibly and non-selectively inhibits cyclooxygenase-1 (COX-1) and cyclooxygenase-2 (COX-2) enzymes, preventing the conversion of arachidonic acid to prostaglandins and thromboxanes, eliminating inflammatory swelling, peripheral pain sensitization, and hypothalamic fever response.",
    "common_side_effects": [
      "Epigastric burning and dyspepsia",
      "Heartburn and nausea",
      "Mild dizziness and headache",
      "Fluid retention and peripheral edema"
    ],
    "serious_side_effects": [
      "Gastrointestinal ulceration, massive bleeding, and stomach perforation (FDA Boxed Warning)",
      "Major cardiovascular thrombotic events, myocardial infarction, and stroke (FDA Boxed Warning)",
      "Acute kidney injury and interstitial nephritis",
      "Aspirin-Exacerbated Respiratory Disease (severe bronchospasm in asthmatics)"
    ],
    "contraindications": [
      "Active peptic ulcer disease or history of GI bleeding",
      "CRITICAL: Dengue Fever and suspected hemorrhagic fevers (causes severe platelet dysfunction and fatal hemorrhage)",
      "Aspirin-induced asthma or triad (nasal polyps, asthma, NSAID allergy)",
      "Third trimester of pregnancy (causes premature ductus arteriosus closure)",
      "Severe heart failure or severe renal failure"
    ],
    "drug_interactions": [
      "Anticoagulants (Warfarin, Apixaban) and Antiplatelets (Aspirin, Clopidogrel): Dramatically multiplies catastrophic GI bleeding risk",
      "ACE Inhibitors & ARBs: Blunts antihypertensive effect and precipitates acute kidney injury (the 'Triple Whammy' with diuretics)",
      "Lithium and Methotrexate: Impairs renal clearance leading to severe toxicity"
    ],
    "food_alcohol_interactions": [
      "Always ingest with meals or a full glass of milk to buffer gastric mucosal irritation. Concurrent alcohol sharply increases gastric ulceration and bleeding risk."
    ],
    "allergy_precautions": "Contraindicated in individuals who have experienced asthma, urticaria, or allergic-type reactions after taking aspirin or other NSAIDs.",
    "age_precautions": {
      "children": "Approved in children >= 6 months for fever and pain (5\u201310 mg/kg every 6\u20138 hours). Never administer to dehydrated children due to acute tubular necrosis risk.",
      "older_adults": "Beers Criteria warning: High risk of silent GI bleeding, worsening hypertension, heart failure exacerbation, and acute renal decline. Avoid chronic use."
    },
    "pregnancy_breastfeeding": "Contraindicated in the third trimester of pregnancy (FDA Category D: oligohydramnios and premature ductus arteriosus closure). Compatible in low doses during breastfeeding.",
    "kidney_liver_precautions": "Contraindicated in severe renal failure. NSAIDs inhibit protective renal vasodilating prostaglandins (PGE2, PGI2), compromising renal perfusion. Use caution in hepatic impairment.",
    "monitoring_requirements": "Blood pressure; CBC and hemoglobin (for occult blood loss); BUN and serum creatinine in chronic therapy.",
    "precautions": [
      "FDA Boxed Warnings for GI Bleeding and Cardiovascular Risk",
      "Use lowest effective dose for shortest possible duration",
      "Strictly prohibited in suspected Dengue"
    ],
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from excessive heat and direct light.",
    "dosage_forms": [
      "Oral Tablet",
      "Softgel Capsule",
      "Oral Suspension",
      "Topical Gel"
    ],
    "strengths": [
      "200 mg",
      "400 mg",
      "600 mg",
      "800 mg",
      "100 mg/5 mL suspension"
    ],
    "manufacturer": "Pfizer / Haleon / Abbott / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning & Prescribing Information",
      "British National Formulary (BNF)",
      "NICE Clinical Guidelines",
      "DailyMed"
    ],
    "last_updated": "2026-07-22",
    "administration": "Take orally with food or milk to minimize stomach upset. Swallow tablets or capsules with a full glass of water. Do not lie down for 15 to 30 minutes after taking. Use the lowest effective dose for the shortest duration.",
    "overdose_guidance": "Symptoms include nausea, vomiting, epigastric pain, lethargy, drowsiness, nystagmus, metabolic acidosis, acute renal failure, and rarely coma or respiratory depression. Administer activated charcoal if presentation is within 1 hour of ingestion. Provide IV fluids and symptomatic care. Hemodialysis does not remove ibuprofen.",
    "slug": "ibuprofen"
  },
  {
    "name": "Artemether and Lumefantrine",
    "brand_names": [
      "Coartem",
      "Riamet",
      "Falcinil-LF",
      "Lumartem"
    ],
    "generic_name": "Artemether and lumefantrine",
    "active_ingredients": "Artemether (20 mg) + Lumefantrine (120 mg)",
    "image": "",
    "category": "Infectious & Tropical / Antimalarial",
    "therapeutic_class": "Artemisinin-Based Combination Therapy (ACT)",
    "used_for": "First-line oral treatment of acute, uncomplicated malaria infections caused by Plasmodium falciparum or mixed malarial infections in adults and pediatric patients.",
    "prescribed_for": [
      "Uncomplicated Plasmodium falciparum Malaria",
      "Chloroquine-Resistant P. vivax Malaria (Where Endorsed by WHO)",
      "Mixed Plasmodial Infections"
    ],
    "how_it_works": "Dual-action antimalarial: Artemether is rapidly metabolized to dihydroartemisinin (DHA), generating free radical endoperoxides that rapidly destroy malarial parasite biomass within hours; Lumefantrine has a prolonged half-life, preventing nucleic acid and protein synthesis to eradicate any residual parasites and prevent recrudescence.",
    "common_side_effects": [
      "Headache and dizziness",
      "Anorexia and nausea",
      "Abdominal pain and vomiting",
      "Asthenia and fatigue",
      "Arthralgia and myalgia",
      "Sleep disturbances"
    ],
    "serious_side_effects": [
      "Cardiac QTc interval prolongation (arrhythmia risk)",
      "Severe hypersensitivity and urticaria",
      "Hemolytic anemia (rare post-artemisinin delayed hemolysis)"
    ],
    "contraindications": [
      "Known hypersensitivity to artemether, lumefantrine, or artemisinin derivatives",
      "Severe / complicated cerebral malaria requiring intravenous artesunate",
      "Congenital long QT syndrome or concurrent administration of QT-prolonging drugs",
      "First trimester of pregnancy (unless no alternative is available, per WHO guidelines)"
    ],
    "drug_interactions": [
      "QT-Prolonging Medications (Haloperidol, Erythromycin, Moxifloxacin, Amiodarone): Multiplies dangerous ventricular arrhythmia risk",
      "Strong CYP3A4 Inducers (Rifampin, Carbamazepine, St. John's Wort): Drastically reduces artemether and lumefantrine levels, leading to treatment failure",
      "Strong CYP3A4 Inhibitors (Ketoconazole): Elevates lumefantrine exposure and cardiac toxicity"
    ],
    "food_alcohol_interactions": [
      "CRITICAL INSTRUCTION: Must be taken with high-fat food or full-cream milk. Lumefantrine bioavailability increases up to 16-fold in the presence of dietary lipids."
    ],
    "allergy_precautions": "Discontinue immediately and provide emergency support if angioedema, bronchospasm, or anaphylaxis occurs.",
    "age_precautions": {
      "children": "Approved in infants and children weighing >= 5 kg. Dosing follows a strict 6-dose regimen over 3 days based entirely on body weight bands.",
      "older_adults": "Monitor baseline ECG and electrolytes due to higher vulnerability to drug-induced cardiac conduction abnormalities."
    },
    "pregnancy_breastfeeding": "WHO recommends artemether-lumefantrine as treatment of choice for uncomplicated falciparum malaria during the second and third trimesters of pregnancy. In the first trimester, use if other antimalarials are unavailable. Excreted in breast milk; safe under clinical supervision.",
    "kidney_liver_precautions": "No dose adjustment required in mild-to-moderate renal or hepatic impairment. Exercise caution in severe hepatic dysfunction.",
    "monitoring_requirements": "Baseline and follow-up microscopic blood smears (thick and thin films) for parasite clearance; ECG monitoring in high-risk patients; serum potassium and magnesium.",
    "precautions": [
      "Must complete the entire 6-dose course over 3 days even if fever clears",
      "If patient vomits within 1 hour of ingestion, repeat the full dose"
    ],
    "storage": "Store below 30\u00b0C (86\u00b0F). Protect from moisture and heat.",
    "dosage_forms": [
      "Oral Tablet",
      "Dispersible Tablet for Paediatric Use"
    ],
    "strengths": [
      "20 mg Artemether / 120 mg Lumefantrine",
      "80 mg / 480 mg Forte Tablet"
    ],
    "manufacturer": "Novartis / Cipla / Ajanta Pharma / Generic manufacturers",
    "sources": [
      "WHO Guidelines for Malaria",
      "FDA Prescribing Information",
      "CDC Yellow Book Malaria Guidance",
      "DailyMed"
    ],
    "last_updated": "2026-08-01",
    "administration": "Take orally with high-fat food or drinks (e.g., whole milk) to ensure adequate systemic bioavailability of lumefantrine. Complete the full 6-dose regimen over 3 days exactly as scheduled to prevent recrudescence.",
    "overdose_guidance": "Overdose increases risk of cardiac QT prolongation and neurotoxicity. ECG monitoring and supportive care are indicated. Hemodialysis is not effective.",
    "slug": "artemether_and_lumefantrine"
  },
  {
    "name": "Levetiracetam",
    "brand_names": [
      "Keppra",
      "Levroxa",
      "Elepsia XR",
      "Spritam"
    ],
    "generic_name": "Levetiracetam",
    "active_ingredients": "Levetiracetam",
    "image": "",
    "category": "Neurological / Anticonvulsant",
    "therapeutic_class": "Synaptic Vesicle Protein 2A (SV2A) Ligand",
    "used_for": "Monotherapy and adjunctive treatment of focal (partial onset) seizures, generalized tonic-clonic seizures, and myoclonic seizures in patients with epilepsy.",
    "prescribed_for": [
      "Focal Onset Seizures with or without Secondary Generalization",
      "Primary Generalized Tonic-Clonic Seizures (PGTCS)",
      "Juvenile Myoclonic Epilepsy (JME)",
      "Status Epilepticus (Second-Line IV Rescue)",
      "Post-Traumatic Brain Injury Seizure Prophylaxis"
    ],
    "how_it_works": "Selectively binds to synaptic vesicle protein 2A (SV2A) in presynaptic nerve terminals, inhibiting presynaptic vesicle exocytosis and modulating neurotransmitter release, thereby suppressing abnormal epileptiform burst firing without significantly affecting normal neuronal excitability.",
    "common_side_effects": [
      "Somnolence and fatigue",
      "Dizziness and ataxia",
      "Nasopharyngitis and upper respiratory symptoms",
      "Headache",
      "Irritability and emotional lability"
    ],
    "serious_side_effects": [
      "Neuropsychiatric symptoms (depression, agitation, psychosis, suicidal ideation)",
      "Severe cutaneous adverse reactions (SJS / TEN)",
      "Anaphylaxis and angioedema",
      "Agranulocytosis or neutropenia (rare)"
    ],
    "contraindications": [
      "Hypersensitivity to levetiracetam, pyrrolidone derivatives, or formulation excipients"
    ],
    "drug_interactions": [
      "Minimal CYP450 interactions: Does not induce or inhibit hepatic enzymes, making it exceptionally safe in combination antiepileptic therapy",
      "Methotrexate: Concurrent use may reduce renal methotrexate clearance, raising methotrexate toxicity",
      "CNS Depressants and Alcohol: Additive psychomotor impairment and sedation"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without food. Avoid alcohol, which amplifies somnolence, cognitive slowing, and can provoke breakthrough seizures."
    ],
    "allergy_precautions": "Discontinue if unexplained rash or systemic signs of hypersensitivity appear.",
    "age_precautions": {
      "children": "Approved in infants as young as 1 month of age for focal seizures. Paediatric oral solution allows precise weight-based titration (mg/kg).",
      "older_adults": "Dose adjustment required based on age-related decline in creatinine clearance. Vulnerable to somnolence and unsteadiness (fall risk)."
    },
    "pregnancy_breastfeeding": "Pregnancy Category C. Preferred first-line antiepileptic during pregnancy due to lowest major congenital malformation rates in international pregnancy registries (EURAP). Serum levels decline markedly during third trimester; therapeutic drug monitoring required. Compatible with breastfeeding.",
    "kidney_liver_precautions": "Eliminated primarily via renal excretion (~66% unchanged). Mandatory dosage reduction in renal impairment: eGFR 50\u201379 mL/min (500\u20131000 mg q12h); eGFR 30\u201349 mL/min (250\u2013750 mg q12h); eGFR < 30 mL/min (250\u2013500 mg q12h).",
    "monitoring_requirements": "Renal function (BUN/creatinine); screening for emergent behavioral/mood changes and suicidal ideation at every clinical visit.",
    "precautions": [
      "FDA Warning for Suicidal Behavior and Ideation",
      "NEVER abruptly discontinue antiepileptic therapy; sudden cessation triggers rebound status epilepticus (taper gradually)",
      "Warn patient regarding driving restrictions until seizure-free"
    ],
    "storage": "Store at 25\u00b0C (77\u00b0F). Protect from light and moisture.",
    "dosage_forms": [
      "Immediate-Release Oral Tablet",
      "Extended-Release (XR) Tablet",
      "Oral Solution (100 mg/mL)",
      "Intravenous Solution"
    ],
    "strengths": [
      "250 mg",
      "500 mg",
      "750 mg",
      "1000 mg",
      "500 mg XR",
      "750 mg XR",
      "100 mg/mL solution"
    ],
    "manufacturer": "UCB Pharma / Sun Pharma / Lupin / Generic manufacturers",
    "sources": [
      "FDA Prescribing Information",
      "American Epilepsy Society (AES) Guidelines",
      "NICE Guideline NG217",
      "DailyMed"
    ],
    "last_updated": "2026-08-16",
    "administration": "Take orally twice daily in two equally divided doses, approximately 12 hours apart, with or without food. Swallow tablets whole with water; do not chew or crush. Do not stop abruptly; taper slowly to avoid withdrawal seizures.",
    "overdose_guidance": "Manifestations include somnolence, agitation, aggression, respiratory depression, and coma. Provide supportive airway and cardiovascular management. Hemodialysis effectively removes approximately 50% of systemic levetiracetam in 4 hours.",
    "slug": "levetiracetam"
  },
  {
    "name": "Sodium Valproate",
    "brand_names": [
      "Depakote",
      "Epilim",
      "Depakene",
      "Encorate",
      "Valparin"
    ],
    "generic_name": "Divalproex sodium / Sodium valproate",
    "active_ingredients": "Sodium valproate / Valproic acid",
    "image": "",
    "category": "Neurological & Psychiatric / Anticonvulsant",
    "therapeutic_class": "Broad-Spectrum Antiepileptic & Mood Stabilizer",
    "used_for": "Broad-spectrum control of generalized, focal, absence, and myoclonic seizures; acute manic episodes of Bipolar Disorder; prophylaxis of migraine headaches.",
    "prescribed_for": [
      "Generalized Tonic-Clonic Seizures",
      "Absence Seizures (Petit Mal)",
      "Myoclonic Seizures in Juvenile Myoclonic Epilepsy",
      "Focal Seizures",
      "Bipolar I Acute Mania",
      "Migraine Headache Prophylaxis"
    ],
    "how_it_works": "Multi-mechanistic action: Blocks voltage-gated sodium channels, inhibits T-type calcium channels, and enhances inhibitory GABAergic neurotransmission by inhibiting GABA transaminase and stimulating glutamate decarboxylase.",
    "common_side_effects": [
      "Tremor (postural hand tremor)",
      "Weight gain and increased appetite",
      "Alopecia (hair thinning)",
      "Nausea and dyspepsia",
      "Menstrual irregularities and polycystic ovarian changes"
    ],
    "serious_side_effects": [
      "Fatal hepatotoxicity (FDA Boxed Warning: peak risk in children under 2 years)",
      "Pancreatitis (FDA Boxed Warning: severe, hemorrhagic, life-threatening)",
      "Severe teratogenicity (FDA Boxed Warning: neural tube defects, lower IQ scores in offspring)",
      "Hyperammonemic encephalopathy (with or without abnormal liver enzymes)",
      "Thrombocytopenia and coagulopathy"
    ],
    "contraindications": [
      "Pregnancy for migraine prevention, and pregnancy for epilepsy unless no suitable alternative exists (Pregnancy Prevention Programme mandatory)",
      "Active hepatic disease or significant hepatic impairment",
      "Known mitochondrial disorders caused by mutations in mitochondrial DNA polymerase-gamma (POLG)",
      "Known urea cycle disorders (hyperammonemic coma risk)"
    ],
    "drug_interactions": [
      "Carbapenem Antibiotics (Meropenem, Imipenem): CRITICAL CONTRAINDICATION \u2014 carbapenems plummet valproate blood levels by 80% within 24 hours, triggering status epilepticus",
      "Lamotrigine: Valproate inhibits lamotrigine glucuronidation, doubling lamotrigine half-life and multiplying toxic epidermal necrolysis (TEN) risk",
      "Aspirin: Displaces valproate from albumin and impairs metabolism, elevating free active valproate levels"
    ],
    "food_alcohol_interactions": [
      "Take with food to minimize gastric irritation. Do not crush enteric-coated tablets. Strictly avoid alcohol."
    ],
    "allergy_precautions": "Immediate discontinuation required if DRESS syndrome (fever, rash, lymphadenopathy, multiorgan involvement) develops.",
    "age_precautions": {
      "children": "FDA Boxed Warning: Children under 2 years of age have a dramatically elevated risk of fatal hepatotoxicity. Use with extreme caution as sole agent.",
      "older_adults": "Higher unbound free valproate fraction due to decreased albumin. Lower starting doses and slow titration required."
    },
    "pregnancy_breastfeeding": "FDA Boxed Warning: High rate of major congenital malformations (neural tube defects / spina bifida in 1\u20132%) and 8\u201310 point reduction in childhood IQ scores. Strictly avoided in women of childbearing potential unless adhering to pregnancy prevention programme (Pledge/Prevent). Excreted in breast milk in small amounts.",
    "kidney_liver_precautions": "Strictly contraindicated in hepatic disease. No dosage adjustments required for renal impairment, but free unbound drug fraction is increased.",
    "monitoring_requirements": "Baseline and periodic Liver Function Tests (LFTs); Complete Blood Count with Platelets; Serum Valproate therapeutic level (trough target: 50\u2013100 mcg/mL); Serum ammonia in patients presenting with lethargy or confusion.",
    "precautions": [
      "FDA Boxed Warnings for Hepatotoxicity, Pancreatitis, and Teratogenicity",
      "Instruct patient to seek urgent care for abdominal pain (pancreatitis) or jaundice (liver injury)",
      "Never discontinue abruptly"
    ],
    "storage": "Store at 25\u00b0C (77\u00b0F). Keep containers tightly closed.",
    "dosage_forms": [
      "Enteric-Coated Tablet",
      "Extended-Release (ER) Tablet",
      "Oral Solution",
      "Delayed-Release Sprinkle Capsule",
      "IV Infusion"
    ],
    "strengths": [
      "125 mg",
      "250 mg",
      "500 mg",
      "250 mg ER",
      "500 mg ER",
      "250 mg/5 mL syrup"
    ],
    "manufacturer": "AbbVie / Sanofi / Torrent / Sun Pharma",
    "sources": [
      "FDA Boxed Warnings and Prescribing Information",
      "NICE Epilepsy Guidelines",
      "DailyMed",
      "BNF"
    ],
    "last_updated": "2026-08-12",
    "administration": "Take orally with or after food to minimize gastrointestinal irritation. Swallow enteric-coated tablets whole; do not break or crush. Maintain consistent timing every day.",
    "overdose_guidance": "Overdose causes somnolence, heart block, deep coma, severe hyperammonemia, and metabolic acidosis with respiratory depression. Naloxone can reverse CNS depression in some cases. L-carnitine IV is the specific antidote for valproate-induced hyperammonemic encephalopathy and hepatotoxicity. Hemodialysis is effective.",
    "slug": "sodium_valproate"
  },
  {
    "name": "Amlodipine",
    "brand_names": [
      "Amlong",
      "Stamlo",
      "Norvasc",
      "Amlovas",
      "Amlopin"
    ],
    "generic_name": "Amlodipine besylate",
    "active_ingredients": "Amlodipine besylate",
    "image": "",
    "category": "Cardiovascular / Antihypertensive",
    "therapeutic_class": "Dihydropyridine Calcium Channel Blocker (CCB)",
    "used_for": "First-line management of essential hypertension; chronic stable angina pectoris; vasospastic (Prinzmetal's) angina.",
    "prescribed_for": [
      "Essential Hypertension in Adults and Children",
      "Chronic Stable Angina",
      "Vasospastic (Prinzmetal's) Angina",
      "Coronary Artery Disease Plaque Stabilization"
    ],
    "how_it_works": "Selectively inhibits transmembrane influx of extracellular calcium ions into vascular smooth muscle cells and myocardial cells, causing systemic peripheral arterial vasodilation, reducing total peripheral resistance, systemic blood pressure, and cardiac afterload without depressing cardiac nodal conduction.",
    "common_side_effects": [
      "Peripheral dependent ankle edema (fluid accumulation in lower extremities)",
      "Flushing and warm sensation",
      "Dizziness and lightheadedness",
      "Headache",
      "Fatigue",
      "Palpitations"
    ],
    "serious_side_effects": [
      "Severe symptomatic hypotension / syncope",
      "Worsening angina or acute myocardial infarction upon initiation or dose escalation in severe obstructive CAD",
      "Gingival hyperplasia"
    ],
    "contraindications": [
      "Severe hypotension (systolic BP < 90 mmHg)",
      "Cardiogenic shock or severe aortic stenosis",
      "Known hypersensitivity to dihydropyridine calcium channel blockers"
    ],
    "drug_interactions": [
      "Simvastatin: Amlodipine increases simvastatin exposure; limit simvastatin dose to a maximum of 20 mg/day to avoid rhabdomyolysis",
      "CYP3A4 Inhibitors (Ketoconazole, Itraconazole, Diltiazem): Elevate amlodipine plasma levels",
      "Cyclosporine / Tacrolimus: Amlodipine increases calcineurin inhibitor blood concentrations"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without food. Avoid excessive grapefruit juice, which can inhibit CYP3A4 and increase drug levels. Alcohol potentiates hypotensive effects."
    ],
    "allergy_precautions": "Contraindicated in patients with severe dihydropyridine allergy.",
    "age_precautions": {
      "children": "Approved in pediatric patients 6\u201317 years of age for hypertension (starting dose 2.5 mg once daily).",
      "older_adults": "Clearance is decreased in elderly individuals; start at lower dose (2.5 mg once daily) to avoid severe orthostatic hypotension."
    },
    "pregnancy_breastfeeding": "Category C. Limited human data; other antihypertensive agents (labetalol, nifedipine, methyldopa) are preferred in pregnancy. Excreted into human milk in small amounts.",
    "kidney_liver_precautions": "Safe in renal impairment without dose adjustment. Extensively metabolized by the liver; initial dose should be reduced to 2.5 mg daily in severe hepatic impairment.",
    "monitoring_requirements": "Blood pressure and heart rate; inspection for lower extremity peripheral edema.",
    "precautions": [
      "Advise patient regarding benign ankle edema which responds poorly to diuretics but improves with leg elevation or ARB co-prescription",
      "Do not stop taking suddenly"
    ],
    "storage": "Store between 15\u00b0C and 30\u00b0C (59\u00b0F and 86\u00b0F). Protect from light.",
    "dosage_forms": [
      "Oral Tablet"
    ],
    "strengths": [
      "2.5 mg",
      "5 mg",
      "10 mg"
    ],
    "manufacturer": "Pfizer / Viatris / Sun Pharma / Generic manufacturers",
    "sources": [
      "FDA Prescribing Information",
      "AHA/ACC Hypertension Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-11",
    "administration": "Take orally once daily with or without food, at the same time every day. Swallow tablet whole with water. Can be taken in the morning or evening as advised by physician.",
    "overdose_guidance": "Overdose produces pronounced peripheral vasodilation with marked and prolonged hypotension, reflex tachycardia, and potential cardiogenic shock and non-cardiogenic pulmonary edema. Emergency hospitalization with continuous cardiac monitoring is mandatory. Provide active cardiovascular support: IV fluid resuscitation, calcium gluconate IV, vasopressors (norepinephrine, dopamine), and high-dose insulin euglycemic therapy (HIET). Amlodipine is not dialyzable.",
    "slug": "amlodipine"
  },
  {
    "name": "Lisinopril",
    "brand_names": [
      "Zestril",
      "Prinivil",
      "Lipril",
      "Listril"
    ],
    "generic_name": "Lisinopril",
    "active_ingredients": "Lisinopril dihydrate",
    "image": "",
    "category": "Cardiovascular / Antihypertensive",
    "therapeutic_class": "Angiotensin-Converting Enzyme (ACE) Inhibitor",
    "used_for": "Treatment of hypertension; adjunctive therapy in systolic heart failure (HFrEF); reduction of mortality within 24 hours of acute myocardial infarction; slowing progression of diabetic nephropathy.",
    "prescribed_for": [
      "Essential Hypertension",
      "Heart Failure with Reduced Ejection Fraction (HFrEF)",
      "Post-Myocardial Infarction Survival Improvement",
      "Diabetic Nephropathy / Proteinuria Reduction"
    ],
    "how_it_works": "Competitively inhibits angiotensin-converting enzyme (ACE), preventing the conversion of angiotensin I to the potent vasoconstrictor angiotensin II, decreasing systemic vascular resistance, reducing aldosterone secretion, promoting natriuresis, and blunting sympathetic activation; concurrently suppresses bradykinin degradation.",
    "common_side_effects": [
      "Persistent dry, hacking, non-productive cough (bradykinin-mediated)",
      "Dizziness and lightheadedness",
      "Headache",
      "Fatigue",
      "Diarrhea"
    ],
    "serious_side_effects": [
      "Life-threatening Angioedema (FDA Boxed Warning: swelling of lips, tongue, pharynx, larynx causing acute asphyxiation)",
      "Fetal toxicity and fetal demise (FDA Boxed Warning: strictly contraindicated in pregnancy)",
      "Hyperkalemia (elevated serum potassium)",
      "Acute renal failure in bilateral renal artery stenosis"
    ],
    "contraindications": [
      "Pregnancy (FDA Boxed Warning: causes severe oligohydramnios, skull hypoplasia, and fetal death)",
      "History of ACE inhibitor-induced angioedema or hereditary angioedema",
      "Concomitant use of Sacubitril/Valsartan (Entresto) within 36 hours (massive angioedema risk)",
      "Concomitant aliskiren in patients with diabetes mellitus"
    ],
    "drug_interactions": [
      "Potassium Supplements & Potassium-Sparing Diuretics (Spironolactone, Amiloride): Severe, fatal hyperkalemia risk",
      "NSAIDs (Ibuprofen, Naproxen): Antagonize antihypertensive response and accelerate acute renal failure",
      "Lithium: Lisinopril reduces renal lithium excretion, causing severe lithium toxicity",
      "Sacubitril: Requires 36-hour washout period to prevent fatal angioedema"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without food. Avoid potassium-containing salt substitutes (potassium chloride) to prevent dangerous hyperkalemia. Alcohol compounds hypotension."
    ],
    "allergy_precautions": "Immediate permanent discontinuation required if facial or laryngeal swelling occurs. Black patients have a 4- to 5-fold higher risk of angioedema.",
    "age_precautions": {
      "children": "Approved in pediatric patients >= 6 years of age for hypertension.",
      "older_adults": "Start at low doses (2.5\u20135 mg daily). High susceptibility to orthostatic hypotension and hyperkalemia."
    },
    "pregnancy_breastfeeding": "FDA Boxed Warning: Pregnancy Category D. Must be discontinued immediately when pregnancy is detected. Not recommended during breastfeeding.",
    "kidney_liver_precautions": "Excreted entirely unchanged by the kidneys. Initial dose must be reduced in renal impairment (eGFR 10\u201330 mL/min: start 5 mg/day; eGFR < 10 mL/min: start 2.5 mg/day). Not metabolized by the liver.",
    "monitoring_requirements": "Serum potassium, serum creatinine, and BUN at baseline, 1\u20132 weeks post-initiation/dose titration, and every 6\u201312 months; blood pressure.",
    "precautions": [
      "FDA Boxed Warning for Fetal Toxicity",
      "Educate patient on persistent dry cough which does not respond to cough suppressants (requires switching to an ARB like Losartan)"
    ],
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from excessive moisture.",
    "dosage_forms": [
      "Oral Tablet",
      "Oral Solution (1 mg/mL)"
    ],
    "strengths": [
      "2.5 mg",
      "5 mg",
      "10 mg",
      "20 mg",
      "30 mg",
      "40 mg"
    ],
    "manufacturer": "AstraZeneca / Alvogen / Lupin / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning & Prescribing Information",
      "AHA/ACC/HFSA Heart Failure Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-15",
    "administration": "Take orally once daily at approximately the same time each day, with or without food. Swallow with a glass of water. Maintain adequate daily hydration.",
    "overdose_guidance": "The most likely manifestation of overdose is severe hypotension, electrolyte disturbances (hyperkalemia), and acute renal failure. Place the patient in a supine shock position and infuse intravenous isotonic normal saline. Lisinopril can be removed from systemic circulation by hemodialysis.",
    "slug": "lisinopril"
  },
  {
    "name": "Atorvastatin",
    "brand_names": [
      "Atorva",
      "Storvas",
      "Lipitor",
      "Lipvas",
      "Tonact",
      "Aztor",
      "Atocor"
    ],
    "generic_name": "Atorvastatin calcium",
    "active_ingredients": "Atorvastatin calcium",
    "image": "",
    "category": "Cardiovascular & Metabolic / Lipid-Lowering",
    "therapeutic_class": "HMG-CoA Reductase Inhibitor (Statin)",
    "used_for": "Primary and secondary prevention of atherosclerotic cardiovascular events (heart attack, stroke, revascularization); treatment of primary hyperlipidemia and mixed dyslipidemia.",
    "prescribed_for": [
      "Primary Hypercholesterolemia and Mixed Dyslipidemia",
      "Secondary Prevention Post-Myocardial Infarction / Angina",
      "Ischemic Stroke Risk Reduction",
      "Type 2 Diabetes Mellitus Cardiovascular Risk Reduction",
      "Familial Hypercholesterolemia"
    ],
    "how_it_works": "Competitively inhibits 3-hydroxy-3-methylglutaryl-coenzyme A (HMG-CoA) reductase, the rate-limiting enzyme in cholesterol biosynthesis, upregulating hepatic low-density lipoprotein (LDL) receptors, clearing circulating atherogenic LDL particles and apolipoprotein B from the bloodstream and stabilizing arterial plaques.",
    "common_side_effects": [
      "Myalgia (mild muscle aches)",
      "Arthralgia and joint pain",
      "Nasopharyngitis",
      "Diarrhea and dyspepsia",
      "Mild elevation in blood glucose and HbA1c"
    ],
    "serious_side_effects": [
      "Rhabdomyolysis with acute myoglobinuric renal failure (severe muscle breakdown)",
      "Immune-mediated necrotizing myopathy (IMNM \u2014 anti-HMGCR antibodies)",
      "Hepatotoxicity and severe jaundice (rare)",
      "Hemorrhagic stroke in patients with recent hemorrhagic cerebrovascular events"
    ],
    "contraindications": [
      "Active liver disease or unexplained persistent elevations in hepatic transaminases",
      "Known hypersensitivity to atorvastatin",
      "Pregnancy and breastfeeding (contraindicated due to interference with fetal steroid synthesis)"
    ],
    "drug_interactions": [
      "Strong CYP3A4 Inhibitors (Clarithromycin, Itraconazole, Protease Inhibitors): Substantially elevate atorvastatin exposure, multiplying rhabdomyolysis risk",
      "Cyclosporine and Gemfibrozil: Severe rhabdomyolysis risk (avoid co-administration)",
      "Digoxin: Mild increase in steady-state digoxin levels"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without meals at any time of day. Avoid consuming > 1.2 liters of grapefruit juice daily (CYP3A4 inhibition). Limit chronic heavy alcohol intake."
    ],
    "allergy_precautions": "Contraindicated in known statin hypersensitivity.",
    "age_precautions": {
      "children": "Approved in children >= 10 years of age with heterozygous familial hypercholesterolemia (starting dose 10 mg/day).",
      "older_adults": "Efficacy demonstrated across elderly trials. Monitor for increased susceptibility to drug-induced myopathy and frailty."
    },
    "pregnancy_breastfeeding": "Contraindicated during pregnancy and lactation. Discontinue immediately if pregnancy occurs.",
    "kidney_liver_precautions": "No dose adjustment required in renal impairment (cleared primarily via hepatic metabolism). Contraindicated in active acute hepatic disease.",
    "monitoring_requirements": "Baseline lipid panel, then 4\u201312 weeks after initiation or dose titration, then every 3\u201312 months; baseline hepatic transaminases (ALT/AST); serum creatine kinase (CK) in patients reporting muscle pain, tenderness, or weakness.",
    "precautions": [
      "Instruct patient to report unexplained muscle pain, tenderness, or dark brown urine immediately",
      "Small increase in diabetes risk is far outweighed by monumental cardiovascular death reduction"
    ],
    "storage": "Store between 20\u00b0C and 25\u00b0C (68\u00b0F to 77\u00b0F).",
    "dosage_forms": [
      "Film-Coated Oral Tablet"
    ],
    "strengths": [
      "10 mg",
      "20 mg",
      "40 mg",
      "80 mg"
    ],
    "manufacturer": "Pfizer / Viatris / Sun Pharma / Torrent / Generic manufacturers",
    "sources": [
      "FDA Prescribing Information",
      "AHA/ACC Cholesterol Guidelines",
      "NICE Clinical Guidelines",
      "DailyMed"
    ],
    "last_updated": "2026-08-18",
    "administration": "Take orally once daily at any time of day, with or without food. Take at roughly the same time each day to maintain consistent blood levels. Maintain a standard cholesterol-lowering diet during therapy.",
    "overdose_guidance": "There is no specific antidote for atorvastatin overdose. If an acute overdose occurs, provide supportive care and monitor liver function tests and serum creatine kinase (CK) levels to watch for myopathy or rhabdomyolysis. Hemodialysis is not expected to significantly increase atorvastatin clearance due to extensive plasma protein binding (>98%).",
    "slug": "atorvastatin"
  },
  {
    "name": "Amoxicillin and Clavulanate Potassium",
    "brand_names": [
      "Augmentin",
      "Clavam",
      "Moxikind-CV",
      "Augpen",
      "Mega-CV",
      "Amoclav"
    ],
    "generic_name": "Amoxicillin and clavulanate potassium",
    "active_ingredients": "Amoxicillin trihydrate + Clavulanate potassium",
    "image": "",
    "category": "Antibacterial / Beta-Lactam Combination",
    "therapeutic_class": "Aminopenicillin with Beta-Lactamase Inhibitor",
    "used_for": "Treatment of susceptible bacterial infections of the lower respiratory tract (community-acquired pneumonia), acute bacterial sinusitis, acute otitis media, urinary tract infections, and complicated skin structure infections caused by beta-lactamase-producing organisms.",
    "prescribed_for": [
      "Community-Acquired Pneumonia (Bacterial)",
      "Acute Bacterial Exacerbation of Chronic Bronchitis",
      "Acute Bacterial Rhinosinusitis",
      "Severe Acute Otitis Media",
      "Complicated Urinary Tract Infections",
      "Skin and Soft Tissue Abscesses / Animal Bites"
    ],
    "how_it_works": "Amoxicillin inhibits bacterial cell wall peptidoglycan transpeptidation, causing osmotic lysis; Clavulanate is a suicidal beta-lactamase inhibitor that irreversibly binds and inactivates beta-lactamase enzymes produced by resistant bacteria, restoring amoxicillin's broad antibacterial spectrum.",
    "common_side_effects": [
      "Diarrhea (frequent, mediated by clavulanic acid hypermotility)",
      "Nausea and vomiting",
      "Abdominal discomfort",
      "Oral or vaginal candidiasis (thrush)",
      "Mild maculopapular skin rash"
    ],
    "serious_side_effects": [
      "Immediate Type I Anaphylactic Reaction (laryngeal edema, bronchospasm, cardiovascular collapse)",
      "Cholestatic jaundice and hepatitis (Augmentin-induced hepatotoxicity)",
      "Clostridioides difficile-associated severe pseudomembranous colitis",
      "Toxic Epidermal Necrolysis / Stevens-Johnson Syndrome"
    ],
    "contraindications": [
      "History of severe allergic reaction (anaphylaxis) to penicillin or any beta-lactam antibiotic",
      "History of amoxicillin/clavulanate-associated cholestatic jaundice or hepatic dysfunction",
      "Infectious mononucleosis (EBV \u2014 high incidence of erythematous rash)"
    ],
    "drug_interactions": [
      "Warfarin: May prolong prothrombin time and elevate INR, increasing bleeding risk",
      "Methotrexate: Decreases renal tubular clearance of methotrexate, causing severe toxicity",
      "Allopurinol: Concomitant use increases incidence of drug-induced skin eruptions",
      "Probenecid: Decreases renal tubular secretion of amoxicillin, producing prolonged high antibiotic levels"
    ],
    "food_alcohol_interactions": [
      "CRITICAL: Administer at the start of a meal to enhance clavulanate absorption and dramatically reduce gastrointestinal upset and diarrhea. Avoid alcohol."
    ],
    "allergy_precautions": "STRICTLY CONTRAINDICATED in documented penicillin allergy. Inquire thoroughly regarding past penicillin rashes or anaphylactic history.",
    "age_precautions": {
      "children": "Approved in infants and children. Weight-based dosing (mg amoxicillin component/kg/day) in divided doses every 8 or 12 hours. Do not interchange different ratio formulations.",
      "older_adults": "Substantially excreted by the kidney; monitor renal function and adjust dose accordingly."
    },
    "pregnancy_breastfeeding": "Category B. Generally considered safe during pregnancy when clinically indicated. Compatible with breastfeeding (monitor infant for loose stools).",
    "kidney_liver_precautions": "Dosage adjustment required in moderate-to-severe renal impairment: eGFR 10\u201330 mL/min (500/125 mg q12h); eGFR < 10 mL/min (500/125 mg q24h). Avoid 875/125 mg tablets if eGFR < 30. Use caution and monitor liver enzymes in hepatic dysfunction.",
    "monitoring_requirements": "Complete prescribed course; monitor hepatic transaminases in prolonged treatment (> 14 days); monitor for severe watery diarrhea (C. diff).",
    "precautions": [
      "Must complete the entire prescribed regimen to prevent selection of multi-drug resistant bacterial strains",
      "Discontinue immediately if allergic symptoms appear"
    ],
    "storage": "Store tablets below 25\u00b0C (77\u00b0F). Reconstituted oral suspension must be kept refrigerated (2\u00b0C\u20138\u00b0C) and discarded after 10 days.",
    "dosage_forms": [
      "Film-Coated Tablet",
      "Chewable Tablet",
      "Powder for Oral Suspension",
      "IV Formulation"
    ],
    "strengths": [
      "500/125 mg",
      "875/125 mg",
      "250/62.5 mg/5 mL suspension",
      "400/57 mg/5 mL suspension",
      "1000/62.5 mg ER"
    ],
    "manufacturer": "GSK / Sandoz / Teva / Cipla / Generic manufacturers",
    "sources": [
      "FDA Prescribing Information",
      "IDSA/ATS Community-Acquired Pneumonia Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-20",
    "administration": "Take orally at the start of a meal or light snack to optimize absorption of clavulanic acid and significantly minimize gastrointestinal distress. Swallow tablets whole with a full glass of water. Do not crush or chew film-coated tablets. Complete full course as prescribed.",
    "overdose_guidance": "Overdosage can cause gastrointestinal symptoms (nausea, vomiting, diarrhea) and fluid/electrolyte disturbances. Renal crystalluria leading to acute renal failure has been reported with high doses. Maintain adequate fluid intake and diuresis. Amoxicillin and clavulanate potassium may both be removed from systemic circulation by hemodialysis.",
    "slug": "amoxicillin_and_clavulanate_potassium"
  },
  {
    "name": "Azithromycin",
    "brand_names": [
      "Azee",
      "Azithral",
      "Zithromax",
      "Z-Pak",
      "Azax",
      "Azimax"
    ],
    "generic_name": "Azithromycin dihydrate",
    "active_ingredients": "Azithromycin",
    "image": "",
    "category": "Antibacterial / Macrolide",
    "therapeutic_class": "Azalide Subclass Macrolide Antibiotic",
    "used_for": "Treatment of mild-to-moderate community-acquired pneumonia (covering atypical pathogens: Mycoplasma, Chlamydophila, Legionella); acute bacterial exacerbations of COPD; streptococcal pharyngitis in penicillin-allergic patients; chlamydial urethritis.",
    "prescribed_for": [
      "Atypical and Bacterial Community-Acquired Pneumonia",
      "Acute Bacterial Exacerbations of Chronic Bronchitis",
      "Acute Bacterial Sinusitis",
      "Streptococcal Pharyngitis / Tonsillitis (Penicillin-Allergic Patients)",
      "Uncomplicated Chlamydial Genital Infections"
    ],
    "how_it_works": "Binds reversibly to the 50S ribosomal subunit of susceptible bacterial microorganisms, interfering with transpeptidation and inhibiting bacterial protein synthesis, producing bacteriostatic inhibition of bacterial replication.",
    "common_side_effects": [
      "Diarrhea and loose stools",
      "Nausea and abdominal cramping",
      "Vomiting",
      "Headache and dizziness"
    ],
    "serious_side_effects": [
      "Cardiac QTc interval prolongation and Torsades de Pointes (FDA Drug Safety Warning)",
      "Severe Clostridioides difficile-associated colitis",
      "Hepatotoxicity / cholestatic jaundice",
      "Severe cutaneous adverse reactions (DRESS, SJS, TEN)"
    ],
    "contraindications": [
      "Known hypersensitivity to azithromycin, erythromycin, or any macrolide/ketolide antibiotic",
      "History of cholestatic jaundice or hepatic impairment associated with prior azithromycin use"
    ],
    "drug_interactions": [
      "QT-Prolonging Medications (Antiarrhythmics: Amiodarone, Sotalol; Antipsychotics; Fluoroquinolones): Additive risk of fatal ventricular arrhythmias",
      "Warfarin: Potentiation of anticoagulant effects and increased bleeding risk",
      "Antacids Containing Aluminum or Magnesium: Reduce peak serum concentration of azithromycin (space administration by at least 2 hours)"
    ],
    "food_alcohol_interactions": [
      "Oral tablets may be taken with or without food. Immediate-release oral suspension may be taken with food to decrease GI upset. Avoid alcohol."
    ],
    "allergy_precautions": "Discontinue immediately and provide emergency resuscitation if laryngeal swelling, hives, or bronchospasm develops.",
    "age_precautions": {
      "children": "Approved in pediatric patients >= 6 months of age for acute otitis media and pneumonia (10 mg/kg day 1, then 5 mg/kg days 2\u20135).",
      "older_adults": "Elderly patients are significantly more susceptible to drug-induced cardiac QTc prolongation and fatal arrhythmias."
    },
    "pregnancy_breastfeeding": "Category B. Animal studies reveal no evidence of fetal harm. Used in pregnancy when benefits outweigh risks. Excreted into breast milk; safe under clinical supervision.",
    "kidney_liver_precautions": "Eliminated primarily via the biliary route and liver; exercise caution in severe hepatic impairment. No dose adjustment necessary in mild-to-moderate renal failure (eGFR >= 10 mL/min).",
    "monitoring_requirements": "ECG in patients with pre-existing cardiac conduction risk factors or concomitant QT-prolonging drugs; resolution of pulmonary symptoms.",
    "precautions": [
      "FDA Warning regarding QTc prolongation and cardiovascular death risk in high-risk patients",
      "Complete prescribed 3-day or 5-day course"
    ],
    "storage": "Store tablets and dry powder between 15\u00b0C and 30\u00b0C (59\u00b0F and 86\u00b0F).",
    "dosage_forms": [
      "Oral Film-Coated Tablet",
      "Powder for Oral Suspension",
      "IV Infusion"
    ],
    "strengths": [
      "250 mg",
      "500 mg",
      "600 mg",
      "100 mg/5 mL",
      "200 mg/5 mL",
      "500 mg IV"
    ],
    "manufacturer": "Pfizer / Teva / Cipla / Lupin / Generic manufacturers",
    "sources": [
      "FDA Drug Safety Warning & Prescribing Information",
      "IDSA Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-25",
    "administration": "Take orally once daily as prescribed, with or without food. Taking with food may reduce gastrointestinal discomfort. Swallow tablets whole with water. Complete the entire prescribed regimen (e.g., 3-day or 5-day course).",
    "overdose_guidance": "Symptoms of overdose are similar to adverse reactions: severe nausea, vomiting, diarrhea, and reversible hearing impairment. Provide supportive medical care, maintain hydration and electrolytes, and monitor ECG for QT interval prolongation and ventricular arrhythmias.",
    "slug": "azithromycin"
  },
  {
    "name": "Salbutamol",
    "brand_names": [
      "Asthalin",
      "Ventolin",
      "ProAir",
      "Proventil",
      "Aerocort (Plain)",
      "Aerolin"
    ],
    "generic_name": "Albuterol / Salbutamol sulfate",
    "active_ingredients": "Salbutamol sulfate",
    "image": "",
    "category": "Respiratory / Bronchodilator",
    "therapeutic_class": "Short-Acting Beta-2 Adrenergic Agonist (SABA)",
    "used_for": "Rapid relief and emergency rescue reversal of acute bronchospasm in asthma, chronic obstructive pulmonary disease (COPD), and exercise-induced bronchospasm.",
    "prescribed_for": [
      "Acute Asthma Bronchospasm Attack (Reliever Inhaler)",
      "Exercise-Induced Bronchospasm (EIB) Prevention",
      "COPD Acute Exacerbation Bronchodilation",
      "Hyperkalemia Emergency Management (High-Dose Nebulization)"
    ],
    "how_it_works": "Selectively stimulates beta-2 adrenergic receptors on bronchial smooth muscle, activating intracellular adenylyl cyclase to convert ATP to cyclic adenosine monophosphate (cAMP), lowering intracellular calcium and producing rapid bronchial smooth muscle relaxation and airway dilation within 5 minutes.",
    "common_side_effects": [
      "Tremor (skeletal muscle hand tremors)",
      "Tachycardia and palpitations",
      "Nervousness and restlessness",
      "Headache",
      "Throat irritation and cough"
    ],
    "serious_side_effects": [
      "Paradoxical bronchospasm (sudden life-threatening airway narrowing upon inhalation)",
      "Cardiac arrhythmias and myocardial ischemia in susceptible cardiac patients",
      "Hypokalemia (intracellular potassium shift with high doses)",
      "Metabolic lactic acidosis"
    ],
    "contraindications": [
      "Hypersensitivity to salbutamol sulfate or formulation excipients (e.g., milk protein in dry powder inhalers)"
    ],
    "drug_interactions": [
      "Non-Selective Beta-Blockers (Propranolol, Carvedilol): Directly antagonize salbutamol, completely blocking bronchodilation and triggering fatal acute asthma exacerbations",
      "Diuretics (Furosemide, Thiazides): Worsens hypokalemia",
      "MAO Inhibitors and Tricyclic Antidepressants: Multiplies cardiovascular toxicity and arrhythmias"
    ],
    "food_alcohol_interactions": [
      "Inhalers are independent of food. Avoid excessive dietary caffeine which compounds tremors and tachycardia."
    ],
    "allergy_precautions": "If paradoxical bronchospasm occurs, discontinue immediately and initiate alternative emergency therapy.",
    "age_precautions": {
      "children": "Approved in all age groups. In children under 5 years, ALWAYS administer Metered Dose Inhaler (MDI) with a valved holding chamber (spacer) and fitted facial mask for effective drug deposition.",
      "older_adults": "Vulnerable to tachycardia, tremor, and ischemic cardiac stress. Monitor pulse."
    },
    "pregnancy_breastfeeding": "Category C. SABA of choice for acute asthma exacerbations in pregnancy (maternal hypoxia poses far greater risk to fetus than beta-2 agonist exposure). Compatible with breastfeeding.",
    "kidney_liver_precautions": "No dose adjustments necessary for inhaler administration.",
    "monitoring_requirements": "Frequency of inhaler usage (using a reliever > 2 times/week signals poorly controlled asthma requiring escalation of inhaled corticosteroid controller therapy); peak expiratory flow (PEF).",
    "precautions": [
      "SABA is a RESCUE reliever, NOT an anti-inflammatory controller",
      "Over-reliance on SABAs without inhaled corticosteroids dramatically increases asthma-related death (GINA consensus)"
    ],
    "storage": "Store between 15\u00b0C and 25\u00b0C (59\u00b0F and 77\u00b0F). Protect from freezing and direct sunlight. Canister is pressurized.",
    "dosage_forms": [
      "Metered-Dose Inhaler (MDI)",
      "Dry Powder Inhaler (DPI)",
      "Nebulizer Solution",
      "Oral Syrup / Tablet"
    ],
    "strengths": [
      "100 mcg/actuation (90 mcg base MDI)",
      "2.5 mg/2.5 mL nebulizer solution",
      "2 mg/5 mL syrup"
    ],
    "manufacturer": "GSK / Teva / Cipla / Perrigo",
    "sources": [
      "GINA Global Strategy for Asthma Management",
      "FDA Prescribing Information",
      "British Thoracic Society (BTS)",
      "DailyMed"
    ],
    "last_updated": "2026-08-15",
    "administration": "Inhale through the mouth using the metered-dose inhaler (MDI), ideally with a spacer device. Shake inhaler well before each actuation. Breathe out fully, place mouthpiece in mouth, press canister while inhaling slowly and deeply, and hold breath for 10 seconds. Wait 1 minute before taking a second puff if prescribed.",
    "overdose_guidance": "Manifestations of overdose are exaggerated beta-adrenergic stimulation: marked tachycardia, palpitations, severe muscle tremors, agitation, cardiac arrhythmias, hypokalemia, and metabolic acidosis. Discontinue salbutamol immediately. Provide cardiac monitoring. Cardioselective beta-blockers (e.g., metoprolol) can be cautiously considered with extreme care due to bronchospasm risk in asthmatic patients.",
    "slug": "salbutamol"
  },
  {
    "name": "Budesonide and Formoterol",
    "brand_names": [
      "Symbicort",
      "Foracort",
      "Vannair"
    ],
    "generic_name": "Budesonide and formoterol fumarate dihydrate",
    "active_ingredients": "Budesonide (inhaled corticosteroid) + Formoterol fumarate (LABA)",
    "image": "",
    "category": "Respiratory / Anti-Inflammatory Bronchodilator",
    "therapeutic_class": "ICS / LABA Fixed-Dose Combination",
    "used_for": "Maintenance and reliever treatment of bronchial asthma; maintenance treatment of airflow obstruction in Chronic Obstructive Pulmonary Disease (COPD).",
    "prescribed_for": [
      "Moderate-to-Severe Persistent Asthma",
      "SMART / MART Protocol (Single Inhaler Maintenance and Reliever Therapy)",
      "Chronic Obstructive Pulmonary Disease (COPD) Maintenance"
    ],
    "how_it_works": "Dual anti-inflammatory and bronchodilating mechanism: Budesonide binds to glucocorticoid receptors to suppress multiple inflammatory cytokines, airway eosinophil infiltration, and microvascular hyperpermeability; Formoterol is a rapid-onset, long-acting beta-2 agonist (LABA) providing smooth muscle relaxation within 1\u20133 minutes lasting >= 12 hours.",
    "common_side_effects": [
      "Oropharyngeal candidiasis (oral thrush)",
      "Dysphonia (hoarse voice)",
      "Throat irritation",
      "Mild hand tremor",
      "Headache"
    ],
    "serious_side_effects": [
      "Pneumonia in COPD patients",
      "Paradoxical bronchospasm",
      "Systemic corticosteroid effects with prolonged high doses (adrenal suppression, reduced bone mineral density, cataracts, glaucoma)",
      "Hypokalemia and cardiac arrhythmias"
    ],
    "contraindications": [
      "Primary treatment of status epilepticus or acute life-threatening episodes requiring intensive care",
      "Hypersensitivity to budesonide, formoterol, or formulation components"
    ],
    "drug_interactions": [
      "Strong CYP3A4 Inhibitors (Ketoconazole, Clarithromycin, Ritonavir): Substantially increase systemic budesonide exposure",
      "Beta-Blockers: Diminish or abolish bronchodilator response and trigger severe bronchospasm",
      "QT-Prolonging Drugs: Heighten arrhythmia risk"
    ],
    "food_alcohol_interactions": [
      "Inhaled administration is independent of meals. CRITICAL: Rinse mouth thoroughly with water and spit it out after every inhalation to prevent oral thrush and dysphonia."
    ],
    "allergy_precautions": "Discontinue if allergic bronchospasm or urticaria develops.",
    "age_precautions": {
      "children": "Approved in pediatric patients >= 6 years of age for asthma. Monitor linear height growth in children receiving chronic inhaled corticosteroids.",
      "older_adults": "Evaluate inhaler inspiratory technique; check for COPD pneumonia signs."
    },
    "pregnancy_breastfeeding": "Category C. Preferred controller option in persistent asthma during pregnancy (budesonide has the most extensive reassuring human pregnancy safety data of any ICS). Compatible with breastfeeding.",
    "kidney_liver_precautions": "No dose adjustments for renal impairment. Extensively metabolized by the liver; monitor in severe hepatic failure.",
    "monitoring_requirements": "Spirometry / FEV1 and peak flow; oral cavity inspection for fungal thrush; growth in pediatric patients; annual ophthalmologic exams with high doses.",
    "precautions": [
      "Mouth rinsing and spitting is mandatory after every use",
      "Instruct patient on proper inhaler actuation and inhalation technique"
    ],
    "storage": "Store at controlled room temperature 20\u00b0C to 25\u00b0C. Keep canister upright.",
    "dosage_forms": [
      "Metered-Dose Inhaler (MDI)",
      "Dry Powder Turbuhaler / Inhaler"
    ],
    "strengths": [
      "80/4.5 mcg",
      "160/4.5 mcg per actuation"
    ],
    "manufacturer": "AstraZeneca / Cipla / Generic manufacturers",
    "sources": [
      "GINA Global Strategy for Asthma",
      "FDA Prescribing Information",
      "GOLD COPD Guidelines",
      "DailyMed"
    ],
    "last_updated": "2026-08-19",
    "administration": "Rinse mouth thoroughly with water and spit it out after every inhalation to prevent oral candidiasis (thrush) and dysphonia. Administer twice daily, approximately 12 hours apart, morning and evening. Never swallow the inhalation powder.",
    "overdose_guidance": "Overdose risks stem primarily from the formoterol component (tachycardia, palpitations, tremor, headache, hypokalemia, arrhythmias) and high cumulative steroid doses (hypothalamic-pituitary-adrenal axis suppression). Provide supportive care and ECG monitoring.",
    "slug": "budesonide_and_formoterol"
  },
  {
    "name": "Oral Rehydration Salts (ORS)",
    "brand_names": [
      "Electral",
      "WHO-ORS",
      "Hydralyte",
      "Pedialyte",
      "Enerzal",
      "Rehydral"
    ],
    "generic_name": "Oral rehydration salts formula (WHO low-osmolarity formula)",
    "active_ingredients": "Sodium chloride (2.6 g) + Glucose anhydrous (13.5 g) + Potassium chloride (1.5 g) + Trisodium citrate dihydrate (2.9 g) per liter",
    "image": "",
    "category": "Gastrointestinal & Emergency / Fluid-Electrolyte",
    "therapeutic_class": "Oral Electrolyte and Glucose Fluid Replacement Solution",
    "used_for": "First-line prevention and treatment of dehydration and electrolyte depletion caused by acute diarrheal illnesses, gastroenteritis, cholera, heat exhaustion, and viral fevers, including Dengue.",
    "prescribed_for": [
      "Dehydration Secondary to Acute Gastroenteritis / Diarrhea",
      "Dengue Fever Fluid Maintenance (Critical to Prevent Plasma Leakage)",
      "Viral Enteritis (Rotavirus, Norovirus)",
      "Heat Exhaustion and Strenuous Dehydration",
      "Post-Surgical High-Output Stoma Fluid Balance"
    ],
    "how_it_works": "Leverages the intact intestinal sodium-glucose cotransport mechanism (SGLT1) in the apical brush border membrane of enterocytes: glucose absorption drives active sodium uptake against an electrochemical gradient, with water passively following osmolar transport, restoring intravascular volume without stressing the gut.",
    "common_side_effects": [
      "Mild nausea if ingested too rapidly in a single bolus",
      "Mild abdominal distension if overconsumed"
    ],
    "serious_side_effects": [
      "Hypernatremia (if mixed in incorrect high powder concentration with too little water)",
      "Worsening fluid overload in end-stage oliguric renal failure or uncompensated congestive heart failure"
    ],
    "contraindications": [
      "Severe intractable vomiting where fluids cannot be retained (requires intravenous rehydration)",
      "Severe hypovolemic shock (requires immediate emergency IV Ringer's Lactate / Saline resuscitation)",
      "Paralytic ileus or bowel obstruction",
      "Anuria (absence of urine output)"
    ],
    "drug_interactions": [
      "Safe and compatible with all standard antimicrobial, antipyretic, and maintenance medications"
    ],
    "food_alcohol_interactions": [
      "Dissolve strictly in clean, boiled-and-cooled drinking water. NEVER mix into milk, fruit juices, sodas, or sports drinks (which disrupt osmolarity)."
    ],
    "allergy_precautions": "No known allergic potential. Physiologic electrolyte solution.",
    "age_precautions": {
      "children": "WHO universal life-saving therapy. Administer frequent small spoonfuls or sips (5 mL every 2\u20133 minutes). Continue breastfeeding uninterrupted throughout diarrheal episodes.",
      "older_adults": "Safely prevents acute prerenal kidney failure during infectious diarrhea. Monitor in advanced congestive heart failure."
    },
    "pregnancy_breastfeeding": "Completely safe and essential in pregnancy and lactation. Rapidly reverses maternal dehydration and prevents hypoperfusion.",
    "kidney_liver_precautions": "Caution in advanced oliguric renal failure (monitor serum potassium to prevent hyperkalemia). Safe in liver disease.",
    "monitoring_requirements": "Clinical hydration status (mucous membranes, skin turgor, urine color, capillary refill, mental alertness); frequency of diarrheal stools and vomiting.",
    "precautions": [
      "CRITICAL: Mix entire packet in the exact volume of drinking water indicated on packet (typically exactly 1 liter or 200 mL)",
      "Discard any unconsumed reconstituted solution after 24 hours"
    ],
    "storage": "Store dry packets in a cool, dry place. Once mixed, use within 24 hours.",
    "dosage_forms": [
      "Dry Soluble Powder Packets",
      "Premixed Ready-to-Drink Solution",
      "Effervescent Tablets"
    ],
    "strengths": [
      "WHO Low-Osmolarity Formula (Total osmolarity: 245 mOsm/L; Sodium 75 mmol/L, Glucose 75 mmol/L)"
    ],
    "manufacturer": "FDC / Abbott / Cipla / Halewood / Generic manufacturers",
    "sources": [
      "WHO/UNICEF Diarrhea Clinical Guidelines",
      "CDC Clinical Guidance on Dehydration",
      "DailyMed"
    ],
    "last_updated": "2026-08-05",
    "administration": "Dissolve entire packet in the exact volume of clean drinking water specified on the sachet (typically 1 liter). Mix thoroughly until completely dissolved. Drink in frequent small sips throughout the day. Discard any unused solution after 24 hours.",
    "overdose_guidance": "Overdose from excessive ingestion without fluid loss can cause hypernatremia, hyperkalemia, and fluid overload. Manage by discontinuing ORS, providing plain water or hypotonic IV fluids, and monitoring serum electrolytes.",
    "slug": "oral_rehydration_salts_ors"
  },
  {
    "name": "Furosemide",
    "brand_names": [
      "Lasix",
      "Frusid",
      "Salix",
      "Uremide"
    ],
    "generic_name": "Furosemide",
    "active_ingredients": "Furosemide",
    "image": "",
    "category": "Renal & Cardiovascular / Diuretic",
    "therapeutic_class": "Loop (High-Ceiling) Diuretic",
    "used_for": "Treatment of edema associated with congestive heart failure, cirrhosis of the liver, and renal disease, including nephrotic syndrome and chronic kidney disease; management of hypertensive crisis.",
    "prescribed_for": [
      "Congestive Heart Failure Volume Overload and Pulmonary Edema",
      "Chronic Kidney Disease Edema and Volume Management",
      "Nephrotic Syndrome",
      "Hepatic Cirrhosis Ascites (with Spironolactone)",
      "Acute Oliguric Renal Failure Volume Challenge"
    ],
    "how_it_works": "Inhibits the Na+/K+/2Cl- cotransporter in the thick ascending limb of the loop of Henle, abolishing the medullary hypertonic osmotic gradient and blocking the reabsorption of sodium, chloride, and water, producing potent, rapid natriuresis and diuresis.",
    "common_side_effects": [
      "Frequent urination (polyuria)",
      "Dizziness and orthostatic hypotension",
      "Hypokalemia (muscle cramps, weakness)",
      "Hyponatremia",
      "Hyperuricemia (can precipitate acute gout attacks)"
    ],
    "serious_side_effects": [
      "Ototoxicity and permanent hearing loss (especially with rapid IV boluses or co-administered aminoglycosides)",
      "Profound volume depletion, severe dehydration, and prerenal azotemia (FDA Boxed Warning)",
      "Severe electrolyte disturbances (hypokalemia, hypomagnesemia, metabolic alkalosis)",
      "Agranulocytosis and thrombocytopenia"
    ],
    "contraindications": [
      "Anuria refractory to test doses",
      "Hepatic coma or severe electrolyte depletion until state is corrected",
      "Known hypersensitivity to furosemide or sulfonamides (sulfa drug allergy)"
    ],
    "drug_interactions": [
      "Aminoglycoside Antibiotics (Gentamicin, Amikacin): Multiplies severe ototoxicity and nephrotoxicity risk",
      "Digoxin: Furosemide-induced hypokalemia severely predisposes patient to fatal digoxin arrhythmias",
      "Lithium: Decreases renal lithium clearance, leading to acute lithium toxicity",
      "NSAIDs: Blunt furosemide's diuretic and natriuretic response"
    ],
    "food_alcohol_interactions": [
      "May take with food if gastric distress occurs. Avoid alcohol which compounds orthostatic dizziness. Encourage dietary potassium unless renal failure is present."
    ],
    "allergy_precautions": "Caution in patients with sulfonamide allergies (cross-reactivity is clinically uncommon but documented).",
    "age_precautions": {
      "children": "Approved in pediatric patients. Use weight-based dosing (1\u20132 mg/kg). Monitor for nephrocalcinosis in premature infants.",
      "older_adults": "Extreme susceptibility to sudden volume contraction, orthostatic syncope, and fall fractures. Start at lowest effective dose."
    },
    "pregnancy_breastfeeding": "Category C. Crosses the placenta; decreases maternal plasma volume and placental perfusion. Avoid unless maternal cardiac life-support necessitates. Suppresses lactation.",
    "kidney_liver_precautions": "Effective in advanced renal impairment (unlike thiazides, works down to eGFR < 30 mL/min, though higher doses are required). In hepatic cirrhosis with ascites, electrolyte shifts can trigger hepatic encephalopathy.",
    "monitoring_requirements": "Serum electrolytes (potassium, sodium, magnesium), BUN, serum creatinine, and blood pressure regularly; daily morning weight tracking.",
    "precautions": [
      "FDA Boxed Warning for Fluid and Electrolyte Depletion",
      "Usually administered in the morning or early afternoon to avoid sleep disruption from nocturia",
      "Potassium supplementation frequently required"
    ],
    "storage": "Store between 15\u00b0C and 30\u00b0C (59\u00b0F and 86\u00b0F). Protect from light.",
    "dosage_forms": [
      "Oral Tablet",
      "Oral Solution",
      "Intravenous / IM Injection"
    ],
    "strengths": [
      "20 mg",
      "40 mg",
      "80 mg",
      "10 mg/mL oral liquid",
      "10 mg/mL injection"
    ],
    "manufacturer": "Sanofi / Teva / Viatris / Sun Pharma",
    "sources": [
      "FDA Boxed Warning & Prescribing Information",
      "AHA Heart Failure Guidelines",
      "KDIGO Guidelines",
      "DailyMed"
    ],
    "last_updated": "2026-08-14",
    "administration": "Take orally in the morning with a glass of water. If taking twice daily, take the second dose in the early afternoon (e.g., 2 PM) to avoid nocturnal diuresis disrupting sleep. Can be taken with food to reduce GI upset.",
    "overdose_guidance": "Overdose causes excessive diuresis, profound volume depletion, severe dehydration, circulatory collapse, and life-threatening electrolyte derangements (hypokalemia, hyponatremia, hypochloremic alkalosis). Replace fluids and electrolytes intravenously with continuous BP, pulse, and electrolyte monitoring.",
    "slug": "furosemide"
  },
  {
    "name": "Losartan",
    "brand_names": [
      "Cozaar",
      "Losar",
      "Repace",
      "Tozaar"
    ],
    "generic_name": "Losartan potassium",
    "active_ingredients": "Losartan potassium",
    "image": "",
    "category": "Cardiovascular & Renal / Antihypertensive",
    "therapeutic_class": "Angiotensin II Receptor Blocker (ARB)",
    "used_for": "Treatment of hypertension; reduction of stroke risk in hypertensive patients with left ventricular hypertrophy; renal protection in type 2 diabetic nephropathy with elevated serum creatinine and proteinuria.",
    "prescribed_for": [
      "Hypertension (High Blood Pressure)",
      "Diabetic Nephropathy in Type 2 Diabetes Mellitus",
      "Stroke Risk Reduction in Left Ventricular Hypertrophy",
      "Proteinuria Reduction in Chronic Kidney Disease"
    ],
    "how_it_works": "Selectively blocks the binding of angiotensin II to the AT1 receptor in vascular smooth muscle and the adrenal gland, preventing vasoconstriction and aldosterone secretion, lowering systemic vascular resistance, reducing intraglomerular pressure, and halting renal fibrosis without inhibiting bradykinin degradation (no chronic dry cough).",
    "common_side_effects": [
      "Dizziness and lightheadedness",
      "Upper respiratory congestion",
      "Fatigue",
      "Back pain",
      "Orthostatic hypotension"
    ],
    "serious_side_effects": [
      "Hyperkalemia (high blood potassium)",
      "Acute renal failure in patients with bilateral renal artery stenosis",
      "Fetal toxicity and fetal demise (FDA Boxed Warning: strictly contraindicated in pregnancy)",
      "Angioedema (rare compared to ACE inhibitors)"
    ],
    "contraindications": [
      "Pregnancy (FDA Boxed Warning: causes severe oligohydramnios, skull hypoplasia, and fetal death)",
      "Concomitant use of aliskiren in patients with diabetes",
      "Known hypersensitivity to losartan"
    ],
    "drug_interactions": [
      "Potassium Supplements and Potassium-Sparing Diuretics: Multiplies hyperkalemia risk",
      "NSAIDs (Ibuprofen, Naproxen): Blunts blood pressure lowering and precipitates acute kidney injury",
      "Lithium: Decreases renal lithium clearance, causing lithium toxicity"
    ],
    "food_alcohol_interactions": [
      "May take with or without food. Avoid potassium-rich salt substitutes to prevent fatal hyperkalemia. Avoid alcohol."
    ],
    "allergy_precautions": "Patients with a history of angioedema from ACE inhibitors should be monitored with extreme vigilance.",
    "age_precautions": {
      "children": "Approved in pediatric patients >= 6 years of age for hypertension (0.7 mg/kg once daily up to 50 mg).",
      "older_adults": "Safe first-line agent. Monitor baseline kidney function and potassium."
    },
    "pregnancy_breastfeeding": "FDA Boxed Warning: Discontinue immediately when pregnancy is detected. Not recommended during breastfeeding.",
    "kidney_liver_precautions": "Proven renal benefit in diabetic nephropathy. In patients with severe volume depletion or bilateral renal artery stenosis, acute decline in renal function may occur. Extensively metabolized by the liver; initial dose should be 25 mg daily in hepatic impairment.",
    "monitoring_requirements": "Serum potassium, serum creatinine, BUN, and blood pressure at baseline and periodically.",
    "precautions": [
      "FDA Boxed Warning for Fetal Toxicity",
      "Discontinue immediately upon pregnancy diagnosis"
    ],
    "storage": "Store at 15\u00b0C to 30\u00b0C. Protect from light and moisture.",
    "dosage_forms": [
      "Film-Coated Oral Tablet"
    ],
    "strengths": [
      "25 mg",
      "50 mg",
      "100 mg"
    ],
    "manufacturer": "Organon / Merck / Torrent / Generic manufacturers",
    "sources": [
      "FDA Drug Label",
      "AHA/ACC Hypertension Guidelines",
      "KDIGO Diabetic Kidney Disease Guidelines",
      "DailyMed"
    ],
    "last_updated": "2026-08-16",
    "administration": "Take orally once or twice daily with or without food. Swallow tablet whole with water. Can be taken with other antihypertensive agents as prescribed.",
    "overdose_guidance": "Significant overdose produces severe hypotension, dizziness, and tachycardia or bradycardia (from vagal stimulation). Treatment is supportive: administer IV normal saline for volume expansion. Losartan and its active metabolite are not removed by hemodialysis.",
    "slug": "losartan"
  },
  {
    "name": "Levofloxacin",
    "brand_names": [
      "L-Cin",
      "Levaquin",
      "Glevo",
      "Levomac",
      "Fynal"
    ],
    "generic_name": "Levofloxacin hemihydrate",
    "active_ingredients": "Levofloxacin",
    "image": "",
    "category": "Antibacterial / Fluoroquinolone",
    "therapeutic_class": "Respiratory Fluoroquinolone",
    "used_for": "Treatment of severe or complicated community-acquired pneumonia; hospital-acquired pneumonia; acute bacterial exacerbations of chronic bronchitis; complicated urinary tract infections and acute pyelonephritis.",
    "prescribed_for": [
      "Severe Community-Acquired Pneumonia (CAP)",
      "Hospital-Acquired / Ventilator-Associated Pneumonia",
      "Acute Pyelonephritis and Complicated UTIs",
      "Inhalation Anthrax (Post-Exposure Prophylaxis)"
    ],
    "how_it_works": "Inhibits bacterial topoisomerase II (DNA gyrase) and topoisomerase IV, essential enzymes required for bacterial DNA replication, transcription, repair, and recombination, triggering rapid concentration-dependent bacterial death.",
    "common_side_effects": [
      "Nausea and diarrhea",
      "Headache and insomnia",
      "Dizziness",
      "Dyspepsia and abdominal pain"
    ],
    "serious_side_effects": [
      "Tendonitis and tendon rupture (FDA Boxed Warning: peak risk in Achilles tendon, elevated in elderly and steroid users)",
      "Peripheral neuropathy (FDA Boxed Warning: potentially irreversible nerve damage)",
      "Central nervous system toxicities (FDA Boxed Warning: psychosis, seizures, hallucinations)",
      "Cardiac QTc interval prolongation and Torsades de Pointes",
      "Aortic aneurysm and dissection (FDA Warning)",
      "Exacerbation of myasthenia gravis (FDA Boxed Warning)"
    ],
    "contraindications": [
      "History of tendon disorders related to fluoroquinolone administration",
      "Known hypersensitivity to levofloxacin or quinolones",
      "Myasthenia gravis (FDA Boxed Warning)",
      "Uncorrected hypokalemia or hypomagnesemia"
    ],
    "drug_interactions": [
      "Multivalent Cations (Antacids with Al/Mg, Iron supplements, Sucralfate, Didanosine): Chelate levofloxacin, completely blocking oral absorption (space by at least 2 hours before or 4 hours after)",
      "QT-Prolonging Antiarrhythmics (Amiodarone, Sotalol): Severe ventricular arrhythmia risk",
      "Systemic Corticosteroids: Multiplies tendon rupture risk by up to 5-fold",
      "Warfarin: Potentiates anticoagulant effect"
    ],
    "food_alcohol_interactions": [
      "May take with or without meals. Maintain generous water hydration to prevent crystalluria. Avoid calcium-fortified juices alone unless taken with a full meal."
    ],
    "allergy_precautions": "Discontinue at the first appearance of a skin rash, jaundice, or tendon pain/swelling.",
    "age_precautions": {
      "children": "Generally avoided in pediatric patients due to juvenile articular cartilage damage, unless treating inhalation anthrax or plague.",
      "older_adults": "FDA Boxed Warning: Severe vulnerability to Achilles tendon rupture, fatal QTc arrhythmias, and CNS delirium. Reserve for when no alternatives exist."
    },
    "pregnancy_breastfeeding": "Category C. Avoid in pregnancy and breastfeeding due to potential arthropathy in developing fetal weight-bearing joints.",
    "kidney_liver_precautions": "Excreted predominantly unchanged via renal excretion (~87%). Mandatory dosage adjustment in renal impairment: eGFR 20\u201349 mL/min (500 mg initial, then 250 mg q24h); eGFR 10\u201319 mL/min (500 mg initial, then 250 mg q48h).",
    "monitoring_requirements": "Renal function; ECG in patients with cardiac conduction risk; immediate cessation upon any tendon pain or swelling.",
    "precautions": [
      "FDA Boxed Warnings for Tendonitis/Rupture, Neuropathy, CNS Toxicities, and Myasthenia Gravis",
      "Do not exercise if joint or tendon aching develops"
    ],
    "storage": "Store at 25\u00b0C (77\u00b0F). Protect from light.",
    "dosage_forms": [
      "Oral Film-Coated Tablet",
      "Oral Solution (25 mg/mL)",
      "IV Premixed Infusion"
    ],
    "strengths": [
      "250 mg",
      "500 mg",
      "750 mg",
      "500 mg IV",
      "750 mg IV"
    ],
    "manufacturer": "Janssen / Sanofi / Cipla / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning & Prescribing Information",
      "IDSA Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-22",
    "administration": "Take orally once daily with a full glass of water, with or without meals. Drink plenty of water throughout the day to avoid crystalluria. Space at least 2 hours before or 2 hours after magnesium/aluminum antacids, iron supplements, or sucralfate.",
    "overdose_guidance": "Symptoms include CNS toxicities (confusion, dizziness, tremor, convulsions) and QT prolongation. Maintain hydration, monitor ECG and electrolytes, and provide supportive management. Hemodialysis removes minimal drug.",
    "slug": "levofloxacin"
  },
  {
    "name": "Cetirizine",
    "brand_names": [
      "Cetzine",
      "Alerid",
      "Okacet",
      "Zyrtec",
      "Incid L",
      "Piriteze",
      "Zyrtec Allergy"
    ],
    "generic_name": "Cetirizine hydrochloride",
    "active_ingredients": "Cetirizine hydrochloride",
    "image": "",
    "category": "Allergic & Respiratory / Antihistamine",
    "therapeutic_class": "Second-Generation H1 Receptor Antagonist",
    "used_for": "Relief of allergic symptoms associated with seasonal and perennial allergic rhinitis (sneezing, runny nose, itching, post-nasal drip) and treatment of uncomplicated skin manifestations of chronic idiopathic urticaria.",
    "prescribed_for": [
      "Allergic Rhinitis (Hay Fever)",
      "Chronic Idiopathic Urticaria (Hives)",
      "Allergic Conjunctivitis",
      "Dermatographism and Pruritus",
      "Insect Bite Hypersensitivity"
    ],
    "how_it_works": "Competitively and selectively inhibits peripheral H1 histamine receptors on effector cells, preventing histamine-mediated capillary permeability, wheal and flare formation, mucosal edema, pruritus, and smooth muscle contraction, with minimal penetration of the blood-brain barrier resulting in low sedation rates.",
    "common_side_effects": [
      "Mild somnolence / drowsiness (dose-dependent)",
      "Dry mouth (mild anticholinergic)",
      "Fatigue",
      "Headache",
      "Pharyngitis"
    ],
    "serious_side_effects": [
      "Severe hypersensitivity reactions and angioedema (rare)",
      "Urinary retention in prostatic hypertrophy",
      "Severe central sedation with concomitant depressants"
    ],
    "contraindications": [
      "Severe end-stage renal disease (eGFR < 10 mL/min) or patients undergoing hemodialysis",
      "Known hypersensitivity to cetirizine, hydroxyzine, or piperazine derivatives"
    ],
    "drug_interactions": [
      "CNS Depressants (Alcohol, Benzodiazepines, Opioids, Sedating Antidepressants): Additive central nervous system depression and psychomotor impairment",
      "Theophylline: Small reduction in cetirizine clearance"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without food. Avoid alcohol, which compounds drowsiness and slows reaction times."
    ],
    "allergy_precautions": "Discontinue if urticaria worsens or angioedema develops.",
    "age_precautions": {
      "children": "Approved in infants and children >= 6 months of age for allergic rhinitis and chronic hives. Oral syrup formulation allows accurate dosing.",
      "older_adults": "Decreased renal clearance; start at 5 mg once daily to prevent accumulation and daytime sedation."
    },
    "pregnancy_breastfeeding": "Category B. Large human prospective registry data show no increase in birth defects. Second-generation antihistamine of choice in pregnancy. Excreted in breast milk in small amounts.",
    "kidney_liver_precautions": "Dosage reduction (5 mg once daily) required if eGFR < 50 mL/min or in hepatic impairment. Contraindicated if eGFR < 10 mL/min.",
    "monitoring_requirements": "Symptom control; assessment for excessive somnolence.",
    "precautions": [
      "Warn patients to observe individual response before driving or operating hazardous machinery",
      "Avoid concurrent alcohol"
    ],
    "storage": "Store between 20\u00b0C and 25\u00b0C (68\u00b0F to 77\u00b0F).",
    "dosage_forms": [
      "Oral Film-Coated Tablet",
      "Chewable Tablet",
      "Oral Syrup (5 mg/5 mL)"
    ],
    "strengths": [
      "5 mg",
      "10 mg",
      "5 mg/5 mL syrup"
    ],
    "manufacturer": "Johnson & Johnson / Haleon / Cipla / Generic manufacturers",
    "sources": [
      "FDA Drug Label",
      "EAACI Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-10",
    "administration": "Take orally once daily with or without food, preferably in the evening if drowsiness occurs. Swallow tablet with a glass of water. Avoid exceeding the recommended 10 mg daily dose in adults.",
    "overdose_guidance": "Symptoms of overdose include somnolence, confusion, agitation, restlessness, tachycardia, tremors, and urinary retention. In case of massive overdose, gastric lavage should be considered alongside symptomatic and supportive treatment. Cetirizine is not effectively eliminated by hemodialysis.",
    "slug": "cetirizine"
  },
  {
    "name": "Omeprazole",
    "brand_names": [
      "Omez",
      "Omee",
      "Prilosec",
      "Losec",
      "Ocid",
      "Prilosec OTC"
    ],
    "generic_name": "Omeprazole",
    "active_ingredients": "Omeprazole magnesium",
    "image": "",
    "category": "Gastrointestinal / Acid-Suppressing",
    "therapeutic_class": "Proton Pump Inhibitor (PPI)",
    "used_for": "Treatment of gastroesophageal reflux disease (GERD), erosive esophagitis, active duodenal and benign gastric ulcers; Helicobacter pylori eradication (in combination with antibiotics); prevention of NSAID-induced ulcers.",
    "prescribed_for": [
      "Gastroesophageal Reflux Disease (GERD)",
      "Erosive Esophagitis Healing and Maintenance",
      "Peptic Ulcer Disease (Gastric and Duodenal)",
      "Helicobacter pylori Triple Therapy Eradication",
      "NSAID Gastroprotection in High-Risk Patients",
      "Zollinger-Ellison Syndrome"
    ],
    "how_it_works": "Irreversibly inhibits the gastric parietal cell hydrogen-potassium ATPase enzyme system (H+/K+ ATPase 'proton pump'), suppressing both basal and stimulated gastric acid secretion regardless of secretagogue stimulus, providing sustained acid suppression allowing mucosal healing.",
    "common_side_effects": [
      "Headache",
      "Abdominal pain and flatulence",
      "Nausea and vomiting",
      "Diarrhea or constipation"
    ],
    "serious_side_effects": [
      "Clostridioides difficile-associated severe diarrhea",
      "Bone fracture risk (hip, wrist, spine) with high-dose long-term therapy (FDA Warning)",
      "Hypomagnesemia with long-term therapy",
      "Acute interstitial nephritis (kidney inflammation)",
      "Vitamin B12 deficiency with chronic use (> 3 years)"
    ],
    "contraindications": [
      "Known hypersensitivity to omeprazole or any substituted benzimidazole PPI",
      "Concomitant administration of rilpivirine-containing products"
    ],
    "drug_interactions": [
      "Clopidogrel (Plavix): FDA Boxed Warning \u2014 Omeprazole competitively inhibits CYP2C19, reducing active clopidogrel metabolite formation by ~45% and blunting antiplatelet protection (use pantoprazole instead if PPI required)",
      "Methotrexate: Elevates methotrexate levels and toxicity",
      "HIV Protease Inhibitors (Atazanavir): Significantly decreases atazanavir absorption"
    ],
    "food_alcohol_interactions": [
      "CRITICAL: Take 30 to 60 minutes before breakfast on an empty stomach for maximum acid suppression. Swallow delayed-release capsules whole; do not crush or chew."
    ],
    "allergy_precautions": "Discontinue if acute tubulointerstitial nephritis, maculopapular rash, or erythema multiforme develops.",
    "age_precautions": {
      "children": "Approved in pediatric patients >= 1 year of age for GERD and erosive esophagitis (dose based on body weight).",
      "older_adults": "Higher susceptibility to bone fractures, C. diff diarrhea, and vitamin B12 malabsorption. Use lowest effective dose for shortest duration."
    },
    "pregnancy_breastfeeding": "Category C. Epidemiological studies show no major malformations; however, preferred in pregnancy if indicated. Excreted into human milk in low amounts.",
    "kidney_liver_precautions": "No dose adjustment required in renal impairment. In hepatic impairment, bioavailability is increased; maximum daily dose is 20 mg.",
    "monitoring_requirements": "Serum magnesium periodically with prolonged use (> 1 year); bone density in high-risk patients; vitamin B12 levels.",
    "precautions": [
      "Take 30\u201360 minutes before morning meal",
      "Do not take clopidogrel concurrently (CYP2C19 interaction)"
    ],
    "storage": "Store between 15\u00b0C and 30\u00b0C. Protect from moisture.",
    "dosage_forms": [
      "Delayed-Release Capsule",
      "Delayed-Release Oral Suspension"
    ],
    "strengths": [
      "10 mg",
      "20 mg",
      "40 mg"
    ],
    "manufacturer": "AstraZeneca / Haleon / Dr. Reddy's / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning & Prescribing Information",
      "ACG GERD Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-12",
    "administration": "Take orally once daily in the morning, 30 to 60 minutes before breakfast. Capsules should be swallowed whole with water; do not crush or chew. For patients unable to swallow capsules, open capsule and sprinkle intact pellets onto a tablespoon of cool applesauce and swallow immediately without chewing.",
    "overdose_guidance": "Overdose symptoms include confusion, drowsiness, blurred vision, tachycardia, nausea, vomiting, diaphoresis, flushing, and dry mouth. Manifestations are typically transient. Treatment is symptomatic and supportive; omeprazole is not readily dialyzable due to extensive protein binding.",
    "slug": "omeprazole"
  },
  {
    "name": "Aspirin",
    "brand_names": [
      "Bayer Aspirin",
      "Ecosprin",
      "Disprin",
      "Bufferin"
    ],
    "generic_name": "Acetylsalicylic acid (ASA)",
    "active_ingredients": "Acetylsalicylic acid",
    "image": "",
    "category": "Antiplatelet & Analgesic / NSAID",
    "therapeutic_class": "Salicylate Antiplatelet Agent",
    "used_for": "Secondary prevention of cardiovascular events (heart attack, ischemic stroke) at low doses (75\u2013100 mg), and relief of pain, inflammation, and fever at higher doses (325\u2013650 mg). STRICTLY AVOID IN DENGUE due to fatal hemorrhage risk.",
    "prescribed_for": [
      "Coronary Artery Disease",
      "Secondary Prevention of Ischemic Stroke & TIA",
      "Post-PCI / Post-CABG Antithrombotic Therapy",
      "Acute Coronary Syndrome",
      "Mild-to-Moderate Pain and Fever (Non-Dengue)"
    ],
    "how_it_works": "Irreversibly acetylates and inactivates platelet cyclooxygenase-1 (COX-1), blocking thromboxane A2 production for the entire lifespan of the platelet (7\u201310 days).",
    "common_side_effects": [
      "Dyspepsia and gastric irritation",
      "Nausea",
      "Easy bruising and prolonged bleeding time",
      "Tinnitus (at high doses)"
    ],
    "serious_side_effects": [
      "Major gastrointestinal hemorrhage or ulcer perforation",
      "Hemorrhagic stroke",
      "Reye's syndrome in children/adolescents with viral illness",
      "Aspirin-induced bronchospasm in asthmatics"
    ],
    "contraindications": [
      "Active peptic ulcer disease or severe GI bleeding",
      "Bleeding disorders (hemophilia)",
      "CRITICAL: Dengue fever or suspected viral hemorrhagic illnesses",
      "Children and teenagers with viral infections (Reye's syndrome risk)",
      "Severe renal or hepatic failure",
      "Aspirin-exacerbated respiratory disease (AERD)"
    ],
    "drug_interactions": [
      "Other anticoagulants (Warfarin, Apixaban) & antiplatelets \u2014 major bleeding risk",
      "NSAIDs (ibuprofen) \u2014 blocks aspirin's irreversible platelet inhibition when taken before aspirin",
      "Methotrexate \u2014 reduced clearance and increased toxicity"
    ],
    "food_alcohol_interactions": [
      "Take with food or a large glass of water to reduce gastric discomfort. Avoid alcohol which compounds gastric mucosal bleeding risk."
    ],
    "allergy_precautions": "Contraindicated in patients with aspirin allergy or triad asthma.",
    "age_precautions": {
      "children": "STRICTLY CONTRAINDICATED in children and teenagers under 16 years of age suffering from viral infections due to fatal Reye's syndrome risk.",
      "older_adults": "High risk of occult gastrointestinal hemorrhage. Routine primary prevention in adults > 70 years is no longer recommended by ACC/AHA."
    },
    "pregnancy_breastfeeding": "Low-dose (81 mg) is used under obstetrician care to prevent preeclampsia in high-risk pregnancies. High-dose is contraindicated in the third trimester.",
    "kidney_liver_precautions": "Avoid in severe renal impairment (eGFR < 10 mL/min) and severe hepatic failure.",
    "monitoring_requirements": "Complete blood count and hemoglobin; monitoring for signs of black tarry stools (melena) or unusual bruising.",
    "precautions": [
      "Contraindicated in children under 16 years with viral fevers (Reye's syndrome)",
      "Discontinue 7 days before major elective surgery if instructed by surgical team"
    ],
    "storage": "Store below 25\u00b0C in airtight containers. Discard if vinegar odor develops (hydrolysis).",
    "dosage_forms": [
      "Enteric-Coated Tablet",
      "Dispersible Tablet",
      "Chewable Tablet"
    ],
    "strengths": [
      "75 mg",
      "81 mg",
      "100 mg",
      "300 mg",
      "325 mg",
      "500 mg"
    ],
    "manufacturer": "Bayer / USV / Sanofi / Generic manufacturers",
    "sources": [
      "FDA Drug Label",
      "AHA/ACC Secondary Prevention Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-14",
    "administration": "Take orally with food or a large glass of water to minimize gastric mucosal irritation. Swallow enteric-coated (cardiac low-dose) tablets whole; do not crush or chew.",
    "overdose_guidance": "Salicylate poisoning presents with tinnitus, tachypnea (respiratory alkalosis followed by severe metabolic acidosis), hyperthermia, vomiting, confusion, seizures, and non-cardiogenic pulmonary edema. Administer activated charcoal, urinary alkalinization with IV sodium bicarbonate (target urine pH 7.5-8.0) to enhance renal elimination, and emergent hemodialysis for severe poisoning (levels > 100 mg/dL or severe acidosis).",
    "slug": "aspirin"
  },
  {
    "name": "Clopidogrel",
    "brand_names": [
      "Plavix",
      "Deplatt",
      "Clopilet",
      "Ceruvit"
    ],
    "generic_name": "Clopidogrel bisulfate",
    "active_ingredients": "Clopidogrel bisulfate",
    "image": "",
    "category": "Cardiovascular / Antiplatelet",
    "therapeutic_class": "Thienopyridine P2Y12 Platelet Inhibitor",
    "used_for": "Prevention of atherothrombotic events in patients with acute coronary syndrome, recent myocardial infarction, recent ischemic stroke, or established peripheral arterial disease.",
    "prescribed_for": [
      "Acute Coronary Syndrome (STEMI / NSTEMI)",
      "Recent Myocardial Infarction",
      "Recent Ischemic Stroke",
      "Percutaneous Coronary Intervention (PCI / Stent)",
      "Peripheral Arterial Disease"
    ],
    "how_it_works": "Prodrug metabolized by hepatic CYP2C19 into an active thiol metabolite that irreversibly binds to the P2Y12 adenosine diphosphate (ADP) receptor on platelets, inhibiting ADP-mediated activation of the GPIIb/IIIa complex.",
    "common_side_effects": [
      "Hematoma and bruising",
      "Epistaxis (nosebleeds)",
      "Gastrointestinal bleeding",
      "Dyspepsia and abdominal pain"
    ],
    "serious_side_effects": [
      "Thrombotic Thrombocytopenic Purpura (TTP \u2014 urgent medical emergency)",
      "Severe major internal hemorrhage",
      "Agranulocytosis / severe neutropenia (rare)"
    ],
    "contraindications": [
      "Active pathological bleeding (such as peptic ulcer or intracranial hemorrhage)",
      "Known hypersensitivity to clopidogrel"
    ],
    "drug_interactions": [
      "CYP2C19 Inhibitors (Omeprazole, Esomeprazole) \u2014 FDA Boxed Warning: significantly reduces clopidogrel activation; use pantoprazole instead if PPI is required",
      "Anticoagulants & NSAIDs \u2014 additive bleeding risk"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without meals. Avoid alcohol to minimize gastrointestinal ulceration and bleeding risk."
    ],
    "allergy_precautions": "Discontinue if acute generalized exanthematous pustulosis or angioedema occurs.",
    "age_precautions": {
      "children": "Safety and efficacy not established in pediatric patients.",
      "older_adults": "Elderly patients have higher baseline bleeding risks. Monitor closely."
    },
    "pregnancy_breastfeeding": "Category B. Use only if clearly needed. Discontinue during breastfeeding.",
    "kidney_liver_precautions": "Experience limited in renal impairment. Avoid in severe hepatic impairment where bleeding diathesis may be exacerbated.",
    "monitoring_requirements": "Complete blood counts (platelets); hemoglobin/hematocrit periodically.",
    "precautions": [
      "FDA Boxed Warning: Reduced effectiveness in CYP2C19 poor metabolizers",
      "Usually withheld 5 days prior to elective coronary artery bypass graft (CABG) surgery"
    ],
    "storage": "Store at 25\u00b0C (77\u00b0F). Protect from moisture.",
    "dosage_forms": [
      "Film-Coated Tablet"
    ],
    "strengths": [
      "75 mg",
      "300 mg (loading dose)"
    ],
    "manufacturer": "Sanofi / Bristol-Myers Squibb / Sun Pharma / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning and Prescribing Information",
      "AHA/ACC PCI Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-07-29",
    "administration": "Take orally once daily with or without food, at the same time each day. Swallow whole with water. Do not stop taking clopidogrel without consulting your cardiologist, as abrupt cessation drastically increases stent thrombosis risk.",
    "overdose_guidance": "Manifestations of overdose include prolonged bleeding time and catastrophic hemorrhage. There is no specific pharmacological reversal agent; if rapid reversal is necessary, platelet transfusions can restore hemostasis.",
    "slug": "clopidogrel"
  },
  {
    "name": "Metoprolol",
    "brand_names": [
      "Lopressor",
      "Toprol-XL",
      "Betaloc",
      "Metolar"
    ],
    "generic_name": "Metoprolol tartrate / succinate",
    "active_ingredients": "Metoprolol succinate (extended-release) or Metoprolol tartrate (immediate-release)",
    "image": "",
    "category": "Cardiovascular / Beta-Blocker",
    "therapeutic_class": "Cardioselective Beta-1 Adrenergic Receptor Blocker",
    "used_for": "Management of hypertension, long-term angina pectoris, hemodynamically stable congestive heart failure, and post-myocardial infarction cardioprotection.",
    "prescribed_for": [
      "Hypertension",
      "Angina Pectoris (Chest Pain)",
      "Heart Failure with Reduced Ejection Fraction (HFrEF)",
      "Atrial Fibrillation Rate Control",
      "Post-Heart Attack Cardioprotection",
      "Migraine Prophylaxis"
    ],
    "how_it_works": "Competitively blocks beta-1 adrenergic receptors in cardiac tissue, reducing heart rate, cardiac output, myocardial oxygen demand, and renin release from juxtaglomerular cells.",
    "common_side_effects": [
      "Bradycardia (slow heart rate)",
      "Fatigue and exercise intolerance",
      "Dizziness",
      "Cold hands and feet (peripheral vasoconstriction)",
      "Depression or sleep disturbance"
    ],
    "serious_side_effects": [
      "Severe bradycardia or complete heart block",
      "Acute heart failure exacerbation upon initiation",
      "Bronchospasm in asthmatic patients (at higher doses where beta-1 selectivity is lost)",
      "Masking of hypoglycemia symptoms in diabetics (except sweating)"
    ],
    "contraindications": [
      "Severe bradycardia (< 45 bpm)",
      "Second- or third-degree heart block (without a pacemaker)",
      "Cardiogenic shock or decompensated heart failure",
      "Severe peripheral arterial disease"
    ],
    "drug_interactions": [
      "Non-dihydropyridine CCBs (Verapamil, Diltiazem) \u2014 severe bradycardia and conduction block",
      "Amiodarone and Digoxin \u2014 additive slowing of AV node conduction",
      "CYP2D6 inhibitors (fluoxetine, paroxetine) \u2014 marked elevation of metoprolol levels"
    ],
    "food_alcohol_interactions": [
      "Take Toprol-XL (succinate) with or immediately following a meal. Alcohol can accelerate drug release from some extended-release formulations."
    ],
    "allergy_precautions": "Contraindicated in severe beta-blocker hypersensitivity.",
    "age_precautions": {
      "children": "Approved in pediatric patients >= 6 years of age for hypertension.",
      "older_adults": "Start at lower doses due to decreased hepatic metabolism and susceptibility to severe bradycardia."
    },
    "pregnancy_breastfeeding": "Category C. Can cause fetal bradycardia and growth restriction. Use only if benefits clearly outweigh risks. Excreted in breast milk in small amounts.",
    "kidney_liver_precautions": "No dose adjustment needed in renal failure. Extensively cleared by the liver; dose reduction required in severe hepatic impairment.",
    "monitoring_requirements": "Blood pressure and heart rate (pulse) regularly; monitor for heart failure signs (shortness of breath, swelling).",
    "precautions": [
      "FDA Boxed Warning: Never abruptly discontinue beta-blocker therapy; sudden cessation can trigger severe rebound angina, arrhythmias, or myocardial infarction (taper over 1\u20132 weeks)",
      "Use with extreme caution in asthmatics"
    ],
    "storage": "Store at 20\u00b0C to 25\u00b0C. Protect from moisture.",
    "dosage_forms": [
      "Immediate-Release Tablet (Tartrate)",
      "Extended-Release Tablet (Succinate ER)",
      "IV Injection"
    ],
    "strengths": [
      "25 mg",
      "50 mg",
      "100 mg",
      "200 mg ER"
    ],
    "manufacturer": "AstraZeneca / Novartis / Cipla / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning and Prescribing Information",
      "AHA/ACC Heart Failure Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-22",
    "administration": "Take orally with or immediately following a meal, as food significantly increases systemic bioavailability. Swallow extended-release (succinate) tablets whole; scored tablets may be split but not crushed or chewed.",
    "overdose_guidance": "Overdose presents with severe bradycardia, profound hypotension, heart block, cardiogenic shock, bronchospasm, and hypoglycemia. Immediately institute cardiac monitoring. Administer IV atropine for bradycardia. If refractory, administer intravenous Glucagon (5 to 10 mg bolus followed by infusion), high-dose insulin euglycemic therapy, or transvenous pacemaker.",
    "slug": "metoprolol"
  },
  {
    "name": "Montelukast",
    "brand_names": [
      "Singulair",
      "Montair",
      "Telekast",
      "Romilast"
    ],
    "generic_name": "Montelukast sodium",
    "active_ingredients": "Montelukast sodium",
    "image": "",
    "category": "Respiratory & Allergy / Leukotriene Receptor Antagonist",
    "therapeutic_class": "Cysteinyl Leukotriene Receptor Antagonist (LTRA)",
    "used_for": "Prophylaxis and chronic treatment of bronchial asthma in adults and children; prevention of exercise-induced bronchospasm; relief of symptoms of seasonal and perennial allergic rhinitis.",
    "prescribed_for": [
      "Chronic Asthma Maintenance",
      "Exercise-Induced Bronchospasm Prevention",
      "Seasonal Allergic Rhinitis",
      "Perennial Allergic Rhinitis",
      "Aspirin-Exacerbated Respiratory Disease (AERD)"
    ],
    "how_it_works": "Selectively binds with high affinity to the cysteinyl leukotriene receptor (CysLT1) on airway smooth muscle cells and macrophages, blocking the pro-inflammatory actions of LTC4, LTD4, and LTE4, preventing airway edema, smooth muscle contraction, and cellular inflammation.",
    "common_side_effects": [
      "Upper respiratory infection",
      "Fever and headache",
      "Pharyngitis and cough",
      "Abdominal pain and diarrhea",
      "Otitis media in young children"
    ],
    "serious_side_effects": [
      "Serious neuropsychiatric events (FDA Boxed Warning: agitation, aggression, depression, sleep disturbances, hallucinations, suicidal ideation)",
      "Systemic eosinophilia and Churg-Strauss syndrome (eosinophilic granulomatosis with polyangiitis)",
      "Severe hepatic impairment (rare)"
    ],
    "contraindications": [
      "Known hypersensitivity to montelukast sodium or formulation excipients"
    ],
    "drug_interactions": [
      "Phenobarbital and Rifampin: Induce CYP3A4, reducing montelukast serum concentrations",
      "Gemfibrozil: Inhibits CYP2C8, doubling montelukast exposure"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without food. Typically administered once daily in the evening for asthma."
    ],
    "allergy_precautions": "Discontinue immediately and seek psychiatric/medical attention if mood or behavioral changes occur.",
    "age_precautions": {
      "children": "Approved in pediatric patients as young as 12 months for asthma (chewable tablets and oral granules).",
      "older_adults": "No overall differences in safety or effectiveness observed in geriatric trials."
    },
    "pregnancy_breastfeeding": "Category B. Available human pregnancy registry data have not established a drug-associated risk of major birth defects. Compatible with breastfeeding.",
    "kidney_liver_precautions": "No dose adjustment required in renal impairment. Caution in severe hepatic insufficiency (metabolized extensively by liver).",
    "monitoring_requirements": "Screen for neuropsychiatric symptoms and behavioral disturbances at every clinical consultation; asthma symptom control.",
    "precautions": [
      "FDA Boxed Warning for Neuropsychiatric Events",
      "Not indicated for the reversal of acute bronchospasm attack (continue carrying rescue SABA inhaler)"
    ],
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from moisture and light.",
    "dosage_forms": [
      "Film-Coated Tablet",
      "Chewable Tablet",
      "Oral Granules Packet"
    ],
    "strengths": [
      "4 mg chewable / granules",
      "5 mg chewable",
      "10 mg tablet"
    ],
    "manufacturer": "Organon / Merck / Cipla / Sun Pharma / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning and Prescribing Information",
      "GINA Guidelines",
      "British National Formulary (BNF)",
      "DailyMed"
    ],
    "last_updated": "2026-08-15",
    "administration": "Take orally once daily in the evening, with or without food. For asthma, administration in the evening provides peak airway protection during vulnerable early morning hours. Chewable tablets must be chewed completely before swallowing.",
    "overdose_guidance": "Symptoms in overdose include abdominal pain, somnolence, thirst, headache, vomiting, and psychomotor hyperactivity. Treatment is supportive. Hemodialysis is ineffective due to extensive protein binding (>99%).",
    "slug": "montelukast"
  },
  {
    "name": "Pantoprazole",
    "brand_names": [
      "Pan 40",
      "Pantocid",
      "Protonix",
      "Pantodac",
      "Pantosec",
      "Pan D (Plain)"
    ],
    "generic_name": "Pantoprazole sodium",
    "active_ingredients": "Pantoprazole sodium",
    "image": "",
    "category": "Gastrointestinal / Acid-Suppressing",
    "therapeutic_class": "Proton Pump Inhibitor (PPI)",
    "used_for": "Treatment of gastroesophageal reflux disease (GERD), erosive esophagitis, Zollinger-Ellison syndrome; preferred PPI in patients receiving clopidogrel antiplatelet therapy due to minimal CYP2C19 inhibition.",
    "prescribed_for": [
      "Gastroesophageal Reflux Disease (GERD)",
      "Erosive Esophagitis",
      "Peptic Ulcer Bleeding Prevention",
      "Zollinger-Ellison Syndrome",
      "Co-prescription with Clopidogrel in High GI-Risk Cardiac Patients"
    ],
    "how_it_works": "Binds covalently to the H+/K+ ATPase enzyme system at the secretory surface of the gastric parietal cell, blocking the final step in gastric acid production. Exhibits low affinity for hepatic CYP2C19, avoiding metabolic interference with clopidogrel activation.",
    "common_side_effects": [
      "Headache",
      "Diarrhea",
      "Nausea and abdominal pain",
      "Flatulence",
      "Dizziness"
    ],
    "serious_side_effects": [
      "Clostridioides difficile-associated diarrhea",
      "Bone fractures with long-term high-dose therapy",
      "Hypomagnesemia",
      "Acute interstitial nephritis",
      "Subacute cutaneous lupus erythematosus"
    ],
    "contraindications": [
      "Hypersensitivity to pantoprazole or substituted benzimidazoles",
      "Concurrent administration of rilpivirine"
    ],
    "drug_interactions": [
      "Unlike omeprazole, does NOT significantly inhibit CYP2C19 or diminish clopidogrel antiplatelet activity (preferred PPI for cardiac patients on Plavix)",
      "Methotrexate: Elevates methotrexate levels",
      "HIV Protease Inhibitors: Reduces atazanavir absorption"
    ],
    "food_alcohol_interactions": [
      "Take 30 minutes before breakfast with water. Swallow delayed-release tablets whole; do not chew, crush, or split."
    ],
    "allergy_precautions": "Discontinue if acute tubulointerstitial nephritis, maculopapular rash, or erythema multiforme develops.",
    "age_precautions": {
      "children": "Approved in pediatric patients >= 5 years of age for erosive esophagitis.",
      "older_adults": "Use lowest effective dose for shortest duration to minimize bone fracture and infection risks."
    },
    "pregnancy_breastfeeding": "Category B. Preferred over other PPIs in many clinical settings. Excreted into human milk in low amounts.",
    "kidney_liver_precautions": "No dose adjustments for renal failure. Daily dose should not exceed 20 mg in severe cirrhosis.",
    "monitoring_requirements": "Serum magnesium periodically with prolonged therapy; monitoring for persistent watery diarrhea.",
    "precautions": [
      "Take 30 minutes before breakfast",
      "Preferred PPI when antiplatelet clopidogrel therapy is co-administered"
    ],
    "storage": "Store between 20\u00b0C and 25\u00b0C. Protect from moisture.",
    "dosage_forms": [
      "Delayed-Release Tablet",
      "Powder for Delayed-Release Oral Suspension",
      "IV Formulation"
    ],
    "strengths": [
      "20 mg",
      "40 mg",
      "40 mg IV"
    ],
    "manufacturer": "Pfizer / Sun Pharma / Alkem / Generic manufacturers",
    "sources": [
      "FDA Prescribing Information",
      "ACG Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-16",
    "administration": "Take orally once daily in the morning, 30 minutes before a meal with a full glass of water. Delayed-release tablets must be swallowed whole and must not be chewed, crushed, or split because the enteric coating protects the active drug from gastric acid.",
    "overdose_guidance": "Overdose symptoms may include drowsiness, flushing, blurred vision, headache, and abdominal pain. Monitor vital signs and provide supportive care. Hemodialysis is not effective in clearing pantoprazole due to extensive protein binding (~98%).",
    "slug": "pantoprazole"
  },
  {
    "name": "Sertraline",
    "brand_names": [
      "Sertima",
      "Zoloft",
      "Daxid",
      "Lustral",
      "Serlift"
    ],
    "generic_name": "Sertraline hydrochloride",
    "active_ingredients": "Sertraline hydrochloride",
    "image": "",
    "category": "Psychiatric / Antidepressant",
    "therapeutic_class": "Selective Serotonin Reuptake Inhibitor (SSRI)",
    "used_for": "Treatment of Major Depressive Disorder (MDD), Obsessive-Compulsive Disorder (OCD), Panic Disorder, Post-Traumatic Stress Disorder (PTSD), Social Anxiety Disorder, and Premenstrual Dysphoric Disorder.",
    "prescribed_for": [
      "Major Depressive Disorder",
      "Generalized Anxiety Disorder & Panic Disorder",
      "Obsessive-Compulsive Disorder",
      "Post-Traumatic Stress Disorder",
      "Social Anxiety Disorder"
    ],
    "how_it_works": "Selectively inhibits the presynaptic neuronal reuptake of serotonin (5-HT), increasing synaptic serotonin concentrations in the central nervous system, enhancing serotonergic neurotransmission and downregulating inhibitory autoreceptors over 2\u20134 weeks.",
    "common_side_effects": [
      "Nausea and diarrhea",
      "Insomnia or somnolence",
      "Tremor and dizziness",
      "Dry mouth",
      "Sexual dysfunction (delayed ejaculation, decreased libido)",
      "Fatigue"
    ],
    "serious_side_effects": [
      "Suicidal thoughts and behaviors in young adults/children (FDA Boxed Warning)",
      "Serotonin Syndrome (hyperthermia, rigidity, clonus, autonomic instability \u2014 medical emergency)",
      "Abnormal bleeding and ecchymosis",
      "Hyponatremia / SIADH (especially in elderly)",
      "Activation of mania in unrecognized bipolar disorder"
    ],
    "contraindications": [
      "Concomitant use of Monoamine Oxidase Inhibitors (MAOIs) or within 14 days of stopping MAOIs (fatal serotonin syndrome)",
      "Concomitant use of pimozide (cardiac arrhythmia risk)",
      "Known hypersensitivity to sertraline"
    ],
    "drug_interactions": [
      "MAOIs and Linezolid: Life-threatening Serotonin Syndrome (strictly contraindicated)",
      "Antiplatelets & NSAIDs: Multiplies upper gastrointestinal bleeding risk",
      "Triptans, Tramadol, St. John's Wort: Elevated serotonin syndrome risk",
      "Warfarin: Mild prolongation of prothrombin time"
    ],
    "food_alcohol_interactions": [
      "May be taken with or without meals once daily in the morning or evening. Strictly avoid alcohol due to compounded cognitive and psychomotor impairment."
    ],
    "allergy_precautions": "Discontinue if allergic rash, angioedema, or neuroleptic-like signs develop.",
    "age_precautions": {
      "children": "Approved in pediatric patients >= 6 years of age for OCD only. FDA Boxed Warning for suicidal thoughts in patients <= 24 years.",
      "older_adults": "High risk of SIADH and hyponatremia. Monitor serum sodium regularly."
    },
    "pregnancy_breastfeeding": "Category C. Antidepressant of choice during lactation (lowest infant serum concentrations among SSRIs). Weigh risks and benefits in pregnancy.",
    "kidney_liver_precautions": "No dose adjustments in renal impairment. Extensively metabolized by the liver; dose reduction or less frequent dosing required in hepatic impairment.",
    "monitoring_requirements": "Close monitoring for worsening depression, emergence of agitation, and suicidal ideation, especially during initial 1\u20132 months of therapy; serum sodium in elderly.",
    "precautions": [
      "FDA Boxed Warning for Suicidal Thoughts in Children and Young Adults",
      "Never discontinue abruptly (taper over several weeks to avoid antidepressant discontinuation syndrome)"
    ],
    "storage": "Store at 20\u00b0C to 25\u00b0C. Protect from moisture.",
    "dosage_forms": [
      "Film-Coated Tablet",
      "Oral Concentrate Solution (20 mg/mL)"
    ],
    "strengths": [
      "25 mg",
      "50 mg",
      "100 mg",
      "20 mg/mL oral liquid"
    ],
    "manufacturer": "Viatris / Pfizer / Sun Pharma / Lupin / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning and Prescribing Information",
      "APA Depression Guidelines",
      "NICE Guidelines",
      "DailyMed"
    ],
    "last_updated": "2026-08-20",
    "administration": "Take orally once daily in either the morning or evening, with or without food. Taking with food enhances peak absorption. Swallow tablet whole with water. Do not discontinue abruptly; taper gradually.",
    "overdose_guidance": "Overdose manifestations include serotonin syndrome, somnolence, gastrointestinal disturbance, tachycardia, tremor, and dizziness. Rarely, QT prolongation occurs. Primary management is supportive: secure airway, monitor cardiac rhythm, and manage serotonin syndrome with IV fluids, benzodiazepines, and cyproheptadine if indicated.",
    "slug": "sertraline"
  },
  {
    "name": "Ciprofloxacin",
    "brand_names": [
      "Cifran",
      "Ciplox",
      "Cipro",
      "Ciprolet",
      "Zoxan"
    ],
    "generic_name": "Ciprofloxacin hydrochloride",
    "active_ingredients": "Ciprofloxacin",
    "image": "",
    "category": "Antibacterial / Fluoroquinolone",
    "therapeutic_class": "Second-Generation Fluoroquinolone Antibacterial",
    "used_for": "Treatment of complicated urinary tract infections, acute pyelonephritis, infectious bacterial diarrhea, typhoid fever, complicated intra-abdominal infections, and bone and joint infections.",
    "prescribed_for": [
      "Complicated Urinary Tract Infections and Pyelonephritis",
      "Infectious Bacterial Diarrhea (Salmonella, Shigella, Campylobacter)",
      "Typhoid / Enteric Fever",
      "Pseudomonas Aeruginosa Susceptible Infections",
      "Prostatitis"
    ],
    "how_it_works": "Inhibits bacterial DNA gyrase (topoisomerase II) and topoisomerase IV, preventing DNA supercoiling, replication, and transcription, producing rapid concentration-dependent bacterial killing with potent Gram-negative activity.",
    "common_side_effects": [
      "Nausea and diarrhea",
      "Vomiting and abdominal discomfort",
      "Dizziness and headache",
      "Mild skin rash"
    ],
    "serious_side_effects": [
      "Tendonitis and tendon rupture (FDA Boxed Warning)",
      "Peripheral neuropathy and nerve damage (FDA Boxed Warning)",
      "Central nervous system toxicities (FDA Boxed Warning: seizures, psychosis)",
      "Cardiac QTc prolongation and arrhythmias",
      "Aortic aneurysm and dissection (FDA Warning)",
      "Exacerbation of myasthenia gravis (FDA Boxed Warning)"
    ],
    "contraindications": [
      "History of fluoroquinolone-induced tendon rupture",
      "Concomitant tizanidine administration (severe hypotension and sedation)",
      "Myasthenia gravis",
      "Known hypersensitivity to ciprofloxacin or quinolones"
    ],
    "drug_interactions": [
      "Multivalent Cations (Antacids with Al/Mg, Iron, Sucralfate, Calcium): Chelate ciprofloxacin, reducing absorption by up to 90% (space by 2 hours before or 6 hours after)",
      "Theophylline: Ciprofloxacin markedly inhibits CYP1A2, doubling theophylline levels and causing toxic seizures",
      "Warfarin: Potentiates anticoagulant effect"
    ],
    "food_alcohol_interactions": [
      "Do not take with dairy products (milk, yogurt) or calcium-fortified juice ALONE (chelation); however, taking with a complete meal containing dairy is acceptable."
    ],
    "allergy_precautions": "Discontinue immediately at first sign of skin rash, tendon pain, or neuropathy.",
    "age_precautions": {
      "children": "Generally not recommended in pediatric patients due to arthropathy, except for complicated UTI, pyelonephritis, or anthrax exposure.",
      "older_adults": "Severe vulnerability to Achilles tendon rupture and fatal cardiac arrhythmias. Reserve for situations where alternative antibiotics are unsuitable."
    },
    "pregnancy_breastfeeding": "Category C. Avoid in pregnancy and lactation due to potential cartilage damage in growing joints.",
    "kidney_liver_precautions": "Excreted renally; dose reduction required if eGFR < 50 mL/min: eGFR 30\u201350 mL/min (250\u2013500 mg q12h); eGFR < 30 mL/min (250\u2013500 mg q18h or 24h).",
    "monitoring_requirements": "Renal and hepatic function; immediate cessation upon any tendon pain, tenderness, or neurological numbness.",
    "precautions": [
      "FDA Boxed Warnings for Tendonitis, Neuropathy, CNS Toxicities, and Myasthenia Gravis",
      "Maintain vigorous fluid hydration to prevent crystalluria"
    ],
    "storage": "Store below 25\u00b0C. Protect from moisture.",
    "dosage_forms": [
      "Film-Coated Tablet",
      "Oral Suspension",
      "IV Infusion",
      "Ophthalmic / Otic Solution"
    ],
    "strengths": [
      "250 mg",
      "500 mg",
      "750 mg",
      "200 mg IV",
      "400 mg IV"
    ],
    "manufacturer": "Bayer / Sun Pharma / Cipla / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning & Prescribing Information",
      "IDSA Guidelines",
      "BNF",
      "DailyMed"
    ],
    "last_updated": "2026-08-22",
    "administration": "Take orally with plenty of fluids. May be taken with or without food, but do NOT take with dairy products (milk, yogurt) or calcium-fortified juices alone. Separate by at least 2 hours before or 6 hours after antacids, iron, or sucralfate.",
    "overdose_guidance": "Symptoms include dizziness, tremor, headache, fatigue, seizures, hallucinations, and renal crystalluria. Provide supportive measures, maintain adequate hydration and diuresis, and monitor renal function. Hemodialysis removes only ~10% of ciprofloxacin.",
    "slug": "ciprofloxacin"
  },
  {
    "name": "Levothyroxine",
    "brand_names": [
      "Thyronorm",
      "Eltroxin",
      "Synthroid",
      "Levoxyl",
      "Thyrox"
    ],
    "generic_name": "Levothyroxine sodium",
    "active_ingredients": "Levothyroxine sodium (synthetic T4)",
    "image": "",
    "category": "Endocrine / Thyroid Hormone Replacement",
    "therapeutic_class": "Synthetic Thyroid Hormone (T4)",
    "used_for": "Replacement therapy in congenital or acquired primary, secondary, and tertiary hypothyroidism; pituitary thyroid-stimulating hormone (TSH) suppression in the management of thyroid cancer.",
    "prescribed_for": [
      "Primary Hypothyroidism (Hashimoto's Thyroiditis)",
      "Post-Thyroidectomy or Radioiodine Hypothyroidism",
      "Congenital Hypothyroidism (Cretinism)",
      "Pituitary TSH Suppression in Well-Differentiated Thyroid Cancer"
    ],
    "how_it_works": "Synthetic crystalline L-tetraiodothyronine (T4) that identical to natural human thyroxine. Acts as a prohormone converted peripherally in liver and kidneys to triiodothyronine (T3), which enters the nucleus to bind thyroid hormone receptors, regulating transcription of metabolic genes, stimulating oxygen consumption, basal metabolic rate, protein synthesis, and lipid metabolism.",
    "common_side_effects": [
      "Side effects are virtually non-existent at precise therapeutic replacement doses",
      "Over-replacement signs: Palpitations, tachycardia, anxiety, heat intolerance, tremor, weight loss, insomnia"
    ],
    "serious_side_effects": [
      "Cardiac arrhythmias, atrial fibrillation, and myocardial infarction (especially in elderly with underlying ischemic heart disease)",
      "Bone mineral density reduction (osteoporosis from long-term subclinical hyperthyroidism)",
      "Thyrotoxic crisis / storm (with severe massive overdosage)"
    ],
    "contraindications": [
      "Untreated subclinical or overt thyrotoxicosis",
      "Acute uncorrected myocardial infarction",
      "Untreated adrenal cortical insufficiency (corticosteroid replacement must precede thyroid hormone initiation to prevent acute Addisonian crisis)"
    ],
    "drug_interactions": [
      "Calcium Carbonate, Iron Supplements, Sucralfate, Aluminum Antacids, Bile Acid Sequestrants: Drastically bind and inhibit levothyroxine absorption (space administration by at least 4 hours)",
      "Warfarin: Levothyroxine increases catabolism of vitamin K-dependent clotting factors, potentiating anticoagulant effect and bleeding risk",
      "Proton Pump Inhibitors: Reduce gastric acidity, lowering levothyroxine dissolution"
    ],
    "food_alcohol_interactions": [
      "CRITICAL INSTRUCTION: Must take on an empty stomach with a full glass of water, at least 30 to 60 minutes before breakfast or coffee. Dietary fiber, soy, and espresso coffee severely impede absorption."
    ],
    "allergy_precautions": "Formulation contains no animal protein; hypersensitivity to synthetic hormone is exceptionally rare.",
    "age_precautions": {
      "children": "Congenital hypothyroidism is an emergency: Immediate full replacement therapy is vital to prevent irreversible intellectual disability and growth stunting.",
      "older_adults": "Start low and go slow: Begin at 12.5\u201325 mcg once daily in elderly patients or those with coronary artery disease, titrating by 12.5\u201325 mcg every 6\u20138 weeks to avoid precipitating angina or fatal arrhythmias."
    },
    "pregnancy_breastfeeding": "Category A. Thyroid hormone requirements typically increase by 30\u201350% during pregnancy; monitor TSH every 4 weeks until stable to prevent miscarriage and fetal neurodevelopmental impairment. Completely compatible with breastfeeding.",
    "kidney_liver_precautions": "No dose adjustments for renal or hepatic impairment (monitored purely by serum TSH titration).",
    "monitoring_requirements": "Serum Thyroid Stimulating Hormone (TSH) and Free T4 measured 6 to 8 weeks after any dose adjustment, and annually once stabilized in therapeutic target range (typically 0.5\u20132.5 mIU/L).",
    "precautions": [
      "FDA Boxed Warning: Thyroid hormones must NOT be used for the treatment of obesity or weight loss (ineffective and potentially life-threatening)",
      "Narrow therapeutic index drug; do not switch brands without re-testing TSH"
    ],
    "storage": "Store between 20\u00b0C and 25\u00b0C. Protect from moisture and light.",
    "dosage_forms": [
      "Oral Tablet",
      "Oral Capsule (Tirosint)",
      "Lyophilized Powder for Injection"
    ],
    "strengths": [
      "25 mcg",
      "50 mcg",
      "75 mcg",
      "88 mcg",
      "100 mcg",
      "112 mcg",
      "125 mcg",
      "137 mcg",
      "150 mcg",
      "175 mcg",
      "200 mcg"
    ],
    "manufacturer": "AbbVie / Pfizer / GSK / Abbott / Generic manufacturers",
    "sources": [
      "FDA Boxed Warning & Prescribing Information",
      "ATA/AACE Hypothyroidism Guidelines",
      "NICE Guidelines",
      "DailyMed"
    ],
    "last_updated": "2026-08-14",
    "administration": "Take orally once daily on an empty stomach with a full glass of water, at least 30 to 60 minutes before breakfast. Do not take with coffee, soy, iron, or calcium supplements; space by at least 4 hours.",
    "overdose_guidance": "Symptoms are those of acute hyperthyroidism: tachycardia, arrhythmias, chest pain, anxiety, tremor, insomnia, fever, and diaphoresis. Treatment includes beta-blockers (propranolol) to control sympathetic hyperactivity and supportive measures.",
    "slug": "levothyroxine"
  },
  {
    "name": "Insulin (Human & Glargine)",
    "slug": "insulin",
    "brand_names": [
      "Lantus",
      "Basalog",
      "Novorapid",
      "Humalog",
      "Actrapid",
      "Mixtard",
      "Apidra",
      "Tresiba"
    ],
    "generic_name": "Insulin (Human Recombinant & Insulin Analogs)",
    "active_ingredients": "Human Insulin / Insulin Glargine / Insulin Lispro",
    "image": "/static/images/medicines/insulin.jpg",
    "category": "Antidiabetic Agent",
    "therapeutic_class": "Parenteral Hypoglycemic Hormone",
    "used_for": [
      "Glycemic control in patients with Type 1 Diabetes Mellitus",
      "Glycemic control in patients with Type 2 Diabetes Mellitus inadequate on oral agents",
      "Management of Diabetic Ketoacidosis (DKA) and Hyperosmolar Hyperglycemic State (HHS)",
      "Gestational Diabetes Mellitus requiring pharmacotherapy"
    ],
    "prescribed_for": [
      "Type 1 Diabetes Mellitus (absolute insulin deficiency)",
      "Type 2 Diabetes Mellitus with secondary oral hypoglycemic failure",
      "Diabetic emergencies requiring rapid glycemic normalization"
    ],
    "how_it_works": "Regulates glucose metabolism by binding to insulin receptors on muscle and adipose cells, facilitating cellular glucose uptake while simultaneously inhibiting hepatic glucose output, lipolysis, and proteolysis.",
    "dosage_forms": [
      "Subcutaneous Injection Pen (100 units/mL, 300 units/mL)",
      "Injection Vial (100 units/mL for U-100 syringe)",
      "Cartridge for pen injector"
    ],
    "strengths": [
      "100 IU/mL (U-100)",
      "300 IU/mL (U-300)",
      "Pre-filled Solostar / FlexPen 3 mL"
    ],
    "administration": "Administer subcutaneously into the abdomen, thigh, buttocks, or upper arm. Rotate injection sites within the same anatomical region to prevent lipodystrophy. Do not administer intravenously unless in an acute hospital intensive care setting with Regular Human Insulin. Long-acting basal insulins (Glargine) should be given once daily at the same time each day.",
    "common_side_effects": [
      "Mild hypoglycemia (tremors, sweating, palpitations, hunger, dizziness)",
      "Injection site reactions (erythema, localized mild discomfort)",
      "Lipohypertrophy or lipoatrophy with improper site rotation",
      "Mild peripheral edema upon glycemic initiation",
      "Weight gain associated with improved metabolic glycemic retention"
    ],
    "serious_side_effects": [
      "Severe hypoglycemia (neuroglycopenia, loss of consciousness, seizures)",
      "Severe systemic anaphylactic allergy (generalized rash, bronchospasm, angioedema)",
      "Severe hypokalemia, particularly with intravenous insulin infusion",
      "Hypoglycemic unawareness in longstanding autonomic diabetic neuropathy"
    ],
    "contraindications": [
      "Active episodes of hypoglycemia",
      "Known severe hypersensitivity to insulin or any formulation excipients"
    ],
    "drug_interactions": [
      "Beta-blockers: Mask tachycardia and adrenergic autonomic warning signs of hypoglycemia",
      "Oral antidiabetic agents (Sulfonylureas, Meglitinides): Synergistic hypoglycemic risk",
      "Systemic corticosteroids, thiazide diuretics: Reduce insulin sensitivity and elevate blood glucose",
      "Alcohol: Impairs gluconeogenesis and sharply accentuates hypoglycemia risk",
      "ACE inhibitors, Angiotensin receptor blockers: May occasionally enhance insulin sensitivity"
    ],
    "food_alcohol_interactions": [
      "Alcohol inhibits hepatic gluconeogenesis and significantly precipitates prolonged hypoglycemia; avoid acute or heavy consumption.",
      "Consistent carbohydrate distribution throughout daily meals is essential for predictable glycemic control."
    ],
    "allergy_precautions": [
      "Patients with known allergy to metacresol or other formulation preservatives must be evaluated.",
      "Local injection urticaria should be evaluated to differentiate from systemic IgE-mediated hypersensitivity."
    ],
    "age_precautions": [
      "Pediatric: Safe and essential for Type 1 diabetes; strict glycemic targets must be balanced against hypoglycemia risk in young children.",
      "Geriatric: Heightened vulnerability to unrecognized severe hypoglycemia, falls, and cardiovascular events; individualized, less stringent HbA1c targets (7.5% - 8.0%) recommended."
    ],
    "pregnancy_breastfeeding": "Category B. Insulin is the therapeutic gold standard for diabetes management in pregnancy (pre-existing and gestational diabetes); does not cross the placental barrier. Compatible with breastfeeding.",
    "kidney_liver_precautions": "Insulin requirements may decrease markedly in patients with renal impairment (reduced renal clearance of insulin) or hepatic impairment (reduced gluconeogenic capacity). Frequent blood glucose monitoring and dosage titration are mandated.",
    "storage": "Store unopened vials and pens refrigerated at 2\u00b0C to 8\u00b0C (36\u00b0F to 46\u00b0F). Do not freeze; discard if frozen. In-use vials or pens can be kept at room temperature below 30\u00b0C (86\u00b0F) protected from direct sunlight and heat, typically for up to 28 days.",
    "overdose_guidance": "Severe insulin overdose produces life-threatening neuroglycopenic hypoglycemia. If the patient is conscious, administer 15-20 grams of fast-acting oral carbohydrates (glucose tablets, fruit juice, sugar water). If unconscious, do not administer anything by mouth; immediately inject 1 mg Glucagon intramuscularly/subcutaneously, call emergency medical services (911 / 1066 / 112), and administer intravenous dextrose 25% or 50% upon EMS arrival.",
    "monitoring_requirements": [
      "Self-monitoring of blood glucose (SMBG) pre-prandial and post-prandial",
      "HbA1c testing every 3 months until target achieved, then every 6 months",
      "Periodic serum potassium testing during intensive insulin titration",
      "Visual inspection of injection sites for lipodystrophy at clinical visits"
    ],
    "precautions": [
      "Never share insulin pens or syringes between patients due to blood-borne pathogen transmission risk",
      "Always keep fast-acting oral carbohydrates or glucagon kit readily accessible",
      "Adjust dose during periods of acute infection, fever, trauma, or emotional stress"
    ],
    "manufacturer": "Sanofi-Aventis, Novo Nordisk, Eli Lilly, Biocon",
    "sources": [
      "American Diabetes Association (ADA) Standards of Medical Care in Diabetes 2024",
      "DailyMed / FDA Prescribing Information for Lantus & Humulin",
      "British National Formulary (BNF 86)",
      "WHO Model Formulary"
    ],
    "last_updated": "2024-11-15"
  },
  {
    "name": "Amoxicillin",
    "slug": "amoxicillin",
    "brand_names": [
      "Novamox",
      "Amoxil",
      "Mox",
      "Wymox",
      "Almox",
      "Moxikind"
    ],
    "generic_name": "Amoxicillin Trihydrate",
    "active_ingredients": "Amoxicillin Trihydrate",
    "image": "/static/images/medicines/amoxicillin.jpg",
    "category": "Antibiotic",
    "therapeutic_class": "Aminopenicillin Beta-Lactam Antibacterial",
    "used_for": [
      "Acute bacterial otitis media and sinusitis",
      "Streptococcal pharyngitis and tonsillitis",
      "Community-acquired pneumonia and lower respiratory infections",
      "Uncomplicated urinary tract infections (UTIs)",
      "Helicobacter pylori eradication (as part of triple therapy regimen)"
    ],
    "prescribed_for": [
      "Susceptible Gram-positive and select Gram-negative bacterial infections",
      "Dental abscesses and endodontic infections"
    ],
    "how_it_works": "Bactericidal agent that inhibits the synthesis of bacterial cell walls by binding to one or more penicillin-binding proteins (PBPs), leading to bacterial cell lysis and death.",
    "dosage_forms": [
      "Capsule",
      "Tablet",
      "Oral Suspension (dry powder for reconstitution)",
      "Chewable Tablet"
    ],
    "strengths": [
      "250 mg",
      "500 mg",
      "875 mg",
      "125 mg/5 mL suspension",
      "250 mg/5 mL suspension"
    ],
    "administration": "May be taken without regard to meals; taking with food may decrease gastrointestinal upset. Reconstituted oral suspension must be shaken vigorously before each dose and stored in refrigerator or room temperature as labeled. Complete the entire prescribed duration even if symptoms improve.",
    "common_side_effects": [
      "Diarrhea and loose stools",
      "Nausea and mild stomach discomfort",
      "Transient skin rash (maculopapular)",
      "Oral candidiasis (oral thrush)",
      "Headache"
    ],
    "serious_side_effects": [
      "Severe anaphylaxis (angioedema, bronchospasm, anaphylactic shock)",
      "Clostridioides difficile-associated diarrhea and pseudomembranous colitis",
      "Stevens-Johnson syndrome (SJS) and toxic epidermal necrolysis (TEN)",
      "Drug-induced liver injury with cholestatic jaundice"
    ],
    "contraindications": [
      "Documented history of severe allergic reaction (anaphylaxis, angioedema) to any penicillin or beta-lactam antibiotic"
    ],
    "drug_interactions": [
      "Probenecid: Decreases renal tubular secretion of amoxicillin, increasing blood concentrations",
      "Allopurinol: Concomitant administration substantially increases the risk of cutaneous drug rash",
      "Oral anticoagulants (Warfarin): May prolong prothrombin time / INR; monitor closely",
      "Methotrexate: Penicillins may decrease clearance of methotrexate, increasing toxicity"
    ],
    "food_alcohol_interactions": [
      "Amoxicillin absorption is unaffected by food; taking with light meals improves gastric tolerance.",
      "Moderate alcohol intake does not directly inactivate amoxicillin, but alcohol should be avoided during systemic bacterial infection."
    ],
    "allergy_precautions": [
      "Cross-sensitivity with other penicillins and cephalosporins (up to 5-10% cross-reactivity). Carefully investigate past allergic drug reactions."
    ],
    "age_precautions": [
      "Pediatric: Safe and widely used for bacterial infections; weight-based dosing (25-45 mg/kg/day or high-dose 80-90 mg/kg/day for otitis media) is strictly required.",
      "Geriatric: Monitor renal function because amoxicillin is substantially excreted by the kidneys; dosage adjustment may be necessary in moderate-to-severe renal impairment."
    ],
    "pregnancy_breastfeeding": "Category B. Considered safe and widely prescribed during pregnancy when clinically indicated. Excreted in breast milk in small amounts; generally compatible with nursing.",
    "kidney_liver_precautions": "Dosing interval must be extended in patients with severe renal impairment (GFR < 30 mL/min). Hepatic monitoring recommended during prolonged therapy.",
    "storage": "Store dry capsules and tablets between 20\u00b0C and 25\u00b0C (68\u00b0F to 77\u00b0F). Reconstituted oral suspension should ideally be refrigerated at 2\u00b0C to 8\u00b0C and discarded after 14 days.",
    "overdose_guidance": "Overdose is generally well tolerated but can cause severe gastrointestinal symptoms (nausea, vomiting, diarrhea) and renal crystalluria, potentially leading to acute oliguric renal failure. Maintain hydration and diuresis; hemodialysis effectively clears amoxicillin from circulation.",
    "monitoring_requirements": [
      "Resolution of clinical infection signs (fever, WBC, pain)",
      "Renal function and complete blood count during extended courses (>14 days)",
      "Stool monitoring if persistent watery diarrhea develops"
    ],
    "precautions": [
      "Do not prescribe amoxicillin to patients with suspected infectious mononucleosis (Epstein-Barr virus) due to high incidence of maculopapular rash.",
      "Complete full course to prevent bacterial resistance emergence."
    ],
    "manufacturer": "Cipla, Alkem, GSK, Sun Pharma, Teva",
    "sources": [
      "FDA DailyMed Prescribing Information for Amoxicillin",
      "NICE Clinical Guidelines for Respiratory Tract Infections",
      "British National Formulary (BNF 86)",
      "WHO Essential Medicines List"
    ],
    "last_updated": "2024-11-10"
  },
  {
    "name": "Diclofenac",
    "slug": "diclofenac",
    "brand_names": [
      "Voveran",
      "Voltaren",
      "Reactin",
      "Diclogel",
      "Zipsor",
      "Cataflam"
    ],
    "generic_name": "Diclofenac Sodium / Diclofenac Potassium",
    "active_ingredients": "Diclofenac Sodium",
    "image": "/static/images/medicines/diclofenac.jpg",
    "category": "Analgesic / Anti-inflammatory",
    "therapeutic_class": "Nonsteroidal Anti-inflammatory Drug (NSAID)",
    "used_for": [
      "Osteoarthritis, rheumatoid arthritis, and ankylosing spondylitis",
      "Acute musculoskeletal injuries, sprains, and back pain",
      "Post-operative surgical pain and acute gout attacks",
      "Severe dysmenorrhea and renal colic"
    ],
    "prescribed_for": [
      "Moderate to severe acute and chronic inflammatory pain disorders"
    ],
    "how_it_works": "Inhibits cyclooxygenase enzymes COX-1 and COX-2, leading to significant reduction in the biosynthesis of pro-inflammatory prostaglandins responsible for pain, edema, and hyperalgesia.",
    "dosage_forms": [
      "Enteric-coated Tablet",
      "Sustained-release Tablet",
      "Topical Gel (1%, 2%)",
      "Intramuscular Injection",
      "Ophthalmic Drops"
    ],
    "strengths": [
      "25 mg",
      "50 mg",
      "75 mg",
      "100 mg SR",
      "1% Gel"
    ],
    "administration": "Swallow tablets whole with a full glass of water. Do not crush, chew, or break enteric-coated tablets. Take with food or milk to minimize gastric mucosal irritation. Use the lowest effective dose for the shortest possible duration.",
    "common_side_effects": [
      "Dyspepsia, heartburn, and epigastric discomfort",
      "Nausea and abdominal cramps",
      "Headache and dizziness",
      "Fluid retention and mild peripheral edema",
      "Elevated liver transaminases (ALT/AST)"
    ],
    "serious_side_effects": [
      "Gastrointestinal ulceration, perforation, and acute upper GI hemorrhage (FDA Boxed Warning)",
      "Increased risk of serious cardiovascular thrombotic events, myocardial infarction, and stroke (FDA Boxed Warning)",
      "Acute kidney injury, interstitial nephritis, and renal papillary necrosis",
      "Hepatotoxicity including fulminant hepatitis and liver failure",
      "Severe bronchospasm in aspirin-sensitive asthmatic patients"
    ],
    "contraindications": [
      "Active peptic ulcer disease or gastrointestinal bleeding",
      "History of asthma, urticaria, or allergic reactions after taking aspirin or other NSAIDs",
      "Setting of coronary artery bypass graft (CABG) surgery",
      "Severe heart failure (NYHA Class II-IV)",
      "Severe hepatic or renal impairment"
    ],
    "drug_interactions": [
      "Anticoagulants (Warfarin, Heparin, DOACs): Substantially increases catastrophic GI bleeding risk",
      "Antiplatelet agents (Aspirin, Clopidogrel): Synergistic ulceration and hemorrhage risk",
      "ACE inhibitors, ARBs, Diuretics: Attenuates antihypertensive effect; increases acute kidney failure risk",
      "Lithium, Methotrexate: Increases serum levels and toxicities of both agents",
      "Corticosteroids: Multiplies risk of gastrointestinal mucosal ulceration"
    ],
    "food_alcohol_interactions": [
      "Always take with meals to reduce gastric irritation.",
      "Avoid alcohol: concurrent alcohol intake significantly elevates the risk of severe gastric mucosal erosion and GI bleeding."
    ],
    "allergy_precautions": [
      "Severe cross-reactivity with aspirin and other NSAIDs. Contraindicated in patients with aspirin-exacerbated respiratory disease (AERD) / Samter's triad."
    ],
    "age_precautions": [
      "Pediatric: Generally not recommended in children except under specialist pediatric rheumatology supervision.",
      "Geriatric: Elderly patients are at much higher risk for fatal gastrointestinal, renal, and cardiovascular adverse events; co-prescription of gastroprotective PPI is strongly advised."
    ],
    "pregnancy_breastfeeding": "Contraindicated in the third trimester of pregnancy (causes premature closure of fetal ductus arteriosus and persistent pulmonary hypertension). Avoid from 20 weeks onward due to oligohydramnios risk. Trace amounts in breast milk; consult physician.",
    "kidney_liver_precautions": "Contraindicated in advanced renal and hepatic disease. NSAID-induced prostaglandin inhibition decreases renal perfusion, precipitating renal decompensation in pre-existing renal disease or volume depletion.",
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from excessive heat and direct light.",
    "overdose_guidance": "Symptoms include lethargy, somnolence, nausea, vomiting, epigastric pain, GI hemorrhage, acute renal failure, and respiratory depression. Management is symptomatic and supportive. Administer activated charcoal within 1 hour of ingestion if conscious; hemodialysis is ineffective due to high protein binding (>99%).",
    "monitoring_requirements": [
      "Complete blood count (CBC) to screen for occult GI bleeding",
      "Serum creatinine, BUN, and electrolytes (potassium)",
      "Baseline and periodic liver enzyme testing (ALT, AST)",
      "Blood pressure monitoring upon initiation"
    ],
    "precautions": [
      "FDA Boxed Warning for Cardiovascular and Gastrointestinal Risks",
      "Use lowest effective dose for shortest duration required",
      "Prescribe alongside a proton pump inhibitor (PPI) in patients over 65 or with ulcer history"
    ],
    "manufacturer": "Novartis, Cipla, Sun Pharma, Dr. Reddy's",
    "sources": [
      "FDA DailyMed Prescribing Information for Voltaren",
      "European Medicines Agency (EMA) Safety Review on Diclofenac",
      "British National Formulary (BNF 86)",
      "WHO Model Formulary"
    ],
    "last_updated": "2024-11-01"
  },
  {
    "name": "Telmisartan",
    "slug": "telmisartan",
    "brand_names": [
      "Telma",
      "Micardis",
      "Telpres",
      "Arbitel",
      "Telsartan",
      "Creser"
    ],
    "generic_name": "Telmisartan",
    "active_ingredients": "Telmisartan",
    "image": "/static/images/medicines/telmisartan.jpg",
    "category": "Antihypertensive",
    "therapeutic_class": "Angiotensin II Receptor Blocker (ARB)",
    "used_for": [
      "Essential hypertension (high blood pressure) in adults",
      "Cardiovascular risk reduction in patients unable to take ACE inhibitors",
      "Diabetic nephropathy in hypertensive patients"
    ],
    "prescribed_for": [
      "Primary hypertension",
      "Prevention of cardiovascular morbidity in high-risk atherothrombotic patients"
    ],
    "how_it_works": "Selectively blocks the binding of angiotensin II to the AT1 receptor in vascular smooth muscle and the adrenal gland, resulting in vasodilation, reduced systemic vascular resistance, and decreased aldosterone secretion.",
    "dosage_forms": [
      "Oral Tablet"
    ],
    "strengths": [
      "20 mg",
      "40 mg",
      "80 mg"
    ],
    "administration": "Take once daily orally with or without food, preferably at the same time each morning. Swallow tablet whole with water. Do not remove tablet from blister package until immediately before administration because telmisartan is hygroscopic.",
    "common_side_effects": [
      "Dizziness and lightheadedness (especially upon standing)",
      "Back pain and sinus congestion",
      "Diarrhea and mild gastrointestinal disturbance",
      "Fatigue",
      "Mild hyperkalemia"
    ],
    "serious_side_effects": [
      "Fetal toxicity and neonatal death if used during pregnancy (FDA Boxed Warning)",
      "Severe symptomatic hypotension in volume-depleted or salt-depleted patients",
      "Hyperkalemia (serum potassium > 5.5 mEq/L), particularly in renal impairment",
      "Acute renal impairment / oliguria in patients with renal artery stenosis",
      "Angioedema (swelling of face, lips, tongue, or airway)"
    ],
    "contraindications": [
      "Pregnancy (FDA Boxed Warning: discontinued immediately upon pregnancy detection)",
      "Severe hepatic impairment or biliary obstructive disorders",
      "Concomitant use with aliskiren in patients with diabetes mellitus"
    ],
    "drug_interactions": [
      "Potassium-sparing diuretics, potassium supplements, salt substitutes: Substantial hyperkalemia risk",
      "NSAIDs (Ibuprofen, Diclofenac): Blunts antihypertensive efficacy and precipitates acute renal failure",
      "Lithium: Telmisartan reduces renal excretion of lithium, elevating lithium toxicity risk",
      "Other antihypertensive agents: Synergistic blood pressure reduction; monitor for postural hypotension"
    ],
    "food_alcohol_interactions": [
      "Avoid potassium-containing salt substitutes without physician approval.",
      "Alcohol accentuates vasodilatory blood pressure lowering, potentially triggering orthostatic syncope."
    ],
    "allergy_precautions": [
      "History of angioedema with ARBs or ACE inhibitors mandates extreme caution."
    ],
    "age_precautions": [
      "Pediatric: Safety and efficacy not established in pediatric patients under 18 years.",
      "Geriatric: Start at standard adult doses (40 mg); monitor renal function and orthostatic blood pressure."
    ],
    "pregnancy_breastfeeding": "Contraindicated in pregnancy (FDA Boxed Warning for Fetal Toxicity; can cause fetal oligohydramnios, skeletal hypoplasia, and neonatal death). Discontinue immediately if pregnancy is detected. Not recommended during breastfeeding.",
    "kidney_liver_precautions": "Telmisartan is almost exclusively eliminated via biliary excretion into feces; use with extreme caution in patients with hepatic impairment. In renal artery stenosis, ARBs can cause severe acute renal insufficiency.",
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from moisture; keep in original blister pack.",
    "overdose_guidance": "Most likely manifestations of overdose are hypotension, dizziness, and tachycardia or bradycardia. Treatment is supportive: place patient in supine position with elevated legs, administer intravenous normal saline for volume expansion. Telmisartan is not removed by hemodialysis.",
    "monitoring_requirements": [
      "Baseline and routine blood pressure monitoring",
      "Serum potassium level monitoring",
      "Serum creatinine and estimated GFR (eGFR)"
    ],
    "precautions": [
      "FDA Boxed Warning for Fetal Toxicity",
      "Correct hypovolemia or salt depletion prior to starting therapy to avoid precipitous hypotension",
      "Monitor serum potassium especially in patients with chronic kidney disease"
    ],
    "manufacturer": "Boehringer Ingelheim, Glenmark, Torrent, Sun Pharma",
    "sources": [
      "FDA DailyMed Prescribing Information for Micardis",
      "AHA/ACC Guideline for the Prevention and Management of High Blood Pressure",
      "British National Formulary (BNF 86)"
    ],
    "last_updated": "2024-11-12"
  },
  {
    "name": "Rosuvastatin",
    "slug": "rosuvastatin",
    "brand_names": [
      "Crestor",
      "Rosuvas",
      "Rozavel",
      "Novastat",
      "Turbovas",
      "Roseday"
    ],
    "generic_name": "Rosuvastatin Calcium",
    "active_ingredients": "Rosuvastatin Calcium",
    "image": "/static/images/medicines/rosuvastatin.jpg",
    "category": "Lipid-lowering Agent",
    "therapeutic_class": "HMG-CoA Reductase Inhibitor (High-Intensity Statin)",
    "used_for": [
      "Primary hyperlipidemia and mixed dyslipidemia",
      "Hypertriglyceridemia and primary dysbetalipoproteinemia",
      "Prevention of major cardiovascular events (myocardial infarction, stroke, revascularization)",
      "Slowing progression of coronary atherosclerosis"
    ],
    "prescribed_for": [
      "High cardiovascular risk individuals needing aggressive LDL cholesterol reduction"
    ],
    "how_it_works": "Competitively inhibits 3-hydroxy-3-methylglutaryl-coenzyme A (HMG-CoA) reductase, the rate-limiting enzyme in cholesterol biosynthesis, up-regulating hepatic LDL receptors and increasing catabolism of circulating LDL particles.",
    "dosage_forms": [
      "Oral Tablet"
    ],
    "strengths": [
      "5 mg",
      "10 mg",
      "20 mg",
      "40 mg"
    ],
    "administration": "Take once daily orally at any time of day, with or without food. Can be taken with meals if stomach upset occurs. Swallow tablet whole with a glass of water. Maintain a standard cholesterol-lowering diet during treatment.",
    "common_side_effects": [
      "Myalgia (muscle aches and tenderness without weakness)",
      "Headache and dizziness",
      "Abdominal pain and nausea",
      "Asthenia and fatigue",
      "Mild transaminase elevation"
    ],
    "serious_side_effects": [
      "Rhabdomyolysis with acute renal failure secondary to myoglobinuria",
      "Severe immune-mediated necrotizing myopathy (IMNM)",
      "Hepatotoxicity with jaundice and elevated liver enzymes > 3x ULN",
      "New-onset diabetes mellitus (modest elevation in HbA1c/fasting blood glucose)",
      "Pancreatitis"
    ],
    "contraindications": [
      "Active liver disease or unexplained persistent elevations in hepatic transaminases",
      "Pregnancy and nursing mothers",
      "Concomitant use with cyclosporine",
      "Known severe hypersensitivity to rosuvastatin"
    ],
    "drug_interactions": [
      "Cyclosporine: Increases rosuvastatin exposure 7-fold; contraindicated",
      "Gemfibrozil, Fenofibrate: Synergistic increase in myopathy and rhabdomyolysis risk; avoid gemfibrozil",
      "Antacids containing aluminum and magnesium hydroxide: Decreases rosuvastatin absorption; take 2 hours apart",
      "Protease inhibitors (Atazanavir, Lopinavir/Ritonavir): Significantly increases rosuvastatin levels",
      "Warfarin: May enhance anticoagulant effect; closely monitor INR"
    ],
    "food_alcohol_interactions": [
      "Alcohol consumption: Heavy or chronic alcohol use increases risk of statin-induced hepatotoxicity.",
      "Unlike some other statins, rosuvastatin metabolism does not depend heavily on CYP3A4, so grapefruit juice does not cause major interactions."
    ],
    "allergy_precautions": [
      "Evaluate past statin intolerance; discontinue if generalized rash or angioedema develops."
    ],
    "age_precautions": [
      "Pediatric: Approved down to age 7 in heterozygous familial hypercholesterolemia.",
      "Geriatric: Patients >= 65 years have higher risk for myopathy; consider starting at lower dose (5 mg)."
    ],
    "pregnancy_breastfeeding": "Contraindicated in pregnancy. Cholesterol is crucial for fetal development; statins may cause fetal harm. Rosuvastatin is excreted in human milk; nursing is contraindicated.",
    "kidney_liver_precautions": "In patients with severe renal impairment (CrCl < 30 mL/min/1.73m2) not on hemodialysis, initial dose should be 5 mg once daily, not to exceed 10 mg once daily. Contraindicated in active liver disease.",
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from moisture.",
    "overdose_guidance": "No specific antidote exists. In event of overdose, monitor liver function and serum creatine kinase (CK) levels. Institute supportive measures. Hemodialysis does not significantly enhance rosuvastatin clearance.",
    "monitoring_requirements": [
      "Lipid panel at 4 to 12 weeks after initiation or dose adjustment, then every 3 to 12 months",
      "Baseline liver function tests (ALT, AST, Total Bilirubin)",
      "Serum creatine kinase (CK) in patients reporting persistent muscle pain or weakness",
      "Fasting blood glucose or HbA1c periodically in patients with diabetes risk factors"
    ],
    "precautions": [
      "Instruct patients to promptly report unexplained muscle pain, tenderness, or weakness, especially if accompanied by malaise or dark tea-colored urine",
      "Asian patients have approximately 2-fold higher median exposure; consider 5 mg starting dose"
    ],
    "manufacturer": "AstraZeneca, Sun Pharma, Cipla, Torrent, Lupin",
    "sources": [
      "FDA DailyMed Prescribing Information for Crestor",
      "AHA/ACC Cholesterol Clinical Guidelines",
      "British National Formulary (BNF 86)",
      "WHO Essential Medicines List"
    ],
    "last_updated": "2024-11-05"
  },
  {
    "name": "Glimepiride",
    "slug": "glimepiride",
    "brand_names": [
      "Amaryl",
      "Glimy",
      "Zoryl",
      "Glypride",
      "G-Lim",
      "Diapride"
    ],
    "generic_name": "Glimepiride",
    "active_ingredients": "Glimepiride",
    "image": "/static/images/medicines/glimepiride.jpg",
    "category": "Antidiabetic Agent",
    "therapeutic_class": "Second-Generation Sulfonylurea",
    "used_for": [
      "Adjunct to diet and exercise to improve glycemic control in adults with Type 2 Diabetes Mellitus",
      "Combination therapy with Metformin or Insulin in Type 2 Diabetes"
    ],
    "prescribed_for": [
      "Type 2 Diabetes Mellitus with insufficient glycemic control on lifestyle and metformin"
    ],
    "how_it_works": "Stimulates insulin release from functioning pancreatic beta cells by binding to sulfonylurea receptors (SUR1) and closing ATP-sensitive potassium channels, resulting in beta-cell membrane depolarization and calcium-mediated insulin exocytosis.",
    "dosage_forms": [
      "Oral Tablet"
    ],
    "strengths": [
      "1 mg",
      "2 mg",
      "3 mg",
      "4 mg"
    ],
    "administration": "Take once daily orally with breakfast or the first main meal of the day. Do not skip meals after taking glimepiride. Swallow tablet with water.",
    "common_side_effects": [
      "Hypoglycemia (sweating, trembling, hunger, anxiety, palpitations)",
      "Dizziness and headache",
      "Nausea and upper abdominal fullness",
      "Mild weight gain",
      "Transient visual accommodation disturbance at therapy onset"
    ],
    "serious_side_effects": [
      "Severe prolonged hypoglycemia requiring hospital admission and IV glucose",
      "Hemolytic anemia in patients with glucose-6-phosphate dehydrogenase (G6PD) deficiency",
      "Cholestatic jaundice and hepatic impairment",
      "Thrombocytopenia, leukopenia, and agranulocytosis",
      "Severe cutaneous hypersensitivity (erythema multiforme, Stevens-Johnson syndrome)"
    ],
    "contraindications": [
      "Known hypersensitivity to glimepiride or other sulfonylureas/sulfonamides",
      "Type 1 Diabetes Mellitus (ineffective due to lack of endogenous beta-cells)",
      "Diabetic ketoacidosis (DKA)",
      "Severe hepatic or renal impairment"
    ],
    "drug_interactions": [
      "Other antidiabetic agents (Insulin, Metformin): Synergistic hypoglycemic effect",
      "NSAIDs, Salicylates, Sulfonamides: Displace sulfonylurea from protein binding, precipitating hypoglycemia",
      "Beta-blockers: Mask signs of hypoglycemia (tachycardia, tremor)",
      "Fluconazole and CYP2C9 inhibitors: Elevate glimepiride levels, triggering prolonged hypoglycemia",
      "Thiazide diuretics, Corticosteroids: Antagonize hypoglycemic efficacy"
    ],
    "food_alcohol_interactions": [
      "Must be taken with breakfast or first main meal. Skipping meals leads directly to severe hypoglycemia.",
      "Alcohol strongly potentiates hypoglycemic risk and may rarely produce a disulfiram-like reaction."
    ],
    "allergy_precautions": [
      "History of severe allergy to sulfonamide medications mandates caution due to potential structural cross-allergy."
    ],
    "age_precautions": [
      "Pediatric: Safety and effectiveness not established in pediatric patients.",
      "Geriatric: Elderly, debilitated, or malnourished patients are particularly susceptible to severe, prolonged hypoglycemic episodes; initiate at 1 mg daily and titrate conservatively."
    ],
    "pregnancy_breastfeeding": "Contraindicated in pregnancy. Prolonged severe hypoglycemia reported in neonates born to mothers receiving sulfonylureas at delivery. Insulin is preferred. Not recommended during breastfeeding.",
    "kidney_liver_precautions": "In patients with renal or hepatic impairment, glimepiride clearance is diminished, significantly increasing the duration and severity of hypoglycemia. Start at 1 mg daily with careful titration.",
    "storage": "Store below 25\u00b0C (77\u00b0F). Protect from moisture and excessive light.",
    "overdose_guidance": "Sulfonylurea overdose can cause severe, prolonged hypoglycemia persisting for 24 to 72 hours due to active metabolites. Hospitalization with continuous IV dextrose 10% infusion and frequent blood glucose checks is essential. Octreotide (somatostatin analog) may be required to suppress rebound insulin secretion.",
    "monitoring_requirements": [
      "Fasting and postprandial blood glucose self-monitoring",
      "HbA1c testing every 3 months",
      "Renal and hepatic function panels periodically",
      "Screening for G6PD deficiency if unexplained hemolytic anemia occurs"
    ],
    "precautions": [
      "Educate patient and family thoroughly on recognizing and treating early hypoglycemia symptoms",
      "Avoid skipping meals or engaging in prolonged unaccustomed heavy exercise without carbohydrate intake"
    ],
    "manufacturer": "Sanofi, Torrent, Intas, Cipla, Zydus",
    "sources": [
      "FDA DailyMed Prescribing Information for Amaryl",
      "ADA Standards of Medical Care in Diabetes 2024",
      "British National Formulary (BNF 86)"
    ],
    "last_updated": "2024-11-08"
  },
  {
    "name": "Famotidine",
    "slug": "famotidine",
    "brand_names": [
      "Pepcid",
      "Famocid",
      "Facid",
      "Topcid",
      "Pepfiz"
    ],
    "generic_name": "Famotidine",
    "active_ingredients": "Famotidine",
    "image": "/static/images/medicines/famotidine.jpg",
    "category": "Gastrointestinal Agent",
    "therapeutic_class": "Histamine H2-Receptor Antagonist (H2RA)",
    "used_for": [
      "Active duodenal ulcer and benign gastric ulcer treatment",
      "Gastroesophageal reflux disease (GERD) and acid indigestion / heartburn",
      "Pathological hypersecretory conditions (Zollinger-Ellison syndrome)",
      "Maintenance therapy for duodenal ulcer prevention"
    ],
    "prescribed_for": [
      "Acid-related gastric and esophageal disorders requiring rapid acid suppression"
    ],
    "how_it_works": "Competitively inhibits histamine at H2 receptors of gastric parietal cells, inhibiting basal and nocturnal gastric acid secretion as well as secretion stimulated by food, betazole, and pentagastrin.",
    "dosage_forms": [
      "Oral Tablet",
      "Oral Suspension",
      "Intravenous Injection"
    ],
    "strengths": [
      "10 mg",
      "20 mg",
      "40 mg"
    ],
    "administration": "Take orally with a glass of water. For heartburn prevention, take 15 to 60 minutes before consuming food or beverages that trigger symptoms. For ulcer or GERD treatment, take once daily at bedtime or twice daily as prescribed. May be taken with or without food.",
    "common_side_effects": [
      "Headache",
      "Dizziness",
      "Constipation or mild diarrhea",
      "Fatigue",
      "Dry mouth"
    ],
    "serious_side_effects": [
      "Central nervous system effects (confusion, delirium, hallucinations, agitation, seizures), especially in elderly or renally impaired patients",
      "Arrhythmias and QT prolongation (rare, associated with high IV doses in renal failure)",
      "Thrombocytopenia and leukopenia (very rare)",
      "Severe anaphylaxis and angioedema"
    ],
    "contraindications": [
      "Known severe hypersensitivity to famotidine or other H2-receptor antagonists"
    ],
    "drug_interactions": [
      "Medicines requiring gastric acidity for absorption (Ketoconazole, Itraconazole, Atazanavir, Cefditoren): Absorption markedly reduced",
      "Tizanidine: Minor increase in tizanidine exposure",
      "Sucralfate: Stagger doses by at least 2 hours to avoid binding interactions"
    ],
    "food_alcohol_interactions": [
      "Avoid spicy, high-fat, or acidic foods and late-night snacking that aggravate gastric acid reflux.",
      "Alcohol directly irritates the gastric mucosa and stimulates acid production; avoid during active ulcer treatment."
    ],
    "allergy_precautions": [
      "Cross-sensitivity with other H2-receptor antagonists (cimetidine, ranitidine) has been observed."
    ],
    "age_precautions": [
      "Pediatric: Safe and approved in pediatric patients for peptic ulcer and GERD with weight-based dosing.",
      "Geriatric: Elderly patients are at much higher risk for CNS side effects (confusion, disorientation); dose adjustment for age-related renal clearance reduction is mandatory."
    ],
    "pregnancy_breastfeeding": "Category B. Considered safe in pregnancy when clinically indicated. Excreted in human breast milk; evaluate clinical benefit versus infant exposure.",
    "kidney_liver_precautions": "Famotidine is primarily cleared by the kidneys. In moderate to severe renal impairment (CrCl < 50 mL/min), reduce dose by 50% or extend dosing interval to 36-48 hours to prevent severe CNS toxicities.",
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from moisture and excessive light.",
    "overdose_guidance": "Symptoms of overdose are similar to adverse reactions: CNS confusion, agitation, severe hypotension, and vomiting. Treatment is symptomatic and supportive. Hemodialysis is partially effective in clearing famotidine.",
    "monitoring_requirements": [
      "Renal function tests (eGFR, serum creatinine) in elderly or chronically ill patients",
      "Resolution of dyspeptic symptoms and gastrointestinal comfort",
      "Endoscopy evaluation if symptoms fail to improve or alarm symptoms (weight loss, dysphagia, hematemesis) occur"
    ],
    "precautions": [
      "Symptomatic response to famotidine does not preclude the presence of gastric malignancy",
      "Adjust dosage in renal impairment to avoid CNS neurotoxicity"
    ],
    "manufacturer": "Johnson & Johnson, Sun Pharma, Cipla, Alkem",
    "sources": [
      "FDA DailyMed Prescribing Information for Pepcid",
      "American Gastroenterological Association (AGA) Guidelines",
      "British National Formulary (BNF 86)"
    ],
    "last_updated": "2024-11-02"
  },
  {
    "name": "Dextromethorphan",
    "slug": "dextromethorphan",
    "brand_names": [
      "Benadryl DR",
      "Ascoril D",
      "Corex DX",
      "Delsym",
      "Robitussin",
      "Alex Cough Syrup"
    ],
    "generic_name": "Dextromethorphan Hydrobromide",
    "active_ingredients": "Dextromethorphan Hydrobromide",
    "image": "/static/images/medicines/dextromethorphan.jpg",
    "category": "Antitussive",
    "therapeutic_class": "Centrally Acting Cough Suppressant",
    "used_for": [
      "Temporary relief of nonproductive, dry, hacking cough caused by minor throat and bronchial irritation",
      "Upper respiratory tract viral infections (common cold, mild viral bronchitis)"
    ],
    "prescribed_for": [
      "Symptomatic suppression of non-productive dry cough"
    ],
    "how_it_works": "Acts centrally on the medullary cough center of the brainstem, elevating the cough threshold through non-opioid sigma-1 receptor agonism and NMDA receptor antagonism without impairing normal ciliary clearance.",
    "dosage_forms": [
      "Oral Syrup / Elixir",
      "Oral Lozenge",
      "Oral Capsule / Softgel"
    ],
    "strengths": [
      "10 mg/5 mL",
      "15 mg/5 mL",
      "30 mg extended-release / 5 mL",
      "15 mg capsule"
    ],
    "administration": "Measure liquid formulations accurately using a calibrated medical measuring cup or oral syringe, not a household spoon. Take with a full glass of water. May be taken with or without food. Do not exceed the maximum recommended daily dose.",
    "common_side_effects": [
      "Mild drowsiness and sedation",
      "Dizziness and lightheadedness",
      "Nausea and mild gastrointestinal upset",
      "Constipation",
      "Abdominal pain"
    ],
    "serious_side_effects": [
      "Serotonin Syndrome (hyperthermia, rigidity, myoclonus, autonomic instability, delirium) when combined with serotonergic drugs (MAOIs, SSRIs)",
      "Respiratory depression and severe CNS depression in extreme overdose",
      "Dissociative hallucinations and psychosis (dextromethorphan abuse / recreational intoxication)",
      "Severe allergic angioedema and anaphylaxis"
    ],
    "contraindications": [
      "Concurrent use or within 14 days of discontinuing a Monoamine Oxidase Inhibitor (MAOI)",
      "Known severe hypersensitivity to dextromethorphan",
      "Chronic productive cough with copious phlegm (suppressing productive cough impairs airway clearance in asthma/COPD)"
    ],
    "drug_interactions": [
      "MAOIs (Phenelzine, Selegiline, Linezolid): Severe, fatal serotonin syndrome and malignant hyperthermia; strictly contraindicated",
      "SSRIs, SNRIs (Fluoxetine, Paroxetine, Sertraline): Potent CYP2D6 inhibition elevates dextromethorphan levels and causes serotonin toxicity",
      "CNS depressants, Alcohol, Opioids: Additive sedation and psychomotor impairment"
    ],
    "food_alcohol_interactions": [
      "Avoid alcohol: concurrent alcohol intake multiplies sedation, dizziness, and motor impairment.",
      "Grapefruit juice inhibits CYP3A4 and modestly increases dextromethorphan bioavailability."
    ],
    "allergy_precautions": [
      "Check for excipients such as artificial dyes, sulfites, or aspartame in syrups and lozenges."
    ],
    "age_precautions": [
      "Pediatric: Contraindicated or not recommended in children under 4 years of age due to risk of fatal respiratory depression and lack of proven efficacy. Use pediatric-specific formulations in older children.",
      "Geriatric: Elderly individuals are more sensitive to sedative and anticholinergic-like CNS side effects; start at lower therapeutic range."
    ],
    "pregnancy_breastfeeding": "Category C. Animal studies show risk or data is limited. Use during pregnancy only if clearly needed. Small amounts may enter breast milk; use with caution while nursing.",
    "kidney_liver_precautions": "Metabolized extensively in the liver via CYP2D6 to dextrorphan. Use with caution in patients with hepatic impairment.",
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Do not freeze liquid formulations.",
    "overdose_guidance": "Massive overdose produces hyperexcitability, confusion, toxic psychosis, ataxia, respiratory depression, stupor, and coma. Naloxone (0.4 to 2 mg IV) is an effective antidote that can reverse dextromethorphan-induced CNS and respiratory depression. Provide supportive care and respiratory support.",
    "monitoring_requirements": [
      "Monitoring for persistent cough > 7 days or accompanying high fever, rash, or persistent headache",
      "Screening for signs of serotonin syndrome if patient takes psychiatric medications",
      "Screening for medication misuse or psychological dependence in adolescents and young adults"
    ],
    "precautions": [
      "Do not use for persistent or chronic cough associated with smoking, asthma, chronic bronchitis, or emphysema",
      "Never exceed recommended daily doses; risk of accidental overdose with combination cold medications"
    ],
    "manufacturer": "Reckitt Benckiser, Haleon, Glenmark, Cipla, Abbott",
    "sources": [
      "FDA DailyMed Labeling for Dextromethorphan",
      "American Academy of Pediatrics (AAP) Cough and Cold Policy",
      "British National Formulary (BNF 86)"
    ],
    "last_updated": "2024-11-04"
  },
  {
    "name": "Gabapentin",
    "slug": "gabapentin",
    "brand_names": [
      "Neurontin",
      "Gabapin",
      "Pentanerv",
      "Gralise",
      "Horizant",
      "Gabantin"
    ],
    "generic_name": "Gabapentin",
    "active_ingredients": "Gabapentin",
    "image": "/static/images/medicines/gabapentin.jpg",
    "category": "Neurological Agent",
    "therapeutic_class": "Gabapentinoid Anticonvulsant / Neuropathic Analgesic",
    "used_for": [
      "Postherpetic neuralgia (pain following shingles) in adults",
      "Adjunctive therapy in the treatment of partial-onset seizures in patients 3 years and older",
      "Diabetic peripheral neuropathy and fibromyalgia (widespread evidence-based clinical use)",
      "Restless legs syndrome (RLS)"
    ],
    "prescribed_for": [
      "Neuropathic nerve pain disorders and refractory focal epilepsy"
    ],
    "how_it_works": "Binds with high affinity to the alpha-2-delta auxiliary subunit of voltage-gated calcium channels in presynaptic neurons, reducing calcium influx and suppressing the release of excitatory neurotransmitters including glutamate, substance P, and norepinephrine.",
    "dosage_forms": [
      "Oral Capsule",
      "Oral Tablet",
      "Oral Solution (250 mg/5 mL)"
    ],
    "strengths": [
      "100 mg",
      "300 mg",
      "400 mg",
      "600 mg",
      "800 mg"
    ],
    "administration": "Take orally with or without food. Swallow capsules whole with a full glass of water. Do not crush or chew. When initiating therapy, titrate slowly according to physician schedule to minimize drowsiness. If dose is discontinued, taper gradually over at least 1 week to avoid withdrawal seizures.",
    "common_side_effects": [
      "Drowsiness, somnolence, and sedation",
      "Dizziness, ataxia, and unsteadiness",
      "Peripheral edema (swelling of ankles and feet)",
      "Fatigue and asthenia",
      "Weight gain and increased appetite"
    ],
    "serious_side_effects": [
      "Life-threatening respiratory depression, particularly when combined with opioids or in COPD (FDA Warning)",
      "Suicidal thoughts, behavior, and clinical depression worsening (FDA Warning)",
      "Drug Reaction with Eosinophilia and Systemic Symptoms (DRESS / Multi-organ hypersensitivity)",
      "Severe withdrawal seizures and delirium upon abrupt cessation",
      "Anaphylaxis and angioedema"
    ],
    "contraindications": [
      "Known severe hypersensitivity to gabapentin or formulation components"
    ],
    "drug_interactions": [
      "Opioid analgesics (Morphine, Oxycodone, Fentanyl): Synergistic respiratory depression and overdose death risk (FDA Warning)",
      "CNS depressants, Alcohol, Benzodiazepines: Severe additive sedation, falls, and motor impairment",
      "Antacids containing aluminum and magnesium: Reduce gabapentin bioavailability by ~20%; separate by at least 2 hours"
    ],
    "food_alcohol_interactions": [
      "Absorption is unaffected by food.",
      "Alcohol drastically amplifies sedation, dizziness, impaired reaction time, and respiratory depression risk; strictly avoid."
    ],
    "allergy_precautions": [
      "Discontinue immediately at first sign of rash, facial swelling, or lymphadenopathy."
    ],
    "age_precautions": [
      "Pediatric: Approved for partial seizures down to 3 years; higher incidence of emotional lability and hyperkinesia reported in children.",
      "Geriatric: Elderly patients frequently exhibit reduced renal clearance; clearance of gabapentin is directly proportional to creatinine clearance. Lower starting doses and careful titration are mandatory."
    ],
    "pregnancy_breastfeeding": "Category C. Crosses the placenta; risk of neonatal withdrawal symptoms. Use only if potential benefit justifies potential fetal risk. Secreted in breast milk; use with caution under medical supervision.",
    "kidney_liver_precautions": "Gabapentin is eliminated entirely unchanged by renal excretion and is not metabolized by the liver. Dosing must be strictly adjusted based on measured or estimated creatinine clearance (CrCl). In hemodialysis, supplemental maintenance doses are required.",
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from moisture.",
    "overdose_guidance": "Symptoms include double vision (diplopia), slurred speech, profound drowsiness, lethargy, diarrhea, and coma. Gabapentin can be effectively removed from systemic circulation by hemodialysis. Provide supportive respiratory care.",
    "monitoring_requirements": [
      "Baseline and routine serum creatinine and creatinine clearance calculations",
      "Screening for emergence of suicidal ideation, depression, or mood alterations",
      "Monitoring for respiratory depression when co-prescribed with opioids or sedatives",
      "Monitoring for signs of physical dependence and misuse"
    ],
    "precautions": [
      "FDA Warning regarding serious breathing difficulties in patients with respiratory risk factors or taking opioids",
      "Do not discontinue abruptly; taper gradually to prevent rebound seizures and severe agitation",
      "Do not drive or operate heavy machinery until full adaptation to sedative effects occurs"
    ],
    "manufacturer": "Pfizer, Sun Pharma, Intas, Torrent, Cipla",
    "sources": [
      "FDA DailyMed Prescribing Information for Neurontin",
      "American Academy of Neurology Guidelines for Neuropathic Pain",
      "British National Formulary (BNF 86)"
    ],
    "last_updated": "2024-11-14"
  },
  {
    "name": "Doxycycline",
    "slug": "doxycycline",
    "brand_names": [
      "Doxicip",
      "Vibramycin",
      "Minocycline",
      "Doxy-1",
      "Monodox",
      "Oracea"
    ],
    "generic_name": "Doxycycline Hyclate / Doxycycline Monohydrate",
    "active_ingredients": "Doxycycline Hyclate",
    "image": "/static/images/medicines/doxycycline.jpg",
    "category": "Antibiotic",
    "therapeutic_class": "Tetracycline-Class Broad-Spectrum Antibacterial",
    "used_for": [
      "Atypical community-acquired pneumonia and respiratory infections",
      "Tick-borne rickettsial diseases (Lyme disease, Rocky Mountain spotted fever)",
      "Moderate to severe acne vulgaris and rosacea",
      "Sexually transmitted infections (Chlamydia trachomatis, non-gonococcal urethritis)",
      "Malaria chemoprophylaxis in chloroquine-resistant regions"
    ],
    "prescribed_for": [
      "Susceptible Gram-positive, Gram-negative, atypical bacterial, and protozoal infections"
    ],
    "how_it_works": "Bacteriostatic agent that inhibits bacterial protein synthesis by reversibly binding to the 30S ribosomal subunit, preventing the accession of aminoacyl-tRNA to the ribosomal acceptor site.",
    "dosage_forms": [
      "Oral Capsule",
      "Oral Tablet",
      "Intravenous Infusion"
    ],
    "strengths": [
      "50 mg",
      "100 mg",
      "200 mg"
    ],
    "administration": "Swallow whole with a full glass of water (at least 200 mL). Administer while sitting upright or standing, and do NOT lie down for at least 30 to 60 minutes after taking to prevent severe pill-induced esophageal ulceration. Take with food or milk if gastrointestinal irritation occurs.",
    "common_side_effects": [
      "Nausea, vomiting, and epigastric burning",
      "Photosensitivity (exaggerated sunburn on sun-exposed skin)",
      "Diarrhea and loose stools",
      "Esophageal irritation and dysphagia",
      "Vaginal candidiasis (yeast infection)"
    ],
    "serious_side_effects": [
      "Severe esophageal ulceration and stricture",
      "Benign intracranial hypertension (pseudotumor cerebri) with headache and vision blurring",
      "Severe cutaneous adverse reactions (Stevens-Johnson syndrome, DRESS)",
      "Clostridioides difficile-associated colitis",
      "Permanent tooth discoloration and enamel hypoplasia during tooth development"
    ],
    "contraindications": [
      "Documented hypersensitivity to doxycycline or any tetracycline class antibiotic",
      "Pregnancy and lactation (except for life-threatening conditions like anthrax or RMSF)",
      "Children under 8 years of age (risk of permanent tooth staining, except short courses for life-threatening infections like Lyme/RMSF)"
    ],
    "drug_interactions": [
      "Antacids, iron supplements, calcium, magnesium, bismuth subsalicylate: Form insoluble chelates; separate by at least 2 to 3 hours",
      "Oral anticoagulants (Warfarin): Depresses plasma prothrombin activity; decrease anticoagulant dose if needed",
      "Penicillins: Tetracyclines may interfere with bactericidal action of penicillins; avoid concurrent use",
      "Barbiturates, Carbamazepine, Phenytoin: Accelerate metabolism of doxycycline, shortening half-life"
    ],
    "food_alcohol_interactions": [
      "Dairy products and calcium-fortified foods slightly reduce absorption; however, unlike older tetracyclines, doxycycline can still be taken with small meals to reduce severe nausea.",
      "Chronic alcohol consumption accelerates hepatic metabolism of doxycycline, reducing its half-life and efficacy."
    ],
    "allergy_precautions": [
      "Complete cross-allergenicity across all tetracycline-class antimicrobials."
    ],
    "age_precautions": [
      "Pediatric: Generally contraindicated in children younger than 8 years because of permanent tooth staining and enamel hypoplasia; permitted for short-duration life-threatening rickettsial infections.",
      "Geriatric: No dose reduction generally required; monitor for pill-induced esophagitis."
    ],
    "pregnancy_breastfeeding": "Category D. Contraindicated during pregnancy. Crosses placenta and deposits in fetal bones and teeth, causing permanent yellow-gray-brown discoloration and reversible retardation of skeletal development. Secreted in breast milk; avoid during nursing.",
    "kidney_liver_precautions": "Unlike older tetracyclines, doxycycline is primarily excreted via biliary and non-renal pathways; dosage adjustment is generally not required in renal failure. Use with caution in severe hepatic impairment.",
    "storage": "Store at 20\u00b0C to 25\u00b0C (68\u00b0F to 77\u00b0F). Protect from light and moisture.",
    "overdose_guidance": "Overdose causes nausea, anorexia, vomiting, dizziness, and diarrhea. Management is supportive. Dialysis does not alter serum half-life of doxycycline and is not beneficial.",
    "monitoring_requirements": [
      "Complete blood count, renal function, and hepatic function during prolonged therapy (>21 days)",
      "Immediate visual acuity examination if symptoms of pseudotumor cerebri (persistent headache, diplopia) appear",
      "Skin evaluation for photosensitivity rashes"
    ],
    "precautions": [
      "Advise patients to avoid excessive sunlight and UV light exposure; use broad-spectrum SPF 30+ sunscreen",
      "Always drink plenty of fluids and remain upright after swallowing to avoid severe esophageal damage",
      "Complete entire course to prevent antimicrobial resistance"
    ],
    "manufacturer": "Pfizer, Cipla, Alkem, Sun Pharma, Lupin",
    "sources": [
      "FDA DailyMed Prescribing Information for Vibramycin",
      "CDC Guidelines for Tick-Borne Diseases",
      "British National Formulary (BNF 86)",
      "WHO Model Formulary"
    ],
    "last_updated": "2024-11-06"
  },
  {
    "name": "Metronidazole",
    "slug": "metronidazole",
    "brand_names": [
      "Flagyl",
      "Metrogyl",
      "Aldazole",
      "Rozex",
      "Metron",
      "Aristogyl"
    ],
    "generic_name": "Metronidazole",
    "active_ingredients": "Metronidazole",
    "image": "/static/images/medicines/metronidazole.jpg",
    "category": "Antimicrobial / Antiprotozoal",
    "therapeutic_class": "Nitroimidazole Antibacterial and Antiprotozoal",
    "used_for": [
      "Anaerobic bacterial infections (intra-abdominal, pelvic, skin, bone, CNS)",
      "Amoebiasis (entamoeba histolytica dysentery and liver abscess)",
      "Giardiasis and Trichomoniasis (urogenital tract)",
      "Bacterial vaginosis and dental infections",
      "Clostridioides difficile infection and H. pylori combination therapy"
    ],
    "prescribed_for": [
      "Anaerobic bacterial and protozoal parasitic infections"
    ],
    "how_it_works": "Enters bacterial and protozoal cells where its nitro group is reduced by electron transport proteins (ferredoxin) to cytotoxic reactive intermediates that bind to and disrupt helical DNA structure, causing DNA strand breakage and rapid cell death.",
    "dosage_forms": [
      "Oral Tablet",
      "Intravenous Infusion",
      "Topical Gel / Cream",
      "Oral Suspension"
    ],
    "strengths": [
      "200 mg",
      "400 mg",
      "500 mg",
      "5 mg/mL IV (100 mL)",
      "1% Gel"
    ],
    "administration": "Take orally with or after food with a full glass of water. Swallow tablets whole; do not crush or chew due to intensely bitter taste. Complete full treatment course. Strictly abstain from all alcoholic beverages during treatment and for at least 48 to 72 hours following the final dose.",
    "common_side_effects": [
      "Unpleasant sharp metallic taste in mouth",
      "Nausea, anorexia, and epigastric discomfort",
      "Headache and dizziness",
      "Darkened or reddish-brown urine (harmless metabolite chromaturia)",
      "Fur-coated tongue and dry mouth"
    ],
    "serious_side_effects": [
      "Severe Disulfiram-like reaction (violent vomiting, flushing, tachycardia, hypotension) with alcohol ingestion",
      "Peripheral neuropathy (numbness, paresthesias) with prolonged therapy (FDA Warning)",
      "Encephalopathy, cerebellar toxicity (ataxia, dysarthria), and seizures (FDA Warning)",
      "Aseptic meningitis and severe CNS toxicity",
      "Severe hepatotoxicity in patients with Cockayne syndrome (FDA Boxed Warning)"
    ],
    "contraindications": [
      "Hypersensitivity to metronidazole or other nitroimidazole derivatives",
      "First trimester of pregnancy in trichomoniasis",
      "Cockayne syndrome (FDA Boxed Warning for fatal acute liver failure)",
      "Concurrent use of alcohol or products containing propylene glycol within 48 hours"
    ],
    "drug_interactions": [
      "Alcohol: Produces severe disulfiram-like ethanol reaction; strictly avoid",
      "Warfarin: Potently inhibits warfarin metabolism, significantly increasing INR and bleeding risk",
      "Lithium: Increases serum lithium concentrations, precipitating acute lithium toxicity",
      "Phenytoin, Phenobarbital: Induces CYP450 metabolism, accelerating metronidazole clearance",
      "Disulfiram: Concomitant use may precipitate acute psychosis and confusion"
    ],
    "food_alcohol_interactions": [
      "STRICT CONTRAINDICATION WITH ALCOHOL: Ingestion of even minute quantities of alcohol (including cough syrups or mouthwash) produces severe abdominal cramps, violent nausea, vomiting, facial flushing, headache, and palpitations.",
      "Taking with meals reduces gastrointestinal nausea."
    ],
    "allergy_precautions": [
      "Check for prior hypersensitivity to tinidazole, ornidazole, or secnidazole."
    ],
    "age_precautions": [
      "Pediatric: Safe and approved for amoebiasis, giardiasis, and anaerobic infections with weight-based dosing (30-50 mg/kg/day).",
      "Geriatric: Monitor for CNS neurotoxicity and ataxia; renal/hepatic excretion is prolonged in elderly patients."
    ],
    "pregnancy_breastfeeding": "Contraindicated during first trimester of pregnancy for trichomoniasis; use in second and third trimesters only for essential indications. Excreted in breast milk in concentrations comparable to maternal serum; consider pumping and discarding milk during and for 24 hours after dose.",
    "kidney_liver_precautions": "Metronidazole is extensively metabolized by the liver. In severe hepatic impairment (Child-Pugh C), reduce dose by 50% to prevent drug accumulation and CNS toxicity. In end-stage renal disease on hemodialysis, supplement dose after dialysis session.",
    "storage": "Store between 15\u00b0C and 25\u00b0C (59\u00b0F and 77\u00b0F). Protect from direct light.",
    "overdose_guidance": "Symptoms include severe nausea, vomiting, ataxia, and peripheral neurotoxicity. Treatment is supportive and symptomatic. Metronidazole and its metabolites are rapidly cleared by hemodialysis.",
    "monitoring_requirements": [
      "Neurological evaluation for paresthesias, numbness, or ataxia during extended therapy (>10 days)",
      "Complete blood count (differential) before and after prolonged treatment courses",
      "Prothrombin time / INR closely monitored in patients taking oral anticoagulants"
    ],
    "precautions": [
      "FDA Warning for Potential Carcinogenicity in animal studies; avoid unnecessary or prolonged use",
      "Warn patients explicitly regarding alcohol prohibition during and for 3 days post-treatment",
      "Discontinue therapy immediately if ataxia or peripheral neuropathy develops"
    ],
    "manufacturer": "Pfizer, J.B. Chemicals (Unique), Cipla, Sanofi",
    "sources": [
      "FDA DailyMed Prescribing Information for Flagyl",
      "CDC Sexually Transmitted Infections Treatment Guidelines",
      "British National Formulary (BNF 86)",
      "WHO Essential Medicines List"
    ],
    "last_updated": "2024-11-10"
  }
]


def get_db_connection(db_path=None):
    """Obtain a SQLite database connection with row factory."""
    path = db_path or DATABASE
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_medicine_table(db=None):
    """
    Initialize verified_medicines table and seed base clinical monographs.
    Idempotent: updates existing and inserts new entries.
    """
    close_at_end = False
    if db is None:
        db = get_db_connection()
        close_at_end = True
        
    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS verified_medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                generic_name TEXT NOT NULL,
                brand_names TEXT NOT NULL,
                active_ingredients TEXT NOT NULL,
                category TEXT NOT NULL,
                therapeutic_class TEXT NOT NULL,
                used_for TEXT NOT NULL,
                prescribed_for TEXT NOT NULL,
                how_it_works TEXT NOT NULL,
                dosage_forms TEXT NOT NULL,
                strengths TEXT NOT NULL,
                administration TEXT NOT NULL,
                common_side_effects TEXT NOT NULL,
                serious_side_effects TEXT NOT NULL,
                contraindications TEXT NOT NULL,
                drug_interactions TEXT NOT NULL,
                food_alcohol_interactions TEXT NOT NULL,
                allergy_precautions TEXT NOT NULL,
                age_precautions TEXT NOT NULL,
                pregnancy_breastfeeding TEXT NOT NULL,
                kidney_liver_precautions TEXT NOT NULL,
                storage TEXT NOT NULL,
                overdose_guidance TEXT NOT NULL,
                monitoring_requirements TEXT NOT NULL,
                precautions TEXT NOT NULL,
                manufacturer TEXT,
                image TEXT,
                sources TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                is_external INTEGER DEFAULT 0
            );
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_vm_slug ON verified_medicines(slug);")
        db.execute("CREATE INDEX IF NOT EXISTS idx_vm_generic ON verified_medicines(generic_name);")
        db.execute("CREATE INDEX IF NOT EXISTS idx_vm_category ON verified_medicines(category);")
        db.commit()

        # Seed or refresh base medicines
        for med in BASE_MEDICINES_DATA:
            db.execute("""
                INSERT INTO verified_medicines (
                    name, slug, generic_name, brand_names, active_ingredients,
                    category, therapeutic_class, used_for, prescribed_for, how_it_works,
                    dosage_forms, strengths, administration, common_side_effects, serious_side_effects,
                    contraindications, drug_interactions, food_alcohol_interactions, allergy_precautions, age_precautions,
                    pregnancy_breastfeeding, kidney_liver_precautions, storage, overdose_guidance, monitoring_requirements,
                    precautions, manufacturer, image, sources, last_updated, is_external
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(name) DO UPDATE SET
                    slug = excluded.slug,
                    generic_name = excluded.generic_name,
                    brand_names = excluded.brand_names,
                    active_ingredients = excluded.active_ingredients,
                    category = excluded.category,
                    therapeutic_class = excluded.therapeutic_class,
                    used_for = excluded.used_for,
                    prescribed_for = excluded.prescribed_for,
                    how_it_works = excluded.how_it_works,
                    dosage_forms = excluded.dosage_forms,
                    strengths = excluded.strengths,
                    administration = excluded.administration,
                    common_side_effects = excluded.common_side_effects,
                    serious_side_effects = excluded.serious_side_effects,
                    contraindications = excluded.contraindications,
                    drug_interactions = excluded.drug_interactions,
                    food_alcohol_interactions = excluded.food_alcohol_interactions,
                    allergy_precautions = excluded.allergy_precautions,
                    age_precautions = excluded.age_precautions,
                    pregnancy_breastfeeding = excluded.pregnancy_breastfeeding,
                    kidney_liver_precautions = excluded.kidney_liver_precautions,
                    storage = excluded.storage,
                    overdose_guidance = excluded.overdose_guidance,
                    monitoring_requirements = excluded.monitoring_requirements,
                    precautions = excluded.precautions,
                    manufacturer = excluded.manufacturer,
                    image = excluded.image,
                    sources = excluded.sources,
                    last_updated = excluded.last_updated;
            """, (
                med["name"],
                med["slug"],
                med["generic_name"],
                json.dumps(med.get("brand_names", [])),
                med.get("active_ingredients", med["generic_name"]),
                med.get("category", "Prescription Pharmaceutical"),
                med.get("therapeutic_class", "Therapeutic Agent"),
                json.dumps(med.get("used_for", [])),
                json.dumps(med.get("prescribed_for", [])),
                med.get("how_it_works", ""),
                json.dumps(med.get("dosage_forms", [])),
                json.dumps(med.get("strengths", [])),
                med.get("administration", "Take as directed by physician."),
                json.dumps(med.get("common_side_effects", [])),
                json.dumps(med.get("serious_side_effects", [])),
                json.dumps(med.get("contraindications", [])),
                json.dumps(med.get("drug_interactions", [])),
                json.dumps(med.get("food_alcohol_interactions", [])),
                json.dumps(med.get("allergy_precautions", [])),
                json.dumps(med.get("age_precautions", [])),
                med.get("pregnancy_breastfeeding", ""),
                med.get("kidney_liver_precautions", ""),
                med.get("storage", "Store at controlled room temperature."),
                med.get("overdose_guidance", "Seek immediate emergency medical care."),
                json.dumps(med.get("monitoring_requirements", [])),
                json.dumps(med.get("precautions", [])),
                med.get("manufacturer", "Verified Pharmaceutical Manufacturer"),
                med.get("image", "/static/images/medicines/default.jpg"),
                json.dumps(med.get("sources", ["DailyMed / FDA", "British National Formulary"])),
                med.get("last_updated", "2024-11-15")
            ))
        db.commit()
    finally:
        if close_at_end:
            db.close()

def deserialize_medicine_row(row):
    """Convert SQLite Row into clean python dictionary with JSON fields unpacked."""
    if not row:
        return None
    d = dict(row)
    json_keys = [
        "brand_names", "used_for", "prescribed_for", "dosage_forms", "strengths",
        "common_side_effects", "serious_side_effects", "contraindications",
        "drug_interactions", "food_alcohol_interactions", "allergy_precautions",
        "age_precautions", "monitoring_requirements", "precautions", "sources"
    ]
    for k in json_keys:
        if k in d and isinstance(d[k], str):
            try:
                d[k] = json.loads(d[k])
            except Exception:
                d[k] = [d[k]] if d[k] else []
    return d

def get_medicine_by_slug_or_id(ident, db=None):
    """Retrieve complete 22-field medicine record by slug, id, or name."""
    close_at_end = False
    if db is None:
        db = get_db_connection()
        close_at_end = True
    try:
        ident_str = str(ident).strip()
        # Try ID if integer
        if ident_str.isdigit():
            row = db.execute("SELECT * FROM verified_medicines WHERE id = ?", (int(ident_str),)).fetchone()
            if row:
                return deserialize_medicine_row(row)
        
        # Try slug
        row = db.execute("SELECT * FROM verified_medicines WHERE slug = ?", (ident_str.lower(),)).fetchone()
        if row:
            return deserialize_medicine_row(row)
            
        # Try exact name or generic name
        row = db.execute("SELECT * FROM verified_medicines WHERE LOWER(name) = ? OR LOWER(generic_name) = ?", (ident_str.lower(), ident_str.lower())).fetchone()
        if row:
            return deserialize_medicine_row(row)
            
        # Try checking brand names JSON string
        row = db.execute("SELECT * FROM verified_medicines WHERE brand_names LIKE ? LIMIT 1", (f'%"{ident_str}"%',)).fetchone()
        if row:
            return deserialize_medicine_row(row)
            
        return None
    finally:
        if close_at_end:
            db.close()

def get_all_categories(db=None):
    """Retrieve distinct medicine categories for filtering."""
    close_at_end = False
    if db is None:
        db = get_db_connection()
        close_at_end = True
    try:
        rows = db.execute("SELECT DISTINCT category FROM verified_medicines WHERE category != '' ORDER BY category").fetchall()
        return [r["category"] for r in rows]
    finally:
        if close_at_end:
            db.close()

def search_medicines_db(query="", category=None, page=1, per_page=9, db=None):
    """
    Search medicines in database.
    Separates results into:
    - generic_matches (matching generic name, active ingredients)
    - brand_matches (matching verified brand names)
    - all_matches (combined deduplicated list)
    Supports category filtering and pagination.
    """
    close_at_end = False
    if db is None:
        db = get_db_connection()
        close_at_end = True
    try:
        clean_q = (query or "").strip().lower()
        cat_filter = (category or "").strip()
        
        # Fetch candidate rows
        if cat_filter and cat_filter != "All":
            rows = db.execute("SELECT * FROM verified_medicines WHERE category = ? ORDER BY name ASC", (cat_filter,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM verified_medicines ORDER BY name ASC").fetchall()
            
        all_meds = [deserialize_medicine_row(r) for r in rows]
        
        if not clean_q:
            # Empty query: return all medicines within category
            total_count = len(all_meds)
            total_pages = max(1, math.ceil(total_count / per_page))
            current_page = min(max(1, page), total_pages)
            start_idx = (current_page - 1) * per_page
            page_items = all_meds[start_idx:start_idx + per_page]
            
            return {
                "found": total_count > 0,
                "query": "",
                "category": cat_filter,
                "generic_matches": all_meds,
                "brand_matches": [],
                "all_matches": all_meds,
                "page_items": page_items,
                "total_count": total_count,
                "page": current_page,
                "per_page": per_page,
                "total_pages": total_pages,
                "categories": get_all_categories(db),
                "suggestions": []
            }

        # Query provided: partition matches into Generics vs Brands
        generic_matches = []
        brand_matches = []
        
        for m in all_meds:
            is_generic_match = False
            is_brand_match = False
            
            # Check name or generic name
            if clean_q in m["name"].lower() or clean_q in m["generic_name"].lower():
                is_generic_match = True
            elif clean_q in m.get("active_ingredients", "").lower():
                is_generic_match = True
                
            # Check brand names
            matching_brands = [b for b in m.get("brand_names", []) if clean_q in b.lower()]
            if matching_brands:
                is_brand_match = True
                
            # Check therapeutic class or category
            if not is_generic_match and not is_brand_match:
                if clean_q in m["category"].lower() or clean_q in m["therapeutic_class"].lower():
                    is_generic_match = True
                    
            if is_generic_match:
                generic_matches.append(m)
            elif is_brand_match:
                # Add a helper attribute for template displaying which brand matched
                m_copy = dict(m)
                m_copy["matched_brand"] = matching_brands[0] if matching_brands else m["brand_names"][0]
                brand_matches.append(m_copy)

        # Combined unique list (generics first, then brands)
        seen_ids = set()
        all_matches = []
        for m in generic_matches + brand_matches:
            if m["id"] not in seen_ids:
                seen_ids.add(m["id"])
                all_matches.append(m)
                
        total_count = len(all_matches)
        total_pages = max(1, math.ceil(total_count / per_page)) if total_count > 0 else 1
        current_page = min(max(1, page), total_pages)
        start_idx = (current_page - 1) * per_page
        page_items = all_matches[start_idx:start_idx + per_page]
        
        suggestions = []
        if total_count == 0:
            suggestions = get_spelling_suggestions(clean_q, db=db)
            
        return {
            "found": total_count > 0,
            "query": query,
            "category": cat_filter,
            "generic_matches": generic_matches,
            "brand_matches": brand_matches,
            "all_matches": all_matches,
            "page_items": page_items,
            "total_count": total_count,
            "page": current_page,
            "per_page": per_page,
            "total_pages": total_pages,
            "categories": get_all_categories(db),
            "suggestions": suggestions
        }
    finally:
        if close_at_end:
            db.close()

def get_autocomplete(query, db=None, limit=12):
    """
    Fast typeahead autocomplete returning generic and brand matches.
    """
    clean_q = (query or "").strip().lower()
    if not clean_q or len(clean_q) < 2:
        return []
        
    close_at_end = False
    if db is None:
        db = get_db_connection()
        close_at_end = True
    try:
        rows = db.execute("SELECT id, name, slug, generic_name, brand_names, category, active_ingredients FROM verified_medicines").fetchall()
        results = []
        seen = set()
        
        for r in rows:
            name = r["name"]
            gen_name = r["generic_name"]
            brands = json.loads(r["brand_names"]) if r["brand_names"] else []
            slug = r["slug"]
            cat = r["category"]
            
            # Check generic match
            if clean_q in name.lower() or clean_q in gen_name.lower():
                key = f"gen_{slug}"
                if key not in seen:
                    seen.add(key)
                    results.append({
                        "label": f"{gen_name} (Generic)",
                        "name": name,
                        "generic_name": gen_name,
                        "brand_names": brands[:3],
                        "category": cat,
                        "slug": slug,
                        "type": "generic"
                    })
                    
            # Check brand match
            for b in brands:
                if clean_q in b.lower():
                    key = f"brand_{b.lower()}"
                    if key not in seen:
                        seen.add(key)
                        results.append({
                            "label": f"{b} (Brand of {gen_name})",
                            "name": b,
                            "generic_name": gen_name,
                            "brand_names": [b],
                            "category": cat,
                            "slug": slug,
                            "type": "brand"
                        })
                        
            if len(results) >= limit:
                break
                
        return results[:limit]
    finally:
        if close_at_end:
            db.close()

def get_spelling_suggestions(query, db=None, limit=3):
    """Generate spelling suggestions from registered names, generics, and brands."""
    clean_q = (query or "").strip().lower()
    if not clean_q or len(clean_q) < 3:
        return []
        
    close_at_end = False
    if db is None:
        db = get_db_connection()
        close_at_end = True
    try:
        rows = db.execute("SELECT name, generic_name, brand_names FROM verified_medicines").fetchall()
        candidates = set()
        for r in rows:
            candidates.add(r["name"])
            candidates.add(r["generic_name"])
            if r["brand_names"]:
                try:
                    for b in json.loads(r["brand_names"]):
                        candidates.add(b)
                except Exception:
                    pass
        matches = difflib.get_close_matches(clean_q, list(candidates), n=limit, cutoff=0.55)
        return matches
    finally:
        if close_at_end:
            db.close()

def clean_fda_field(field_val):
    """Normalize and format text extracted from openFDA label fields."""
    if not field_val:
        return ""
    if isinstance(field_val, list):
        field_val = " ".join(field_val)
    text = re.sub(r'\[.*?\]', '', str(field_val))
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:900]

def fetch_and_store_external(query, db=None):
    """
    Query openFDA Drug Label API dynamically for any unlisted medicine.
    If valid FDA drug monograph found, assemble all 22 required fields,
    store into SQLite verified_medicines to avoid future roundtrips,
    and return the structured dictionary.
    """
    clean_q = (query or "").strip()
    if not clean_q or len(clean_q) < 3:
        return None
        
    # Check if network available and query openFDA
    q_enc = urllib.parse.quote(f'"{clean_q}"')
    url = f'https://api.fda.gov/drug/label.json?search=(openfda.generic_name:{q_enc}+openfda.brand_name:{q_enc}+openfda.substance_name:{q_enc})&limit=1'
    
    data = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VaidyaraMedicineSystem/2.0"})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        # Fallback to wildcard prefix search
        q_simple = urllib.parse.quote(clean_q.split()[0])
        url2 = f'https://api.fda.gov/drug/label.json?search=(openfda.brand_name:{q_simple}*+openfda.generic_name:{q_simple}*)&limit=1'
        try:
            req = urllib.request.Request(url2, headers={"User-Agent": "VaidyaraMedicineSystem/2.0"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None
            
    if not data or not data.get("results"):
        return None
        
    res = data["results"][0]
    ofda = res.get("openfda", {})
    
    brand_names = ofda.get("brand_name", [])
    generic_name = ofda.get("generic_name", [clean_q.title()])[0] if ofda.get("generic_name") else clean_q.title()
    name = brand_names[0] if brand_names else generic_name
    slug = re.sub(r'[^a-z0-9_]', '', name.lower().replace(" ", "_"))
    
    # Check if already exists in DB
    existing = get_medicine_by_slug_or_id(slug, db=db)
    if existing:
        return existing
        
    # Extract clinical fields
    active_ing = clean_fda_field(res.get("active_ingredient") or res.get("substance_name")) or generic_name
    category = clean_fda_field(ofda.get("pharm_class_epc") or ofda.get("pharm_class_moa")) or "Prescription Pharmaceutical / Therapeutic Agent"
    therapeutic_class = clean_fda_field(ofda.get("pharm_class_cs")) or category
    
    used_for_raw = clean_fda_field(res.get("indications_and_usage") or res.get("purpose")) or "Prescribed for conditions authorized under official drug regulatory approval."
    used_for = [u.strip() for u in re.split(r'[;\.\n]', used_for_raw) if len(u.strip()) > 10][:4]
    if not used_for:
        used_for = [used_for_raw[:200]]
        
    prescribed_for = used_for[:3]
    how_it_works = clean_fda_field(res.get("mechanism_of_action") or res.get("clinical_pharmacology")) or "Pharmacological mechanism documented in official FDA label monograph."
    
    dosage_forms = ofda.get("dosage_form", ["Tablet / Capsule / Injection"])
    strengths = ["Refer to packaging label for approved strengths"]
    
    admin_raw = clean_fda_field(res.get("dosage_and_administration")) or "Administer strictly in accordance with prescription labeling and medical directions."
    administration = admin_raw[:400]
    
    side_effects_raw = clean_fda_field(res.get("adverse_reactions"))
    common_side_effects = [s.strip() for s in re.split(r'[;•\n\.]', side_effects_raw) if len(s.strip()) > 5][:5] if side_effects_raw else ["Refer to official product label for reported adverse events."]
    
    warnings_raw = clean_fda_field(res.get("warnings_and_cautions") or res.get("boxed_warning")) or "Use with clinical caution. Consult treating physician."
    serious_side_effects = [w.strip() for w in re.split(r'[;•\n\.]', warnings_raw) if len(w.strip()) > 10][:4] if warnings_raw else ["Promptly report any acute adverse reactions to your doctor."]
    
    contraindications_raw = clean_fda_field(res.get("contraindications")) or "Documented hypersensitivity to this active pharmaceutical substance or any formulation excipients."
    contraindications = [c.strip() for c in re.split(r'[;•\n\.]', contraindications_raw) if len(c.strip()) > 10][:3] if contraindications_raw else [contraindications_raw]
    
    interactions_raw = clean_fda_field(res.get("drug_interactions")) or "Review concurrent medications with a pharmacist or physician before co-administration."
    drug_interactions = [d.strip() for d in re.split(r'[;•\n\.]', interactions_raw) if len(d.strip()) > 10][:4] if interactions_raw else [interactions_raw]
    
    food_alcohol = [
        "Consult medical provider regarding specific dietary or alcohol restrictions for this medication.",
        "Alcohol should be avoided during active therapeutic treatment unless explicitly cleared by doctor."
    ]
    
    allergy_precautions = [
        "Contraindicated in individuals with verified severe hypersensitivity to active substance.",
        "Discontinue immediately if cutaneous rash, urticaria, facial edema, or respiratory difficulty occurs."
    ]
    
    ped_raw = clean_fda_field(res.get("pediatric_use")) or "Safety and effectiveness in pediatric patients must be evaluated by a pediatrician."
    ger_raw = clean_fda_field(res.get("geriatric_use")) or "Elderly patients should be initiated with cautious dosage titration."
    age_precautions = [f"Pediatric: {ped_raw[:150]}", f"Geriatric: {ger_raw[:150]}"]
    
    preg_raw = clean_fda_field(res.get("pregnancy") or res.get("nursing_mothers")) or "Use during pregnancy or lactation only if potential benefit justifies potential risk to fetus/infant."
    pregnancy_breastfeeding = preg_raw[:300]
    
    kidney_liver = "Hepatic or renal impairment may necessitate dosage adjustment or therapeutic drug monitoring. Consult prescribing clinician."
    
    storage_raw = clean_fda_field(res.get("storage_and_handling")) or "Store at controlled room temperature 20°C to 25°C (68°F to 77°F). Protect from excessive moisture and heat."
    storage = storage_raw[:250]
    
    overdose_raw = clean_fda_field(res.get("overdosage")) or "In case of acute overdose, immediately contact regional poison control or emergency medical services. Provide supportive care."
    overdose_guidance = overdose_raw[:350]
    
    monitoring_requirements = [
        "Periodic clinical assessment of therapeutic response and tolerance",
        "Routine laboratory monitoring as determined by the treating clinician"
    ]
    
    precautions = [
        "Follow prescribed dosage instructions strictly",
        "Keep out of reach of children"
    ]
    
    manufacturer = ofda.get("manufacturer_name", ["Authorized Pharmaceutical Manufacturer"])[0]
    sources = ["U.S. Food and Drug Administration (FDA) Drug Label Database (openFDA)", "DailyMed National Library of Medicine"]
    last_updated = datetime.now().strftime("%Y-%m-%d")
    
    # Store into SQLite database
    close_at_end = False
    if db is None:
        db = get_db_connection()
        close_at_end = True
    try:
        db.execute("""
            INSERT OR REPLACE INTO verified_medicines (
                name, slug, generic_name, brand_names, active_ingredients,
                category, therapeutic_class, used_for, prescribed_for, how_it_works,
                dosage_forms, strengths, administration, common_side_effects, serious_side_effects,
                contraindications, drug_interactions, food_alcohol_interactions, allergy_precautions, age_precautions,
                pregnancy_breastfeeding, kidney_liver_precautions, storage, overdose_guidance, monitoring_requirements,
                precautions, manufacturer, image, sources, last_updated, is_external
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            name, slug, generic_name, json.dumps(brand_names), active_ing,
            category, therapeutic_class, json.dumps(used_for), json.dumps(prescribed_for), how_it_works,
            json.dumps(dosage_forms), json.dumps(strengths), administration, json.dumps(common_side_effects),
            json.dumps(serious_side_effects), json.dumps(contraindications), json.dumps(drug_interactions),
            json.dumps(food_alcohol), json.dumps(allergy_precautions), json.dumps(age_precautions),
            pregnancy_breastfeeding, kidney_liver, storage, overdose_guidance, json.dumps(monitoring_requirements),
            json.dumps(precautions), manufacturer, "/static/images/medicines/default.jpg",
            json.dumps(sources), last_updated
        ))
        db.commit()
    finally:
        if close_at_end:
            db.close()
            
    return get_medicine_by_slug_or_id(slug)
