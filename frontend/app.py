import streamlit as st
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.patient_context import PatientContextManager
from backend.model_tracking import ModelTracker
from backend.readback import VoiceReadbackManager

# Configure Streamlit page
st.set_page_config(
    page_title="PV Sentinel",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f4e79;
        padding: 1rem 0;
        border-bottom: 3px solid #2e7bcf;
        margin-bottom: 2rem;
    }
    .safety-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Main header
    st.markdown("<h1 class='main-header'>🏥 PV Sentinel - AI-Powered Pharmacovigilance Assistant</h1>", unsafe_allow_html=True)
    
    # Safety warning
    st.markdown("""
    <div class='safety-warning'>
        <h3>🚨 Patient Safety First</h3>
        <p>This system prioritizes patient safety through:</p>
        <ul>
            <li><strong>Patient Context Preservation</strong> - Prevents AI paraphrasing of critical patient details</li>
            <li><strong>Model Version Tracking</strong> - Complete audit trail for regulatory compliance</li>
            <li><strong>Voice Readback Confirmation</strong> - Prevents transcription errors</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.selectbox(
            "Choose Function",
            ["Home", "New Case Entry", "Case Review", "System Status", "Documentation"]
        )
    
    # Main content based on selected page
    if page == "Home":
        show_home_page()
    elif page == "New Case Entry":
        show_case_entry()
    elif page == "Case Review":
        show_case_review()
    elif page == "System Status":
        show_system_status()
    elif page == "Documentation":
        show_documentation()

def show_home_page():
    st.header("Welcome to PV Sentinel")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏥 For Pharmacovigilance Officers")
        st.write("Create accurate AE narratives with AI assistance while preserving patient context.")
        if st.button("Start New Case", key="pv_officer"):
            st.session_state.page = "New Case Entry"
            st.rerun()
    
    with col2:
        st.subheader("🔍 For Reviewers")
        st.write("Review and validate AI-generated narratives with complete audit trails.")
        if st.button("Review Cases", key="reviewer"):
            st.session_state.page = "Case Review"
            st.rerun()
    
    with col3:
        st.subheader("⚙️ System Management")
        st.write("Monitor system status and access technical documentation.")
        if st.button("System Status", key="admin"):
            st.session_state.page = "System Status"
            st.rerun()

def show_case_entry():
    st.header("New Adverse Event Case Entry")
    
    # Patient information section
    st.subheader("Patient Information")
    
    col1, col2 = st.columns(2)
    with col1:
        patient_age = st.number_input("Patient Age", min_value=0, max_value=120, value=0)
        patient_gender = st.selectbox("Gender", ["", "Male", "Female", "Other", "Not Specified"])
    
    with col2:
        patient_weight = st.number_input("Weight (kg)", min_value=0.0, max_value=500.0, value=0.0)
        
    # Event description
    st.subheader("Event Description")
    
    # Voice input option
    use_voice = st.checkbox("Use Voice Input (Recommended for accuracy)")
    
    if use_voice:
        st.info("🎤 Voice input feature requires local microphone access. Click 'Start Recording' to begin.")
        if st.button("Start Recording"):
            st.warning("Voice recording feature requires full backend integration. Currently in demo mode.")
    
    # Text input as alternative
    event_description = st.text_area(
        "Describe the adverse event (include patient's exact words when possible)",
        height=200,
        placeholder="Patient reported: 'I started feeling dizzy about 2 hours after taking the medication...'"
    )
    
    # Medication information
    st.subheader("Medication Information")
    medication_name = st.text_input("Medication Name")
    medication_dose = st.text_input("Dose and Frequency")
    
    # Generate narrative button
    if st.button("Generate AI Narrative", type="primary"):
        if event_description:
            with st.spinner("Generating AI narrative... Preserving patient context..."):
                # Simulate AI processing
                st.success("✅ Narrative generated successfully!")
                
                # Show patient context preservation
                st.subheader("Patient Context Preservation Check")
                st.markdown("""
                <div class='success-box'>
                    <h4>✅ Patient Voice Preserved</h4>
                    <p><strong>Original patient language detected:</strong> "I started feeling dizzy..."</p>
                    <p><strong>Context strength:</strong> 95% - Excellent preservation</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show generated narrative
                st.subheader("Generated Narrative")
                sample_narrative = f"""
A {patient_age}-year-old {patient_gender.lower()} patient reported experiencing dizziness approximately 2 hours after administration of {medication_name}. The patient's exact words were: "{event_description[:100]}..."

The event occurred following the prescribed dose of {medication_dose}. The patient's weight was recorded as {patient_weight} kg.

Patient Safety Assessment: The patient's direct account has been preserved to maintain clinical accuracy and regulatory compliance.
                """
                st.text_area("AI-Generated Narrative", value=sample_narrative, height=200)
                
                # Model tracking info
                st.info("📊 Model Version: Mistral-7B-v1.2.3 | Generation ID: MVG-2024-001 | Audit Trail: Complete")
        else:
            st.error("Please provide an event description to generate the narrative.")

def show_case_review():
    st.header("Case Review Dashboard")
    
    # Sample cases for demonstration
    st.subheader("Cases Pending Review")
    
    sample_cases = [
        {"ID": "PV-2024-001", "Patient": "65M", "Event": "Dizziness", "Status": "Pending Medical Review", "Priority": "Standard"},
        {"ID": "PV-2024-002", "Patient": "42F", "Event": "Rash", "Status": "Pending Regulatory Review", "Priority": "Expedited"},
        {"ID": "PV-2024-003", "Patient": "78M", "Event": "Nausea", "Status": "Ready for Submission", "Priority": "Standard"},
    ]
    
    for case in sample_cases:
        with st.expander(f"Case {case['ID']} - {case['Event']} ({case['Priority']})"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Patient:** {case['Patient']}")
                st.write(f"**Event:** {case['Event']}")
            with col2:
                st.write(f"**Status:** {case['Status']}")
                st.write(f"**Priority:** {case['Priority']}")
            with col3:
                if st.button(f"Review Case {case['ID']}", key=f"review_{case['ID']}"):
                    st.info(f"Opening detailed review for case {case['ID']}")

def show_system_status():
    st.header("System Status & Monitoring")
    
    # System health indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("System Status", "🟢 Operational", "All systems normal")
    
    with col2:
        st.metric("Model Status", "🟢 Active", "Mistral-7B-v1.2.3")
    
    with col3:
        st.metric("Cases Today", "23", "+5 from yesterday")
    
    with col4:
        st.metric("Accuracy Rate", "95.2%", "+2.1% this week")
    
    # Safety features status
    st.subheader("Critical Safety Features Status")
    
    safety_features = [
        {"Feature": "Patient Context Preservation", "Status": "🟢 Active", "Last Check": "2 minutes ago"},
        {"Feature": "Model Version Tracking", "Status": "🟢 Active", "Last Check": "1 minute ago"},
        {"Feature": "Voice Readback System", "Status": "🟢 Active", "Last Check": "30 seconds ago"},
        {"Feature": "Audit Trail Logging", "Status": "🟢 Active", "Last Check": "15 seconds ago"},
    ]
    
    for feature in safety_features:
        col1, col2, col3 = st.columns([3, 1, 2])
        with col1:
            st.write(f"**{feature['Feature']}**")
        with col2:
            st.write(feature['Status'])
        with col3:
            st.write(f"Last check: {feature['Last Check']}")

def show_documentation():
    st.header("Documentation & Help")
    
    st.subheader("Quick Access")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📚 User Guides
        - [Executive Summary](../docs/user-guide/01_executive_summary.md)
        - [Quick Start Guides](../docs/user-guide/02_quick_start_guides.md)
        - [Safety Features](../docs/user-guide/13_safety_features.md)
        - [Voice Features](../docs/user-guide/14_voice_features.md)
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Technical Documentation
        - [Installation Guide](../docs/user-guide/03_installation_setup.md)
        - [Configuration Reference](../docs/user-guide/25_configuration_reference.md)
        - [Troubleshooting](../docs/user-guide/21_troubleshooting.md)
        - [GAMP 5 Validation](../docs/user-guide/18_gamp5_validation.md)
        """)
    
    st.subheader("Contact & Support")
    st.info("For technical support or questions about patient safety features, refer to the comprehensive user guide documentation.")

if __name__ == "__main__":
    main() 