import os
import tempfile
from fpdf import FPDF
from datetime import datetime

class OfficialSAR(FPDF):
    def __init__(self, jurisdiction):
        super().__init__()
        self.jurisdiction = jurisdiction
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Draw the EXACT headers
        if self.jurisdiction == "USA (FinCEN)":
            self.set_font("Arial", "B", 16)
            self.cell(0, 8, "Suspicious Activity Report", ln=True, align="C")
            self.set_font("Arial", "", 10)
            self.cell(0, 5, "FRB: FR 2230 | OMB No. 7100-0212 | FDIC: 6710/06 | TREASURY: TD F 90-22.47", ln=True, align="C")
            self.set_font("Arial", "I", 9)
            self.cell(0, 5, "ALWAYS COMPLETE ENTIRE REPORT", ln=True, align="C")
            
        elif self.jurisdiction == "UK (NCA)":
            self.set_font("Arial", "B", 16)
            self.cell(0, 8, "Financial Conduct Authority (FCA)", ln=True, align="C")
            self.set_font("Arial", "B", 12)
            self.cell(0, 6, "Suspicious Transaction Reporting Form", ln=True, align="C")
            self.set_font("Arial", "I", 9)
            self.cell(0, 5, "Please note this form is for the use of PRA and FCA Authorised firms only.", ln=True, align="C")
            
        else: # India (FIU-IND)
            self.set_font("Arial", "B", 16)
            self.cell(0, 8, "FIU-IND", ln=True, align="C")
            self.set_font("Arial", "B", 12)
            self.cell(0, 6, "Financial Intelligence Unit - India", ln=True, align="C")
            self.set_font("Arial", "B", 10)
            self.cell(0, 6, "SUSPICIOUS TRANSACTION REPORT (STR) FOR A BANKING COMPANY", ln=True, align="C")
            
        self.ln(6)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"CONFIDENTIAL | Aletheia AI Generation | Page {self.page_no()}", 0, 0, "C")

    def draw_section_header(self, title, is_dark=True):
        self.ln(2)
        self.set_font("Arial", "B", 10)
        if is_dark:
            self.set_fill_color(10, 25, 47) # Navy Blue
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(230, 230, 230) # Light Gray
            self.set_text_color(0, 0, 0)
        
        self.cell(190, 8, f"  {title}", ln=True, fill=True)
        self.set_text_color(0, 0, 0) # Reset to black
        self.ln(1)

    def draw_row(self, fields):
        """
        The Enterprise Grid System.
        Fields must be a list of tuples: (label, value, width)
        Total width should ideally sum up to ~190 for a full page width.
        """
        start_x = self.get_x()
        start_y = self.get_y()
        row_height = 11

        # Check if we need a page break before drawing the row
        if start_y + row_height > 270: 
            self.add_page()
            start_x = self.get_x()
            start_y = self.get_y()

        for label, value, width in fields:
            # Clean up value encoding to prevent PDF crash on weird characters
            clean_val = str(value).encode('latin-1', 'replace').decode('latin-1')
            
            # 1. Draw the Label (Top half of the box)
            self.set_xy(start_x, start_y)
            self.set_font("Arial", "B", 7)
            self.set_text_color(100, 100, 100)
            self.cell(width, 4, f" {label}", border="LTR", align="L")
            
            # 2. Draw the Value (Bottom half of the box)
            self.set_xy(start_x, start_y + 4)
            self.set_font("Arial", "", 10)
            self.set_text_color(0, 0, 0)
            self.cell(width, 7, f" {clean_val}", border="LBR", align="L")
            
            # 3. Move X to the right for the next box in the row
            start_x += width

        # 4. Move Y down below the completed row
        self.set_xy(10, start_y + row_height)


def generate_sba_pdf(narrative, df, jurisdiction="India (FIU-IND)"):
    # Sanitize LLM artifacts
    safe_narrative = narrative.replace('₹', 'INR ').replace('**', '').replace('•', '-').replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    
    suspect = df.iloc[0] if not df.empty else None
    
    # Extract data safely
    s_name = suspect['customer_name'] if suspect is not None else "UNKNOWN"
    s_first = s_name.split()[0] if s_name != "UNKNOWN" else ""
    s_last = s_name.split()[-1] if s_name != "UNKNOWN" else ""
    s_dob = suspect['dob'] if suspect is not None else "UNKNOWN"
    s_tax = suspect['tax_id'] if suspect is not None else "UNKNOWN"
    s_addr = suspect['address'] if suspect is not None else "UNKNOWN"
    s_acct = suspect['account_no'] if suspect is not None else "UNKNOWN"

    pdf = OfficialSAR(jurisdiction)
    pdf.add_page()
    
    if jurisdiction == "USA (FinCEN)":
        pdf.draw_section_header("Part I   Reporting Financial Institution Information")
        pdf.draw_row([
            ("2 Name of Financial Institution", "Barclays Bank PLC (US Branch)", 100),
            ("3 EIN", "12-3456789", 90)
        ])
        pdf.draw_row([
            ("4 Address of Financial Institution", "745 7th Avenue", 100),
            ("6 City", "New York", 40),
            ("7 State", "NY", 20),
            ("8 Zip Code", "10019", 30)
        ])
        
        pdf.draw_section_header("Part II  Suspect Information")
        pdf.draw_row([
            ("15 Last Name or Name of Entity", s_last, 95),
            ("16 First Name", s_first, 95)
        ])
        pdf.draw_row([
            ("19 SSN, EIN or TIN", s_tax, 95),
            ("27 Date of Birth", s_dob, 95)
        ])
        pdf.draw_row([
            ("18 Address", s_addr, 130),
            ("14 Account number(s)", s_acct, 60)
        ])
        
        pdf.draw_section_header("Part V   Suspicious Activity Information Explanation/Description")

    elif jurisdiction == "UK (NCA)":
        pdf.draw_section_header("Identities of persons carrying out transaction(s)", is_dark=False)
        pdf.draw_row([
            ("Name of Subject", s_name, 95),
            ("Date of Birth", s_dob, 45),
            ("Account Number", s_acct, 50)
        ])
        pdf.draw_row([
            ("Registered Address", s_addr, 190)
        ])
        
        pdf.draw_section_header("Reasons for suspecting that the transaction(s) might constitute insider dealing", is_dark=False)

    else:
        pdf.draw_section_header("PART 1   DETAILS OF REPORT")
        pdf.draw_row([
            ("1.1 Date of sending report", datetime.now().strftime("%d-%m-%Y"), 95),
            ("1.2 Is this a replacement to an earlier report?", "NO", 95)
        ])
        
        pdf.draw_section_header("PART 4   LIST OF INDIVIDUALS LINKED TO TRANSACTIONS")
        pdf.draw_row([
            ("Name of individual", s_name, 95),
            ("Customer ID/number (PAN)", s_tax, 95)
        ])
        pdf.draw_row([
            ("Address", s_addr, 190)
        ])
        
        pdf.draw_section_header("PART 6   LIST OF ACCOUNTS LINKED TO TRANSACTIONS")
        pdf.draw_row([
            ("Account Number", s_acct, 190)
        ])
        
        pdf.draw_section_header("PART 7   DETAILS OF SUSPICIOUS TRANSACTION")
    
    # Write the AI Narrative with professional legal formatting
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)
    # Using 'J' aligns both the left and right margins of the text like a newspaper/legal doc
    pdf.multi_cell(0, 7, safe_narrative.encode('latin-1', 'replace').decode('latin-1'), align='J')

    # Return Bytes (Memory Safe)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp.seek(0)
        pdf_bytes = tmp.read()
        
    os.unlink(tmp.name) 
    
    return pdf_bytes