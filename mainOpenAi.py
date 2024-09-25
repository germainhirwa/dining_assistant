import streamlit as st
import openai
from scrape import (
    scrape_website,
    split_dom_content,
    clean_body_content,
    extract_body_content,
)
from parseOpenAi import parse_with_openai

# Default dining center URL
DEFAULT_URL = "https://dash.swarthmore.edu/menu/dining-center"

# Streamlit UI
st.title("GermAI Dining Assistant")

# Set the URL as the dining center by default
url = DEFAULT_URL
st.write(f"Scraping site: {url}")

if st.button("Scrape Site"):
    st.write("Scraping the dining center's menu...")
    
    result = scrape_website(url)
    body_content = extract_body_content(result)
    cleaned_content = clean_body_content(body_content)
    
    st.session_state.dom_content = cleaned_content  # Store cleaned content in session state
    
    with st.expander("View Menu Content"):
        st.text_area("Menu Content", cleaned_content, height=300)

if "dom_content" in st.session_state:
    # User input for preferences (e.g., dietary needs, athlete-specific meals)
    parse_description = st.text_area("Describe your meal preferences (e.g., 'high-protein dinner for athletes'):")
    
    if st.button("Get Meal Recommendations"):
        if parse_description:
            st.write("Parsing the dining menu based on your preferences...")
            
            dom_chunks = split_dom_content(st.session_state.dom_content)
            result = parse_with_openai(dom_chunks, parse_description)
            
            st.write(result)
