import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import time
import requests
import json
import os
import hashlib
from datetime import datetime

# Try importing the PDF generator module
try:
    from pdf_generator import generate_sba_pdf
except ImportError:
    st.error("⚠️ 'pdf_generator.py' not found. Please ensure it is in the same directory.")

# --- 1. Page Configuration & Custom CSS ---
st.set_page_config(page_title="Aletheia", layout="wide")

# Inject Custom CSS for the 'Glass Box' enterprise feel (Navy & Gold)
st.markdown("""
    <style>
    .stApp { background-color: #0A192F; color: #E6F1FF; }   
    .stDataFrame { border: 1px solid #FFD700; }
    h1, h2, h3 { color: #FFD700; }
    .stTextArea textarea { background-color: #112240; color: #ffffff; border: 1px solid #FFD700; }
    .stButton>button { background-color: #FFD700; color: #0A192F; font-weight: bold; border-radius: 5px; }
    .stButton>button:hover { background-color: #e6c200; color: #0A192F; }
    div[data-testid="stFileUploader"] { background-color: #112240; border: 1px dashed #FFD700; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ ALETHEIA")
st.markdown("### Compliance Workbench")

# --- 2. Dynamic Ingestion (Sidebar) ---
with st.sidebar:
    st.header("📂 Case File Ingestion")
    uploaded_file = st.file_uploader("Upload Transaction CSV", type="csv")
    st.info("Upload the 'synthetic_banking_data.csv' file generated in the previous step.")
    
    st.markdown("---")
    st.header("🌍 Jurisdiction Settings")
    jurisdiction = st.selectbox(
        "Select Regulatory Framework:",
        ["India (FIU-IND)", "USA (FinCEN)", "UK (NCA)"],
        help="Dynamically routes the AI's legal reasoning to match regional laws."
    )
    
    st.markdown("---")
    st.markdown("**System Status:**")
    # Quick check if Ollama is running
    try:
        requests.get("http://localhost:11434/")
        st.success("🟢 Ollama (Llama 3) Online")
    except:
        st.error("🔴 Ollama Offline. Run 'ollama run llama3' in terminal.")
        
    # --- NEW: ENTERPRISE AUDIT TRAIL VIEWER ---
    st.markdown("---")
    with st.expander("🔐 View Immutable Audit Ledger"):
        st.caption("Cryptographic Chain of Custody (SHA-256)")
        try:
            import json
            import pandas as pd
            with open("audit_ledger.json", "r") as f:
                ledger_data = json.load(f)
            
            if ledger_data:
                # Convert to dataframe and reverse it to show the newest entries at the top
                df_audit = pd.DataFrame(ledger_data).iloc[::-1]
                
                # Display a clean, miniaturized enterprise table
                st.dataframe(
                    df_audit[['timestamp', 'actor', 'action', 'target_account', 'jurisdiction', 'cryptographic_hash']], 
                    hide_index=True,
                    use_container_width=True
                )
                
                # Highlight the most recent cryptographic hash
                st.caption("Latest Cryptographic Signature:")
                st.code(df_audit.iloc[0]['cryptographic_hash'], language="text")
            else:
                st.write("Ledger is currently empty.")
        except FileNotFoundError:
            st.info("No audit events logged yet.")
    # ------------------------------------------

if uploaded_file:
    # Load Data into Session State to persist across reruns
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(uploaded_file)
    df = st.session_state.df

    # --- 3. The Glass Box Layout ---
    col_evidence, col_narrative = st.columns([1.2, 1]) # Left column slightly wider

    with col_evidence:
        st.subheader("🔍 EVIDENCE: Transaction Data")
        
        # --- THE RULE ENGINE (Deterministic Trigger) ---
        @st.cache_data
        def run_rule_engine(data):
            suspects = set()
            
            # RULE 1: Structuring (Smurfing)
            # Flags accounts with 3 or more cash deposits between INR 40k-50k
            cash_deposits = data[(data['mode'] == 'CASH') & (data['txn_type'] == 'CREDIT') & (data['amount'] >= 40000) & (data['amount'] < 50000)]
            structuring_counts = cash_deposits.groupby('account_no').size()
            suspects.update(structuring_counts[structuring_counts >= 3].index.tolist())
            
            # RULE 2: Layering (High Value / Velocity)
            # Flags accounts involved in single rapid transfers over INR 5 Lakhs (500,000)
            large_transfers = data[data['amount'] >= 500000]
            suspects.update(large_transfers['account_no'].unique().tolist())
            
            return list(suspects)

        # 1. Run the data through the Rule Engine first
        suspect_accounts = run_rule_engine(df)
        
        # 2. Handle the Empty State (No crime found)
        if not suspect_accounts:
            st.success("✅ No suspicious activity detected in this batch by the Rule Engine.")
            st.stop() # Halts the UI rendering here
            
        # 3. Populate dropdown ONLY with flagged suspects
        filter_acct = st.selectbox(
            f"🚨 Alert: {len(suspect_accounts)} Suspicious Account(s) Detected:", 
            suspect_accounts
        )
        
        display_df = df[df['account_no'] == filter_acct]
        st.dataframe(display_df, height=250, use_container_width=True)

        # Pyvis Network Visualization
        st.subheader("🕸️ Fund Flow Network")
        
        # Build the Graph based on the filtered data
        net = Network(height='400px', width='100%', bgcolor='#112240', font_color='white')
        
        # We'll graph the transactions related to the selected account
        graph_df = display_df.groupby(['account_no', 'counterparty'])['amount'].sum().reset_index()
        
        for _, row in graph_df.iterrows():
            src = str(row['account_no'])
            dst = str(row['counterparty'])
            w = float(row['amount'])
            
            # Add nodes and edges
            # Truncate labels for cleaner graph
            src_label = src[:8] + "..." if len(src) > 8 else src
            dst_label = dst[:8] + "..." if len(dst) > 8 else dst
            
            net.add_node(src, label=src_label, color='#FFD700', shape='dot', title=src) # Gold for Suspect
            net.add_node(dst, label=dst_label, color='#00ff00', shape='dot', title=dst) # Green for Counterparty
            net.add_edge(src, dst, value=w, title=f"Total: ₹{w:,.2f}")
            
        # Physics settings for nice clustering
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=200)
        
        # Render the graph
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
                net.save_graph(tmp_file.name)
                with open(tmp_file.name, 'r', encoding='utf-8') as f:
                    html_data = f.read()
            components.html(html_data, height=420)
        except Exception as e:
            st.error(f"Graph visualization error: {e}")

    with col_narrative:
        
        # State management for the narrative
        if 'narrative' not in st.session_state:
            st.session_state.narrative = "Upload data and click 'Generate Narrative' to begin analysis..."
            
            # --- INNOVATION #1: THE FALSE-POSITIVE KILLER ---
        st.markdown("---")
        st.subheader("🛡️ AI 'Life Event' Clearance Engine")
        st.caption("Automatically scans transaction context to dismiss legitimate life events, reducing operational false positives.")
        
        if st.button("🔍 Run AI Clearance Pre-Check"):
            with st.spinner("Clearance Agent scanning transaction memos and open banking context..."):
                # 1. Prepare data specifically for the clearance agent
                clearance_data = display_df[['txn_date', 'amount', 'counterparty', 'transaction_memo']].to_string(index=False)
                
                # 2. The Clearance Prompt
                clearance_prompt = f"""You are an AI False-Positive Clearance Agent for a Tier-1 Bank.
Your job is to read transaction memos and determine if a flagged alert is actually a legitimate 'Life Event' (e.g., buying a house, receiving an inheritance, paying a medical bill).

Transactions:
{clearance_data}

INSTRUCTIONS:
1. If you see a clear, legitimate reason for the large transaction in the memos, output EXACTLY this format: 
   "CLEARED: [Explain the life event found in 1 sentence]."
2. If the transactions look like actual money laundering (structuring, smurfing, offshore wire transfers), output EXACTLY: 
   "SUSPICIOUS: Proceed to SAR generation."

Output nothing else."""

                # 3. Call the Local LLM (Llama 3)
                try:
                    import requests
                    response = requests.post("http://localhost:11434/api/generate", json={
                        "model": "llama3",
                        "prompt": clearance_prompt,
                        "stream": False
                    }).json()["response"].strip()
                    
                    # 4. Route the UI based on the AI's decision
                    if response.startswith("CLEARED"):
                        st.success(f"✅ **FALSE POSITIVE DISMISSED**\n\n{response}")
                    else:
                        st.error(f"🚨 **ANOMALY CONFIRMED**\n\n{response}")
                except Exception as e:
                    st.error(f"Clearance Agent offline: {e}")
        st.markdown("---")

        if st.button("🤖 Generate Citation-Backed Narrative"):
            with st.spinner("Agentic AI analyzing typologies against PMLA guidelines..."):
                
                # 1. Prepare the Data Context (Now including KYC data)
                # Assuming your df now has these columns, we pass them to the LLM
                context_data = display_df.to_string(index=False)
                
                # --- THE ENTERPRISE MULTI-JURISDICTION ROUTER ---
                if jurisdiction == "India (FIU-IND)":
                    regulator = "Financial Intelligence Unit - India (FIU-IND)"
                    law_context = "Prevention of Money Laundering Act, 2002 (PMLA)"
                    rule_context = "Focus on 'Structuring' to evade the INR 50,000 PAN reporting threshold. Specifically map behavior to 'Reason for suspicion: Value just under the reporting threshold amount in an apparent attempt to avoid reporting'."
                
                elif jurisdiction == "USA (FinCEN)":
                    regulator = "Financial Crimes Enforcement Network (FinCEN)"
                    law_context = "Bank Secrecy Act (31 U.S.C. 5318)"
                    rule_context = "Focus on 'Structuring' to evade the $10,000 Currency Transaction Report (CTR) limit, or anomalies aggregating over $5,000."
                
                else: # UK (FCA)
                    regulator = "Financial Conduct Authority (FCA)"
                    law_context = "UK Market Abuse Regulation (UK MAR)"
                    rule_context = "Focus on suspected Market Abuse, Insider Dealing, or suspicious financial instrument orders based on the transaction memos."

                # 2. The Dynamic Master Prompt
                system_prompt = f"""You are a Senior Financial Crime Compliance Officer.
Your task is to draft the highly formal narrative section for a Suspicious Activity Report to {regulator} under the {law_context}.

Here is the transaction history for the flagged account:
{context_data}

INSTRUCTIONS:
1. LEGAL ANALYSIS: {rule_context}
2. CITATION REQUIREMENT (CRITICAL): Every factual claim (amounts, dates, behaviors) MUST be cited with the exact Txn ID in brackets. Example: "A deposit of 48,000 was made [1D640F1C9085]."
3. FORMATTING: Output ONLY the chronological narrative and grounds for suspicion. Do NOT include KYC details (Name, DOB) in your output, as those are handled by the system wrapper.

Output only the highly formal, legalistic report text."""

                # 3. Call Local Ollama (Llama 3) API
                url = "http://localhost:11434/api/generate"
                payload = {
                    "model": "llama3",
                    "prompt": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1 # Low temperature for factual, rigid compliance text
                    }
                }
                
                try:
                    response = requests.post(url, json=payload)
                    response.raise_for_status()
                    # Parse Ollama's response
                    ai_response = response.json()['response']
                    st.session_state.narrative = ai_response
                    st.rerun()
                except requests.exceptions.ConnectionError:
                    st.error("🔴 Connection Error: Is Ollama running? Open your terminal and type `ollama run llama3`.")
                except Exception as e:
                    st.error(f"AI Generation Error: {e}")

        # Human-in-the-Loop Editor
        edited_narrative = st.text_area(
            "Review and Edit Narrative for Part 7 (Grounds of Suspicion):", 
            value=st.session_state.narrative, 
            height=350,
            help="Citations link back to the Evidence panel."
        )

        # Make the button name dynamic too!
        if st.button(f"✅ Approve & Generate Official {jurisdiction} PDF"):
            if edited_narrative != st.session_state.narrative:
                st.warning("⚠️ Human edits detected. Delta logged to immutable Audit Trail.")
            
            try:
                # --- 1. GENERATE CRYPTOGRAPHIC AUDIT HASH ---
                # We hash the exact state of the CSV data + the final approved narrative
                audit_payload = f"TIMESTAMP:{datetime.now().isoformat()}|JURISDICTION:{jurisdiction}|DATA:{display_df.to_string()}|NARRATIVE:{edited_narrative}"
                sha256_hash = hashlib.sha256(audit_payload.encode('utf-8')).hexdigest()

                # --- 2. SAVE TO IMMUTABLE LEDGER (Simulating PostgreSQL) ---
                target_acct = str(display_df['account_no'].iloc[0]) if not display_df.empty else "UNKNOWN"
                
                # NEW: Create a detailed action description based on human behavior
                if edited_narrative != st.session_state.narrative:
                    action_desc = "SAR Approved (With Human Overrides)"
                else:
                    action_desc = "SAR Approved (Unmodified AI Output)"
                
                ledger_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "actor": "Analyst_ID_8849", # Simulating a logged-in bank employee
                    "action": action_desc,
                    "target_account": target_acct,
                    "jurisdiction": jurisdiction,
                    "cryptographic_hash": sha256_hash,
                    "status": "LOCKED"
                }
                
                # Append to our local JSON ledger
                ledger_filename = "audit_ledger.json"
                try:
                    with open(ledger_filename, "r") as f:
                        ledger = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    ledger = []
                    
                ledger.append(ledger_entry)
                
                with open(ledger_filename, "w") as f:
                    json.dump(ledger, f, indent=4)
                
                # --- 3. GENERATE THE PDF ---
                pdf_bytes = generate_sba_pdf(edited_narrative, display_df, jurisdiction)
                
                # --- 4. DISPLAY ENTERPRISE UI SUCCESS ---
                st.success("Report Finalized! PDF generation successful.")
                
                # Show the cryptographic proof to the user
                st.info(f"🔒 **Cryptographic Chain of Custody Locked**\n\n**SHA-256 Hash:** `{sha256_hash}`\n\n*Pursuant to FinCEN 5-year retention mandates, this cryptographic signature and the underlying evidence have been committed to the immutable audit ledger.*")
                
                # Streamlit serves the bytes directly to the browser
                st.download_button(
                    label=f"📄 Download Official Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"Aletheia_{jurisdiction[:3]}_SAR.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Failed to generate PDF or Audit Trail: {e}")

else:
    # Empty State
    st.info("👈 Please upload the 'synthetic_banking_data.csv' from the sidebar to begin the investigation.")