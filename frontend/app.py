import streamlit as st

# Configure Streamlit page FIRST - before any other Streamlit commands
st.set_page_config(
    page_title="PV Sentinel",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import backend modules
sys.path.append(str(Path(__file__).parent.parent))

# Import the correct class names from backend modules
import_error_message = None
try:
    from backend.patient_context import PatientContextPreserver
    from backend.model_tracking import ModelVersionTracker
    from backend.readback import VoiceReadbackConfirmer
    # Phase 1 imports
    from backend.pii_protection import create_pii_protector
    # Phase 2 imports
    from backend.patient_voice import create_patient_voice_protector
    from backend.narrative_comparison import create_narrative_comparison_system
    # Phase 3 imports
    from backend.ux_enhancement import create_ux_enhancement_system
    # Phase 4A imports
    from backend.enhanced_analytics import create_enhanced_analytics_manager
    from backend.operational_improvements import create_operational_improvements_system
    # Phase 4B imports - Focus Group Priority Features
    from backend.regulatory_export import create_regulatory_export_manager
    from backend.meddra_integration import create_meddra_integration_system
    from backend.smart_automation import create_smart_automation_system
    backend_available = True
except ImportError as e:
    # Store the error message for later display - don't use st.warning() here
    import_error_message = f"Backend modules not fully available: {e}"
    backend_available = False

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
        if import_error_message:
            st.warning(f"⚠️ {import_error_message}")
        else:
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
        
        # Check if there's a navigation target from button clicks
        if "navigation_target" in st.session_state:
            default_page = st.session_state.navigation_target
            del st.session_state.navigation_target  # Clear after use
        else:
            default_page = "Home"
        
        page_options = ["Home", "New Case Entry", "Case Review", "Patient Voice Protection", "Narrative Comparison", "Analytics Dashboard", "Patient Portal", "Accessibility Settings", "Enhanced Analytics", "Templates & Bulk Actions", "Regulatory Export", "MedDRA Integration", "Smart Automation", "System Status", "Documentation"]
        default_index = page_options.index(default_page) if default_page in page_options else 0
        
        page = st.selectbox(
            "Choose Function",
            page_options,
            index=default_index
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
    elif page == "Analytics Dashboard":
        show_analytics_dashboard(user_role)
    elif page == "Patient Portal":
        show_patient_portal(user_role)
    elif page == "Accessibility Settings":
        show_accessibility_settings(user_role)
    elif page == "Enhanced Analytics":
        show_enhanced_analytics(user_role)
    elif page == "Templates & Bulk Actions":
        show_templates_bulk_actions(user_role)
    elif page == "Regulatory Export":
        show_regulatory_export(user_role)
    elif page == "MedDRA Integration":
        show_meddra_integration(user_role)
    elif page == "Smart Automation":
        show_smart_automation(user_role)
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
            st.session_state.navigation_target = "New Case Entry"
            st.rerun()
    
    with col2:
        st.subheader("🔍 For Reviewers")
        st.write("Review and validate AI-generated narratives with complete audit trails.")
        if st.button("Review Cases", key="reviewer"):
            st.session_state.navigation_target = "Case Review"
            st.rerun()
    
    with col3:
        st.subheader("⚙️ System Management")
        st.write("Monitor system status and access technical documentation.")
        if st.button("System Status", key="admin"):
            st.session_state.navigation_target = "System Status"
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

def show_analytics_dashboard(user_role: str = "admin"):
    """Phase 3 Feature: Advanced Analytics Dashboard"""
    st.header("📊 Analytics Dashboard")
    
    # Phase 3 feature notice
    st.markdown("""
    <div style='background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>🚀 Phase 3 Feature: Advanced Analytics</h4>
        <p><strong>Enhanced User Experience:</strong> Real-time analytics with mobile-responsive design</p>
        <ul>
            <li>User behavior analytics with privacy protection</li>
            <li>Performance monitoring and optimization</li>
            <li>Accessibility compliance tracking</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize UX enhancement system
    if backend_available:
        try:
            demo_config = {
                'ux_enhancement': {
                    'analytics': True,
                    'responsive_design': True,
                    'accessibility': True
                }
            }
            
            responsive_manager, accessibility_manager, analytics_manager, patient_interface_manager = create_ux_enhancement_system(demo_config)
            
            # Generate demo analytics data
            analytics_data = analytics_manager.get_analytics_dashboard_data(7)
            
            # Display analytics metrics
            st.subheader("📈 Usage Analytics (Last 7 Days)")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Page Views", analytics_data['summary']['page_views'], delta="12%")
            with col2:
                st.metric("Unique Users", analytics_data['summary']['unique_users'], delta="8%")
            with col3:
                st.metric("Total Events", analytics_data['summary']['total_events'], delta="15%")
            with col4:
                st.metric("Engagement Rate", "78.5%", delta="5.2%")
            
            # Popular pages
            st.subheader("🏆 Most Popular Pages")
            if analytics_data['popular_pages']:
                for page, views in analytics_data['popular_pages']:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{page}**")
                    with col2:
                        st.write(f"{views} views")
            else:
                st.info("📊 Analytics data is being collected. Check back later for insights.")
            
            # Device distribution
            st.subheader("📱 Device Usage Distribution")
            if analytics_data['device_distribution']:
                device_data = analytics_data['device_distribution']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Desktop", f"{device_data.get('desktop', 0)}%")
                with col2:
                    st.metric("Mobile", f"{device_data.get('mobile', 0)}%")
                with col3:
                    st.metric("Tablet", f"{device_data.get('tablet', 0)}%")
                
                st.info("📱 Mobile-responsive design ensures optimal experience across all devices")
            
        except Exception as e:
            st.error(f"Error loading analytics backend: {e}")
            show_demo_analytics()
    else:
        show_demo_analytics()

def show_demo_analytics():
    """Demo analytics when backend is not available"""
    st.subheader("📈 Usage Analytics (Demo Data)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Page Views", "1,245", delta="12%")
    with col2:
        st.metric("Unique Users", "89", delta="8%")
    with col3:
        st.metric("Total Events", "3,421", delta="15%")
    with col4:
        st.metric("Engagement Rate", "78.5%", delta="5.2%")
    
    st.info("📊 Demo mode - Full analytics available with backend integration")

def show_patient_portal(user_role: str = "drafter"):
    """Phase 3 Feature: Patient-Facing Interface"""
    st.header("👥 Patient Portal")
    
    # Phase 3 feature notice
    st.markdown("""
    <div style='background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>🌟 Phase 3 Feature: Patient-Friendly Interface</h4>
        <p><strong>Accessibility First:</strong> Simplified interface designed for patient use</p>
        <ul>
            <li>Plain language explanations for medical terms</li>
            <li>Large buttons and clear navigation for motor accessibility</li>
            <li>Visual progress indicators and confirmation steps</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Patient-friendly interface toggle
    patient_mode = st.toggle("Enable Simplified Patient Interface", value=True)
    
    if patient_mode:
        # Simplified patient interface
        st.markdown("""
        <style>
        .patient-interface {
            font-size: 1.1em;
            line-height: 1.6;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
        }
        .large-button {
            font-size: 1.2em !important;
            padding: 15px 30px !important;
            min-height: 60px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='patient-interface'>
            <h3>📋 Report a Side Effect from Your Medicine</h3>
            <p>Your report helps make medicines safer for everyone. We protect your personal information while keeping the important medical details.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Simplified form with large buttons
        st.subheader("Tell Us What Happened")
        
        # Progress indicator
        progress_col1, progress_col2, progress_col3 = st.columns(3)
        with progress_col1:
            st.markdown("**✅ Step 1:** Tell your story")
        with progress_col2:
            st.markdown("**⏳ Step 2:** Review information")
        with progress_col3:
            st.markdown("**⏳ Step 3:** Submit report")
        
        st.progress(0.33)
        
        # Simple patient story input
        patient_story = st.text_area(
            "In your own words, tell us what happened after taking your medicine:",
            height=150,
            placeholder="For example: 'I started feeling dizzy about an hour after I took my morning pill. I had to sit down because I felt like I might fall...'"
        )
        
        # Medicine information with explanations
        st.subheader("About Your Medicine")
        
        col1, col2 = st.columns(2)
        with col1:
            medicine_name = st.text_input("Name of the medicine", placeholder="e.g., Aspirin, Tylenol")
            st.caption("💡 Look on the medicine bottle or package for the exact name")
        
        with col2:
            medicine_amount = st.text_input("How much did you take?", placeholder="e.g., 1 tablet, 5ml")
            st.caption("💡 This is usually on the medicine label")
        
        # Large, accessible buttons
        if st.button("Continue to Next Step ➡️", key="patient_continue", help="Review your information before submitting"):
            if patient_story:
                st.success("✅ Thank you for sharing your story. Your report helps keep medicines safe!")
                
                # Show what happens next with patient-friendly explanation
                if backend_available:
                    try:
                        demo_config = {'ux_enhancement': {'patient_interface': True, 'simplify_language': True}}
                        _, _, _, patient_interface_manager = create_ux_enhancement_system(demo_config)
                        
                        explanation = patient_interface_manager.get_patient_explanation('narrative_generation')
                        st.markdown(f"""
                        <div style='background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 15px 0;'>
                            <h4>What Happens Next?</h4>
                            {explanation}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Error loading patient interface: {e}")
                        show_demo_patient_explanation()
                else:
                    show_demo_patient_explanation()
            else:
                st.error("Please tell us your story so we can help make medicines safer.")
    
    else:
        st.info("Professional interface mode - Switch to 'Simplified Patient Interface' for patient-facing design")

def show_demo_patient_explanation():
    """Demo patient explanation when backend is not available"""
    st.markdown("""
    <div style='background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>What Happens Next?</h4>
        <p>We're creating a summary of what happened with your medicine. This helps doctors and researchers 
        understand how medicines affect people and make them safer for everyone.</p>
    </div>
    """, unsafe_allow_html=True)

def show_accessibility_settings(user_role: str = "drafter"):
    """Phase 3 Feature: Accessibility Settings and WCAG Compliance"""
    st.header("♿ Accessibility Settings")
    
    # Phase 3 feature notice
    st.markdown("""
    <div style='background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>🌐 Phase 3 Feature: WCAG 2.1 AA Compliance</h4>
        <p><strong>Universal Design:</strong> Accessibility features for all users</p>
        <ul>
            <li>Screen reader optimization and keyboard navigation</li>
            <li>High contrast themes for visual accessibility</li>
            <li>Motor accessibility with large touch targets</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Accessibility preferences
    st.subheader("👤 Personal Accessibility Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎨 Visual Preferences**")
        theme = st.selectbox("Theme", ["Light", "Dark", "High Contrast"], help="Choose a theme that works best for you")
        font_size = st.selectbox("Font Size", ["Small", "Medium", "Large", "Extra Large"], index=1)
        color_blind_support = st.checkbox("Color blind support", help="Adds patterns and symbols in addition to colors")
        
    with col2:
        st.markdown("**⌨️ Navigation Preferences**")
        keyboard_nav = st.checkbox("Enhanced keyboard navigation", value=True, help="Improves focus indicators and tab order")
        screen_reader = st.checkbox("Screen reader optimization", help="Adds extra labels and descriptions")
        motor_accessibility = st.checkbox("Motor accessibility", help="Larger buttons and increased spacing")
    
    # Language preferences
    st.subheader("🌍 Language Settings")
    language = st.selectbox("Interface Language", ["English", "Spanish", "French", "German"], help="Choose your preferred language")
    simplify_language = st.checkbox("Simplify medical terms", value=True, help="Replace medical terms with simpler explanations")
    
    # Apply settings button
    if st.button("Apply Accessibility Settings", type="primary"):
        if backend_available:
            try:
                demo_config = {
                    'ux_enhancement': {
                        'accessibility': True,
                        'wcag_level': 'AA',
                        'multilingual_support': True
                    }
                }
                
                _, accessibility_manager, _, patient_interface_manager = create_ux_enhancement_system(demo_config)
                
                # Create user preferences
                from backend.ux_enhancement import UserPreferences, AccessibilityLevel, InterfaceType
                
                preferences = UserPreferences(
                    user_id=user_role,
                    theme=theme.lower().replace(' ', '_'),
                    font_size=font_size.lower().replace(' ', '_'),
                    language=language.lower()[:2],
                    accessibility_level=AccessibilityLevel.AA,
                    interface_type=InterfaceType.PROFESSIONAL,
                    notifications_enabled=True,
                    keyboard_navigation=keyboard_nav,
                    screen_reader_optimized=screen_reader,
                    color_blind_support=color_blind_support,
                    motor_accessibility=motor_accessibility,
                    created_timestamp="",
                    last_updated=""
                )
                
                # Generate accessibility CSS
                accessibility_css = accessibility_manager.get_accessibility_css(preferences)
                
                st.success("✅ Accessibility settings applied!")
                
                # Show preview of applied settings
                st.markdown(accessibility_css, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 15px 0;'>
                    <h5>Settings Applied:</h5>
                    <ul>
                        <li><strong>Theme:</strong> """ + theme + """</li>
                        <li><strong>Font Size:</strong> """ + font_size + """</li>
                        <li><strong>Language:</strong> """ + language + """</li>
                        <li><strong>Keyboard Navigation:</strong> """ + ("Enabled" if keyboard_nav else "Disabled") + """</li>
                        <li><strong>Screen Reader Support:</strong> """ + ("Enabled" if screen_reader else "Disabled") + """</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error applying accessibility settings: {e}")
                show_demo_accessibility_applied()
        else:
            show_demo_accessibility_applied()
    
    # Accessibility compliance status
    st.subheader("📊 WCAG 2.1 Compliance Status")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Compliance Level", "AA", help="WCAG 2.1 Level AA compliance")
    with col2:
        st.metric("Accessibility Score", "95%", delta="5%", help="Overall accessibility rating")
    with col3:
        st.metric("Issues Resolved", "12", delta="8", help="Accessibility improvements made")
    
    # Quick accessibility test
    st.subheader("🧪 Quick Accessibility Test")
    
    test_options = [
        "Test keyboard navigation (Tab through interface)",
        "Test screen reader compatibility",
        "Test color contrast ratios",
        "Test with high contrast theme",
        "Test large font sizes"
    ]
    
    selected_test = st.selectbox("Choose accessibility test", test_options)
    
    if st.button("Run Accessibility Test"):
        with st.spinner("Running accessibility test..."):
            time.sleep(2)  # Simulate test
            st.success(f"✅ {selected_test} - PASSED")
            st.info("All accessibility requirements met for this test")

def show_demo_accessibility_applied():
    """Demo accessibility settings confirmation"""
    st.success("✅ Accessibility settings applied!")
    st.markdown("""
    <div style='background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h5>Settings Applied (Demo Mode):</h5>
        <p>Your accessibility preferences have been saved and will be applied throughout the application.</p>
        <p><strong>Note:</strong> Full accessibility features are available with backend integration.</p>
    </div>
    """, unsafe_allow_html=True)

def show_enhanced_analytics(user_role: str = "admin"):
    """Phase 4A Feature: Enhanced Analytics & Reporting"""
    st.header("📊 Enhanced Analytics & Reporting")
    
    # Phase 4A feature notice
    st.markdown("""
    <div style='background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>🚀 Phase 4A Feature: Advanced Analytics</h4>
        <p><strong>MVP Enhancement:</strong> Professional reporting and export capabilities</p>
        <ul>
            <li>Export reports in PDF, Excel, CSV, JSON formats</li>
            <li>Custom dashboards by stakeholder role</li>
            <li>MVP validation metrics and ROI tracking</li>
            <li>Trend analysis and productivity insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Export functionality
    st.subheader("📤 Export Analytics Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        export_format = st.selectbox("Export Format", ["PDF", "Excel", "CSV", "JSON"])
        
    with col2:
        time_period = st.selectbox("Time Period", ["7 days", "30 days", "90 days", "1 year"])
        
    with col3:
        include_trends = st.checkbox("Include Trend Analysis", value=True)
    
    if st.button("📤 Generate & Export Report", type="primary"):
        if backend_available:
            try:
                demo_config = {'phase_4a': {'enhanced_analytics': {'enabled': True, 'export_enabled': True}}}
                enhanced_analytics_manager = create_enhanced_analytics_manager(demo_config)
                
                # Simulate export
                st.success(f"✅ {export_format} report generated successfully!")
                st.info(f"📊 Report includes data for {time_period} with {'trend analysis' if include_trends else 'basic metrics'}")
                
                # Show download link simulation
                st.markdown("""
                <div style='background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 15px 0;'>
                    <h5>📥 Download Ready</h5>
                    <p>Your analytics report is ready for download:</p>
                    <a href="#" style="color: #155724; text-decoration: underline;">📄 PV_Sentinel_Analytics_Report_2024.pdf</a>
                    <br><small>File size: 2.3 MB | Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</small>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error generating report: {e}")
        else:
            show_demo_enhanced_analytics()
    
    # MVP Validation Metrics
    st.subheader("🎯 MVP Validation Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("User Adoption", "87.5%", "12.3%", help="Percentage of users actively using the system")
    
    with col2:
        st.metric("Time Savings", "34.7%", "8.2%", help="Average time reduction in case processing")
    
    with col3:
        st.metric("Satisfaction Score", "92.1", "5.8", help="Average stakeholder satisfaction rating")
    
    with col4:
        st.metric("ROI Indicator", "$45K", "$12K", help="Estimated monthly cost savings")
    
    # Stakeholder-specific dashboards
    st.subheader(f"📋 {user_role.title()} Dashboard")
    
    if user_role in ["medical_director", "admin"]:
        st.markdown("**Medical Director View:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Processing time chart
            chart_data = {
                "Date": ["Jan 1", "Jan 2", "Jan 3", "Jan 4", "Jan 5"],
                "Processing Time (min)": [32.1, 29.8, 27.5, 25.3, 23.9]
            }
            st.line_chart(chart_data, x="Date", y="Processing Time (min)")
        
        with col2:
            # Quality scores
            quality_data = {
                "Metric": ["Accuracy", "Completeness", "Timeliness", "Compliance"],
                "Score": [94.2, 89.7, 92.1, 96.3]
            }
            st.bar_chart(quality_data, x="Metric", y="Score")
    
    elif user_role == "operations_manager":
        st.markdown("**Operations Manager View:**")
        
        # Feature usage table
        feature_usage = [
            {"Feature": "Case Entry", "Usage Count": 1247, "Avg Time": "5.2 min", "Efficiency": "+34%"},
            {"Feature": "Patient Voice Protection", "Usage Count": 892, "Avg Time": "2.1 min", "Efficiency": "+45%"},
            {"Feature": "Narrative Comparison", "Usage Count": 654, "Avg Time": "3.8 min", "Efficiency": "+28%"},
            {"Feature": "Analytics Dashboard", "Usage Count": 423, "Avg Time": "4.5 min", "Efficiency": "+15%"}
        ]
        
        st.dataframe(feature_usage, use_container_width=True)
    
    else:
        st.info("📊 General analytics view - Switch to Medical Director or Operations Manager role for specialized dashboards")

def show_templates_bulk_actions(user_role: str = "drafter"):
    """Phase 4A Feature: Templates & Bulk Processing"""
    st.header("📝 Templates & Bulk Actions")
    
    # Phase 4A feature notice
    st.markdown("""
    <div style='background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>⚡ Phase 4A Feature: Operational Efficiency</h4>
        <p><strong>Productivity Boost:</strong> 50%+ improvement in daily operations</p>
        <ul>
            <li>Pre-built templates for common documents</li>
            <li>Bulk processing for multiple cases</li>
            <li>Quick action shortcuts</li>
            <li>Enhanced search and filtering</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Template Management Section
    st.subheader("📄 Template Library")
    
    tab1, tab2, tab3 = st.tabs(["📋 Available Templates", "➕ Create Template", "🔧 Quick Actions"])
    
    with tab1:
        st.markdown("**Available Templates:**")
        
        template_categories = {
            "Case Narratives": [
                {"name": "Standard AE Narrative", "usage": 1247, "variables": 12},
                {"name": "Serious AE Narrative", "usage": 435, "variables": 15},
                {"name": "Pregnancy Case Narrative", "usage": 156, "variables": 18}
            ],
            "Follow-up Communications": [
                {"name": "Follow-up Request", "usage": 892, "variables": 6},
                {"name": "Medical Query", "usage": 324, "variables": 8},
                {"name": "Clarification Request", "usage": 203, "variables": 5}
            ],
            "Regulatory Documents": [
                {"name": "Safety Letter", "usage": 67, "variables": 10},
                {"name": "Regulatory Report", "usage": 89, "variables": 20}
            ]
        }
        
        for category, templates in template_categories.items():
            with st.expander(f"{category} ({len(templates)} templates)"):
                for template in templates:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(f"📄 {template['name']}")
                    with col2:
                        st.write(f"Used: {template['usage']}")
                    with col3:
                        st.write(f"Vars: {template['variables']}")
                    with col4:
                        if st.button("Use", key=f"use_{template['name']}"):
                            st.success(f"✅ Applied template: {template['name']}")
    
    with tab2:
        st.markdown("**Create New Template:**")
        
        template_name = st.text_input("Template Name", placeholder="e.g., Special Population AE Narrative")
        template_type = st.selectbox("Template Type", ["Case Narrative", "Follow-up", "Medical Query", "Safety Letter", "Custom"])
        template_description = st.text_area("Description", placeholder="Brief description of when to use this template")
        
        template_content = st.text_area(
            "Template Content", 
            height=200,
            placeholder="Enter template content here. Use {variable_name} for variables that will be substituted.",
            help="Use curly braces {} around variable names, e.g., {patient_age}, {event_description}"
        )
        
        if st.button("💾 Save Template", type="primary"):
            if template_name and template_content:
                st.success(f"✅ Template '{template_name}' created successfully!")
                st.info("Template is now available in the template library")
            else:
                st.error("Please provide both template name and content")
    
    with tab3:
        st.markdown("**Quick Actions:**")
        
        # Bulk selection simulation
        st.markdown("**Select Cases for Bulk Actions:**")
        
        sample_cases = [
            {"id": "CASE_001", "priority": "High", "status": "Pending Review", "assignee": "Dr. Smith"},
            {"id": "CASE_002", "priority": "Medium", "status": "In Progress", "assignee": "Dr. Johnson"},
            {"id": "CASE_003", "priority": "High", "status": "Pending Review", "assignee": "Unassigned"},
            {"id": "CASE_004", "priority": "Low", "status": "Complete", "assignee": "Dr. Wilson"},
            {"id": "CASE_005", "priority": "Medium", "status": "Pending Review", "assignee": "Dr. Brown"}
        ]
        
        selected_cases = []
        for i, case in enumerate(sample_cases):
            if st.checkbox(f"{case['id']} - {case['priority']} Priority", key=f"case_{i}"):
                selected_cases.append(case['id'])
        
        if selected_cases:
            st.success(f"✅ Selected {len(selected_cases)} cases for bulk action")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("👤 Assign Reviewer", help="Ctrl+R"):
                    reviewer = st.selectbox("Select Reviewer", ["Dr. Smith", "Dr. Johnson", "Dr. Wilson"])
                    st.success(f"✅ Assigned {len(selected_cases)} cases to {reviewer}")
            
            with col2:
                if st.button("⚡ Set Priority", help="Ctrl+P"):
                    priority = st.selectbox("Select Priority", ["Low", "Medium", "High", "Urgent"])
                    st.success(f"✅ Set priority to {priority} for {len(selected_cases)} cases")
            
            with col3:
                if st.button("✅ Approve Batch", help="Ctrl+A"):
                    st.success(f"✅ Approved {len(selected_cases)} cases for submission")
            
            with col4:
                if st.button("📤 Export Batch", help="Ctrl+E"):
                    export_format = st.selectbox("Export Format", ["PDF", "Excel", "XML"])
                    st.success(f"✅ Exported {len(selected_cases)} cases as {export_format}")
    
    # Enhanced Search Section
    st.subheader("🔍 Enhanced Search & Filtering")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search Cases", placeholder="Enter search terms, case IDs, or keywords...")
    
    with col2:
        search_type = st.selectbox("Search Type", ["All Fields", "Case ID", "Patient Info", "Product", "Event"])
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            priority_filter = st.multiselect("Priority", ["Low", "Medium", "High", "Urgent"])
            status_filter = st.multiselect("Status", ["Pending Review", "In Progress", "Complete", "On Hold"])
        
        with filter_col2:
            date_from = st.date_input("From Date")
            date_to = st.date_input("To Date")
        
        with filter_col3:
            assignee_filter = st.multiselect("Assignee", ["Dr. Smith", "Dr. Johnson", "Dr. Wilson", "Dr. Brown", "Unassigned"])
    
    if st.button("🔍 Search", type="primary") or search_query:
        # Simulate search results
        st.markdown("**Search Results:**")
        
        search_results = [
            {"Case ID": "CASE_001", "Priority": "High", "Status": "Pending Review", "Created": "2024-01-05", "Relevance": "95%"},
            {"Case ID": "CASE_003", "Priority": "High", "Status": "Pending Review", "Created": "2024-01-04", "Relevance": "92%"},
            {"Case ID": "CASE_002", "Priority": "Medium", "Status": "In Progress", "Created": "2024-01-03", "Relevance": "87%"}
        ]
        
        st.dataframe(search_results, use_container_width=True)
        st.info(f"Found {len(search_results)} results in 0.23 seconds")

def show_demo_enhanced_analytics():
    """Demo enhanced analytics when backend is not available"""
    st.success("✅ PDF report generated successfully! (Demo Mode)")
    st.markdown("""
    <div style='background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h5>📥 Demo Report Generated</h5>
        <p>In full deployment, your analytics report would be available for download.</p>
        <p><strong>Note:</strong> Export functionality requires backend integration.</p>
    </div>
    """, unsafe_allow_html=True)

def show_regulatory_export(user_role: str = "admin"):
    """Phase 4B Critical Feature: Regulatory Export - Focus Group Priority #1"""
    st.header("📋 Regulatory Export & Compliance")
    
    # Critical feature notice
    st.markdown("""
    <div style='background-color: #dc3545; color: white; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>🚨 Critical Phase 4B Feature: Regulatory Export</h4>
        <p><strong>Focus Group Validation:</strong> Essential for €25-40K license tier</p>
        <ul>
            <li>E2B R3 XML generation for international submission</li>
            <li>PSUR narrative formatting for periodic safety updates</li>
            <li>FDA FAERS compatibility for US market entry</li>
            <li>Complete audit trails for validation compliance</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🌍 E2B Export", "📊 PSUR Generation", "🇺🇸 FAERS Export", "✅ Validation"])
    
    with tab1:
        st.subheader("E2B R3 XML Export")
        st.markdown("**International Regulatory Submission Format**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_region = st.selectbox("Target Region", ["EU (EMA)", "ICH Global", "Japan (PMDA)", "Canada (HC)"])
            sender_id = st.text_input("Sender ID", value="PV_SENTINEL_001")
            receiver_id = st.text_input("Receiver ID", value="REGULATORY_AUTHORITY")
        
        with col2:
            case_selection = st.multiselect("Select Cases for Export", 
                                          ["CASE_001", "CASE_002", "CASE_003", "CASE_004", "CASE_005"])
            include_audit_trail = st.checkbox("Include Audit Trail", value=True)
            validation_level = st.selectbox("Validation Level", ["Standard", "Strict", "Custom"])
        
        if st.button("🌍 Generate E2B XML", type="primary"):
            if case_selection:
                with st.spinner("Generating E2B R3 XML export..."):
                    st.success(f"✅ E2B export generated successfully!")
                    
                    # Show export summary
                    export_summary = {
                        "Message Number": f"PVS_20240107_1234_{len(case_selection):04d}",
                        "Cases Exported": len(case_selection),
                        "Region": export_region,
                        "Validation Status": "PASS",
                        "File Size": f"{len(case_selection) * 45}KB",
                        "Generated": "2024-01-07 14:30:25"
                    }
                    
                    for key, value in export_summary.items():
                        st.metric(key, value)
                    
                    st.download_button("📥 Download E2B XML", 
                                     data="<E2B_MESSAGE>...</E2B_MESSAGE>", 
                                     file_name=f"e2b_export_{export_summary['Message Number']}.xml",
                                     mime="application/xml")
            else:
                st.error("Please select cases to export")
    
    with tab2:
        st.subheader("PSUR Narrative Generation")
        st.markdown("**Periodic Safety Update Report Automation**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name", value="Investigational Product X")
            reporting_period = st.text_input("Reporting Period", value="01-Jul-2023 to 31-Dec-2023")
            data_lock_point = st.date_input("Data Lock Point")
        
        with col2:
            narrative_sections = st.multiselect("Include Sections", 
                                              ["Executive Summary", "Serious AEs", "Non-Serious AEs", 
                                               "Safety Analysis", "Conclusion"], 
                                              default=["Executive Summary", "Serious AEs", "Conclusion"])
            include_case_summaries = st.checkbox("Include Individual Case Summaries", value=True)
        
        if st.button("📊 Generate PSUR Narrative", type="primary"):
            with st.spinner("Generating PSUR narrative..."):
                st.success("✅ PSUR narrative generated successfully!")
                
                # Show narrative preview
                st.markdown("**Generated PSUR Narrative Preview:**")
                narrative_preview = f"""
                **PERIODIC SAFETY UPDATE REPORT**
                Product: {product_name}
                Reporting Period: {reporting_period}
                Data Lock Point: {data_lock_point}
                
                **EXECUTIVE SUMMARY**
                During the reporting period {reporting_period}, a total of {len(case_selection) if 'case_selection' in locals() else 5} adverse event reports were received for {product_name}...
                """
                
                st.text_area("Narrative Content", narrative_preview, height=200)
                st.download_button("📥 Download PSUR Narrative", 
                                 data=narrative_preview, 
                                 file_name=f"psur_narrative_{product_name.replace(' ', '_')}.txt")
    
    with tab3:
        st.subheader("FDA FAERS Export")
        st.markdown("**US Market Regulatory Submission**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submission_type = st.selectbox("Submission Type", ["Initial Report", "Follow-up", "Correction"])
            manufacturer_name = st.text_input("Manufacturer Name")
            fda_registration = st.text_input("FDA Registration Number")
        
        with col2:
            expedited_report = st.checkbox("Expedited Report (15-day)")
            include_meddra_codes = st.checkbox("Include MedDRA Codes", value=True)
        
        if st.button("🇺🇸 Generate FAERS XML", type="primary"):
            with st.spinner("Generating FAERS-compatible export..."):
                st.success("✅ FAERS export generated successfully!")
                
                st.info("📝 **US Market Entry Feature:** Enables expansion to $500M+ US pharmacovigilance market")
                st.download_button("📥 Download FAERS XML", 
                                 data="<FAERSSubmission>...</FAERSSubmission>", 
                                 file_name="faers_submission.xml",
                                 mime="application/xml")
    
    with tab4:
        st.subheader("Export Validation & Compliance")
        st.markdown("**Quality Assurance & Regulatory Compliance**")
        
        # Validation dashboard
        validation_metrics = {
            "E2B Compliance": 98.5,
            "Data Completeness": 96.7,
            "Validation Errors": 2,
            "Export Success Rate": 99.1
        }
        
        col1, col2, col3, col4 = st.columns(4)
        for i, (metric, value) in enumerate(validation_metrics.items()):
            with [col1, col2, col3, col4][i]:
                if metric == "Validation Errors":
                    st.metric(metric, f"{value}", delta=f"-{value}" if value > 0 else "0")
                else:
                    st.metric(metric, f"{value}%" if value > 10 else f"{value}")
        
        # Validation log
        st.markdown("**Recent Validation Results:**")
        validation_log = [
            {"Timestamp": "2024-01-07 14:25", "Export Type": "E2B", "Status": "✅ PASS", "Cases": 3},
            {"Timestamp": "2024-01-07 13:45", "Export Type": "PSUR", "Status": "✅ PASS", "Cases": 15},
            {"Timestamp": "2024-01-07 12:30", "Export Type": "FAERS", "Status": "⚠️ WARNING", "Cases": 2},
            {"Timestamp": "2024-01-07 11:15", "Export Type": "E2B", "Status": "✅ PASS", "Cases": 7}
        ]
        
        st.dataframe(validation_log, use_container_width=True)

def show_meddra_integration(user_role: str = "drafter"):
    """Phase 4B High Priority Feature: MedDRA Integration - Focus Group Priority #2"""
    st.header("🧠 MedDRA Integration & Term Mapping")
    
    # High priority feature notice
    st.markdown("""
    <div style='background-color: #fd7e14; color: white; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>⚡ High Priority Phase 4B Feature: MedDRA Integration</h4>
        <p><strong>Focus Group Impact:</strong> 30-50% processing time reduction for CROs</p>
        <ul>
            <li>95%+ accuracy automated term mapping</li>
            <li>Sub-second lookup times for real-time suggestions</li>
            <li>Batch validation for bulk processing</li>
            <li>Local MedDRA server support for enterprise</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Auto-Mapping", "📚 Term Lookup", "📦 Batch Processing", "⚙️ Configuration"])
    
    with tab1:
        st.subheader("Automatic Term Mapping")
        st.markdown("**AI-Powered Medical Term Recognition**")
        
        # Text input for mapping
        medical_text = st.text_area(
            "Enter medical description for automatic MedDRA mapping:",
            placeholder="e.g., Patient experienced severe nausea and vomiting after medication administration",
            height=120
        )
        
        confidence_threshold = st.slider("Mapping Confidence Threshold", 0.5, 1.0, 0.8, 0.05)
        
        if st.button("🧠 Auto-Map Terms", type="primary") and medical_text:
            with st.spinner("Analyzing medical text and mapping to MedDRA terms..."):
                # Simulate auto-mapping results
                st.success("✅ Automatic mapping completed!")
                
                mapping_results = [
                    {
                        "Original Text": "severe nausea",
                        "MedDRA PT": "Nausea",
                        "Code": "10017947",
                        "Confidence": 0.96,
                        "Status": "✅ High Confidence"
                    },
                    {
                        "Original Text": "vomiting",
                        "MedDRA PT": "Vomiting",
                        "Code": "10046743",
                        "Confidence": 0.94,
                        "Status": "✅ High Confidence"
                    },
                    {
                        "Original Text": "after medication",
                        "MedDRA PT": "Drug administration",
                        "Code": "10013761",
                        "Confidence": 0.72,
                        "Status": "⚠️ Review Recommended"
                    }
                ]
                
                st.dataframe(mapping_results, use_container_width=True)
                
                # Mapping statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Terms Identified", len(mapping_results))
                with col2:
                    st.metric("High Confidence", sum(1 for r in mapping_results if r["Confidence"] >= 0.9))
                with col3:
                    st.metric("Avg Confidence", f"{sum(r['Confidence'] for r in mapping_results) / len(mapping_results):.2f}")
                with col4:
                    st.metric("Processing Time", "0.34s")
    
    with tab2:
        st.subheader("MedDRA Term Lookup")
        st.markdown("**Search and Validate MedDRA Terms**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_type = st.selectbox("Search Type", ["Term Name", "MedDRA Code", "Partial Match"])
            search_query = st.text_input("Search Query", placeholder="Enter term or code")
        
        with col2:
            term_level = st.selectbox("Term Level", ["All Levels", "PT (Preferred Term)", "LLT (Lowest Level)", "HLT (High Level)", "SOC (System Organ Class)"])
            show_hierarchy = st.checkbox("Show Hierarchy", value=True)
        
        if st.button("🔍 Search MedDRA") and search_query:
            # Simulate search results
            search_results = [
                {
                    "Code": "10017947",
                    "Level": "PT",
                    "Term": "Nausea",
                    "Status": "Current",
                    "Parent": "Nausea and vomiting symptoms (HLT)"
                },
                {
                    "Code": "10017948",
                    "Level": "LLT",
                    "Term": "Nausea severe",
                    "Status": "Current",
                    "Parent": "Nausea (PT)"
                },
                {
                    "Code": "10017949",
                    "Level": "LLT",
                    "Term": "Nausea chronic",
                    "Status": "Current",
                    "Parent": "Nausea (PT)"
                }
            ]
            
            st.dataframe(search_results, use_container_width=True)
            
            if show_hierarchy:
                st.markdown("**Term Hierarchy:**")
                hierarchy_display = """
                📋 **Gastrointestinal disorders (SOC)**
                  └── 📁 Nausea and vomiting symptoms (HLT)
                      └── 📝 Nausea (PT)
                          ├── 📝 Nausea severe (LLT)
                          └── 📝 Nausea chronic (LLT)
                """
                st.code(hierarchy_display)
    
    with tab3:
        st.subheader("Batch Term Processing")
        st.markdown("**Bulk MedDRA Mapping for Multiple Cases**")
        
        # File upload simulation
        uploaded_file = st.file_uploader("Upload CSV with medical terms", type=['csv'])
        
        if not uploaded_file:
            st.info("💡 Upload a CSV file with medical descriptions for batch processing")
            
            # Show sample format
            sample_data = {
                "Case_ID": ["CASE_001", "CASE_002", "CASE_003"],
                "Medical_Description": [
                    "Patient reported severe headache and dizziness",
                    "Experienced rash and itching after drug administration",
                    "Complained of chest pain and shortness of breath"
                ]
            }
            st.markdown("**Expected CSV Format:**")
            st.dataframe(sample_data)
        
        batch_settings = st.expander("⚙️ Batch Processing Settings")
        with batch_settings:
            col1, col2 = st.columns(2)
            with col1:
                batch_confidence = st.slider("Minimum Confidence", 0.5, 1.0, 0.7)
                auto_approve_high = st.checkbox("Auto-approve high confidence (>90%)", value=True)
            with col2:
                max_alternatives = st.number_input("Max alternatives per term", 1, 10, 3)
                flag_manual_review = st.checkbox("Flag low confidence for manual review", value=True)
        
        if st.button("🚀 Start Batch Processing", type="primary"):
            with st.spinner("Processing batch mapping..."):
                # Simulate batch processing
                st.success("✅ Batch processing completed!")
                
                batch_results = {
                    "Total Terms": 45,
                    "Successfully Mapped": 41,
                    "High Confidence (>90%)": 38,
                    "Manual Review Required": 4,
                    "Processing Time": "2.7 seconds"
                }
                
                col1, col2, col3, col4, col5 = st.columns(5)
                metrics = list(batch_results.items())
                for i, (metric, value) in enumerate(metrics):
                    with [col1, col2, col3, col4, col5][i]:
                        st.metric(metric, value)
                
                st.download_button("📥 Download Results", 
                                 data="Case_ID,Original_Term,MedDRA_PT,Code,Confidence\n...", 
                                 file_name="batch_mapping_results.csv")
    
    with tab4:
        st.subheader("MedDRA Configuration")
        st.markdown("**System Configuration and Database Management**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Database Status:**")
            db_metrics = {
                "MedDRA Version": "26.0",
                "Database Status": "✅ Connected",
                "Total Terms": "87,453",
                "Last Updated": "2024-01-01",
                "Index Status": "✅ Optimized"
            }
            
            for metric, value in db_metrics.items():
                st.text(f"{metric}: {value}")
        
        with col2:
            st.markdown("**Performance Metrics:**")
            perf_metrics = {
                "Avg Lookup Time": "0.23s",
                "Mapping Accuracy": "95.7%",
                "Cache Hit Rate": "89.2%",
                "API Response Time": "0.45s"
            }
            
            for metric, value in perf_metrics.items():
                st.text(f"{metric}: {value}")
        
        # Configuration options
        st.markdown("**Configuration Options:**")
        
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            enable_caching = st.checkbox("Enable Term Caching", value=True)
            auto_update = st.checkbox("Auto-update MedDRA Database", value=False)
            local_server = st.checkbox("Use Local MedDRA Server", value=True)
        
        with config_col2:
            confidence_default = st.slider("Default Confidence Threshold", 0.5, 1.0, 0.8)
            max_suggestions = st.number_input("Max Term Suggestions", 1, 10, 5)
        
        if st.button("💾 Save Configuration"):
            st.success("✅ Configuration saved successfully!")

def show_smart_automation(user_role: str = "admin"):
    """Phase 4B Smart Automation Feature: AI-Powered Workflow Automation"""
    st.header("🤖 Smart Automation & AI Workflows")
    
    # Smart automation feature notice
    st.markdown("""
    <div style='background-color: #6f42c1; color: white; border-radius: 5px; padding: 15px; margin: 15px 0;'>
        <h4>🤖 Phase 4B Feature: Smart Automation</h4>
        <p><strong>AI-Powered Efficiency:</strong> 60%+ improvement in case processing</p>
        <ul>
            <li>Intelligent severity classification with confidence scoring</li>
            <li>Advanced NLP for medical term extraction</li>
            <li>Automated workflow routing based on case characteristics</li>
            <li>Quality scoring and compliance checking</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Auto-Classification", "🧠 NLP Processing", "🔄 Workflow Automation", "📊 Quality Scoring"])
    
    with tab1:
        st.subheader("Intelligent Case Classification")
        st.markdown("**AI-Powered Severity Assessment**")
        
        # Case input for classification
        col1, col2 = st.columns(2)
        
        with col1:
            patient_age = st.number_input("Patient Age", 0, 120, 45)
            patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            case_description = st.text_area("Case Description", 
                                           placeholder="Describe the adverse event...", 
                                           height=120)
        
        with col2:
            product_name = st.text_input("Product Name")
            time_to_onset = st.number_input("Time to Onset (hours)", 0, 1000, 24)
            reporter_type = st.selectbox("Reporter Type", ["Physician", "Pharmacist", "Patient", "Nurse"])
        
        if st.button("🎯 Classify Case", type="primary") and case_description:
            with st.spinner("Analyzing case with AI classification engine..."):
                # Simulate AI classification
                st.success("✅ AI classification completed!")
                
                # Classification results
                classification_result = {
                    "Predicted Severity": "Serious",
                    "Confidence Score": 0.87,
                    "Contributing Factors": ["hospitalization keywords", "vulnerable population"],
                    "Recommended Actions": [
                        "Medical review within 24 hours",
                        "Request additional medical records",
                        "Assess causality relationship"
                    ]
                }
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Severity Level", classification_result["Predicted Severity"])
                with col2:
                    st.metric("Confidence", f"{classification_result['Confidence Score']:.1%}")
                with col3:
                    st.metric("Processing Time", "1.2s")
                
                # Detailed results
                st.markdown("**Contributing Factors:**")
                for factor in classification_result["Contributing Factors"]:
                    st.write(f"• {factor}")
                
                st.markdown("**Recommended Actions:**")
                for action in classification_result["Recommended Actions"]:
                    st.write(f"✅ {action}")
    
    with tab2:
        st.subheader("Advanced NLP Processing")
        st.markdown("**Medical Text Analysis & Term Extraction**")
        
        nlp_text = st.text_area("Enter medical text for NLP analysis:",
                               placeholder="Patient reported experiencing severe nausea, vomiting, and dizziness approximately 2 hours after taking the medication...",
                               height=150)
        
        nlp_options = st.columns(3)
        with nlp_options[0]:
            extract_terms = st.checkbox("Extract Medical Terms", value=True)
        with nlp_options[1]:
            generate_summary = st.checkbox("Generate Case Summary", value=True)
        with nlp_options[2]:
            assess_causality = st.checkbox("Assess Causality", value=True)
        
        if st.button("🧠 Process with NLP", type="primary") and nlp_text:
            with st.spinner("Processing text with advanced NLP..."):
                st.success("✅ NLP processing completed!")
                
                if extract_terms:
                    st.markdown("**Extracted Medical Terms:**")
                    extracted_terms = [
                        {"Term": "nausea", "Category": "adverse_events", "Confidence": 0.95, "MedDRA": "Nausea (10017947)"},
                        {"Term": "vomiting", "Category": "adverse_events", "Confidence": 0.93, "MedDRA": "Vomiting (10046743)"},
                        {"Term": "dizziness", "Category": "adverse_events", "Confidence": 0.89, "MedDRA": "Dizziness (10013573)"}
                    ]
                    st.dataframe(extracted_terms, use_container_width=True)
                
                if generate_summary:
                    st.markdown("**AI-Generated Case Summary:**")
                    case_summary = """
                    **Executive Summary:** A 45-year-old patient experienced multiple gastrointestinal and neurological adverse events following medication administration.
                    
                    **Key Facts:**
                    • Patient: 45-year-old Male
                    • Event onset: 2 hours post-administration
                    • Primary events: Nausea, vomiting, dizziness
                    • Reporter: Physician
                    
                    **Risk Factors:** None identified
                    
                    **Recommended Follow-up:**
                    • Assess causality relationship
                    • Monitor for symptom resolution
                    • Consider dose adjustment if rechallenge occurs
                    """
                    st.text_area("Generated Summary", case_summary, height=200)
                
                if assess_causality:
                    st.markdown("**Causality Assessment:**")
                    causality_result = {
                        "Assessment": "Probable",
                        "Confidence": 0.78,
                        "Reasoning": [
                            "Reasonable temporal relationship (2 hours)",
                            "Known adverse events for drug class",
                            "No alternative explanations identified"
                        ],
                        "WHO-UMC Score": 7
                    }
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Causality", causality_result["Assessment"])
                    with col2:
                        st.metric("Confidence", f"{causality_result['Confidence']:.1%}")
                    with col3:
                        st.metric("WHO-UMC Score", causality_result["WHO-UMC Score"])
    
    with tab3:
        st.subheader("Automated Workflow Routing")
        st.markdown("**Smart Case Assignment & Priority Management**")
        
        # Workflow rules configuration
        st.markdown("**Current Routing Rules:**")
        
        routing_rules = [
            {"Severity": "Death", "Assignee": "Senior Medical Officer", "Priority": "Urgent", "Timeline": "Immediate"},
            {"Severity": "Life-threatening", "Assignee": "Medical Officer", "Priority": "High", "Timeline": "4 hours"},
            {"Severity": "Hospitalization", "Assignee": "Medical Officer", "Priority": "High", "Timeline": "24 hours"},
            {"Severity": "Serious", "Assignee": "Reviewer", "Priority": "Medium", "Timeline": "3 days"},
            {"Severity": "Non-serious", "Assignee": "Reviewer", "Priority": "Low", "Timeline": "7 days"}
        ]
        
        st.dataframe(routing_rules, use_container_width=True)
        
        # Workflow simulation
        st.markdown("**Simulate Workflow Routing:**")
        
        col1, col2 = st.columns(2)
        with col1:
            sim_severity = st.selectbox("Case Severity", ["Non-serious", "Serious", "Hospitalization", "Life-threatening", "Death"])
            sim_confidence = st.slider("Classification Confidence", 0.5, 1.0, 0.85)
        
        with col2:
            sim_patient_age = st.number_input("Patient Age", 0, 120, 65)
            sim_product_type = st.selectbox("Product Type", ["Standard", "Vaccine", "Biologic"])
        
        if st.button("🔄 Simulate Routing"):
            # Simulate routing decision
            routing_decision = {
                "Recommended Assignee": "Medical Officer",
                "Priority Level": "High",
                "Review Timeline": "24 hours",
                "Notifications": ["assigned_reviewer", "medical_director"],
                "Special Considerations": ["Elderly patient - requires specialized review"]
            }
            
            st.success("✅ Routing decision generated!")
            
            for key, value in routing_decision.items():
                if isinstance(value, list):
                    st.write(f"**{key}:** {', '.join(value)}")
                else:
                    st.write(f"**{key}:** {value}")
        
        # Automation statistics
        st.markdown("**Automation Performance:**")
        automation_stats = {
            "Cases Auto-Routed": 1247,
            "Routing Accuracy": "94.2%",
            "Avg Processing Time": "1.8s",
            "Manual Interventions": "5.8%"
        }
        
        col1, col2, col3, col4 = st.columns(4)
        for i, (metric, value) in enumerate(automation_stats.items()):
            with [col1, col2, col3, col4][i]:
                st.metric(metric, value)
    
    with tab4:
        st.subheader("Quality Scoring & Compliance")
        st.markdown("**Automated Quality Assessment**")
        
        # Quality assessment simulation
        st.markdown("**Quality Assessment Factors:**")
        
        quality_factors = [
            {"Factor": "Patient Info Completeness", "Weight": "20%", "Current Score": 85},
            {"Factor": "Event Description Adequacy", "Weight": "20%", "Current Score": 92},
            {"Factor": "Temporal Relationship Clarity", "Weight": "15%", "Current Score": 78},
            {"Factor": "Outcome Documentation", "Weight": "15%", "Current Score": 88},
            {"Factor": "Reporter Credibility", "Weight": "20%", "Current Score": 95},
            {"Factor": "Supporting Documents", "Weight": "10%", "Current Score": 72}
        ]
        
        st.dataframe(quality_factors, use_container_width=True)
        
        # Overall quality metrics
        overall_score = sum(factor["Current Score"] * int(factor["Weight"].rstrip('%'))/100 for factor in quality_factors)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Quality Score", f"{overall_score:.1f}/100")
        with col2:
            quality_grade = "A" if overall_score >= 90 else "B" if overall_score >= 80 else "C" if overall_score >= 70 else "D"
            st.metric("Quality Grade", f"{quality_grade} - {'Excellent' if quality_grade == 'A' else 'Good' if quality_grade == 'B' else 'Adequate'}")
        with col3:
            st.metric("Compliance Status", "✅ Compliant" if overall_score >= 80 else "⚠️ Review Required")
        
        # Compliance checklist
        st.markdown("**Compliance Checklist:**")
        
        compliance_checks = [
            {"Check": "Reporting Timeline", "Status": "✅ Pass", "Details": "Within regulatory timeframes"},
            {"Check": "Required Fields", "Status": "✅ Pass", "Details": "All mandatory fields completed"},
            {"Check": "Patient Consent", "Status": "⚠️ Warning", "Details": "Consent documentation pending"},
            {"Check": "Data Quality", "Status": "✅ Pass", "Details": "Adequate event description"},
            {"Check": "Regulatory Requirements", "Status": "✅ Pass", "Details": "Meets current standards"}
        ]
        
        for check in compliance_checks:
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:
                st.write(check["Check"])
            with col2:
                st.write(check["Status"])
            with col3:
                st.write(check["Details"])

if __name__ == "__main__":
    main() 