import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from fpdf import FPDF
import io

# Page Configuration
st.set_page_config(
    page_title="OpenRTE - National Infrastructure Intelligence & Compliance Engine",
    page_icon="🏛️",
    layout="wide"
)

# --- 1. PRE-LOADED UDISE+ DATABASE (EXTENSIBLE DATASET) ---
@st.cache_data
def get_master_data():
    data = [
        {
            "UDISE Code": "19200804502",
            "School Name": "Salboni Rural Primary School",
            "State": "West Bengal",
            "District": "Paschim Medinipur",
            "Block": "Salboni",
            "Functional Girls Toilets": 0,
            "Functional Boys Toilets": 1,
            "Potable Drinking Water": "Non-Functional Handpump",
            "Electricity": "No",
            "Boundary Wall": "None",
            "CWSN Ramp": "No",
            "MDM Kitchen": "Yes"
        },
        {
            "UDISE Code": "19131401201",
            "School Name": "Karisunda Prathamik Vidyalaya",
            "State": "West Bengal",
            "District": "Bankura",
            "Block": "Indas",
            "Functional Girls Toilets": 0,
            "Functional Boys Toilets": 0,
            "Potable Drinking Water": "Not Available",
            "Electricity": "No",
            "Boundary Wall": "Dilapidated",
            "CWSN Ramp": "No",
            "MDM Kitchen": "No"
        },
        {
            "UDISE Code": "19200101102",
            "School Name": "Medinipur Town Model Primary",
            "State": "West Bengal",
            "District": "Paschim Medinipur",
            "Block": "Medinipur Sadar",
            "Functional Girls Toilets": 3,
            "Functional Boys Toilets": 3,
            "Potable Drinking Water": "Functional RO Unit",
            "Electricity": "Yes",
            "Boundary Wall": "Pucca",
            "CWSN Ramp": "Yes",
            "MDM Kitchen": "Yes"
        },
        {
            "UDISE Code": "19200502201",
            "School Name": "Garbeta West Junior Basic",
            "State": "West Bengal",
            "District": "Paschim Medinipur",
            "Block": "Garbeta",
            "Functional Girls Toilets": 0,
            "Functional Boys Toilets": 1,
            "Potable Drinking Water": "Functional Well",
            "Electricity": "Yes",
            "Boundary Wall": "Partially Damaged",
            "CWSN Ramp": "No",
            "MDM Kitchen": "Yes"
        },
        {
            "UDISE Code": "19130208801",
            "School Name": "Kotulpur Board Primary School",
            "State": "West Bengal",
            "District": "Bankura",
            "Block": "Kotulpur",
            "Functional Girls Toilets": 1,
            "Functional Boys Toilets": 1,
            "Potable Drinking Water": "Functional Tap Water",
            "Electricity": "Yes",
            "Boundary Wall": "Pucca",
            "CWSN Ramp": "Yes",
            "MDM Kitchen": "Yes"
        },
        {
            "UDISE Code": "19130704403",
            "School Name": "Bishnupur Tribal Primary Vidyalaya",
            "State": "West Bengal",
            "District": "Bankura",
            "Block": "Bishnupur",
            "Functional Girls Toilets": 0,
            "Functional Boys Toilets": 0,
            "Potable Drinking Water": "Non-Functional Tube-well",
            "Electricity": "No",
            "Boundary Wall": "None",
            "CWSN Ramp": "No",
            "MDM Kitchen": "No"
        }
    ]
    return pd.DataFrame(data)

df = get_master_data()

# --- 2. STATUTORY DEFICIT & SCORING ENGINE ---
def compute_compliance(row):
    deficits = []
    score = 100
    
    # Statutory RTE Schedule Benchmarks
    if row["Functional Girls Toilets"] == 0:
        deficits.append("Zero Functional Girls' Toilets (Sec 19 Violation)")
        score -= 25
    if "Not" in str(row["Potable Drinking Water"]) or "Non" in str(row["Potable Drinking Water"]):
        deficits.append("Absence of Potable Drinking Water Supply")
        score -= 25
    if row["Electricity"] == "No":
        deficits.append("Lack of Classroom Electrification & Ceiling Fans")
        score -= 15
    if row["Boundary Wall"] in ["None", "Dilapidated", "Partially Damaged"]:
        deficits.append("Compromised Perimeter / No Secure Boundary Wall")
        score -= 15
    if row["CWSN Ramp"] == "No":
        deficits.append("No Barrier-Free Disabled (CWSN) Ramp Access")
        score -= 10
    if row["MDM Kitchen"] == "No":
        deficits.append("Missing PM-POSHAN Mid-Day Meal Kitchen Facility")
        score -= 10
        
    grade = "A+ (Compliant)"
    if score < 50:
        grade = "F (Severe Statutory Default)"
    elif score < 70:
        grade = "D (Critical Deficits)"
    elif score < 85:
        grade = "B (Partial Compliance)"
        
    return pd.Series([deficits, score, grade], index=["Deficits", "Compliance_Score", "Grade"])

df[["Deficits", "Compliance_Score", "Grade"]] = df.apply(compute_compliance, axis=1)

# --- 3. PDF GENERATION ENGINE ---
class LegalPetitionPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, "FORMAL STATUTORY CITIZEN MEMORANDUM & GRIEVANCE", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 5, "Pursuant to Section 19 & Schedule to the Right of Children to Free and Compulsory Education (RTE) Act, 2009", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 24, 200, 24)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"OpenRTE Automated Civic Intelligence Engine | Page {self.page_no()}", align="C")

def create_pdf(school_name, udise_code, district, state, petition_text):
    pdf = LegalPetitionPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, f"Target Institution: {school_name} (UDISE: {udise_code})", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Jurisdiction: {district}, {state}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font("Helvetica", size=9.5)
    clean_text = petition_text.replace("**", "").replace("#", "").replace("–", "-").replace("—", "-")
    pdf.multi_cell(0, 5.5, clean_text)
    
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(0, 6, "Verification and Endorsement by Citizens / SMC Representatives:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8.5)
    pdf.cell(0, 5, "1. Name: _______________________  Signature: __________________  Date: ____________", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "2. Name: _______________________  Signature: __________________  Date: ____________", new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())

# --- 4. DASHBOARD UI ---
st.title("🏛️ OpenRTE: National Infrastructure Audit & Statutory Compliance Engine")
st.markdown(
    "Automating public school infrastructure audits and legal grievance generation under **Section 19 of the RTE Act, 2009**."
)

tab_search, tab_analytics, tab_custom = st.tabs(["🔍 Instant UDISE+ Lookup & Legal Drafter", "📊 District Heatmap & Leaderboards", "✍️ Manual School Audit"])

# --- TAB 1: INSTANT LOOKUP ---
with tab_search:
    st.subheader("Instant School Compliance Lookup")
    
    search_col1, search_col2 = st.columns([2, 1])
    with search_col1:
        school_options = [f"{row['School Name']} ({row['UDISE Code']}) - {row['District']}" for _, row in df.iterrows()]
        selected_option = st.selectbox("Search by School Name or UDISE Code:", school_options)
    
    selected_udise = selected_option.split("(")[1].split(")")[0]
    school_record = df[df["UDISE Code"] == selected_udise].iloc[0]
    
    # Scorecard Display
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Compliance Score", f"{school_record['Compliance_Score']}/100")
    m2.metric("Statutory Rating", school_record["Grade"])
    m3.metric("District / Block", f"{school_record['District']} / {school_record['Block']}")
    m4.metric("Girls' Functional Toilets", f"{school_record['Functional Girls Toilets']}")
    
    st.markdown("#### Identified Statutory Non-Compliance Deficits:")
    if school_record["Deficits"]:
        for d in school_record["Deficits"]:
            st.error(f"🔴 {d}")
    else:
        st.success("✅ Fully Compliant with Section 19 Infrastructure Norms")
        
    st.divider()
    
    if st.button("⚖️ Generate Official Legal Petition for this School", type="primary"):
        with st.spinner("Compiling statutory citations and drafting petition via Gemini..."):
            try:
                client = genai.Client()
                prompt = f"""
                Draft a formal, structured public grievance petition for submission to the District Magistrate, District Inspector of Schools, and Principal Secretary of Education.
                
                Institution Details:
                - School Name: {school_record['School Name']}
                - UDISE Code: {school_record['UDISE Code']}
                - Block: {school_record['Block']}, District: {school_record['District']}, State: {school_record['State']}
                - Official Compliance Rating: {school_record['Grade']} (Score: {school_record['Compliance_Score']}/100)
                
                Identified Infrastructure Deficits:
                {', '.join(school_record['Deficits'])}
                
                Legal Directives:
                - Cite Section 19 and the Schedule to the Right of Children to Free and Compulsory Education (RTE) Act, 2009.
                - Reference Supreme Court precedent in Environmental & Consumer Protection Foundation v. Union of India (2012) regarding fundamental rights under Article 21A.
                - Demand a joint physical verification within 7 days and release of Samagra Shiksha repair grants with a 30-day compliance timeline.
                - Tone must be strictly objective, legal, and professional.
                """
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                
                petition_text = response.text
                st.success("✅ Legal Dossier Generated Successfully!")
                st.text_area("Generated Petition Preview", petition_text, height=300)
                
                pdf_data = create_pdf(
                    school_record['School Name'],
                    school_record['UDISE Code'],
                    school_record['District'],
                    school_record['State'],
                    petition_text
                )
                
                st.download_button(
                    label="📄 Download Official Legal Dossier (Printable PDF)",
                    data=pdf_data,
                    file_name=f"RTE_Grievance_{school_record['UDISE Code']}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"AI Engine Error: {e}")

# --- TAB 2: DISTRICT ANALYTICS ---
with tab_analytics:
    st.subheader("District Infrastructure Health & Deficit Leaderboard")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_pie = px.pie(df, names="Grade", title="Overall Statutory Compliance Breakdown", color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_g2:
        fig_bar = px.bar(df, x="School Name", y="Compliance_Score", color="Grade", title="Institutional Compliance Scores", text="Compliance_Score")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.markdown("#### Complete Institutional Deficit Ledger")
    st.dataframe(df[["School Name", "UDISE Code", "District", "Block", "Compliance_Score", "Grade", "Deficits"]], use_container_width=True)

# --- TAB 3: CUSTOM / UNLISTED SCHOOL AUDIT ---
with tab_custom:
    st.subheader("Audit Any Unlisted School in India")
    c_name = st.text_input("School Name", placeholder="e.g. Rampur Primary School")
    c_udise = st.text_input("UDISE Code", placeholder="e.g. 19200000000")
    c_dist = st.text_input("District", placeholder="e.g. Jhargram")
    c_deficits = st.multiselect("Flag Infrastructure Deficits", [
        "Zero Functional Girls' Toilets",
        "No Potable Drinking Water Supply",
        "Lack of Electrification / Fans",
        "Missing Boundary Wall",
        "No CWSN Ramp Access"
    ])
    
    if st.button("Generate Custom Legal Dossier"):
        if not c_name or not c_udise or not c_deficits:
            st.warning("Please fill in the School Name, UDISE code, and select at least one deficit.")
        else:
            with st.spinner("Generating legal memorandum..."):
                try:
                    client = genai.Client()
                    prompt = f"Draft a formal RTE Section 19 grievance for {c_name} (UDISE: {c_udise}, {c_dist}) suffering from: {', '.join(c_deficits)}. Cite Supreme Court 2012 precedent."
                    res = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
                    st.text_area("Draft Preview", res.text, height=250)
                    pdf_data = create_pdf(c_name, c_udise, c_dist, "India", res.text)
                    st.download_button("📄 Download Custom PDF", data=pdf_data, file_name=f"RTE_{c_udise}.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"Error: {e}")