__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
from src.components.sidebar import render_sidebar
from src.components.researcher import run_research
from src.utils.output_handler import capture_output

#--------------------------------#
#         Streamlit App          #
#--------------------------------#
st.set_page_config(
    page_title="CrewAI Research Assistant",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo
st.logo(
    "https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg",
    link="https://www.crewai.com/",
    size="large"
)

# Main title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🔍 CrewAI Research Assistant")

# Render sidebar (to set API keys and model)
selection = render_sidebar()

# Validate required API keys
if ((selection["provider"] == "OpenAI" and not os.getenv("OPENAI_API_KEY")) or 
    (selection["provider"] == "GROQ" and not os.getenv("GROQ_API_KEY")) or 
    (selection["provider"] != "Ollama" and not os.getenv("EXA_API_KEY"))):
    st.warning("⚠️ Please enter your API keys in the sidebar to get started")
    st.stop()

if selection["provider"] == "Ollama" and not selection["model"]:
    st.warning("⚠️ No Ollama models found. Please ensure Ollama is running and models are loaded.")
    st.stop()

# Research input area
input_col1, input_col2, input_col3 = st.columns([1, 3, 1])
with input_col2:
    research_query = st.text_area(
        "Enter your research query:",
        value="Research the latest advancements in AI Agent research and summarize key findings.",
        height=100
    )

# Start research button
col1, col2, col3 = st.columns([1, 0.5, 1])
with col2:
    start_research = st.button("🚀 Start Research", type="primary")

if start_research:
    with st.status("🤖 Conducting research...", expanded=True) as status:
        try:
            process_container = st.container()
            output_container = process_container.container()
            
            # Capture any printed output (logs, etc.) in the UI
            with capture_output(output_container):
                result = run_research(research_query)
                status.update(label="✅ Research completed!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="❌ Error occurred", state="error")
            st.error(f"An error occurred: {str(e)}")
            st.stop()
    
    # Convert Crew output to string for display and download
    result_text = str(result)
    st.markdown(result_text)
    
    st.divider()
    download_col1, download_col2, download_col3 = st.columns([1, 2, 1])
    with download_col2:
        st.markdown("### 📥 Download Research Report")
        st.download_button(
            label="Download Report",
            data=result_text,
            file_name="research_report.md",
            mime="text/markdown",
            help="Download the research report in Markdown format"
        )

st.divider()
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.caption("Made with ❤️ using [CrewAI](https://crewai.com), [Exa](https://exa.ai) and [Streamlit](https://streamlit.io)")
