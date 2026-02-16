from fpdf import FPDF
import pandas as pd
from datetime import datetime
import tempfile
import os

class SBAPDF(FPDF):
    def header(self):
        # Official FIU-IND Header mimicking the real document
        self.set_font('Arial', 'B', 14)
        self.cell(0, 6, 'FIU-IND', 0, 1, 'L')
        self.set_font('Arial', 'B', 12)
        self.cell(0, 6, 'Financial Intelligence Unit- India', 0, 1, 'L')
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, 'SUSPICIOUS TRANSACTION REPORT (STR) FOR A BANKING COMPANY', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, 4, 'Kindly fill in CAPITAL. Read the instructions before filling the form.', 0, 1, 'L')
        self.line(10, 36, 200, 36)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 8)
        self.cell(0, 10, 'DO NOT FILL. FOR FIU-IND USE ONLY.', 0, 0, 'L')
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')

    def draw_section_header(self, part_num, title):
        self.ln(4)
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.cell(20, 6, part_num, 1, 0, 'C', fill=True)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, f" {title}", 1, 1, 'L', fill=True)

    def draw_checkbox(self, x, y, checked=False):
        """Draws a physical square checkbox"""
        self.rect(x, y, 4, 4)
        if checked:
            self.set_font('Arial', 'B', 10)
            self.text(x + 0.5, y + 3.5, 'X')

def generate_sba_pdf(narrative, df):
    # --- THE FIX: SANITIZE LLM ARTIFACTS ---
    safe_narrative = (narrative
        .replace('₹', 'INR ')
        .replace('**', '')       # Remove markdown bold
        .replace('•', '-')       # Replace bullet points with hyphens
        .replace('“', '"')       # Replace smart quotes
        .replace('”', '"')
        .replace('‘', "'")
        .replace('’', "'")
        .replace('—', '-')       # Replace em dash
        .replace('–', '-')       # Replace en dash
    )
    
    pdf = SBAPDF()
    pdf.add_page()

    # --- PART 1: DETAILS OF REPORT ---
    pdf.draw_section_header("PART 1", "DETAILS OF REPORT")
    pdf.set_font('Arial', '', 9)
    pdf.cell(80, 8, "1.1 Date of sending report:", 'L,T,B')
    pdf.set_font('Courier', 'B', 10)
    pdf.cell(0, 8, datetime.now().strftime("%d-%m-%Y"), 'R,T,B', 1)
    
    pdf.set_font('Arial', '', 9)
    pdf.cell(80, 8, "1.2 Is this a replacement to an earlier report?", 'L,B')
    # Draw NO checkbox
    pdf.draw_checkbox(100, pdf.get_y() + 2, checked=True)
    pdf.text(106, pdf.get_y() + 5, "NO")
    # Draw YES checkbox
    pdf.draw_checkbox(120, pdf.get_y() + 2, checked=False)
    pdf.text(126, pdf.get_y() + 5, "YES")
    pdf.cell(0, 8, "", 'R,B', 1)

    # --- PART 2: DETAILS OF PRINCIPAL OFFICER ---
    pdf.draw_section_header("PART 2", "DETAILS OF PRINCIPAL OFFICER")
    pdf.set_font('Arial', '', 9)
    
    # Grid Layout for Bank Details
    pdf.cell(50, 6, "2.1 Name of Bank", 1)
    pdf.set_font('Courier', 'B', 9)
    pdf.cell(0, 6, "ALETHEIA BANK LTD", 1, 1)
    
    pdf.set_font('Arial', '', 9)
    pdf.cell(50, 6, "2.3 ID allotted by FIU-IND", 1)
    pdf.set_font('Courier', 'B', 9)
    pdf.cell(50, 6, "FIU-IND-9999", 1)
    pdf.set_font('Arial', '', 9)
    pdf.cell(40, 6, "2.4 Category of bank", 1)
    pdf.set_font('Courier', 'B', 9)
    pdf.cell(0, 6, "A", 1, 1) # 'A' represents Public Sector Bank in SBA
    
    pdf.set_font('Arial', '', 9)
    pdf.cell(50, 6, "2.5 Name of principal officer", 1)
    pdf.set_font('Courier', 'B', 9)
    pdf.cell(0, 6, "RAJESH KUMAR", 1, 1)

    # --- PART 6: LIST OF ACCOUNTS ---
    pdf.draw_section_header("PART 6", "LIST OF ACCOUNTS LINKED TO TRANSACTIONS")
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(10, 6, "S.N.", 1, 0, 'C')
    pdf.cell(90, 6, "Account Number", 1, 0, 'C')
    pdf.cell(90, 6, "Annexure", 1, 1, 'C')
    
    pdf.set_font('Courier', '', 9)
    unique_accounts = df['account_no'].unique()
    for idx, acc in enumerate(unique_accounts):
        pdf.cell(10, 6, f"6.{idx+1}", 1, 0, 'C')
        pdf.cell(90, 6, str(acc), 1, 0, 'C')
        pdf.cell(90, 6, f"C{idx+1}", 1, 1, 'C')

    # --- PART 7: DETAILS OF SUSPICIOUS TRANSACTION ---
    pdf.draw_section_header("PART 7", "DETAILS OF SUSPICIOUS TRANSACTION")
    
    # 7.1 CHECKBOXES (Mimicking Page 3 of the real form)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 6, "7.1 Reasons for suspicion (Tick as applicable):", 'L,T,R', 1)
    
    pdf.set_font('Arial', '', 9)
    current_y = pdf.get_y()
    
    # Left Column
    pdf.draw_checkbox(15, current_y + 1, checked=False)
    pdf.text(22, current_y + 4, "A   Identity of client")
    pdf.draw_checkbox(15, current_y + 7, checked=False)
    pdf.text(22, current_y + 10, "B   Background of client")
    pdf.draw_checkbox(15, current_y + 13, checked=False)
    pdf.text(22, current_y + 16, "C   Multiple accounts")
    
    # Right Column
    pdf.draw_checkbox(100, current_y + 1, checked=False)
    pdf.text(107, current_y + 4, "D   Activity in account")
    pdf.draw_checkbox(100, current_y + 7, checked=False)
    pdf.text(107, current_y + 10, "E   Nature of transaction")
    
    # MARKING 'F' AS THE DETECTED CRIME
    pdf.draw_checkbox(100, current_y + 13, checked=True) 
    pdf.text(107, current_y + 16, "F   Value of transaction")
    
    pdf.cell(0, 20, "", 'L,R,B', 1) # Advance Y-axis past the checkboxes
    
    # 7.2 THE NARRATIVE BOX (Mimicking Page 3/4 of the real form)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 6, "7.2 Grounds of Suspicion (Mention summary of suspicion and sequence of events):", 'L,T,R', 1)
    
    pdf.set_font('Times', '', 10)
    # Draw a large rectangle for the narrative box
    x = pdf.get_x()
    y = pdf.get_y()
    pdf.rect(x, y, 190, 80) # 190 width, 80 height
    
    pdf.set_xy(x + 2, y + 2) # Padding inside the box
    pdf.multi_cell(186, 5, safe_narrative)
    
    pdf.set_xy(x, y + 80) # Move past the narrative box

    # --- ANNEXURE C: TRANSACTION LOG ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "ANNEXURE C: LIST OF ACCOUNTS LINKED TO TRANSACTIONS", 0, 1, 'C')
    pdf.ln(2)
    
    # Table Header
    pdf.set_font('Arial', 'B', 8)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(20, 6, "Date", 1, 0, 'C', fill=True)
    pdf.cell(20, 6, "Type", 1, 0, 'C', fill=True)
    pdf.cell(20, 6, "Mode", 1, 0, 'C', fill=True)
    pdf.cell(30, 6, "Amount (INR)", 1, 0, 'C', fill=True)
    pdf.cell(60, 6, "Counterparty", 1, 0, 'C', fill=True)
    pdf.cell(40, 6, "Txn ID", 1, 1, 'C', fill=True)
    
    # Table Body
    pdf.set_font('Courier', '', 8)
    for _, row in df.iterrows():
        amount_str = str(row['amount']).replace('₹', '')
        pdf.cell(20, 6, str(row['txn_date'])[:10], 1)
        pdf.cell(20, 6, str(row['txn_type']), 1)
        pdf.cell(20, 6, str(row['mode']), 1)
        pdf.cell(30, 6, amount_str, 1, 0, 'R')
        pdf.cell(60, 6, str(row['counterparty'])[:28], 1)
        pdf.cell(40, 6, str(row['txn_id']), 1, 1)

    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, "FIU_IND_SBA_Report.pdf")
    pdf.output(filepath)
    return filepath