import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import pandas as pd
import base64
import os

st.set_page_config(page_title="M-KOPA Analytics Portal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    h1, h2, h3, h4 {
        color: #111827 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    hr {
        border: 0;
        height: 2px;
        background-image: linear-gradient(to right, #00A859, #F3F4F6);
    }
    .stAlert {
        background-color: rgba(0, 168, 89, 0.1) !important;
        color: #111827 !important;
        border-left: 4px solid #00A859;
    }
    div.row-widget.stRadio > div {
        flex-direction: row;
        background-color: #F3F4F6;
        padding: 5px;
        border-radius: 10px;
    }
    .sample-q {
        font-size: 0.9rem;
        color: #00A859;
        font-style: italic;
        margin-bottom: 2px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        calls = pd.read_csv("calls.csv")
        orders = pd.read_csv("orders.csv")
        leads = pd.read_csv("leads.csv")
        campaigns = pd.read_csv("campaigns.csv")
        return calls, orders, leads, campaigns
    except Exception as e:
        return None, None, None, None

calls_df, orders_df, leads_df, campaigns_df = load_data()

data_context = ""
if calls_df is not None:
    # --- PRE-CALCULATE ALL DATA DIMENSIONS FOR THE AI ---
    # 1. Agent Totals
    agent_calls = calls_df.groupby('agent_id').size().reset_index(name='Total_Calls').sort_values(by='Total_Calls', ascending=False)
    
    # 2. Campaign Totals
    campaign_calls = calls_df.groupby('campaign_id').size().reset_index(name='Total_Calls').sort_values(by='Total_Calls', ascending=False)
    
    # 3. Attempt Drop-off Funnel
    if 'attempt_number' in calls_df.columns:
        attempt_funnel = calls_df.groupby('attempt_number').size().reset_index(name='Total_Calls')
    else:
        attempt_funnel = "Attempt number data not available in raw format."

    data_context = f"""
    PRE-CALCULATED SQL AGGREGATIONS (Use these strictly to answer granular data questions):
    
    --- 1. AGENT PERFORMANCE MATRIX (Ranked by Call Volume) ---
    {agent_calls.to_string(index=False)}
    
    --- 2. CAMPAIGN VOLUMES (Ranked by Call Volume) ---
    {campaign_calls.head(10).to_string(index=False)}
    
    --- 3. ATTEMPT FUNNEL (Calls per Dial Attempt) ---
    {attempt_funnel}
    """

def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo_b64 = get_image_base64("logo.png")

if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height: 65px; object-fit: contain; background-color: white; padding: 8px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
else:
    logo_html = '<span style="font-size: 3rem;">📊</span>'

st.markdown(f"""
<div style="background-color: #00A859; padding: 20px 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 25px; margin-bottom: 20px;">
    <div>{logo_html}</div>
    <div>
        <h1 style="color: white !important; margin: 0; padding: 0; font-size: 2.2rem; line-height: 1.2;">Telesales Operations & AI Analytics Portal</h1>
        <p style="color: white !important; margin: 0; padding-top: 5px; font-size: 1.1rem; font-weight: 500;">Created by Francis Afful Gyan | BI Analyst Candidate</p>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Interactive Dashboards & AI", "📄 Executive Report & Next Steps"])

with tab1:
    col_dash, col_chat = st.columns([2.2, 1])

    with col_dash:
        view_selection = st.radio(
            "Toggle Analytical View:", 
            ["📈 Phase 3: 12-Week Power BI Dashboard", "📊 Phase 1: 4-Week Excel Summary"]
        )
        
        if view_selection == "📈 Phase 3: 12-Week Power BI Dashboard":
            st.subheader("12-Week Strategic Performance")
            pbi_iframe = """
            <iframe title="MKOPA - Assessment_Dashboard" 
            width="100%" height="650" 
            src="https://app.powerbi.com/view?r=eyJrIjoiMTVjYTZmMDMtMDdlNC00MzE5LTgzMzItYmI1ZDk3ZmMzNzNjIiwidCI6IjhkMWE2OWVjLTAzYjUtNDM0NS1hZTIxLWRhZDExMmY1ZmI0ZiIsImMiOjN9" 
            frameborder="0" allowFullScreen="true"></iframe>
            """
            components.html(pbi_iframe, height=650)
        else:
            st.subheader("4-Week Tactical Snapshot (Excel)")
            st.info("This view represents the initial data exploration, cleaning, and tactical KPI formulation phase prior to the 12-week BI scale-up.")
            try:
                st.image("4-weeks.png", use_container_width=True)
            except:
                st.error("Missing '4-weeks.png'. Please ensure the screenshot is uploaded to the root directory.")

    with col_chat:
        st.subheader("🤖 Data Assistant")
        st.info("Ask me anything about the datasets, the 4-week Excel summary, or the 12-week Power BI dashboard.")
        
        # --- UI ENHANCEMENT: SAMPLE QUESTIONS ---
        st.markdown("**💡 Try asking:**")
        st.markdown("<p class='sample-q'>1. What is the total GMV and Conversion Rate for the 12-week period?</p>", unsafe_allow_html=True)
        st.markdown("<p class='sample-q'>2. Which agent recorded the highest total call volume?</p>", unsafe_allow_html=True)
        st.markdown("<p class='sample-q'>3. What happens to the connect rate after the 3rd dial attempt?</p>", unsafe_allow_html=True)
        st.markdown("<p class='sample-q'>4. Which lead source generates the most orders?</p>", unsafe_allow_html=True)
        st.markdown("<p class='sample-q'>5. What are your top operational recommendations?</p>", unsafe_allow_html=True)
        st.write("") # Spacer
        
        system_instruction = f"""
        You are the Senior Data Assistant for M-KOPA's telesales team, built by Francis Afful Gyan.
        You have complete knowledge of the end-to-end assessment, the UI dashboards, the data, and the executive report.
        
        CRITICAL INSTRUCTION: If asked for totals, KPIs, or metrics, ALWAYS use the hardcoded numbers below to perfectly match the dashboard UI. If asked granular questions (like top agent), refer to the PRE-CALCULATED SQL AGGREGATIONS at the bottom.
        
        PHASE 1: EXCEL (Last 4 Weeks Snapshot - Aug 7 to Sept 4)
        - Total Calls: 2,915
        - Connect Rate: 46.03% (1,342 connects)
        - Avg Talk Time: 123 seconds (measured on connected calls only)
        - Conversion Rate: 6.86% (200 orders)
        - Total GMV: $30,678.77
        - Average Order Value (AOV): $153.39
        - Expected Margin: 28%
        - Funnel: 2,915 Attempts -> 1,342 Connects -> 1,063 Qualified -> 200 Orders.
        
        PHASE 3: POWER BI (12-Week Trend - June to August)
        - Total Calls: 9,056
        - Total Orders: 420
        - Total GMV: $61.73K
        - Connect Rate: 45.54%
        - Lead Conversion Rate: 27.10%
        - Average Order Value (AOV): $146.98
        - Avg Margin: 27.66%
        - Orders by Lead Source: Cross Sell (27.38%), Winback (23.1%), Inbound (15%), Referral (12.86%), Digital (11.43%), Field (8.33%).
        
        EXECUTIVE REPORT & INSIGHTS (Quote these if asked for recommendations or attempt limits):
        - Insight 1: Diminishing Returns. Connection/conversion rates peak at Attempts 1 and 2. They plummet after Attempt 3. High effort, low reward. Action: Implement hard cap on the dialer.
        - Insight 2: Campaign & Agent ROI. GMV remains highly dependent on fresh, top-tier campaigns. Connect rates are uniform, but conversion rates vary heavily by agent. Action: Trace lead sources and peer-to-peer coaching.
        - Strategic Next Steps: 1) Institute 3-attempt dialer cap. 2) Marketing alignment to scale top 5 campaigns. 3) Enablement/Coaching for agents under 3% conversion.
        
        {data_context}
        
        Always answer as Francis's intelligent, confident assistant. Be concise, highly analytical, and reference specific data points from the summaries above when answering.
        """
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I am Francis's AI Assistant. I have analyzed all the raw data, calculated agent performance, and memorized the 12-week BI model. How can I help?"}
            ]

        # Shortened height slightly to make room for the sample questions
        chat_container = st.container(height=380)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Ask about GMV, recommendations, or lead sources..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                try:
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    
                    if not available_models:
                        bot_reply = "Error: Your API key is active, but it does not have access to any generation models. Check your Google AI Studio account."
                    else:
                        model_name = next((m for m in available_models if '1.5-flash' in m), available_models[0])
                        
                        model = genai.GenerativeModel(model_name)
                        
                        full_prompt = f"SYSTEM KNOWLEDGE & INSTRUCTIONS:\n{system_instruction}\n\n"
                        full_prompt += "--- CURRENT CONVERSATION ---\n"
                        full_prompt += "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                        
                        response = model.generate_content(full_prompt)
                        bot_reply = response.text
                        
                except Exception as e:
                    bot_reply = f"System Error: {e}"
                
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)
            
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

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
