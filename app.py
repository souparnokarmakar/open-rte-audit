import json
import pandas as pd
from google import genai

# 1. Initialize Gemini Client (Requires GEMINI_API_KEY environment variable)
# You can set it in terminal via: export GEMINI_API_KEY="your-api-key" or in PowerShell: $env:GEMINI_API_KEY="your-api-key"
client = genai.Client()

# 2. Input Data (You can add multiple schools here from UDISE+ manual copy or CSV)
sample_schools = [
    {
        "name": "Karisunda Prathamik Vidyalaya",
        "udise_code": "19131401201",
        "district": "Bankura",
        "block": "Indas",
        "electricity": "No",
        "functional_girls_toilets": 0,
        "potable_water": "Not Functional",
        "boundary_wall": "Dilapidated"
    },
    {
        "name": "Salboni Rural Primary School",
        "udise_code": "19200804502",
        "district": "Paschim Medinipur",
        "block": "Salboni",
        "electricity": "Yes",
        "functional_girls_toilets": 0,
        "potable_water": "Non-Functional Handpump",
        "boundary_wall": "None"
    }
]

def check_rte_deficits(school):
    """Flags if a school violates basic RTE Schedule norms"""
    deficits = []
    if school.get("electricity") in ["No", "None", False]:
        deficits.append("No Classroom Electrification/Fans")
    if school.get("functional_girls_toilets", 0) == 0:
        deficits.append("Zero Functional Girls Toilets (RTE Sec 19 Violation)")
    if "Not" in school.get("potable_water", "") or "Non" in school.get("potable_water", ""):
        deficits.append("No Potable Drinking Water Supply")
    if school.get("boundary_wall") in ["None", "Dilapidated"]:
        deficits.append("Compromised School Perimeter/Safety")
    return deficits

def generate_grievance(school, deficits):
    """Uses Gemini to format a legal CPGRAMS petition"""
    prompt = f"""
    Draft a formal, structured public grievance petition for submission to the District Magistrate and State Education Secretary.
    
    School Details:
    - Name: {school['name']}
    - UDISE Code: {school['udise_code']}
    - Block: {school['block']}, District: {school['district']}
    
    Identified Deficits:
    {', '.join(deficits)}
    
    Legal Grounding:
    - Cite Section 19 and Schedule of the Right of Children to Free and Compulsory Education (RTE) Act, 2009.
    - Demand immediate administrative inspection and allocation of basic repair/maintenance funds.
    - Keep tone professional, legal, and non-accusatory.
    """
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )
    return response.text

# 3. Main Execution Engine
results = []
print("🔍 Scanning schools for RTE infrastructure non-compliance...\n")

for school in sample_schools:
    deficits = check_rte_deficits(school)
    if deficits:
        print(f"⚠️ Flagged Deficit: {school['name']} ({school['udise_code']})")
        print(f"   Issues: {', '.join(deficits)}")
        
        # Draft legal petition via AI
        grievance_draft = generate_grievance(school, deficits)
        
        results.append({
            "School Name": school["name"],
            "UDISE Code": school["udise_code"],
            "District": school["district"],
            "Block": school["block"],
            "Deficits Found": "; ".join(deficits),
            "Ready Grievance Petition": grievance_draft
        })

# 4. Save structured results to Excel / CSV
if results:
    df = pd.DataFrame(results)
    df.to_csv("flagged_schools_grievances.csv", index=False)
    print("\n✅ Finished! All drafts exported to 'flagged_schools_grievances.csv'")