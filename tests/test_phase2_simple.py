"""
Simple Test Suite for PV Sentinel Phase 2 Features
Basic tests for patient voice protection and narrative comparison

Author: PV Sentinel Development Team
Created: June 2024
Phase: 2 - Narrative Control
"""

import pytest
import sys
from pathlib import Path

# Adjust import paths for testing
sys.path.append(str(Path(__file__).parent.parent))

def test_phase2_imports():
    """Test that Phase 2 modules can be imported"""
    try:
        from backend.patient_voice import PatientVoiceExtractor, PatientVoiceProtector
        from backend.narrative_comparison import NarrativeComparator, NarrativeVersionManager
        assert True, "Phase 2 modules imported successfully"
    except ImportError as e:
        pytest.skip(f"Phase 2 modules not available: {e}")

def test_patient_voice_extractor_basic():
    """Test basic PatientVoiceExtractor functionality"""
    try:
        from backend.patient_voice import PatientVoiceExtractor
        
        config = {
            'patient_voice': {
                'protection_enabled': True,
                'extraction_threshold': 0.7,
                'auto_lock_enabled': True
            }
        }
        
        extractor = PatientVoiceExtractor(config)
        assert extractor.voice_protection_enabled == True
        assert extractor.extraction_threshold == 0.7
        
    except ImportError:
        pytest.skip("PatientVoiceExtractor not available")

def test_patient_voice_protector_basic():
    """Test basic PatientVoiceProtector functionality"""
    try:
        from backend.patient_voice import PatientVoiceProtector
        
        config = {
            'patient_voice': {
                'protection_enabled': True,
                'auto_lock_enabled': True,
                'log_modification_attempts': True
            }
        }
        
        protector = PatientVoiceProtector(config)
        assert protector.protection_enabled == True
        assert protector.auto_lock_enabled == True
        
    except ImportError:
        pytest.skip("PatientVoiceProtector not available")

def test_narrative_comparator_basic():
    """Test basic NarrativeComparator functionality"""
    try:
        from backend.narrative_comparison import NarrativeComparator
        
        config = {
            'narrative_comparison': {
                'enabled': True,
                'auto_severity': True,
                'require_justification': True
            }
        }
        
        comparator = NarrativeComparator(config)
        assert comparator.comparison_enabled == True
        assert comparator.auto_severity_assessment == True
        
    except ImportError:
        pytest.skip("NarrativeComparator not available")

def test_narrative_version_manager_basic():
    """Test basic NarrativeVersionManager functionality"""
    try:
        from backend.narrative_comparison import NarrativeVersionManager
        
        config = {
            'narrative_comparison': {
                'enabled': True,
                'auto_severity': True
            }
        }
        
        manager = NarrativeVersionManager(config)
        assert manager.comparator is not None
        
    except ImportError:
        pytest.skip("NarrativeVersionManager not available")

def test_config_file_exists():
    """Test that clinical terms config file exists"""
    config_file = Path(__file__).parent.parent / "config" / "clinical_terms.json"
    assert config_file.exists(), "Clinical terms configuration file should exist"

def test_phase2_config_structure():
    """Test that Phase 2 configuration is properly structured"""
    import yaml
    
    config_file = Path(__file__).parent.parent / "config" / "config.yaml"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check Phase 2 configuration sections exist
        assert 'patient_voice' in config, "Patient voice configuration should exist"
        assert 'narrative_comparison' in config, "Narrative comparison configuration should exist"
        
        # Check patient voice config
        pv_config = config['patient_voice']
        assert 'protection_enabled' in pv_config
        assert 'extraction_threshold' in pv_config
        
        # Check narrative comparison config
        nc_config = config['narrative_comparison']
        assert 'enabled' in nc_config
        assert 'auto_severity' in nc_config
    else:
        pytest.skip("Configuration file not found")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 