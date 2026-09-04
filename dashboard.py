import streamlit as st
import pandas as pd
from google import genai
from fpdf import FPDF

# Page Configuration
st.set_page_config(
    page_title="OpenRTE - National Infrastructure & RTI Intelligence Engine",
    page_icon="🏛️",
    layout="wide"
)

# State-to-Authority Administrative Mapping
STATE_AUTHORITY_MAP = {
    "West Bengal": {"officer": "District Inspector of Schools (DI/SE)", "dept": "School Education Department, Govt. of West Bengal"},
    "Uttar Pradesh": {"officer": "Basic Shiksha Adhikari (BSA)", "dept": "Department of Basic Education, Govt. of Uttar Pradesh"},
    "Bihar": {"officer": "District Education Officer (DEO)", "dept": "Education Department, Govt. of Bihar"},
    "Tamil Nadu": {"officer": "Chief Educational Officer (CEO)", "dept": "School Education Department, Govt. of Tamil Nadu"},
    "Maharashtra": {"officer": "Education Officer (Primary/Secondary), Zilla Parishad", "dept": "School Education and Sports Department, Govt. of Maharashtra"},
    "Karnataka": {"officer": "Deputy Director of Public Instruction (DDPI)", "dept": "Department of School Education and Literacy, Govt. of Karnataka"},
    "Jharkhand": {"officer": "District Education Officer (DEO) / DSE", "dept": "Department of School Education & Literacy, Govt. of Jharkhand"},
    "Odisha": {"officer": "District Education Officer (DEO)", "dept": "School & Mass Education Department, Govt. of Odisha"},
    "Rajasthan": {"officer": "Chief District Education Officer (CDEO)", "dept": "Department of School Education, Govt. of Rajasthan"},
    "Madhya Pradesh": {"officer": "District Education Officer (DEO)", "dept": "School Education Department, Govt. of Madhya Pradesh"},
    "Assam": {"officer": "District Elementary Education Officer (DEEO)", "dept": "Department of School Education, Govt. of Assam"},
    "Delhi (NCT)": {"officer": "Deputy Director of Education (DDE), District Zone", "dept": "Directorate of Education, Govt. of NCT of Delhi"}
}

# PDF Generator Class
class NationalLegalDossierPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 7, "STATUTORY CITIZEN DOSSIER & RTI DEMAND UNDER RTE ACT, 2009", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 8.5)
        self.cell(0, 5, "Generated via OpenRTE National Civic Intelligence Engine | Form 6(1) RTI & Section 19 Compliance", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 23, 200, 23)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"OpenRTE National Infrastructure Protocol | Page {self.page_no()}", align="C")

def generate_pdf(school_name, udise_code, state, district, block, content):
    pdf = NationalLegalDossierPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Metadata Box
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(0, 5, f"INSTITUTION: {school_name} | UDISE: {udise_code}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)
    pdf.cell(0, 5, f"JURISDICTION: Block {block}, District {district}, {state}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Clean and render body text
    pdf.set_font("Helvetica", size=9)
    clean_text = content.replace("**", "").replace("#", "").replace("–", "-").replace("—", "-")
    pdf.multi_cell(0, 5.2, clean_text)
    
    # Formal Signature Blocks
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Submitted on behalf of School Management Committee (SMC) & Concerned Citizens:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8.5)
    pdf.cell(0, 5, "1. Name: _______________________  Signature: __________________  Date: ____________", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "2. Name: _______________________  Signature: __________________  Date: ____________", new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())

# Main Interface
st.title("🏛️ OpenRTE: Pan-India Infrastructure & Statutory Action Engine")
st.markdown(
    "Automating the generation of **Legally-Binding Grievance Memorandums** and **Section 6(1) RTI Applications** "
    "for any public school across India under **Section 19 of the RTE Act, 2009**."
)

st.divider()

# Input Grid
col1, col2, col3 = st.columns(3)
with col1:
    school_name = st.text_input("School Name*", placeholder="e.g. Salboni Rural Primary School")
    udise_code = st.text_input("11-Digit National UDISE Code*", placeholder="e.g. 19200804502")

with col2:
    state = st.selectbox("State / UT*", list(STATE_AUTHORITY_MAP.keys()))
    district = st.text_input("District*", placeholder="e.g. Paschim Medinipur")

with col3:
    block = st.text_input("Block / Tehsil / Mandal*", placeholder="e.g. Salboni")
    language = st.selectbox("Target Drafting Language", [
        "English (Formal Judicial)",
        "Bengali (বাংলা)",
        "Hindi (हिन्दी)",
        "Tamil (தமிழ்)",
        "Telugu (తెలుగు)",
        "Marathi (मराठी)",
        "Kannada (ಕನ್ನಡ)",
        "Odia (ଓଡ଼ିଆ)"
    ])

st.markdown("#### Audit Statutory Deficits (Schedule to Section 19, RTE Act 2009):")
d_col1, d_col2 = st.columns(2)
with d_col1:
    d1 = st.checkbox("Zero functional gender-segregated toilets for girls/boys")
    d2 = st.checkbox("Absence of functional potable drinking water facility")
    d3 = st.checkbox("Absence of classroom electrification & functional ceiling fans")
with d_col2:
    d4 = st.checkbox("Compromised perimeter / Missing or collapsed boundary wall")
    d5 = st.checkbox("Absence of barrier-free disabled access ramps (CWSN)")
    d6 = st.checkbox("Dilapidated or missing Mid-Day Meal (PM POSHAN) kitchen shed")

st.divider()

if st.button("🚀 Generate Dual-Action Dossier (Grievance + RTI Form)", type="primary"):
    flagged = []
    if d1: flagged.append("Zero functional gender-segregated toilets (Violation of RTE Sec 19 Norms)")
    if d2: flagged.append("Absence of safe potable drinking water on premises")
    if d3: flagged.append("Lack of classroom electrification and fans")
    if d4: flagged.append("Non-existent/damaged boundary wall compromising child safety")
    if d5: flagged.append("Absence of CWSN disabled-friendly barrier-free access")
    if d6: flagged.append("Missing/non-functional PM POSHAN kitchen infrastructure")

    if not school_name or not udise_code or not district or not block:
        st.error("Please complete all required fields (marked with *).")
    elif not flagged:
        st.warning("Please flag at least one infrastructure deficit.")
    else:
        authority_info = STATE_AUTHORITY_MAP.get(state, {"officer": "District Education Officer", "dept": "School Education Department"})
        
        with st.spinner("Compiling dual legal instruments and statutory citations..."):
            try:
                client = genai.Client()
                prompt = f"""
                You are an elite Indian administrative and constitutional legal expert. 
                Generate a comprehensive two-part statutory document:
                
                TARGET INSTITUTION DETAILS:
                - School Name: {school_name}
                - UDISE Code: {udise_code}
                - Jurisdiction: Block {block}, District {district}, State of {state}
                - Designated Statutory Recipient: {authority_info['officer']}, {authority_info['dept']}, and the District Magistrate/Collector.
                - Flagged Deficits: {', '.join(flagged)}
                - Language Requirement: {language}
                
                STRUCTURE THE OUTPUT INTO TWO DISTINCT LEGAL SECTIONS:
                
                SECTION I: STATUTORY CITIZEN GRIEVANCE MEMORANDUM
                1. Addressed to: The District Magistrate and the {authority_info['officer']}.
                2. Subject: Formal Representation regarding non-compliance with Section 19 read with the Schedule of the RTE Act, 2009 at {school_name}.
                3. Grounds:
                   - Cite Section 19 and Schedule norms of the RTE Act, 2009.
                   - Cite Supreme Court precedent: Environmental & Consumer Protection Foundation v. Union of India (2012) 10 SCC 197 (holding that basic school infrastructure is an inalienable component of the Article 21A right to education).
                4. Prayer for Relief: Demand immediate physical site inspection within 7 days, sanction of emergency composite school/civil repair grants under Samagra Shiksha, and time-bound 30-day compliance.
                
                SECTION II: FORM 6(1) RIGHT TO INFORMATION (RTI) APPLICATION
                1. Addressed to: Public Information Officer (PIO), Office of the {authority_info['officer']}.
                2. Specific Information Demanded under Section 6(1) of the RTI Act, 2005:
                   - Certified copies of annual civil maintenance and composite grants sanctioned to {school_name} (UDISE: {udise_code}) under Samagra Shiksha for the past 3 financial years.
                   - Inspection notes and compliance reports submitted by the Block Education Officer (BEO) regarding these deficits during the last 24 months.
                   - Certified expenditure and utilization certificates (UC) submitted for toilet and drinking water repairs for this school.
                
                Ensure the tone is strictly legal, authoritative, and structured for immediate official submission.
                """

                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )

                dossier_text = response.text
                st.success("✅ Dual Legal Dossier Generated Successfully!")
                
                st.text_area("Legal Memorandum & RTI Application Preview", dossier_text, height=400)
                
                # Generate PDF (in English encoding for standard printable format)
                pdf_bytes = generate_pdf(school_name, udise_code, state, district, block, dossier_text)
                
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    st.download_button(
                        label="📄 Download Official Printable Dossier (PDF)",
                        data=pdf_bytes,
                        file_name=f"OpenRTE_Dossier_{udise_code}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                with p_col2:
                    st.download_button(
                        label="📝 Download Raw Dossier (.txt)",
                        data=dossier_text,
                        file_name=f"OpenRTE_Dossier_{udise_code}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Engine Error: {e}")