__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
from src.components.sidebar import render_sidebar
from src.components.researcher import create_baseball_researcher, create_baseball_task, run_baseball_research
from src.utils.output_handler import capture_output

#--------------------------------#
#         Streamlit App          #
#--------------------------------#
# Configure the page
st.set_page_config(
    page_title="Baseball Research Assistant",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main layout
st.title("⚾ Baseball Research Assistant", anchor=False)

# Render sidebar and get selection (provider and model)
selection = render_sidebar()

# Check if API keys are set
if ((selection["provider"] == "GROQ" and not os.getenv("GROQ_API_KEY")) or \
    (not os.getenv("EXA_API_KEY"))):
    st.warning("⚠️ Please enter your API keys in the sidebar to get started")
    st.stop()

# Create two columns for the input section
input_col1, input_col2, input_col3 = st.columns([1, 3, 1])
with input_col2:
    task_description = st.text_area(
        "What baseball statistics would you like to analyze?",
        value="Analyze Aaron Judge's batting statistics for the 2022 season and compare them to league averages.",
        height=68
    )

col1, col2, col3 = st.columns([1, 0.5, 1])
with col2:
    start_research = st.button("⚾ Start Analysis", use_container_width=False, type="primary")

if start_research:
    with st.status("🤖 Analyzing...", expanded=True) as status:
        try:
            # Create persistent container for process output with fixed height
            process_container = st.container(height=300, border=True)
            output_container = process_container.container()
            
            # Single output capture context
            with capture_output(output_container):
                researcher = create_baseball_researcher(selection)
                task = create_baseball_task(researcher, task_description)
                result = run_baseball_research(researcher, task)
                status.update(label="✅ Analysis completed!", state="complete", expanded=False)
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
        
        # Download as Markdown
        st.download_button(
            label="Download Report",
            data=result_text,
            file_name="baseball_analysis.md",
            mime="text/markdown",
            help="Download the baseball analysis report in Markdown format"
        )

# Add footer
st.divider()
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.caption("Made with ❤️ using pybaseball, [Exa](https://exa.ai), and [Streamlit](https://streamlit.io)")
