# Fix SQLite version issue by using pysqlite3
import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.document_processor import process_document
from utils.gemini import initialize_gemini, analyze_risk_with_gemini
from utils.db import initialize_chroma, store_in_chroma, query_chroma
import time

# Load environment variables
load_dotenv()

# Set API key directly as fallback if not loaded from .env
if not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = "AIzaSyBdz-qcLFRDsR-mm37AlRf2w6RZws2lDL0"

# Set page configuration
st.set_page_config(
    page_title="Risk Control Matrix Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini
gemini_model = initialize_gemini()

def main():
    # Add custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 20px;
    }
    .card {
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .dept-card {
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        background-color: transparent;
    }
    .high-risk {
        /* Removed border-left */
    }
    .medium-risk {
        /* Removed border-left */
    }
    .low-risk {
        /* Removed border-left */
    }
    .analyzing {
        text-align: center;
        padding: 20px;
        border-radius: 5px;
        background-color: transparent;
        margin-bottom: 20px;
        font-size: 1.2rem;
        color: #2E7D32;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 0 !important;
    }
    /* Make streamlit components background transparent */
    .stExpander {
        background-color: transparent !important;
    }
    /* Make general streamlit elements background transparent */
    .stMarkdown, .stInfo {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("<h1 class='main-header'>Risk Control Matrix Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Upload your RCM document for AI risk analysis</p>", unsafe_allow_html=True)
    
    # Create a simple upload interface
    uploaded_file = st.file_uploader("Upload Risk Control Matrix document", 
                                   type=["xlsx", "csv", "pdf", "docx"], 
                                   help="Upload RCM file to analyze")
    
    if uploaded_file:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.info(f"Uploaded: {uploaded_file.name}")
            analyze_button = st.button("Analyze Document", type="primary")
        
        with col2:
            st.info("This tool will analyze your Risk Control Matrix and identify key risks across departments.")
    
    # Main content area
    if 'analyzed_data' not in st.session_state:
        st.session_state.analyzed_data = None
        
    if uploaded_file and analyze_button:
        with st.spinner():
            # Show "being analyzed by AI" message
            st.markdown("<div class='analyzing'><b>🔍 Being analyzed by AI...</b><br>Examining departments, control objectives, and identifying risk patterns</div>", unsafe_allow_html=True)
            
            # Save the uploaded file temporarily
            temp_file_path = f"temp_{uploaded_file.name}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Process document
            try:
                processed_data = process_document(temp_file_path)
                
                # Store in ChromaDB
                db = initialize_chroma("risk_control_matrix")
                store_in_chroma(db, processed_data)
                
                # Analyze with Gemini
                st.session_state.analyzed_data = analyze_risk_with_gemini(
                    gemini_model,
                    processed_data
                )
                
                # Remove temp file
                os.remove(temp_file_path)
                
                st.success("Analysis complete!")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error analyzing document: {str(e)}")
                st.exception(e)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
    
    # Display analyzed data if available
    if st.session_state.analyzed_data:
        display_simplified_analysis(st.session_state.analyzed_data)

def display_simplified_analysis(data):
    """Display a simplified analysis focusing on departmental risks and gaps"""
    
    # Overview section
    st.markdown("## Departmental Risk Analysis")
    
    # Process departments
    departments = list(data.get("department_risks", {}).keys()) if data.get("department_risks") else data.get("departments", [])
    control_objectives = data.get("control_objectives", [])
    gaps = data.get("gaps", [])
    
    if not departments:
        st.warning("No departments found in the document. Please check the file format.")
        return
    
    # Create tabs for each department
    dept_tabs = st.tabs(departments)
    
    # Create analysis for each department
    for i, dept in enumerate(departments):
        with dept_tabs[i]:
            # Get department-specific data
            dept_objectives = [obj for obj in control_objectives if obj.get("department") == dept]
            dept_gaps = [gap for gap in gaps if gap.get("department") == dept]
            
            # Department overview
            dept_risk_data = data.get("department_risks", {}).get(dept, {})
            if dept_risk_data:
                risk_level = dept_risk_data.get("overall_risk_level", "Medium")
                risk_class = "high-risk" if risk_level == "High" else "medium-risk" if risk_level == "Medium" else "low-risk"
                
                st.markdown(f"<div class='dept-card {risk_class}'>", unsafe_allow_html=True)
                st.markdown(f"### {dept} Department - {risk_level} Risk")
                st.markdown(f"**Summary**: {dept_risk_data.get('summary', 'No summary available.')}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Risk Categories Analysis
            st.markdown("### Risk Type Analysis")
            
            # Define the specific risk types the user wants to analyze
            risk_types = ["Operational", "Financial", "Fraud", "Financial Fraud", "Operational Fraud"]
            
            # Check if we have RAG analysis results with risk_types directly
            if "risk_types" in dept_risk_data or "risk_analysis" in dept_risk_data:
                risk_type_data = dept_risk_data.get("risk_types", dept_risk_data.get("risk_analysis", {}))
                
                cols = st.columns(len(risk_types))
                for i, risk_type in enumerate(risk_types):
                    with cols[i]:
                        risks = risk_type_data.get(risk_type, [])
                        count = len(risks)
                        level = "High" if count >= 3 else "Medium" if count >= 1 else "Low"
                        color = "#FF5252" if level == "High" else "#FFC107" if level == "Medium" else "#4CAF50"
                        
                        st.markdown(f"<div style='text-align:center'>", unsafe_allow_html=True)
                        st.markdown(f"<h4>{risk_type}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<h2 style='color:{color}'>{count}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<span style='color:{color}'>{level} Risk</span>", unsafe_allow_html=True)
                        st.markdown(f"</div>", unsafe_allow_html=True)
                
                # Show specific risks for each type in an expander
                with st.expander("View Specific Risks by Type"):
                    for risk_type in risk_types:
                        risks = risk_type_data.get(risk_type, [])
                        if risks:
                            st.markdown(f"#### {risk_type} Risks")
                            for risk in risks:
                                st.markdown(f"- {risk}")
                            st.markdown("---")
            else:
                # Analyze content to detect risk types - fallback to keyword analysis
                risk_findings = {}
                for risk_type in risk_types:
                    risk_findings[risk_type] = []
                    
                    # Keywords for each risk type
                    keywords = {
                        "Operational": ["process", "workflow", "efficiency", "performance", "delivery", "resource", "procedure"],
                        "Financial": ["financial", "budget", "cost", "expense", "revenue", "payment", "accounting"],
                        "Fraud": ["fraud", "misappropriation", "theft", "falsification", "bribery", "corruption"],
                        "Financial Fraud": ["financial fraud", "embezzlement", "accounting fraud", "false reporting", "misstatement"],
                        "Operational Fraud": ["operational fraud", "process manipulation", "override", "unauthorized"]
                    }
                    
                    # Check each objective for this risk type
                    for obj in dept_objectives:
                        objective = obj.get("objective", "").lower()
                        risk = obj.get("what_can_go_wrong", "").lower()
                        
                        # Check if any keywords match
                        matched = False
                        for keyword in keywords.get(risk_type, []):
                            if keyword in objective or keyword in risk:
                                risk_findings[risk_type].append({
                                    "objective": obj.get("objective", ""),
                                    "risk": obj.get("what_can_go_wrong", ""),
                                    "risk_level": obj.get("risk_level", "Medium")
                                })
                                matched = True
                                break
                
                # Display risk findings
                cols = st.columns(len(risk_types))
                for i, risk_type in enumerate(risk_types):
                    with cols[i]:
                        count = len(risk_findings[risk_type])
                        level = "High" if count >= 3 else "Medium" if count >= 1 else "Low"
                        color = "#FF5252" if level == "High" else "#FFC107" if level == "Medium" else "#4CAF50"
                        
                        st.markdown(f"<div style='text-align:center'>", unsafe_allow_html=True)
                        st.markdown(f"<h4>{risk_type}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<h2 style='color:{color}'>{count}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<span style='color:{color}'>{level} Risk</span>", unsafe_allow_html=True)
                        st.markdown(f"</div>", unsafe_allow_html=True)
            
            # Control Gaps and Recommendations
            st.markdown("### Control Gaps and Recommendations")
            
            if dept_gaps:
                for i, gap in enumerate(dept_gaps):
                    st.markdown(f"<div class='dept-card high-risk'>", unsafe_allow_html=True)
                    st.markdown(f"**Gap {i+1}**: {gap.get('gap_title', '')}")
                    st.markdown(f"**Control Objective**: {gap.get('control_objective', '')}")
                    st.markdown(f"**Impact**: {gap.get('risk_impact', '')}")
                    
                    # Get or generate recommendation
                    recommendation = gap.get('proposed_solution', '')
                    if not recommendation:
                        # Find matching recommendation from overall recommendations
                        for rec in data.get("recommendations", []):
                            if rec.get("department") == dept:
                                recommendation = rec.get("description", "")
                                break
                    
                    st.markdown(f"**Recommended Action**: {recommendation}")
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No control gaps identified for this department.")
            
            # Key Risks
            st.markdown("### Key Risks")
            key_risks = dept_risk_data.get("key_risks", [])
            if key_risks:
                for risk in key_risks:
                    st.markdown(f"- {risk}")
            else:
                # Generate a list of key risks if none exist
                if dept_objectives:
                    st.markdown("Based on analysis of control objectives:")
                    high_risks = [obj for obj in dept_objectives if obj.get("risk_level", "").lower() in ["high", "h", "critical"]]
                    for i, risk in enumerate(high_risks[:3]):  # Show up to 3 high risks
                        st.markdown(f"- {risk.get('what_can_go_wrong', '')}")
                else:
                    st.info("No key risks identified for this department.")
    
    # Overall Recommendations
    st.markdown("## Overall Recommendations")
    recommendations = data.get("recommendations", [])
    if recommendations:
        for i, rec in enumerate(recommendations[:5]):  # Show top 5 recommendations
            priority = rec.get("priority", "Medium")
            rec_class = "high-risk" if priority == "High" else "medium-risk" if priority == "Medium" else "low-risk"
            
            st.markdown(f"<div class='dept-card {rec_class}'>", unsafe_allow_html=True)
            st.markdown(f"**{rec.get('title', f'Recommendation {i+1}')}** (Priority: {priority})")
            st.markdown(f"{rec.get('description', '')}")
            
            if "impact" in rec:
                st.markdown(f"**Expected Impact**: {rec.get('impact', '')}")
                
            if "department" in rec and rec["department"]:
                st.markdown(f"**Department**: {rec.get('department', '')}")
                
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No specific recommendations generated. Consider reviewing the identified gaps.")

if __name__ == "__main__":
    main() 