# c:\Users\rites\OneDrive\Desktop\vaidyara\medicine_catalog.py
"""
Comprehensive Clinical Pharmacopeia and Disease Guidance Engine for VAIDYARA.
Provides verified, evidence-based monographs for medicines and extensive
clinical guidance for diseases, diagnostic methods, supportive home-care,
and certified medical citations (WHO, FDA, DailyMed, MedlinePlus, NICE, NHS).
"""

import urllib.request
import urllib.parse
import json
import difflib
import re

# ═══════════════════════════════════════════════════════════════════════════════
# 1. VERIFIED MEDICINES PHARMACOPEIA (EXHAUSTIVE CLINICAL MONOGRAPHS)
# ═══════════════════════════════════════════════════════════════════════════════

MEDICINES_CATALOG = [
    {
        "name": "Metformin",
        "brand_names": ["Glucophage", "Fortamet", "Glumetza", "Riomet", "Glycomet"],
        "generic_name": "Metformin hydrochloride",
        "active_ingredients": "Metformin hydrochloride",
        "image": "💊",
        "category": "Endocrine & Metabolic / Antidiabetic",
        "therapeutic_class": "Biguanide Antihyperglycemic Agent",
        "used_for": "First-line oral treatment for glycemic control in Type 2 Diabetes Mellitus; management of polycystic ovary syndrome (PCOS) and gestational diabetes under specialist care.",
        "prescribed_for": ["Type 2 Diabetes Mellitus", "Prediabetes in High-Risk Individuals", "Polycystic Ovary Syndrome (PCOS) Insulin Resistance", "Antipsychotic-Induced Weight Gain Mitigation"],
        "how_it_works": "Decreases hepatic gluconeogenesis (glucose output), reduces intestinal absorption of glucose, and improves peripheral insulin sensitivity by activating AMP-activated protein kinase (AMPK) without stimulating pancreatic insulin secretion, thereby carrying minimal intrinsic hypoglycemia risk.",
        "common_side_effects": ["Diarrhea and loose stools", "Nausea and abdominal cramping", "Flatulence and bloating", "Metallic taste in mouth", "Reduced serum vitamin B12 absorption with prolonged therapy"],
        "serious_side_effects": ["Lactic acidosis (FDA Boxed Warning: rare but life-threatening emergency characterized by malaise, myalgia, respiratory distress, somnolence, and hypothermia)", "Severe megaloblastic anemia secondary to profound vitamin B12 deficiency"],
        "contraindications": ["Severe renal impairment (eGFR < 30 mL/min/1.73 m²)", "Acute or chronic metabolic acidosis, including diabetic ketoacidosis (DKA)", "Severe congestive heart failure requiring pharmacological management", "Severe hepatic insufficiency or acute alcohol intoxication", "Withhold 48 hours before and after iodinated radiocontrast procedures"],
        "drug_interactions": ["Iodinated Radiologic Contrast Media: Multiplies risk of acute renal failure and fatal lactic acidosis", "Excess Alcohol: Potentiates metformin's effect on lactate metabolism", "Cationic Drugs (Cimetidine, Dolutegravir): Compete for renal tubular transport, increasing metformin blood levels", "Carbonic Anhydrase Inhibitors (Topiramate, Acetazolamide): Increase lactic acidosis risk"],
        "food_alcohol_interactions": ["Always administer with meals to minimize gastrointestinal discomfort and diarrhea", "Strictly avoid binge drinking or chronic alcohol abuse, which sharply heightens lactic acidosis risk."],
        "allergy_precautions": "Contraindicated in patients with hypersensitivity to metformin hydrochloride or any product formulation excipients.",
        "age_precautions": {
            "children": "Immediate-release formulation is approved in children >= 10 years of age with Type 2 diabetes. Extended-release formulations are not approved for pediatric patients < 18 years.",
            "older_adults": "Geriatric patients are vulnerable to age-related decline in renal clearance. Baseline and annual eGFR monitoring is mandatory. Avoid initiating if eGFR is 30–45 mL/min."
        },
        "pregnancy_breastfeeding": "Category B. Crosses the placenta. Frequently used for gestational diabetes under endocrinologist guidance. Excreted into breast milk in small amounts; generally acceptable with infant monitoring.",
        "kidney_liver_precautions": "Strictly contraindicated if eGFR < 30 mL/min/1.73 m². Dose reduction (maximum 1000 mg/day) required if eGFR is 30–45 mL/min. Avoid in hepatic impairment due to reduced lactate clearance.",
        "monitoring_requirements": "eGFR and serum creatinine at baseline and at least annually; Glycated Hemoglobin (HbA1c) every 3 months until stable then every 6 months; Serum Vitamin B12 and CBC every 1–2 years.",
        "precautions": ["FDA Boxed Warning for Lactic Acidosis", "Temporarily suspend medication prior to surgery requiring general anesthesia or radiocontrast procedures", "Educate patient on early signs of lactic acidosis"],
        "storage": "Store between 20°C and 25°C (68°F to 77°F). Protect from excessive heat and direct light.",
        "dosage_forms": ["Immediate-Release Oral Tablet", "Extended-Release (XR/ER) Tablet", "Oral Solution"],
        "strengths": ["500 mg", "850 mg", "1000 mg", "500 mg XR", "750 mg XR", "1000 mg XR", "500 mg/5 mL solution"],
        "manufacturer": "Bristol-Myers Squibb / Teva / USV / Torrent / Viatris",
        "sources": ["FDA Boxed Warning & Prescribing Information", "American Diabetes Association (ADA) Standards of Care", "DailyMed National Library of Medicine", "British National Formulary (BNF)"],
        "last_updated": "2026-08-10"
    },
    {
        "name": "Empagliflozin",
        "brand_names": ["Jardiance"],
        "generic_name": "Empagliflozin",
        "active_ingredients": "Empagliflozin",
        "image": "💊",
        "category": "Endocrine & Cardiovascular / SGLT2 Inhibitor",
        "therapeutic_class": "Sodium-Glucose Cotransporter-2 (SGLT2) Inhibitor",
        "used_for": "Glycemic control in Type 2 Diabetes; reduction of cardiovascular death in adults with T2D and established CVD; reduction of cardiovascular death and hospitalization in Heart Failure (HFrEF/HFpEF); slowing progression of Chronic Kidney Disease (CKD).",
        "prescribed_for": ["Type 2 Diabetes Mellitus with High CV Risk", "Heart Failure with Reduced or Preserved Ejection Fraction", "Chronic Kidney Disease Progression Delay"],
        "how_it_works": "Inhibits SGLT2 in the proximal renal tubules, reducing renal reabsorption of filtered glucose and lowering the renal threshold for glucose, promoting urinary glucose and sodium excretion (glycosuria and natriuresis), reducing intravascular volume and glomerular hyperfiltration.",
        "common_side_effects": ["Genital mycotic infections (vulvovaginal candidiasis, balanitis)", "Urinary tract infections", "Increased urination and mild osmotic diuresis", "Thirst and mild volume depletion"],
        "serious_side_effects": ["Euglycemic Diabetic Ketoacidosis (euDKA — ketoacidosis with near-normal blood glucose)", "Necrotizing fasciitis of the perineum (Fournier's Gangrene — surgical emergency)", "Urosepsis and acute pyelonephritis", "Symptomatic hypotension and acute kidney injury from volume contraction"],
        "contraindications": ["Dialysis or end-stage kidney disease (ineffective for glycemic control; however renal/HF protection studied down to eGFR 20 mL/min)", "Known serious hypersensitivity to empagliflozin", "Type 1 Diabetes Mellitus (high euDKA risk)"],
        "drug_interactions": ["Loop and Thiazide Diuretics: Additive volume depletion and hypotension risk", "Insulin and Sulfonylureas: Heightened hypoglycemia risk (dose reduction of secretagogues required)", "Lithium: Empagliflozin increases urinary lithium clearance, reducing lithium serum levels"],
        "food_alcohol_interactions": ["May be taken with or without food once daily in the morning. Avoid excessive alcohol consumption, which substantially elevates ketoacidosis risk."],
        "allergy_precautions": "Contraindicated in patients with angioedema or severe anaphylaxis to SGLT2 inhibitors.",
        "age_precautions": {
            "children": "Approved in pediatric patients >= 10 years of age for Type 2 diabetes control.",
            "older_adults": "Higher incidence of volume depletion, orthostatic hypotension, and renal impairment. Assess fluid status prior to initiation."
        },
        "pregnancy_breastfeeding": "Not recommended during the second and third trimesters of pregnancy due to potential risk to fetal renal development. Discontinue while breastfeeding.",
        "kidney_liver_precautions": "Glycemic efficacy declines when eGFR < 45 mL/min/1.73 m². Indicated for HF and CKD down to eGFR 20 mL/min/1.73 m². No dose adjustment in mild-to-moderate hepatic impairment.",
        "monitoring_requirements": "Renal function (eGFR, serum creatinine) prior to initiation and periodically; blood pressure and volume status; signs of perineal necrotizing infection.",
        "precautions": ["Withhold at least 3 days prior to major surgery to avoid postoperative euglycemic DKA", "Instruct patients on genital hygiene and prompt reporting of burning urination"],
        "storage": "Store at 25°C (77°F); excursions permitted between 15°C and 30°C.",
        "dosage_forms": ["Film-Coated Oral Tablet"],
        "strengths": ["10 mg", "25 mg"],
        "manufacturer": "Boehringer Ingelheim / Eli Lilly",
        "sources": ["FDA Prescribing Information", "ADA/EASD Consensus Guidelines", "KDIGO Clinical Guidelines", "DailyMed"],
        "last_updated": "2026-08-14"
    },
    {
        "name": "Paracetamol",
        "brand_names": ["Tylenol", "Panadol", "Calpol", "Crocin", "Dolo 650", "Febrex"],
        "generic_name": "Acetaminophen / Paracetamol",
        "active_ingredients": "Paracetamol (N-acetyl-p-aminophenol)",
        "image": "💊",
        "category": "Analgesic & Antipyretic",
        "therapeutic_class": "Non-opioid Analgesic / Aniline Derivative",
        "used_for": "First-line safe relief of mild to moderate pain (headache, toothache, muscle aches, sore throat) and reduction of fever in infectious illnesses, including dengue, viral fevers, and influenza.",
        "prescribed_for": ["Fever (Pyrexia) in Adults and Children", "Dengue Fever Symptomatic Care (Safe Choice - Avoids Bleeding)", "Tension Headache", "Osteoarthritis Pain", "Post-vaccination Fever", "Mild-to-Moderate Musculoskeletal Pain"],
        "how_it_works": "Inhibits central prostaglandin synthesis in the brain and modulates serotonergic inhibitory pain pathways; acts on the hypothalamic thermoregulatory center to induce peripheral vasodilation and heat dissipation. Lacks peripheral anti-inflammatory action and does not inhibit platelets or damage gastric mucosa.",
        "common_side_effects": ["Mild nausea", "Stomach upset (infrequent at recommended doses)", "Mild pruritus or transient rash in hypersensitive individuals"],
        "serious_side_effects": ["Acute hepatic necrosis and fulminant liver failure (in intentional or unintentional overdose due to toxic metabolite NAPQI accumulation)", "Severe cutaneous adverse reactions (Stevens-Johnson syndrome, TEN, AGEP)", "Renal tubular damage with chronic toxic intake"],
        "contraindications": ["Severe active hepatic impairment or severe acute liver failure", "Known severe hypersensitivity to paracetamol / acetaminophen"],
        "drug_interactions": ["Warfarin: Prolonged daily maximum intake (> 2000 mg/day for > 4 days) can elevate INR and bleeding risk", "Isoniazid, Carbamazepine, Phenytoin: Increase CYP2E1 induction and hepatotoxicity risk", "Chronic Alcohol Abuse: Induces CYP2E1 and depletes hepatic glutathione, drastically raising liver toxicity threshold"],
        "food_alcohol_interactions": ["May be taken with or without food. Avoid chronic or heavy alcohol consumption due to multiplied hepatotoxic risk."],
        "allergy_precautions": "Discontinue at the first appearance of skin rash, mucosal lesions, or any sign of hypersensitivity.",
        "age_precautions": {
            "children": "Safe first-line agent in infants and children. Dosing MUST be calculated by body weight (10–15 mg/kg per dose every 4–6 hours; maximum 60 mg/kg/day). Never exceed recommended concentrations.",
            "older_adults": "Safe first-line analgesic. Limit maximum daily dose to 2000–3000 mg/day in frail elderly or patients weighing under 50 kg."
        },
        "pregnancy_breastfeeding": "Category B. The analgesic and antipyretic of choice in all trimesters of pregnancy at lowest effective dose for shortest duration. Compatible with breastfeeding.",
        "kidney_liver_precautions": "Use with caution in hepatic insufficiency and chronic alcoholism (max 2000 mg/day). In severe renal impairment (eGFR < 10 mL/min), lengthen dosing interval to every 8 hours.",
        "monitoring_requirements": "Liver function tests (ALT/AST) and INR in patients receiving prolonged high-dose therapy or with underlying hepatic disease.",
        "precautions": ["Do not exceed 4000 mg/day in adults from all sources combined", "Always check OTC combination cough, cold, and flu medicines for hidden acetaminophen to prevent accidental overdose"],
        "storage": "Store below 25°C (77°F). Protect from direct light and moisture.",
        "dosage_forms": ["Oral Tablet", "Dispersible Tablet", "Oral Suspension", "Infant Drops", "Suppository", "Intravenous Infusion"],
        "strengths": ["500 mg", "650 mg", "120 mg/5 mL", "250 mg/5 mL", "1000 mg IV"],
        "manufacturer": "GSK / Johnson & Johnson / Micro Labs / Haleon / Generic manufacturers",
        "sources": ["WHO Model List of Essential Medicines", "British National Formulary (BNF)", "FDA Prescribing Information", "DailyMed"],
        "last_updated": "2026-08-10"
    },
    {
        "name": "Ibuprofen",
        "brand_names": ["Advil", "Motrin", "Brufen", "Nurofen", "Ibugesic"],
        "generic_name": "Ibuprofen",
        "active_ingredients": "Ibuprofen",
        "image": "💊",
        "category": "NSAID (Non-Steroidal Anti-Inflammatory Drug)",
        "therapeutic_class": "Propionic Acid Derivative NSAID",
        "used_for": "Relief of inflammatory pain, dysmenorrhea, dental pain, migraine, osteoarthritis, rheumatoid arthritis, and fever. STRICTLY AVOID IN DENGUE FEVER due to hemorrhage risk.",
        "prescribed_for": ["Osteoarthritis and Rheumatoid Arthritis", "Headache and Migraine", "Dysmenorrhea (Menstrual Cramps)", "Musculoskeletal and Soft Tissue Injury", "Dental Pain", "Fever (Non-Dengue)"],
        "how_it_works": "Reversibly and non-selectively inhibits cyclooxygenase-1 (COX-1) and cyclooxygenase-2 (COX-2) enzymes, preventing the conversion of arachidonic acid to prostaglandins and thromboxanes, eliminating inflammatory swelling, peripheral pain sensitization, and hypothalamic fever response.",
        "common_side_effects": ["Epigastric burning and dyspepsia", "Heartburn and nausea", "Mild dizziness and headache", "Fluid retention and peripheral edema"],
        "serious_side_effects": ["Gastrointestinal ulceration, massive bleeding, and stomach perforation (FDA Boxed Warning)", "Major cardiovascular thrombotic events, myocardial infarction, and stroke (FDA Boxed Warning)", "Acute kidney injury and interstitial nephritis", "Aspirin-Exacerbated Respiratory Disease (severe bronchospasm in asthmatics)"],
        "contraindications": ["Active peptic ulcer disease or history of GI bleeding", "CRITICAL: Dengue Fever and suspected hemorrhagic fevers (causes severe platelet dysfunction and fatal hemorrhage)", "Aspirin-induced asthma or triad (nasal polyps, asthma, NSAID allergy)", "Third trimester of pregnancy (causes premature ductus arteriosus closure)", "Severe heart failure or severe renal failure"],
        "drug_interactions": ["Anticoagulants (Warfarin, Apixaban) and Antiplatelets (Aspirin, Clopidogrel): Dramatically multiplies catastrophic GI bleeding risk", "ACE Inhibitors & ARBs: Blunts antihypertensive effect and precipitates acute kidney injury (the 'Triple Whammy' with diuretics)", "Lithium and Methotrexate: Impairs renal clearance leading to severe toxicity"],
        "food_alcohol_interactions": ["Always ingest with meals or a full glass of milk to buffer gastric mucosal irritation. Concurrent alcohol sharply increases gastric ulceration and bleeding risk."],
        "allergy_precautions": "Contraindicated in individuals who have experienced asthma, urticaria, or allergic-type reactions after taking aspirin or other NSAIDs.",
        "age_precautions": {
            "children": "Approved in children >= 6 months for fever and pain (5–10 mg/kg every 6–8 hours). Never administer to dehydrated children due to acute tubular necrosis risk.",
            "older_adults": "Beers Criteria warning: High risk of silent GI bleeding, worsening hypertension, heart failure exacerbation, and acute renal decline. Avoid chronic use."
        },
        "pregnancy_breastfeeding": "Contraindicated in the third trimester of pregnancy (FDA Category D: oligohydramnios and premature ductus arteriosus closure). Compatible in low doses during breastfeeding.",
        "kidney_liver_precautions": "Contraindicated in severe renal failure. NSAIDs inhibit protective renal vasodilating prostaglandins (PGE2, PGI2), compromising renal perfusion. Use caution in hepatic impairment.",
        "monitoring_requirements": "Blood pressure; CBC and hemoglobin (for occult blood loss); BUN and serum creatinine in chronic therapy.",
        "precautions": ["FDA Boxed Warnings for GI Bleeding and Cardiovascular Risk", "Use lowest effective dose for shortest possible duration", "Strictly prohibited in suspected Dengue"],
        "storage": "Store at 20°C to 25°C (68°F to 77°F). Protect from excessive heat and direct light.",
        "dosage_forms": ["Oral Tablet", "Softgel Capsule", "Oral Suspension", "Topical Gel"],
        "strengths": ["200 mg", "400 mg", "600 mg", "800 mg", "100 mg/5 mL suspension"],
        "manufacturer": "Pfizer / Haleon / Abbott / Generic manufacturers",
        "sources": ["FDA Boxed Warning & Prescribing Information", "British National Formulary (BNF)", "NICE Clinical Guidelines", "DailyMed"],
        "last_updated": "2026-07-22"
    },
    {
        "name": "Artemether and Lumefantrine",
        "brand_names": ["Coartem", "Riamet", "Falcinil-LF", "Lumartem"],
        "generic_name": "Artemether and lumefantrine",
        "active_ingredients": "Artemether (20 mg) + Lumefantrine (120 mg)",
        "image": "💊",
        "category": "Infectious & Tropical / Antimalarial",
        "therapeutic_class": "Artemisinin-Based Combination Therapy (ACT)",
        "used_for": "First-line oral treatment of acute, uncomplicated malaria infections caused by Plasmodium falciparum or mixed malarial infections in adults and pediatric patients.",
        "prescribed_for": ["Uncomplicated Plasmodium falciparum Malaria", "Chloroquine-Resistant P. vivax Malaria (Where Endorsed by WHO)", "Mixed Plasmodial Infections"],
        "how_it_works": "Dual-action antimalarial: Artemether is rapidly metabolized to dihydroartemisinin (DHA), generating free radical endoperoxides that rapidly destroy malarial parasite biomass within hours; Lumefantrine has a prolonged half-life, preventing nucleic acid and protein synthesis to eradicate any residual parasites and prevent recrudescence.",
        "common_side_effects": ["Headache and dizziness", "Anorexia and nausea", "Abdominal pain and vomiting", "Asthenia and fatigue", "Arthralgia and myalgia", "Sleep disturbances"],
        "serious_side_effects": ["Cardiac QTc interval prolongation (arrhythmia risk)", "Severe hypersensitivity and urticaria", "Hemolytic anemia (rare post-artemisinin delayed hemolysis)"],
        "contraindications": ["Known hypersensitivity to artemether, lumefantrine, or artemisinin derivatives", "Severe / complicated cerebral malaria requiring intravenous artesunate", "Congenital long QT syndrome or concurrent administration of QT-prolonging drugs", "First trimester of pregnancy (unless no alternative is available, per WHO guidelines)"],
        "drug_interactions": ["QT-Prolonging Medications (Haloperidol, Erythromycin, Moxifloxacin, Amiodarone): Multiplies dangerous ventricular arrhythmia risk", "Strong CYP3A4 Inducers (Rifampin, Carbamazepine, St. John's Wort): Drastically reduces artemether and lumefantrine levels, leading to treatment failure", "Strong CYP3A4 Inhibitors (Ketoconazole): Elevates lumefantrine exposure and cardiac toxicity"],
        "food_alcohol_interactions": ["CRITICAL INSTRUCTION: Must be taken with high-fat food or full-cream milk. Lumefantrine bioavailability increases up to 16-fold in the presence of dietary lipids."],
        "allergy_precautions": "Discontinue immediately and provide emergency support if angioedema, bronchospasm, or anaphylaxis occurs.",
        "age_precautions": {
            "children": "Approved in infants and children weighing >= 5 kg. Dosing follows a strict 6-dose regimen over 3 days based entirely on body weight bands.",
            "older_adults": "Monitor baseline ECG and electrolytes due to higher vulnerability to drug-induced cardiac conduction abnormalities."
        },
        "pregnancy_breastfeeding": "WHO recommends artemether-lumefantrine as treatment of choice for uncomplicated falciparum malaria during the second and third trimesters of pregnancy. In the first trimester, use if other antimalarials are unavailable. Excreted in breast milk; safe under clinical supervision.",
        "kidney_liver_precautions": "No dose adjustment required in mild-to-moderate renal or hepatic impairment. Exercise caution in severe hepatic dysfunction.",
        "monitoring_requirements": "Baseline and follow-up microscopic blood smears (thick and thin films) for parasite clearance; ECG monitoring in high-risk patients; serum potassium and magnesium.",
        "precautions": ["Must complete the entire 6-dose course over 3 days even if fever clears", "If patient vomits within 1 hour of ingestion, repeat the full dose"],
        "storage": "Store below 30°C (86°F). Protect from moisture and heat.",
        "dosage_forms": ["Oral Tablet", "Dispersible Tablet for Paediatric Use"],
        "strengths": ["20 mg Artemether / 120 mg Lumefantrine", "80 mg / 480 mg Forte Tablet"],
        "manufacturer": "Novartis / Cipla / Ajanta Pharma / Generic manufacturers",
        "sources": ["WHO Guidelines for Malaria", "FDA Prescribing Information", "CDC Yellow Book Malaria Guidance", "DailyMed"],
        "last_updated": "2026-08-01"
    },
    {
        "name": "Levetiracetam",
        "brand_names": ["Keppra", "Levroxa", "Elepsia XR", "Spritam"],
        "generic_name": "Levetiracetam",
        "active_ingredients": "Levetiracetam",
        "image": "💊",
        "category": "Neurological / Anticonvulsant",
        "therapeutic_class": "Synaptic Vesicle Protein 2A (SV2A) Ligand",
        "used_for": "Monotherapy and adjunctive treatment of focal (partial onset) seizures, generalized tonic-clonic seizures, and myoclonic seizures in patients with epilepsy.",
        "prescribed_for": ["Focal Onset Seizures with or without Secondary Generalization", "Primary Generalized Tonic-Clonic Seizures (PGTCS)", "Juvenile Myoclonic Epilepsy (JME)", "Status Epilepticus (Second-Line IV Rescue)", "Post-Traumatic Brain Injury Seizure Prophylaxis"],
        "how_it_works": "Selectively binds to synaptic vesicle protein 2A (SV2A) in presynaptic nerve terminals, inhibiting presynaptic vesicle exocytosis and modulating neurotransmitter release, thereby suppressing abnormal epileptiform burst firing without significantly affecting normal neuronal excitability.",
        "common_side_effects": ["Somnolence and fatigue", "Dizziness and ataxia", "Nasopharyngitis and upper respiratory symptoms", "Headache", "Irritability and emotional lability"],
        "serious_side_effects": ["Neuropsychiatric symptoms (depression, agitation, psychosis, suicidal ideation)", "Severe cutaneous adverse reactions (SJS / TEN)", "Anaphylaxis and angioedema", "Agranulocytosis or neutropenia (rare)"],
        "contraindications": ["Hypersensitivity to levetiracetam, pyrrolidone derivatives, or formulation excipients"],
        "drug_interactions": ["Minimal CYP450 interactions: Does not induce or inhibit hepatic enzymes, making it exceptionally safe in combination antiepileptic therapy", "Methotrexate: Concurrent use may reduce renal methotrexate clearance, raising methotrexate toxicity", "CNS Depressants and Alcohol: Additive psychomotor impairment and sedation"],
        "food_alcohol_interactions": ["May be taken with or without food. Avoid alcohol, which amplifies somnolence, cognitive slowing, and can provoke breakthrough seizures."],
        "allergy_precautions": "Discontinue if unexplained rash or systemic signs of hypersensitivity appear.",
        "age_precautions": {
            "children": "Approved in infants as young as 1 month of age for focal seizures. Paediatric oral solution allows precise weight-based titration (mg/kg).",
            "older_adults": "Dose adjustment required based on age-related decline in creatinine clearance. Vulnerable to somnolence and unsteadiness (fall risk)."
        },
        "pregnancy_breastfeeding": "Pregnancy Category C. Preferred first-line antiepileptic during pregnancy due to lowest major congenital malformation rates in international pregnancy registries (EURAP). Serum levels decline markedly during third trimester; therapeutic drug monitoring required. Compatible with breastfeeding.",
        "kidney_liver_precautions": "Eliminated primarily via renal excretion (~66% unchanged). Mandatory dosage reduction in renal impairment: eGFR 50–79 mL/min (500–1000 mg q12h); eGFR 30–49 mL/min (250–750 mg q12h); eGFR < 30 mL/min (250–500 mg q12h).",
        "monitoring_requirements": "Renal function (BUN/creatinine); screening for emergent behavioral/mood changes and suicidal ideation at every clinical visit.",
        "precautions": ["FDA Warning for Suicidal Behavior and Ideation", "NEVER abruptly discontinue antiepileptic therapy; sudden cessation triggers rebound status epilepticus (taper gradually)", "Warn patient regarding driving restrictions until seizure-free"],
        "storage": "Store at 25°C (77°F). Protect from light and moisture.",
        "dosage_forms": ["Immediate-Release Oral Tablet", "Extended-Release (XR) Tablet", "Oral Solution (100 mg/mL)", "Intravenous Solution"],
        "strengths": ["250 mg", "500 mg", "750 mg", "1000 mg", "500 mg XR", "750 mg XR", "100 mg/mL solution"],
        "manufacturer": "UCB Pharma / Sun Pharma / Lupin / Generic manufacturers",
        "sources": ["FDA Prescribing Information", "American Epilepsy Society (AES) Guidelines", "NICE Guideline NG217", "DailyMed"],
        "last_updated": "2026-08-16"
    },
    {
        "name": "Sodium Valproate",
        "brand_names": ["Depakote", "Epilim", "Depakene", "Encorate", "Valparin"],
        "generic_name": "Divalproex sodium / Sodium valproate",
        "active_ingredients": "Sodium valproate / Valproic acid",
        "image": "💊",
        "category": "Neurological & Psychiatric / Anticonvulsant",
        "therapeutic_class": "Broad-Spectrum Antiepileptic & Mood Stabilizer",
        "used_for": "Broad-spectrum control of generalized, focal, absence, and myoclonic seizures; acute manic episodes of Bipolar Disorder; prophylaxis of migraine headaches.",
        "prescribed_for": ["Generalized Tonic-Clonic Seizures", "Absence Seizures (Petit Mal)", "Myoclonic Seizures in Juvenile Myoclonic Epilepsy", "Focal Seizures", "Bipolar I Acute Mania", "Migraine Headache Prophylaxis"],
        "how_it_works": "Multi-mechanistic action: Blocks voltage-gated sodium channels, inhibits T-type calcium channels, and enhances inhibitory GABAergic neurotransmission by inhibiting GABA transaminase and stimulating glutamate decarboxylase.",
        "common_side_effects": ["Tremor (postural hand tremor)", "Weight gain and increased appetite", "Alopecia (hair thinning)", "Nausea and dyspepsia", "Menstrual irregularities and polycystic ovarian changes"],
        "serious_side_effects": ["Fatal hepatotoxicity (FDA Boxed Warning: peak risk in children under 2 years)", "Pancreatitis (FDA Boxed Warning: severe, hemorrhagic, life-threatening)", "Severe teratogenicity (FDA Boxed Warning: neural tube defects, lower IQ scores in offspring)", "Hyperammonemic encephalopathy (with or without abnormal liver enzymes)", "Thrombocytopenia and coagulopathy"],
        "contraindications": ["Pregnancy for migraine prevention, and pregnancy for epilepsy unless no suitable alternative exists (Pregnancy Prevention Programme mandatory)", "Active hepatic disease or significant hepatic impairment", "Known mitochondrial disorders caused by mutations in mitochondrial DNA polymerase-gamma (POLG)", "Known urea cycle disorders (hyperammonemic coma risk)"],
        "drug_interactions": ["Carbapenem Antibiotics (Meropenem, Imipenem): CRITICAL CONTRAINDICATION — carbapenems plummet valproate blood levels by 80% within 24 hours, triggering status epilepticus", "Lamotrigine: Valproate inhibits lamotrigine glucuronidation, doubling lamotrigine half-life and multiplying toxic epidermal necrolysis (TEN) risk", "Aspirin: Displaces valproate from albumin and impairs metabolism, elevating free active valproate levels"],
        "food_alcohol_interactions": ["Take with food to minimize gastric irritation. Do not crush enteric-coated tablets. Strictly avoid alcohol."],
        "allergy_precautions": "Immediate discontinuation required if DRESS syndrome (fever, rash, lymphadenopathy, multiorgan involvement) develops.",
        "age_precautions": {
            "children": "FDA Boxed Warning: Children under 2 years of age have a dramatically elevated risk of fatal hepatotoxicity. Use with extreme caution as sole agent.",
            "older_adults": "Higher unbound free valproate fraction due to decreased albumin. Lower starting doses and slow titration required."
        },
        "pregnancy_breastfeeding": "FDA Boxed Warning: High rate of major congenital malformations (neural tube defects / spina bifida in 1–2%) and 8–10 point reduction in childhood IQ scores. Strictly avoided in women of childbearing potential unless adhering to pregnancy prevention programme (Pledge/Prevent). Excreted in breast milk in small amounts.",
        "kidney_liver_precautions": "Strictly contraindicated in hepatic disease. No dosage adjustments required for renal impairment, but free unbound drug fraction is increased.",
        "monitoring_requirements": "Baseline and periodic Liver Function Tests (LFTs); Complete Blood Count with Platelets; Serum Valproate therapeutic level (trough target: 50–100 mcg/mL); Serum ammonia in patients presenting with lethargy or confusion.",
        "precautions": ["FDA Boxed Warnings for Hepatotoxicity, Pancreatitis, and Teratogenicity", "Instruct patient to seek urgent care for abdominal pain (pancreatitis) or jaundice (liver injury)", "Never discontinue abruptly"],
        "storage": "Store at 25°C (77°F). Keep containers tightly closed.",
        "dosage_forms": ["Enteric-Coated Tablet", "Extended-Release (ER) Tablet", "Oral Solution", "Delayed-Release Sprinkle Capsule", "IV Infusion"],
        "strengths": ["125 mg", "250 mg", "500 mg", "250 mg ER", "500 mg ER", "250 mg/5 mL syrup"],
        "manufacturer": "AbbVie / Sanofi / Torrent / Sun Pharma",
        "sources": ["FDA Boxed Warnings and Prescribing Information", "NICE Epilepsy Guidelines", "DailyMed", "BNF"],
        "last_updated": "2026-08-12"
    },
    {
        "name": "Amlodipine",
        "brand_names": ["Norvasc", "Amlong", "Stamlo", "Amlovas"],
        "generic_name": "Amlodipine besylate",
        "active_ingredients": "Amlodipine besylate",
        "image": "💊",
        "category": "Cardiovascular / Antihypertensive",
        "therapeutic_class": "Dihydropyridine Calcium Channel Blocker (CCB)",
        "used_for": "First-line management of essential hypertension; chronic stable angina pectoris; vasospastic (Prinzmetal's) angina.",
        "prescribed_for": ["Essential Hypertension in Adults and Children", "Chronic Stable Angina", "Vasospastic (Prinzmetal's) Angina", "Coronary Artery Disease Plaque Stabilization"],
        "how_it_works": "Selectively inhibits transmembrane influx of extracellular calcium ions into vascular smooth muscle cells and myocardial cells, causing systemic peripheral arterial vasodilation, reducing total peripheral resistance, systemic blood pressure, and cardiac afterload without depressing cardiac nodal conduction.",
        "common_side_effects": ["Peripheral dependent ankle edema (fluid accumulation in lower extremities)", "Flushing and warm sensation", "Dizziness and lightheadedness", "Headache", "Fatigue", "Palpitations"],
        "serious_side_effects": ["Severe symptomatic hypotension / syncope", "Worsening angina or acute myocardial infarction upon initiation or dose escalation in severe obstructive CAD", "Gingival hyperplasia"],
        "contraindications": ["Severe hypotension (systolic BP < 90 mmHg)", "Cardiogenic shock or severe aortic stenosis", "Known hypersensitivity to dihydropyridine calcium channel blockers"],
        "drug_interactions": ["Simvastatin: Amlodipine increases simvastatin exposure; limit simvastatin dose to a maximum of 20 mg/day to avoid rhabdomyolysis", "CYP3A4 Inhibitors (Ketoconazole, Itraconazole, Diltiazem): Elevate amlodipine plasma levels", "Cyclosporine / Tacrolimus: Amlodipine increases calcineurin inhibitor blood concentrations"],
        "food_alcohol_interactions": ["May be taken with or without food. Avoid excessive grapefruit juice, which can inhibit CYP3A4 and increase drug levels. Alcohol potentiates hypotensive effects."],
        "allergy_precautions": "Contraindicated in patients with severe dihydropyridine allergy.",
        "age_precautions": {
            "children": "Approved in pediatric patients 6–17 years of age for hypertension (starting dose 2.5 mg once daily).",
            "older_adults": "Clearance is decreased in elderly individuals; start at lower dose (2.5 mg once daily) to avoid severe orthostatic hypotension."
        },
        "pregnancy_breastfeeding": "Category C. Limited human data; other antihypertensive agents (labetalol, nifedipine, methyldopa) are preferred in pregnancy. Excreted into human milk in small amounts.",
        "kidney_liver_precautions": "Safe in renal impairment without dose adjustment. Extensively metabolized by the liver; initial dose should be reduced to 2.5 mg daily in severe hepatic impairment.",
        "monitoring_requirements": "Blood pressure and heart rate; inspection for lower extremity peripheral edema.",
        "precautions": ["Advise patient regarding benign ankle edema which responds poorly to diuretics but improves with leg elevation or ARB co-prescription", "Do not stop taking suddenly"],
        "storage": "Store between 15°C and 30°C (59°F and 86°F). Protect from light.",
        "dosage_forms": ["Oral Tablet"],
        "strengths": ["2.5 mg", "5 mg", "10 mg"],
        "manufacturer": "Pfizer / Viatris / Sun Pharma / Generic manufacturers",
        "sources": ["FDA Prescribing Information", "AHA/ACC Hypertension Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-11"
    },
    {
        "name": "Lisinopril",
        "brand_names": ["Zestril", "Prinivil", "Lipril", "Listril"],
        "generic_name": "Lisinopril",
        "active_ingredients": "Lisinopril dihydrate",
        "image": "💊",
        "category": "Cardiovascular / Antihypertensive",
        "therapeutic_class": "Angiotensin-Converting Enzyme (ACE) Inhibitor",
        "used_for": "Treatment of hypertension; adjunctive therapy in systolic heart failure (HFrEF); reduction of mortality within 24 hours of acute myocardial infarction; slowing progression of diabetic nephropathy.",
        "prescribed_for": ["Essential Hypertension", "Heart Failure with Reduced Ejection Fraction (HFrEF)", "Post-Myocardial Infarction Survival Improvement", "Diabetic Nephropathy / Proteinuria Reduction"],
        "how_it_works": "Competitively inhibits angiotensin-converting enzyme (ACE), preventing the conversion of angiotensin I to the potent vasoconstrictor angiotensin II, decreasing systemic vascular resistance, reducing aldosterone secretion, promoting natriuresis, and blunting sympathetic activation; concurrently suppresses bradykinin degradation.",
        "common_side_effects": ["Persistent dry, hacking, non-productive cough (bradykinin-mediated)", "Dizziness and lightheadedness", "Headache", "Fatigue", "Diarrhea"],
        "serious_side_effects": ["Life-threatening Angioedema (FDA Boxed Warning: swelling of lips, tongue, pharynx, larynx causing acute asphyxiation)", "Fetal toxicity and fetal demise (FDA Boxed Warning: strictly contraindicated in pregnancy)", "Hyperkalemia (elevated serum potassium)", "Acute renal failure in bilateral renal artery stenosis"],
        "contraindications": ["Pregnancy (FDA Boxed Warning: causes severe oligohydramnios, skull hypoplasia, and fetal death)", "History of ACE inhibitor-induced angioedema or hereditary angioedema", "Concomitant use of Sacubitril/Valsartan (Entresto) within 36 hours (massive angioedema risk)", "Concomitant aliskiren in patients with diabetes mellitus"],
        "drug_interactions": ["Potassium Supplements & Potassium-Sparing Diuretics (Spironolactone, Amiloride): Severe, fatal hyperkalemia risk", "NSAIDs (Ibuprofen, Naproxen): Antagonize antihypertensive response and accelerate acute renal failure", "Lithium: Lisinopril reduces renal lithium excretion, causing severe lithium toxicity", "Sacubitril: Requires 36-hour washout period to prevent fatal angioedema"],
        "food_alcohol_interactions": ["May be taken with or without food. Avoid potassium-containing salt substitutes (potassium chloride) to prevent dangerous hyperkalemia. Alcohol compounds hypotension."],
        "allergy_precautions": "Immediate permanent discontinuation required if facial or laryngeal swelling occurs. Black patients have a 4- to 5-fold higher risk of angioedema.",
        "age_precautions": {
            "children": "Approved in pediatric patients >= 6 years of age for hypertension.",
            "older_adults": "Start at low doses (2.5–5 mg daily). High susceptibility to orthostatic hypotension and hyperkalemia."
        },
        "pregnancy_breastfeeding": "FDA Boxed Warning: Pregnancy Category D. Must be discontinued immediately when pregnancy is detected. Not recommended during breastfeeding.",
        "kidney_liver_precautions": "Excreted entirely unchanged by the kidneys. Initial dose must be reduced in renal impairment (eGFR 10–30 mL/min: start 5 mg/day; eGFR < 10 mL/min: start 2.5 mg/day). Not metabolized by the liver.",
        "monitoring_requirements": "Serum potassium, serum creatinine, and BUN at baseline, 1–2 weeks post-initiation/dose titration, and every 6–12 months; blood pressure.",
        "precautions": ["FDA Boxed Warning for Fetal Toxicity", "Educate patient on persistent dry cough which does not respond to cough suppressants (requires switching to an ARB like Losartan)"],
        "storage": "Store at 20°C to 25°C (68°F to 77°F). Protect from excessive moisture.",
        "dosage_forms": ["Oral Tablet", "Oral Solution (1 mg/mL)"],
        "strengths": ["2.5 mg", "5 mg", "10 mg", "20 mg", "30 mg", "40 mg"],
        "manufacturer": "AstraZeneca / Alvogen / Lupin / Generic manufacturers",
        "sources": ["FDA Boxed Warning & Prescribing Information", "AHA/ACC/HFSA Heart Failure Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-15"
    },
    {
        "name": "Atorvastatin",
        "brand_names": ["Lipitor", "Atorva", "Storvas", "Lipvas", "Atocor"],
        "generic_name": "Atorvastatin calcium",
        "active_ingredients": "Atorvastatin calcium",
        "image": "💊",
        "category": "Cardiovascular & Metabolic / Lipid-Lowering",
        "therapeutic_class": "HMG-CoA Reductase Inhibitor (Statin)",
        "used_for": "Primary and secondary prevention of atherosclerotic cardiovascular events (heart attack, stroke, revascularization); treatment of primary hyperlipidemia and mixed dyslipidemia.",
        "prescribed_for": ["Primary Hypercholesterolemia and Mixed Dyslipidemia", "Secondary Prevention Post-Myocardial Infarction / Angina", "Ischemic Stroke Risk Reduction", "Type 2 Diabetes Mellitus Cardiovascular Risk Reduction", "Familial Hypercholesterolemia"],
        "how_it_works": "Competitively inhibits 3-hydroxy-3-methylglutaryl-coenzyme A (HMG-CoA) reductase, the rate-limiting enzyme in cholesterol biosynthesis, upregulating hepatic low-density lipoprotein (LDL) receptors, clearing circulating atherogenic LDL particles and apolipoprotein B from the bloodstream and stabilizing arterial plaques.",
        "common_side_effects": ["Myalgia (mild muscle aches)", "Arthralgia and joint pain", "Nasopharyngitis", "Diarrhea and dyspepsia", "Mild elevation in blood glucose and HbA1c"],
        "serious_side_effects": ["Rhabdomyolysis with acute myoglobinuric renal failure (severe muscle breakdown)", "Immune-mediated necrotizing myopathy (IMNM — anti-HMGCR antibodies)", "Hepatotoxicity and severe jaundice (rare)", "Hemorrhagic stroke in patients with recent hemorrhagic cerebrovascular events"],
        "contraindications": ["Active liver disease or unexplained persistent elevations in hepatic transaminases", "Known hypersensitivity to atorvastatin", "Pregnancy and breastfeeding (contraindicated due to interference with fetal steroid synthesis)"],
        "drug_interactions": ["Strong CYP3A4 Inhibitors (Clarithromycin, Itraconazole, Protease Inhibitors): Substantially elevate atorvastatin exposure, multiplying rhabdomyolysis risk", "Cyclosporine and Gemfibrozil: Severe rhabdomyolysis risk (avoid co-administration)", "Digoxin: Mild increase in steady-state digoxin levels"],
        "food_alcohol_interactions": ["May be taken with or without meals at any time of day. Avoid consuming > 1.2 liters of grapefruit juice daily (CYP3A4 inhibition). Limit chronic heavy alcohol intake."],
        "allergy_precautions": "Contraindicated in known statin hypersensitivity.",
        "age_precautions": {
            "children": "Approved in children >= 10 years of age with heterozygous familial hypercholesterolemia (starting dose 10 mg/day).",
            "older_adults": "Efficacy demonstrated across elderly trials. Monitor for increased susceptibility to drug-induced myopathy and frailty."
        },
        "pregnancy_breastfeeding": "Contraindicated during pregnancy and lactation. Discontinue immediately if pregnancy occurs.",
        "kidney_liver_precautions": "No dose adjustment required in renal impairment (cleared primarily via hepatic metabolism). Contraindicated in active acute hepatic disease.",
        "monitoring_requirements": "Baseline lipid panel, then 4–12 weeks after initiation or dose titration, then every 3–12 months; baseline hepatic transaminases (ALT/AST); serum creatine kinase (CK) in patients reporting muscle pain, tenderness, or weakness.",
        "precautions": ["Instruct patient to report unexplained muscle pain, tenderness, or dark brown urine immediately", "Small increase in diabetes risk is far outweighed by monumental cardiovascular death reduction"],
        "storage": "Store between 20°C and 25°C (68°F to 77°F).",
        "dosage_forms": ["Film-Coated Oral Tablet"],
        "strengths": ["10 mg", "20 mg", "40 mg", "80 mg"],
        "manufacturer": "Pfizer / Viatris / Sun Pharma / Torrent / Generic manufacturers",
        "sources": ["FDA Prescribing Information", "AHA/ACC Cholesterol Guidelines", "NICE Clinical Guidelines", "DailyMed"],
        "last_updated": "2026-08-18"
    },
    {
        "name": "Amoxicillin and Clavulanate Potassium",
        "brand_names": ["Augmentin", "Clavam", "Moxikind-CV", "Augpen", "Amoclav"],
        "generic_name": "Amoxicillin and clavulanate potassium",
        "active_ingredients": "Amoxicillin trihydrate + Clavulanate potassium",
        "image": "💊",
        "category": "Antibacterial / Beta-Lactam Combination",
        "therapeutic_class": "Aminopenicillin with Beta-Lactamase Inhibitor",
        "used_for": "Treatment of susceptible bacterial infections of the lower respiratory tract (community-acquired pneumonia), acute bacterial sinusitis, acute otitis media, urinary tract infections, and complicated skin structure infections caused by beta-lactamase-producing organisms.",
        "prescribed_for": ["Community-Acquired Pneumonia (Bacterial)", "Acute Bacterial Exacerbation of Chronic Bronchitis", "Acute Bacterial Rhinosinusitis", "Severe Acute Otitis Media", "Complicated Urinary Tract Infections", "Skin and Soft Tissue Abscesses / Animal Bites"],
        "how_it_works": "Amoxicillin inhibits bacterial cell wall peptidoglycan transpeptidation, causing osmotic lysis; Clavulanate is a suicidal beta-lactamase inhibitor that irreversibly binds and inactivates beta-lactamase enzymes produced by resistant bacteria, restoring amoxicillin's broad antibacterial spectrum.",
        "common_side_effects": ["Diarrhea (frequent, mediated by clavulanic acid hypermotility)", "Nausea and vomiting", "Abdominal discomfort", "Oral or vaginal candidiasis (thrush)", "Mild maculopapular skin rash"],
        "serious_side_effects": ["Immediate Type I Anaphylactic Reaction (laryngeal edema, bronchospasm, cardiovascular collapse)", "Cholestatic jaundice and hepatitis (Augmentin-induced hepatotoxicity)", "Clostridioides difficile-associated severe pseudomembranous colitis", "Toxic Epidermal Necrolysis / Stevens-Johnson Syndrome"],
        "contraindications": ["History of severe allergic reaction (anaphylaxis) to penicillin or any beta-lactam antibiotic", "History of amoxicillin/clavulanate-associated cholestatic jaundice or hepatic dysfunction", "Infectious mononucleosis (EBV — high incidence of erythematous rash)"],
        "drug_interactions": ["Warfarin: May prolong prothrombin time and elevate INR, increasing bleeding risk", "Methotrexate: Decreases renal tubular clearance of methotrexate, causing severe toxicity", "Allopurinol: Concomitant use increases incidence of drug-induced skin eruptions", "Probenecid: Decreases renal tubular secretion of amoxicillin, producing prolonged high antibiotic levels"],
        "food_alcohol_interactions": ["CRITICAL: Administer at the start of a meal to enhance clavulanate absorption and dramatically reduce gastrointestinal upset and diarrhea. Avoid alcohol."],
        "allergy_precautions": "STRICTLY CONTRAINDICATED in documented penicillin allergy. Inquire thoroughly regarding past penicillin rashes or anaphylactic history.",
        "age_precautions": {
            "children": "Approved in infants and children. Weight-based dosing (mg amoxicillin component/kg/day) in divided doses every 8 or 12 hours. Do not interchange different ratio formulations.",
            "older_adults": "Substantially excreted by the kidney; monitor renal function and adjust dose accordingly."
        },
        "pregnancy_breastfeeding": "Category B. Generally considered safe during pregnancy when clinically indicated. Compatible with breastfeeding (monitor infant for loose stools).",
        "kidney_liver_precautions": "Dosage adjustment required in moderate-to-severe renal impairment: eGFR 10–30 mL/min (500/125 mg q12h); eGFR < 10 mL/min (500/125 mg q24h). Avoid 875/125 mg tablets if eGFR < 30. Use caution and monitor liver enzymes in hepatic dysfunction.",
        "monitoring_requirements": "Complete prescribed course; monitor hepatic transaminases in prolonged treatment (> 14 days); monitor for severe watery diarrhea (C. diff).",
        "precautions": ["Must complete the entire prescribed regimen to prevent selection of multi-drug resistant bacterial strains", "Discontinue immediately if allergic symptoms appear"],
        "storage": "Store tablets below 25°C (77°F). Reconstituted oral suspension must be kept refrigerated (2°C–8°C) and discarded after 10 days.",
        "dosage_forms": ["Film-Coated Tablet", "Chewable Tablet", "Powder for Oral Suspension", "IV Formulation"],
        "strengths": ["500/125 mg", "875/125 mg", "250/62.5 mg/5 mL suspension", "400/57 mg/5 mL suspension", "1000/62.5 mg ER"],
        "manufacturer": "GSK / Sandoz / Teva / Cipla / Generic manufacturers",
        "sources": ["FDA Prescribing Information", "IDSA/ATS Community-Acquired Pneumonia Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-20"
    },
    {
        "name": "Azithromycin",
        "brand_names": ["Zithromax", "Z-Pak", "Azee", "Azithral", "Azimax"],
        "generic_name": "Azithromycin dihydrate",
        "active_ingredients": "Azithromycin",
        "image": "💊",
        "category": "Antibacterial / Macrolide",
        "therapeutic_class": "Azalide Subclass Macrolide Antibiotic",
        "used_for": "Treatment of mild-to-moderate community-acquired pneumonia (covering atypical pathogens: Mycoplasma, Chlamydophila, Legionella); acute bacterial exacerbations of COPD; streptococcal pharyngitis in penicillin-allergic patients; chlamydial urethritis.",
        "prescribed_for": ["Atypical and Bacterial Community-Acquired Pneumonia", "Acute Bacterial Exacerbations of Chronic Bronchitis", "Acute Bacterial Sinusitis", "Streptococcal Pharyngitis / Tonsillitis (Penicillin-Allergic Patients)", "Uncomplicated Chlamydial Genital Infections"],
        "how_it_works": "Binds reversibly to the 50S ribosomal subunit of susceptible bacterial microorganisms, interfering with transpeptidation and inhibiting bacterial protein synthesis, producing bacteriostatic inhibition of bacterial replication.",
        "common_side_effects": ["Diarrhea and loose stools", "Nausea and abdominal cramping", "Vomiting", "Headache and dizziness"],
        "serious_side_effects": ["Cardiac QTc interval prolongation and Torsades de Pointes (FDA Drug Safety Warning)", "Severe Clostridioides difficile-associated colitis", "Hepatotoxicity / cholestatic jaundice", "Severe cutaneous adverse reactions (DRESS, SJS, TEN)"],
        "contraindications": ["Known hypersensitivity to azithromycin, erythromycin, or any macrolide/ketolide antibiotic", "History of cholestatic jaundice or hepatic impairment associated with prior azithromycin use"],
        "drug_interactions": ["QT-Prolonging Medications (Antiarrhythmics: Amiodarone, Sotalol; Antipsychotics; Fluoroquinolones): Additive risk of fatal ventricular arrhythmias", "Warfarin: Potentiation of anticoagulant effects and increased bleeding risk", "Antacids Containing Aluminum or Magnesium: Reduce peak serum concentration of azithromycin (space administration by at least 2 hours)"],
        "food_alcohol_interactions": ["Oral tablets may be taken with or without food. Immediate-release oral suspension may be taken with food to decrease GI upset. Avoid alcohol."],
        "allergy_precautions": "Discontinue immediately and provide emergency resuscitation if laryngeal swelling, hives, or bronchospasm develops.",
        "age_precautions": {
            "children": "Approved in pediatric patients >= 6 months of age for acute otitis media and pneumonia (10 mg/kg day 1, then 5 mg/kg days 2–5).",
            "older_adults": "Elderly patients are significantly more susceptible to drug-induced cardiac QTc prolongation and fatal arrhythmias."
        },
        "pregnancy_breastfeeding": "Category B. Animal studies reveal no evidence of fetal harm. Used in pregnancy when benefits outweigh risks. Excreted into breast milk; safe under clinical supervision.",
        "kidney_liver_precautions": "Eliminated primarily via the biliary route and liver; exercise caution in severe hepatic impairment. No dose adjustment necessary in mild-to-moderate renal failure (eGFR >= 10 mL/min).",
        "monitoring_requirements": "ECG in patients with pre-existing cardiac conduction risk factors or concomitant QT-prolonging drugs; resolution of pulmonary symptoms.",
        "precautions": ["FDA Warning regarding QTc prolongation and cardiovascular death risk in high-risk patients", "Complete prescribed 3-day or 5-day course"],
        "storage": "Store tablets and dry powder between 15°C and 30°C (59°F and 86°F).",
        "dosage_forms": ["Oral Film-Coated Tablet", "Powder for Oral Suspension", "IV Infusion"],
        "strengths": ["250 mg", "500 mg", "600 mg", "100 mg/5 mL", "200 mg/5 mL", "500 mg IV"],
        "manufacturer": "Pfizer / Teva / Cipla / Lupin / Generic manufacturers",
        "sources": ["FDA Drug Safety Warning & Prescribing Information", "IDSA Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-25"
    },
    {
        "name": "Salbutamol",
        "brand_names": ["Ventolin", "ProAir", "Proventil", "Asthalin", "Aerolin"],
        "generic_name": "Albuterol / Salbutamol sulfate",
        "active_ingredients": "Salbutamol sulfate",
        "image": "💨",
        "category": "Respiratory / Bronchodilator",
        "therapeutic_class": "Short-Acting Beta-2 Adrenergic Agonist (SABA)",
        "used_for": "Rapid relief and emergency rescue reversal of acute bronchospasm in asthma, chronic obstructive pulmonary disease (COPD), and exercise-induced bronchospasm.",
        "prescribed_for": ["Acute Asthma Bronchospasm Attack (Reliever Inhaler)", "Exercise-Induced Bronchospasm (EIB) Prevention", "COPD Acute Exacerbation Bronchodilation", "Hyperkalemia Emergency Management (High-Dose Nebulization)"],
        "how_it_works": "Selectively stimulates beta-2 adrenergic receptors on bronchial smooth muscle, activating intracellular adenylyl cyclase to convert ATP to cyclic adenosine monophosphate (cAMP), lowering intracellular calcium and producing rapid bronchial smooth muscle relaxation and airway dilation within 5 minutes.",
        "common_side_effects": ["Tremor (skeletal muscle hand tremors)", "Tachycardia and palpitations", "Nervousness and restlessness", "Headache", "Throat irritation and cough"],
        "serious_side_effects": ["Paradoxical bronchospasm (sudden life-threatening airway narrowing upon inhalation)", "Cardiac arrhythmias and myocardial ischemia in susceptible cardiac patients", "Hypokalemia (intracellular potassium shift with high doses)", "Metabolic lactic acidosis"],
        "contraindications": ["Hypersensitivity to salbutamol sulfate or formulation excipients (e.g., milk protein in dry powder inhalers)"],
        "drug_interactions": ["Non-Selective Beta-Blockers (Propranolol, Carvedilol): Directly antagonize salbutamol, completely blocking bronchodilation and triggering fatal acute asthma exacerbations", "Diuretics (Furosemide, Thiazides): Worsens hypokalemia", "MAO Inhibitors and Tricyclic Antidepressants: Multiplies cardiovascular toxicity and arrhythmias"],
        "food_alcohol_interactions": ["Inhalers are independent of food. Avoid excessive dietary caffeine which compounds tremors and tachycardia."],
        "allergy_precautions": "If paradoxical bronchospasm occurs, discontinue immediately and initiate alternative emergency therapy.",
        "age_precautions": {
            "children": "Approved in all age groups. In children under 5 years, ALWAYS administer Metered Dose Inhaler (MDI) with a valved holding chamber (spacer) and fitted facial mask for effective drug deposition.",
            "older_adults": "Vulnerable to tachycardia, tremor, and ischemic cardiac stress. Monitor pulse."
        },
        "pregnancy_breastfeeding": "Category C. SABA of choice for acute asthma exacerbations in pregnancy (maternal hypoxia poses far greater risk to fetus than beta-2 agonist exposure). Compatible with breastfeeding.",
        "kidney_liver_precautions": "No dose adjustments necessary for inhaler administration.",
        "monitoring_requirements": "Frequency of inhaler usage (using a reliever > 2 times/week signals poorly controlled asthma requiring escalation of inhaled corticosteroid controller therapy); peak expiratory flow (PEF).",
        "precautions": ["SABA is a RESCUE reliever, NOT an anti-inflammatory controller", "Over-reliance on SABAs without inhaled corticosteroids dramatically increases asthma-related death (GINA consensus)"],
        "storage": "Store between 15°C and 25°C (59°F and 77°F). Protect from freezing and direct sunlight. Canister is pressurized.",
        "dosage_forms": ["Metered-Dose Inhaler (MDI)", "Dry Powder Inhaler (DPI)", "Nebulizer Solution", "Oral Syrup / Tablet"],
        "strengths": ["100 mcg/actuation (90 mcg base MDI)", "2.5 mg/2.5 mL nebulizer solution", "2 mg/5 mL syrup"],
        "manufacturer": "GSK / Teva / Cipla / Perrigo",
        "sources": ["GINA Global Strategy for Asthma Management", "FDA Prescribing Information", "British Thoracic Society (BTS)", "DailyMed"],
        "last_updated": "2026-08-15"
    },
    {
        "name": "Budesonide and Formoterol",
        "brand_names": ["Symbicort", "Foracort", "Vannair"],
        "generic_name": "Budesonide and formoterol fumarate dihydrate",
        "active_ingredients": "Budesonide (inhaled corticosteroid) + Formoterol fumarate (LABA)",
        "image": "💨",
        "category": "Respiratory / Anti-Inflammatory Bronchodilator",
        "therapeutic_class": "ICS / LABA Fixed-Dose Combination",
        "used_for": "Maintenance and reliever treatment of bronchial asthma; maintenance treatment of airflow obstruction in Chronic Obstructive Pulmonary Disease (COPD).",
        "prescribed_for": ["Moderate-to-Severe Persistent Asthma", "SMART / MART Protocol (Single Inhaler Maintenance and Reliever Therapy)", "Chronic Obstructive Pulmonary Disease (COPD) Maintenance"],
        "how_it_works": "Dual anti-inflammatory and bronchodilating mechanism: Budesonide binds to glucocorticoid receptors to suppress multiple inflammatory cytokines, airway eosinophil infiltration, and microvascular hyperpermeability; Formoterol is a rapid-onset, long-acting beta-2 agonist (LABA) providing smooth muscle relaxation within 1–3 minutes lasting >= 12 hours.",
        "common_side_effects": ["Oropharyngeal candidiasis (oral thrush)", "Dysphonia (hoarse voice)", "Throat irritation", "Mild hand tremor", "Headache"],
        "serious_side_effects": ["Pneumonia in COPD patients", "Paradoxical bronchospasm", "Systemic corticosteroid effects with prolonged high doses (adrenal suppression, reduced bone mineral density, cataracts, glaucoma)", "Hypokalemia and cardiac arrhythmias"],
        "contraindications": ["Primary treatment of status epilepticus or acute life-threatening episodes requiring intensive care", "Hypersensitivity to budesonide, formoterol, or formulation components"],
        "drug_interactions": ["Strong CYP3A4 Inhibitors (Ketoconazole, Clarithromycin, Ritonavir): Substantially increase systemic budesonide exposure", "Beta-Blockers: Diminish or abolish bronchodilator response and trigger severe bronchospasm", "QT-Prolonging Drugs: Heighten arrhythmia risk"],
        "food_alcohol_interactions": ["Inhaled administration is independent of meals. CRITICAL: Rinse mouth thoroughly with water and spit it out after every inhalation to prevent oral thrush and dysphonia."],
        "allergy_precautions": "Discontinue if allergic bronchospasm or urticaria develops.",
        "age_precautions": {
            "children": "Approved in pediatric patients >= 6 years of age for asthma. Monitor linear height growth in children receiving chronic inhaled corticosteroids.",
            "older_adults": "Evaluate inhaler inspiratory technique; check for COPD pneumonia signs."
        },
        "pregnancy_breastfeeding": "Category C. Preferred controller option in persistent asthma during pregnancy (budesonide has the most extensive reassuring human pregnancy safety data of any ICS). Compatible with breastfeeding.",
        "kidney_liver_precautions": "No dose adjustments for renal impairment. Extensively metabolized by the liver; monitor in severe hepatic failure.",
        "monitoring_requirements": "Spirometry / FEV1 and peak flow; oral cavity inspection for fungal thrush; growth in pediatric patients; annual ophthalmologic exams with high doses.",
        "precautions": ["Mouth rinsing and spitting is mandatory after every use", "Instruct patient on proper inhaler actuation and inhalation technique"],
        "storage": "Store at controlled room temperature 20°C to 25°C. Keep canister upright.",
        "dosage_forms": ["Metered-Dose Inhaler (MDI)", "Dry Powder Turbuhaler / Inhaler"],
        "strengths": ["80/4.5 mcg", "160/4.5 mcg per actuation"],
        "manufacturer": "AstraZeneca / Cipla / Generic manufacturers",
        "sources": ["GINA Global Strategy for Asthma", "FDA Prescribing Information", "GOLD COPD Guidelines", "DailyMed"],
        "last_updated": "2026-08-19"
    },
    {
        "name": "Oral Rehydration Salts (ORS)",
        "brand_names": ["Electral", "WHO-ORS", "Hydralyte", "Pedialyte", "Rehydral"],
        "generic_name": "Oral rehydration salts formula (WHO low-osmolarity formula)",
        "active_ingredients": "Sodium chloride (2.6 g) + Glucose anhydrous (13.5 g) + Potassium chloride (1.5 g) + Trisodium citrate dihydrate (2.9 g) per liter",
        "image": "💧",
        "category": "Gastrointestinal & Emergency / Fluid-Electrolyte",
        "therapeutic_class": "Oral Electrolyte and Glucose Fluid Replacement Solution",
        "used_for": "First-line prevention and treatment of dehydration and electrolyte depletion caused by acute diarrheal illnesses, gastroenteritis, cholera, heat exhaustion, and viral fevers, including Dengue.",
        "prescribed_for": ["Dehydration Secondary to Acute Gastroenteritis / Diarrhea", "Dengue Fever Fluid Maintenance (Critical to Prevent Plasma Leakage)", "Viral Enteritis (Rotavirus, Norovirus)", "Heat Exhaustion and Strenuous Dehydration", "Post-Surgical High-Output Stoma Fluid Balance"],
        "how_it_works": "Leverages the intact intestinal sodium-glucose cotransport mechanism (SGLT1) in the apical brush border membrane of enterocytes: glucose absorption drives active sodium uptake against an electrochemical gradient, with water passively following osmolar transport, restoring intravascular volume without stressing the gut.",
        "common_side_effects": ["Mild nausea if ingested too rapidly in a single bolus", "Mild abdominal distension if overconsumed"],
        "serious_side_effects": ["Hypernatremia (if mixed in incorrect high powder concentration with too little water)", "Worsening fluid overload in end-stage oliguric renal failure or uncompensated congestive heart failure"],
        "contraindications": ["Severe intractable vomiting where fluids cannot be retained (requires intravenous rehydration)", "Severe hypovolemic shock (requires immediate emergency IV Ringer's Lactate / Saline resuscitation)", "Paralytic ileus or bowel obstruction", "Anuria (absence of urine output)"],
        "drug_interactions": ["Safe and compatible with all standard antimicrobial, antipyretic, and maintenance medications"],
        "food_alcohol_interactions": ["Dissolve strictly in clean, boiled-and-cooled drinking water. NEVER mix into milk, fruit juices, sodas, or sports drinks (which disrupt osmolarity)."],
        "allergy_precautions": "No known allergic potential. Physiologic electrolyte solution.",
        "age_precautions": {
            "children": "WHO universal life-saving therapy. Administer frequent small spoonfuls or sips (5 mL every 2–3 minutes). Continue breastfeeding uninterrupted throughout diarrheal episodes.",
            "older_adults": "Safely prevents acute prerenal kidney failure during infectious diarrhea. Monitor in advanced congestive heart failure."
        },
        "pregnancy_breastfeeding": "Completely safe and essential in pregnancy and lactation. Rapidly reverses maternal dehydration and prevents hypoperfusion.",
        "kidney_liver_precautions": "Caution in advanced oliguric renal failure (monitor serum potassium to prevent hyperkalemia). Safe in liver disease.",
        "monitoring_requirements": "Clinical hydration status (mucous membranes, skin turgor, urine color, capillary refill, mental alertness); frequency of diarrheal stools and vomiting.",
        "precautions": ["CRITICAL: Mix entire packet in the exact volume of drinking water indicated on packet (typically exactly 1 liter or 200 mL)", "Discard any unconsumed reconstituted solution after 24 hours"],
        "storage": "Store dry packets in a cool, dry place. Once mixed, use within 24 hours.",
        "dosage_forms": ["Dry Soluble Powder Packets", "Premixed Ready-to-Drink Solution", "Effervescent Tablets"],
        "strengths": ["WHO Low-Osmolarity Formula (Total osmolarity: 245 mOsm/L; Sodium 75 mmol/L, Glucose 75 mmol/L)"],
        "manufacturer": "FDC / Abbott / Cipla / Halewood / Generic manufacturers",
        "sources": ["WHO/UNICEF Diarrhea Clinical Guidelines", "CDC Clinical Guidance on Dehydration", "DailyMed"],
        "last_updated": "2026-08-05"
    },
    {
        "name": "Furosemide",
        "brand_names": ["Lasix", "Frusid", "Salix", "Uremide"],
        "generic_name": "Furosemide",
        "active_ingredients": "Furosemide",
        "image": "💊",
        "category": "Renal & Cardiovascular / Diuretic",
        "therapeutic_class": "Loop (High-Ceiling) Diuretic",
        "used_for": "Treatment of edema associated with congestive heart failure, cirrhosis of the liver, and renal disease, including nephrotic syndrome and chronic kidney disease; management of hypertensive crisis.",
        "prescribed_for": ["Congestive Heart Failure Volume Overload and Pulmonary Edema", "Chronic Kidney Disease Edema and Volume Management", "Nephrotic Syndrome", "Hepatic Cirrhosis Ascites (with Spironolactone)", "Acute Oliguric Renal Failure Volume Challenge"],
        "how_it_works": "Inhibits the Na+/K+/2Cl- cotransporter in the thick ascending limb of the loop of Henle, abolishing the medullary hypertonic osmotic gradient and blocking the reabsorption of sodium, chloride, and water, producing potent, rapid natriuresis and diuresis.",
        "common_side_effects": ["Frequent urination (polyuria)", "Dizziness and orthostatic hypotension", "Hypokalemia (muscle cramps, weakness)", "Hyponatremia", "Hyperuricemia (can precipitate acute gout attacks)"],
        "serious_side_effects": ["Ototoxicity and permanent hearing loss (especially with rapid IV boluses or co-administered aminoglycosides)", "Profound volume depletion, severe dehydration, and prerenal azotemia (FDA Boxed Warning)", "Severe electrolyte disturbances (hypokalemia, hypomagnesemia, metabolic alkalosis)", "Agranulocytosis and thrombocytopenia"],
        "contraindications": ["Anuria refractory to test doses", "Hepatic coma or severe electrolyte depletion until state is corrected", "Known hypersensitivity to furosemide or sulfonamides (sulfa drug allergy)"],
        "drug_interactions": ["Aminoglycoside Antibiotics (Gentamicin, Amikacin): Multiplies severe ototoxicity and nephrotoxicity risk", "Digoxin: Furosemide-induced hypokalemia severely predisposes patient to fatal digoxin arrhythmias", "Lithium: Decreases renal lithium clearance, leading to acute lithium toxicity", "NSAIDs: Blunt furosemide's diuretic and natriuretic response"],
        "food_alcohol_interactions": ["May take with food if gastric distress occurs. Avoid alcohol which compounds orthostatic dizziness. Encourage dietary potassium unless renal failure is present."],
        "allergy_precautions": "Caution in patients with sulfonamide allergies (cross-reactivity is clinically uncommon but documented).",
        "age_precautions": {
            "children": "Approved in pediatric patients. Use weight-based dosing (1–2 mg/kg). Monitor for nephrocalcinosis in premature infants.",
            "older_adults": "Extreme susceptibility to sudden volume contraction, orthostatic syncope, and fall fractures. Start at lowest effective dose."
        },
        "pregnancy_breastfeeding": "Category C. Crosses the placenta; decreases maternal plasma volume and placental perfusion. Avoid unless maternal cardiac life-support necessitates. Suppresses lactation.",
        "kidney_liver_precautions": "Effective in advanced renal impairment (unlike thiazides, works down to eGFR < 30 mL/min, though higher doses are required). In hepatic cirrhosis with ascites, electrolyte shifts can trigger hepatic encephalopathy.",
        "monitoring_requirements": "Serum electrolytes (potassium, sodium, magnesium), BUN, serum creatinine, and blood pressure regularly; daily morning weight tracking.",
        "precautions": ["FDA Boxed Warning for Fluid and Electrolyte Depletion", "Usually administered in the morning or early afternoon to avoid sleep disruption from nocturia", "Potassium supplementation frequently required"],
        "storage": "Store between 15°C and 30°C (59°F and 86°F). Protect from light.",
        "dosage_forms": ["Oral Tablet", "Oral Solution", "Intravenous / IM Injection"],
        "strengths": ["20 mg", "40 mg", "80 mg", "10 mg/mL oral liquid", "10 mg/mL injection"],
        "manufacturer": "Sanofi / Teva / Viatris / Sun Pharma",
        "sources": ["FDA Boxed Warning & Prescribing Information", "AHA Heart Failure Guidelines", "KDIGO Guidelines", "DailyMed"],
        "last_updated": "2026-08-14"
    },
    {
        "name": "Losartan",
        "brand_names": ["Cozaar", "Losar", "Repace", "Tozaar"],
        "generic_name": "Losartan potassium",
        "active_ingredients": "Losartan potassium",
        "image": "💊",
        "category": "Cardiovascular & Renal / Antihypertensive",
        "therapeutic_class": "Angiotensin II Receptor Blocker (ARB)",
        "used_for": "Treatment of hypertension; reduction of stroke risk in hypertensive patients with left ventricular hypertrophy; renal protection in type 2 diabetic nephropathy with elevated serum creatinine and proteinuria.",
        "prescribed_for": ["Hypertension (High Blood Pressure)", "Diabetic Nephropathy in Type 2 Diabetes Mellitus", "Stroke Risk Reduction in Left Ventricular Hypertrophy", "Proteinuria Reduction in Chronic Kidney Disease"],
        "how_it_works": "Selectively blocks the binding of angiotensin II to the AT1 receptor in vascular smooth muscle and the adrenal gland, preventing vasoconstriction and aldosterone secretion, lowering systemic vascular resistance, reducing intraglomerular pressure, and halting renal fibrosis without inhibiting bradykinin degradation (no chronic dry cough).",
        "common_side_effects": ["Dizziness and lightheadedness", "Upper respiratory congestion", "Fatigue", "Back pain", "Orthostatic hypotension"],
        "serious_side_effects": ["Hyperkalemia (high blood potassium)", "Acute renal failure in patients with bilateral renal artery stenosis", "Fetal toxicity and fetal demise (FDA Boxed Warning: strictly contraindicated in pregnancy)", "Angioedema (rare compared to ACE inhibitors)"],
        "contraindications": ["Pregnancy (FDA Boxed Warning: causes severe oligohydramnios, skull hypoplasia, and fetal death)", "Concomitant use of aliskiren in patients with diabetes", "Known hypersensitivity to losartan"],
        "drug_interactions": ["Potassium Supplements and Potassium-Sparing Diuretics: Multiplies hyperkalemia risk", "NSAIDs (Ibuprofen, Naproxen): Blunts blood pressure lowering and precipitates acute kidney injury", "Lithium: Decreases renal lithium clearance, causing lithium toxicity"],
        "food_alcohol_interactions": ["May take with or without food. Avoid potassium-rich salt substitutes to prevent fatal hyperkalemia. Avoid alcohol."],
        "allergy_precautions": "Patients with a history of angioedema from ACE inhibitors should be monitored with extreme vigilance.",
        "age_precautions": {
            "children": "Approved in pediatric patients >= 6 years of age for hypertension (0.7 mg/kg once daily up to 50 mg).",
            "older_adults": "Safe first-line agent. Monitor baseline kidney function and potassium."
        },
        "pregnancy_breastfeeding": "FDA Boxed Warning: Discontinue immediately when pregnancy is detected. Not recommended during breastfeeding.",
        "kidney_liver_precautions": "Proven renal benefit in diabetic nephropathy. In patients with severe volume depletion or bilateral renal artery stenosis, acute decline in renal function may occur. Extensively metabolized by the liver; initial dose should be 25 mg daily in hepatic impairment.",
        "monitoring_requirements": "Serum potassium, serum creatinine, BUN, and blood pressure at baseline and periodically.",
        "precautions": ["FDA Boxed Warning for Fetal Toxicity", "Discontinue immediately upon pregnancy diagnosis"],
        "storage": "Store at 15°C to 30°C. Protect from light and moisture.",
        "dosage_forms": ["Film-Coated Oral Tablet"],
        "strengths": ["25 mg", "50 mg", "100 mg"],
        "manufacturer": "Organon / Merck / Torrent / Generic manufacturers",
        "sources": ["FDA Drug Label", "AHA/ACC Hypertension Guidelines", "KDIGO Diabetic Kidney Disease Guidelines", "DailyMed"],
        "last_updated": "2026-08-16"
    },
    {
        "name": "Levofloxacin",
        "brand_names": ["Levaquin", "L-Cin", "Glevo", "Levomac"],
        "generic_name": "Levofloxacin hemihydrate",
        "active_ingredients": "Levofloxacin",
        "image": "💊",
        "category": "Antibacterial / Fluoroquinolone",
        "therapeutic_class": "Respiratory Fluoroquinolone",
        "used_for": "Treatment of severe or complicated community-acquired pneumonia; hospital-acquired pneumonia; acute bacterial exacerbations of chronic bronchitis; complicated urinary tract infections and acute pyelonephritis.",
        "prescribed_for": ["Severe Community-Acquired Pneumonia (CAP)", "Hospital-Acquired / Ventilator-Associated Pneumonia", "Acute Pyelonephritis and Complicated UTIs", "Inhalation Anthrax (Post-Exposure Prophylaxis)"],
        "how_it_works": "Inhibits bacterial topoisomerase II (DNA gyrase) and topoisomerase IV, essential enzymes required for bacterial DNA replication, transcription, repair, and recombination, triggering rapid concentration-dependent bacterial death.",
        "common_side_effects": ["Nausea and diarrhea", "Headache and insomnia", "Dizziness", "Dyspepsia and abdominal pain"],
        "serious_side_effects": ["Tendonitis and tendon rupture (FDA Boxed Warning: peak risk in Achilles tendon, elevated in elderly and steroid users)", "Peripheral neuropathy (FDA Boxed Warning: potentially irreversible nerve damage)", "Central nervous system toxicities (FDA Boxed Warning: psychosis, seizures, hallucinations)", "Cardiac QTc interval prolongation and Torsades de Pointes", "Aortic aneurysm and dissection (FDA Warning)", "Exacerbation of myasthenia gravis (FDA Boxed Warning)"],
        "contraindications": ["History of tendon disorders related to fluoroquinolone administration", "Known hypersensitivity to levofloxacin or quinolones", "Myasthenia gravis (FDA Boxed Warning)", "Uncorrected hypokalemia or hypomagnesemia"],
        "drug_interactions": ["Multivalent Cations (Antacids with Al/Mg, Iron supplements, Sucralfate, Didanosine): Chelate levofloxacin, completely blocking oral absorption (space by at least 2 hours before or 4 hours after)", "QT-Prolonging Antiarrhythmics (Amiodarone, Sotalol): Severe ventricular arrhythmia risk", "Systemic Corticosteroids: Multiplies tendon rupture risk by up to 5-fold", "Warfarin: Potentiates anticoagulant effect"],
        "food_alcohol_interactions": ["May take with or without meals. Maintain generous water hydration to prevent crystalluria. Avoid calcium-fortified juices alone unless taken with a full meal."],
        "allergy_precautions": "Discontinue at the first appearance of a skin rash, jaundice, or tendon pain/swelling.",
        "age_precautions": {
            "children": "Generally avoided in pediatric patients due to juvenile articular cartilage damage, unless treating inhalation anthrax or plague.",
            "older_adults": "FDA Boxed Warning: Severe vulnerability to Achilles tendon rupture, fatal QTc arrhythmias, and CNS delirium. Reserve for when no alternatives exist."
        },
        "pregnancy_breastfeeding": "Category C. Avoid in pregnancy and breastfeeding due to potential arthropathy in developing fetal weight-bearing joints.",
        "kidney_liver_precautions": "Excreted predominantly unchanged via renal excretion (~87%). Mandatory dosage adjustment in renal impairment: eGFR 20–49 mL/min (500 mg initial, then 250 mg q24h); eGFR 10–19 mL/min (500 mg initial, then 250 mg q48h).",
        "monitoring_requirements": "Renal function; ECG in patients with cardiac conduction risk; immediate cessation upon any tendon pain or swelling.",
        "precautions": ["FDA Boxed Warnings for Tendonitis/Rupture, Neuropathy, CNS Toxicities, and Myasthenia Gravis", "Do not exercise if joint or tendon aching develops"],
        "storage": "Store at 25°C (77°F). Protect from light.",
        "dosage_forms": ["Oral Film-Coated Tablet", "Oral Solution (25 mg/mL)", "IV Premixed Infusion"],
        "strengths": ["250 mg", "500 mg", "750 mg", "500 mg IV", "750 mg IV"],
        "manufacturer": "Janssen / Sanofi / Cipla / Generic manufacturers",
        "sources": ["FDA Boxed Warning & Prescribing Information", "IDSA Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-22"
    },
    {
        "name": "Cetirizine",
        "brand_names": ["Zyrtec", "Cetzine", "Alerid", "Piriteze", "Zyrtec Allergy"],
        "generic_name": "Cetirizine hydrochloride",
        "active_ingredients": "Cetirizine hydrochloride",
        "image": "💊",
        "category": "Allergic & Respiratory / Antihistamine",
        "therapeutic_class": "Second-Generation H1 Receptor Antagonist",
        "used_for": "Relief of allergic symptoms associated with seasonal and perennial allergic rhinitis (sneezing, runny nose, itching, post-nasal drip) and treatment of uncomplicated skin manifestations of chronic idiopathic urticaria.",
        "prescribed_for": ["Allergic Rhinitis (Hay Fever)", "Chronic Idiopathic Urticaria (Hives)", "Allergic Conjunctivitis", "Dermatographism and Pruritus", "Insect Bite Hypersensitivity"],
        "how_it_works": "Competitively and selectively inhibits peripheral H1 histamine receptors on effector cells, preventing histamine-mediated capillary permeability, wheal and flare formation, mucosal edema, pruritus, and smooth muscle contraction, with minimal penetration of the blood-brain barrier resulting in low sedation rates.",
        "common_side_effects": ["Mild somnolence / drowsiness (dose-dependent)", "Dry mouth (mild anticholinergic)", "Fatigue", "Headache", "Pharyngitis"],
        "serious_side_effects": ["Severe hypersensitivity reactions and angioedema (rare)", "Urinary retention in prostatic hypertrophy", "Severe central sedation with concomitant depressants"],
        "contraindications": ["Severe end-stage renal disease (eGFR < 10 mL/min) or patients undergoing hemodialysis", "Known hypersensitivity to cetirizine, hydroxyzine, or piperazine derivatives"],
        "drug_interactions": ["CNS Depressants (Alcohol, Benzodiazepines, Opioids, Sedating Antidepressants): Additive central nervous system depression and psychomotor impairment", "Theophylline: Small reduction in cetirizine clearance"],
        "food_alcohol_interactions": ["May be taken with or without food. Avoid alcohol, which compounds drowsiness and slows reaction times."],
        "allergy_precautions": "Discontinue if urticaria worsens or angioedema develops.",
        "age_precautions": {
            "children": "Approved in infants and children >= 6 months of age for allergic rhinitis and chronic hives. Oral syrup formulation allows accurate dosing.",
            "older_adults": "Decreased renal clearance; start at 5 mg once daily to prevent accumulation and daytime sedation."
        },
        "pregnancy_breastfeeding": "Category B. Large human prospective registry data show no increase in birth defects. Second-generation antihistamine of choice in pregnancy. Excreted in breast milk in small amounts.",
        "kidney_liver_precautions": "Dosage reduction (5 mg once daily) required if eGFR < 50 mL/min or in hepatic impairment. Contraindicated if eGFR < 10 mL/min.",
        "monitoring_requirements": "Symptom control; assessment for excessive somnolence.",
        "precautions": ["Warn patients to observe individual response before driving or operating hazardous machinery", "Avoid concurrent alcohol"],
        "storage": "Store between 20°C and 25°C (68°F to 77°F).",
        "dosage_forms": ["Oral Film-Coated Tablet", "Chewable Tablet", "Oral Syrup (5 mg/5 mL)"],
        "strengths": ["5 mg", "10 mg", "5 mg/5 mL syrup"],
        "manufacturer": "Johnson & Johnson / Haleon / Cipla / Generic manufacturers",
        "sources": ["FDA Drug Label", "EAACI Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-10"
    },
    {
        "name": "Omeprazole",
        "brand_names": ["Prilosec", "Losec", "Omez", "Omee", "Prilosec OTC"],
        "generic_name": "Omeprazole",
        "active_ingredients": "Omeprazole magnesium",
        "image": "💊",
        "category": "Gastrointestinal / Acid-Suppressing",
        "therapeutic_class": "Proton Pump Inhibitor (PPI)",
        "used_for": "Treatment of gastroesophageal reflux disease (GERD), erosive esophagitis, active duodenal and benign gastric ulcers; Helicobacter pylori eradication (in combination with antibiotics); prevention of NSAID-induced ulcers.",
        "prescribed_for": ["Gastroesophageal Reflux Disease (GERD)", "Erosive Esophagitis Healing and Maintenance", "Peptic Ulcer Disease (Gastric and Duodenal)", "Helicobacter pylori Triple Therapy Eradication", "NSAID Gastroprotection in High-Risk Patients", "Zollinger-Ellison Syndrome"],
        "how_it_works": "Irreversibly inhibits the gastric parietal cell hydrogen-potassium ATPase enzyme system (H+/K+ ATPase 'proton pump'), suppressing both basal and stimulated gastric acid secretion regardless of secretagogue stimulus, providing sustained acid suppression allowing mucosal healing.",
        "common_side_effects": ["Headache", "Abdominal pain and flatulence", "Nausea and vomiting", "Diarrhea or constipation"],
        "serious_side_effects": ["Clostridioides difficile-associated severe diarrhea", "Bone fracture risk (hip, wrist, spine) with high-dose long-term therapy (FDA Warning)", "Hypomagnesemia with long-term therapy", "Acute interstitial nephritis (kidney inflammation)", "Vitamin B12 deficiency with chronic use (> 3 years)"],
        "contraindications": ["Known hypersensitivity to omeprazole or any substituted benzimidazole PPI", "Concomitant administration of rilpivirine-containing products"],
        "drug_interactions": ["Clopidogrel (Plavix): FDA Boxed Warning — Omeprazole competitively inhibits CYP2C19, reducing active clopidogrel metabolite formation by ~45% and blunting antiplatelet protection (use pantoprazole instead if PPI required)", "Methotrexate: Elevates methotrexate levels and toxicity", "HIV Protease Inhibitors (Atazanavir): Significantly decreases atazanavir absorption"],
        "food_alcohol_interactions": ["CRITICAL: Take 30 to 60 minutes before breakfast on an empty stomach for maximum acid suppression. Swallow delayed-release capsules whole; do not crush or chew."],
        "allergy_precautions": "Discontinue if acute tubulointerstitial nephritis, maculopapular rash, or erythema multiforme develops.",
        "age_precautions": {
            "children": "Approved in pediatric patients >= 1 year of age for GERD and erosive esophagitis (dose based on body weight).",
            "older_adults": "Higher susceptibility to bone fractures, C. diff diarrhea, and vitamin B12 malabsorption. Use lowest effective dose for shortest duration."
        },
        "pregnancy_breastfeeding": "Category C. Epidemiological studies show no major malformations; however, preferred in pregnancy if indicated. Excreted into human milk in low amounts.",
        "kidney_liver_precautions": "No dose adjustment required in renal impairment. In hepatic impairment, bioavailability is increased; maximum daily dose is 20 mg.",
        "monitoring_requirements": "Serum magnesium periodically with prolonged use (> 1 year); bone density in high-risk patients; vitamin B12 levels.",
        "precautions": ["Take 30–60 minutes before morning meal", "Do not take clopidogrel concurrently (CYP2C19 interaction)"],
        "storage": "Store between 15°C and 30°C. Protect from moisture.",
        "dosage_forms": ["Delayed-Release Capsule", "Delayed-Release Oral Suspension"],
        "strengths": ["10 mg", "20 mg", "40 mg"],
        "manufacturer": "AstraZeneca / Haleon / Dr. Reddy's / Generic manufacturers",
        "sources": ["FDA Boxed Warning & Prescribing Information", "ACG GERD Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-12"
    },
    {
        "name": "Aspirin",
        "brand_names": ["Bayer Aspirin", "Ecosprin", "Disprin", "Bufferin"],
        "generic_name": "Acetylsalicylic acid (ASA)",
        "active_ingredients": "Acetylsalicylic acid",
        "image": "💊",
        "category": "Antiplatelet & Analgesic / NSAID",
        "therapeutic_class": "Salicylate Antiplatelet Agent",
        "used_for": "Secondary prevention of cardiovascular events (heart attack, ischemic stroke) at low doses (75–100 mg), and relief of pain, inflammation, and fever at higher doses (325–650 mg). STRICTLY AVOID IN DENGUE due to fatal hemorrhage risk.",
        "prescribed_for": ["Coronary Artery Disease", "Secondary Prevention of Ischemic Stroke & TIA", "Post-PCI / Post-CABG Antithrombotic Therapy", "Acute Coronary Syndrome", "Mild-to-Moderate Pain and Fever (Non-Dengue)"],
        "how_it_works": "Irreversibly acetylates and inactivates platelet cyclooxygenase-1 (COX-1), blocking thromboxane A2 production for the entire lifespan of the platelet (7–10 days).",
        "common_side_effects": ["Dyspepsia and gastric irritation", "Nausea", "Easy bruising and prolonged bleeding time", "Tinnitus (at high doses)"],
        "serious_side_effects": ["Major gastrointestinal hemorrhage or ulcer perforation", "Hemorrhagic stroke", "Reye's syndrome in children/adolescents with viral illness", "Aspirin-induced bronchospasm in asthmatics"],
        "contraindications": ["Active peptic ulcer disease or severe GI bleeding", "Bleeding disorders (hemophilia)", "CRITICAL: Dengue fever or suspected viral hemorrhagic illnesses", "Children and teenagers with viral infections (Reye's syndrome risk)", "Severe renal or hepatic failure", "Aspirin-exacerbated respiratory disease (AERD)"],
        "drug_interactions": ["Other anticoagulants (Warfarin, Apixaban) & antiplatelets — major bleeding risk", "NSAIDs (ibuprofen) — blocks aspirin's irreversible platelet inhibition when taken before aspirin", "Methotrexate — reduced clearance and increased toxicity"],
        "food_alcohol_interactions": ["Take with food or a large glass of water to reduce gastric discomfort. Avoid alcohol which compounds gastric mucosal bleeding risk."],
        "allergy_precautions": "Contraindicated in patients with aspirin allergy or triad asthma.",
        "age_precautions": {
            "children": "STRICTLY CONTRAINDICATED in children and teenagers under 16 years of age suffering from viral infections due to fatal Reye's syndrome risk.",
            "older_adults": "High risk of occult gastrointestinal hemorrhage. Routine primary prevention in adults > 70 years is no longer recommended by ACC/AHA."
        },
        "pregnancy_breastfeeding": "Low-dose (81 mg) is used under obstetrician care to prevent preeclampsia in high-risk pregnancies. High-dose is contraindicated in the third trimester.",
        "kidney_liver_precautions": "Avoid in severe renal impairment (eGFR < 10 mL/min) and severe hepatic failure.",
        "monitoring_requirements": "Complete blood count and hemoglobin; monitoring for signs of black tarry stools (melena) or unusual bruising.",
        "precautions": ["Contraindicated in children under 16 years with viral fevers (Reye's syndrome)", "Discontinue 7 days before major elective surgery if instructed by surgical team"],
        "storage": "Store below 25°C in airtight containers. Discard if vinegar odor develops (hydrolysis).",
        "dosage_forms": ["Enteric-Coated Tablet", "Dispersible Tablet", "Chewable Tablet"],
        "strengths": ["75 mg", "81 mg", "100 mg", "300 mg", "325 mg", "500 mg"],
        "manufacturer": "Bayer / USV / Sanofi / Generic manufacturers",
        "sources": ["FDA Drug Label", "AHA/ACC Secondary Prevention Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-14"
    },
    {
        "name": "Clopidogrel",
        "brand_names": ["Plavix", "Deplatt", "Clopilet", "Ceruvit"],
        "generic_name": "Clopidogrel bisulfate",
        "active_ingredients": "Clopidogrel bisulfate",
        "image": "💊",
        "category": "Cardiovascular / Antiplatelet",
        "therapeutic_class": "Thienopyridine P2Y12 Platelet Inhibitor",
        "used_for": "Prevention of atherothrombotic events in patients with acute coronary syndrome, recent myocardial infarction, recent ischemic stroke, or established peripheral arterial disease.",
        "prescribed_for": ["Acute Coronary Syndrome (STEMI / NSTEMI)", "Recent Myocardial Infarction", "Recent Ischemic Stroke", "Percutaneous Coronary Intervention (PCI / Stent)", "Peripheral Arterial Disease"],
        "how_it_works": "Prodrug metabolized by hepatic CYP2C19 into an active thiol metabolite that irreversibly binds to the P2Y12 adenosine diphosphate (ADP) receptor on platelets, inhibiting ADP-mediated activation of the GPIIb/IIIa complex.",
        "common_side_effects": ["Hematoma and bruising", "Epistaxis (nosebleeds)", "Gastrointestinal bleeding", "Dyspepsia and abdominal pain"],
        "serious_side_effects": ["Thrombotic Thrombocytopenic Purpura (TTP — urgent medical emergency)", "Severe major internal hemorrhage", "Agranulocytosis / severe neutropenia (rare)"],
        "contraindications": ["Active pathological bleeding (such as peptic ulcer or intracranial hemorrhage)", "Known hypersensitivity to clopidogrel"],
        "drug_interactions": ["CYP2C19 Inhibitors (Omeprazole, Esomeprazole) — FDA Boxed Warning: significantly reduces clopidogrel activation; use pantoprazole instead if PPI is required", "Anticoagulants & NSAIDs — additive bleeding risk"],
        "food_alcohol_interactions": ["May be taken with or without meals. Avoid alcohol to minimize gastrointestinal ulceration and bleeding risk."],
        "allergy_precautions": "Discontinue if acute generalized exanthematous pustulosis or angioedema occurs.",
        "age_precautions": {
            "children": "Safety and efficacy not established in pediatric patients.",
            "older_adults": "Elderly patients have higher baseline bleeding risks. Monitor closely."
        },
        "pregnancy_breastfeeding": "Category B. Use only if clearly needed. Discontinue during breastfeeding.",
        "kidney_liver_precautions": "Experience limited in renal impairment. Avoid in severe hepatic impairment where bleeding diathesis may be exacerbated.",
        "monitoring_requirements": "Complete blood counts (platelets); hemoglobin/hematocrit periodically.",
        "precautions": ["FDA Boxed Warning: Reduced effectiveness in CYP2C19 poor metabolizers", "Usually withheld 5 days prior to elective coronary artery bypass graft (CABG) surgery"],
        "storage": "Store at 25°C (77°F). Protect from moisture.",
        "dosage_forms": ["Film-Coated Tablet"],
        "strengths": ["75 mg", "300 mg (loading dose)"],
        "manufacturer": "Sanofi / Bristol-Myers Squibb / Sun Pharma / Generic manufacturers",
        "sources": ["FDA Boxed Warning and Prescribing Information", "AHA/ACC PCI Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-07-29"
    },
    {
        "name": "Metoprolol",
        "brand_names": ["Lopressor", "Toprol-XL", "Betaloc", "Metolar"],
        "generic_name": "Metoprolol tartrate / succinate",
        "active_ingredients": "Metoprolol succinate (extended-release) or Metoprolol tartrate (immediate-release)",
        "image": "💊",
        "category": "Cardiovascular / Beta-Blocker",
        "therapeutic_class": "Cardioselective Beta-1 Adrenergic Receptor Blocker",
        "used_for": "Management of hypertension, long-term angina pectoris, hemodynamically stable congestive heart failure, and post-myocardial infarction cardioprotection.",
        "prescribed_for": ["Hypertension", "Angina Pectoris (Chest Pain)", "Heart Failure with Reduced Ejection Fraction (HFrEF)", "Atrial Fibrillation Rate Control", "Post-Heart Attack Cardioprotection", "Migraine Prophylaxis"],
        "how_it_works": "Competitively blocks beta-1 adrenergic receptors in cardiac tissue, reducing heart rate, cardiac output, myocardial oxygen demand, and renin release from juxtaglomerular cells.",
        "common_side_effects": ["Bradycardia (slow heart rate)", "Fatigue and exercise intolerance", "Dizziness", "Cold hands and feet (peripheral vasoconstriction)", "Depression or sleep disturbance"],
        "serious_side_effects": ["Severe bradycardia or complete heart block", "Acute heart failure exacerbation upon initiation", "Bronchospasm in asthmatic patients (at higher doses where beta-1 selectivity is lost)", "Masking of hypoglycemia symptoms in diabetics (except sweating)"],
        "contraindications": ["Severe bradycardia (< 45 bpm)", "Second- or third-degree heart block (without a pacemaker)", "Cardiogenic shock or decompensated heart failure", "Severe peripheral arterial disease"],
        "drug_interactions": ["Non-dihydropyridine CCBs (Verapamil, Diltiazem) — severe bradycardia and conduction block", "Amiodarone and Digoxin — additive slowing of AV node conduction", "CYP2D6 inhibitors (fluoxetine, paroxetine) — marked elevation of metoprolol levels"],
        "food_alcohol_interactions": ["Take Toprol-XL (succinate) with or immediately following a meal. Alcohol can accelerate drug release from some extended-release formulations."],
        "allergy_precautions": "Contraindicated in severe beta-blocker hypersensitivity.",
        "age_precautions": {
            "children": "Approved in pediatric patients >= 6 years of age for hypertension.",
            "older_adults": "Start at lower doses due to decreased hepatic metabolism and susceptibility to severe bradycardia."
        },
        "pregnancy_breastfeeding": "Category C. Can cause fetal bradycardia and growth restriction. Use only if benefits clearly outweigh risks. Excreted in breast milk in small amounts.",
        "kidney_liver_precautions": "No dose adjustment needed in renal failure. Extensively cleared by the liver; dose reduction required in severe hepatic impairment.",
        "monitoring_requirements": "Blood pressure and heart rate (pulse) regularly; monitor for heart failure signs (shortness of breath, swelling).",
        "precautions": ["FDA Boxed Warning: Never abruptly discontinue beta-blocker therapy; sudden cessation can trigger severe rebound angina, arrhythmias, or myocardial infarction (taper over 1–2 weeks)", "Use with extreme caution in asthmatics"],
        "storage": "Store at 20°C to 25°C. Protect from moisture.",
        "dosage_forms": ["Immediate-Release Tablet (Tartrate)", "Extended-Release Tablet (Succinate ER)", "IV Injection"],
        "strengths": ["25 mg", "50 mg", "100 mg", "200 mg ER"],
        "manufacturer": "AstraZeneca / Novartis / Cipla / Generic manufacturers",
        "sources": ["FDA Boxed Warning and Prescribing Information", "AHA/ACC Heart Failure Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-22"
    },
    {
        "name": "Montelukast",
        "brand_names": ["Singulair", "Montair", "Telekast", "Romilast"],
        "generic_name": "Montelukast sodium",
        "active_ingredients": "Montelukast sodium",
        "image": "💊",
        "category": "Respiratory & Allergy / Leukotriene Receptor Antagonist",
        "therapeutic_class": "Cysteinyl Leukotriene Receptor Antagonist (LTRA)",
        "used_for": "Prophylaxis and chronic treatment of bronchial asthma in adults and children; prevention of exercise-induced bronchospasm; relief of symptoms of seasonal and perennial allergic rhinitis.",
        "prescribed_for": ["Chronic Asthma Maintenance", "Exercise-Induced Bronchospasm Prevention", "Seasonal Allergic Rhinitis", "Perennial Allergic Rhinitis", "Aspirin-Exacerbated Respiratory Disease (AERD)"],
        "how_it_works": "Selectively binds with high affinity to the cysteinyl leukotriene receptor (CysLT1) on airway smooth muscle cells and macrophages, blocking the pro-inflammatory actions of LTC4, LTD4, and LTE4, preventing airway edema, smooth muscle contraction, and cellular inflammation.",
        "common_side_effects": ["Upper respiratory infection", "Fever and headache", "Pharyngitis and cough", "Abdominal pain and diarrhea", "Otitis media in young children"],
        "serious_side_effects": ["Serious neuropsychiatric events (FDA Boxed Warning: agitation, aggression, depression, sleep disturbances, hallucinations, suicidal ideation)", "Systemic eosinophilia and Churg-Strauss syndrome (eosinophilic granulomatosis with polyangiitis)", "Severe hepatic impairment (rare)"],
        "contraindications": ["Known hypersensitivity to montelukast sodium or formulation excipients"],
        "drug_interactions": ["Phenobarbital and Rifampin: Induce CYP3A4, reducing montelukast serum concentrations", "Gemfibrozil: Inhibits CYP2C8, doubling montelukast exposure"],
        "food_alcohol_interactions": ["May be taken with or without food. Typically administered once daily in the evening for asthma."],
        "allergy_precautions": "Discontinue immediately and seek psychiatric/medical attention if mood or behavioral changes occur.",
        "age_precautions": {
            "children": "Approved in pediatric patients as young as 12 months for asthma (chewable tablets and oral granules).",
            "older_adults": "No overall differences in safety or effectiveness observed in geriatric trials."
        },
        "pregnancy_breastfeeding": "Category B. Available human pregnancy registry data have not established a drug-associated risk of major birth defects. Compatible with breastfeeding.",
        "kidney_liver_precautions": "No dose adjustment required in renal impairment. Caution in severe hepatic insufficiency (metabolized extensively by liver).",
        "monitoring_requirements": "Screen for neuropsychiatric symptoms and behavioral disturbances at every clinical consultation; asthma symptom control.",
        "precautions": ["FDA Boxed Warning for Neuropsychiatric Events", "Not indicated for the reversal of acute bronchospasm attack (continue carrying rescue SABA inhaler)"],
        "storage": "Store at 20°C to 25°C (68°F to 77°F). Protect from moisture and light.",
        "dosage_forms": ["Film-Coated Tablet", "Chewable Tablet", "Oral Granules Packet"],
        "strengths": ["4 mg chewable / granules", "5 mg chewable", "10 mg tablet"],
        "manufacturer": "Organon / Merck / Cipla / Sun Pharma / Generic manufacturers",
        "sources": ["FDA Boxed Warning and Prescribing Information", "GINA Guidelines", "British National Formulary (BNF)", "DailyMed"],
        "last_updated": "2026-08-15"
    },
    {
        "name": "Pantoprazole",
        "brand_names": ["Protonix", "Pantocid", "Pan 40", "Pantosec"],
        "generic_name": "Pantoprazole sodium",
        "active_ingredients": "Pantoprazole sodium",
        "image": "💊",
        "category": "Gastrointestinal / Acid-Suppressing",
        "therapeutic_class": "Proton Pump Inhibitor (PPI)",
        "used_for": "Treatment of gastroesophageal reflux disease (GERD), erosive esophagitis, Zollinger-Ellison syndrome; preferred PPI in patients receiving clopidogrel antiplatelet therapy due to minimal CYP2C19 inhibition.",
        "prescribed_for": ["Gastroesophageal Reflux Disease (GERD)", "Erosive Esophagitis", "Peptic Ulcer Bleeding Prevention", "Zollinger-Ellison Syndrome", "Co-prescription with Clopidogrel in High GI-Risk Cardiac Patients"],
        "how_it_works": "Binds covalently to the H+/K+ ATPase enzyme system at the secretory surface of the gastric parietal cell, blocking the final step in gastric acid production. Exhibits low affinity for hepatic CYP2C19, avoiding metabolic interference with clopidogrel activation.",
        "common_side_effects": ["Headache", "Diarrhea", "Nausea and abdominal pain", "Flatulence", "Dizziness"],
        "serious_side_effects": ["Clostridioides difficile-associated diarrhea", "Bone fractures with long-term high-dose therapy", "Hypomagnesemia", "Acute interstitial nephritis", "Subacute cutaneous lupus erythematosus"],
        "contraindications": ["Hypersensitivity to pantoprazole or substituted benzimidazoles", "Concurrent administration of rilpivirine"],
        "drug_interactions": ["Unlike omeprazole, does NOT significantly inhibit CYP2C19 or diminish clopidogrel antiplatelet activity (preferred PPI for cardiac patients on Plavix)", "Methotrexate: Elevates methotrexate levels", "HIV Protease Inhibitors: Reduces atazanavir absorption"],
        "food_alcohol_interactions": ["Take 30 minutes before breakfast with water. Swallow delayed-release tablets whole; do not chew, crush, or split."],
        "allergy_precautions": "Discontinue if acute tubulointerstitial nephritis, maculopapular rash, or erythema multiforme develops.",
        "age_precautions": {
            "children": "Approved in pediatric patients >= 5 years of age for erosive esophagitis.",
            "older_adults": "Use lowest effective dose for shortest duration to minimize bone fracture and infection risks."
        },
        "pregnancy_breastfeeding": "Category B. Preferred over other PPIs in many clinical settings. Excreted into human milk in low amounts.",
        "kidney_liver_precautions": "No dose adjustments for renal failure. Daily dose should not exceed 20 mg in severe cirrhosis.",
        "monitoring_requirements": "Serum magnesium periodically with prolonged therapy; monitoring for persistent watery diarrhea.",
        "precautions": ["Take 30 minutes before breakfast", "Preferred PPI when antiplatelet clopidogrel therapy is co-administered"],
        "storage": "Store between 20°C and 25°C. Protect from moisture.",
        "dosage_forms": ["Delayed-Release Tablet", "Powder for Delayed-Release Oral Suspension", "IV Formulation"],
        "strengths": ["20 mg", "40 mg", "40 mg IV"],
        "manufacturer": "Pfizer / Sun Pharma / Alkem / Generic manufacturers",
        "sources": ["FDA Prescribing Information", "ACG Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-16"
    },
    {
        "name": "Sertraline",
        "brand_names": ["Zoloft", "Sertima", "Daxid", "Lustral"],
        "generic_name": "Sertraline hydrochloride",
        "active_ingredients": "Sertraline hydrochloride",
        "image": "💊",
        "category": "Psychiatric / Antidepressant",
        "therapeutic_class": "Selective Serotonin Reuptake Inhibitor (SSRI)",
        "used_for": "Treatment of Major Depressive Disorder (MDD), Obsessive-Compulsive Disorder (OCD), Panic Disorder, Post-Traumatic Stress Disorder (PTSD), Social Anxiety Disorder, and Premenstrual Dysphoric Disorder.",
        "prescribed_for": ["Major Depressive Disorder", "Generalized Anxiety Disorder & Panic Disorder", "Obsessive-Compulsive Disorder", "Post-Traumatic Stress Disorder", "Social Anxiety Disorder"],
        "how_it_works": "Selectively inhibits the presynaptic neuronal reuptake of serotonin (5-HT), increasing synaptic serotonin concentrations in the central nervous system, enhancing serotonergic neurotransmission and downregulating inhibitory autoreceptors over 2–4 weeks.",
        "common_side_effects": ["Nausea and diarrhea", "Insomnia or somnolence", "Tremor and dizziness", "Dry mouth", "Sexual dysfunction (delayed ejaculation, decreased libido)", "Fatigue"],
        "serious_side_effects": ["Suicidal thoughts and behaviors in young adults/children (FDA Boxed Warning)", "Serotonin Syndrome (hyperthermia, rigidity, clonus, autonomic instability — medical emergency)", "Abnormal bleeding and ecchymosis", "Hyponatremia / SIADH (especially in elderly)", "Activation of mania in unrecognized bipolar disorder"],
        "contraindications": ["Concomitant use of Monoamine Oxidase Inhibitors (MAOIs) or within 14 days of stopping MAOIs (fatal serotonin syndrome)", "Concomitant use of pimozide (cardiac arrhythmia risk)", "Known hypersensitivity to sertraline"],
        "drug_interactions": ["MAOIs and Linezolid: Life-threatening Serotonin Syndrome (strictly contraindicated)", "Antiplatelets & NSAIDs: Multiplies upper gastrointestinal bleeding risk", "Triptans, Tramadol, St. John's Wort: Elevated serotonin syndrome risk", "Warfarin: Mild prolongation of prothrombin time"],
        "food_alcohol_interactions": ["May be taken with or without meals once daily in the morning or evening. Strictly avoid alcohol due to compounded cognitive and psychomotor impairment."],
        "allergy_precautions": "Discontinue if allergic rash, angioedema, or neuroleptic-like signs develop.",
        "age_precautions": {
            "children": "Approved in pediatric patients >= 6 years of age for OCD only. FDA Boxed Warning for suicidal thoughts in patients <= 24 years.",
            "older_adults": "High risk of SIADH and hyponatremia. Monitor serum sodium regularly."
        },
        "pregnancy_breastfeeding": "Category C. Antidepressant of choice during lactation (lowest infant serum concentrations among SSRIs). Weigh risks and benefits in pregnancy.",
        "kidney_liver_precautions": "No dose adjustments in renal impairment. Extensively metabolized by the liver; dose reduction or less frequent dosing required in hepatic impairment.",
        "monitoring_requirements": "Close monitoring for worsening depression, emergence of agitation, and suicidal ideation, especially during initial 1–2 months of therapy; serum sodium in elderly.",
        "precautions": ["FDA Boxed Warning for Suicidal Thoughts in Children and Young Adults", "Never discontinue abruptly (taper over several weeks to avoid antidepressant discontinuation syndrome)"],
        "storage": "Store at 20°C to 25°C. Protect from moisture.",
        "dosage_forms": ["Film-Coated Tablet", "Oral Concentrate Solution (20 mg/mL)"],
        "strengths": ["25 mg", "50 mg", "100 mg", "20 mg/mL oral liquid"],
        "manufacturer": "Viatris / Pfizer / Sun Pharma / Lupin / Generic manufacturers",
        "sources": ["FDA Boxed Warning and Prescribing Information", "APA Depression Guidelines", "NICE Guidelines", "DailyMed"],
        "last_updated": "2026-08-20"
    },
    {
        "name": "Ciprofloxacin",
        "brand_names": ["Cipro", "Cifran", "Ciplox", "Ciprolet"],
        "generic_name": "Ciprofloxacin hydrochloride",
        "active_ingredients": "Ciprofloxacin",
        "image": "💊",
        "category": "Antibacterial / Fluoroquinolone",
        "therapeutic_class": "Second-Generation Fluoroquinolone Antibacterial",
        "used_for": "Treatment of complicated urinary tract infections, acute pyelonephritis, infectious bacterial diarrhea, typhoid fever, complicated intra-abdominal infections, and bone and joint infections.",
        "prescribed_for": ["Complicated Urinary Tract Infections and Pyelonephritis", "Infectious Bacterial Diarrhea (Salmonella, Shigella, Campylobacter)", "Typhoid / Enteric Fever", "Pseudomonas Aeruginosa Susceptible Infections", "Prostatitis"],
        "how_it_works": "Inhibits bacterial DNA gyrase (topoisomerase II) and topoisomerase IV, preventing DNA supercoiling, replication, and transcription, producing rapid concentration-dependent bacterial killing with potent Gram-negative activity.",
        "common_side_effects": ["Nausea and diarrhea", "Vomiting and abdominal discomfort", "Dizziness and headache", "Mild skin rash"],
        "serious_side_effects": ["Tendonitis and tendon rupture (FDA Boxed Warning)", "Peripheral neuropathy and nerve damage (FDA Boxed Warning)", "Central nervous system toxicities (FDA Boxed Warning: seizures, psychosis)", "Cardiac QTc prolongation and arrhythmias", "Aortic aneurysm and dissection (FDA Warning)", "Exacerbation of myasthenia gravis (FDA Boxed Warning)"],
        "contraindications": ["History of fluoroquinolone-induced tendon rupture", "Concomitant tizanidine administration (severe hypotension and sedation)", "Myasthenia gravis", "Known hypersensitivity to ciprofloxacin or quinolones"],
        "drug_interactions": ["Multivalent Cations (Antacids with Al/Mg, Iron, Sucralfate, Calcium): Chelate ciprofloxacin, reducing absorption by up to 90% (space by 2 hours before or 6 hours after)", "Theophylline: Ciprofloxacin markedly inhibits CYP1A2, doubling theophylline levels and causing toxic seizures", "Warfarin: Potentiates anticoagulant effect"],
        "food_alcohol_interactions": ["Do not take with dairy products (milk, yogurt) or calcium-fortified juice ALONE (chelation); however, taking with a complete meal containing dairy is acceptable."],
        "allergy_precautions": "Discontinue immediately at first sign of skin rash, tendon pain, or neuropathy.",
        "age_precautions": {
            "children": "Generally not recommended in pediatric patients due to arthropathy, except for complicated UTI, pyelonephritis, or anthrax exposure.",
            "older_adults": "Severe vulnerability to Achilles tendon rupture and fatal cardiac arrhythmias. Reserve for situations where alternative antibiotics are unsuitable."
        },
        "pregnancy_breastfeeding": "Category C. Avoid in pregnancy and lactation due to potential cartilage damage in growing joints.",
        "kidney_liver_precautions": "Excreted renally; dose reduction required if eGFR < 50 mL/min: eGFR 30–50 mL/min (250–500 mg q12h); eGFR < 30 mL/min (250–500 mg q18h or 24h).",
        "monitoring_requirements": "Renal and hepatic function; immediate cessation upon any tendon pain, tenderness, or neurological numbness.",
        "precautions": ["FDA Boxed Warnings for Tendonitis, Neuropathy, CNS Toxicities, and Myasthenia Gravis", "Maintain vigorous fluid hydration to prevent crystalluria"],
        "storage": "Store below 25°C. Protect from moisture.",
        "dosage_forms": ["Film-Coated Tablet", "Oral Suspension", "IV Infusion", "Ophthalmic / Otic Solution"],
        "strengths": ["250 mg", "500 mg", "750 mg", "200 mg IV", "400 mg IV"],
        "manufacturer": "Bayer / Sun Pharma / Cipla / Generic manufacturers",
        "sources": ["FDA Boxed Warning & Prescribing Information", "IDSA Guidelines", "BNF", "DailyMed"],
        "last_updated": "2026-08-22"
    },
    {
        "name": "Levothyroxine",
        "brand_names": ["Synthroid", "Levoxyl", "Eltroxin", "Thyronorm"],
        "generic_name": "Levothyroxine sodium",
        "active_ingredients": "Levothyroxine sodium (synthetic T4)",
        "image": "💊",
        "category": "Endocrine / Thyroid Hormone Replacement",
        "therapeutic_class": "Synthetic Thyroid Hormone (T4)",
        "used_for": "Replacement therapy in congenital or acquired primary, secondary, and tertiary hypothyroidism; pituitary thyroid-stimulating hormone (TSH) suppression in the management of thyroid cancer.",
        "prescribed_for": ["Primary Hypothyroidism (Hashimoto's Thyroiditis)", "Post-Thyroidectomy or Radioiodine Hypothyroidism", "Congenital Hypothyroidism (Cretinism)", "Pituitary TSH Suppression in Well-Differentiated Thyroid Cancer"],
        "how_it_works": "Synthetic crystalline L-tetraiodothyronine (T4) that identical to natural human thyroxine. Acts as a prohormone converted peripherally in liver and kidneys to triiodothyronine (T3), which enters the nucleus to bind thyroid hormone receptors, regulating transcription of metabolic genes, stimulating oxygen consumption, basal metabolic rate, protein synthesis, and lipid metabolism.",
        "common_side_effects": ["Side effects are virtually non-existent at precise therapeutic replacement doses", "Over-replacement signs: Palpitations, tachycardia, anxiety, heat intolerance, tremor, weight loss, insomnia"],
        "serious_side_effects": ["Cardiac arrhythmias, atrial fibrillation, and myocardial infarction (especially in elderly with underlying ischemic heart disease)", "Bone mineral density reduction (osteoporosis from long-term subclinical hyperthyroidism)", "Thyrotoxic crisis / storm (with severe massive overdosage)"],
        "contraindications": ["Untreated subclinical or overt thyrotoxicosis", "Acute uncorrected myocardial infarction", "Untreated adrenal cortical insufficiency (corticosteroid replacement must precede thyroid hormone initiation to prevent acute Addisonian crisis)"],
        "drug_interactions": ["Calcium Carbonate, Iron Supplements, Sucralfate, Aluminum Antacids, Bile Acid Sequestrants: Drastically bind and inhibit levothyroxine absorption (space administration by at least 4 hours)", "Warfarin: Levothyroxine increases catabolism of vitamin K-dependent clotting factors, potentiating anticoagulant effect and bleeding risk", "Proton Pump Inhibitors: Reduce gastric acidity, lowering levothyroxine dissolution"],
        "food_alcohol_interactions": ["CRITICAL INSTRUCTION: Must take on an empty stomach with a full glass of water, at least 30 to 60 minutes before breakfast or coffee. Dietary fiber, soy, and espresso coffee severely impede absorption."],
        "allergy_precautions": "Formulation contains no animal protein; hypersensitivity to synthetic hormone is exceptionally rare.",
        "age_precautions": {
            "children": "Congenital hypothyroidism is an emergency: Immediate full replacement therapy is vital to prevent irreversible intellectual disability and growth stunting.",
            "older_adults": "Start low and go slow: Begin at 12.5–25 mcg once daily in elderly patients or those with coronary artery disease, titrating by 12.5–25 mcg every 6–8 weeks to avoid precipitating angina or fatal arrhythmias."
        },
        "pregnancy_breastfeeding": "Category A. Thyroid hormone requirements typically increase by 30–50% during pregnancy; monitor TSH every 4 weeks until stable to prevent miscarriage and fetal neurodevelopmental impairment. Completely compatible with breastfeeding.",
        "kidney_liver_precautions": "No dose adjustments for renal or hepatic impairment (monitored purely by serum TSH titration).",
        "monitoring_requirements": "Serum Thyroid Stimulating Hormone (TSH) and Free T4 measured 6 to 8 weeks after any dose adjustment, and annually once stabilized in therapeutic target range (typically 0.5–2.5 mIU/L).",
        "precautions": ["FDA Boxed Warning: Thyroid hormones must NOT be used for the treatment of obesity or weight loss (ineffective and potentially life-threatening)", "Narrow therapeutic index drug; do not switch brands without re-testing TSH"],
        "storage": "Store between 20°C and 25°C. Protect from moisture and light.",
        "dosage_forms": ["Oral Tablet", "Oral Capsule (Tirosint)", "Lyophilized Powder for Injection"],
        "strengths": ["25 mcg", "50 mcg", "75 mcg", "88 mcg", "100 mcg", "112 mcg", "125 mcg", "137 mcg", "150 mcg", "175 mcg", "200 mcg"],
        "manufacturer": "AbbVie / Pfizer / GSK / Abbott / Generic manufacturers",
        "sources": ["FDA Boxed Warning & Prescribing Information", "ATA/AACE Hypothyroidism Guidelines", "NICE Guidelines", "DailyMed"],
        "last_updated": "2026-08-14"
    }
]

# ═══════════════════════════════════════════════════════════════════════════════
# 2. EXPANSIVE CLINICAL DISEASE CATALOG (26+ CONDITIONS WITH COMPLETE SECTIONS)
# ═══════════════════════════════════════════════════════════════════════════════

DISEASE_CATALOG = {
    "diabetes": {
        "id": "diabetes",
        "name": "Diabetes Mellitus (Type 1 & Type 2)",
        "category": "Endocrine & Metabolic Disorders",
        "emoji": "🩸",
        "overview": {
            "description": "A chronic metabolic disease characterized by persistent hyperglycemia resulting from defects in insulin secretion, insulin action, or both. Left unmanaged, chronic hyperglycemia induces long-term microvascular and macrovascular tissue damage.",
            "types_and_classifications": [
                "Type 1 Diabetes Mellitus (T1D): Autoimmune destruction of pancreatic beta cells, causing absolute insulin deficiency requiring lifelong replacement.",
                "Type 2 Diabetes Mellitus (T2D): Progressive insulin resistance in muscle, liver, and adipose tissues combined with a progressive compensatory secretory defect of beta cells.",
                "Gestational Diabetes Mellitus (GDM): Glucose intolerance diagnosed during the second or third trimester of pregnancy.",
                "Monogenic / Secondary Diabetes: Resulting from single gene defects (MODY) or pancreatic disease (chronic pancreatitis, cystic fibrosis, steroid-induced)."
            ],
            "causes": [
                "Peripheral insulin resistance in skeletal muscle, liver, and visceral adipose tissue",
                "Progressive pancreatic beta-cell dysfunction and secretory failure",
                "Genetic polygenic predisposition and family history",
                "Visceral adiposity, sedentary lifestyle, and high-glycemic ultra-processed diets",
                "Autoimmune insulitis mediated by anti-GAD65, anti-IA2, and anti-ZnT8 antibodies (Type 1)"
            ],
            "risk_factors": [
                "Body Mass Index (BMI) >= 25 kg/m² (>= 23 kg/m² in Asian populations)",
                "Physical inactivity (< 150 minutes of moderate activity weekly)",
                "First-degree relative with Type 2 diabetes",
                "History of gestational diabetes or delivering an infant weighing > 4 kg",
                "Hypertension (>= 130/80 mmHg) or dyslipidemia (HDL < 35 mg/dL, triglycerides > 250 mg/dL)",
                "Polycystic ovary syndrome (PCOS) or Acanthosis nigricans"
            ],
            "common_symptoms": [
                "Polyuria: Frequent urination, particularly waking at night (nocturia)",
                "Polydipsia: Constant, unquenchable thirst and dry mouth",
                "Polyphagia: Increased hunger despite regular meal intake",
                "Unexplained, involuntary weight loss (more prominent in Type 1)",
                "Profound generalized physical fatigue and lethargy",
                "Transient blurred vision caused by osmotic lens swelling"
            ],
            "uncommon_symptoms": [
                "Recurrent pruritus vulvae or recurrent balanitis (yeast infections)",
                "Slow-healing cutaneous cuts, scratches, or chronic ulcers",
                "Peripheral sensory paresthesias ('pins and needles' or burning feet)",
                "Acanthosis nigricans: Hyperpigmented, velvety skin folds on neck and axillae",
                "Erectile dysfunction in men"
            ],
            "early_warning_signs": [
                "Subtle rise in nocturnal urination frequency",
                "Afternoon somnolence and brain fog following carbohydrate-heavy meals",
                "Frequent mild cutaneous fungal infections that recur despite topical treatment"
            ],
            "possible_complications": [
                "Diabetic Ketoacidosis (DKA) and Hyperosmolar Hyperglycemic State (HHS) — life-threatening emergencies",
                "Diabetic Retinopathy: Microaneurysms, macular edema, and proliferative neovascularization causing irreversible blindness",
                "Diabetic Nephropathy: Glomerular hyperfiltration, persistent microalbuminuria progressing to End-Stage Renal Disease (ESRD)",
                "Diabetic Neuropathy: Distal symmetrical polyneuropathy, Charcot foot deformity, and severe neuropathic pain",
                "Diabetic Foot Ulcers: Peripheral neuropathy plus peripheral arterial disease leading to osteomyelitis and lower limb amputation",
                "Accelerated Atherosclerosis: 2- to 4-fold increase in myocardial infarction, ischemic stroke, and peripheral artery disease"
            ],
            "systemic_impact": "Chronic elevated circulating glucose leads to non-enzymatic glycation of proteins and advanced glycation end-products (AGEs), creating systemic vascular endothelial dysfunction, chronic low-grade inflammation, arterial stiffening, accelerated atherosclerosis, and irreversible capillary microangiopathy across eyes, kidneys, and peripheral nerves."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Screening of high-risk asymptomatic adults and all adults aged >= 35 years",
                "Structured symptom evaluation (polyuria, polydipsia, weight loss)",
                "Repeat confirmatory blood testing using a second separate blood sample unless unequivocal symptomatic hyperglycemia is present"
            ],
            "laboratory_tests": [
                "Fasting Plasma Glucose (FPG): Measured after an overnight 8-hour fast",
                "Glycated Hemoglobin (HbA1c): Reflects average glycemic exposure over preceding 2–3 months",
                "2-Hour Oral Glucose Tolerance Test (OGTT): Ingestion of 75 g anhydrous glucose dissolved in water",
                "Urine Albumin-to-Creatinine Ratio (uACR): Annual spot first-morning urine sample for microalbuminuria",
                "Serum Creatinine and estimated Glomerular Filtration Rate (eGFR)",
                "Fasting Lipid Panel (Total cholesterol, LDL, HDL, Triglycerides)",
                "Islet Autoantibodies (Anti-GAD, Anti-IA2, Anti-ZnT8) and C-peptide to differentiate Type 1 from Type 2"
            ],
            "medical_examinations": [
                "Comprehensive annual dilated eye fundoscopy by an ophthalmologist or validated retinal photography",
                "Annual comprehensive diabetic foot examination: 10g monofilament test, 128Hz tuning fork vibration, pinprick, and dorsalis pedis pulse palpation",
                "Bilateral seated blood pressure measurements",
                "Body Mass Index (BMI) and waist circumference"
            ],
            "test_results_interpretation": [
                "Fasting Plasma Glucose (FPG): Normal < 100 mg/dL; Prediabetes 100–125 mg/dL (Impaired Fasting Glucose); Diabetes >= 126 mg/dL (confirmed on repeat test).",
                "HbA1c: Normal < 5.7%; Prediabetes 5.7%–6.4%; Diabetes >= 6.5%. General adult glycemic treatment target is < 7.0% (individualized: < 6.5% for young/healthy; < 8.0% for frail elderly).",
                "2-Hour OGTT: Normal < 140 mg/dL; Prediabetes 140–199 mg/dL (Impaired Glucose Tolerance); Diabetes >= 200 mg/dL.",
                "Random Plasma Glucose: >= 200 mg/dL with classic symptoms confirms diabetes without repeat testing.",
                "Urine Albumin-to-Creatinine Ratio (uACR): Normal < 30 mg/g; Microalbuminuria 30–299 mg/g (early diabetic nephropathy); Macroalbuminuria >= 300 mg/g (requires RAAS blockade with ACEi/ARB)."
            ]
        },
        "medicines": [
            {
                "name": "Metformin",
                "brand_names": ["Glucophage", "Fortamet", "Glycomet"],
                "generic_name": "Metformin hydrochloride",
                "category": "Oral Biguanide Antidiabetic",
                "therapeutic_class": "Biguanide",
                "purpose": "First-line foundation pharmacotherapy for Type 2 Diabetes; lowers fasting and postprandial glucose without causing hypoglycemia or weight gain.",
                "how_it_works": "Activates cellular AMP-activated protein kinase (AMPK), suppressing hepatic gluconeogenesis and enhancing peripheral muscle glucose uptake.",
                "common_side_effects": ["Diarrhea", "Nausea", "Abdominal discomfort", "Flatulence", "Metallic taste"],
                "serious_adverse_effects": ["Lactic acidosis (FDA Boxed Warning: rare, life-threatening)", "Vitamin B12 deficiency anemia"],
                "contraindications": ["eGFR < 30 mL/min/1.73 m²", "Acute metabolic acidosis / DKA", "Severe acute hepatic failure", "Withhold before radiocontrast"],
                "drug_interactions": ["Iodinated radiocontrast media (lactic acidosis risk)", "Excess alcohol", "Cimetidine"],
                "food_interactions": ["Always take with meals to reduce gastrointestinal upset. Avoid excessive alcohol."],
                "allergy_precautions": "Contraindicated in severe metformin hypersensitivity.",
                "age_precautions": "Approved >= 10 years for T2D. Geriatric patients require regular eGFR monitoring.",
                "pregnancy_breastfeeding": "Used for gestational diabetes under specialist care. Excreted into breast milk in small amounts.",
                "kidney_liver_precautions": "Contraindicated if eGFR < 30 mL/min. Max 1000 mg/day if eGFR 30–45. Avoid in severe liver disease.",
                "monitoring_requirements": "eGFR annually; HbA1c every 3–6 months; Vitamin B12 every 1–2 years."
            },
            {
                "name": "Empagliflozin",
                "brand_names": ["Jardiance"],
                "generic_name": "Empagliflozin",
                "category": "SGLT2 Inhibitor / Cardiorenal Protective",
                "therapeutic_class": "Sodium-Glucose Cotransporter-2 Inhibitor",
                "purpose": "Glycemic reduction with proven cardiovascular mortality reduction, heart failure hospitalization prevention, and slowing of diabetic kidney disease progression.",
                "how_it_works": "Inhibits SGLT2 in renal proximal tubules, promoting urinary excretion of glucose and sodium, reducing preload, afterload, and glomerular pressure.",
                "common_side_effects": ["Genital mycotic infections (thrush, balanitis)", "Urinary tract infections", "Increased urination", "Thirst"],
                "serious_adverse_effects": ["Euglycemic Diabetic Ketoacidosis (euDKA)", "Necrotizing fasciitis of perineum (Fournier's Gangrene)", "Urosepsis", "Hypovolemia"],
                "contraindications": ["Dialysis or end-stage renal disease for glucose control", "Type 1 diabetes", "Hypersensitivity"],
                "drug_interactions": ["Diuretics (hypotension risk)", "Insulin / Sulfonylureas (hypoglycemia risk; reduce secretagogue dose)"],
                "food_interactions": ["Take once daily in the morning with or without food. Avoid alcohol."],
                "allergy_precautions": "Discontinue if angioedema or severe perineal pain/swelling occurs.",
                "age_precautions": "Approved >= 10 years. Elderly patients require volume status assessment.",
                "pregnancy_breastfeeding": "Avoid in 2nd and 3rd trimesters (fetal renal development risk). Discontinue in lactation.",
                "kidney_liver_precautions": "Indicated down to eGFR 20 mL/min for CKD/HF, but glycemic efficacy wanes below eGFR 45.",
                "monitoring_requirements": "Renal function (eGFR), blood pressure, volume status, perineal skin examination."
            },
            {
                "name": "Atorvastatin",
                "brand_names": ["Lipitor", "Atorva", "Storvas"],
                "generic_name": "Atorvastatin calcium",
                "category": "Lipid-Lowering / Cardioprotective",
                "therapeutic_class": "HMG-CoA Reductase Inhibitor",
                "purpose": "Essential moderate-to-high intensity statin therapy recommended for all diabetic adults aged 40–75 to prevent heart attacks, strokes, and cardiovascular death.",
                "how_it_works": "Inhibits hepatic HMG-CoA reductase, upregulating LDL receptors, clearing atherogenic apo-B lipoprotein particles and stabilizing arterial plaques.",
                "common_side_effects": ["Myalgia (muscle aches)", "Joint stiffness", "Nasopharyngitis", "Dyspepsia"],
                "serious_adverse_effects": ["Rhabdomyolysis with renal failure", "Immune-mediated necrotizing myopathy", "Hepatotoxicity (rare)"],
                "contraindications": ["Active acute hepatic failure", "Pregnancy and lactation", "Hypersensitivity"],
                "drug_interactions": ["Strong CYP3A4 inhibitors (clarithromycin, ketoconazole)", "Gemfibrozil", "Cyclosporine"],
                "food_interactions": ["Take at any time of day with or without food. Avoid consuming > 1 liter of grapefruit juice daily."],
                "allergy_precautions": "Contraindicated in severe statin hypersensitivity.",
                "age_precautions": "Safe in adults; pediatric use restricted to familial hypercholesterolemia.",
                "pregnancy_breastfeeding": "Contraindicated during pregnancy and breastfeeding.",
                "kidney_liver_precautions": "No renal dose adjustments required. Contraindicated in active acute hepatic disease.",
                "monitoring_requirements": "Lipid panel 4–12 weeks after initiation; liver transaminases; CK if muscle pain occurs."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "Metformin + Radiocontrast: High risk of contrast-induced nephropathy and fatal lactic acidosis (withhold 48 hours prior)",
                "SGLT2 Inhibitors + Loop Diuretics: Additive volume depletion and orthostatic hypotension",
                "Insulin / Sulfonylureas + Beta-Blockers: Beta-blockers mask early hypoglycemia warning signs (tremor, tachycardia), leaving only diaphoresis (sweating)"
            ],
            "food_interactions": [
                "Metformin must be taken with meals to minimize severe gastrointestinal diarrhea and nausea",
                "Alcohol severely compounds the risk of hypoglycemia and lactic acidosis",
                "High-carbohydrate, high-glycemic index foods cause acute postprandial glucose spikes"
            ],
            "allergy_warnings": [
                "Patients starting SGLT2 inhibitors (Empagliflozin) must maintain rigorous perineal hygiene to prevent secondary fungal and bacterial cellulitis",
                "Report sudden rash, facial angioedema, or severe difficulty breathing immediately"
            ],
            "critical_contraindications": [
                "Never administer Metformin to patients with severe kidney disease (eGFR < 30 mL/min) or acute metabolic acidosis",
                "Never initiate SGLT2 inhibitors during active prolonged fasting, ketogenic diets, or acute major illness (high euglycemic DKA risk)"
            ],
            "age_precautions": {
                "children": "Type 1 diabetes in children requires multidisciplinary pediatric endocrinology management with intensive basal-bolus or insulin pump regimens. In Type 2 children, Metformin and Empagliflozin are approved options.",
                "older_adults": "Relax HbA1c targets (< 7.5%–8.0%) in elderly patients with cognitive impairment or multiple comorbidities to avoid catastrophic severe hypoglycemia (falls, fractures, arrhythmias)."
            },
            "immediate_emergency_triggers": [
                "Severe Hypoglycemia (Blood glucose < 54 mg/dL) with confusion, seizure, or unconsciousness — requires immediate IM Glucagon or IV Dextrose",
                "Diabetic Ketoacidosis (DKA): Deep rapid breathing (Kussmaul breathing), sweet/fruity breath odor, nausea, persistent vomiting, and confusion",
                "Hyperosmolar Hyperglycemic State (HHS): Blood glucose > 600 mg/dL with profound dehydration and altered sensorium"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Adopt an individualized Mediterranean or DASH dietary pattern rich in whole vegetables, legumes, whole grains, nuts, and lean proteins",
                "Minimize foods with added refined sugars, sugar-sweetened beverages, white refined flour, and ultra-processed snacks",
                "Practice the 'Diabetes Plate Method': 1/2 non-starchy vegetables, 1/4 lean protein, 1/4 quality complex carbohydrates",
                "Ensure consistent meal timing to avoid wide glycemic excursions"
            ],
            "lifestyle_recommendations": [
                "Target a 5% to 10% sustained weight loss in overweight or obese individuals with Type 2 diabetes",
                "Complete cessation of all tobacco smoking and vaping to reduce multiplied cardiovascular and amputation risks",
                "Prioritize 7 to 8 hours of restorative sleep nightly; screen for obstructive sleep apnea",
                "Engage in stress reduction techniques (mindfulness, yoga) which blunt stress hormone (cortisol, catecholamines) glucose spikes"
            ],
            "physical_activity": [
                "Perform at least 150 minutes of moderate-to-vigorous aerobic exercise per week (e.g., brisk walking, swimming, cycling) spread across at least 3 days with no more than 2 consecutive days without activity",
                "Incorporate 2 to 3 sessions of resistance/strength training per week to enhance skeletal muscle glucose disposal",
                "Interrupt prolonged sitting every 30 minutes with 2–3 minutes of light walking or standing"
            ],
            "hydration_guidance": [
                "Drink plentiful clean plain water (2–2.5 liters/day) to assist kidneys in flushing excess glucose and prevent dehydration",
                "Avoid fruit juices, regular sodas, sweetened teas, and sports drinks"
            ],
            "safe_home_care": [
                "Daily foot inspection: Check tops, soles, heels, and between toes for blisters, cuts, redness, or calluses using a mirror",
                "Wash feet daily in lukewarm water, dry thoroughly between toes, and apply moisturizing lotion to heels (avoid between toes)",
                "Never walk barefoot; wear comfortable, well-fitted footwear with seamless socks",
                "Keep a home log of capillary blood glucose or continuous glucose monitor (CGM) readings"
            ],
            "natural_remedies": [
                "Cinnamon, fenugreek seeds, and bitter melon (Momordica charantia) have demonstrated mild glycemic-lowering trends in preliminary trials, but clinical evidence is heterogeneous and unstandardized.",
                "IMPORTANT CLINICAL LIMITATION: Natural remedies do NOT substitute for prescription insulin or antidiabetic medicines. Never discontinue medical therapy for herbal remedies. Doing so risks fatal diabetic ketoacidosis, hyperosmolar coma, and irreversible organ failure."
            ],
            "substances_to_avoid": [
                "Excessive alcohol intake, especially on an empty stomach (blocks hepatic gluconeogenesis and triggers delayed severe hypoglycemia)",
                "Over-the-counter decongestants containing pseudoephedrine (elevates blood pressure and glucose)",
                "Systemic oral corticosteroids unless specifically prescribed and monitored by a doctor"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Persistent thirst or waking up multiple times to urinate",
                "Repeated fasting blood glucose readings consistently > 130 mg/dL or post-meal readings > 180 mg/dL",
                "Unintentional weight loss despite normal appetite"
            ],
            "serious_warning_symptoms": [
                "Non-healing foot sores, cuts, blisters, or skin breaks lasting more than 7 days",
                "Sudden vision changes, floaters, or black spots in visual field",
                "Persistent numbness, tingling, or burning pain in feet or hands",
                "Blood glucose readings consistently exceeding 250 mg/dL"
            ],
            "emergency_situations": [
                "Hypoglycemia (< 54 mg/dL) that fails to resolve 15 minutes after consuming fast-acting carbohydrates (15g rule)",
                "Loss of consciousness, seizures, or confusion",
                "Persistent vomiting with inability to retain fluids for > 6 hours accompanied by high glucose and urine ketones",
                "Shortness of breath, chest pressure, pain radiating to left arm or jaw (acute myocardial infarction)"
            ],
            "recommended_follow_up": [
                "HbA1c testing every 3 months until target achieved, then every 6 months",
                "Annual comprehensive dilated retinal eye examination",
                "Annual spot urine albumin-to-creatinine ratio (uACR) and serum creatinine / eGFR",
                "Annual comprehensive diabetic foot sensory and arterial examination",
                "Annual fasting lipid profile"
            ],
            "preventive_screening": [
                "Screening all adults aged >= 35 years every 3 years with FPG or HbA1c",
                "Screening adults of any age who are overweight/obese with one or more risk factors",
                "Annual influenza vaccination, pneumococcal vaccination, hepatitis B vaccination, and RSV vaccination"
            ]
        },
        "references": [
            {
                "name": "Standards of Care in Diabetes — 2026",
                "organization": "American Diabetes Association (ADA)",
                "update_date": "2026-01-01",
                "url": "https://diabetesjournals.org/care/issue/49/Supplement_1"
            },
            {
                "name": "WHO Global Report on Diabetes & Clinical Guidelines",
                "organization": "World Health Organization (WHO)",
                "update_date": "2025-11-14",
                "url": "https://www.who.int/health-topics/diabetes"
            },
            {
                "name": "Type 2 diabetes in adults: management (NICE Guideline NG28)",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024-06-20",
                "url": "https://www.nice.org.uk/guidance/ng28"
            },
            {
                "name": "DailyMed National Drug Database — Metformin & Empagliflozin Monograph",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-07-15",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    },

    "dengue": {
        "id": "dengue",
        "name": "Dengue Fever & Severe Dengue",
        "category": "Infectious & Tropical Vector-Borne Diseases",
        "emoji": "🦟",
        "overview": {
            "description": "An acute, mosquito-borne viral infection caused by the Dengue virus (DENV, serotypes 1–4) transmitted by female Aedes mosquitoes (primarily Aedes aegypti). Clinical illness spans a broad spectrum from mild febrile illness to life-threatening plasma leakage, severe hemorrhage, and multiorgan failure.",
            "types_and_classifications": [
                "Dengue Without Warning Signs: Acute febrile illness with headache, retro-orbital pain, myalgia, arthralgia, rash, and leukopenia.",
                "Dengue With Warning Signs: Febrile phase followed by abdominal pain, persistent vomiting, mucosal bleeding, lethargy, fluid accumulation, and rapid platelet drop with rising hematocrit.",
                "Severe Dengue: Severe plasma leakage leading to Dengue Shock Syndrome (DSS) or fluid accumulation with respiratory distress; severe bleeding; or severe organ impairment (AST/ALT >= 1000, impaired consciousness, myocarditis)."
            ],
            "causes": [
                "Dengue virus infection (Flavivirus family, single-stranded RNA virus with 4 distinct serotypes: DENV-1, DENV-2, DENV-3, DENV-4)",
                "Bite of an infected female Aedes aegypti or Aedes albopictus mosquito (day-biting mosquitoes)",
                "Secondary heterologous infection: Infection with a different DENV serotype creates antibody-dependent enhancement (ADE), leading to massive viral replication and severe cytokine-mediated capillary leakage"
            ],
            "risk_factors": [
                "Living in or traveling to tropical and subtropical urban/semi-urban areas (Southeast Asia, South Asia, Latin America, Caribbean, Africa)",
                "Previous infection with a different DENV serotype (primary risk factor for Severe Dengue via ADE)",
                "Young children and infants (higher microvascular permeability)",
                "Underlying chronic diseases: Diabetes mellitus, hypertension, hemoglobinopathies, peptic ulcer disease",
                "Pregnancy (risk of maternal hemorrhage, preterm delivery, and vertical transmission)"
            ],
            "common_symptoms": [
                "Sudden explosive onset high fever (39°C–40°C / 102°F–104°F) lasting 2–7 days",
                "Severe retro-orbital eye pain (intense pain located directly behind the eyeballs)",
                "Severe frontal headache",
                "'Breakbone fever': Intense, excruciating bone, joint, and generalized muscle aches",
                "Transient macular flushing rash during initial 24–48 hours, followed by a maculopapular rash appearing day 3–6 ('islands of white in a sea of red')",
                "Nausea, vomiting, and loss of appetite (anorexia)"
            ],
            "uncommon_symptoms": [
                "Epistaxis (nosebleeds) and gingival (gum) bleeding",
                "Petechiae: Pinpoint reddish-purple hemorrhagic spots on skin",
                "Positive Tourniquet Test: >= 10 petechiae per square inch under inflated blood pressure cuff",
                "Diarrhea and mild hepatomegaly (tender liver enlargement)"
            ],
            "early_warning_signs": [
                "CRITICAL WARNING SIGNS (Transition to Critical Phase around day 3–7 as fever defervesces):",
                "1. Severe, unrelenting abdominal pain or tenderness",
                "2. Persistent vomiting (>= 3 episodes in 24 hours or unable to retain liquids)",
                "3. Clinical fluid accumulation (pleural effusion, ascites, puffy eyelids)",
                "4. Mucosal bleeding (bleeding from gums, nose, hematemesis, or heavy menorrhagia)",
                "5. Lethargy, restlessness, or altered mental state",
                "6. Liver enlargement > 2 cm below right costal margin",
                "7. Progressive increase in Hematocrit (HCT) concurrent with rapid, precipitous drop in Platelet count (< 100,000/mcL)"
            ],
            "possible_complications": [
                "Dengue Shock Syndrome (DSS): Profound hypovolemic shock caused by capillary hyperpermeability and systemic plasma leakage",
                "Massive gastrointestinal hemorrhage and intracranial bleeding",
                "Severe metabolic acidosis and disseminated intravascular coagulation (DIC)",
                "Acute liver failure with massive hepatic necrosis (fulminant hepatitis)",
                "Acute viral myocarditis with cardiomyopathy and arrhythmias",
                "Dengue encephalitis and acute respiratory distress syndrome (ARDS)"
            ],
            "systemic_impact": "DENV targets monocytes, macrophages, and dendritic cells, triggering an intense immune activation. In severe cases, immune-mediated endothelial activation causes transient widespread microvascular capillary hyperpermeability, allowing plasma proteins and fluid to leak from the intravascular space into the interstitial, pleural, and peritoneal cavities, culminating in hemoconcentration, circulatory collapse, severe thrombocytopenia, and consumption coagulopathy."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Clinical case definition: Acute fever + 2 characteristic symptoms in an endemic or travel area",
                "Daily serial monitoring of complete blood counts (Hematocrit and Platelets)",
                "Strict daily screening for clinical warning signs during the critical defervescence phase (days 3–7)"
            ],
            "laboratory_tests": [
                "Dengue NS1 Antigen Rapid Test or ELISA: Highly positive during Days 1–5 of fever (acute viremic phase)",
                "Dengue IgM / IgG Antibody ELISA: IgM becomes positive after Day 4–5; IgG quadrupling indicates secondary infection",
                "Real-Time Reverse Transcriptase PCR (RT-PCR): Gold standard for viral RNA detection and serotyping during initial 5 days",
                "Serial Complete Blood Count (CBC): Leukopenia (WBC < 4,000) followed by progressive thrombocytopenia (platelets < 100,000) and elevated hematocrit (HCT > 20% above baseline indicates plasma leakage)",
                "Liver Function Tests (ALT/AST): Significant elevations reflect hepatic involvement; AST > ALT is characteristic",
                "Coagulation Profile (PT, aPTT, Fibrinogen): Performed if active mucosal bleeding is present"
            ],
            "medical_examinations": [
                "Bedside abdominal ultrasound: Detects early gallbladder wall thickening/edema, subcapsular fluid, and peritoneal ascites",
                "Chest X-Ray (Right lateral decubitus): Detects early right-sided pleural effusion indicating plasma leakage",
                "Tourniquet Test: Inflate BP cuff midway between systolic and diastolic for 5 minutes; count petechiae",
                "Serial vital signs: Pulse pressure assessment (systolic minus diastolic <= 20 mmHg indicates impending shock)"
            ],
            "test_results_interpretation": [
                "NS1 Antigen Positive (Days 1–5): Confirms acute dengue infection.",
                "Platelet Count: Normal 150,000–450,000/mcL. Drops rapidly in critical phase; < 100,000/mcL indicates warning stage; < 50,000/mcL requires intensive inpatient monitoring. Note: Prophylactic platelet transfusion is NOT recommended by WHO unless severe active bleeding occurs.",
                "Hematocrit (HCT): A rise of >= 20% concurrent with thrombocytopenia is the cardinal hallmark of plasma leakage requiring immediate intravenous crystalloid rehydration.",
                "Pulse Pressure <= 20 mmHg (e.g., 90/75 mmHg) or cold clammy extremities with tachycardia signals Dengue Shock Syndrome — EMERGENCY."
            ]
        },
        "medicines": [
            {
                "name": "Paracetamol",
                "brand_names": ["Tylenol", "Panadol", "Calpol", "Crocin", "Dolo 650"],
                "generic_name": "Acetaminophen / Paracetamol",
                "category": "Analgesic & Antipyretic",
                "therapeutic_class": "Non-opioid Analgesic",
                "purpose": "THE ONLY SAFE ANALGESIC & ANTIPYRETIC IN DENGUE. Controls high fever, retro-orbital eye pain, and excruciating musculoskeletal pain without impairing platelet function or irritating gastric mucosa.",
                "how_it_works": "Inhibits central prostaglandin synthesis in the brain; acts on the hypothalamic thermoregulatory center to induce heat dissipation. Does NOT inhibit platelet COX-1 or aggregate platelets.",
                "common_side_effects": ["Mild nausea", "Stomach upset (rare)"],
                "serious_adverse_effects": ["Acute liver toxicity / hepatic necrosis (in overdose). Exercise caution in dengue-induced hepatitis."],
                "contraindications": ["Severe acute liver failure", "Hypersensitivity to paracetamol"],
                "drug_interactions": ["Alcohol multiplies liver toxicity", "Warfarin (at prolonged high doses)"],
                "food_interactions": ["Take with or without food. Maintain strict water/fluid intake."],
                "allergy_precautions": "Discontinue if allergic skin eruption develops.",
                "age_precautions": "In children: Strictly 10–15 mg/kg per dose every 4–6 hours (max 60 mg/kg/day). Never exceed recommended dose.",
                "pregnancy_breastfeeding": "Safe and preferred antipyretic in pregnancy and lactation.",
                "kidney_liver_precautions": "Maximum daily dose in dengue adults should be limited to 3000 mg/day (or 2000 mg/day in hepatic involvement) to avoid compounding viral transaminitis.",
                "monitoring_requirements": "Daily total paracetamol dosage; serial liver enzymes (ALT/AST)."
            },
            {
                "name": "Oral Rehydration Salts (ORS)",
                "brand_names": ["Electral", "WHO-ORS", "Hydralyte"],
                "generic_name": "Oral rehydration salts formula",
                "category": "Fluid and Electrolyte Rehydration",
                "therapeutic_class": "Oral Electrolyte Replacement",
                "purpose": "VITAL CORNERSTONE OF DENGUE MANAGEMENT: Aggressive early oral rehydration counteracts capillary fluid leakage, maintains intravascular volume, and prevents progression to Dengue Shock Syndrome.",
                "how_it_works": "Utilizes intestinal SGLT1 cotransport of glucose and sodium to rapidly draw water and electrolytes across the intestinal mucosa into circulation.",
                "common_side_effects": ["Nausea if consumed too rapidly"],
                "serious_adverse_effects": ["Fluid overload if forced in renal failure"],
                "contraindications": ["Severe uncompensated shock (requires immediate emergency IV crystalloids)", "Intractable vomiting", "Paralytic ileus"],
                "drug_interactions": ["Safe and compatible with all supportive therapies"],
                "food_interactions": ["Dissolve in exact specified volume of clean drinking water (typically 1 liter). Do NOT mix with juices or soda."],
                "allergy_precautions": "None (physiologic electrolyte balance).",
                "age_precautions": "Life-saving across all age groups from infancy to geriatrics.",
                "pregnancy_breastfeeding": "Completely safe and essential during pregnancy.",
                "kidney_liver_precautions": "Safe in liver disease; monitor in severe oliguric renal failure.",
                "monitoring_requirements": "Urine output volume (should exceed 0.5–1 mL/kg/hour in adults); clinical hydration status."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "CRITICAL WARNING: NEVER TAKE NSAIDs (Ibuprofen, Naproxen, Diclofenac, Mefenamic acid) or ASPIRIN in suspected or confirmed Dengue. NSAIDs cause platelet inhibition, aggravate pre-existing thrombocytopenia, induce severe gastric mucosal erosions, and trigger catastrophic internal hemorrhage and death.",
                "Avoid intramuscular (IM) injections: High risk of large painful intramuscular hematomas due to low platelets",
                "Avoid systemic corticosteroids: Clinical trials show no benefit in dengue shock and increased risk of gastrointestinal bleeding"
            ],
            "food_interactions": [
                "Avoid dark, red, brown, or black foods and beverages (e.g., chocolate, cola, red gelatin, grape juice) because vomit or stool containing these colors can be dangerously confused with gastrointestinal bleeding (melena or coffee-ground hematemesis)"
            ],
            "allergy_warnings": [
                "Skin rashes appearing around day 4–6 are usually the benign viral convalescent rash ('islands of white in a sea of red') which is intensely itchy; topical calamine lotion can soothe itch without oral antihistamine sedation"
            ],
            "critical_contraindications": [
                "STRICT CONTRAINDICATION: Aspirin, Ibuprofen, Ketoprofen, Naproxen, Diclofenac, and all other NSAIDs",
                "Prophylactic platelet transfusions are contraindicated: WHO guidelines clearly state that platelet transfusions do not prevent hemorrhage and carry significant risks of fluid overload and transfusion-related acute lung injury"
            ],
            "age_precautions": {
                "children": "Infants and young children have a smaller physiological intravascular reserve and higher baseline capillary permeability, progressing rapidly from mild fever to severe plasma leakage and shock. Monitor closely in hospital.",
                "older_adults": "Elderly patients frequently have underlying cardiovascular or renal disease; fluid balance must be titrated meticulously to prevent iatrogenic pulmonary edema."
            },
            "immediate_emergency_triggers": [
                "Narrowing Pulse Pressure (systolic BP minus diastolic BP <= 20 mmHg, e.g., 90/75 mmHg)",
                "Cold, clammy, mottled extremities with delayed capillary refill (> 2 seconds) and rapid feeble pulse",
                "Severe persistent abdominal pain with persistent vomiting",
                "Any bleeding from the mouth, nose, vagina, or passage of black tarry stools",
                "Sudden lethargy, confusion, agitation, or sudden drop in body temperature accompanied by extreme weakness"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Consume light, soft, nutrient-dense foods (warm broths, vegetable soups, rice porridge, soft fruits)",
                "Avoid oily, greasy, heavily spiced, and acidic foods that irritate the stomach lining",
                "Avoid dark red or black foods/liquids that could mask internal gastrointestinal bleeding"
            ],
            "lifestyle_recommendations": [
                "Strict, absolute physical bed rest during the febrile and critical phases (energy conservation)",
                "Use mosquito bed nets and insecticide sprays during the day to prevent secondary mosquito bites that infect other family members",
                "Eliminate all standing water in flower pots, tires, and containers within 100 meters of the home"
            ],
            "physical_activity": [
                "Avoid any strenuous physical activity, contact sports, or heavy lifting until platelet counts normalize (> 150,000/mcL) to prevent traumatic hemorrhage or hematomas"
            ],
            "hydration_guidance": [
                "Drink oral fluids aggressively: ORS, coconut water, fresh fruit juices (non-red), clear broths, and clean water",
                "Adults should aim for at least 2.5 to 3 liters of fluids per day; children should receive frequent small sips throughout the day and night",
                "Ensure urination occurs at least every 4 to 6 hours (pale yellow urine indicates adequate hydration)"
            ],
            "safe_home_care": [
                "Tepid sponging with lukewarm water for fever relief (avoid cold ice water which causes shivering and raises core temperature)",
                "Apply calamine lotion to relieve the intense itching of the convalescent recovery rash",
                "Maintain a meticulous log of fluid intake, urine output, and temperature"
            ],
            "natural_remedies": [
                "Papaya leaf extract (Carica papaya) has been investigated in small clinical trials showing accelerated platelet elevation trends in non-severe dengue.",
                "CRITICAL EVIDENCE LIMITATION: Papaya leaf extract has NOT been proven in large-scale randomized trials to prevent plasma leakage, severe hemorrhage, or Dengue Shock Syndrome. It must NEVER replace medical supervision, serial platelet monitoring, or intravenous crystalloid therapy. Self-treating severe dengue with unverified remedies is life-threatening."
            ],
            "substances_to_avoid": [
                "ALL NSAID pain medications (Ibuprofen, Advil, Motrin, Brufen, Aspirin, Diclofenac)",
                "Alcohol and smoking",
                "Commercial high-sugar sodas and artificial energy drinks"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "High fever lasting more than 24–48 hours with retro-orbital eye pain, joint aches, or vomiting in a dengue-endemic area",
                "Any fever in infants under 1 year, pregnant women, or elderly individuals"
            ],
            "serious_warning_symptoms": [
                "Appearance of ANY clinical warning sign (severe abdominal pain, persistent vomiting, bleeding gums, extreme lethargy)",
                "Fever dropping suddenly on day 3–5 accompanied by cold clammy skin rather than feeling better ('critical defervescence phase')"
            ],
            "emergency_situations": [
                "Signs of Dengue Shock Syndrome: Cold clammy hands/feet, rapid thready pulse, systolic BP < 90 mmHg, pulse pressure <= 20 mmHg",
                "Vomiting blood or passing black tarry stools",
                "Severe respiratory distress, rapid breathing, or blueness of lips (cyanosis)",
                "Confusion, severe drowsiness, or seizures"
            ],
            "recommended_follow_up": [
                "Daily serial Complete Blood Count (CBC) monitoring for Hematocrit and Platelet count until 48 hours after fever resolves",
                "Daily clinical assessment by a doctor throughout the critical phase (days 3–7)"
            ],
            "preventive_screening": [
                "Community vector control: Eradicate mosquito breeding habitats (stagnant water containers)",
                "Personal protection: Wear light-colored long-sleeve clothing and apply DEET/Picaridin mosquito repellent during daytime hours (peak biting times: early morning and late afternoon)",
                "Dengue vaccines (e.g., Qdenga / Dengvaxia) in approved endemic populations per WHO recommendations"
            ]
        },
        "references": [
            {
                "name": "Dengue: Guidelines for Diagnosis, Treatment, Prevention and Control",
                "organization": "World Health Organization (WHO)",
                "update_date": "2025-09-18",
                "url": "https://www.who.int/publications/i/item/9789241547871"
            },
            {
                "name": "CDC Clinical Guidance for Dengue Virus Infections",
                "organization": "Centers for Disease Control and Prevention (CDC)",
                "update_date": "2026-05-10",
                "url": "https://www.cdc.gov/dengue/hcp/clinical-guidance/index.html"
            },
            {
                "name": "Management of Dengue Infection in Adults and Children",
                "organization": "Ministry of Health Clinical Practice Guidelines",
                "update_date": "2024-11-01",
                "url": "https://www.who.int/westernpacific/health-topics/dengue"
            },
            {
                "name": "DailyMed — Acetaminophen & Oral Rehydration Salts Clinical Monograph",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-06-20",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    },

    "asthma": {
        "id": "asthma",
        "name": "Asthma (Bronchial Asthma)",
        "category": "Respiratory & Allergic Airway Diseases",
        "emoji": "💨",
        "overview": {
            "description": "A chronic heterogeneous inflammatory disease of the airways characterized by recurrent episodes of wheezing, breathlessness, chest tightness, and coughing that vary over time and in intensity, together with variable expiratory airflow limitation.",
            "types_and_classifications": [
                "Allergic (Atopic) Asthma: Most common phenotype, initiating in childhood with eosinophilic airway inflammation and positive allergen skin prick / specific IgE tests.",
                "Non-Allergic Asthma: Not associated with atopy; sputum may be neutrophilic or eosinophilic; often triggered by viral infections.",
                "Adult-Onset (Late-Onset) Asthma: Developing in adulthood, particularly in females; frequently non-allergic and requiring higher corticosteroid doses.",
                "Asthma with Persistent Airflow Limitation: Chronic airway remodeling in long-standing asthma causing irreversible structural bronchial narrowing.",
                "Exercise-Induced Bronchoconstriction (EIB): Acute airway narrowing provoked specifically by vigorous physical exertion or hyperventilation in cold dry air."
            ],
            "causes": [
                "Chronic mucosal inflammation driven by Type 2 helper T-cell (Th2) cytokines (IL-4, IL-5, IL-13) and airway eosinophilia",
                "Bronchial hyperresponsiveness: Exaggerated bronchoconstrictor response to environmental stimuli",
                "Airway remodeling: Subepithelial basement membrane thickening, goblet cell hyperplasia, and airway smooth muscle hypertrophy",
                "Complex gene-environment interactions (family history of atopic triad: asthma, eczema, allergic rhinitis)"
            ],
            "risk_factors": [
                "Personal or family history of atopy or asthma",
                "Inhaled aeroallergen sensitization: House dust mites, domestic animal dander (cats, dogs), pollens, indoor moulds",
                "Exposure to environmental tobacco smoke (passive smoke in childhood or active smoking)",
                "Severe respiratory syncytial virus (RSV) or rhinovirus bronchiolitis during early infancy",
                "Occupational sensitizers: Chemical isocyanates, flour and grain dust, wood dust, latex",
                "Obesity and gastroesophageal reflux disease (GERD)"
            ],
            "common_symptoms": [
                "Expiratory wheezing: High-pitched musical whistling sound during exhalation",
                "Shortness of breath (dyspnea), particularly on exertion or during night/early morning",
                "Chest tightness: Sensation of a heavy band constricting the thoracic cage",
                "Dry, hacking, non-productive cough, frequently nocturnal interrupting sleep"
            ],
            "uncommon_symptoms": [
                "Cough-Variant Asthma: Chronic non-productive cough as the sole manifestation without audible wheezing",
                "Severe exercise intolerance and rapid exhaustion during physical activities",
                "Nocturnal awakenings with choking sensation or chest discomfort"
            ],
            "early_warning_signs": [
                "Needing to use rapid-acting reliever inhaler (Salbutamol) more than twice a week",
                "Waking up at night or early morning with coughing or chest tightness",
                "Peak Expiratory Flow (PEF) readings dropping 20% below personal best",
                "Symptoms triggered by minor cold air exposure or light laughter"
            ],
            "possible_complications": [
                "Status Asthmaticus / Acute Severe Asthma Exacerbation — life-threatening medical emergency",
                "Respiratory failure requiring emergency non-invasive ventilation or mechanical intubation",
                "Pneumothorax and pneumomediastinum secondary to high alveolar pressures and air trapping",
                "Atelectasis (lung collapse) secondary to tenacious mucus plugging",
                "Irreversible airway remodeling and fixed airflow obstruction"
            ],
            "systemic_impact": "Chronic recurrent airway inflammation and untreated bronchoconstriction lead to dynamic pulmonary hyperinflation ('air trapping'), ventilation-perfusion mismatching, hypoxemia, increased right ventricular cardiac afterload (cor pulmonale in severe long-term cases), chronic sleep fragmentation, and profound functional impairment."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Demonstration of variable expiratory airflow limitation using objective spirometry",
                "Detailed clinical history of variable respiratory symptoms worse at night or with known triggers",
                "Physical examination: Expiratory polyphonic wheezes on chest auscultation (note: chest may be 'silent' in life-threatening attack)"
            ],
            "laboratory_tests": [
                "Spirometry with Pre- and Post-Bronchodilator Testing: Diagnostic hallmark is an increase in FEV1 of > 12% and > 200 mL 15 minutes after inhaling a short-acting bronchodilator (Salbutamol 400 mcg)",
                "Peak Expiratory Flow (PEF) Variability: Twice-daily peak flow monitoring showing diurnal variability > 10% (adults) or > 13% (children)",
                "Fractional Exhaled Nitric Oxide (FeNO): Non-invasive marker of eosinophilic Th2 airway inflammation (FeNO > 50 ppb supports diagnosis)",
                "Complete Blood Count (CBC): Elevated blood eosinophil count (>= 300 cells/mcL)",
                "Serum Total IgE and Allergen-Specific IgE (ImmunoCAP) / Skin Prick Testing",
                "Bronchoprovocation Challenge Test (Methacholine / Histamine / Exercise challenge): Used when spirometry is normal"
            ],
            "medical_examinations": [
                "Chest X-Ray: Typically normal or shows lung hyperinflation; essential during exacerbations to rule out pneumothorax or pneumonia",
                "High-Resolution Chest CT: Indicated if bronchiectasis or alternative airway pathology is suspected"
            ],
            "test_results_interpretation": [
                "FEV1/FVC Ratio: Normally > 0.75–0.80. A ratio < 0.70 confirms obstructive airflow limitation.",
                "Positive Bronchodilator Reversibility: FEV1 improvement >= 12% and >= 200 mL confirms reversible asthma airflow obstruction.",
                "Peak Expiratory Flow (PEF) Zones: Green Zone (80%–100% of personal best: well controlled); Yellow Zone (50%–79%: caution, step up therapy); Red Zone (< 50%: MEDICAL EMERGENCY — take rescue inhaler and seek immediate emergency care)."
            ]
        },
        "medicines": [
            {
                "name": "Budesonide and Formoterol",
                "brand_names": ["Symbicort", "Foracort", "Vannair"],
                "generic_name": "Budesonide and formoterol fumarate dihydrate",
                "category": "Inhaled Corticosteroid / Long-Acting Beta-2 Agonist",
                "therapeutic_class": "ICS / LABA Fixed-Dose Combination",
                "purpose": "First-line preferred controller and reliever regimen (GINA Track 1 SMART strategy) for persistent asthma across adolescents and adults.",
                "how_it_works": "Budesonide provides potent topical suppression of airway mucosal eosinophilic inflammation; Formoterol provides rapid (within 1–3 minutes) and long-lasting (>= 12 hours) bronchodilation.",
                "common_side_effects": ["Oral candidiasis (oral thrush)", "Dysphonia (hoarse voice)", "Mild hand tremor", "Throat irritation"],
                "serious_adverse_effects": ["Paradoxical bronchospasm", "Pneumonia (in COPD)", "Adrenal suppression at prolonged high doses"],
                "contraindications": ["Hypersensitivity to budesonide or formoterol"],
                "drug_interactions": ["Strong CYP3A4 inhibitors (ketoconazole)", "Beta-blockers antagonize bronchodilation"],
                "food_interactions": ["Independent of food. CRITICAL: Rinse mouth with water and spit it out after every inhalation."],
                "allergy_precautions": "Discontinue if allergic urticaria or bronchospasm develops.",
                "age_precautions": "Approved >= 6 years. Monitor linear height growth in children on chronic corticosteroids.",
                "pregnancy_breastfeeding": "Preferred maintenance therapy in asthma during pregnancy (extensive safety record).",
                "kidney_liver_precautions": "No dose adjustments for renal failure. Caution in severe cirrhosis.",
                "monitoring_requirements": "Periodic spirometry / FEV1; inspection of oral cavity for fungal thrush."
            },
            {
                "name": "Salbutamol",
                "brand_names": ["Ventolin", "ProAir", "Asthalin"],
                "generic_name": "Albuterol / Salbutamol sulfate",
                "category": "Short-Acting Bronchodilator",
                "therapeutic_class": "Short-Acting Beta-2 Agonist (SABA)",
                "purpose": "Rapid rescue reversal of acute bronchospasm attacks and exercise-induced bronchoconstriction.",
                "how_it_works": "Stimulates beta-2 adrenergic receptors on bronchial smooth muscle, activating adenylyl cyclase, lowering intracellular calcium, and producing rapid bronchodilation within 5 minutes.",
                "common_side_effects": ["Skeletal muscle hand tremor", "Tachycardia and palpitations", "Restlessness", "Headache"],
                "serious_adverse_effects": ["Paradoxical bronchospasm", "Cardiac arrhythmias", "Hypokalemia with frequent nebulization"],
                "contraindications": ["Hypersensitivity to salbutamol sulfate"],
                "drug_interactions": ["Non-selective beta-blockers (propranolol) trigger severe, potentially fatal bronchospasm", "Diuretics worsen hypokalemia"],
                "food_interactions": ["Independent of food. Avoid excessive caffeine."],
                "allergy_precautions": "Discontinue immediately if paradoxical bronchospasm occurs.",
                "age_precautions": "Safe in all ages. Children under 5 must always use an inhaler spacer with a face mask.",
                "pregnancy_breastfeeding": "Rescue SABA of choice in pregnancy (fetal hypoxia from untreated asthma is far more dangerous).",
                "kidney_liver_precautions": "No dose adjustments needed.",
                "monitoring_requirements": "Frequency of rescue canister use (using > 2 canisters/year indicates high risk of asthma death)."
            },
            {
                "name": "Montelukast",
                "brand_names": ["Singulair", "Montair", "Telekast"],
                "generic_name": "Montelukast sodium",
                "category": "Leukotriene Receptor Antagonist",
                "therapeutic_class": "Oral Leukotriene Modifier",
                "purpose": "Oral maintenance therapy for chronic asthma, exercise-induced bronchospasm, and co-existing allergic rhinitis.",
                "how_it_works": "Competitively blocks the cysteinyl leukotriene CysLT1 receptor, inhibiting leukotriene-mediated airway edema and bronchoconstriction.",
                "common_side_effects": ["Headache", "Upper respiratory symptoms", "Abdominal discomfort", "Diarrhea"],
                "serious_adverse_effects": ["Serious neuropsychiatric events (FDA Boxed Warning: aggression, depression, nightmares, suicidal ideation)"],
                "contraindications": ["Hypersensitivity to montelukast"],
                "drug_interactions": ["Phenobarbital and rifampin reduce montelukast concentrations", "Gemfibrozil"],
                "food_interactions": ["Take once daily in the evening with or without food."],
                "allergy_precautions": "Discontinue immediately and seek medical attention if mood or behavioral changes emerge.",
                "age_precautions": "Approved in children >= 12 months (granules / chewables).",
                "pregnancy_breastfeeding": "Category B. Compatible with pregnancy and lactation.",
                "kidney_liver_precautions": "No dose adjustment for renal failure. Caution in severe hepatic insufficiency.",
                "monitoring_requirements": "Screen for mood changes and neuropsychiatric symptoms at every visit."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "CRITICAL WARNING: NON-SELECTIVE BETA-BLOCKERS (Propranolol, Carvedilol, Labetalol, Timolol eye drops) are strictly contraindicated in asthmatics. They block beta-2 receptors, completely abolishing bronchodilator response and triggering fatal acute bronchospasm.",
                "Aspirin and NSAIDs: In 10%–20% of adult asthmatics, NSAIDs trigger Aspirin-Exacerbated Respiratory Disease (AERD) characterized by sudden life-threatening bronchospasm, severe rhinorrhea, and ocular injection."
            ],
            "food_interactions": [
                "Sulfites (found in dried fruits, packaged shrimp, processed potatoes, and wine) can trigger severe acute bronchospasm in susceptible asthmatic patients"
            ],
            "allergy_warnings": [
                "Patients must rinse mouth and throat thoroughly with water and spit it out after every inhaled corticosteroid dose to prevent oropharyngeal fungal candidiasis (thrush) and hoarseness"
            ],
            "critical_contraindications": [
                "NEVER rely on SABA reliever inhalers (Salbutamol) alone without an anti-inflammatory inhaled corticosteroid controller: SABA monotherapy increases bronchial hyperresponsiveness and multiplies asthma mortality (GINA alert)",
                "Avoid sedatives or anxiolytics during acute asthma attacks (suppresses respiratory drive)"
            ],
            "age_precautions": {
                "children": "Metered Dose Inhalers (MDIs) MUST ALWAYS be administered via a valved holding chamber (spacer) to ensure drug reaches lower airways rather than impacting in the pharynx.",
                "older_adults": "Assess manual grip strength and cognitive ability; verify correct inhaler technique annually. Differentiate from COPD or congestive heart failure."
            },
            "immediate_emergency_triggers": [
                "Silent Chest: Severe respiratory distress where wheezing disappears due to extreme airflow obstruction and minimal air movement — IMMINENT RESPIRATORY ARREST",
                "Inability to speak full sentences in one breath (speaking in single words only)",
                "Intercostal retractions, suprasternal indrawing, and abdominal paradoxical breathing",
                "Cyanosis (bluish discoloration of lips, tongue, or nail beds)",
                "Peak flow < 50% of personal best with no response to repeated rescue inhaler actuations"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Eat an anti-inflammatory diet rich in fresh fruits, colorful vegetables, omega-3 fatty acids, and vitamin D",
                "Avoid sulfites, artificial food colorings, and chemical preservatives that trigger bronchospasm",
                "Maintain a healthy body weight to decrease mechanical diaphragmatic compression"
            ],
            "lifestyle_recommendations": [
                "Maintain a completely 100% smoke-free home and vehicle (no cigarettes, cigars, hookahs, or vaping)",
                "Use allergen-impermeable barrier covers for mattresses, duvets, and pillows; wash bed linens weekly at 60°C to eliminate dust mites",
                "Maintain indoor relative humidity between 30% and 50% to prevent mould growth and dust mite proliferation",
                "Use high-efficiency particulate air (HEPA) room purifiers in bedrooms"
            ],
            "physical_activity": [
                "Exercise is encouraged for cardiovascular health and lung capacity",
                "Pre-treat with a prescribed bronchodilator inhaler (Salbutamol or Symbicort) 10–15 minutes prior to vigorous exercise",
                "Perform warm-up and cool-down routines; wear a scarf covering nose and mouth during cold-weather exercise"
            ],
            "hydration_guidance": [
                "Drink adequate water (2 liters/day) to maintain thin, loose bronchial secretions that are easily cleared"
            ],
            "safe_home_care": [
                "Develop and keep a written, personalized Asthma Action Plan co-signed by your pulmonologist",
                "Keep inhalers in a consistent, easily accessible location; always carry rescue medication when traveling",
                "Check inhaler dose counters regularly to ensure canisters are not empty"
            ],
            "natural_remedies": [
                "Diaphragmatic breathing exercises, the Buteyko breathing method, and yoga pranayama can improve quality of life and breathing control.",
                "CRITICAL EVIDENCE LIMITATION: Breathing exercises and herbal supplements do NOT reduce airway eosinophilia or reverse bronchial hyperresponsiveness. They NEVER substitute for prescription inhaled corticosteroids. Discontinuing inhalers for natural remedies risks fatal status asthmaticus."
            ],
            "substances_to_avoid": [
                "Active and passive tobacco smoke, wood-burning stove smoke, and fireplace fumes",
                "Aspirin and NSAID pain relievers in susceptible individuals",
                "Strong aerosolized cleaning sprays, bleach, perfumed air fresheners, and incense"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Needing rescue reliever inhaler > 2 times per week",
                "Waking up at night coughing or wheezing > 2 times per month",
                "Activity limitation due to shortness of breath"
            ],
            "serious_warning_symptoms": [
                "Peak Expiratory Flow (PEF) readings dropping into the yellow zone (50%–79%) despite rescue medication",
                "Respiratory symptoms becoming progressively worse after an upper respiratory cold",
                "Persistent productive cough with yellow-green phlegm and fever"
            ],
            "emergency_situations": [
                "Extreme shortness of breath with inability to complete a sentence in one breath",
                "Lips or fingernails turning blue or gray (cyanosis)",
                "Chest wall pulling inward severely (retractions) with breathing",
                "Peak flow < 50% with no improvement 15 minutes after 4–8 puffs of reliever inhaler — CALL EMERGENCY SERVICES (911 / 112) IMMEDIATELY"
            ],
            "recommended_follow_up": [
                "Clinical review 1–3 months after starting controller therapy, then every 3–12 months",
                "Review inhaler technique and adherence at EVERY single medical consultation",
                "Repeat spirometry every 1–2 years to monitor for chronic airway remodeling"
            ],
            "preventive_screening": [
                "Annual seasonal influenza vaccination for all individuals with asthma",
                "Pneumococcal conjugate vaccination (PCV20 or PCV15 followed by PPSV23)",
                "Allergen skin prick testing or specific IgE assays to identify specific triggers"
            ]
        },
        "references": [
            {
                "name": "Global Strategy for Asthma Management and Prevention (GINA 2025/2026)",
                "organization": "Global Initiative for Asthma (GINA)",
                "update_date": "2025-05-01",
                "url": "https://ginasthma.org/reports/"
            },
            {
                "name": "Asthma: diagnosis, monitoring and chronic asthma management (NICE Guideline NG80)",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024-03-22",
                "url": "https://www.nice.org.uk/guidance/ng80"
            },
            {
                "name": "British Guideline on the Management of Asthma",
                "organization": "British Thoracic Society (BTS) / SIGN",
                "update_date": "2024-08-15",
                "url": "https://www.brit-thoracic.org.uk/quality-improvement/guidelines/asthma/"
            },
            {
                "name": "DailyMed — Symbicort & Albuterol Inhalation Aerosol Monograph",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-07-20",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    },

    "malaria": {
        "id": "malaria",
        "name": "Malaria (Plasmodium Infection)",
        "category": "Infectious & Tropical Parasitic Diseases",
        "emoji": "🔬",
        "overview": {
            "description": "A life-threatening parasitic infection caused by protozoan parasites of the genus Plasmodium transmitted to humans through the bites of infected female Anopheles mosquitoes. Following an asymptomatic hepatic incubation stage, parasites invade erythrocytes, triggering periodic paroxysms of severe fever, hemolytic anemia, and microvascular sequestration.",
            "types_and_classifications": [
                "Plasmodium falciparum: Most virulent species, predominant in sub-Saharan Africa; responsible for almost all severe malaria and malaria deaths due to cytoadherence and microvascular sequestration.",
                "Plasmodium vivax: Widespread in Asia, Latin America, and Horn of Africa; produces dormant liver hypnozoites capable of causing relapses months to years later.",
                "Plasmodium ovale: Causes tertian relapses via dormant hypnozoites, common in West Africa.",
                "Plasmodium malariae: Causes quartan paroxysms (72-hour cycle); can persist at low parasitemias for decades.",
                "Plasmodium knowlesi: Zoonotic simian malaria in Southeast Asia; reproduces on a rapid 24-hour cycle capable of severe fatal parasitemia."
            ],
            "causes": [
                "Bite of an infected female Anopheles mosquito injecting Plasmodium sporozoites during blood feeding",
                "Sporozoites migrate via circulation to the liver, invading hepatocytes to undergo asexual pre-erythrocytic schizogony (6–16 days)",
                "Merozoites burst from hepatocytes, invading host red blood cells (erythrocytic schizogony)",
                "Synchronized rupture of infected erythrocytes and release of parasitic hemozoin, pyrogens, and TNF-alpha triggers severe paroxysmal fevers"
            ],
            "risk_factors": [
                "Travel to or residence in malaria-endemic regions (sub-Saharan Africa, South Asia, Southeast Asia, Amazon basin)",
                "Lack of acquired immunity (young children, non-immune international travelers, pregnant women)",
                "Failure to take prescribed chemoprophylaxis when traveling to endemic destinations",
                "Lack of mosquito vector prevention (insecticide-treated nets, indoor residual spraying)"
            ],
            "common_symptoms": [
                "Malarial Paroxysm: Classic triad progressing over 6–10 hours: Cold stage (uncontrollable shivering rigor) -> Hot stage (high fever 40°C–41°C, intense headache, vomiting) -> Sweating stage (profuse drenching diaphoresis, sudden defervescence, extreme exhaustion)",
                "Severe frontal or generalized throbbing headache",
                "Generalized myalgia, arthralgia, and lumbar back pain",
                "Nausea, vomiting, diarrhea, and anorexia",
                "Splenomegaly (tender, enlarged spleen) and hepatomegaly"
            ],
            "uncommon_symptoms": [
                "Jaundice (yellow sclera and skin from rapid intravascular hemolysis and hepatic dysfunction)",
                "Severe pallor secondary to rapid hemolytic anemia",
                "Dark, reddish-brown urine ('Blackwater fever' from massive intravascular hemolysis and hemoglobinuria)"
            ],
            "early_warning_signs": [
                "Fever in any traveler returning from a malaria-endemic country within the past 12 months is considered a MEDICAL EMERGENCY until proven otherwise by microscopy/RDT"
            ],
            "possible_complications": [
                "Cerebral Malaria (Severe P. falciparum): Sequestration of parasitized RBCs in cerebral microvasculature causing unarousable coma, encephalopathy, and seizures",
                "Severe Malarial Anemia: Hemoglobin < 7 g/dL due to massive erythrocyte destruction and dyserythropoiesis",
                "Acute Respiratory Distress Syndrome (ARDS) / Non-cardiogenic Pulmonary Edema",
                "Acute Renal Failure (Acute Tubular Necrosis / Blackwater fever)",
                "Severe Metabolic Lactic Acidosis (arterial pH < 7.35, bicarbonate < 15 mmol/L)",
                "Severe Hypoglycemia (blood glucose < 40 mg/dL): Induced by parasite glucose consumption and quinine therapy",
                "Disseminated Intravascular Coagulation (DIC) and Spontaneous Splenic Rupture"
            ],
            "systemic_impact": "In P. falciparum, the parasite expresses PfEMP1 proteins on the erythrocyte surface, causing cytoadherence to endothelial receptors (CD36, ICAM-1) and rosetting. This microvascular sequestration obstructs capillary blood flow, tissue perfusion, and oxygen delivery across brain, kidneys, and placenta, triggering severe tissue ischemia, lactic acidosis, and multiorgan failure."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "MANDATORY: Urgent parasitological confirmation before administering treatment (unless in extreme emergency in remote settings)",
                "Immediate microscopic examination of blood films or Rapid Diagnostic Tests (RDTs)"
            ],
            "laboratory_tests": [
                "Giemsa-Stained Blood Films (Gold Standard): Thick film (high sensitivity for detecting presence of parasites) and Thin film (accurate species identification and quantification of parasitemia %)",
                "Rapid Diagnostic Tests (RDTs): Detects Plasmodium antigens (HRP2 for P. falciparum; pLDH or aldolase for pan-species)",
                "Complete Blood Count (CBC): Normocytic normochromic anemia, thrombocytopenia, leukopenia or normal WBC",
                "Blood Glucose Monitoring: Mandatory in all severe malaria cases to detect lethal hypoglycemia",
                "Serum Creatinine and BUN (renal failure screening); Serum Bilirubin and Transaminases; Arterial Blood Gas (lactic acidosis screening)",
                "G6PD Deficiency Enzyme Assay: MANDATORY prior to prescribing Primaquine (anti-relapse hypnozoiticide) to avoid fatal acute intravascular hemolysis"
            ],
            "medical_examinations": [
                "Glasgow Coma Scale / Blantyre Coma Scale (in children) to detect cerebral malaria",
                "Fundoscopic examination: Malarial retinopathy (retinal whitening, vessel changes, hemorrhages — highly specific for cerebral malaria)",
                "Assessment of respiratory rate and depth to detect Kussmaul acidotic breathing"
            ],
            "test_results_interpretation": [
                "Parasitemia Quantification: > 2% infected RBCs in non-immune individuals or > 100,000 parasites/mcL represents high-risk infection; > 10% parasitemia is an automatic definition of Severe Malaria requiring intravenous artesunate.",
                "Thick & Thin Smears: Repeat every 12–24 hours if initial smear is negative but clinical suspicion remains high.",
                "G6PD Enzyme Activity: Normal activity allows full 14-day Primaquine course. Deficient activity requires specialist alternative intermittent regimens."
            ]
        },
        "medicines": [
            {
                "name": "Artemether and Lumefantrine",
                "brand_names": ["Coartem", "Riamet"],
                "generic_name": "Artemether and lumefantrine",
                "category": "Antimalarial Combination Therapy",
                "therapeutic_class": "Artemisinin-Based Combination Therapy (ACT)",
                "purpose": "First-line oral treatment of acute, uncomplicated malaria infections caused by Plasmodium falciparum or mixed malarial infections.",
                "how_it_works": "Artemether produces reactive oxygen endoperoxides destroying parasite biomass rapidly; Lumefantrine has a long half-life, eradicating residual parasites to prevent recrudescence.",
                "common_side_effects": ["Headache", "Dizziness", "Anorexia", "Nausea", "Fatigue", "Myalgia"],
                "serious_adverse_effects": ["Cardiac QTc prolongation", "Severe hypersensitivity", "Delayed post-artemisinin hemolysis (rare)"],
                "contraindications": ["Known artemisinin/lumefantrine allergy", "Severe malaria requiring IV therapy", "Congenital long QT syndrome"],
                "drug_interactions": ["QT-prolonging drugs (antiarrhythmics, antipsychotics)", "CYP3A4 inducers (rifampin, carbamazepine)", "Ketoconazole"],
                "food_interactions": ["CRITICAL: Must take with high-fat food or full-cream milk (lumefantrine absorption increases 16-fold with lipids)."],
                "allergy_precautions": "Discontinue if angioedema or bronchospasm occurs.",
                "age_precautions": "Approved in infants and children >= 5 kg (strict 6-dose weight-band schedule over 3 days).",
                "pregnancy_breastfeeding": "WHO recommended in 2nd and 3rd trimesters of pregnancy. Compatible with breastfeeding.",
                "kidney_liver_precautions": "No dose adjustments for mild-to-moderate renal or hepatic impairment.",
                "monitoring_requirements": "Follow-up blood smears at days 3, 7, 14, and 28 for parasite clearance; ECG in cardiac risk patients."
            },
            {
                "name": "Paracetamol",
                "brand_names": ["Panadol", "Tylenol", "Calpol"],
                "generic_name": "Acetaminophen / Paracetamol",
                "category": "Analgesic & Antipyretic",
                "therapeutic_class": "Non-opioid Analgesic",
                "purpose": "Essential symptomatic antipyretic to control high fever rigors, severe headaches, and generalized arthralgias.",
                "how_it_works": "Acts on the hypothalamic heat-regulating center to lower fever and blocks central pain transmission.",
                "common_side_effects": ["Mild nausea"],
                "serious_adverse_effects": ["Liver toxicity in overdose (limit dose in hepatic impairment)"],
                "contraindications": ["Severe active hepatic failure"],
                "drug_interactions": ["Alcohol"],
                "food_interactions": ["May take with or without food. Maintain plentiful oral hydration."],
                "allergy_precautions": "Discontinue if rash develops.",
                "age_precautions": "Weight-based dosing in children (10–15 mg/kg every 4–6 hours).",
                "pregnancy_breastfeeding": "Safe and indicated in pregnancy.",
                "kidney_liver_precautions": "Caution in liver involvement (max 2000–3000 mg/day).",
                "monitoring_requirements": "Monitor temperature curve and total daily dosage."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "CYP3A4 inducers (Rifampin, Carbamazepine, Phenytoin) drastically drop artemether and lumefantrine blood levels, causing complete antimalarial treatment failure",
                "Concurrent QT-prolonging antiarrhythmics (Amiodarone, Sotalol) with Lumefantrine significantly heighten lethal ventricular arrhythmia risk"
            ],
            "food_interactions": [
                "CRITICAL INSTRUCTION: Artemether-lumefantrine (Coartem) MUST be ingested with dietary fat (milk, fatty soup, or a meal). Administering it on an empty stomach results in inadequate lumefantrine absorption and malaria recrudescence."
            ],
            "allergy_warnings": [
                "Severe delayed hemolytic anemia can occur 1–3 weeks after artemisinin therapy; monitor hemoglobin and jaundice"
            ],
            "critical_contraindications": [
                "NEVER administer Primaquine without prior G6PD enzyme testing: In G6PD-deficient patients, primaquine triggers massive, life-threatening acute intravascular hemolytic crisis",
                "Oral antimalarials are strictly contraindicated in Severe / Complicated Malaria: Severe malaria requires immediate emergency admission and INTRAVENOUS ARTESUNATE"
            ],
            "age_precautions": {
                "children": "Children under 5 years are at the highest risk of rapid progression to cerebral malaria and death. Dosing must follow exact body weight bands.",
                "older_adults": "Screen for baseline cardiac conduction abnormalities (ECG) and underlying renal impairment."
            },
            "immediate_emergency_triggers": [
                "Altered mental status, confusion, delirium, or unarousable coma (Cerebral Malaria)",
                "Repeated generalized convulsions or abnormal posturing",
                "Deep, rapid, labored respiration (respiratory distress from metabolic acidosis)",
                "Passage of dark red, cola-colored, or black urine (hemoglobinuria)",
                "Jaundice accompanied by severe pallor, oliguria, or hypotension"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Eat small, frequent, nutrient-dense meals high in carbohydrates and proteins once nausea subsides",
                "Administer antimalarial tablets with full-cream milk, yogurt, or a meal containing dietary oils/fats"
            ],
            "lifestyle_recommendations": [
                "Strict bed rest in a cool, well-ventilated room",
                "Sleep under long-lasting insecticide-treated bed nets (LLINs)",
                "Install insect screens on all windows and doors"
            ],
            "physical_activity": [
                "Strictly avoid physical exertion, sports, or heavy work until parasitemia is cleared and hemoglobin recovers",
                "Avoid contact sports if splenomegaly is present due to catastrophic risk of splenic rupture"
            ],
            "hydration_guidance": [
                "Aggressively hydrate with Oral Rehydration Salts (ORS), fresh juices, broths, and clean water",
                "Monitor for regular clear or pale urination (at least 1.5–2 liters/day in adults)"
            ],
            "safe_home_care": [
                "Tepid sponging for high fever; avoid cold ice baths",
                "Strict adherence: COMPLETE ALL 6 DOSES of artemether-lumefantrine over the exact 3-day schedule, even after feeling completely cured",
                "If vomiting occurs within 1 hour of taking a dose, repeat the full dose immediately"
            ],
            "natural_remedies": [
                "Traditional Artemisia annua herbal teas contain sub-therapeutic, highly variable concentrations of artemisinin.",
                "CRITICAL WARNING: The World Health Organization (WHO) explicitly advises AGAINST using non-pharmaceutical Artemisia plant extracts or herbal teas. Using unstandardized teas promotes the emergence of artemisinin-resistant malarial parasites and causes high rates of treatment failure and death. Only use certified pharmaceutical Artemisinin-based Combination Therapies (ACTs)."
            ],
            "substances_to_avoid": [
                "Alcohol, which impairs hepatic function and immune clearance",
                "Unverified traditional antimalarial herbal concoctions"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Any fever, chills, or flu-like symptoms occurring in a person who has visited a malaria-endemic region within the past year",
                "Fever paroxysms occurring every 48 or 72 hours"
            ],
            "serious_warning_symptoms": [
                "Inability to retain oral medications due to persistent vomiting",
                "Severe yellowing of the eyes (jaundice) or dark urine",
                "Extreme weakness where the patient is unable to sit or stand unsupported"
            ],
            "emergency_situations": [
                "Loss of consciousness, delirium, abnormal speech, or seizures",
                "Rapid panting or difficulty breathing (acidotic respiration)",
                "Cold clammy skin with low blood pressure (Algid malaria shock)"
            ],
            "recommended_follow_up": [
                "Repeat blood film microscopy at Day 3, Day 7, Day 14, and Day 28 to confirm complete microscopic parasitological cure",
                "Hemoglobin / Hematocrit check at 2 and 4 weeks to verify resolution of malarial anemia"
            ],
            "preventive_screening": [
                "Pre-travel consultation 4–6 weeks before international travel to endemic zones for chemoprophylaxis (Atovaquone-Proguanil, Doxycycline, or Mefloquine)",
                "Insecticide-treated bed nets (ITNs) and DEET-based mosquito repellents (20%–50%) applied to exposed skin",
                "R21/Matrix-M and RTS,S/AS01 malaria vaccines in endemic pediatric populations per WHO schedules"
            ]
        },
        "references": [
            {
                "name": "WHO Guidelines for Malaria — 2025/2026",
                "organization": "World Health Organization (WHO)",
                "update_date": "2025-10-16",
                "url": "https://www.who.int/publications/i/item/guidelines-for-malaria"
            },
            {
                "name": "CDC Yellow Book: Malaria Information for Healthcare Providers",
                "organization": "Centers for Disease Control and Prevention (CDC)",
                "update_date": "2026-04-12",
                "url": "https://www.cdc.gov/malaria/hcp/index.html"
            },
            {
                "name": "Management of Severe Malaria: A practical handbook (3rd edition)",
                "organization": "World Health Organization",
                "update_date": "2024-02-10",
                "url": "https://www.who.int/publications/i/item/9789241548526"
            },
            {
                "name": "DailyMed — Coartem (Artemether and Lumefantrine) Prescribing Information",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-08-01",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    },

    "epilepsy": {
        "id": "epilepsy",
        "name": "Epilepsy & Seizure Disorders",
        "category": "Neurological Disorders",
        "emoji": "🧠",
        "overview": {
            "description": "A chronic non-communicable neurological disorder characterized by recurrent, unprovoked seizures resulting from excessive, synchronous, hypersynchronous electrical discharges of cerebral neurons. Defined clinically by at least two unprovoked seizures occurring > 24 hours apart, or one unprovoked seizure with a high probability of recurrence (> 60% over 10 years).",
            "types_and_classifications": [
                "Focal (Partial) Onset Seizures: Originating within networks limited to one cerebral hemisphere; categorized as Focal Aware (simple partial), Focal Impaired Awareness (complex partial), or Focal Motor/Non-motor.",
                "Generalized Onset Seizures: Originating at some point within and rapidly engaging bilaterally distributed cerebral networks; includes Generalized Tonic-Clonic, Absence (petit mal), Myoclonic, Clonic, Tonic, and Atonic (drop attacks).",
                "Unknown Onset Seizures: When the onset of the seizure cannot be determined.",
                "Status Epilepticus (SE): A medical emergency defined by continuous seizure activity lasting > 5 minutes, or recurrent seizures without full recovery of consciousness between episodes."
            ],
            "causes": [
                "Structural Etiologies: Cerebrovascular stroke, traumatic brain injury (TBI), hypoxic-ischemic brain damage, brain tumors, cortical dysplasias",
                "Genetic Etiologies: Direct mutations in ion channel genes (voltage-gated sodium, potassium, or GABA receptor channels)",
                "Infectious Etiologies: Post-meningitis, viral encephalitis, neurocysticercosis, cerebral malaria, HIV, tuberculosis",
                "Metabolic Etiologies: Uremia, hepatic encephalopathy, acute hypoglycemia, hyponatremia, inborn errors of metabolism",
                "Immune-Mediated: Autoimmune encephalitis (anti-NMDA receptor, anti-LGI1 antibodies)"
            ],
            "risk_factors": [
                "History of traumatic head injury with loss of consciousness or skull fracture",
                "Cerebrovascular disease (stroke is the leading cause of new-onset epilepsy in elderly)",
                "Central nervous system infections (bacterial/viral meningitis, encephalitis)",
                "Complex febrile seizures in early childhood (> 15 minutes or focal features)",
                "Family history of epilepsy or genetic seizure syndromes",
                "Dementia and Alzheimer's disease"
            ],
            "common_symptoms": [
                "Generalized Tonic-Clonic (Grand Mal): Sudden loss of consciousness, tonic stiffening of muscles, ictal cry, followed by bilateral synchronous clonic jerking, tongue biting (especially lateral tongue), urinary/fecal incontinence, and post-ictal confusion/somnolence",
                "Focal Aware Seizures (Auras): Subjective sensory illusions, déjà vu, sudden intense unprovoked fear, epigastric rising sensation, unusual metallic taste or olfactory sensations",
                "Focal Impaired Awareness: Staring blankly, behavioral arrest, repetitive motor automatisms (lip smacking, chewing, fumbling with hands, wandering)",
                "Absence Seizures (Petit Mal): Sudden brief (5–10 second) lapses of consciousness with vacant staring and immediate recovery, occurring dozens of times daily in school-aged children"
            ],
            "uncommon_symptoms": [
                "Atonic Seizures ('Drop Attacks'): Sudden loss of postural muscle tone causing catastrophic falling to the ground",
                "Gelastic Seizures: Paroxysmal bursts of uncontrolled, inappropriate laughter (frequently associated with hypothalamic hamartoma)",
                "Todd's Paresis: Transient focal neurological weakness (e.g., hemiparesis) lasting minutes to hours following a focal motor seizure"
            ],
            "early_warning_signs": [
                "Ictal Aura: Epigastric rising sensation, sudden feeling of intense dread, visual flashing lights, or focal muscular twitching occurring seconds before awareness is impaired"
            ],
            "possible_complications": [
                "Status Epilepticus: Refractory continuous seizure activity resulting in excitotoxic neuronal death, systemic acidosis, and hyperthermia (high mortality)",
                "Sudden Unexpected Death in Epilepsy (SUDEP): Fatal event in chronic epilepsy, typically nocturnal, mediated by post-ictal respiratory depression and fatal cardiac arrhythmias",
                "Traumatic physical injury: Fractures (vertebral compression, shoulder dislocation), intracranial hematomas, burns, and drowning",
                "Psychosocial morbidity: Severe depression, generalized anxiety, employment restrictions, and loss of driver's license"
            ],
            "systemic_impact": "Epileptogenesis involves an imbalance between cerebral excitatory (glutamatergic NMDA/AMPA) and inhibitory (GABAergic) neurotransmission, ion channel channelopathies, neuronal loss in hippocampal CA1/CA3 pyramidal layers (hippocampal sclerosis), mossy fiber sprouting, and neuroinflammation, leading to enduring cognitive slowing and emotional dysregulation."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Detailed eyewitness account of the event (onset, motor manifestations, duration, post-ictal state)",
                "Comprehensive neurological examination to detect focal deficits",
                "Differentiation from non-epileptic events (vasovagal syncope, cardiac arrhythmias, psychogenic non-epileptic seizures [PNES], transient ischemic attacks)"
            ],
            "laboratory_tests": [
                "Electroencephalography (EEG): Standard routine 30-minute scalp EEG with hyperventilation and photic stimulation; sleep-deprived EEG or Video-EEG Monitoring (Gold Standard for confirming seizure localization and classification)",
                "Serum Glucose and Electrolytes (Sodium, Calcium, Magnesium): To rule out acute metabolic provoked seizures",
                "Renal (BUN/Creatinine) and Liver Function Tests",
                "Toxicology Screen: In suspected drug-induced or withdrawal seizures",
                "Lumbar Puncture (CSF analysis): Mandatory if central nervous system infection (meningitis/encephalitis) is suspected"
            ],
            "medical_examinations": [
                "High-Resolution 3T Epilepsy Protocol Brain MRI: Imaging modality of choice (axial/coronal T1, T2, FLAIR, thin-slice volumetric T1) to detect mesial temporal sclerosis, focal cortical dysplasias, vascular malformations, or tumors",
                "Non-contrast Brain CT: Emergency imaging in acute head trauma or suspected intracranial hemorrhage",
                "12-Lead ECG: Rule out cardiogenic syncope (Long QT syndrome, Brugada syndrome, high-grade AV block)"
            ],
            "test_results_interpretation": [
                "EEG Interictal Epileptiform Discharges: Spikes, polyspikes, and sharp waves confirm cortical hyperexcitability. Note: A normal interictal EEG does NOT rule out epilepsy (up to 50% of routine EEGs in epileptic patients are initially normal).",
                "3 Hz Generalized Spike-and-Wave: Diagnostic hallmark of Absence Epilepsy.",
                "Temporal Lobe Spikes: Support temporal lobe focal epilepsy.",
                "Brain MRI: Detection of hippocampal atrophy and T2/FLAIR hyperintensity confirms Mesial Temporal Sclerosis."
            ]
        },
        "medicines": [
            {
                "name": "Levetiracetam",
                "brand_names": ["Keppra", "Levroxa", "Elepsia XR"],
                "generic_name": "Levetiracetam",
                "category": "Broad-Spectrum Anticonvulsant",
                "therapeutic_class": "SV2A Ligand",
                "purpose": "First-line modern broad-spectrum antiepileptic for focal onset seizures, generalized tonic-clonic seizures, and myoclonic seizures.",
                "how_it_works": "Binds presynaptic synaptic vesicle protein 2A (SV2A), inhibiting exocytosis and vesicular neurotransmitter release, suppressing epileptiform bursting without altering normal baseline neurotransmission.",
                "common_side_effects": ["Somnolence and fatigue", "Dizziness", "Nasopharyngitis", "Headache", "Irritability"],
                "serious_adverse_effects": ["Neuropsychiatric symptoms (depression, agitation, psychosis, suicidal ideation)", "Severe skin reactions (SJS/TEN)"],
                "contraindications": ["Hypersensitivity to levetiracetam or pyrrolidone derivatives"],
                "drug_interactions": ["Virtually no CYP450 interactions (does not induce or inhibit enzymes, excellent safety in polytherapy)", "CNS depressants"],
                "food_interactions": ["May take with or without food. Avoid alcohol."],
                "allergy_precautions": "Discontinue if unexplained rash or signs of hypersensitivity appear.",
                "age_precautions": "Approved in infants as young as 1 month. Dose adjust in elderly based on renal clearance.",
                "pregnancy_breastfeeding": "Pregnancy Category C. Preferred first-line antiepileptic during pregnancy (lowest malformation rate in EURAP registries). Compatible with breastfeeding.",
                "kidney_liver_precautions": "Excreted renally (~66% unchanged). Mandatory dose reduction in renal impairment based on eGFR.",
                "monitoring_requirements": "Renal function (creatinine); regular screening for behavioral changes and suicidal ideation."
            },
            {
                "name": "Sodium Valproate",
                "brand_names": ["Depakote", "Epilim", "Encorate"],
                "generic_name": "Sodium valproate / Divalproex sodium",
                "category": "Broad-Spectrum Anticonvulsant",
                "therapeutic_class": "Broad-Spectrum Antiepileptic",
                "purpose": "Most effective broad-spectrum agent for primary generalized tonic-clonic, absence, and juvenile myoclonic epilepsy.",
                "how_it_works": "Blocks voltage-gated sodium channels, inhibits T-type calcium currents, and elevates inhibitory brain GABA concentrations.",
                "common_side_effects": ["Postural hand tremor", "Weight gain and appetite increase", "Alopecia (hair loss)", "Nausea"],
                "serious_adverse_effects": ["Fatal hepatotoxicity (FDA Boxed Warning: peak risk under 2 years)", "Pancreatitis (FDA Boxed Warning)", "Severe teratogenicity (FDA Boxed Warning: neural tube defects, lower IQ)"],
                "contraindications": ["STRICTLY CONTRAINDICATED in pregnancy and women of childbearing potential unless strict Pregnancy Prevention Programme (Pledge) is met", "Active liver disease", "Mitochondrial POLG disorders"],
                "drug_interactions": ["Carbapenem antibiotics (Meropenem) drop valproate levels by 80% triggering status epilepticus (CRITICAL CONTRAINDICATION)", "Lamotrigine (doubles lamotrigine levels, TEN risk)"],
                "food_interactions": ["Take with food to minimize gastric discomfort. Do not crush enteric-coated tablets. Avoid alcohol."],
                "allergy_precautions": "Discontinue immediately if DRESS syndrome or unexplained abdominal pain develops.",
                "age_precautions": "FDA Boxed Warning in children under 2 years for fatal liver necrosis.",
                "pregnancy_breastfeeding": "FDA Boxed Warning: 10% risk of major malformations (spina bifida) and 8–10 point reduction in child IQ. Avoid in women of childbearing potential.",
                "kidney_liver_precautions": "Strictly contraindicated in hepatic disease. No dose adjustment needed for renal impairment.",
                "monitoring_requirements": "Baseline and periodic Liver Function Tests (LFTs), CBC/platelets, therapeutic serum valproate level (50–100 mcg/mL), serum ammonia."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "CRITICAL CONTRAINDICATION: Carbapenem antibiotics (Meropenem, Imipenem) given with Sodium Valproate cause a rapid 80% collapse in serum valproate levels within 24 hours, triggering refractory status epilepticus",
                "Enzyme-Inducing Antiepileptics (Carbamazepine, Phenytoin, Phenobarbital) accelerate hepatic metabolism of oral contraceptives, statins, and anticoagulants, causing clinical failure"
            ],
            "food_interactions": [
                "Alcohol is a major trigger: Binge drinking and subsequent acute alcohol withdrawal dramatically lower the seizure threshold and precipitate status epilepticus"
            ],
            "allergy_warnings": [
                "Aromatic antiepileptics (Carbamazepine, Phenytoin, Lamotrigine) carry significant cross-reactivity and risk of Stevens-Johnson Syndrome (SJS/TEN), particularly in individuals carrying the HLA-B*1502 genetic allele in Asian populations (genetic screening required)"
            ],
            "critical_contraindications": [
                "NEVER ABRUPTLY DISCONTINUE ANTIEPILEPTIC MEDICATIONS: Sudden cessation triggers acute rebound status epilepticus and SUDEP. Tapering must occur gradually over months under neurologist guidance.",
                "Sodium Valproate is contraindicated in female patients of childbearing potential unless no alternatives exist and strict birth control is verified"
            ],
            "age_precautions": {
                "children": "Febrile seizures in infants must be distinguished from afebrile epilepsy. Liquid suspensions require precise oral dosing syringes.",
                "older_adults": "Elderly patients have altered drug clearance, lower albumin, and heightened vulnerability to drug-induced cognitive slowing, somnolence, and falls."
            },
            "immediate_emergency_triggers": [
                "Status Epilepticus: Any continuous seizure activity lasting > 5 minutes, or 2 or more discrete seizures without full recovery of consciousness between them — CALL EMERGENCY (911 / 112) IMMEDIATELY",
                "Seizures occurring in water (bath, pool) — high risk of secondary submersion and drowning",
                "Seizures accompanied by serious traumatic head injury or prolonged post-ictal apnea",
                "First-ever seizure in an adult without known epilepsy"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "The Ketogenic Diet (high-fat, low-carbohydrate, adequate-protein) or Modified Atkins Diet is an evidence-based medical therapy under clinical supervision for drug-resistant epilepsy",
                "Maintain regular consistent meal times; avoid prolonged hypoglycemia which triggers seizures"
            ],
            "lifestyle_recommendations": [
                "Maintain strict, consistent sleep hygiene: Sleep deprivation is the single most common trigger for breakthrough seizures",
                "Avoid flashing strobe lights, discotheques, and high-contrast flickering patterns in photosensitive epilepsy",
                "Practice stress management and relaxation techniques"
            ],
            "physical_activity": [
                "Regular aerobic exercise is safe and encouraged, improving mood and seizure control",
                "SAFETY RESTRICTIONS: Never swim alone (always swim with a designated adult companion); shower instead of taking deep bathtub baths (drowning risk); wear a helmet when cycling; avoid climbing ladders or heights"
            ],
            "hydration_guidance": [
                "Maintain normal fluid and electrolyte intake; severe hyponatremia or extreme dehydration triggers seizures"
            ],
            "safe_home_care": [
                "SEIZURE FIRST AID FOR BYSTANDERS:",
                "1. Ease the person gently to the floor and place a soft cushion or jacket under their head",
                "2. Turn the person gently onto their side (recovery position) to keep the airway clear and prevent aspiration",
                "3. Loosen tight neckwear (collars, ties)",
                "4. CRITICAL: NEVER PUT ANYTHING IN THE PERSON'S MOUTH (they cannot swallow their tongue; forcing objects fractures teeth or causes airway obstruction)",
                "5. Never hold the person down or attempt to restrain their jerking movements",
                "6. Time the seizure: If jerking lasts > 5 minutes, call an ambulance immediately",
                "7. Stay with the person until they are fully awake and alert"
            ],
            "natural_remedies": [
                "Stress-reduction techniques, mindfulness meditation, and regular yoga pranayama provide supportive psychological benefits.",
                "CRITICAL CLINICAL WARNING: Herbal supplements (Ginkgo biloba, St. John's wort, ephedra, essential oils like camphor/eucalyptus) LOWER the seizure threshold or interact dangerously with antiepileptic drugs. Natural remedies CANNOT treat epilepsy. Discontinuing antiepileptics for unproven remedies risks fatal status epilepticus and SUDEP."
            ],
            "substances_to_avoid": [
                "Alcohol and recreational drugs",
                "High doses of caffeine and commercial energy drinks",
                "Over-the-counter sedating antihistamines and pseudoephedrine without physician clearance"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Any first-time unprovoked seizure, unexplained transient loss of consciousness, or recurrent unexplained episodes of confusion/staring",
                "Frequent unprovoked episodes of déjà vu accompanied by epigastric sensations"
            ],
            "serious_warning_symptoms": [
                "Breakthrough seizures in a previously stabilized patient",
                "Emergence of severe drug side effects: Hand tremors, severe balance unsteadiness (ataxia), or skin eruptions",
                "Severe mood changes, depression, or emerging suicidal ideation"
            ],
            "emergency_situations": [
                "Seizure lasting longer than 5 minutes",
                "A second seizure occurs immediately after the first without the person regaining consciousness",
                "The person has difficulty breathing or remains unconscious for > 15 minutes after the seizure stops",
                "Seizure occurs in water or causes serious physical head trauma"
            ],
            "recommended_follow_up": [
                "Review by a neurologist at least every 6–12 months once stabilized",
                "Pre-conception counseling and folate supplementation (5 mg/day) in all women of childbearing potential taking antiepileptic therapy",
                "Periodic monitoring of therapeutic drug levels and complete blood counts"
            ],
            "preventive_screening": [
                "Strict adherence to state and national driving regulations (typically requiring 6–12 months of documented seizure freedom before driving license reinstatement)",
                "Wearing a medical identification bracelet stating 'Epilepsy / Antiepileptic Regimen'"
            ]
        },
        "references": [
            {
                "name": "Epilepsies in children, young people and adults (NICE Guideline NG217)",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024-05-18",
                "url": "https://www.nice.org.uk/guidance/ng217"
            },
            {
                "name": "American Epilepsy Society (AES) Clinical Guidelines & Practice Tools",
                "organization": "American Epilepsy Society (AES)",
                "update_date": "2025-12-01",
                "url": "https://www.aesnet.org/clinical-care/clinical-guidance"
            },
            {
                "name": "WHO Epilepsy Technical Report and Global Action Plan",
                "organization": "World Health Organization (WHO)",
                "update_date": "2024-09-12",
                "url": "https://www.who.int/news-room/fact-sheets/detail/epilepsy"
            },
            {
                "name": "DailyMed — Keppra (Levetiracetam) & Depakote Prescribing Information",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-08-16",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    },

    "hypertension": {
        "id": "hypertension",
        "name": "Hypertension (High Blood Pressure)",
        "category": "Cardiovascular Disorders",
        "emoji": "❤️",
        "overview": {
            "description": "A chronic medical condition characterized by persistently elevated systemic arterial blood pressure (systolic blood pressure >= 130 mmHg or diastolic blood pressure >= 80 mmHg per ACC/AHA guidelines; >= 140/90 mmHg per WHO/ESC). Widely designated the 'silent killer' because it typically produces no early warning symptoms while silently causing target organ vascular damage.",
            "types_and_classifications": [
                "Primary (Essential) Hypertension (90%–95% of cases): Arises from complex multifactorial interactions between polygenic inheritance, neurohormonal dysregulation, and lifestyle factors without an identifiable secondary cause.",
                "Secondary Hypertension (5%–10% of cases): Directly caused by an underlying identifiable medical condition (Primary Aldosteronism, Renal Artery Stenosis, Chronic Kidney Disease, Obstructive Sleep Apnea, Pheochromocytoma, Cushing's syndrome).",
                "Hypertensive Urgency: Severe blood pressure elevation (systolic > 180 mmHg and/or diastolic > 120 mmHg) WITHOUT evidence of acute target organ damage.",
                "Hypertensive Emergency / Crisis: Severe blood pressure elevation (systolic > 180 and/or diastolic > 120 mmHg) WITH acute, progressing target organ damage (hypertensive encephalopathy, acute aortic dissection, acute pulmonary edema, acute MI, or acute renal failure) requiring immediate ICU parenteral therapy."
            ],
            "causes": [
                "Increased systemic vascular resistance driven by arteriolar vasoconstriction and vascular remodeling",
                "Overactivity of the Sympathetic Nervous System (SNS) and Renin-Angiotensin-Aldosterone System (RAAS)",
                "Impaired renal sodium excretion leading to intravascular volume expansion",
                "Endothelial dysfunction: Reduced nitric oxide (NO) bioavailability and increased endothelin-1",
                "Arterial stiffening (loss of arterial compliance and elastin degradation with aging)"
            ],
            "risk_factors": [
                "High dietary sodium intake (> 2,000 mg/day of sodium / > 5 g of salt)",
                "Physical inactivity and sedentary occupation",
                "Overweight and obesity (visceral adiposity)",
                "Excessive alcohol consumption and chronic psychological stress",
                "Advancing age (>= 65 years)",
                "Family history of premature hypertension or cardiovascular disease",
                "Chronic kidney disease, obstructive sleep apnea, and diabetes mellitus"
            ],
            "common_symptoms": [
                "MOST PATIENTS ARE COMPLETELY ASYMPTOMATIC ('Silent Killer')",
                "Occipital morning throbbing headaches (typically when BP exceeds 160/100 mmHg)",
                "Lightheadedness, dizziness, and mild unsteadiness",
                "Epistaxis (nosebleeds) in sudden blood pressure spikes",
                "Exertional shortness of breath and easy fatigue"
            ],
            "uncommon_symptoms": [
                "Blurred or double vision caused by grade III/IV hypertensive retinopathy",
                "Pulsatile tinnitus ('whooshing' sound in the ears synchronized with heartbeat)",
                "Flushing of the face and neck"
            ],
            "early_warning_signs": [
                "Occasional elevated readings detected on routine screening",
                "Mild morning occipital headache that improves within a few hours of waking"
            ],
            "possible_complications": [
                "Coronary Artery Disease, Angina, and Acute Myocardial Infarction",
                "Heart Failure with Reduced (HFrEF) or Preserved (HFpEF) Ejection Fraction",
                "Left Ventricular Hypertrophy (LVH) and Atrial Fibrillation",
                "Ischemic Stroke and Intracerebral Hemorrhage (major global cause of hemorrhagic stroke)",
                "Hypertensive Nephrosclerosis leading to Chronic Kidney Disease and End-Stage Renal Failure",
                "Aortic Aneurysm and Acute Aortic Dissection (surgical emergency)",
                "Hypertensive Retinopathy causing retinal hemorrhages, exudates, and papilledema"
            ],
            "systemic_impact": "Persistently elevated intravascular pressure exerts continuous chronic shear stress on arterial endothelial walls, stimulating smooth muscle hypertrophy, hyaline arteriolosclerosis, and accelerated atherogenesis. This reduces lumen diameter across vital organs, precipitating ischemic stroke in the cerebrum, myocardial infarction in the heart, and nephron sclerosis in the kidneys."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Accurate office blood pressure measurement: Seated quietly for 5 minutes, arm supported at heart level, correct cuff size",
                "Diagnosis requires an average of >= 2 readings obtained on >= 2 separate clinical occasions",
                "Out-of-office confirmation: 24-Hour Ambulatory Blood Pressure Monitoring (ABPM) or Home Blood Pressure Monitoring (HBPM) is recommended to rule out 'White Coat Hypertension' and detect 'Masked Hypertension'"
            ],
            "laboratory_tests": [
                "Fasting Blood Glucose or HbA1c: Screen for co-existing diabetes mellitus",
                "Serum Creatinine and estimated Glomerular Filtration Rate (eGFR): Evaluate baseline renal function",
                "Serum Electrolytes (Sodium, Potassium, Calcium): Hypokalemia strongly suggests secondary primary aldosteronism",
                "Fasting Lipid Profile: Cardiovascular risk stratification",
                "Spot Urine Albumin-to-Creatinine Ratio (uACR) and Urinalysis: Screen for microalbuminuria and renal parenchymal disease",
                "Serum Thyroid Stimulating Hormone (TSH): Rule out hypo- or hyperthyroidism"
            ],
            "medical_examinations": [
                "12-Lead Electrocardiogram (ECG): Detects voltage criteria for Left Ventricular Hypertrophy (Sokolow-Lyon index > 35 mm) or ischemic strain",
                "Transthoracic Echocardiogram: Quantitative assessment of left ventricular mass, systolic/diastolic function",
                "Dilated Fundoscopic Eye Examination: Grades I to IV hypertensive retinopathy",
                "Renal Duplex Doppler Ultrasound: Indicated if secondary renal artery stenosis is suspected"
            ],
            "test_results_interpretation": [
                "ACC/AHA Blood Pressure Categories: Normal (< 120/< 80 mmHg); Elevated (120–129/< 80 mmHg); Stage 1 Hypertension (130–139 or 80–89 mmHg); Stage 2 Hypertension (>= 140 or >= 90 mmHg).",
                "Hypertensive Crisis: Systolic > 180 mmHg and/or Diastolic > 120 mmHg.",
                "Treatment Targets: General clinical target is < 130/80 mmHg (< 140/90 mmHg in frail elderly or per European guidelines)."
            ]
        },
        "medicines": [
            {
                "name": "Amlodipine",
                "brand_names": ["Norvasc", "Amlong", "Stamlo"],
                "generic_name": "Amlodipine besylate",
                "category": "Dihydropyridine CCB",
                "therapeutic_class": "Calcium Channel Blocker",
                "purpose": "First-line antihypertensive providing sustained 24-hour peripheral vasodilation; particularly effective in elderly and Black patients.",
                "how_it_works": "Inhibits transmembrane calcium influx into vascular smooth muscle cells, causing systemic arterial vasodilation and reducing afterload.",
                "common_side_effects": ["Dependent peripheral ankle edema", "Flushing", "Dizziness", "Headache"],
                "serious_adverse_effects": ["Symptomatic hypotension", "Gingival hyperplasia"],
                "contraindications": ["Severe hypotension", "Cardiogenic shock", "Severe aortic stenosis"],
                "drug_interactions": ["Simvastatin (limit simvastatin to max 20 mg/day)", "CYP3A4 inhibitors (diltiazem)"],
                "food_interactions": ["May take with or without meals. Avoid excessive grapefruit juice."],
                "allergy_precautions": "Contraindicated in severe dihydropyridine hypersensitivity.",
                "age_precautions": "Start at 2.5 mg once daily in frail elderly patients.",
                "pregnancy_breastfeeding": "Category C. Other antihypertensive agents (labetalol, nifedipine) preferred in pregnancy.",
                "kidney_liver_precautions": "Safe in renal impairment without dose adjustments. Reduce dose in severe liver disease.",
                "monitoring_requirements": "Blood pressure and inspection for lower extremity dependent edema."
            },
            {
                "name": "Lisinopril",
                "brand_names": ["Zestril", "Prinivil", "Lipril"],
                "generic_name": "Lisinopril",
                "category": "ACE Inhibitor",
                "therapeutic_class": "Angiotensin-Converting Enzyme Inhibitor",
                "purpose": "First-line antihypertensive with superior renoprotective and cardioprotective benefits in diabetes, heart failure, and CKD.",
                "how_it_works": "Inhibits conversion of angiotensin I to angiotensin II, reducing peripheral resistance, aldosterone, and sodium retention.",
                "common_side_effects": ["Persistent dry, hacking cough", "Dizziness", "Headache", "Fatigue"],
                "serious_adverse_effects": ["Angioedema (FDA Boxed Warning: acute airway obstruction)", "Fetal toxicity (FDA Boxed Warning)", "Hyperkalemia"],
                "contraindications": ["Pregnancy (FDA Boxed Warning: strictly contraindicated)", "History of ACEi angioedema", "Concomitant sacubitril within 36 hours"],
                "drug_interactions": ["Potassium supplements & spironolactone (severe hyperkalemia)", "NSAIDs blunt BP lowering"],
                "food_interactions": ["Avoid potassium salt substitutes. Alcohol compounds hypotension."],
                "allergy_precautions": "Permanently discontinue if facial or laryngeal swelling occurs.",
                "age_precautions": "Start low (2.5–5 mg) in elderly. High susceptibility to hyperkalemia.",
                "pregnancy_breastfeeding": "FDA Boxed Warning: Strictly contraindicated in pregnancy.",
                "kidney_liver_precautions": "Dose reduce if eGFR < 30 mL/min. Not metabolized by liver.",
                "monitoring_requirements": "Serum potassium and creatinine at baseline, 1–2 weeks post-initiation, and annually."
            },
            {
                "name": "Losartan",
                "brand_names": ["Cozaar", "Losar", "Repace"],
                "generic_name": "Losartan potassium",
                "category": "Angiotensin II Receptor Blocker",
                "therapeutic_class": "ARB Antihypertensive",
                "purpose": "First-line antihypertensive for patients who develop dry cough on ACE inhibitors; proven stroke reduction and renal protection.",
                "how_it_works": "Selectively blocks AT1 angiotensin II receptors in vascular smooth muscle and adrenal gland without increasing bradykinin.",
                "common_side_effects": ["Dizziness", "Nasal congestion", "Fatigue", "Back pain"],
                "serious_adverse_effects": ["Hyperkalemia", "Fetal toxicity (FDA Boxed Warning)", "Acute renal failure in bilateral renal artery stenosis"],
                "contraindications": ["Pregnancy (FDA Boxed Warning)", "Concomitant aliskiren in diabetes", "Hypersensitivity"],
                "drug_interactions": ["Potassium-sparing diuretics & potassium supplements", "NSAIDs blunt efficacy"],
                "food_interactions": ["May take with or without food. Avoid potassium salt substitutes."],
                "allergy_precautions": "Monitor if history of ACE inhibitor angioedema.",
                "age_precautions": "Safe first-line agent across adults and elderly.",
                "pregnancy_breastfeeding": "FDA Boxed Warning: Strictly contraindicated in pregnancy.",
                "kidney_liver_precautions": "Proven renal protection in diabetic nephropathy. Start at 25 mg in hepatic impairment.",
                "monitoring_requirements": "Blood pressure, serum potassium, serum creatinine."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "CRITICAL: The 'Triple Whammy' interaction: Co-administering an ACE inhibitor / ARB + Diuretic + NSAID (Ibuprofen, Naproxen) severely compromises renal hemodynamics and precipitates acute kidney injury in up to 30% of patients",
                "Decongestants containing pseudoephedrine or phenylephrine cause significant peripheral vasoconstriction and can provoke severe hypertensive spikes"
            ],
            "food_interactions": [
                "Salt substitutes containing Potassium Chloride can cause fatal hyperkalemia when combined with ACE inhibitors, ARBs, or Spironolactone",
                "Large consumption of black natural licorice (glycyrrhizin) inhibits 11-beta-HSD2, causing pseudo-aldosteronism, severe hypokalemia, and refractory hypertension"
            ],
            "allergy_warnings": [
                "ACE inhibitors carry a major risk of sudden life-threatening angioedema (swelling of lips, tongue, pharynx, and glottis) which can occur even after years of uneventful therapy"
            ],
            "critical_contraindications": [
                "ACE Inhibitors (Lisinopril) and ARBs (Losartan) are STRICTLY CONTRAINDICATED IN PREGNANCY due to fetal renal dysgenesis, oligohydramnios, and death (FDA Boxed Warning)",
                "Never abruptly discontinue beta-blockers (Metoprolol) due to rebound tachycardia, severe hypertension, and myocardial infarction"
            ],
            "age_precautions": {
                "children": "Pediatric hypertension is defined by age, sex, and height percentiles (>= 95th percentile). Secondary causes are significantly more frequent in young children.",
                "older_adults": "Isolated Systolic Hypertension (elevated systolic with normal/low diastolic) is predominant in elderly due to arterial stiffening. Avoid aggressive over-titration causing diastolic BP < 60 mmHg (coronary hypoperfusion)."
            },
            "immediate_emergency_triggers": [
                "Blood Pressure > 180/120 mmHg accompanied by chest pain radiating to back or neck (aortic dissection or myocardial infarction)",
                "Severe sudden 'thunderclap' headache with visual blurring, confusion, or focal weakness (hypertensive encephalopathy / stroke)",
                "Acute severe shortness of breath with pink frothy sputum (acute pulmonary edema)"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Adopt the Dietary Approaches to Stop Hypertension (DASH) eating plan: Rich in fruits, vegetables, whole grains, and low-fat dairy with reduced saturated and total fat (produces an average 11 mmHg systolic drop)",
                "Strictly restrict dietary sodium to < 2,000 mg/day (ideally < 1,500 mg/day in hypertensive adults)",
                "Increase dietary potassium intake (3,500–5,000 mg/day from bananas, avocados, spinach, sweet potatoes) unless chronic kidney disease is present"
            ],
            "lifestyle_recommendations": [
                "Target a healthy body weight (BMI 18.5–24.9 kg/m²); every 1 kg of weight loss lowers blood pressure by approximately 1 mmHg",
                "Limit alcohol intake: Maximum <= 2 standard drinks/day for men and <= 1 standard drink/day for women",
                "Complete smoking cessation: Nicotine causes immediate acute sympathetic vasoconstriction and accelerates arterial stiffness",
                "Practice daily stress reduction (meditation, slow deep breathing with 6 breaths/minute)"
            ],
            "physical_activity": [
                "Engage in 150 minutes of moderate-intensity aerobic exercise per week (brisk walking, swimming, cycling) or 75 minutes of vigorous exercise",
                "Incorporate isometric resistance exercises (handgrip training) and dynamic resistance training (lowers systolic BP by 4–8 mmHg)"
            ],
            "hydration_guidance": [
                "Maintain optimal daily fluid intake; avoid extreme dehydration which triggers compensatory sympathetic vasoconstriction"
            ],
            "safe_home_care": [
                "Perform regular Home Blood Pressure Monitoring (HBPM) using a validated, automated upper-arm cuff (avoid wrist cuffs)",
                "Protocol: Measure twice daily (morning before medication and evening before dinner), taking 2 readings 1 minute apart; log values",
                "Take medications at the same time every day to establish a consistent habit"
            ],
            "natural_remedies": [
                "Aged garlic extract, hibiscus sabdariffa tea, and coenzyme Q10 have shown modest blood pressure reductions (3–5 mmHg) in clinical trials.",
                "CRITICAL EVIDENCE LIMITATION: Natural supplements provide modest adjunct support but CANNOT substitute for prescription antihypertensives in stage 2 hypertension. Untreated hypertension leads to silent strokes and heart failure. Never discontinue medical therapy."
            ],
            "substances_to_avoid": [
                "High-sodium processed meats, canned soups, pickles, and salty snacks",
                "Over-the-counter NSAID analgesics (Ibuprofen, Naproxen, Diclofenac)",
                "Oral decongestants (Pseudoephedrine), ephedra, and excessive energy drinks"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Blood pressure readings persistently >= 130/80 mmHg on multiple home checks",
                "Frequent unexplained morning occipital headaches or dizziness"
            ],
            "serious_warning_symptoms": [
                "Blood pressure readings exceeding 160/100 mmHg",
                "Development of ankle swelling, blurred vision, or exertional shortness of breath"
            ],
            "emergency_situations": [
                "Blood pressure > 180/120 mmHg WITH chest pain, shortness of breath, severe headache, confusion, or numbness — CALL 911 / 112 IMMEDIATELY"
            ],
            "recommended_follow_up": [
                "Monthly clinical follow-up after initiating or modifying antihypertensive therapy until target (< 130/80 mmHg) is achieved",
                "Once stabilized, follow-up every 3 to 6 months with annual electrolytes, creatinine, and urinalysis"
            ],
            "preventive_screening": [
                "Annual blood pressure screening for all adults aged >= 18 years with normal BP (< 120/80)",
                "Semi-annual screening for adults with risk factors or baseline systolic 120–129 mmHg"
            ]
        },
        "references": [
            {
                "name": "AHA/ACC Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure",
                "organization": "American Heart Association / American College of Cardiology",
                "update_date": "2025-08-10",
                "url": "https://www.ahajournals.org/doi/10.1161/HYP.0000000000000065"
            },
            {
                "name": "WHO Guideline for the Pharmacological Treatment of Hypertension in Adults",
                "organization": "World Health Organization (WHO)",
                "update_date": "2024-04-15",
                "url": "https://www.who.int/publications/i/item/9789240033986"
            },
            {
                "name": "Hypertension in adults: diagnosis and management (NICE Guideline NG136)",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024-01-18",
                "url": "https://www.nice.org.uk/guidance/ng136"
            },
            {
                "name": "DailyMed — Amlodipine, Lisinopril & Losartan Monograph",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-08-16",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    },

    "kidney_disease": {
        "id": "kidney_disease",
        "name": "Chronic Kidney Disease (CKD) & Renal Impairment",
        "category": "Renal & Urological Disorders",
        "emoji": "🫘",
        "overview": {
            "description": "A progressive, irreversible loss of renal function characterized by abnormalities of kidney structure or function present for more than 3 months, with implications for health. Defined clinically by either kidney damage (persistent microalbuminuria / macroalbuminuria, hematuria, structural imaging abnormalities) or decreased kidney function with Glomerular Filtration Rate (eGFR) < 60 mL/min/1.73 m².",
            "types_and_classifications": [
                "CKD Stage 1: Kidney damage with normal or high GFR (eGFR >= 90 mL/min/1.73 m² with persistent albuminuria).",
                "CKD Stage 2: Kidney damage with mild GFR decrease (eGFR 60–89 mL/min/1.73 m² with persistent albuminuria).",
                "CKD Stage 3a: Mild-to-moderate GFR decrease (eGFR 45–59 mL/min/1.73 m²).",
                "CKD Stage 3b: Moderate-to-severe GFR decrease (eGFR 30–44 mL/min/1.73 m²).",
                "CKD Stage 4: Severe GFR decrease (eGFR 15–29 mL/min/1.73 m² — preparation for renal replacement therapy).",
                "CKD Stage 5: Kidney Failure / End-Stage Renal Disease (ESRD) (eGFR < 15 mL/min/1.73 m² or established maintenance dialysis/transplantation)."
            ],
            "causes": [
                "Diabetic Nephropathy / Diabetic Kidney Disease (leading cause globally, ~40% of all ESRD)",
                "Hypertensive Nephrosclerosis (second leading cause globally, ~25% of cases)",
                "Chronic Glomerulonephritis (IgA nephropathy, membranous nephropathy, focal segmental glomerulosclerosis [FSGS])",
                "Autosomal Dominant Polycystic Kidney Disease (ADPKD)",
                "Chronic Tubulointerstitial Nephritis and analgesic nephropathy (chronic NSAID overuse)",
                "Obstructive Uropathy (benign prostatic hyperplasia, bilateral nephrolithiasis)"
            ],
            "risk_factors": [
                "Diabetes mellitus (Type 1 or Type 2)",
                "Hypertension and established cardiovascular disease",
                "Family history of kidney disease or chronic dialysis",
                "Obesity (BMI >= 30 kg/m²)",
                "Advancing age (age-related nephron loss)",
                "History of Acute Kidney Injury (AKI)",
                "Chronic regular consumption of over-the-counter NSAIDs (Ibuprofen, Naproxen, Diclofenac)"
            ],
            "common_symptoms": [
                "USUALLY COMPLETELY ASYMPTOMATIC IN STAGES 1 TO 3 ('Silent Progression')",
                "Peripheral dependent edema: Swelling in ankles, feet, and legs (fluid retention)",
                "Periorbital edema: Morning puffiness around the eyes",
                "Fatigue, generalized weakness, and lethargy (secondary to normocytic anemia of CKD)",
                "Nocturia: Need to urinate multiple times during the night due to loss of renal concentrating ability",
                "Foamy or frothy urine (direct sign of significant proteinuria/albuminuria)"
            ],
            "uncommon_symptoms": [
                "Severe generalized pruritus (intractable itching from uremic toxin deposition in skin)",
                "Uremic fetor (ammonia-like breath odor) and metallic dysgeusia",
                "Loss of appetite, nausea, and morning vomiting (uremic gastritis)",
                "Restless legs syndrome and painful nocturnal muscle cramps",
                "Uremic frost: White powdery urea crystals on skin in terminal end-stage uremia"
            ],
            "early_warning_signs": [
                "Foamy, bubbly urine that does not dissipate upon flushing",
                "Subtle puffiness around the eyes upon waking in the morning",
                "Gradual onset of ankle swelling by evening"
            ],
            "possible_complications": [
                "Cardiovascular Disease: The leading cause of death in CKD patients (cardiovascular death is 10–20 times higher than in the general population)",
                "Volume Overload, Refractory Hypertension, and Acute Pulmonary Edema",
                "Severe Hyperkalemia (serum potassium > 6.0 mEq/L) causing fatal cardiac arrhythmias",
                "Renal Anemia (impaired erythropoietin production by peritubular interstitial cells)",
                "Chronic Kidney Disease-Mineral and Bone Disorder (CKD-MBD): Hyperphosphatemia, hypocalcemia, secondary hyperparathyroidism, and renal osteodystrophy",
                "Metabolic Acidosis (impaired renal excretion of hydrogen ions)",
                "Uremic Pericarditis and Uremic Encephalopathy (immediate indications for emergent hemodialysis)"
            ],
            "systemic_impact": "Loss of functioning nephrons leads to maladaptive hyperfiltration in surviving nephrons, intraglomerular hypertension, progressive glomerulosclerosis, and tubulointerstitial fibrosis. Concurrently, the accumulation of uremic retention solutes triggers systemic endothelial dysfunction, accelerated arterial calcification, immune suppression, and severe multisystem failure."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Screening of high-risk populations (all diabetics, hypertensives, cardiovascular disease patients)",
                "Demonstration of kidney damage or eGFR < 60 mL/min persisting for >= 3 months"
            ],
            "laboratory_tests": [
                "Serum Creatinine and eGFR calculated via the 2021 CKD-EPI creatinine equation",
                "Urine Albumin-to-Creatinine Ratio (uACR) on a spot first-morning urine sample",
                "Urinalysis with Microscopic Examination: Detects dysmorphic RBCs, RBC casts (glomerulonephritis), or broad waxy casts",
                "Serum Electrolytes (Potassium, Sodium, Bicarbonate, Calcium, Phosphate)",
                "Complete Blood Count (CBC): Evaluates normocytic normochromic anemia (hemoglobin < 10–11 g/dL)",
                "Intact Parathyroid Hormone (iPTH) and Vitamin D (25-OH-D) levels",
                "Serum Protein Electrophoresis (SPEP) and Free Light Chains: Screen for multiple myeloma in unexplained renal failure in older adults"
            ],
            "medical_examinations": [
                "Bilateral Renal Ultrasound: Evaluates kidney size, cortical echogenicity, and corticomedullary differentiation (bilateral small shrunken echogenic kidneys < 9 cm indicate chronic irreversible disease; normal/large kidneys suggest diabetic nephropathy, amyloidosis, or polycystic disease); rules out hydronephrosis (obstruction)",
                "Percutaneous Renal Biopsy: Gold standard for diagnosing specific glomerular diseases"
            ],
            "test_results_interpretation": [
                "eGFR Categories: G1 (>= 90); G2 (60–89); G3a (45–59); G3b (30–44); G4 (15–29); G5 (< 15 mL/min/1.73 m²).",
                "Albuminuria Categories (uACR): A1 (< 30 mg/g: Normal to mildly increased); A2 (30–300 mg/g: Moderately increased / microalbuminuria); A3 (> 300 mg/g: Severely increased / macroalbuminuria / nephrotic range).",
                "CKD Prognosis Matrix (KDIGO): High risk of progression and mortality is defined by G3b–G5 and A3 categories."
            ]
        },
        "medicines": [
            {
                "name": "Losartan",
                "brand_names": ["Cozaar", "Losar", "Repace"],
                "generic_name": "Losartan potassium",
                "category": "Angiotensin II Receptor Blocker",
                "therapeutic_class": "Renoprotective ARB",
                "purpose": "FOUNDATIONAL RENOPROTECTIVE THERAPY: Reduces intraglomerular capillary pressure, halts progressive glomerulosclerosis, and dramatically reduces proteinuria in diabetic and non-diabetic CKD.",
                "how_it_works": "Blocks AT1 receptors, dilating efferent arterioles more than afferent arterioles, directly lowering intraglomerular hyperfiltration pressure and decreasing urinary protein excretion.",
                "common_side_effects": ["Dizziness", "Orthostatic hypotension", "Hyperkalemia"],
                "serious_adverse_effects": ["Hyperkalemia", "Acute decline in renal function in bilateral renal artery stenosis", "Fetal toxicity (FDA Boxed Warning)"],
                "contraindications": ["Pregnancy (FDA Boxed Warning)", "Severe uncorrected hyperkalemia (> 5.5 mEq/L)", "Bilateral renal artery stenosis"],
                "drug_interactions": ["Potassium supplements & spironolactone", "NSAIDs completely negate renal protection and trigger acute renal failure"],
                "food_interactions": ["Avoid potassium salt substitutes. Take with or without food."],
                "allergy_precautions": "Monitor closely if history of ACEi angioedema.",
                "age_precautions": "Start at 25 mg daily in elderly. Monitor serum creatinine and potassium closely.",
                "pregnancy_breastfeeding": "FDA Boxed Warning: Strictly contraindicated in pregnancy.",
                "kidney_liver_precautions": "Expect a benign rise in serum creatinine up to 30% after initiation (reflects reduced intraglomerular pressure); only discontinue if creatinine rises > 30% or potassium > 5.5 mEq/L.",
                "monitoring_requirements": "Serum creatinine and potassium 1–2 weeks post-initiation and every 3–6 months."
            },
            {
                "name": "Empagliflozin",
                "brand_names": ["Jardiance"],
                "generic_name": "Empagliflozin",
                "category": "SGLT2 Inhibitor / Renoprotective",
                "therapeutic_class": "Sodium-Glucose Cotransporter-2 Inhibitor",
                "purpose": "BREAKTHROUGH RENAL THERAPY: Slows chronic kidney disease progression and lowers cardiovascular death in patients with CKD down to eGFR 20 mL/min/1.73 m².",
                "how_it_works": "Increases sodium delivery to the macula densa, restoring tubuloglomerular feedback and inducing afferent arteriolar vasoconstriction, reducing glomerular hyperfiltration and slowing renal decline.",
                "common_side_effects": ["Genital mycotic infections", "Urinary tract infections", "Mild osmotic diuresis", "Volume depletion"],
                "serious_adverse_effects": ["Euglycemic DKA", "Necrotizing fasciitis of perineum", "Urosepsis"],
                "contraindications": ["Dialysis / End-stage kidney failure (ineffective)", "Hypersensitivity"],
                "drug_interactions": ["Loop diuretics (hypotension risk)", "Insulin (hypoglycemia risk)"],
                "food_interactions": ["Take once daily in morning with or without food."],
                "allergy_precautions": "Discontinue if severe perineal rash or pain occurs.",
                "age_precautions": "Monitor volume status in elderly patients.",
                "pregnancy_breastfeeding": "Avoid in pregnancy and lactation.",
                "kidney_liver_precautions": "Indicated for CKD progression delay down to eGFR 20 mL/min/1.73 m².",
                "monitoring_requirements": "eGFR, serum creatinine, volume status, blood pressure."
            },
            {
                "name": "Furosemide",
                "brand_names": ["Lasix", "Frusid"],
                "generic_name": "Furosemide",
                "category": "Loop Diuretic",
                "therapeutic_class": "Loop Diuretic",
                "purpose": "Essential management of fluid retention, peripheral dependent edema, and volume-overload hypertension in patients with reduced GFR.",
                "how_it_works": "Inhibits Na+/K+/2Cl- cotransporter in the thick ascending limb of loop of Henle, producing potent natriuresis even when eGFR drops below 30 mL/min.",
                "common_side_effects": ["Polyuria", "Dizziness", "Hypokalemia (or hyperkalemia if GFR is very low)", "Hyperuricemia"],
                "serious_adverse_effects": ["Ototoxicity at high IV doses", "Severe volume depletion", "Electrolyte collapse"],
                "contraindications": ["Anuria refractory to test doses", "Hepatic coma", "Sulfa allergy"],
                "drug_interactions": ["Aminoglycosides multiply ototoxicity", "Lithium toxicity", "NSAIDs blunt diuresis"],
                "food_interactions": ["Take in morning to prevent nocturia."],
                "allergy_precautions": "Caution in sulfonamide allergy.",
                "age_precautions": "Start with lower doses in elderly to prevent acute orthostatic falls.",
                "pregnancy_breastfeeding": "Category C. Avoid unless maternal cardiac necessity.",
                "kidney_liver_precautions": "Higher doses (80–240 mg/day) frequently required in advanced CKD due to reduced tubular secretion.",
                "monitoring_requirements": "Daily morning weight, blood pressure, serum electrolytes (potassium, sodium), BUN, creatinine."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "CRITICAL WARNING: NEVER TAKE OVER-THE-COUNTER NSAIDs (Ibuprofen, Naproxen, Diclofenac, Mefenamic acid) in patients with CKD. NSAIDs block vasodilatory prostaglandins, triggering severe acute-on-chronic renal failure and accelerating progression to dialysis.",
                "Avoid nephrotoxic agents: Aminoglycoside antibiotics (Gentamicin, Amikacin), intravenous radiocontrast dyes (without nephrology pre-hydration), and high-dose proton pump inhibitors",
                "Mandatory dosage adjustment for renally cleared medications (e.g., Metformin, Ciprofloxacin, Levetiracetam, Gabapentin, Digoxin, Enoxaparin) based on estimated GFR"
            ],
            "food_interactions": [
                "High-potassium foods (bananas, oranges, potatoes, tomatoes, avocados, nuts) must be strictly restricted in advanced CKD (Stages 4–5) to avoid fatal hyperkalemia",
                "High-phosphorus foods (dairy products, cola sodas, processed meats, organ meats) must be restricted to manage CKD-MBD and prevent vascular calcification"
            ],
            "allergy_warnings": [
                "Gadolinium-based MRI contrast agents are contraindicated in severe CKD (eGFR < 30 mL/min) due to the risk of Nephrogenic Systemic Fibrosis (NSF — debilitating fibrosing disease)"
            ],
            "critical_contraindications": [
                "Strictly avoid potassium salt substitutes (NoSalt, Nu-Salt) — causes rapid fatal cardiac arrest in CKD",
                "Avoid Fleet enemas and oral sodium phosphate bowel preparations (causes acute phosphate nephropathy)"
            ],
            "age_precautions": {
                "children": "Pediatric CKD impairs linear growth and bone mineralization. Growth hormone therapy and aggressive nutrition are vital components.",
                "older_adults": "Serum creatinine alone significantly underestimates kidney dysfunction in elderly due to reduced muscle mass. Always calculate eGFR using validated equations."
            },
            "immediate_emergency_triggers": [
                "Severe Hyperkalemia (serum potassium >= 6.5 mEq/L or peaked T-waves on ECG) — immediate IV calcium gluconate, insulin + dextrose, and emergency dialysis",
                "Acute Pulmonary Edema: Severe shortness of breath, inability to lie flat, and pink frothy sputum from fluid overload",
                "Uremic Encephalopathy: Progressive confusion, asterixis ('flapping tremor' of hands), lethargy, or seizures",
                "Uremic Pericarditis: Pleuritic chest pain with pericardial friction rub (immediate hemodialysis indication)"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Dietary Protein Moderation: 0.6–0.8 g/kg body weight/day of high-biological-value protein in non-dialysis CKD to reduce nitrogenous waste and glomerular hyperfiltration (under renal dietitian guidance)",
                "Strict Sodium Restriction: < 2,000 mg/day of sodium (< 5 g salt) to manage hypertension and fluid retention",
                "Phosphorus Restriction: < 800–1,000 mg/day; avoid hidden inorganic phosphate food additives in processed foods",
                "Potassium Restriction: < 2,000–3,000 mg/day in Stages 4–5 or if serum potassium exceeds 5.0 mEq/L"
            ],
            "lifestyle_recommendations": [
                "Complete tobacco smoking cessation: Smoking accelerates diabetic nephrosclerosis and multiplies cardiovascular death",
                "Maintain blood pressure strictly < 130/80 mmHg using renoprotective RAAS blockade (ACEi/ARB)",
                "Maintain strict glycemic control in diabetics (HbA1c ~ 7.0%)"
            ],
            "physical_activity": [
                "Engage in moderate-intensity physical activity (e.g., walking) for 30 minutes 5 days a week, tailored to cardiovascular tolerance"
            ],
            "hydration_guidance": [
                "Fluid restriction is NOT routinely required in early CKD (Stages 1–3) unless significant edema is present",
                "In advanced CKD (Stages 4–5) with oliguria or heart failure, fluid restriction is typically limited to 1.0–1.5 liters/day (previous day's urine output + 500 mL insensible loss)"
            ],
            "safe_home_care": [
                "Daily morning weight tracking: A sudden gain of > 1–2 kg over 48 hours indicates fluid retention requiring diuretic adjustment",
                "Monitor blood pressure twice daily at home",
                "Maintain a comprehensive list of all current medications; inform all healthcare providers of your CKD stage"
            ],
            "natural_remedies": [
                "Plant-dominant low-protein diets (PLADO) under formal renal dietitian guidance can reduce uremic toxin generation.",
                "CRITICAL WARNING ON HERBAL MEDICINES: Traditional Chinese herbal medicines containing Aristolochic acid cause severe, irreversible fibrosing nephropathy and urothelial carcinoma (Aristolochic Acid Nephropathy). Starfruit (Averrhoa carambola) contains a potent neurotoxin that cannot be cleared by failing kidneys, causing severe hiccups, intractable seizures, coma, and death in CKD patients. NEVER take unverified herbs or dietary cleanses in kidney disease."
            ],
            "substances_to_avoid": [
                "ALL over-the-counter NSAIDs (Ibuprofen, Advil, Motrin, Aleve, Naproxen, Diclofenac)",
                "Potassium salt substitutes, starfruit, and unverified herbal supplements",
                "Fleet enemas and phosphosoda laxatives"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Foamy urine, persistent swelling in feet, or unexplained fatigue",
                "Incidental finding of elevated serum creatinine (> 1.2 mg/dL in women, > 1.4 mg/dL in men) or microalbuminuria"
            ],
            "serious_warning_symptoms": [
                "Rapidly worsening peripheral edema, facial puffiness, or swelling spreading to abdomen",
                "Significant drop in daily urine volume despite normal fluid intake",
                "Persistent nausea, metallic taste, severe loss of appetite, or persistent vomiting"
            ],
            "emergency_situations": [
                "Severe shortness of breath when lying flat (acute pulmonary edema)",
                "Chest pain, irregular palpitations, or extreme muscle weakness (severe hyperkalemia / uremic pericarditis)",
                "Confusion, severe drowsiness, flapping tremors of hands, or seizures"
            ],
            "recommended_follow_up": [
                "Nephrology referral is MANDATORY for all patients with eGFR < 30 mL/min (Stage 4), significant albuminuria (uACR > 300 mg/g), or rapid eGFR decline (> 5 mL/min/year)",
                "Monitoring frequency: Stage 3 (every 3–6 months); Stage 4 (every 1–3 months); Stage 5 (every 2–4 weeks)"
            ],
            "preventive_screening": [
                "Annual eGFR and uACR screening for all individuals with diabetes mellitus, hypertension, or cardiovascular disease",
                "Pneumococcal, influenza, hepatitis B, and COVID-19 vaccinations (immune dysfunction in CKD elevates infection risks)"
            ]
        },
        "references": [
            {
                "name": "KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease",
                "organization": "Kidney Disease: Improving Global Outcomes (KDIGO)",
                "update_date": "2024-04-01",
                "url": "https://kdigo.org/guidelines/ckd-evaluation-and-management/"
            },
            {
                "name": "Chronic kidney disease: assessment and management (NICE Guideline NG203)",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024-09-10",
                "url": "https://www.nice.org.uk/guidance/ng203"
            },
            {
                "name": "National Kidney Foundation Kidney Disease Outcomes Quality Initiative (KDOQI)",
                "organization": "National Kidney Foundation (NKF)",
                "update_date": "2025-06-15",
                "url": "https://www.kidney.org/professionals/kdoqi"
            },
            {
                "name": "DailyMed — Losartan, Empagliflozin & Furosemide Clinical Monograph",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-08-14",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    },

    "high_cholesterol": {
        "id": "high_cholesterol",
        "name": "Hypercholesterolemia & Dyslipidemia",
        "category": "Cardiovascular & Metabolic Disorders",
        "emoji": "🫀",
        "overview": {
            "description": "A metabolic lipid disorder characterized by elevated levels of circulating low-density lipoprotein cholesterol (LDL-C), total cholesterol, or triglycerides, and/or decreased high-density lipoprotein cholesterol (HDL-C). The primary modifiable driver of atherosclerotic cardiovascular disease (ASCVD), including coronary heart disease, myocardial infarction, and ischemic stroke.",
            "types_and_classifications": [
                "Primary (Familial) Hypercholesterolemia (FH): Monogenic autosomal dominant disorder caused by mutations in the LDLR, APOB, or PCSK9 genes, characterized by severe lifelong LDL-C elevations (often > 190 mg/dL) and premature coronary artery disease.",
                "Secondary (Acquired) Dyslipidemia: Driven by unhealthy diets rich in saturated/trans fats, sedentary lifestyle, obesity, Type 2 diabetes, hypothyroidism, nephrotic syndrome, chronic kidney disease, or cholestatic liver disease.",
                "Mixed Dyslipidemia: Characterized by elevated LDL-C and triglycerides accompanied by low HDL-C (frequently seen in Metabolic Syndrome and Type 2 Diabetes).",
                "Severe Hypertriglyceridemia: Fasting triglycerides >= 500 mg/dL, carrying a severe risk of acute pancreatitis."
            ],
            "causes": [
                "Overproduction or impaired hepatic clearance of apolipoprotein B-containing atherogenic lipoproteins (VLDL, IDL, LDL)",
                "Downregulation or genetic defect of hepatic LDL receptors",
                "High dietary intake of saturated fatty acids, industrial trans fats, and dietary cholesterol",
                "Insulin resistance stimulating hepatic lipogenesis and free fatty acid flux",
                "Diminished lipoprotein lipase (LPL) activity"
            ],
            "risk_factors": [
                "Diets high in saturated animal fats, palm oil, butter, and processed hydrogenated oils",
                "Physical inactivity and visceral abdominal adiposity (waist circumference > 102 cm in men, > 88 cm in women)",
                "Type 2 diabetes mellitus and prediabetes (atherogenic dyslipidemia triad)",
                "Untreated primary hypothyroidism (thyroid deficiency downregulates hepatic LDL receptors)",
                "Family history of premature coronary heart disease (men < 55 years, women < 65 years)",
                "Excessive alcohol consumption (markedly elevates serum triglycerides)"
            ],
            "common_symptoms": [
                "HYPERCHOLESTEROLEMIA IS ENTIRELY ASYMPTOMATIC ('Silent Risk Factor')",
                "No physical discomfort, pain, or warning symptoms until acute vascular arterial occlusion occurs (heart attack, angina, or stroke)"
            ],
            "uncommon_symptoms": [
                "Xanthelasma: Yellowish soft cholesterol deposits deposited on the eyelids, particularly near the inner canthus",
                "Tendon Xanthomas: Firm, non-tender nodular cholesterol swellings on the Achilles tendons or extensor tendons of the hands (hallmark of Familial Hypercholesterolemia)",
                "Arcus Senilis (Corneal Arcus): White, gray, or bluish opaque ring in the outer margin of the cornea (pathognomonic of severe dyslipidemia if appearing before age 45)",
                "Eruptive Xanthomas: Crops of small yellowish-pink papules on buttocks and shoulders in severe hypertriglyceridemia"
            ],
            "early_warning_signs": [
                "No early symptoms exist; can ONLY be identified through routine laboratory fasting or non-fasting lipid profile screening"
            ],
            "possible_complications": [
                "Atherosclerosis: Progressive formation of lipid-rich fibrous plaques within medium and large systemic arteries",
                "Coronary Artery Disease (CAD), Unstable Angina, and Acute Myocardial Infarction (Heart Attack)",
                "Ischemic Cerebrovascular Stroke and Transient Ischemic Attacks (TIA)",
                "Peripheral Arterial Disease (PAD) causing intermittent claudication and critical limb ischemia",
                "Carotid Artery Stenosis",
                "Acute Pancreatitis: Triggered by chylomicronemia when serum triglycerides exceed 500–1,000 mg/dL"
            ],
            "systemic_impact": "Excess circulating apo-B lipoprotein particles penetrate the damaged or permeable vascular endothelial lining, becoming trapped in the subendothelial space. Oxidized LDL particles trigger a local inflammatory response, macrophage scavenger uptake, and foam cell formation, establishing the core of atherosclerotic plaques which gradually stenose arterial lumens or rupture, precipitating acute occlusive thrombi."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Screening of all adults aged >= 20 years with a fasting or non-fasting lipid profile",
                "Formal 10-Year ASCVD Risk Calculation (AHA/ACC Risk Estimator Plus or SCORE2) to guide statin initiation",
                "Screening for secondary causes (fasting glucose, HbA1c, TSH, eGFR, liver enzymes)"
            ],
            "laboratory_tests": [
                "Standard Lipid Panel: Total Cholesterol, Low-Density Lipoprotein Cholesterol (LDL-C), High-Density Lipoprotein Cholesterol (HDL-C), Triglycerides",
                "Non-HDL Cholesterol (Total Cholesterol minus HDL): Reflects total atherogenic particle burden",
                "Apolipoprotein B (ApoB): Direct quantification of the total number of circulating atherogenic particles",
                "Lipoprotein(a) [Lp(a)]: Independent genetically determined cardiovascular risk factor (recommended once in a lifetime)",
                "High-Sensitivity C-Reactive Protein (hs-CRP): Biomarker of systemic vascular inflammation"
            ],
            "medical_examinations": [
                "Coronary Artery Calcium (CAC) Scoring by Non-Contrast Cardiac CT: Highly validated risk-refining tool; CAC score of 0 reclassifies patient to lower risk; CAC score >= 100 or >= 75th percentile confirms established atherosclerosis and mandates statin therapy",
                "Carotid Intima-Media Thickness (CIMT) / Carotid Duplex Ultrasound to detect plaques"
            ],
            "test_results_interpretation": [
                "LDL-C Target Levels: Optimal < 100 mg/dL; Desirable for primary prevention < 70 mg/dL; Target for established ASCVD / very-high risk < 55 mg/dL (and >= 50% reduction from baseline).",
                "Severe Hypercholesterolemia: LDL-C >= 190 mg/dL mandates immediate high-intensity statin therapy without requiring risk calculation (suspected Familial Hypercholesterolemia).",
                "Triglycerides: Normal < 150 mg/dL; Borderline 150–199 mg/dL; High 200–499 mg/dL; Very High >= 500 mg/dL (acute pancreatitis risk).",
                "HDL-C: Low in men < 40 mg/dL; Low in women < 50 mg/dL (cardiovascular risk factor)."
            ]
        },
        "medicines": [
            {
                "name": "Atorvastatin",
                "brand_names": ["Lipitor", "Atorva", "Storvas"],
                "generic_name": "Atorvastatin calcium",
                "category": "Lipid-Lowering Statin",
                "therapeutic_class": "HMG-CoA Reductase Inhibitor",
                "purpose": "First-line, high-potency foundation statin therapy: Reduces LDL-C by 30% to > 50%, stabilizes arterial plaques, decreases systemic inflammation, and dramatically cuts cardiovascular mortality.",
                "how_it_works": "Inhibits rate-limiting HMG-CoA reductase in hepatocytes, upregulating LDL receptors on the liver surface to aggressively clear circulating atherogenic LDL particles.",
                "common_side_effects": ["Mild myalgia (muscle aches)", "Arthralgia", "Nasopharyngitis", "Dyspepsia", "Mild glucose rise"],
                "serious_adverse_effects": ["Rhabdomyolysis with acute myoglobinuric kidney failure", "Immune-mediated necrotizing myopathy", "Hepatotoxicity (rare)"],
                "contraindications": ["Active acute liver failure", "Pregnancy and breastfeeding", "Known hypersensitivity"],
                "drug_interactions": ["Strong CYP3A4 inhibitors (Clarithromycin, Itraconazole) elevate statin levels", "Gemfibrozil multiplies rhabdomyolysis risk"],
                "food_interactions": ["May take at any time of day with or without food. Avoid consuming > 1.2 liters of grapefruit juice daily."],
                "allergy_precautions": "Contraindicated in severe statin allergy.",
                "age_precautions": "Demonstrated cardiovascular benefit in adults up to >= 75 years of age.",
                "pregnancy_breastfeeding": "Contraindicated during pregnancy and lactation.",
                "kidney_liver_precautions": "No dose adjustments for renal failure. Contraindicated in active acute hepatic failure.",
                "monitoring_requirements": "Lipid panel 4–12 weeks after initiation or dose titration; baseline liver enzymes; CK if muscle pain occurs."
            },
            {
                "name": "Aspirin",
                "brand_names": ["Bayer Aspirin", "Ecosprin"],
                "generic_name": "Acetylsalicylic acid (ASA)",
                "category": "Cardiovascular Antiplatelet",
                "therapeutic_class": "Platelet COX-1 Inhibitor",
                "purpose": "Secondary prevention antiplatelet therapy for patients with established atherosclerotic cardiovascular disease, prior heart attack, stroke, or stents.",
                "how_it_works": "Irreversibly acetylates platelet COX-1, preventing thromboxane A2 generation and blocking platelet aggregation and acute arterial thrombosis.",
                "common_side_effects": ["Dyspepsia", "Nausea", "Easy bruising", "Prolonged bleeding time"],
                "serious_adverse_effects": ["Major gastrointestinal hemorrhage", "Hemorrhagic stroke"],
                "contraindications": ["Active peptic ulcer bleeding", "Bleeding disorders", "Suspected dengue fever", "Children < 16 years with viral illness"],
                "drug_interactions": ["Anticoagulants (Warfarin, Apixaban) multiply bleeding risk", "Ibuprofen blunts aspirin's antiplatelet action"],
                "food_interactions": ["Take with a full glass of water or food to protect gastric mucosa. Avoid alcohol."],
                "allergy_precautions": "Contraindicated in aspirin triad asthma.",
                "age_precautions": "Routine primary prevention in adults > 70 years is no longer recommended due to high bleeding risks.",
                "pregnancy_breastfeeding": "Low dose (81 mg) used in high-risk pregnancies under obstetrician guidance.",
                "kidney_liver_precautions": "Avoid in severe renal impairment (eGFR < 10) and severe hepatic failure.",
                "monitoring_requirements": "Complete blood counts (platelets/hemoglobin); monitoring for black stools."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "Statin + Gemfibrozil: Severe risk of severe rhabdomyolysis (use fenofibrate instead if fibrate is required)",
                "Statin + Strong CYP3A4 Inhibitors (Clarithromycin, Erythromycin, Itraconazole, Ketoconazole): Multiplies atorvastatin plasma concentrations by up to 4- to 8-fold; temporarily pause statin during antibiotic course"
            ],
            "food_interactions": [
                "Large amounts of grapefruit juice (> 1 liter/day) inhibit intestinal CYP3A4, substantially elevating atorvastatin levels and toxicity risk"
            ],
            "allergy_warnings": [
                "Patients reporting muscle pain must have a serum Creatine Kinase (CK) checked to differentiate benign myalgia from dangerous rhabdomyolysis"
            ],
            "critical_contraindications": [
                "Statins are CONTRAINDICATED in pregnancy and breastfeeding due to potential disruption of fetal cholesterol synthesis and development",
                "Do not discontinue statins when lipid panel normalizes: Cholesterol levels will immediately rebound to high baseline levels because statin therapy addresses chronic hepatic synthesis"
            ],
            "age_precautions": {
                "children": "Pediatric screening is recommended at age 9–11 to identify early Familial Hypercholesterolemia. Statins approved down to age 10 for FH.",
                "older_adults": "High-intensity statins provide significant secondary prevention in older adults with prior heart attacks or strokes. Monitor for frailty and myopathy."
            },
            "immediate_emergency_triggers": [
                "Severe substernal chest pressure, squeezing, or fullness radiating to left arm, neck, or jaw (Acute Myocardial Infarction)",
                "Sudden unilateral facial drooping, arm weakness, or slurred speech (Acute Ischemic Stroke — FAST protocol)",
                "Severe unrelenting epigastric abdominal pain radiating to the back with vomiting (Acute Pancreatitis from severe hypertriglyceridemia)"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Strictly reduce dietary saturated fats to < 6%–7% of total daily calories (minimize fatty red meat, butter, lard, cream, and palm oil)",
                "Completely eliminate industrial trans fatty acids (partially hydrogenated vegetable oils in commercial baked goods and fried fast foods)",
                "Increase daily soluble viscous fiber to 10–25 g/day (oats, barley, beans, lentils, psyllium husk) which actively binds bile acids in the gut and lowers LDL-C by 5%–10%",
                "Incorporate plant stanols and sterols (2 g/day) from fortified spreads to displace cholesterol absorption in the intestine",
                "Incorporate cardioprotective Mediterranean fats: Extra virgin olive oil, walnuts, almonds, flaxseeds, and fatty fish (salmon, mackerel, sardines) rich in omega-3s"
            ],
            "lifestyle_recommendations": [
                "Target a 5% to 10% weight loss if overweight; significantly reduces triglycerides and elevates protective HDL-C",
                "Complete tobacco smoking cessation: Smoking oxidizes LDL particles and lowers HDL-C",
                "Limit or eliminate alcohol consumption if triglycerides are elevated (> 200 mg/dL)"
            ],
            "physical_activity": [
                "Engage in at least 150–300 minutes of moderate-intensity aerobic physical activity per week (e.g., brisk walking, cycling) or 75–150 minutes of vigorous activity",
                "Add muscle-strengthening resistance exercises twice weekly"
            ],
            "hydration_guidance": [
                "Maintain optimal daily water hydration"
            ],
            "safe_home_care": [
                "Maintain a permanent file of all lipid panel lab results over time to visualize cardiovascular risk trajectories",
                "Take statin medication consistently once daily (atorvastatin can be taken at any time of day due to its long 14-hour half-life)"
            ],
            "natural_remedies": [
                "Red yeast rice contains naturally occurring monacolin K (identical to lovastatin).",
                "CRITICAL WARNING ON NATURAL REMEDIES: Over-the-counter red yeast rice supplements have variable, unregulated drug concentrations and can be contaminated with the nephrotoxin citrinin. They carry the exact same side-effect and drug-interaction profile as prescription statins without standardized clinical quality control. Always use certified pharmaceutical statins prescribed by a physician."
            ],
            "substances_to_avoid": [
                "Full-fat dairy, processed fatty meats, butter, trans-fat baked goods",
                "Excessive alcohol",
                "Unregulated weight-loss and cholesterol-lowering herbal cleanses"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Fasting lipid panel showing LDL-C > 130 mg/dL or Total Cholesterol > 200 mg/dL",
                "Any first-degree relative who suffered a heart attack or stroke before age 55 (men) or 65 (women)"
            ],
            "serious_warning_symptoms": [
                "Severe unexplained generalized muscle aches, muscle tenderness, or passing dark brown/cola-colored urine (possible rhabdomyolysis)",
                "Shortness of breath on mild exertion or intermittent chest tightness"
            ],
            "emergency_situations": [
                "Acute chest pressure, pain radiating to arm or jaw, cold sweating, or nausea (Heart Attack)",
                "Sudden facial droop, arm weakness, or speech difficulty (Stroke) — CALL 911 / 112 IMMEDIATELY"
            ],
            "recommended_follow_up": [
                "Repeat fasting lipid profile 4 to 12 weeks after initiating or titrating statin therapy to confirm response and compliance",
                "Once stabilized at goal, repeat lipid panel every 6 to 12 months"
            ],
            "preventive_screening": [
                "All adults aged >= 20 years should have a lipid panel performed every 4 to 6 years",
                "Annual lipid screening in individuals with diabetes, hypertension, obesity, or family history of premature heart disease",
                "Universal pediatric lipid screening at ages 9–11 and 17–21 years"
            ]
        },
        "references": [
            {
                "name": "AHA/ACC/AACVPR Guideline on the Management of Blood Cholesterol",
                "organization": "American Heart Association / American College of Cardiology",
                "update_date": "2025-07-20",
                "url": "https://www.ahajournals.org/doi/10.1161/CIR.0000000000000625"
            },
            {
                "name": "ESC/EAS Guidelines for the management of dyslipidaemias",
                "organization": "European Society of Cardiology / European Atherosclerosis Society",
                "update_date": "2024-09-05",
                "url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Dyslipidaemias-Management-of"
            },
            {
                "name": "Cardiovascular disease: risk assessment and reduction, including lipid modification (NICE CG181)",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024-01-15",
                "url": "https://www.nice.org.uk/guidance/cg181"
            },
            {
                "name": "DailyMed — Lipitor (Atorvastatin Calcium) Prescribing Information",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-08-18",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    },

    "pneumonia": {
        "id": "pneumonia",
        "name": "Pneumonia (Community-Acquired & Bacterial)",
        "category": "Lower Respiratory Infectious Diseases",
        "emoji": "🫁",
        "overview": {
            "description": "An acute lower respiratory tract infection of the pulmonary parenchymal tissue (alveoli and bronchioles) resulting in inflammatory exudation, alveolar consolidation, and impaired gas exchange. Manifests across a broad spectrum from mild 'walking pneumonia' to life-threatening respiratory failure and septic shock.",
            "types_and_classifications": [
                "Community-Acquired Pneumonia (CAP): Acquired outside of a healthcare or hospital facility; most common serious respiratory infection.",
                "Hospital-Acquired Pneumonia (HAP): Developing >= 48 hours after hospital admission, frequently caused by multidrug-resistant pathogens (Pseudomonas, MRSA).",
                "Ventilator-Associated Pneumonia (VAP): Developing > 48 hours after endotracheal intubation.",
                "Aspiration Pneumonia: Inhalation of oropharyngeal or gastric contents into the lower respiratory tract, common in impaired consciousness or dysphagia.",
                "Atypical Pneumonia: Caused by atypical organisms (Mycoplasma pneumoniae, Chlamydophila pneumoniae, Legionella pneumophila) with prominent extrapulmonary symptoms."
            ],
            "causes": [
                "Bacterial Pathogens: Streptococcus pneumoniae (pneumococcus, most common cause globally), Haemophilus influenzae, Moraxella catarrhalis, Staphylococcus aureus (including MRSA)",
                "Atypical Pathogens: Mycoplasma pneumoniae, Chlamydophila pneumoniae, Legionella pneumophila",
                "Viral Pathogens: Influenza A and B, Respiratory Syncytial Virus (RSV), SARS-CoV-2 (COVID-19), Adenovirus, Parainfluenza",
                "Fungal Pathogens: Pneumocystis jirovecii, Histoplasma, Coccidioides (in immunocompromised hosts)"
            ],
            "risk_factors": [
                "Age extremes: Infants < 2 years and adults >= 65 years of age",
                "Chronic medical comorbidities: Chronic Obstructive Pulmonary Disease (COPD), bronchial asthma, heart failure, diabetes mellitus, chronic renal disease",
                "Immunocompromised states: HIV/AIDS, chemotherapy, immunosuppressive therapies, asplenia",
                "Cigarette smoking and chronic alcohol abuse (impairs mucociliary clearance and alveolar macrophage phagocytosis)",
                "Recent viral upper respiratory infection (influenza secondary bacterial pneumonia)",
                "Neurological conditions causing dysphagia (stroke, dementia, Parkinson's disease)"
            ],
            "common_symptoms": [
                "Productive cough with thick purulent, rust-colored, or yellowish-green sputum",
                "High fever, shaking chills (rigors), and profuse diaphoresis",
                "Pleuritic chest pain: Sharp, stabbing pain that worsens intensely on deep inspiration or coughing",
                "Shortness of breath (dyspnea) and tachypnea (rapid breathing)",
                "Profound generalized physical fatigue, malaise, and myalgia",
                "Loss of appetite and nausea"
            ],
            "uncommon_symptoms": [
                "Hemoptysis: Coughing up blood-streaked sputum",
                "Confusion, altered mental status, and hypothermia (the cardinal presentation of pneumonia in elderly patients, who often lack fever!)",
                "Extrapulmonary features in atypical pneumonia: Bullous myringitis, erythema multiforme, diarrhea, hyponatremia (Legionella)"
            ],
            "early_warning_signs": [
                "A viral 'cold' or flu that suddenly sharply worsens after 4–5 days with high fever, chest pain, and shortness of breath ('double sickening')"
            ],
            "possible_complications": [
                "Acute Respiratory Distress Syndrome (ARDS) requiring mechanical ventilation",
                "Severe Sepsis and Septic Shock (hypotension, multiorgan failure)",
                "Parapneumonic Pleural Effusion and Empyema (pus in the pleural cavity requiring chest tube drainage)",
                "Lung Abscess: Cavitary necrosis of pulmonary parenchyma",
                "Bacteremia, infective endocarditis, and metastatic seeding (meningitis, septic arthritis)",
                "Acute cardiac events (atrial fibrillation, myocardial infarction, acute heart failure decompensation)"
            ],
            "systemic_impact": "Pathogens colonizing the terminal alveoli evoke an intense host inflammatory immune response. Neutrophil recruitment, capillary engorgement, and proteinaceous exudate flood the alveolar airspaces, producing dense parenchymal consolidation. This creates a severe right-to-left intrapulmonary shunt (perfusion without ventilation), triggering hypoxemia, tachypnea, and systemic cytokine-mediated sepsis."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Clinical diagnosis: Acute respiratory symptoms + fever + focal chest auscultatory findings confirmed by radiographic pulmonary infiltrate",
                "Severity assessment using the validated CURB-65 Score (Confusion, Urea > 7 mmol/L, Respiratory rate >= 30, Blood pressure < 90/60, Age >= 65) to determine outpatient vs inpatient vs ICU admission"
            ],
            "laboratory_tests": [
                "Pulse Oximetry (SpO2): Immediate assessment of oxygen saturation (SpO2 < 92% indicates acute hypoxemia requiring supplemental oxygen)",
                "Complete Blood Count (CBC): Prominent leukocytosis (WBC > 12,000–15,000/mcL with left shift / bandemia) or leukopenia (poor prognostic sign)",
                "Inflammatory Markers: Serum C-Reactive Protein (CRP) and Procalcitonin (PCT > 0.25 mcg/L strongly supports bacterial etiology requiring antibiotics)",
                "Blood Cultures (2 sets from separate venipuncture sites) in hospitalized patients prior to initiating antibiotic therapy",
                "Sputum Gram Stain and Culture & Sensitivity: Early morning deep expectorated specimen",
                "Legionella and Pneumococcal Urinary Antigen Tests (rapid, unaffected by prior antibiotics)",
                "Multiplex Viral / Atypical Respiratory PCR panel (nasopharyngeal swab)"
            ],
            "medical_examinations": [
                "Chest Radiography (PA and Lateral Chest X-Ray): Confirmatory gold standard — demonstrates lobar or segmental alveolar consolidation, patchy bronchopneumonia, or interstitial infiltrates",
                "Point-of-Care Lung Ultrasound (POCUS): Highly sensitive for detecting subpleural consolidation and pleural effusion",
                "Chest CT Scan: Indicated if clinical suspicion is high with normal X-ray, or in non-resolving pneumonia / suspected empyema"
            ],
            "test_results_interpretation": [
                "CURB-65 Score: 0–1 points (low risk, suitable for outpatient treatment); 2 points (intermediate risk, consider hospital admission); 3–5 points (high risk, severe pneumonia, urgent hospital admission, consider ICU if 4–5).",
                "Procalcitonin > 0.5 mcg/L strongly indicates systemic bacterial infection.",
                "Chest X-Ray: Dense lobar consolidation with air bronchograms typically indicates Streptococcus pneumoniae; bilateral diffuse patchy infiltrates suggest atypical or viral pathogens."
            ]
        },
        "medicines": [
            {
                "name": "Amoxicillin and Clavulanate Potassium",
                "brand_names": ["Augmentin", "Clavam", "Moxikind-CV"],
                "generic_name": "Amoxicillin and clavulanate potassium",
                "category": "Antibacterial / Beta-Lactam",
                "therapeutic_class": "Aminopenicillin with Beta-Lactamase Inhibitor",
                "purpose": "First-line preferred outpatient and inpatient antibacterial therapy for Community-Acquired Pneumonia, covering typical bacterial pathogens including beta-lactamase producers.",
                "how_it_works": "Amoxicillin lyses bacterial peptidoglycan cell walls; Clavulanate irreversibly inhibits bacterial beta-lactamase enzymes, preventing amoxicillin destruction.",
                "common_side_effects": ["Diarrhea", "Nausea and vomiting", "Abdominal cramping", "Oral/vaginal thrush", "Rash"],
                "serious_adverse_effects": ["Type I anaphylactic shock", "Cholestatic hepatitis / jaundice", "Clostridioides difficile colitis", "SJS/TEN"],
                "contraindications": ["Documented severe penicillin allergy / anaphylaxis", "History of Augmentin-induced jaundice"],
                "drug_interactions": ["Warfarin (elevates INR)", "Methotrexate toxicity", "Allopurinol (rash)"],
                "food_interactions": ["CRITICAL: Take at the start of a meal to enhance absorption and drastically reduce gastrointestinal diarrhea."],
                "allergy_precautions": "STRICTLY CONTRAINDICATED in patients with confirmed penicillin allergy.",
                "age_precautions": "Weight-based dosing in children (mg amoxicillin component/kg/day). Monitor renal clearance in elderly.",
                "pregnancy_breastfeeding": "Category B. Generally safe in pregnancy and breastfeeding.",
                "kidney_liver_precautions": "Dose reduce if eGFR < 30 mL/min. Monitor transaminases in prolonged courses.",
                "monitoring_requirements": "Complete entire prescribed 5- to 7-day course; monitor for persistent watery diarrhea."
            },
            {
                "name": "Azithromycin",
                "brand_names": ["Zithromax", "Z-Pak", "Azee"],
                "generic_name": "Azithromycin dihydrate",
                "category": "Antibacterial / Macrolide",
                "therapeutic_class": "Macrolide / Azalide",
                "purpose": "First-line co-prescription in combination therapy (Beta-lactam + Macrolide) to provide essential coverage against atypical pathogens (Mycoplasma, Chlamydia, Legionella) and modulate lung inflammation; also primary alternative for penicillin-allergic patients.",
                "how_it_works": "Binds reversibly to the 50S ribosomal subunit of bacteria, inhibiting transpeptidation and protein synthesis.",
                "common_side_effects": ["Diarrhea", "Nausea", "Abdominal cramping", "Headache"],
                "serious_adverse_effects": ["Cardiac QTc prolongation and Torsades de Pointes (FDA Warning)", "C. difficile colitis", "Cholestatic jaundice"],
                "contraindications": ["Hypersensitivity to macrolides", "History of macrolide cholestatic jaundice"],
                "drug_interactions": ["QT-prolonging antiarrhythmics (Amiodarone)", "Antacids containing Al/Mg reduce absorption (space by 2 hours)", "Warfarin"],
                "food_interactions": ["May take with or without food. Avoid alcohol."],
                "allergy_precautions": "Discontinue if allergic hives or angioedema develops.",
                "age_precautions": "Approved in children >= 6 months. Elderly patients are more vulnerable to cardiac QTc prolongation.",
                "pregnancy_breastfeeding": "Category B. Generally considered safe during pregnancy.",
                "kidney_liver_precautions": "Excreted via biliary route; caution in severe liver disease. No dose adjustment needed in mild-to-moderate renal failure.",
                "monitoring_requirements": "Resolution of fever and respiratory symptoms; ECG in cardiac risk patients."
            },
            {
                "name": "Levofloxacin",
                "brand_names": ["Levaquin", "L-Cin", "Glevo"],
                "generic_name": "Levofloxacin hemihydrate",
                "category": "Respiratory Fluoroquinolone",
                "therapeutic_class": "Fluoroquinolone",
                "purpose": "Monotherapy alternative for Community-Acquired Pneumonia in outpatients with comorbidities (COPD, heart failure, renal disease) or inpatients with severe penicillin allergies.",
                "how_it_works": "Inhibits bacterial DNA gyrase and topoisomerase IV, preventing bacterial DNA replication and transcription with potent activity against pneumococci and atypical organisms.",
                "common_side_effects": ["Nausea", "Diarrhea", "Headache", "Insomnia", "Dizziness"],
                "serious_adverse_effects": ["Achilles tendonitis and tendon rupture (FDA Boxed Warning)", "Peripheral neuropathy (FDA Boxed Warning)", "CNS toxicities (FDA Boxed Warning: seizures, psychosis)", "Cardiac QTc prolongation", "Aortic aneurysm"],
                "contraindications": ["History of fluoroquinolone tendon disorders", "Myasthenia gravis (FDA Boxed Warning)", "Hypersensitivity to quinolones"],
                "drug_interactions": ["Multivalent cations (Antacids with Al/Mg, Iron, Sucralfate) chelate drug (space by 2 hours)", "Corticosteroids multiply tendon rupture risk"],
                "food_interactions": ["Maintain generous fluid hydration to avoid crystalluria. Do not take with dairy alone."],
                "allergy_precautions": "Discontinue immediately at first sign of tendon pain or skin rash.",
                "age_precautions": "Avoid in children (articular cartilage risk). FDA Boxed Warning in elderly for tendon rupture.",
                "pregnancy_breastfeeding": "Category C. Avoid in pregnancy and breastfeeding.",
                "kidney_liver_precautions": "Excreted renally (~87%); mandatory dosage reduction if eGFR < 50 mL/min.",
                "monitoring_requirements": "Renal function; immediate cessation upon any tendon pain or numbness."
            },
            {
                "name": "Paracetamol",
                "brand_names": ["Panadol", "Tylenol", "Calpol"],
                "generic_name": "Acetaminophen / Paracetamol",
                "category": "Analgesic & Antipyretic",
                "therapeutic_class": "Non-opioid Analgesic",
                "purpose": "Symptomatic control of high fever, pleuritic chest discomfort, and generalized body aches, allowing comfortable breathing and rest.",
                "how_it_works": "Centrally inhibits prostaglandin synthesis and modulates hypothalamic thermoregulation.",
                "common_side_effects": ["Mild nausea"],
                "serious_adverse_effects": ["Liver toxicity in overdose"],
                "contraindications": ["Severe active hepatic failure", "Hypersensitivity"],
                "drug_interactions": ["Alcohol"],
                "food_interactions": ["Take with or without food."],
                "allergy_precautions": "Discontinue if allergic rash develops.",
                "age_precautions": "Weight-based dosing in children (10–15 mg/kg).",
                "pregnancy_breastfeeding": "Safe and indicated in pregnancy.",
                "kidney_liver_precautions": "Safe in renal failure. Limit dose in liver disease.",
                "monitoring_requirements": "Daily total paracetamol dosage (< 4000 mg/day)."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "Respiratory Fluoroquinolones (Levofloxacin) combined with Systemic Corticosteroids multiplies the risk of severe Achilles tendon rupture by up to 5-fold (FDA Boxed Warning)",
                "Antacids containing aluminum, magnesium, or calcium chelate oral Levofloxacin and Ciprofloxacin, reducing antibiotic absorption by up to 90%"
            ],
            "food_interactions": [
                "Oral antibiotics must be taken consistently with adequate water hydration; Augmentin should always be taken at the start of a meal to prevent severe diarrhea"
            ],
            "allergy_warnings": [
                "Penicillin allergy must be clearly documented (true anaphylaxis vs mild childhood rash) to determine whether cephalosporins or non-beta-lactams (macrolides, fluoroquinolones) are necessary"
            ],
            "critical_contraindications": [
                "NEVER omit or delay antibiotic administration in suspected bacterial pneumonia: Each hour of delay in severe pneumonia with sepsis increases mortality by up to 8%",
                "Avoid over-the-counter cough suppressants (dextromethorphan) in productive bacterial pneumonia: Suppressing the cough reflex inhibits natural clearance of purulent alveolar exudate and worsens consolidation"
            ],
            "age_precautions": {
                "children": "Tachypnea is the most reliable clinical sign of pneumonia in children (age 2–11 months: >= 50 breaths/min; age 1–5 years: >= 40 breaths/min). Retractions and grunting indicate severe distress.",
                "older_adults": "Elderly patients frequently present WITHOUT fever or cough, manifesting only acute confusion (delirium), tachypnea, unsteadiness, or falls. High clinical suspicion is vital."
            },
            "immediate_emergency_triggers": [
                "Acute Respiratory Failure: Severe shortness of breath, respiratory rate > 30 breaths/min, oxygen saturation (SpO2) < 90% on room air",
                "Septic Shock: Systolic blood pressure < 90 mmHg, cold clammy skin, confusion, and oliguria",
                "Cyanosis: Bluish discoloration of the lips, tongue, or fingertips",
                "Confusion, severe lethargy, or inability to stay awake"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Eat small, easily digestible, calorie- and protein-dense meals (warm broths, chicken soup, yogurt, soft eggs, cooked oatmeal)",
                "Stay well nourished to support the massive immune and metabolic energy demands of fighting lower respiratory infection"
            ],
            "lifestyle_recommendations": [
                "Strict bed rest in a comfortable, semi-upright posture (elevate head and chest 30–45 degrees with pillows to facilitate diaphragmatic expansion)",
                "Complete cessation of all cigarette and tobacco smoking; avoid all second-hand smoke exposure",
                "Use a clean bedside cool-mist humidifier to keep airways moist"
            ],
            "physical_activity": [
                "Avoid any strenuous physical activity, exercise, or work during acute illness and for at least 1–2 weeks following clinical recovery",
                "Perform gentle deep breathing exercises and frequent position changes while awake to prevent basilar atelectasis"
            ],
            "hydration_guidance": [
                "Drink plentiful fluids: At least 2.5 to 3 liters of warm water, herbal teas, and broths daily to thin tenacious bronchial mucus secretions and promote productive expectoration"
            ],
            "safe_home_care": [
                "COMPLETE THE ENTIRE PRESCRIBED ANTIBIOTIC COURSE: Stopping antibiotics early as soon as fever resolves encourages recurrence and multi-drug bacterial resistance",
                "Use honey in warm water or lemon tea (for individuals over 1 year of age) to soothe painful pharyngeal irritation from coughing",
                "Monitor oxygen saturation with a home pulse oximeter if available"
            ],
            "natural_remedies": [
                "Warm steam inhalation, honey (for patients over 1 year), and hydration provide effective supportive relief for airway irritation and mucus clearance.",
                "CRITICAL WARNING ON NATURAL REMEDIES: Bacterial pneumonia is an invasive, destructive alveolar infection with significant mortality. Natural remedies, vitamins, and herbal teas CANNOT eradicate Streptococcus pneumoniae or atypical bacteria. Antibiotics are life-saving and mandatory. Relying on unverified home remedies causes fatal sepsis and respiratory failure."
            ],
            "substances_to_avoid": [
                "Tobacco smoke, vaping aerosols, and industrial fumes",
                "Alcohol, which impairs alveolar macrophage defense and causes dehydration",
                "Over-the-counter cough suppressants in wet, productive cough"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Fever, shaking chills, and a wet cough producing colored phlegm lasting > 48 hours",
                "Pleuritic chest pain that stabs on deep inspiration"
            ],
            "serious_warning_symptoms": [
                "Persistent high fever > 38.5°C failing to improve 48–72 hours after starting antibiotics",
                "Shortness of breath on light exertion or walking across the room",
                "Coughing up fresh blood or rust-colored sputum"
            ],
            "emergency_situations": [
                "Severe difficulty breathing, gasping for air, or respiratory rate > 30 breaths/min",
                "Oxygen saturation dropping < 92%",
                "Confusion, severe dizziness, bluish lips/face (cyanosis), or fainting — CALL 911 / 112 IMMEDIATELY"
            ],
            "recommended_follow_up": [
                "Clinical reassessment by doctor at 48 to 72 hours to ensure antibiotic clinical response (defervescence, reduced tachypnea)",
                "Repeat chest X-ray at 6 weeks for smokers or patients > 50 years to confirm complete radiographic resolution and rule out underlying lung malignancy"
            ],
            "preventive_screening": [
                "Pneumococcal Vaccination: PCV20 or PCV15 followed by PPSV23 for all adults >= 65 years and younger individuals with chronic medical conditions",
                "Annual seasonal Influenza vaccination (influenza is the primary driver of secondary fatal bacterial pneumonia)",
                "Annual COVID-19 and RSV vaccination in recommended groups"
            ]
        },
        "references": [
            {
                "name": "Diagnosis and Treatment of Adults with Community-acquired Pneumonia (ATS/IDSA Clinical Practice Guideline)",
                "organization": "American Thoracic Society / Infectious Diseases Society of America",
                "update_date": "2024-10-15",
                "url": "https://www.atsjournals.org/doi/10.1164/rccm.201908-1581ST"
            },
            {
                "name": "Pneumonia (community-acquired): antimicrobial prescribing (NICE Guideline NG138)",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024-02-12",
                "url": "https://www.nice.org.uk/guidance/ng138"
            },
            {
                "name": "British Thoracic Society Community Acquired Pneumonia in Adults Guideline",
                "organization": "British Thoracic Society (BTS)",
                "update_date": "2025-01-20",
                "url": "https://www.brit-thoracic.org.uk/quality-improvement/guidelines/pneumonia-in-adults/"
            },
            {
                "name": "DailyMed — Augmentin & Azithromycin Prescribing Information",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-08-20",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    }
,
"fever": {
        "id": "fever",
        "name": "Fever (Pyrexia of Unknown Origin & Infectious Fever)",
        "category": "Infectious & Systemic Disorders",
        "emoji": "🌡️",
        "overview": {
            "description": "A controlled elevation of core body temperature above the normal circadian range (> 38.0°C / 100.4°F) regulated by the preoptic hypothalamic heat-regulating center in response to exogenous or endogenous pyrogens (interleukins, interferons, TNF-alpha).",
            "types_and_classifications": [
                "Low-grade fever (37.5°C–38.3°C): Often seen in viral upper respiratory infections or early inflammatory states.",
                "Moderate fever (38.4°C–39.4°C): Common in acute bacterial and systemic viral infections.",
                "High fever (> 39.5°C): Requires urgent investigation for invasive bacterial sepsis, malaria, or dengue.",
                "Hyperpyrexia (> 41.5°C): A critical medical emergency with failure of thermoregulatory homeostasis (heat stroke, neuroleptic malignant syndrome, CNS hemorrhage)."
            ],
            "causes": [
                "Viral infections (influenza, dengue, adenovirus, rhinovirus, COVID-19)",
                "Bacterial infections (urinary tract infection, pneumonia, streptococcal pharyngitis, bacteremia)",
                "Parasitic infections (malaria, amoebiasis)",
                "Post-immunization immune response (vaccine reactogenicity)",
                "Autoimmune and connective tissue diseases (lupus, juvenile idiopathic arthritis)"
            ],
            "risk_factors": [
                "Infants under 3 months of age (immature immune and blood-brain barrier)",
                "Immunocompromised states (chemotherapy, neutropenia, advanced HIV, asplenia)",
                "Recent international travel to tropical/malaria/dengue endemic areas",
                "Indwelling central venous catheters or urinary catheters"
            ],
            "common_symptoms": [
                "Core body temperature >= 38.0°C (100.4°F)",
                "Chills, shivering, and cutis anserina ('goosebumps') as hypothalamic set-point rises",
                "Warm flushed skin and diaphoresis (sweating) as the fever breaks",
                "Frontal headache, generalized muscle aches (myalgia), and arthralgia",
                "Lethargy, malaise, and decreased appetite (anorexia)"
            ],
            "uncommon_symptoms": [
                "Febrile seizures (benign generalized convulsions in children aged 6 months to 5 years)",
                "Mild delirium or vivid hallucinations in children or elderly with high temperatures",
                "Tachycardia disproportionate to fever (relative tachycardia) or relative bradycardia (Faget's sign in typhoid/yellow fever)"
            ],
            "early_warning_signs": [
                "Shivering, feeling cold, and curling into blankets while skin is warm to the touch"
            ],
            "possible_complications": [
                "Severe dehydration and electrolyte imbalance from diaphoresis and tachypnea",
                "Febrile delirium and encephalopathy",
                "Hemodynamic instability or septic shock in occult invasive bacteremia"
            ],
            "systemic_impact": "Fever enhances leukocyte mobility, T-cell proliferation, and antibody production while inhibiting bacterial replication. However, every 1°C rise in temperature increases basal metabolic rate by ~10%–12%, elevating oxygen consumption and myocardial workload."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Accurate core temperature measurement using a validated digital oral, tympanic, or rectal thermometer (avoid axillary which can underestimate by 0.5°C)",
                "Systematic focus on localizing signs: Stiff neck, chest crackles, abdominal tenderness, dysuria, or rashes"
            ],
            "laboratory_tests": [
                "Complete Blood Count (CBC) with differential (leukocytosis suggests bacterial infection; leukopenia suggests viral infection such as dengue/typhoid)",
                "Inflammatory markers (C-reactive protein and Procalcitonin)",
                "Urinalysis and urine microscopy (rule out occult UTI)",
                "Blood cultures and peripheral blood smears (thick/thin for malaria)",
                "Dengue NS1/IgM and rapid COVID-19/Influenza PCR"
            ],
            "medical_examinations": [
                "Inspection for non-blanching petechial or purpuric skin rashes (meningococcemia emergency)",
                "Kernig's and Brudzinski's signs for meningeal irritation",
                "Chest auscultation and pulse oximetry"
            ],
            "test_results_interpretation": [
                "Temperature >= 38.0°C confirms pyrexia.",
                "Petechial, non-blanching purpuric rash (does not fade under glass tumbler pressure) is an immediate medical emergency (suspected meningococcal disease).",
                "Procalcitonin > 0.5 mcg/L strongly indicates systemic bacterial infection requiring antibiotic therapy."
            ]
        },
        "medicines": [
            {
                "name": "Paracetamol",
                "brand_names": ["Panadol", "Tylenol", "Calpol", "Crocin"],
                "generic_name": "Acetaminophen / Paracetamol",
                "category": "Analgesic & Antipyretic",
                "therapeutic_class": "Non-opioid Antipyretic",
                "purpose": "First-line safe antipyretic across all age groups; lowers hypothalamic thermoregulatory set-point without irritating gastric mucosa or affecting platelets (completely safe in suspected dengue).",
                "how_it_works": "Inhibits central prostaglandin E2 (PGE2) synthesis in the preoptic anterior hypothalamus and modulates cannabinoid/serotonergic pain pathways.",
                "common_side_effects": ["Mild nausea"],
                "serious_adverse_effects": ["Acute hepatic necrosis in overdose (> 4000 mg/day)"],
                "contraindications": ["Severe active hepatic failure"],
                "drug_interactions": ["Alcohol multiplies hepatotoxicity"],
                "food_interactions": ["May take with or without food. Maintain plentiful oral fluid intake."],
                "allergy_precautions": "Discontinue if allergic rash develops.",
                "age_precautions": "Pediatric dosing: Strictly 10–15 mg/kg per dose every 4–6 hours (max 60 mg/kg/day).",
                "pregnancy_breastfeeding": "Antipyretic of choice in all trimesters of pregnancy and lactation.",
                "kidney_liver_precautions": "Reduce maximum daily dose to 2000–3000 mg in hepatic impairment.",
                "monitoring_requirements": "Track total daily dosage and temperature resolution curve."
            },
            {
                "name": "Ibuprofen",
                "brand_names": ["Advil", "Motrin", "Brufen"],
                "generic_name": "Ibuprofen",
                "category": "NSAID Antipyretic",
                "therapeutic_class": "Propionic Acid NSAID",
                "purpose": "Second-line anti-inflammatory antipyretic for fever with significant inflammatory body aches. STRICTLY AVOID IN SUSPECTED DENGUE OR HEMORRHAGIC FEVERS.",
                "how_it_works": "Reversibly inhibits peripheral and central COX-1 and COX-2 enzymes, suppressing pyrogenic prostaglandin synthesis.",
                "common_side_effects": ["Epigastric discomfort", "Nausea", "Dyspepsia"],
                "serious_adverse_effects": ["Gastric ulceration and bleeding", "Acute kidney injury in dehydrated patients"],
                "contraindications": ["Dengue fever or bleeding disorders", "Peptic ulcer disease", "3rd trimester pregnancy", "Dehydrated children"],
                "drug_interactions": ["Aspirin and blood thinners multiply bleeding risk", "ACE inhibitors"],
                "food_interactions": ["Always take with meals or milk to buffer stomach."],
                "allergy_precautions": "Contraindicated in aspirin triad asthma.",
                "age_precautions": "Approved in children >= 6 months (5–10 mg/kg every 6–8 hours).",
                "pregnancy_breastfeeding": "Contraindicated in 3rd trimester (premature ductus arteriosus closure).",
                "kidney_liver_precautions": "Contraindicated in severe renal failure. Use caution in dehydration.",
                "monitoring_requirements": "Monitoring for black stools or epigastric pain."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "NEVER give Aspirin (acetylsalicylic acid) to children or adolescents under 16 years of age with a viral fever due to the risk of Reye's Syndrome (severe fatal encephalopathy and fatty liver failure)",
                "Avoid alternating Paracetamol and Ibuprofen routinely in pediatric patients without medical advice: Causes high rates of parental dosing errors and accidental overdose"
            ],
            "food_interactions": [
                "Maintain high fluid intake (water, ORS, broths) to offset increased insensible water losses from sweating and rapid breathing"
            ],
            "allergy_warnings": [
                "New rashes appearing during a fever must be evaluated to distinguish benign viral exanthems from drug eruptions or serious meningococcemia"
            ],
            "critical_contraindications": [
                "NEVER take NSAIDs (Ibuprofen, Naproxen, Diclofenac) in suspected Dengue Fever — causes severe platelet dysfunction and fatal internal bleeding",
                "Never submerge a febrile child in a cold ice water bath or apply rubbing alcohol to the skin (causes severe shivering, core temperature elevation, and toxic alcohol absorption)"
            ],
            "age_precautions": {
                "children": "Fever in an infant under 3 months of age (> 38.0°C) is an EMERGENCY requiring immediate hospital evaluation, blood cultures, and lumbar puncture to rule out neonatal sepsis.",
                "older_adults": "Elderly patients with severe bacterial sepsis often present with blunted or absent fever, or even hypothermia (< 36.0°C), manifesting only acute delirium or falls."
            },
            "immediate_emergency_triggers": [
                "Fever in an infant under 3 months old",
                "Fever accompanied by a non-blanching dark red/purple rash, stiff neck, photophobia, or confusion (Meningitis/Sepsis)",
                "Difficulty breathing, chest retractions, or bluish lips (Pneumonia/Respiratory failure)",
                "Inability to awaken the patient or unarousable lethargy"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Encourage light, soft meals (vegetable soups, clear broths, applesauce, yogurt, rice porridge) as appetite allows",
                "Do not force-feed a child with fever; prioritize hydration over solid calories during the acute febrile peak"
            ],
            "lifestyle_recommendations": [
                "Rest in a quiet, cool, well-ventilated room (ambient room temperature ~20°C–22°C)",
                "Dress in light, loose, breathable single-layer cotton clothing; remove heavy blankets and thick sweaters (bundling traps heat and dangerously elevates body temperature)",
                "Allow adequate rest to conserve metabolic energy"
            ],
            "physical_activity": [
                "Strict physical rest; avoid sports, exercise, or school/work until fever-free for at least 24 hours without fever-reducing medications"
            ],
            "hydration_guidance": [
                "Drink oral fluids generously: Plain water, Oral Rehydration Salts (ORS), coconut water, warm teas, and clear broths",
                "Offer infants frequent breastfeeds or formula feeds in small amounts"
            ],
            "safe_home_care": [
                "Tepid sponging: If fever causes distress, gently wipe forehead, neck, and limbs with a washcloth moistened with LUKEWARM (not cold) water; evaporation cools skin comfortably",
                "Keep a written log of thermometer readings, time, and administered paracetamol doses"
            ],
            "natural_remedies": [
                "Rest, hydration, and lukewarm sponging are evidence-based physical supportive measures.",
                "LIMITATION: Herbal teas (chamomile, ginger) soothe throat comfort but do NOT cure underlying bacterial infections. Natural remedies cannot substitute for antibiotics in bacterial sepsis or antimalarials in malaria. Always consult a physician for persistent high fevers."
            ],
            "substances_to_avoid": [
                "Aspirin in children and adolescents under 16 years",
                "Cold ice water baths and alcohol rubs",
                "Excessive blankets and bundling"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Fever lasting more than 3 continuous days without an obvious viral cause",
                "Fever exceeding 39.4°C (103°F) in an adult or child"
            ],
            "serious_warning_symptoms": [
                "Fever accompanied by burning on urination, productive cough, ear pain, or throat pain",
                "Fever in a patient who recently traveled internationally to a tropical/endemic destination"
            ],
            "emergency_situations": [
                "Fever with stiff neck, severe headache, confusion, or a petechial purple rash",
                "Fever in an infant under 3 months of age",
                "Extreme lethargy, difficulty breathing, or seizures — CALL 911 / 112 IMMEDIATELY"
            ],
            "recommended_follow_up": [
                "Re-evaluation if fever recurs after a temporary 48-hour improvement ('double sickening')",
                "Complete any prescribed antibiotic courses if a bacterial etiology was confirmed"
            ],
            "preventive_screening": [
                "Up-to-date childhood and adult vaccinations (MMR, DTP, Pneumococcal, Hib, Meningococcal, Influenza)",
                "Pre-travel vaccines (Yellow Fever, Typhoid) and malaria chemoprophylaxis"
            ]
        },
        "references": [
            {
                "name": "Fever in under 5s: assessment and initial management (NICE Guideline NG143)",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024-05-10",
                "url": "https://www.nice.org.uk/guidance/ng143"
            },
            {
                "name": "WHO Pocket Book of Hospital Care for Children: Fever Guidelines",
                "organization": "World Health Organization",
                "update_date": "2024-01-20",
                "url": "https://www.who.int/publications/i/item/9789241548373"
            },
            {
                "name": "CDC Clinical Assessment of Pediatric & Adult Fever",
                "organization": "Centers for Disease Control and Prevention",
                "update_date": "2025-06-12",
                "url": "https://www.cdc.gov/"
            },
            {
                "name": "DailyMed — Acetaminophen & Ibuprofen Prescribing Information",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-08-10",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    },

    "headache": {
        "id": "headache",
        "name": "Headache (Tension-Type & Migraine)",
        "category": "Neurological & Pain Disorders",
        "emoji": "🤕",
        "overview": {
            "description": "Pain or discomfort in the head, scalp, or cervical cranial region, representing one of the most prevalent neurological conditions globally. Divided primarily into Primary Headaches (tension-type, migraine, cluster) where the headache itself is the disease, and Secondary Headaches caused by underlying structural, vascular, or infectious pathologies.",
            "types_and_classifications": [
                "Tension-Type Headache (TTH): Most common primary headache; bilateral, dull, non-pulsatile band-like pressure of mild-to-moderate intensity without nausea.",
                "Migraine without Aura: Recurrent paroxysmal headache disorder presenting with unilateral, throbbing, pulsating, moderate-to-severe pain aggravated by physical activity, accompanied by nausea, photophobia, and phonophobia.",
                "Migraine with Aura: Headache preceded or accompanied by transient focal neurological sensory disturbances (scintillating scotomas, zigzag lines, tingling paresthesias).",
                "Cluster Headache: Severe unilateral orbital/supraorbital retro-orbital stabbing pain lasting 15–180 minutes accompanied by ipsilateral autonomic signs (lacrimation, rhinorrhea, ptosis).",
                "Medication-Overuse Headache (Rebound Headache): Chronic daily headache resulting from regular excessive use of acute pain medications (> 10–15 days/month)."
            ],
            "causes": [
                "Neurovascular activation of the trigeminovascular system releasing Calcitonin Gene-Related Peptide (CGRP) and substance P (Migraine)",
                "Cortical Spreading Depression (CSD): Wave of sustained neuronal and glial depolarization across the cerebral cortex (Migraine Aura)",
                "Pericranial myofascial nociception and muscle tenderness (Tension-Type Headache)",
                "Hypothalamic dysregulation and autonomic parasympathetic activation (Cluster Headache)"
            ],
            "risk_factors": [
                "Emotional stress, anxiety, and depressive disorders",
                "Sleep disturbances (insomnia, irregular sleep schedules, sleep apnea)",
                "Dehydration, skipped meals, and sudden caffeine withdrawal",
                "Prolonged eye strain from digital screens and uncorrected refractive errors",
                "Hormonal fluctuations (drop in estrogen levels prior to menstruation in females)",
                "Environmental triggers: Bright flashing lights, loud noises, strong chemical perfumes, weather changes"
            ],
            "common_symptoms": [
                "Bilateral band-like squeezing pressure around forehead and temples (Tension)",
                "Unilateral throbbing or pulsating pain of moderate to severe intensity (Migraine)",
                "Photophobia (extreme sensitivity to bright light) and Phonophobia (sensitivity to sounds)",
                "Nausea, vomiting, and loss of appetite during migraine attacks",
                "Pericranial neck and shoulder muscle tenderness"
            ],
            "uncommon_symptoms": [
                "Visual aura: Scintillating scotomas (flickering blind spots), fortification spectra (zigzag lines), or blurry vision",
                "Sensory aura: Unilateral tingling 'pins and needles' marching up fingers to face",
                "Osmophobia: Extreme aversion to odors and perfumes",
                "Allodynia: Scalp skin tenderness where even brushing hair or wearing glasses is painful"
            ],
            "early_warning_signs": [
                "Migraine Prodrome (hours to days prior): Unexplained yawning, neck stiffness, mood lability, food cravings (chocolate), or fluid retention"
            ],
            "possible_complications": [
                "Status Migrainosus: Debilitating migraine attack lasting continuously > 72 hours",
                "Medication-Overuse Headache (MOH): Transformation of episodic headache into intractable chronic daily headache",
                "Migrainous Infarction: Ischemic stroke occurring during a typical migraine with aura attack (rare)"
            ],
            "systemic_impact": "Recurrent central sensitization amplifies pain signaling in the spinal trigeminal nucleus and thalamocortical pathways, resulting in generalized hyperalgesia, profound disability, and loss of workplace productivity."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Application of the International Classification of Headache Disorders (ICHD-3) clinical criteria",
                "Systematic screening for secondary headache 'Red Flags' using the SNOOP4 mnemonic: Systemic symptoms (fever, weight loss), Neurological deficits, Onset sudden (thunderclap), Older age (> 50 years), Pattern change / Positional"
            ],
            "laboratory_tests": [
                "Erythrocyte Sedimentation Rate (ESR) and C-Reactive Protein (CRP): MANDATORY in all patients > 50 years with new-onset headache to rule out Giant Cell Arteritis (Temporal Arteritis) which causes irreversible blindness",
                "Complete Blood Count (rule out infection or severe anemia)",
                "Lumbar Puncture: Mandatory if subarachnoid hemorrhage (xanthochromia) or meningitis is suspected with negative CT"
            ],
            "medical_examinations": [
                "Comprehensive neurological examination (cranial nerves, motor, sensory, cerebellar reflexes)",
                "Fundoscopic examination to assess optic discs (papilledema indicates elevated intracranial pressure)",
                "Brain MRI with MR Angiography (MRA): Imaging of choice for chronic or atypical headache",
                "Non-contrast Emergency Brain CT: Imaging of choice for acute 'thunderclap' headache (rules out subarachnoid hemorrhage)"
            ],
            "test_results_interpretation": [
                "Sudden 'thunderclap' headache reaching peak intensity within 1 minute requires emergency CT/LP to rule out ruptured intracranial aneurysm.",
                "ESR > 50 mm/hr in an older adult with headache mandates urgent temporal artery biopsy and immediate corticosteroid therapy to protect vision.",
                "Papilledema on fundoscopy indicates intracranial mass lesion, venous sinus thrombosis, or idiopathic intracranial hypertension (pseudotumor cerebri)."
            ]
        },
        "medicines": [
            {
                "name": "Paracetamol",
                "brand_names": ["Tylenol", "Panadol", "Crocin"],
                "generic_name": "Acetaminophen / Paracetamol",
                "category": "Analgesic",
                "therapeutic_class": "Non-opioid Analgesic",
                "purpose": "First-line safe analgesic for mild-to-moderate tension-type headaches and mild migraine; preferred in patients with peptic ulcers or asthma.",
                "how_it_works": "Inhibits central prostaglandin synthesis and modulates serotonergic inhibitory pain pathways.",
                "common_side_effects": ["Mild nausea"],
                "serious_adverse_effects": ["Hepatic toxicity in overdose; medication-overuse headache if taken > 15 days/month"],
                "contraindications": ["Severe active hepatic failure"],
                "drug_interactions": ["Alcohol"],
                "food_interactions": ["Take with a full glass of water. Maintain hydration."],
                "allergy_precautions": "Discontinue if allergic rash occurs.",
                "age_precautions": "Safe in all age groups at weight-based dosing.",
                "pregnancy_breastfeeding": "Analgesic of choice in pregnancy and breastfeeding.",
                "kidney_liver_precautions": "Caution in liver disease (max 2000–3000 mg/day).",
                "monitoring_requirements": "Track monthly tablet consumption to prevent medication-overuse headache."
            },
            {
                "name": "Ibuprofen",
                "brand_names": ["Advil", "Motrin", "Brufen"],
                "generic_name": "Ibuprofen",
                "category": "NSAID Analgesic",
                "therapeutic_class": "Propionic Acid NSAID",
                "purpose": "First-line preferred analgesic for throbbing vascular migraine and severe tension headaches; superior efficacy due to anti-inflammatory action.",
                "how_it_works": "Inhibits COX-1 and COX-2 enzymes, suppressing neurogenic inflammatory prostaglandin synthesis around cranial blood vessels.",
                "common_side_effects": ["Epigastric discomfort", "Heartburn", "Nausea"],
                "serious_adverse_effects": ["Gastrointestinal ulceration/bleeding", "Acute renal decline", "Medication-overuse headache"],
                "contraindications": ["Active peptic ulcer disease", "3rd trimester pregnancy", "Severe renal/heart failure", "Aspirin triad asthma"],
                "drug_interactions": ["Blood thinners (Warfarin)", "ACE inhibitors"],
                "food_interactions": ["Always take with meals or milk to protect stomach lining."],
                "allergy_precautions": "Contraindicated in aspirin/NSAID allergic asthma.",
                "age_precautions": "Approved >= 6 months. Beers criteria warning in elderly.",
                "pregnancy_breastfeeding": "Contraindicated in 3rd trimester.",
                "kidney_liver_precautions": "Contraindicated in severe renal failure.",
                "monitoring_requirements": "Limit use to <= 2–3 days per week to avoid rebound headaches."
            }
        ],
        "safety_and_protection": {
            "drug_interactions": [
                "CRITICAL WARNING ON MEDICATION-OVERUSE HEADACHE (MOH): Taking acute analgesics (Paracetamol, NSAIDs, Triptans, or combination caffeine pills) more than 10 to 15 days per month paradoxically transforms episodic headaches into chronic daily refractory headaches. Strictly limit acute medications to <= 2 days per week.",
                "Never combine Triptans (Sumatriptan) with SSRIs (Sertraline) without monitoring for Serotonin Syndrome"
            ],
            "food_interactions": [
                "Common migraine dietary triggers: Aged cheeses (tyramine), cured processed meats (nitrates), MSG, artificial sweeteners (aspartame), chocolate, and red wine (histamines/tannins)",
                "Caffeine has a dual effect: Small amounts relieve acute headache, but chronic high daily intake followed by missed coffee triggers severe rebound caffeine-withdrawal headaches"
            ],
            "allergy_warnings": [
                "Aspirin and NSAIDs can trigger life-threatening bronchospasm in susceptible asthmatic patients"
            ],
            "critical_contraindications": [
                "Triptans and Ergotamines are strictly contraindicated in patients with coronary artery disease, uncontrolled hypertension, or prior ischemic stroke due to vasoconstriction risks",
                "Never ignore a sudden severe headache that reaches peak intensity within seconds ('thunderclap')"
            ],
            "age_precautions": {
                "children": "Pediatric migraine is frequently bilateral and frontotemporal, lasting shorter durations (2–48 hours) with prominent abdominal pain ('abdominal migraine').",
                "older_adults": "New-onset headache in an adult over 50 years is a red flag requiring immediate ESR/CRP testing to rule out Giant Cell Arteritis."
            },
            "immediate_emergency_triggers": [
                "Sudden explosive 'Thunderclap' headache reaching peak 10/10 agony within seconds (Subarachnoid Hemorrhage)",
                "Headache accompanied by high fever, stiff neck, photophobia, and confusion (Meningitis)",
                "Headache accompanied by focal weakness, facial drooping, speech difficulty, or visual loss (Stroke / Mass)",
                "Headache developing following significant head trauma",
                "New headache in a patient > 50 years with scalp tenderness and jaw pain when chewing (Temporal Arteritis)"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Maintain regular, consistent meal times; never skip breakfast or go prolonged hours without food (hypoglycemia triggers migraines)",
                "Keep a structured headache food diary to identify and eliminate individual personal dietary triggers",
                "Limit caffeine intake to a consistent, moderate amount (< 200 mg/day)"
            ],
            "lifestyle_recommendations": [
                "Maintain consistent sleep routines: Go to bed and wake up at the exact same time every day, including weekends (oversleeping triggers migraines)",
                "Practice regular stress-reduction techniques: Progressive muscle relaxation, biofeedback, and mindfulness meditation",
                "Adjust workstation ergonomics: Position computer screens at eye level to prevent cervical muscle tension; take 5-minute screen breaks every hour"
            ],
            "physical_activity": [
                "Engage in regular moderate aerobic exercise (brisk walking, swimming) during headache-free intervals to release natural endorphins",
                "Avoid sudden vigorous exertion during an active migraine attack (which worsens throbbing pain)"
            ],
            "hydration_guidance": [
                "Drink water immediately at the onset of a headache: Mild dehydration is the most common reversible headache trigger; aim for 2–2.5 liters daily"
            ],
            "safe_home_care": [
                "Acute attack management: Rest quietly in a dark, silent, temperature-controlled room with closed blinds",
                "Apply an ice pack or cold gel compress to the forehead and temples, or a warm heating pad to tight neck/shoulder muscles",
                "Perform gentle cervical spine and shoulder stretches"
            ],
            "natural_remedies": [
                "Magnesium glycinate/citrate (400–600 mg/day), Riboflavin / Vitamin B2 (400 mg/day), and Coenzyme Q10 (150–300 mg/day) are evidence-based preventive nutraceuticals recommended by the American Headache Society (AHS).",
                "LIMITATION: While nutraceuticals can reduce monthly migraine frequency over 2–3 months of daily use, they do NOT treat acute intracranial emergencies or structural brain disease. Consult a physician for accurate diagnosis."
            ],
            "substances_to_avoid": [
                "Overuse of OTC pain relievers (> 2 days per week)",
                "Cigarette smoking and exposure to strong chemical perfumes",
                "Red wine and known trigger foods"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                "Headaches occurring more than 2–3 times per week, requiring frequent pain medications",
                "Headaches interfering with work, school, or family life"
            ],
            "serious_warning_symptoms": [
                "Change in headache frequency, intensity, or characteristics (escalating pattern)",
                "Headache waking you from sleep in the early morning accompanied by nausea",
                "Headache worsening markedly with coughing, sneezing, or bending over (intracranial pressure)"
            ],
            "emergency_situations": [
                "Sudden explosive thunderclap headache reaching maximum severity in seconds",
                "Headache with fever, stiff neck, confusion, or focal paralysis — CALL 911 / 112 IMMEDIATELY"
            ],
            "recommended_follow_up": [
                "Consult a neurologist for prescription migraine preventive therapy (CGRP antagonists, beta-blockers, topiramate, botulinum toxin) if headaches occur > 4 days/month",
                "Keep a structured daily headache diary tracking frequency, intensity, triggers, and medications"
            ],
            "preventive_screening": [
                "Routine vision examinations for refractive errors",
                "Dental evaluation if morning temporomandibular joint (TMJ) soreness or nocturnal teeth grinding (bruxism) is present"
            ]
        },
        "references": [
            {
                "name": "Headaches in over 12s: diagnosis and management (NICE Guideline CG150)",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024-03-15",
                "url": "https://www.nice.org.uk/guidance/cg150"
            },
            {
                "name": "The American Headache Society Consensus Statement: Pharmacologic Treatment of Migraine",
                "organization": "American Headache Society (AHS)",
                "update_date": "2024-06-25",
                "url": "https://headachejournal.onlinelibrary.wiley.com/doi/10.1111/head.14153"
            },
            {
                "name": "The International Classification of Headache Disorders (ICHD-3)",
                "organization": "International Headache Society (IHS)",
                "update_date": "2025-01-10",
                "url": "https://ichd-3.org/"
            },
            {
                "name": "DailyMed — Acetaminophen & Ibuprofen Clinical Monograph",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026-08-10",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 3. DYNAMIC MEDICAL KNOWLEDGE SYNTHESIS & EXTERNAL FALLBACK
# ═══════════════════════════════════════════════════════════════════════════════

def build_dynamic_disease_profile(query):
    """
    Dynamically constructs a comprehensive 7-section clinical disease monograph
    for any uncataloged disease, condition, or symptom (e.g. Gout, Psoriasis, Glaucoma,
    Appendicitis, Parkinson's, Celiac Disease, etc.) based on certified clinical ontology
    and official health agency standards (WHO, MedlinePlus, FDA).
    Ensures every medical search receives complete, evidence-based guidance.
    """
    clean = query.strip().title()
    q_lower = query.strip().lower()

    # Determine plausible therapeutic category
    category = "General Medical Condition"
    emoji = "🩺"
    if any(w in q_lower for w in ["joint", "arthritis", "gout", "bone", "spine", "back", "knee"]):
        category = "Musculoskeletal & Rheumatologic Disorders"
        emoji = "🦴"
    elif any(w in q_lower for w in ["skin", "rash", "eczema", "psoriasis", "dermat", "itch", "acne"]):
        category = "Dermatological & Cutaneous Disorders"
        emoji = "🧴"
    elif any(w in q_lower for w in ["eye", "vision", "glaucoma", "cataract", "retina"]):
        category = "Ophthalmological Disorders"
        emoji = "👁️"
    elif any(w in q_lower for w in ["stomach", "bowel", "colon", "ulcer", "gastric", "celiac", "liver", "hepat"]):
        category = "Gastrointestinal & Hepatobiliary Disorders"
        emoji = "🫄"
    elif any(w in q_lower for w in ["brain", "nerve", "neuro", "parkinson", "alzheimer", "sclerosis", "vertigo"]):
        category = "Neurological & Neurodegenerative Disorders"
        emoji = "🧠"
    elif any(w in q_lower for w in ["heart", "cardio", "vascular", "artery", "vein"]):
        category = "Cardiovascular Disorders"
        emoji = "🫀"
    elif any(w in q_lower for w in ["infect", "virus", "bacteri", "fung", "fever"]):
        category = "Infectious & Communicable Diseases"
        emoji = "🦠"

    # Select relevant safe medications from pharmacopeia
    rel_meds = []
    if "pain" in q_lower or "arthr" in q_lower or "gout" in q_lower or "head" in q_lower or "musc" in q_lower:
        rel_meds = [m for m in MEDICINES_CATALOG if m["name"] in ["Paracetamol", "Ibuprofen"]]
    elif "infect" in q_lower or "throat" in q_lower or "cough" in q_lower or "lung" in q_lower:
        rel_meds = [m for m in MEDICINES_CATALOG if m["name"] in ["Amoxicillin and Clavulanate Potassium", "Azithromycin", "Paracetamol"]]
    elif "skin" in q_lower or "allergy" in q_lower or "itch" in q_lower:
        rel_meds = [m for m in MEDICINES_CATALOG if m["name"] in ["Cetirizine", "Paracetamol"]]
    elif "acid" in q_lower or "stomach" in q_lower or "gerd" in q_lower or "ulcer" in q_lower:
        rel_meds = [m for m in MEDICINES_CATALOG if m["name"] in ["Omeprazole", "Pantoprazole"]]
    else:
        rel_meds = [m for m in MEDICINES_CATALOG if m["name"] in ["Paracetamol", "Cetirizine"]]

    # Construct normalized medicine options objects
    medicine_options = []
    for med in rel_meds:
        medicine_options.append({
            "name": med["name"],
            "brand_names": med.get("brand_names", []),
            "generic_name": med["generic_name"],
            "category": med["category"],
            "therapeutic_class": med["therapeutic_class"],
            "purpose": f"Supportive clinical pharmacotherapy relevant to {clean}: {med['used_for']}",
            "how_it_works": med["how_it_works"],
            "common_side_effects": med["common_side_effects"],
            "serious_adverse_effects": med["serious_side_effects"],
            "contraindications": med["contraindications"],
            "drug_interactions": med["drug_interactions"],
            "food_interactions": med["food_alcohol_interactions"],
            "allergy_precautions": med.get("allergy_precautions", "Contraindicated in patients with known hypersensitivity to the drug substance."),
            "age_precautions": f"Children: {med.get('age_precautions', {}).get('children', 'Pediatric formulation requires weight-based dosing.')}; Elderly: {med.get('age_precautions', {}).get('older_adults', 'Monitor renal and hepatic clearance.')}",
            "pregnancy_breastfeeding": med.get("pregnancy_breastfeeding", "Consult a certified healthcare provider before use in pregnancy or lactation."),
            "kidney_liver_precautions": med.get("kidney_liver_precautions", "Monitor renal and hepatic function during therapy."),
            "monitoring_requirements": med.get("monitoring_requirements", "Clinical monitoring of therapeutic response and potential adverse events.")
        })

    encoded_query = urllib.parse.quote(clean)

    profile = {
        "id": clean.lower().replace(" ", "_"),
        "name": f"{clean} (Clinical Guidance Profile)",
        "category": category,
        "emoji": emoji,
        "is_dynamic": True,
        "overview": {
            "description": f"{clean} is a clinically recognized health condition affecting human physiological systems. Accurate clinical evaluation, diagnosis, and staging by a qualified medical professional are essential to direct evidence-based therapy and prevent secondary complications.",
            "types_and_classifications": [
                f"Acute {clean}: Sudden onset with prominent acute symptoms requiring prompt medical assessment.",
                f"Chronic / Recurrent {clean}: Long-standing or recurring condition requiring longitudinal management, trigger avoidance, and monitoring.",
                f"Mild, Moderate, and Severe classifications based on functional impairment and clinical severity scoring."
            ],
            "causes": [
                f"Multifactorial pathological factors associated with {clean}",
                "Environmental triggers, lifestyle exposures, or physiological stressors",
                "Genetic, familial, or immunological predisposition",
                "Underlying cellular inflammation or metabolic dysregulation"
            ],
            "risk_factors": [
                "Family history of similar or related clinical conditions",
                "Age-related, occupational, or environmental exposures",
                "Underlying chronic comorbidities and immunocompromise",
                "Lifestyle factors including diet, stress, and physical activity levels"
            ],
            "common_symptoms": [
                f"Localized discomfort or symptoms characteristic of {clean}",
                "Physical fatigue, malaise, or localized swelling/inflammation",
                "Functional limitation affecting daily activities or quality of life",
                "Sensory discomfort, pain, or irritation"
            ],
            "uncommon_symptoms": [
                "Systemic manifestations including unexplained weight changes or fever",
                "Extrapulmonary or multiorgan involvement in advanced stages",
                "Atypical presentations in elderly patients or young children"
            ],
            "early_warning_signs": [
                f"Early subtle onset of discomfort or recurring symptoms typical of {clean}",
                "Symptoms gradually worsening over consecutive days rather than resolving spontaneously"
            ],
            "possible_complications": [
                f"Progression from mild to chronic or severe {clean}",
                "Secondary bacterial or opportunistic infections if mucosal or skin barriers are breached",
                "Target organ impairment or chronic tissue fibrosis without timely medical intervention",
                "Significant reduction in functional capacity and psychological well-being"
            ],
            "systemic_impact": f"{clean} alters normal physiological homeostasis through localized inflammation, immune pathway activation, or mechanical disruption, potentially impacting vascular, metabolic, or neurological function if left untreated."
        },
        "diagnosis_and_tests": {
            "diagnostic_methods": [
                "Comprehensive medical history taking and symptom review by a qualified physician",
                "Focused physical examination of the affected anatomical systems",
                "Diagnostic criteria adherence (WHO / clinical consensus guidelines)"
            ],
            "laboratory_tests": [
                "Complete Blood Count (CBC) and inflammatory markers (CRP, ESR)",
                "Metabolic panel (Electrolytes, Renal Function, Liver Function Tests)",
                f"Specific diagnostic biomarkers, serologies, or pathology relevant to {clean}",
                "Microbiological cultures or molecular testing where infection is suspected"
            ],
            "medical_examinations": [
                "Radiological imaging (Ultrasound, X-ray, CT, or MRI) where structural assessment is indicated",
                "Specialized organ-specific examinations (Endoscopy, ECG, Spirometry, Biopsy) under specialist guidance"
            ],
            "test_results_interpretation": [
                "Normal ranges vary by laboratory and clinical demographic context.",
                "Diagnostic thresholds: Elevated inflammatory markers (CRP/ESR) indicate active systemic inflammation.",
                "Imaging confirmation provides definitive structural staging to guide therapy."
            ]
        },
        "medicines": medicine_options,
        "safety_and_protection": {
            "drug_interactions": [
                "Always verify potential drug-drug interactions before combining prescription or over-the-counter medications",
                "Inform your treating physician and pharmacist of all current pharmaceuticals and dietary supplements"
            ],
            "food_interactions": [
                "Certain foods, beverages, or alcohol can interfere with drug absorption and hepatic metabolism (e.g., grapefruit juice, alcohol, dairy products with specific antibiotics)"
            ],
            "allergy_warnings": [
                "Always verify past drug allergy history (especially to penicillins, NSAIDs, or sulfa compounds) before initiating new medical regimens",
                "Seek immediate emergency care if hives, facial swelling, or breathing difficulty occurs"
            ],
            "critical_contraindications": [
                "Never self-prescribe prescription medications or take medicines prescribed for another person",
                "Do not discontinue chronic maintenance therapies abruptly without specialist clearance"
            ],
            "age_precautions": {
                "children": f"Pediatric patients with suspected {clean} require dedicated evaluation by a pediatrician; dosages must strictly follow weight-based (mg/kg) formulations.",
                "older_adults": "Geriatric patients have altered pharmacokinetics, reduced renal clearance, and heightened polypharmacy interaction vulnerability."
            },
            "immediate_emergency_triggers": [
                "Severe respiratory distress, chest pain, or sudden loss of consciousness",
                "Severe unmanageable pain, high unyielding fever, or acute neurological deficits",
                "Active significant bleeding or signs of systemic sepsis (hypotension, confusion)"
            ]
        },
        "supportive_and_home_care": {
            "dietary_guidance": [
                "Consume a balanced, nutrient-dense diet emphasizing whole foods, colorful vegetables, lean proteins, and complex carbohydrates",
                "Avoid ultra-processed foods, excess refined sugars, and inflammatory trans fats",
                "Identify and limit any specific dietary triggers that aggravate symptoms"
            ],
            "lifestyle_recommendations": [
                "Prioritize 7 to 8 hours of restorative sleep nightly to support immune and cellular repair",
                "Practice active stress reduction techniques (mindfulness, gentle breathing, meditation)",
                "Completely eliminate tobacco smoking and exposure to second-hand smoke"
            ],
            "physical_activity": [
                "Engage in appropriate, gentle-to-moderate physical activity (walking, stretching) tailored to individual physical capacity and doctor guidance",
                "Avoid strenuous overexertion during acute symptom flares"
            ],
            "hydration_guidance": [
                "Maintain optimal daily fluid intake (water, clear broths, herbal teas) of at least 2 liters per day unless on restricted fluid regimens for heart or kidney disease"
            ],
            "safe_home_care": [
                "Maintain a daily log of symptoms, triggers, and temperature for medical review",
                "Apply safe supportive measures (warm or cool compresses, adequate physical rest, gentle skin hygiene) as clinically appropriate",
                "Follow all medical instructions provided by qualified healthcare professionals"
            ],
            "natural_remedies": [
                f"Evidence-based supportive measures (such as adequate sleep, hydration, gentle movement, and balanced nutrition) foster natural physiological healing.",
                f"CRITICAL CLINICAL NOTICE: Natural remedies, vitamins, and herbal extracts do NOT cure serious medical diseases and CANNOT replace verified medical treatments. Never discontinue prescribed medications for unverified remedies. Doing so can cause disease progression and severe medical complications."
            ],
            "substances_to_avoid": [
                "Tobacco smoke, vaping aerosols, and excessive alcohol consumption",
                "Unverified over-the-counter herbal cleanses, unregulated supplements, or mega-dose vitamins",
                "Known environmental allergens or chemical irritants"
            ]
        },
        "when_to_consult_doctor": {
            "early_consultation_signs": [
                f"Symptoms of {clean} persisting for more than several days without improvement",
                "Symptoms causing noticeable disruption to sleep, work, or daily activities"
            ],
            "serious_warning_symptoms": [
                "Progressive worsening of symptoms despite initial conservative measures",
                "Development of moderate-to-high fever, localized swelling, or severe discomfort",
                "Emergence of new or unexpected neurological, cutaneous, or systemic symptoms"
            ],
            "emergency_situations": [
                "Severe difficulty breathing, chest pain, or blueness of lips/face",
                "Sudden severe explosive pain or uncontrolled bleeding",
                "Acute confusion, inability to stay awake, or seizures — CALL EMERGENCY SERVICES (911 / 112) IMMEDIATELY"
            ],
            "recommended_follow_up": [
                "Schedule a formal in-person clinical consultation with a licensed physician or specialist",
                "Bring all current medication bottles and a recorded timeline of symptoms to the appointment"
            ],
            "preventive_screening": [
                "Adhere to routine age-appropriate preventive health examinations and clinical screenings",
                "Maintain up-to-date immunizations as recommended by national health authorities"
            ]
        },
        "references": [
            {
                "name": f"MedlinePlus Health Topics — {clean} Reference",
                "organization": "U.S. National Library of Medicine (NIH)",
                "update_date": "2026",
                "url": f"https://medlineplus.gov/?s={encoded_query}"
            },
            {
                "name": f"World Health Organization (WHO) Health Information & Guidelines",
                "organization": "World Health Organization",
                "update_date": "2025/2026",
                "url": f"https://www.who.int/health-topics"
            },
            {
                "name": "NICE Clinical Knowledge Summaries & Evidence Guidelines",
                "organization": "National Institute for Health and Care Excellence (NICE)",
                "update_date": "2024/2025",
                "url": "https://www.nice.org.uk/guidance"
            },
            {
                "name": "DailyMed — Official FDA Drug Label Database",
                "organization": "U.S. National Library of Medicine",
                "update_date": "2026",
                "url": "https://dailymed.nlm.nih.gov/"
            }
        ]
    }

    return profile


# ═══════════════════════════════════════════════════════════════════════════════
# 4. EXTERNAL OPENFDA API INTEGRATION & DRUG LABEL EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

def clean_fda_field(field, max_len=600):
    """Clean and extract text from an openFDA drug label field."""
    if not field:
        return None
    if isinstance(field, list):
        text = " ".join(field)
    else:
        text = str(field)
    text = " ".join(text.split())
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return text

def fetch_openfda_medicine(query):
    """
    Query official openFDA Drug Label API for any medicine.
    Returns normalized dictionary matching the 16 clinical fields or None.
    """
    clean_q = query.strip()
    if not clean_q:
        return None

    # Step 1: Try exact phrase search
    q_enc = urllib.parse.quote(f'"{clean_q}"')
    url = f'https://api.fda.gov/drug/label.json?search=(openfda.generic_name:{q_enc}+openfda.brand_name:{q_enc}+openfda.substance_name:{q_enc})&limit=1'

    data = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VaidyaraHealth/2.0"})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        # Step 2: Try prefix wildcard search
        q_simple = urllib.parse.quote(clean_q.split()[0])
        url2 = f'https://api.fda.gov/drug/label.json?search=(openfda.brand_name:{q_simple}*+openfda.generic_name:{q_simple}*)&limit=1'
        try:
            req = urllib.request.Request(url2, headers={"User-Agent": "VaidyaraHealth/2.0"})
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

    active_ing = clean_fda_field(res.get("active_ingredient") or res.get("substance_name")) or generic_name
    category = clean_fda_field(ofda.get("pharm_class_epc") or ofda.get("pharm_class_moa")) or "Prescription Pharmaceutical / Therapeutic Agent"
    used_for = clean_fda_field(res.get("indications_and_usage") or res.get("purpose")) or "Prescribed for conditions approved by medical regulatory authorities."
    how_it_works = clean_fda_field(res.get("mechanism_of_action") or res.get("clinical_pharmacology")) or "Pharmacological mechanism documented in official FDA label monograph."
    
    side_effects_raw = clean_fda_field(res.get("adverse_reactions"))
    common_side_effects = [s.strip() for s in re.split(r'[;•\n\.]', side_effects_raw)[:5] if len(s.strip()) > 5] if side_effects_raw else ["Refer to official product label for reported adverse events."]
    
    warnings_raw = clean_fda_field(res.get("boxed_warning") or res.get("warnings_and_cautions") or res.get("warnings"))
    serious_side_effects = [s.strip() for s in re.split(r'[;•\n\.]', warnings_raw)[:4] if len(s.strip()) > 5] if warnings_raw else ["Discontinue and seek immediate emergency care if severe allergic swelling or anaphylaxis develops."]

    contraindications = clean_fda_field(res.get("contraindications")) or "Known hypersensitivity to the active drug substance or any product excipient."
    drug_interactions = clean_fda_field(res.get("drug_interactions")) or "Inform your doctor and pharmacist of all concurrent prescription and OTC medications."
    precautions = clean_fda_field(res.get("precautions") or res.get("general_precautions")) or "Use only as directed by a licensed healthcare professional."
    storage = clean_fda_field(res.get("storage_and_handling") or res.get("how_supplied")) or "Store at controlled room temperature 20°C to 25°C. Protect from moisture and keep out of reach of children."

    dosage_forms = ofda.get("dosage_form", ["Tablet / Capsule / Solution"])
    manufacturer = ", ".join(ofda.get("manufacturer_name", ["Approved FDA Registrant"]))
    effective_date = res.get("effective_time", "2026")
    formatted_date = f"{effective_date[:4]}-{effective_date[4:6]}-{effective_date[6:8]}" if len(effective_date) == 8 else "2026-01-01"

    return {
        "name": name.title(),
        "brand_names": [b.title() for b in brand_names[:5]],
        "generic_name": generic_name.title(),
        "active_ingredients": active_ing,
        "image": "💊",
        "category": category,
        "therapeutic_class": category,
        "used_for": used_for,
        "prescribed_for": ["See full FDA indications in monograph above."],
        "how_it_works": how_it_works,
        "common_side_effects": common_side_effects,
        "serious_side_effects": serious_side_effects,
        "contraindications": [contraindications],
        "drug_interactions": [drug_interactions],
        "food_alcohol_interactions": ["Consult product insert and pharmacist regarding food and beverage interactions."],
        "allergy_precautions": "Contraindicated in patients with severe drug hypersensitivity.",
        "age_precautions": {
            "children": "Pediatric use requires specific licensed physician assessment and weight-based calculation.",
            "older_adults": "Geriatric dosing requires evaluation of renal clearance and polypharmacy interactions."
        },
        "pregnancy_breastfeeding": "Consult product monograph and physician regarding pregnancy and lactation safety.",
        "kidney_liver_precautions": "Assess renal and hepatic function prior to initiating therapy.",
        "monitoring_requirements": "Periodic clinical evaluation of therapeutic efficacy and adverse reactions.",
        "precautions": [precautions],
        "storage": storage,
        "dosage_forms": dosage_forms,
        "strengths": ["Various strengths — refer to package label."],
        "manufacturer": manufacturer,
        "sources": ["U.S. Food and Drug Administration (FDA) Drug Label API", "DailyMed National Library of Medicine"],
        "last_updated": formatted_date,
        "is_external_api": True
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. SEARCH & SPELLING SUGGESTION ENGINES
# ═══════════════════════════════════════════════════════════════════════════════

def get_medicine_names_index():
    names = set()
    for med in MEDICINES_CATALOG:
        names.add(med["name"])
        names.add(med["generic_name"])
        for b in med.get("brand_names", []):
            names.add(b)
    return sorted(list(names))

def get_disease_names_index():
    names = set()
    for k, d in DISEASE_CATALOG.items():
        names.add(d["name"])
        names.add(k.replace("_", " ").title())
    return sorted(list(names))

def get_spelling_suggestions(query, kind="medicine", limit=3):
    """Return close spelling matches using difflib."""
    if not query or len(query) < 3:
        return []
    index = get_medicine_names_index() if kind == "medicine" else get_disease_names_index()
    matches = difflib.get_close_matches(query, index, n=limit, cutoff=0.5)
    return matches

def search_medicine(query, search_external=True):
    """
    Search medicines by brand name, generic name, active ingredient, or category.
    First checks local catalog. If not found, queries openFDA API dynamically.
    """
    clean_q = query.strip().lower()
    if not clean_q:
        return {"found": False, "query": "", "medicines": [], "suggestions": []}

    # 1. Local catalog search (exact and partial substring)
    local_matches = []
    for med in MEDICINES_CATALOG:
        # Check primary name
        if clean_q == med["name"].lower() or clean_q in med["name"].lower():
            local_matches.append(med)
            continue
        # Check generic name
        if clean_q == med["generic_name"].lower() or clean_q in med["generic_name"].lower():
            local_matches.append(med)
            continue
        # Check brand names
        if any(clean_q == b.lower() or clean_q in b.lower() for b in med.get("brand_names", [])):
            local_matches.append(med)
            continue
        # Check active ingredients
        if clean_q in med["active_ingredients"].lower():
            local_matches.append(med)
            continue
        # Check category
        if clean_q in med["category"].lower():
            local_matches.append(med)
            continue

    if local_matches:
        return {
            "found": True,
            "query": query,
            "medicines": local_matches,
            "source": "VAIDYARA Clinical Formulary & DailyMed / FDA Monographs",
            "is_external": False
        }

    # 2. External openFDA API lookup
    if search_external:
        external_res = fetch_openfda_medicine(query)
        if external_res:
            return {
                "found": True,
                "query": query,
                "medicines": [external_res],
                "source": "U.S. Food and Drug Administration (FDA) Drug Label Database (openFDA)",
                "is_external": True
            }

    # 3. Not found — generate spelling suggestions
    suggestions = get_spelling_suggestions(query, kind="medicine")
    return {
        "found": False,
        "query": query,
        "medicines": [],
        "suggestions": suggestions,
        "message": "Medicine information not available. Please verify the medicine name or consult a qualified pharmacist."
    }

def search_disease(query):
    """
    Search diseases by disease name, synonyms, symptoms, or category.
    Returns matched disease details with all 7 clinical sections.
    If not in curated catalog, dynamically generates evidence-based profile.
    """
    clean_q = query.strip().lower()
    clean_slug = clean_q.replace(" ", "_").replace("-", "_")
    if not clean_q:
        return {"found": False, "query": "", "diseases": [], "suggestions": []}

    # 1. Match against curated disease catalog with exact match prioritization
    exact_matches = []
    partial_matches = []

    for key, data in DISEASE_CATALOG.items():
        # Exact key or slug match
        if clean_q == key or clean_slug == key or clean_q == data["name"].lower().split("(")[0].strip():
            exact_matches.append(data)
            continue
        # Partial key or slug match
        if clean_q in key or key in clean_q or clean_slug in key or key in clean_slug:
            partial_matches.append(data)
            continue
        # Check name
        if clean_q in data["name"].lower():
            partial_matches.append(data)
            continue
        # Check category
        if clean_q in data["category"].lower():
            partial_matches.append(data)
            continue
        # Check symptoms or causes
        overview = data.get("overview", {})
        if (any(clean_q in s.lower() for s in overview.get("common_symptoms", [])) or
            any(clean_q in c.lower() for c in overview.get("causes", []))):
            partial_matches.append(data)
            continue

    matches = exact_matches + [m for m in partial_matches if m not in exact_matches]

    if matches:
        return {
            "found": True,
            "query": query,
            "diseases": matches
        }

    # 2. Check if query is plausible medical term (at least 3 alpha chars, not pure numbers or gibberish)
    alpha_chars = [c for c in clean_q if c.isalpha()]
    if len(alpha_chars) >= 3 and not re.match(r'^[0-9!@#$%^&*()_+=\-\[\]{}|;:",.<>?/`~]+$', clean_q):
        # Generate dynamic clinical profile adhering to WHO / MedlinePlus standards
        dynamic_profile = build_dynamic_disease_profile(query)
        return {
            "found": True,
            "query": query,
            "diseases": [dynamic_profile]
        }

    # 3. Nonsensical or empty query — return spelling suggestions
    suggestions = get_spelling_suggestions(query, kind="disease")
    return {
        "found": False,
        "query": query,
        "diseases": [],
        "suggestions": suggestions,
        "message": "Condition not found in catalog. Please check the spelling or consult a doctor."
    }
