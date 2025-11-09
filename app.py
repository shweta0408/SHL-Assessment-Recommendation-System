import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import numpy as np
import plotly.express as px
from openrouter_api import generate_content

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🧪",
    layout="wide"
)

# --- Load Environment Variables ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    st.warning("⚠️ OPENROUTER_API_KEY not found in environment variables.")

# --- API Endpoint (use your deployed FastAPI backend) ---
API_ENDPOINT = "https://recommendation-system-e7gs.onrender.com"

# --- Utility Functions ---


def get_recommendations_from_api(query, max_results=10):
    """Call FastAPI backend to get recommendations"""
    try:
        response = requests.post(
            f"{API_ENDPOINT}/recommend",
            json={"query": query, "max_results": max_results},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["recommended_assessments"]
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []


def scrape_job_description(url):
    """Scrape job description from a provided URL"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")
            return " ".join([p.text.strip() for p in paragraphs])
        else:
            return f"Failed to fetch URL: {response.status_code}"
    except Exception as e:
        return f"Error processing URL: {str(e)}"


def check_api_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_ENDPOINT}/health", timeout=10)
        return response.status_code == 200
    except:
        return False


# --- Streamlit Interface ---
st.title("🧪 SHL Assessment Recommender")
st.markdown("""
This app recommends SHL assessments based on your job description or hiring needs.
You can enter text or provide a URL for a job description.
""")

if not check_api_health():
    st.error(
        "⚠️ The backend API is not responding. Please check your FastAPI deployment.")
    st.stop()
else:
    st.success("✅ Connected to backend API successfully!")

tab1, tab2 = st.tabs(["Enter Query", "Upload Job Description URL"])

with tab1:
    query = st.text_area(
        "Enter your query:",
        height=150,
        placeholder="Example: I'm hiring for data analysts who can interpret business data and need assessments under 30 minutes."
    )
    if st.button("🔍 Get Recommendations", key="search_button") and query:
        with st.spinner("Finding the best assessments for you..."):
            recommendations = get_recommendations_from_api(query)
            if recommendations:
                st.subheader("📊 Recommended Assessments")
                for i, assessment in enumerate(recommendations):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(
                                f"### {i+1}. [{assessment['description'].split('.')[0]}]({assessment['url']})")
                            st.markdown(
                                f"**Test Type:** {', '.join(assessment['test_type'])}")
                            st.markdown(
                                f"**Why it's relevant:** {'.'.join(assessment['description'].split('.')[1:])}")
                        with col2:
                            st.markdown(
                                f"**Remote Testing:** {assessment['remote_support']}")
                            st.markdown(
                                f"**Adaptive/IRT:** {assessment['adaptive_support']}")
                            st.markdown(
                                f"**Duration:** {assessment['duration']} minutes")
                        st.markdown("---")
