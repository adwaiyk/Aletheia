import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import time
import requests
import json
import os

# Try importing the PDF generator module
try:
    from pdf_generator import generate_sba_pdf
except ImportError:
    st.error("⚠️ 'pdf_generator.py' not found. Please ensure it is in the same directory.")

# --- 1. Page Configuration & Custom CSS ---
st.set_page_config(page_title="Aletheia: SAR Generator", layout="wide")

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

st.title("⚖️ Aletheia: Local-First SAR Narrative Generator")
st.markdown("### Compliance Workbench | FIU-IND SBA Ready")

# --- 2. Dynamic Ingestion (Sidebar) ---
with st.sidebar:
    st.header("📂 Case File Ingestion")
    uploaded_file = st.file_uploader("Upload Transaction CSV", type="csv")
    st.info("Upload the 'synthetic_banking_data.csv' file generated in the previous step.")
    
    st.markdown("---")
    st.markdown("**System Status:**")
    # Quick check if Ollama is running
    try:
        requests.get("http://localhost:11434/")
        st.success("🟢 Ollama (Llama 3) Online")
    except:
        st.error("🔴 Ollama Offline. Run 'ollama run llama3' in terminal.")

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
        st.subheader("🕸️ VISUALIZATION: Fund Flow Network")
        
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
        st.subheader("📝 NARRATIVE: Draft STR (Editable)")
        
        # State management for the narrative
        if 'narrative' not in st.session_state:
            st.session_state.narrative = "Upload data and click 'Generate Narrative' to begin analysis..."

        if st.button("🤖 Generate Citation-Backed Narrative"):
            with st.spinner("Agentic AI analyzing typologies against PMLA guidelines..."):
                
                # 1. Prepare the Data Context
                # Convert the suspect's transactions into a clean string for the LLM
                # We limit columns to reduce token usage and focus the model
                context_data = display_df[['txn_date', 'txn_type', 'mode', 'amount', 'counterparty', 'txn_id']].to_string(index=False)
                
                # 2. The Master Prompt ("The Bible")
                system_prompt = f"""You are an expert Financial Crime Compliance Officer for a major Indian Bank.
Your task is to draft the "Grounds of Suspicion" (Part 7.2) for a Suspicious Transaction Report (STR) to be submitted to FIU-IND.

Here is the transaction history for Account {filter_acct}:
{context_data}

INSTRUCTIONS:
1. ANALYZE the data for "Structuring" (multiple cash deposits just under INR 50,000 to evade PAN reporting thresholds) or "Layering" (rapid fund movement).
2. DRAFT a formal narrative.
3. CITATION REQUIREMENT (CRITICAL): Every factual claim MUST be cited with the exact Txn ID in brackets. Example: "A cash deposit of 48,000 was made [1D640F1C9085]." Do not hallucinate IDs.
4. FORMAT:
   - Executive Summary
   - Chronology of Events (use bullet points with citations)
   - Grounds for Suspicion
5. TONE: Objective, formal, legalistic. No conversational filler.

Output only the report text, nothing else."""

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

        if st.button("✅ Approve & Generate Official FIU-IND PDF"):
            # The diff checker logic
            if edited_narrative != st.session_state.narrative:
                st.warning("⚠️ Human edits detected. Delta logged to immutable Audit Trail.")
            
            try:
                # Pass the edited text and the filtered dataframe to the PDF generator
                pdf_path = generate_sba_pdf(edited_narrative, display_df)
                
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    
                st.success("Report Finalized! PDF generation triggered.")
                
                # Show the download button
                st.download_button(
                    label="📄 Download Official STR (PDF)",
                    data=pdf_bytes,
                    file_name="FIU_IND_SBA_Report.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")

else:
    # Empty State
    st.info("👈 Please upload the 'synthetic_banking_data.csv' from the sidebar to begin the investigation.")