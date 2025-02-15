__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
from crewai import Crew, Process
from your_ai_module import run_baseball_analysis

#--------------------------------#
#         Streamlit App          #
#--------------------------------#
# Configure the page
st.set_page_config(
    page_title="CrewAI Baseball Analyst",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo
st.logo(
    "https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg",
    link="https://www.crewai.com/",
    size="large"
)

# Main layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("⚾ CrewAI Baseball Analyst", anchor=False)

# Check if API keys are set
if not os.getenv("GROQ_API_KEY") or not os.getenv("EXA_API_KEY"):
    st.warning("⚠️ Please enter your API keys in your environment to get started")
    st.stop()

# Create two columns for the input section
input_col1, input_col2, input_col3 = st.columns([1, 3, 1])
with input_col2:
    query = st.text_area(
        "Enter your baseball analysis query:",
        value="Analyze the top home run hitters in the 2024 season.",
        height=68
    )

col1, col2, col3 = st.columns([1, 0.5, 1])
with col2:
    start_analysis = st.button("🚀 Start Analysis", use_container_width=False, type="primary")

if start_analysis:
    with st.status("🔍 Analyzing...", expanded=True) as status:
        try:
            # Run baseball analysis with AI agents
            result = run_baseball_analysis(query)
            status.update(label="✅ Analysis Completed!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="❌ Error occurred", state="error")
            st.error(f"An error occurred: {str(e)}")
            st.stop()
    
    # Convert result to string for display and download
    result_text = str(result)
    
    # Display the final result
    st.markdown(result_text)
    
    # Create download buttons
    st.divider()
    download_col1, download_col2, download_col3 = st.columns([1, 2, 1])
    with download_col2:
        st.markdown("### 📥 Download Analysis Report")
        st.download_button(
            label="Download Report",
            data=result_text,
            file_name="analysis_report.md",
            mime="text/markdown",
            help="Download the analysis report in Markdown format"
        )

# Add footer
st.divider()
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.caption("Made with ❤️ using [CrewAI](https://crewai.com), [Exa](https://exa.ai) and [Streamlit](https://streamlit.io)")
