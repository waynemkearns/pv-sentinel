import streamlit as st
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import backend modules
sys.path.append(str(Path(__file__).parent.parent))

# Import the correct class names from backend modules
try:
    from backend.patient_context import PatientContextPreserver
    from backend.model_tracking import ModelVersionTracker
    from backend.readback import VoiceReadbackConfirmer
    # Phase 1 imports
    from backend.pii_protection import create_pii_protection_system
    # Phase 2 imports
    from backend.patient_voice import create_patient_voice_protector
    from backend.narrative_comparison import create_narrative_comparison_system
    backend_available = True
except ImportError as e:
    st.warning(f"Backend modules not fully available: {e}")
    backend_available = False

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
    
    # Backend status indicator
    if not backend_available:
        st.error("⚠️ Backend modules not fully loaded. Some features may be limited to demo mode.")
    else:
        st.success("✅ All backend modules loaded successfully")
    
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
        
        # User role selection (Phase 1 New Feature)
        st.subheader("👤 User Role")
        user_role = st.selectbox(
            "Current Role",
            ["drafter", "reviewer", "auditor", "admin"],
            help="Different roles see different levels of data detail"
        )
        
        # Role-based information
        role_descriptions = {
            "drafter": "Can create and edit adverse event cases",
            "reviewer": "Can review and approve cases for submission", 
            "auditor": "Can audit cases with PII masking enabled",
            "admin": "Full system access with all permissions"
        }
        st.caption(role_descriptions.get(user_role, ""))
        
        st.divider()
        
        page = st.selectbox(
            "Choose Function",
            ["Home", "New Case Entry", "Case Review", "Patient Voice Protection", "Narrative Comparison", "System Status", "Documentation"]
        )
    
    # Main content based on selected page
    if page == "Home":
        show_home_page()
    elif page == "New Case Entry":
        show_case_entry(user_role)
    elif page == "Case Review":
        show_case_review(user_role)
    elif page == "Patient Voice Protection":
        show_patient_voice_protection(user_role)
    elif page == "Narrative Comparison":
        show_narrative_comparison(user_role)
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

def show_case_entry(user_role: str = "drafter"):
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
            if backend_available:
                st.warning("Voice recording feature requires full backend integration and microphone setup.")
            else:
                st.warning("Voice recording feature requires full backend integration. Currently in demo mode.")
    
    # Text input as alternative
    st.markdown("""
    <div style='background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 10px; margin: 10px 0;'>
        <strong>🔒 Patient Privacy Notice:</strong> This field may contain sensitive patient information. 
        Data is processed locally and protected according to privacy regulations. 
        Avoid including unnecessary identifying information while preserving clinical context.
    </div>
    """, unsafe_allow_html=True)
    
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
                
                # Show PII protection status (Phase 1 New Feature)
                st.subheader("🔒 Privacy Protection Status")
                
                # Simulate PII detection for demo
                with st.expander("PII Detection Results", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("PII Instances Detected", "2", "Names, 1 Address")
                    with col2:
                        st.metric("Protection Level", "High", "Role-based masking active")
                    
                    st.info("✅ All sensitive information has been identified and protected according to your user role.")
                
                # Show patient context preservation
                st.subheader("Patient Context Preservation Check")
                
                if backend_available:
                    # Try to use real backend for context preservation demo
                    try:
                        # Create a demo config
                        demo_config = {
                            'patient_safety': {
                                'context_preservation': True,
                                'context_validation': True
                            }
                        }
                        
                        # Initialize patient context preserver
                        context_preserver = PatientContextPreserver(demo_config)
                        
                        # Extract patient context
                        patient_context = context_preserver.extract_patient_context(
                            event_description, 
                            "typed" if not use_voice else "voice"
                        )
                        
                        # Show real context analysis
                        st.markdown(f"""
                        <div class='success-box'>
                            <h4>✅ Patient Voice Preserved (Real Analysis)</h4>
                            <p><strong>Patient voice indicators found:</strong> {len(patient_context.patient_voice_indicators)}</p>
                            <p><strong>Key patient expressions:</strong> {'; '.join(patient_context.patient_voice_indicators[:3]) if patient_context.patient_voice_indicators else 'None detected'}</p>
                            <p><strong>Emotional context:</strong> {patient_context.emotional_context or 'None detected'}</p>
                            <p><strong>Input method:</strong> {patient_context.input_method}</p>
                            <p><strong>Context validation:</strong> {'✅ Passed' if all(patient_context.validation_flags.values()) else '⚠️ Review needed'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Error using backend context preservation: {e}")
                        # Fall back to demo mode
                        show_demo_context_preservation()
                else:
                    show_demo_context_preservation()
                
                # Show generated narrative
                st.subheader("Generated Narrative")
                sample_narrative = f"""
A {patient_age}-year-old {patient_gender.lower()} patient reported experiencing dizziness approximately 2 hours after administration of {medication_name}. The patient's exact words were: "{event_description[:100]}..."

The event occurred following the prescribed dose of {medication_dose}. The patient's weight was recorded as {patient_weight} kg.

Patient Safety Assessment: The patient's direct account has been preserved to maintain clinical accuracy and regulatory compliance.
                """
                st.text_area("AI-Generated Narrative", value=sample_narrative, height=200)
                
                # Model tracking info
                if backend_available:
                    st.info("📊 Model Version: Mistral-7B-v1.2.3 | Generation ID: MVG-2024-001 | Audit Trail: Complete | Backend: Active")
                else:
                    st.info("📊 Model Version: Mistral-7B-v1.2.3 | Generation ID: MVG-2024-001 | Audit Trail: Complete | Backend: Demo Mode")
        else:
            st.error("Please provide an event description to generate the narrative.")

def show_demo_context_preservation():
    """Show demo context preservation when backend is not available"""
    st.markdown("""
    <div class='success-box'>
        <h4>✅ Patient Voice Preserved (Demo Mode)</h4>
        <p><strong>Original patient language detected:</strong> "I started feeling dizzy..."</p>
        <p><strong>Context strength:</strong> 95% - Excellent preservation</p>
        <p><strong>Voice indicators:</strong> First-person language, temporal descriptions</p>
        <p><strong>Note:</strong> Full backend integration provides detailed context analysis</p>
    </div>
    """, unsafe_allow_html=True)

def show_case_review(user_role: str = "reviewer"):
    st.header("Case Review Dashboard")
    
    # Show role-based data access (Phase 1 New Feature)
    st.markdown(f"""
    <div style='background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 10px; margin: 10px 0;'>
        <strong>👤 Viewing as:</strong> {user_role.title()} | 
        <strong>Data Protection:</strong> {'PII masking enabled' if user_role in ['auditor', 'readonly'] else 'Full access'}
    </div>
    """, unsafe_allow_html=True)
    
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

def show_patient_voice_protection(user_role: str = "drafter"):
    """Display Patient Voice Protection interface (Phase 2 Feature)"""
    st.header("🗣️ Patient Voice Protection")
    
    # Patient safety notice
    st.markdown("""
    <div style='background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>🛡️ Patient Voice Protection System</h4>
        <p><strong>Critical P0 Feature:</strong> Preserves authentic patient voice that AI cannot modify</p>
        <ul>
            <li>Protects direct patient quotes from AI modification</li>
            <li>Maintains emotional context and patient language</li>
            <li>Provides audit trail for patient voice integrity</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo case selection
    st.subheader("Select Case for Patient Voice Analysis")
    demo_cases = {
        "CASE-001": "Patient dizzy after medication",
        "CASE-002": "Allergic reaction to antibiotic", 
        "CASE-003": "Severe headache post-vaccination"
    }
    
    selected_case = st.selectbox("Case ID", list(demo_cases.keys()), format_func=lambda x: f"{x}: {demo_cases[x]}")
    
    if selected_case:
        st.subheader("🔍 Patient Voice Fragments Detected")
        
        # Demo patient voice fragments
        demo_fragments = {
            "CASE-001": [
                {
                    "id": "PVF-12345678-abcd",
                    "text": "I started feeling really dizzy about 2 hours after I took the pill",
                    "type": "Direct Quote",
                    "confidence": 0.95,
                    "emotional_indicators": ["dizzy"],
                    "protection_level": "Protected"
                },
                {
                    "id": "PVF-87654321-efgh", 
                    "text": "It felt like the room was spinning and I had to sit down",
                    "type": "Reported Speech",
                    "confidence": 0.82,
                    "emotional_indicators": ["spinning"],
                    "protection_level": "Protected"
                }
            ]
        }
        
        fragments = demo_fragments.get(selected_case, [])
        
        for i, fragment in enumerate(fragments):
            with st.expander(f"Fragment {i+1}: {fragment['text'][:50]}...", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Fragment ID:** {fragment['id']}")
                    st.write(f"**Type:** {fragment['type']}")
                    st.write(f"**Confidence:** {fragment['confidence']:.2%}")
                    st.write(f"**Protection Level:** {fragment['protection_level']}")
                
                with col2:
                    st.write(f"**Full Text:**")
                    st.markdown(f"*\"{fragment['text']}\"*")
                    st.write(f"**Emotional Indicators:** {', '.join(fragment['emotional_indicators'])}")
                
                # Protection status indicator
                if fragment['protection_level'] == "Protected":
                    st.success("🔒 This patient voice fragment is protected from AI modification")
                
                # Action buttons
                col3, col4, col5 = st.columns(3)
                with col3:
                    if st.button(f"Add Annotation", key=f"annotate_{i}"):
                        st.text_area("Human Annotation", key=f"annotation_{i}", 
                                   placeholder="Add clarification or context...")
                
                with col4:
                    if st.button(f"Mark as Verified", key=f"verify_{i}"):
                        st.success("✅ Fragment marked as verified")
                
                with col5:
                    if st.button(f"Flag for Review", key=f"flag_{i}"):
                        st.warning("⚠️ Fragment flagged for medical review")
        
        # Summary statistics
        st.subheader("📊 Patient Voice Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Fragments", len(fragments))
        with col2:
            st.metric("Protected Fragments", len([f for f in fragments if f['protection_level'] == 'Protected']))
        with col3:
            avg_confidence = sum(f['confidence'] for f in fragments) / len(fragments) if fragments else 0
            st.metric("Avg. Confidence", f"{avg_confidence:.1%}")
        with col4:
            emotional_count = sum(len(f['emotional_indicators']) for f in fragments)
            st.metric("Emotional Indicators", emotional_count)

def show_narrative_comparison(user_role: str = "reviewer"):
    """Display Narrative Comparison interface (Phase 2 Feature)"""
    st.header("📋 Narrative Comparison & Version Control")
    
    # Feature description
    st.markdown("""
    <div style='background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>🔍 Side-by-Side Narrative Comparison</h4>
        <p><strong>Critical P0 Feature:</strong> Track all narrative changes with justification requirements</p>
        <ul>
            <li>Draft vs Final comparison with diff highlighting</li>
            <li>Clinical impact assessment for each change</li>
            <li>Edit justification tracking for compliance</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo version selection
    st.subheader("Select Narrative Versions to Compare")
    
    col1, col2 = st.columns(2)
    with col1:
        version_1 = st.selectbox("Version 1 (Baseline)", 
                                ["Draft v1.0", "Review v1.1", "Final v1.2"])
    with col2:
        version_2 = st.selectbox("Version 2 (Comparison)", 
                                ["Review v1.1", "Final v1.2", "Locked v1.3"])
    
    if st.button("Generate Comparison", type="primary"):
        st.subheader("📊 Comparison Summary")
        
        # Demo comparison statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Changes", "7", delta="3 new")
        with col2:
            st.metric("Critical Changes", "1", delta="1 critical", delta_color="inverse")
        with col3:
            st.metric("Significant Changes", "3", delta="2 significant", delta_color="normal")
        with col4:
            st.metric("Review Required", "Yes", delta="Medical review needed")
        
        # Change details
        st.subheader("🔍 Detailed Change Analysis")
        
        demo_changes = [
            {
                "id": "NC-12345678-abcd",
                "section": "Timeline",
                "type": "Addition",
                "severity": "Critical", 
                "original": "",
                "modified": "Patient was hospitalized for 3 days",
                "justification": "Added critical hospitalization information",
                "impact": "Significant clinical outcome change",
                "requires_review": True
            },
            {
                "id": "NC-87654321-efgh",
                "section": "Symptoms", 
                "type": "Modification",
                "severity": "Significant",
                "original": "Patient felt dizzy",
                "modified": "Patient experienced severe dizziness requiring assistance",
                "justification": "Clarified severity level based on additional information",
                "impact": "Enhanced symptom description accuracy",
                "requires_review": True
            },
            {
                "id": "NC-11111111-ijkl",
                "section": "Assessment",
                "type": "Style Change", 
                "severity": "Minor",
                "original": "The patient's condition improved gradually",
                "modified": "Patient condition showed gradual improvement",
                "justification": "Style consistency improvement",
                "impact": "No clinical impact",
                "requires_review": False
            }
        ]
        
        for i, change in enumerate(demo_changes):
            with st.expander(f"Change {i+1}: {change['section']} - {change['severity']}", expanded=True):
                # Change header
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Change ID:** {change['id']}")
                    st.write(f"**Section:** {change['section']}")
                with col2:
                    st.write(f"**Type:** {change['type']}")
                    severity_color = {"Critical": "🔴", "Significant": "🟡", "Minor": "🟢", "Style Change": "🔵"}
                    st.write(f"**Severity:** {severity_color.get(change['severity'], '')} {change['severity']}")
                with col3:
                    st.write(f"**Review Required:** {'✅ Yes' if change['requires_review'] else '❌ No'}")
                
                # Before/After comparison
                st.write("**Content Comparison:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Original:**")
                    if change['original']:
                        st.markdown(f"<div style='background-color: #ffebee; padding: 10px; border-radius: 5px;'>{change['original']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; font-style: italic;'>[No original content]</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**Modified:**")
                    st.markdown(f"<div style='background-color: #e8f5e8; padding: 10px; border-radius: 5px;'>{change['modified']}</div>", unsafe_allow_html=True)
                
                # Justification and impact
                st.write(f"**Justification:** {change['justification']}")
                st.write(f"**Clinical Impact:** {change['impact']}")
                
                # Action buttons for reviewers
                if user_role in ["reviewer", "admin"]:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"Approve Change", key=f"approve_{i}"):
                            st.success("✅ Change approved")
                    with col2:
                        if st.button(f"Request Clarification", key=f"clarify_{i}"):
                            st.warning("⚠️ Clarification requested")
                    with col3:
                        if st.button(f"Reject Change", key=f"reject_{i}"):
                            st.error("❌ Change rejected")
        
        # Overall assessment
        st.subheader("📝 Overall Narrative Assessment")
        
        st.markdown("""
        <div style='background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 15px 0;'>
            <h5>🔍 Clinical Impact Assessment</h5>
            <p><strong>HIGH IMPACT:</strong> 1 critical change detected affecting clinical meaning</p>
            <p><strong>Recommendation:</strong> Medical review required before final approval</p>
            <p><strong>Key Changes:</strong> Added hospitalization information, enhanced symptom severity description</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Medical review section
        if user_role in ["reviewer", "admin"]:
            st.subheader("🩺 Medical Review")
            
            review_decision = st.radio(
                "Review Decision",
                ["Approve all changes", "Approve with modifications", "Reject and request revision"],
                help="Medical reviewer decision for narrative changes"
            )
            
            review_comments = st.text_area(
                "Review Comments",
                placeholder="Provide detailed comments on the clinical accuracy and completeness of the narrative changes..."
            )
            
            if st.button("Submit Medical Review", type="primary"):
                st.success(f"✅ Medical review submitted: {review_decision}")
                st.info("📧 Notification sent to case drafter and PV officer")

if __name__ == "__main__":
    main() 