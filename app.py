import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import pandas as pd

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="M-KOPA Analytics Portal", layout="wide", initial_sidebar_state="collapsed")

# --- 2. LOAD RAW DATASETS (Cached for speed) ---
@st.cache_data
def load_data():
    try:
        # Load datasets from the same folder
        calls = pd.read_csv("calls.csv")
        orders = pd.read_csv("orders.csv")
        leads = pd.read_csv("leads.csv")
        campaigns = pd.read_csv("campaigns.csv")
        return calls, orders, leads, campaigns
    except Exception as e:
        return None, None, None, None

calls_df, orders_df, leads_df, campaigns_df = load_data()

# Convert data schemas and samples into a string for the AI's brain. 

data_context = ""
if calls_df is not None:
    data_context = f"""
    RAW DATA SCHEMAS & PREVIEWS:
    Calls Data (Sample): \n{calls_df.head(200).to_csv(index=False)}
    Orders Data (Sample): \n{orders_df.head(200).to_csv(index=False)}
    Leads Data (Sample): \n{leads_df.head(200).to_csv(index=False)}
    Campaigns Data (Full): \n{campaigns_df.to_csv(index=False)}
    """

# --- 3. HEADER & LOGO ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    try:
        st.image("logo.png", width=120)
    except:
        st.write("📊 **M-KOPA**") 

with col_title:
    st.title("Telesales Operations & AI Analytics Portal")
    st.markdown("**Created by Francis Afful Gyan | BI Analyst Candidate**")

st.divider()

# --- 4. TAB LAYOUT ---
tab1, tab2 = st.tabs(["📊 Interactive AI Dashboard", "📄 Executive Report & Next Steps"])

# ==========================================
# TAB 1: DASHBOARD & AI CHAT
# ==========================================
with tab1:
    col_dash, col_chat = st.columns([2.2, 1])

    # --- LEFT COLUMN: POWER BI EMBED ---
    with col_dash:
        st.subheader("12-Week Performance Dashboard")
        pbi_iframe = """
        <iframe title="MKOPA - Assessment_Dashboard" 
        width="100%" height="650" 
        src="https://app.powerbi.com/view?r=eyJrIjoiMTVjYTZmMDMtMDdlNC00MzE5LTgzMzItYmI1ZDk3ZmMzNzNjIiwidCI6IjhkMWE2OWVjLTAzYjUtNDM0NS1hZTIxLWRhZDExMmY1ZmI0ZiIsImMiOjN9" 
        frameborder="0" allowFullScreen="true"></iframe>
        """
        components.html(pbi_iframe, height=650)

    # --- RIGHT COLUMN: GEMINI AI ---
    with col_chat:
        st.subheader("🤖 Data Assistant")
        st.info("Ask me anything about the datasets, the 4-week Excel summary, or the 12-week Power BI dashboard.")
        
        # --- THE AI BRAIN (System Prompt) ---
        system_instruction = f"""
        You are the Senior Data Assistant for M-KOPA's telesales team, built by Francis Afful Gyan.
        You have complete knowledge of the end-to-end assessment. 
        
        PHASE 1: EXCEL (Last 4 Weeks Snapshot - Aug 7 to Sept 4)
        - Total Calls: 2,915
        - Connect Rate: 46.03% (1,342 connects)
        - Avg Talk Time: 123 seconds (measured on connected calls only)
        - Conversion Rate: 6.86% (200 orders)
        - Total GMV: $30,678.77
        - Average Order Value (AOV): $153.39
        - Expected Margin: 28%
        - Funnel: 2,915 Attempts -> 1,342 Connects -> 1,063 Qualified -> 200 Orders.
        
        PHASE 3: POWER BI (12-Week Trend)
        - Total Calls: 9,056
        - Total Orders: 420
        - Total GMV: $61.73K
        - Connect Rate: 45.54%
        - Lead Conversion Rate: 27.10%
        - Average Order Value (AOV): $146.98
        - Avg Margin: 27.66%
        
        KEY STRATEGIC INSIGHTS:
        1. Attempt Strategy: Connection and conversion rates plummet after Attempt 3. High effort, low reward.
        2. Revenue Concentration: GMV is highly dependent on fresh, top-tier campaigns.
        3. Action Plan: Institute a 3-attempt dialer cap, align with marketing on top 5 campaigns, and implement peer coaching for agents under 3% conversion.
        
        {data_context}
        
        Always answer as Francis's intelligent assistant. Be concise, highly analytical, and reference specific data points when answering.
        """
        
        # Initialize Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I am Francis's AI Assistant. I have fully ingested the 4-week Excel models, the 12-week Power BI dashboard, and the datasets. What would you like to know?"}
            ]

        # Display Chat Container
        chat_container = st.container(height=450)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat Input Area
        if prompt := st.chat_input("Ask about GMV, recommendations, or the 4-week Excel data..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # --- LIVE API CALL TO GEMINI ---
                try:
                    # Connects to your secret key stored in Streamlit
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
                    
                    # Pass the conversation history to the model
                    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                    response = model.generate_content(history)
                    bot_reply = response.text
                except Exception as e:
                    bot_reply = f"Error connecting to AI: Please ensure your GEMINI_API_KEY is saved in Streamlit secrets. ({e})"
                
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# ==========================================
# TAB 2: EXECUTIVE REPORT
# ==========================================
with tab2:
    st.header("Executive Summary: Telesales Performance")
    st.markdown("### The Bottom Line")
    st.write("An end-to-end analysis of 12 weeks of telesales data reveals that while our agents are working hard to generate **$61.73K** in GMV, we have a clear opportunity to optimize operations. Currently, agent effort is severely misaligned after the 3rd call attempt, and revenue is heavily concentrated in a handful of top campaigns.")
    
    st.divider()
    
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        st.subheader("📉 Insight 1: The Diminishing Returns of Effort")
        st.write("**The Data:** Connection rates and conversions peak at Attempts 1 and 2.")
        st.write("**The Drop-off:** Significant operational waste occurs on Attempts 4 and beyond. Agents are spending hours dialing unresponsive leads.")
        st.info("**The Action:** Implement a hard cap on the dialer to reallocate agent hours to fresh, high-intent leads.")
        
    with col_insight2:
        st.subheader("💰 Insight 2: Campaign & Agent ROI")
        st.write("**Revenue Concentration:** GMV is highly dependent on our top 5 campaigns, showing a classic Pareto principle distribution.")
        st.write("**Agent Variances:** While connect rates remain uniform across the floor, the *conversion* rates vary heavily by agent.")
        st.info("**The Action:** Trace top lead sources and implement targeted peer-to-peer sales coaching.")

    st.divider()
    
    st.subheader("🚀 Strategic Next Steps")
    st.markdown("""
    1. **Operations (Dialer Cap):** Institute a 3-attempt hard cap on the dialer to optimize average talk time and focus on early-funnel qualified leads.
    2. **Marketing Alignment:** Double down and align with the growth team to scale the specific lead sources feeding the Top 5 GMV campaigns.
    3. **Enablement:** Pair agents falling below the healthy conversion threshold with top performers for targeted closing and objection-handling coaching.
    """)