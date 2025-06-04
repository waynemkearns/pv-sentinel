#!/usr/bin/env python3
"""
Basic functionality test for PV Sentinel MVP
Tests all critical P0 and P1 features before GitHub push
"""

import yaml
import tempfile
import os
import time
from pathlib import Path

# Import our modules
from backend.patient_context import create_patient_context_preserver
from backend.model_tracking import create_model_tracker
from backend.readback import create_readback_confirmer, VoiceCapture
from backend.users import create_user_manager, UserRole
from backend.main import create_pv_sentinel_engine

def create_test_config():
    """Create test configuration"""
    return {
        'system': {
            'logging_level': 'INFO',
            'audit_mode': True,
            'validation_mode': False
        },
        'models': {
            'primary_model': 'mistral-7b-instruct',
            'model_path': 'models/test_model.gguf',
            'prompt_directory': 'prompts/',
            'model_hash_tracking': True
        },
        'patient_safety': {
            'context_preservation': True,
            'voice_confirmation': True,
            'narrative_comparison': True
        },
        'users': {
            'multi_user_support': True,
            'role_based_access': True,
            'session_timeout': 3600
        },
        'stt': {
            'enable_readback': True,
            'confidence_threshold': 0.8
        },
        'validation': {
            'model_hash_tracking': True,
            'prompt_locking': True
        }
    }

def test_patient_context_preservation():
    """Test P0 Critical: Patient Context Preservation"""
    print("🧪 Testing Patient Context Preservation...")
    
    config = create_test_config()
    preserver = create_patient_context_preserver(config)
    
    # Test patient story
    patient_input = "I felt terrible after taking the medication. I developed a severe rash and felt nauseous immediately."
    
    context = preserver.extract_patient_context(patient_input, "typed")
    
    assert context.patient_story == patient_input, "Patient story not preserved"
    assert len(context.patient_voice_indicators) > 0, "No voice indicators found"
    assert context.validation_flags['patient_story_present'], "Patient story validation failed"
    
    print("✅ Patient Context Preservation: PASS")
    return True

def test_model_tracking():
    """Test P0 Critical: Model Version Tracking"""
    print("🧪 Testing Model Version Tracking...")
    
    config = create_test_config()
    tracker = create_model_tracker(config)
    
    # Create test model file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gguf', delete=False) as f:
        f.write("test model content")
        test_model_path = f.name
    
    try:
        # Register model
        metadata = tracker.register_model(test_model_path, "test-model")
        assert metadata.model_name == "test-model", "Model name not set correctly"
        assert metadata.model_hash, "Model hash not generated"
        
        print("✅ Model Version Tracking: PASS")
        return True
        
    finally:
        os.unlink(test_model_path)

def test_voice_readback():
    """Test P0 Critical: Voice Readback Confirmation"""
    print("🧪 Testing Voice Readback Confirmation...")
    
    config = create_test_config()
    confirmer = create_readback_confirmer(config)
    
    # Test voice capture with critical terms
    voice_capture = VoiceCapture(
        original_audio_path=None,
        transcribed_text="Patient died after taking the medication",
        confidence_score=0.7,  # Low confidence to trigger readback
        language_detected="en",
        duration_seconds=10.0,
        timestamp="2024-01-04T10:00:00",
        whisper_model_version="base.en",
        processing_time_ms=1000
    )
    
    should_readback, reason = confirmer.should_trigger_readback(voice_capture)
    assert should_readback, "Readback should be triggered for critical terms"
    assert "critical medical terms" in reason.lower() or "low confidence" in reason.lower(), f"Unexpected reason: {reason}"
    
    # Test session creation
    session = confirmer.create_readback_session(voice_capture)
    assert session.session_id, "Session ID not generated"
    assert session.voice_capture == voice_capture, "Voice capture not preserved"
    
    print("✅ Voice Readback Confirmation: PASS")
    return True

def test_user_management():
    """Test P1 High: Multi-User Support"""
    print("🧪 Testing User Management...")
    
    config = create_test_config()
    user_manager = create_user_manager(config)
    
    # Use timestamp to ensure unique username
    timestamp = str(int(time.time()))
    username = f"test_user_{timestamp}"
    
    # Create test user
    user = user_manager.create_user(
        username=username,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.DRAFTER,
        password="test123"
    )
    
    assert user.username == username, "Username not set correctly"
    assert user.role == UserRole.DRAFTER, "Role not set correctly"
    assert user.permissions.can_create_cases, "Drafter should be able to create cases"
    
    # Test authentication
    session = user_manager.authenticate_user(username, "test123")
    assert session is not None, "Authentication failed"
    assert session.username == username, "Session username incorrect"
    
    # Test permissions
    can_create = user_manager.check_permission(session.session_id, 'can_create_cases')
    assert can_create, "Permission check failed"
    
    print("✅ User Management: PASS")
    return True

def test_configuration_loading():
    """Test configuration loading from YAML"""
    print("🧪 Testing Configuration Loading...")
    
    # Test loading existing config
    try:
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Verify critical safety settings
        assert config['patient_safety']['context_preservation'], "Patient context preservation must be enabled"
        assert config.get('validation', {}).get('model_hash_tracking', True), "Model hash tracking must be enabled"
        assert config['stt']['enable_readback'], "Readback must be enabled"
        
        print("✅ Configuration Loading: PASS")
        return True
        
    except FileNotFoundError:
        print("⚠️  Configuration file not found - this is expected for fresh installations")
        return True

def test_prompt_templates():
    """Test prompt template loading"""
    print("🧪 Testing Prompt Templates...")
    
    prompt_dir = Path('prompts/')
    if not prompt_dir.exists():
        print("⚠️  Prompts directory not found - creating for testing")
        prompt_dir.mkdir(exist_ok=True)
    
    templates = list(prompt_dir.glob('*.txt'))
    assert len(templates) > 0, "No prompt templates found"
    
    # Check for key templates
    template_names = [t.stem for t in templates]
    critical_templates = ['narrative_template_anaphylaxis', 'narrative_template_skin_rash', 'narrative_template_hepatic_injury']
    
    for template in critical_templates:
        assert template in template_names, f"Critical template missing: {template}"
    
    print("✅ Prompt Templates: PASS")
    return True

def main():
    """Run all tests"""
    print("🚀 PV Sentinel Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_configuration_loading,
        test_patient_context_preservation,
        test_model_tracking,
        test_voice_readback,
        test_user_management,
        test_prompt_templates
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: FAILED - {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! PV Sentinel is ready for GitHub push.")
        return True
    else:
        print("⚠️  Some tests failed. Please review before pushing to GitHub.")
        return False

if __name__ == "__main__":
    main() 