import streamlit as st
import pandas as pd
from google import genai

# Page Configuration
st.set_page_config(page_title="OpenRTE - School Infrastructure Tracker", layout="wide")

st.title("🏛️ OpenRTE: Citizen Infrastructure & Deficit Intelligence")
st.markdown(
    "Automated open-source intelligence pipeline auditing statutory compliance under the "
    "**Right to Education (RTE) Act, 2009** using public UDISE+ benchmarks."
)

# 1. Dataset (Expandable with real UDISE CSV dumps)
@st.cache_data
def load_data():
    return pd.DataFrame([
        {
            "School Name": "Karisunda Prathamik Vidyalaya",
            "UDISE Code": "19131401201",
            "District": "Bankura",
            "Block": "Indas",
            "Electricity": "No",
            "Girls Toilets (Functional)": 0,
            "Drinking Water": "Not Functional",
            "Boundary Wall": "Dilapidated"
        },
        {
            "School Name": "Salboni Rural Primary School",
            "UDISE Code": "19200804502",
            "District": "Paschim Medinipur",
            "Block": "Salboni",
            "Electricity": "Yes",
            "Girls Toilets (Functional)": 0,
            "Drinking Water": "Non-Functional Handpump",
            "Boundary Wall": "None"
        },
        {
            "School Name": "Medinipur Town Model Primary",
            "UDISE Code": "19200101102",
            "District": "Paschim Medinipur",
            "Block": "Medinipur Sadar",
            "Electricity": "Yes",
            "Girls Toilets (Functional)": 3,
            "Drinking Water": "Functional RO Unit",
            "Boundary Wall": "Pucca"
        }
    ])

df = load_data()

# 2. Deficit Analyzer Logic
def analyze_deficits(row):
    deficits = []
    if row["Electricity"] in ["No", "None", False]:
        deficits.append("No Classroom Electrification / Ceiling Fans")
    if row["Girls Toilets (Functional)"] == 0:
        deficits.append("Zero Functional Girls' Toilets (RTE Sec 19 Violation)")
    if "Not" in str(row["Drinking Water"]) or "Non" in str(row["Drinking Water"]):
        deficits.append("Unsafe / Non-Functional Drinking Water Source")
    if row["Boundary Wall"] in ["None", "Dilapidated"]:
        deficits.append("Compromised Perimeter / Lack of Secure Boundary Wall")
    return deficits

df["Deficits"] = df.apply(analyze_deficits, axis=1)
df["Compliance Status"] = df["Deficits"].apply(lambda d: "⚠️ Deficit Flagged" if len(d) > 0 else "✅ Compliant")

# 3. Sidebar Filters
st.sidebar.header("Filter Geographic Scope")
selected_district = st.sidebar.selectbox("Select District", ["All"] + list(df["District"].unique()))
filtered_df = df if selected_district == "All" else df[df["District"] == selected_district]

# 4. Metrics Dashboard
col1, col2, col3 = st.columns(3)
col1.metric("Total Schools Tracked", len(filtered_df))
col2.metric("Deficit Institutions", len(filtered_df[filtered_df["Compliance Status"] == "⚠️ Deficit Flagged"]))
col3.metric("Fully Compliant", len(filtered_df[filtered_df["Compliance Status"] == "✅ Compliant"]))

st.divider()

# 5. Data Explorer Table
st.subheader("📋 Institutional Infrastructure Ledger")
st.dataframe(
    filtered_df[["School Name", "UDISE Code", "District", "Block", "Electricity", "Girls Toilets (Functional)", "Drinking Water", "Compliance Status"]],
    use_container_width=True
)

st.divider()

# 6. Automated Legal Dossier Generator
st.subheader("⚖️ Generate Statutory RTE Grievance / RTI Dossier")

flagged_schools = filtered_df[filtered_df["Compliance Status"] == "⚠️ Deficit Flagged"]

if not flagged_schools.empty:
    selected_school_name = st.selectbox("Choose a deficit school to generate petition:", flagged_schools["School Name"].unique())
    school_record = flagged_schools[flagged_schools["School Name"] == selected_school_name].iloc[0]

    st.write(f"**Identified Non-Compliance Issues for {selected_school_name}:**")
    for d in school_record["Deficits"]:
        st.markdown(f"- 🔴 {d}")

    if st.button("Generate Legal Dossier via Gemini Engine"):
        with st.spinner("Compiling statutory citations and drafting petition..."):
            try:
                client = genai.Client()
                prompt = f"""
                Draft a formal, structured public grievance petition for submission to the District Magistrate and State Education Secretary.
                
                School Details:
                - Name: {school_record['School Name']}
                - UDISE Code: {school_record['UDISE Code']}
                - Block: {school_record['Block']}, District: {school_record['District']}
                
                Identified Deficits:
                {', '.join(school_record['Deficits'])}
                
                Legal Grounding:
                - Cite Section 19 and the Schedule to the Right of Children to Free and Compulsory Education (RTE) Act, 2009.
                - Reference Supreme Court landmark precedent in Environmental & Consumer Protection Foundation v. UOI (2012).
                - Demand immediate administrative site inspection and allocation of basic Composite School Grants / SSA funds.
                - Keep tone professional, legal, and non-accusatory.
                """
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                
                petition_text = response.text
                st.success("Dossier Generated Successfully!")
                st.text_area("Generated Petition (Ready to Copy)", petition_text, height=350)
                
                # Download Button for the petition
                st.download_button(
                    label="📥 Download Legal Dossier (.txt)",
                    data=petition_text,
                    file_name=f"RTE_Grievance_{school_record['UDISE Code']}.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Error connecting to AI engine: {e}")
else:
    st.info("No deficit schools found for the selected filters.")