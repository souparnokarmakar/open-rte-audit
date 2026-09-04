import streamlit as st
import pandas as pd
from google import genai
from fpdf import FPDF
import io

# Page Configuration
st.set_page_config(
    page_title="OpenRTE - National Evidentiary Civic Audit Platform",
    page_icon="⚖️",
    layout="wide"
)

# Administrative Hierarchy Mapping across States
JURISDICTION_REGISTRY = {
    "West Bengal": {
        "primary_officer": "District Inspector of Schools (PE / SE)",
        "district_lead": "District Magistrate & Collector",
        "state_dept": "Department of School Education, Govt. of West Bengal",
        "rules_ref": "West Bengal Right of Children to Free and Compulsory Education Rules, 2012"
    },
    "Bihar": {
        "primary_officer": "District Education Officer (DEO) / DPO (SSA)",
        "district_lead": "District Magistrate",
        "state_dept": "Education Department, Govt. of Bihar",
        "rules_ref": "Bihar State RTE Rules, 2011"
    },
    "Uttar Pradesh": {
        "primary_officer": "Basic Shiksha Adhikari (BSA)",
        "district_lead": "District Magistrate",
        "state_dept": "Department of Basic Education, Govt. of Uttar Pradesh",
        "rules_ref": "Uttar Pradesh Right of Children to Free and Compulsory Education Rules, 2011"
    },
    "Maharashtra": {
        "primary_officer": "Education Officer (Primary), Zilla Parishad",
        "district_lead": "District Collector & CEO ZP",
        "state_dept": "School Education Department, Govt. of Maharashtra",
        "rules_ref": "Maharashtra RTE Rules, 2011"
    },
    "Jharkhand": {
        "primary_officer": "District Superintendent of Education (DSE)",
        "district_lead": "Deputy Commissioner",
        "state_dept": "Department of School Education and Literacy, Govt. of Jharkhand",
        "rules_ref": "Jharkhand RTE Rules, 2011"
    },
    "Odisha": {
        "primary_officer": "District Education Officer (DEO)",
        "district_lead": "Collector & District Magistrate",
        "state_dept": "School and Mass Education Department, Govt. of Odisha",
        "rules_ref": "Odisha RTE Rules, 2010"
    },
    "Tamil Nadu": {
        "primary_officer": "Chief Educational Officer (CEO)",
        "district_lead": "District Collector",
        "state_dept": "Department of School Education, Govt. of Tamil Nadu",
        "rules_ref": "Tamil Nadu RTE Rules, 2011"
    }
}

# Advanced PDF Formatter
class AuditDossierPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 7, "STATUTORY FIELD AUDIT & CITIZEN COMPLIANCE DOSSIER", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 8.5)
        self.cell(0, 5, "Statutory Action Pack under RTE Act (Sec 19) & Right to Information Act, 2005 (Sec 6)", border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 23, 200, 23)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"OpenRTE Public Audit & Evidentiary Engine | Document Page {self.page_no()}", align="C")

def build_pdf_dossier(school_name, udise_code, state, district, block, generated_text):
    pdf = AuditDossierPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header Information Box
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(0, 5, f"AUDIT TARGET: {school_name.upper()} | UDISE CODE: {udise_code}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8.5)
    pdf.cell(0, 5, f"ADMINISTRATIVE JURISDICTION: Block {block}, District {district}, {state}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Comprehensive character sanitization for PDF encoding
    clean_text = (
        generated_text.replace("**", "")
        .replace("###", "")
        .replace("##", "")
        .replace("#", "")
        .replace("–", "-")
        .replace("—", "-")
        .replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("₹", "Rs. ")
        .replace("•", "-")
        .replace("…", "...")
    )
    clean_text = clean_text.encode("latin-1", "replace").decode("latin-1")
    
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(0, 5.2, clean_text)
    
    # Field Verification Block
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "ON-GROUND VERIFICATION & PHYSICAL CITIZEN ENDORSEMENT", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=8)
    pdf.cell(0, 4.5, "We hereby certify that a physical spot audit of the institution was conducted and the deficits cited above were verified:", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.cell(0, 5, "1. Name: __________________________  Phone: ___________________  Signature: _______________", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "2. Name: __________________________  Phone: ___________________  Signature: _______________", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "3. SMC / Ward Rep: _________________  Designation: ______________  Signature: _______________", new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())

# Main Streamlit Application UI
st.title("⚖️ OpenRTE: Citizen Evidentiary Audit & Legal Redressal Engine")
st.markdown(
    "Standardizing on-ground school infrastructure audits into **Statutory Section 19 Demands** "
    "and **Form 6(1) RTI Applications** for grassroots transparency campaigns."
)

st.divider()

col_i1, col_i2, col_i3 = st.columns(3)
with col_i1:
    school_name = st.text_input("School / Institution Name*", placeholder="e.g. Salboni Rural Primary School")
    udise_code = st.text_input("11-Digit UDISE+ Code*", placeholder="e.g. 19200804502")
with col_i2:
    state = st.selectbox("State / Territory*", list(JURISDICTION_REGISTRY.keys()))
    district = st.text_input("District*", placeholder="e.g. Paschim Medinipur")
with col_i3:
    block = st.text_input("Block / Mandal / Tehsil*", placeholder="e.g. Salboni")
    audit_date = st.date_input("Audit Inspection Date")

st.markdown("#### Statutory Deficit Audit Checklist (RTE Act, 2009 - Section 19 Schedule Norms)")
ch1, ch2, ch3 = st.columns(3)
with ch1:
    f_toilets = st.checkbox("Zero functional girls' / boys' toilets")
    f_water = st.checkbox("Non-functional or contaminated drinking water source")
with ch2:
    f_power = st.checkbox("Zero classroom electrification / non-functional ceiling fans")
    f_boundary = st.checkbox("Collapsed, dilapidated, or missing boundary wall")
with ch3:
    f_cwsn = st.checkbox("Absence of CWSN disabled barrier-free ramp access")
    f_mdm = st.checkbox("Unsafe or non-existent Mid-Day Meal kitchen shed")

custom_notes = st.text_area("Specific Ground Observations (Optional)", placeholder="e.g. Handpump dry for 14 months; students forced to fetch water from 500m away.")

st.divider()

if st.button("Generate Complete Statutory Legal & RTI Dossier", type="primary"):
    selected_deficits = []
    if f_toilets: selected_deficits.append("Non-provision of separate functional toilets for girls and boys (Violation of RTE Sec 19 & Schedule Item 2)")
    if f_water: selected_deficits.append("Absence of potable, functional drinking water supply on premises (Violation of RTE Schedule Item 3)")
    if f_power: selected_deficits.append("Absence of functional electrical wiring and classroom fans")
    if f_boundary: selected_deficits.append("Lack of secure boundary wall / perimeter fencing creating hazardous conditions")
    if f_cwsn: selected_deficits.append("Absence of barrier-free ramp for Children With Special Needs (CWSN)")
    if f_mdm: selected_deficits.append("Absence of hygienic kitchen shed for PM POSHAN / Mid-Day Meal scheme")

    if not school_name or not udise_code or not district or not block:
        st.error("Please fill in the required institutional identifiers (marked with *).")
    elif not selected_deficits:
        st.warning("Please flag at least one infrastructure deficit to audit.")
    else:
        jurisdiction = JURISDICTION_REGISTRY[state]
        with st.spinner("Compiling statutory citations, precedent rulings, and RTI clauses via Flash engine..."):
            try:
                client = genai.Client()
                prompt = f"""
                You are a senior constitutional litigator and administrative law specialist in India. 
                Generate a formal, publication-grade, two-part statutory document based on the following verified field audit:

                AUDIT PARAMETERS:
                - Target Institution: {school_name}
                - UDISE Code: {udise_code}
                - Location: Block {block}, District {district}, State of {state}
                - Field Inspection Date: {audit_date}
                - Primary Nodal Authority: {jurisdiction['primary_officer']}
                - Appellate / District Authority: {jurisdiction['district_lead']}
                - State Department: {jurisdiction['state_dept']}
                - Applicable State Rules: {jurisdiction['rules_ref']}
                - Verified Deficits: {', '.join(selected_deficits)}
                - Additional Observations: {custom_notes if custom_notes else 'None noted during preliminary scan.'}

                FORMAT THE OUTPUT CLEANLY INTO TWO STANDALONE STATUTORY INSTRUMENTS:

                PART I: FORMAL STATUTORY CITIZEN GRIEVANCE UNDER RTE ACT, 2009
                1. Addressed to: The {jurisdiction['district_lead']} and The {jurisdiction['primary_officer']}.
                2. Subject: Formal Notice of Statutory Default regarding non-compliance with Section 19 read with the Schedule of the RTE Act, 2009 at {school_name} (UDISE: {udise_code}).
                3. Legal Grounding:
                   - Cite statutory non-compliance under Section 19(2) and Schedule specifications of the RTE Act, 2009.
                   - Cite Supreme Court precedent in Environmental & Consumer Protection Foundation v. Union of India & Ors. (2012) 10 SCC 197 (establishing that non-provision of basic sanitation and drinking water violates fundamental rights under Article 21A).
                   - State how this non-compliance triggers provisions under {jurisdiction['rules_ref']}.
                4. Formal Prayer for Relief:
                   - Immediate joint site verification within 7 working days.
                   - Administrative sanction of emergency repair and civil funds under Samagra Shiksha Composite School Grants.
                   - Written time-bound compliance order not exceeding 30 days.

                PART II: FORM 6(1) APPLICATION UNDER RIGHT TO INFORMATION ACT, 2005
                1. Addressed to: Public Information Officer (PIO), Office of the {jurisdiction['primary_officer']}, {district}.
                2. Specific Information Demanded under Section 6(1):
                   - Certified copies of annual civil maintenance, repair, and composite grants sanctioned to {school_name} (UDISE: {udise_code}) under Samagra Shiksha over the past 3 financial years.
                   - Certified copies of physical inspection notes and deficit compliance reports submitted by the Block Education Officer / Sub-Inspector of Schools for this school over the last 24 months.
                   - Certified records of contractors or agencies assigned civil maintenance work for toilets, drinking water, and boundary walls at this institution along with Utilization Certificates (UCs).
                
                Maintain an objective, rigorous, and legally binding tone. Do not include informal commentary.
                """

                # Target gemini-3.6-flash directly for high token allowance and fast execution
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                
                if not response or not response.text:
                    raise Exception("The generation engine returned an empty response.")

                dossier_content = response.text
                st.success("✅ Statutory Field Audit Dossier Generated!")

                st.text_area("Complete Statutory Instrument Preview", dossier_content, height=400)

                # Generate Official PDF Document
                pdf_bytes = build_pdf_dossier(school_name, udise_code, state, district, block, dossier_content)

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    st.download_button(
                        label="📄 Download Official Legal Action Pack (PDF)",
                        data=pdf_bytes,
                        file_name=f"OpenRTE_Dossier_{udise_code}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                with b_col2:
                    st.download_button(
                        label="📝 Download Text File (.txt)",
                        data=dossier_content,
                        file_name=f"OpenRTE_Dossier_{udise_code}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"Generation Error: {e}")