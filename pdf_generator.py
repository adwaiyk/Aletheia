from fpdf import FPDF
import pandas as pd
from datetime import datetime
import tempfile
import os

class SBAPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'FIU-IND: SUSPICIOUS TRANSACTION REPORT (STR) FOR A BANKING COMPANY', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_section_title(self, title):
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(220, 220, 220) 
        self.cell(0, 7, title, 1, 1, 'L', fill=True)

    def add_field_pair(self, label1, value1, label2, value2):
        self.set_font('Arial', 'B', 9)
        self.cell(45, 6, label1, 1)
        self.set_font('Courier', '', 9)
        # Ensure values are sanitized strings
        self.cell(50, 6, str(value1).replace('₹', 'INR '), 1)
        
        self.set_font('Arial', 'B', 9)
        self.cell(45, 6, label2, 1)
        self.set_font('Courier', '', 9)
        self.cell(50, 6, str(value2).replace('₹', 'INR '), 1, 1)

    def add_full_width_field(self, label, value):
        self.set_font('Arial', 'B', 9)
        self.cell(50, 6, label, 1)
        self.set_font('Courier', '', 9)
        self.cell(0, 6, str(value).replace('₹', 'INR '), 1, 1)

def generate_sba_pdf(narrative, df):
    # --- THE FIX: SANITIZE THE INPUT TEXT ---
    # Replace the Rupee symbol with 'INR' to prevent font errors
    safe_narrative = narrative.replace('₹', 'INR ').replace('**', '') 
    
    pdf = SBAPDF()
    pdf.add_page()

    # --- PART 1: DETAILS OF REPORT ---
    pdf.add_section_title("PART 1: DETAILS OF REPORT")
    pdf.add_field_pair(
        "1.1 Date of Report:", datetime.now().strftime("%d-%m-%Y"),
        "1.2 Replacement?", "NO"
    )

    # --- PART 2: DETAILS OF PRINCIPAL OFFICER ---
    pdf.ln(2)
    pdf.add_section_title("PART 2: DETAILS OF PRINCIPAL OFFICER")
    pdf.add_full_width_field("2.1 Name of Bank:", "ALETHEIA BANK LTD")
    pdf.add_field_pair(
        "2.5 Name:", "Rajesh Kumar",
        "2.6 Designation:", "Principal Officer"
    )
    pdf.add_full_width_field("2.7 Address:", "123, Financial District, Mumbai - 400051")
    pdf.add_field_pair(
        "2.3 FIU ID:", "FIU-IND-9999",
        "2.4 Category:", "A - Public Sector"
    )

    # --- PART 6: LIST OF ACCOUNTS ---
    pdf.ln(5)
    pdf.add_section_title("PART 6: LIST OF ACCOUNTS LINKED TO TRANSACTIONS")
    unique_accounts = df['account_no'].unique()
    for acc in unique_accounts:
        pdf.add_field_pair(
            "Account Number:", acc,
            "Annexure Ref:", "C1"
        )

    # --- PART 7: DETAILS OF SUSPICIOUS TRANSACTION ---
    pdf.ln(5)
    pdf.add_section_title("PART 7: DETAILS OF SUSPICIOUS TRANSACTION")
    
    pdf.add_full_width_field("7.1 Reason for Suspicion:", "F - Value of transaction (Structuring/Layering)")
    
    # 7.2 Grounds of Suspicion (The Narrative)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, "7.2 Grounds of Suspicion (Narrative):", 0, 1)
    
    pdf.set_font('Times', '', 10)
    pdf.multi_cell(0, 5, safe_narrative) # Using the sanitized text

    # --- PART 8: ACTION TAKEN ---
    pdf.ln(5)
    pdf.add_section_title("PART 8: DETAILS OF ACTION TAKEN")
    pdf.add_full_width_field("8.1 Investigation Status:", "Internal Investigation Completed. Account Freeze Initiated.")

    # --- ANNEXURE C: ACCOUNT & TRANSACTION DETAILS ---
    pdf.add_page()
    pdf.add_section_title("ANNEXURE C: DETAILED TRANSACTION LOG")
    
    # Table Header
    pdf.set_font('Arial', 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(25, 6, "Date", 1, 0, 'C', fill=True)
    pdf.cell(20, 6, "Type", 1, 0, 'C', fill=True)
    pdf.cell(20, 6, "Mode", 1, 0, 'C', fill=True)
    pdf.cell(30, 6, "Amount (INR)", 1, 0, 'C', fill=True)
    pdf.cell(45, 6, "Counterparty", 1, 0, 'C', fill=True)
    pdf.cell(50, 6, "Txn ID", 1, 1, 'C', fill=True)
    
    # Table Body
    pdf.set_font('Courier', '', 8)
    for _, row in df.iterrows():
        # Sanitize data inside the table loop too!
        amount_str = str(row['amount']).replace('₹', '')
        
        pdf.cell(25, 6, str(row['txn_date']), 1)
        pdf.cell(20, 6, str(row['txn_type']), 1)
        pdf.cell(20, 6, str(row['mode']), 1)
        pdf.cell(30, 6, amount_str, 1, 0, 'R')
        pdf.cell(45, 6, str(row['counterparty'])[:20], 1)
        pdf.cell(50, 6, str(row['txn_id']), 1, 1)

    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, "FIU_IND_SBA_Report.pdf")
    pdf.output(filepath)
    return filepath