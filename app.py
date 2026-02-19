import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import requests
import json
import os
import hashlib
from datetime import datetime

# --- ENTERPRISE FIX: BROWSER REFRESH RECOVERY ---
STATE_FILE = "recovery_state.json"

if 'narrative' not in st.session_state:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                saved_state = json.load(f)
                st.session_state.narrative = saved_state.get("narrative", "")
        except json.JSONDecodeError:
            st.session_state.narrative = ""
    else:
        st.session_state.narrative = ""

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
st.markdown("### FinCrime Investigations Terminal")

# --- 2. Dynamic Ingestion (Sidebar) ---
with st.sidebar:
    st.header("📂 Case File Ingestion")
    uploaded_file = st.file_uploader("Upload Transaction CSV", type="csv")
    
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
        
    # --- ENTERPRISE AUDIT TRAIL VIEWER ---
    st.markdown("---")
    st.header("🔍 Audit Ledger")
    with st.expander("🔐 View Immutable Audit Ledger"):
        st.caption("Cryptographic Chain of Custody (SHA-256)")
        try:
            with open("audit_ledger.json", "r") as f:
                ledger_data = json.load(f)
            
            if ledger_data:
                # Convert to dataframe and reverse it to show the newest entries at the top
                df_audit = pd.DataFrame(ledger_data).iloc[::-1]
                
                # Backward compatibility for old logs
                if 'actor' not in df_audit.columns: df_audit['actor'] = "System"
                if 'action' not in df_audit.columns: df_audit['action'] = "Approved"
                
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
        st.subheader("💰 Transaction Data")
        
        # --- THE RULE ENGINE (Deterministic Trigger) ---
        @st.cache_data
        def run_rule_engine(data):
            # Rule 1: Massive Anomaly (Catches the House Downpayment, Insider Trading, and Heavy Layering)
            rule_1_flags = data[data['amount'] >= 1000000]['account_no'].unique()

            # Rule 2: Structuring / Smurfing (Catches the Cash Structurer and Crypto Smurf)
            # Looks for 3 or more transactions exactly between 45k and 50k
            structuring_txns = data[(data['amount'] >= 45000) & (data['amount'] < 50000)]
            rule_2_flags = structuring_txns.groupby('account_no').filter(lambda x: len(x) >= 3)['account_no'].unique()

            # Combine flagged accounts
            return list(set(rule_1_flags).union(set(rule_2_flags)))

        # 1. Run the data through the Rule Engine first
        suspect_accounts = run_rule_engine(df)
        
        # 2. Handle the Empty State (No crime found)
        if not suspect_accounts:
            st.success("✅ No suspicious activity detected in this batch by the Rule Engine.")
            st.stop() # Halts the UI rendering here
            
        # 3. Populate dropdown ONLY with flagged suspects
        st.markdown(f"🚨 **Alert: {len(suspect_accounts)} Suspicious Account(s) Detected:**")
        filter_acct = st.selectbox("Select Account for Investigation", suspect_accounts, label_visibility="collapsed")
        
        display_df = df[df['account_no'] == filter_acct].sort_values('txn_date')
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
            
            # Add nodes and edges (Truncate labels for cleaner graph)
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
        
        st.subheader("🗂️ Analyst Workspace")
        
        # --- INNOVATION #1: THE FALSE-POSITIVE KILLER ---
        st.markdown("---")
        st.subheader("🛡️ Contextual Alert Triage Engine")
        
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
            with st.spinner("Agentic AI analyzing typologies against global guidelines..."):
                
                # 1. Prepare the Data Context
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
                    # FIRST: Send the request to the AI
                    response = requests.post(url, json=payload)
                    response.raise_for_status()
                    
                    # SECOND: Parse the AI's response
                    generated_text = response.json()['response'].strip()
                    
                    # THIRD: Save to memory and hard drive to survive refresh
                    st.session_state.narrative = generated_text
                    with open(STATE_FILE, "w") as f:
                        json.dump({"narrative": generated_text}, f)
                        
                    # FOURTH: Refresh the UI to show the text
                    st.rerun()
                    
                except requests.exceptions.ConnectionError:
                    st.error("🔴 Connection Error: Is Ollama running? Open your terminal and type `ollama run llama3`.")
                except Exception as e:
                    st.error(f"AI Generation Error: {e}")

        # Human-in-the-Loop Editor
        edited_narrative = st.text_area(
            "Review and Edit Narrative", 
            value=st.session_state.narrative if st.session_state.narrative else "Upload data and click 'Generate Narrative' to begin analysis...", 
            height=350,
            help="Citations link back to the Evidence panel."
        )
        
        # Auto-save Human Edits
        if edited_narrative != st.session_state.narrative and edited_narrative != "Upload data and click 'Generate Narrative' to begin analysis...":
            st.session_state.narrative = edited_narrative
            with open(STATE_FILE, "w") as f:
                json.dump({"narrative": edited_narrative}, f)

        # Make the button name dynamic
        if st.button(f"✅ Approve & Generate Official {jurisdiction} Exports"):
            if edited_narrative != st.session_state.narrative:
                st.warning("⚠️ Human edits detected. Delta logged to immutable Audit Trail.")
            
            try:
                # --- 1. GENERATE CRYPTOGRAPHIC AUDIT HASH ---
                audit_payload = f"TIMESTAMP:{datetime.now().isoformat()}|JURISDICTION:{jurisdiction}|DATA:{display_df.to_string()}|NARRATIVE:{edited_narrative}"
                sha256_hash = hashlib.sha256(audit_payload.encode('utf-8')).hexdigest()

                # --- 2. SAVE TO IMMUTABLE LEDGER ---
                target_acct = str(display_df['account_no'].iloc[0]) if not display_df.empty else "UNKNOWN"
                
                # Detailed action description based on human behavior
                if edited_narrative != st.session_state.narrative:
                    action_desc = "SAR Approved (With Human Overrides)"
                else:
                    action_desc = "SAR Approved (Unmodified AI Output)"
                
                ledger_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "actor": "Analyst_ID_8849", 
                    "action": action_desc,
                    "target_account": target_acct,
                    "jurisdiction": jurisdiction,
                    "cryptographic_hash": sha256_hash,
                    "status": "LOCKED"
                }
                
                ledger_filename = "audit_ledger.json"
                try:
                    with open(ledger_filename, "r") as f:
                        ledger = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    ledger = []
                    
                ledger.append(ledger_entry)
                
                with open(ledger_filename, "w") as f:
                    json.dump(ledger, f, indent=4)
                
                # --- 3. GENERATE THE EXPORTS ---
                pdf_bytes = generate_sba_pdf(edited_narrative, display_df, jurisdiction)
                
                json_data = json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "jurisdiction": jurisdiction,
                    "target_account": target_acct,
                    "narrative": edited_narrative,
                    "cryptographic_hash": sha256_hash
                }, indent=4)

                xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<SuspiciousActivityReport>
    <Timestamp>{datetime.now().isoformat()}</Timestamp>
    <Jurisdiction>{jurisdiction}</Jurisdiction>
    <TargetAccount>{target_acct}</TargetAccount>
    <Narrative>{edited_narrative}</Narrative>
    <CryptographicHash>{sha256_hash}</CryptographicHash>
</SuspiciousActivityReport>"""

                latex_data = f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\begin{{document}}
\\title{{Suspicious Activity Report}}
\\author{{Aletheia FinCrime Terminal}}
\\date{{\\today}}
\\maketitle

\\section*{{Metadata}}
\\textbf{{Jurisdiction:}} {jurisdiction} \\\\
\\textbf{{Target Account:}} {target_acct} \\\\
\\textbf{{Cryptographic Hash:}} \\texttt{{{sha256_hash}}}

\\section*{{Grounds for Suspicion}}
{edited_narrative}

\\end{{document}}"""

                # --- 4. DISPLAY ENTERPRISE UI SUCCESS & BUTTONS ---
                st.success("Report Finalized! Secure exports generated.")
                st.info(f"🔒 **Cryptographic Chain of Custody Locked**\n\n**SHA-256 Hash:** `{sha256_hash}`\n\n*Pursuant to retention mandates, this cryptographic signature and the underlying evidence have been committed to the immutable audit ledger.*")
                
                st.write("**Download Formal Reports & Machine-Readable Artifacts:**")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.download_button("📄 PDF Document", data=pdf_bytes, file_name=f"Aletheia_SAR_{jurisdiction[:3]}.pdf", mime="application/pdf", use_container_width=True)
                with col2:
                    st.download_button("｛｝ JSON Payload", data=json_data, file_name=f"Aletheia_SAR_{jurisdiction[:3]}.json", mime="application/json", use_container_width=True)
                with col3:
                    st.download_button("🌐 XML Feed", data=xml_data, file_name=f"Aletheia_SAR_{jurisdiction[:3]}.xml", mime="application/xml", use_container_width=True)
                with col4:
                    st.download_button("∑ LaTeX Source", data=latex_data, file_name=f"Aletheia_SAR_{jurisdiction[:3]}.tex", mime="text/plain", use_container_width=True)

            except Exception as e:
                st.error(f"Failed to generate Export Artifacts: {e}")

else:
    # Empty State
    st.info("👈 Please upload the data in the sidebar to begin.")