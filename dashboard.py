import streamlit as st
import pandas as pd
from google import genai
from fpdf import FPDF
import io

# Page Configuration
st.set_page_config(page_title="OpenRTE - National Infrastructure Audit Engine", layout="wide", page_icon="🏛️")

# PDF Generator Class
class LegalPetitionPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 8, "FORMAL CITIZEN MEMORANDUM UNDER STATUTORY RTE PROVISIONS", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 5, "Section 19 & Schedule Norms, Right of Children to Free and Compulsory Education Act, 2009", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 24, 200, 24)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"OpenRTE Public Audit Intelligence Engine | Page {self.page_no()}", align="C")

def create_pdf(school_name, udise_code, district, state, petition_text):
    pdf = LegalPetitionPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    
    # Metadata Block
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, f"Target Institution: {school_name} (UDISE: {udise_code})", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Jurisdiction: {district}, {state}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Body
    pdf.set_font("Helvetica", size=9.5)
    # Sanitize markdown formatting and quotes for standard PDF encoding
    clean_text = petition_text.replace("**", "").replace("#", "").replace("–", "-").replace("—", "-")
    pdf.multi_cell(0, 5.5, clean_text)
    
    # Signatures
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(0, 6, "Verification and Endorsement by Citizens / SMC Representatives:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8.5)
    pdf.cell(0, 5, "1. Name: _______________________  Signature: __________________  Date: ____________", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "2. Name: _______________________  Signature: __________________  Date: ____________", new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())

# Main Header
st.title("🏛️ OpenRTE: National School Infrastructure Compliance Engine")
st.markdown(
    "Automating statutory Right to Education (RTE) compliance audits and legal grievance dossier generation across Indian public schools."
)

tab1, tab2 = st.tabs(["🔍 Audit Any Indian School", "📋 Sample Benchmarks & Upload"])

# ----------------- TAB 1: AUDIT ANY SCHOOL IN INDIA -----------------
with tab1:
    st.subheader("Step 1: Enter Institutional Coordinates")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        school_name = st.text_input("School Name*", placeholder="e.g. Salboni Rural Primary School")
        udise_code = st.text_input("11-Digit UDISE Code*", placeholder="e.g. 19200804502")
    with c2:
        state = st.selectbox("State / UT*", [
            "West Bengal", "Bihar", "Uttar Pradesh", "Jharkhand", "Odisha", 
            "Maharashtra", "Madhya Pradesh", "Rajasthan", "Assam", "Tamil Nadu", 
            "Karnataka", "Gujarat", "Andhra Pradesh", "Telangana", "Punjab", "Haryana", "Delhi"
        ])
        district = st.text_input("District*", placeholder="e.g. Paschim Medinipur")
    with c3:
        block = st.text_input("Block / Tehsil / Circle*", placeholder="e.g. Salboni")
        school_cat = st.selectbox("School Category", ["Primary (Grades 1-5)", "Upper Primary (Grades 6-8)", "Secondary/Higher Sec"])

    st.divider()
    st.subheader("Step 2: Audit Infrastructure Deficits (RTE Schedule Norms)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        d_toilets = st.checkbox("❌ Zero Functional Separate Girls'/Boys' Toilets", value=True)
        d_water = st.checkbox("❌ No Safe / Functional Potable Drinking Water Supply", value=True)
        d_power = st.checkbox("❌ Lack of Classroom Electrification / Ceiling Fans")
    with col_b:
        d_boundary = st.checkbox("❌ Dilapidated or Missing Secure Boundary Wall", value=True)
        d_cwsn = st.checkbox("❌ Lack of Barrier-Free CWSN Ramp Access")
        d_kitchen = st.checkbox("❌ Missing Functional Kitchen Shed for PM POSHAN / Mid-Day Meal")

    st.divider()

    if st.button("⚖️ Generate Official Legal Grievance Dossier", type="primary"):
        flagged_deficits = []
        if d_toilets: flagged_deficits.append("Non-availability of functional gender-segregated toilets (Violation of RTE Sec 19)")
        if d_water: flagged_deficits.append("Absence of potable drinking water infrastructure on premises")
        if d_power: flagged_deficits.append("Absence of classroom electrification and fans")
        if d_boundary: flagged_deficits.append("Absence of secured boundary perimeter fencing / wall")
        if d_cwsn: flagged_deficits.append("Absence of disabled-friendly barrier-free ramp access")
        if d_kitchen: flagged_deficits.append("Non-functional or missing kitchen facility for Mid-Day Meal preparation")

        if not school_name or not udise_code or not district or not block:
            st.error("Please fill in all required institutional fields marked with *.")
        elif not flagged_deficits:
            st.warning("Please flag at least one infrastructure deficit.")
        else:
            with st.spinner("Invoking Gemini to compile statutory citations and draft legal memorandum..."):
                try:
                    client = genai.Client()
                    prompt = f"""
                    Draft a formal, structured public grievance petition for submission to the District Magistrate, District Inspector of Schools, and State Principal Secretary of Education.
                    
                    Target Institution Details:
                    - School Name: {school_name}
                    - UDISE Code: {udise_code}
                    - Block/Taluk: {block}, District: {district}, State: {state}
                    - Level: {school_cat}
                    
                    Identified Non-Compliance Deficits:
                    {', '.join(flagged_deficits)}
                    
                    Statutory and Legal Directives to Include:
                    - Cite Section 19 and the Schedule to the Right of Children to Free and Compulsory Education (RTE) Act, 2009.
                    - Cite Supreme Court precedent in Environmental & Consumer Protection Foundation v. Union of India (2012) linking basic school infrastructure directly to Fundamental Rights under Article 21A.
                    - Formulate a formal 'Prayer for Relief' requesting a joint physical verification within 7 days, immediate Composite School Grant / Samagra Shiksha fund sanction, and a 30-day compliance timeline.
                    - Tone must be objective, strictly legal, and formal. Do not make personal accusations.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt
                    )
                    
                    petition_text = response.text
                    
                    st.success("✅ Statutory Dossier Drafted Successfully!")
                    st.text_area("Legal Memorandum Preview", petition_text, height=350)
                    
                    # Generate downloadable PDF
                    pdf_bytes = create_pdf(school_name, udise_code, district, state, petition_text)
                    
                    c_down1, c_down2 = st.columns(2)
                    with c_down1:
                        st.download_button(
                            label="📄 Download Official Legal Dossier (Printable PDF)",
                            data=pdf_bytes,
                            file_name=f"RTE_Legal_Dossier_{udise_code}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    with c_down2:
                        st.download_button(
                            label="📝 Download Raw Text (.txt)",
                            data=petition_text,
                            file_name=f"RTE_Grievance_{udise_code}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"Error connecting to AI engine: {e}")

# ----------------- TAB 2: BENCHMARKS & CSV -----------------
with tab2:
    st.subheader("Batch Ingestion & Preloaded District Samples")
    st.markdown("Upload official directory CSV dumps from `dashboard.udiseplus.gov.in` to audit entire blocks at once.")
    
    uploaded_file = st.file_uploader("Upload UDISE+ CSV Dataset", type=["csv"])
    if uploaded_file:
        batch_df = pd.read_csv(uploaded_file)
        st.write("Uploaded Dataset Overview:")
        st.dataframe(batch_df.head(10), use_container_width=True)
    else:
        st.info("No custom dataset uploaded. Displaying default demonstration ledger:")
        sample_df = pd.DataFrame([
            {"School Name": "Karisunda Prathamik Vidyalaya", "UDISE Code": "19131401201", "District": "Bankura", "Girls Toilets": 0, "Potable Water": "None", "Status": "Critical Violation"},
            {"School Name": "Salboni Rural Primary", "UDISE Code": "19200804502", "District": "Paschim Medinipur", "Girls Toilets": 0, "Potable Water": "Handpump (Dry)", "Status": "Critical Violation"},
            {"School Name": "Medinipur Town Model Primary", "UDISE Code": "19200101102", "District": "Paschim Medinipur", "Girls Toilets": 3, "Potable Water": "Functional RO", "Status": "Compliant"}
        ])
        st.dataframe(sample_df, use_container_width=True)