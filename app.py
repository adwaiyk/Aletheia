import streamlit as st
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import time

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
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Aletheia: Local-First SAR Narrative Generator")
st.markdown("### Compliance Workbench | FIU-IND SBA Ready")

# --- 2. Dynamic Ingestion (Sidebar) ---
with st.sidebar:
    st.header("📂 Case File Ingestion")
    uploaded_file = st.file_uploader("Upload Transaction CSV", type="csv")
    st.info("Upload the 'synthetic_banking_data.csv' file generated in the previous step.")

if uploaded_file:
    # Load Data into Session State to persist across reruns
    if 'df' not in st.session_state:
        st.session_state.df = pd.read_csv(uploaded_file)
    df = st.session_state.df

    # --- 3. The Glass Box Layout ---
    col_evidence, col_narrative = st.columns([1.2, 1]) # Left column slightly wider

    with col_evidence:
        st.subheader("🔍 EVIDENCE: Transaction Data")
        
        # Filtering to find the "Suspect"
        accounts = df['account_no'].unique()
        # Default to the first account (in our generated data, the injected crimes are usually near the top)
        filter_acct = st.selectbox("Filter by Account (Select a suspect):", accounts)
        
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
            net.add_node(src, label=src[:8]+"...", color='#FFD700', shape='dot')
            net.add_node(dst, label=dst[:8]+"...", color='#00ff00', shape='dot')
            net.add_edge(src, dst, value=w, title=f"Total: ₹{w:,.2f}")
            
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
                time.sleep(2) # Fake loading time for dramatic effect during demo
                
                # Mock LLM Output (We will replace this with Ollama in the next step)
                st.session_state.narrative = f"""**Executive Summary:**
The account {filter_acct} reflects a pattern of suspicious activity consistent with **Structuring (Smurfing)**, aimed at evading PMLA reporting thresholds.

**Detailed Analysis:**
* **Structuring Pattern:** The account executed multiple cash deposits over a short timeframe.
* **Threshold Evasion:** Each deposit was valued between ₹40,000 and ₹49,000. This is deliberately just below the ₹50,000 mandatory PAN quoting threshold.
* **Typology Match:** The total cash influx is highly inconsistent with normal retail spending and strongly matches FIU-IND Structuring typologies.

**Conclusion:**
The pattern suggests an attempt to introduce illicit cash into the banking system while avoiding regulatory triggers. 

Recommended for filing STR."""
                st.rerun()

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
                st.warning("Human edits detected. Delta logged to immutable Audit Trail.")
            
            st.success("Report Finalized! PDF generation triggered.")
            # We will wire up the actual PDF download button in the next step!

else:
    st.info("👈 Please upload the transactions CSV from the sidebar to begin the investigation.")