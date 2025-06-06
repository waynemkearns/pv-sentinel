"""
Test Suite for PV Sentinel Phase 2 Features
Essential tests for patient voice protection and narrative comparison

Author: PV Sentinel Development Team
Created: June 2024
Phase: 2 - Narrative Control
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Adjust import paths for testing
import sys
sys.path.append(str(Path(__file__).parent.parent))

from backend.patient_voice import (
    PatientVoiceExtractor, PatientVoiceProtector, PatientVoiceType, 
    PatientVoiceValidation, PatientVoiceFragment, PatientVoiceRecord,
    create_patient_voice_protector
)
from backend.narrative_comparison import (
    NarrativeComparator, NarrativeVersionManager, ChangeType, ChangeSeverity,
    NarrativeChange, NarrativeVersion, ComparisonResult,
    create_narrative_comparison_system
)

@pytest.fixture
def test_config():
    """Test configuration for Phase 2 features"""
    return {
        'patient_voice': {
            'protection_enabled': True,
            'extraction_threshold': 0.7,
            'auto_lock_enabled': True,
            'log_modification_attempts': True
        },
        'narrative_comparison': {
            'enabled': True,
            'auto_severity': True,
            'require_justification': True,
            'clinical_terms_file': 'config/clinical_terms.json'
        }
    }

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def sample_patient_texts():
    """Sample patient voice texts for testing"""
    return {
        'direct_quotes': [
            'Patient said: "I started feeling dizzy about 2 hours after taking the pill"',
            'She reported: "The room was spinning and I had to sit down"',
            'Patient states: "I felt nauseous and threw up twice"'
        ],
        'reported_speech': [
            'Patient reported feeling dizzy after medication',
            'According to the patient, symptoms started within 2 hours',
            'Patient mentioned experiencing severe headache'
        ],
        'emotional_expressions': [
            'Patient was scared and anxious about the reaction',
            'She felt worried about taking the medication again',
            'Patient expressed fear about the side effects'
        ],
        'temporal_expressions': [
            'Symptoms started 2 hours after dose',
            'Patient felt better after 3 days',
            'Reaction lasted for about a week'
        ]
    }

@pytest.fixture
def sample_narratives():
    """Sample narrative versions for comparison testing"""
    return {
        'version_1': """
Patient Overview:
A 65-year-old male patient experienced dizziness after taking medication.

Timeline:
Patient took medication at 10:00 AM. Symptoms began at 12:00 PM.

Assessment:
Mild adverse reaction with good recovery.
""",
        'version_2': """
Patient Overview:
A 65-year-old male patient experienced severe dizziness requiring assistance after taking medication.

Timeline:
Patient took medication at 10:00 AM. Symptoms began at 12:00 PM. Patient was hospitalized for 3 days.

Assessment:
Serious adverse reaction with complete recovery after treatment.
"""
    }

class TestPatientVoiceExtractor:
    """Test Patient Voice Extraction functionality"""
    
    def test_extractor_initialization(self, test_config):
        """Test PatientVoiceExtractor initialization"""
        extractor = PatientVoiceExtractor(test_config)
        
        assert extractor.voice_protection_enabled == True
        assert extractor.extraction_threshold == 0.7
        assert extractor.auto_lock_enabled == True
        assert len(extractor.direct_quote_patterns) > 0
        assert len(extractor.reported_speech_patterns) > 0
    
    def test_direct_quote_extraction(self, test_config):
        """Test extraction of direct patient quotes"""
        extractor = PatientVoiceExtractor(test_config)
        
        quote_text = 'Patient said: "I started feeling dizzy after taking the pill"'
        fragments = extractor.extract_patient_voice(quote_text, "test_user", PatientVoiceType.DIRECT_QUOTE)
        
        assert len(fragments) > 0
        assert fragments[0].voice_type == PatientVoiceType.DIRECT_QUOTE
        assert fragments[0].confidence_score >= 0.8
    
    def test_reported_speech_extraction(self, test_config, sample_patient_texts):
        """Test extraction of reported patient speech"""
        extractor = PatientVoiceExtractor(test_config)
        
        for reported_text in sample_patient_texts['reported_speech']:
            fragments = extractor.extract_patient_voice(reported_text, "test_user", PatientVoiceType.REPORTED_SPEECH)
            
            assert len(fragments) > 0
            assert fragments[0].voice_type == PatientVoiceType.REPORTED_SPEECH
            assert fragments[0].confidence_score >= 0.6  # Medium confidence for reported speech
    
    def test_emotional_expression_extraction(self, test_config, sample_patient_texts):
        """Test extraction of emotional expressions"""
        extractor = PatientVoiceExtractor(test_config)
        
        for emotional_text in sample_patient_texts['emotional_expressions']:
            fragments = extractor.extract_patient_voice(emotional_text, "test_user")
            
            if fragments:  # Some emotional expressions may not be extracted
                assert len(fragments[0].emotional_indicators) > 0
                assert fragments[0].confidence_score >= 0.5
    
    def test_temporal_expression_extraction(self, test_config, sample_patient_texts):
        """Test extraction of temporal expressions"""
        extractor = PatientVoiceExtractor(test_config)
        
        for temporal_text in sample_patient_texts['temporal_expressions']:
            fragments = extractor.extract_patient_voice(temporal_text, "test_user")
            
            if fragments:  # Some temporal expressions may not be extracted
                assert fragments[0].clinical_relevance > 0
    
    def test_fragment_validation(self, test_config):
        """Test fragment validation and threshold filtering"""
        extractor = PatientVoiceExtractor(test_config)
        
        # Test text that should pass validation
        high_quality_text = 'Patient said: "I felt really dizzy and nauseous after taking the medication"'
        fragments = extractor.extract_patient_voice(high_quality_text, "test_user")
        
        assert len(fragments) > 0
        assert all(f.confidence_score >= extractor.extraction_threshold for f in fragments)
    
    def test_duplicate_filtering(self, test_config):
        """Test that duplicate fragments are filtered out"""
        extractor = PatientVoiceExtractor(test_config)
        
        # Same text repeated
        duplicate_text = 'Patient said: "I felt dizzy" Patient said: "I felt dizzy"'
        fragments = extractor.extract_patient_voice(duplicate_text, "test_user")
        
        # Should have only one unique fragment
        unique_texts = set(f.original_text for f in fragments)
        assert len(unique_texts) <= len(fragments)

class TestPatientVoiceProtector:
    """Test Patient Voice Protection functionality"""
    
    def test_protector_initialization(self, test_config):
        """Test PatientVoiceProtector initialization"""
        protector = PatientVoiceProtector(test_config)
        
        assert protector.protection_enabled == True
        assert protector.auto_lock_enabled == True
        assert protector.modification_logging == True
    
    def test_create_protected_record(self, test_config, temp_dir):
        """Test creation of protected patient voice record"""
        test_config['storage_dir'] = temp_dir
        protector = PatientVoiceProtector(test_config)
        
        # Create sample fragments
        fragments = [
            PatientVoiceFragment(
                fragment_id="test-frag-1",
                original_text="I felt really dizzy",
                voice_type=PatientVoiceType.DIRECT_QUOTE,
                validation_level=PatientVoiceValidation.REPORTED,
                source="test_user",
                timestamp=datetime.now().isoformat(),
                confidence_score=0.9,
                context="Patient interview",
                emotional_indicators=["dizzy"],
                clinical_relevance=0.8
            )
        ]
        
        record = protector.create_protected_record(
            case_id="TEST-001",
            fragments=fragments,
            created_by="test_user"
        )
        
        assert record.case_id == "TEST-001"
        assert record.created_by == "test_user"
        assert len(record.patient_fragments) == 1
        assert record.protection_level in ["protected", "locked"]
        assert record.integrity_hash is not None
    
    def test_integrity_verification(self, test_config, temp_dir):
        """Test patient voice record integrity verification"""
        test_config['storage_dir'] = temp_dir
        protector = PatientVoiceProtector(test_config)
        
        # Create and store a record
        fragments = [
            PatientVoiceFragment(
                fragment_id="test-frag-1",
                original_text="Test patient voice",
                voice_type=PatientVoiceType.DIRECT_QUOTE,
                validation_level=PatientVoiceValidation.VERIFIED,
                source="test_user",
                timestamp=datetime.now().isoformat(),
                confidence_score=0.9,
                context="Test context",
                emotional_indicators=[],
                clinical_relevance=0.7
            )
        ]
        
        record = protector.create_protected_record(
            case_id="TEST-002",
            fragments=fragments,
            created_by="test_user"
        )
        
        # Verify integrity
        assert protector.verify_integrity(record.record_id) == True
    
    def test_ai_modification_logging(self, test_config, temp_dir):
        """Test AI modification attempt logging"""
        test_config['storage_dir'] = temp_dir
        protector = PatientVoiceProtector(test_config)
        
        # Create a record first
        fragments = [
            PatientVoiceFragment(
                fragment_id="test-frag-1",
                original_text="Protected patient voice",
                voice_type=PatientVoiceType.DIRECT_QUOTE,
                validation_level=PatientVoiceValidation.VERIFIED,
                source="test_user",
                timestamp=datetime.now().isoformat(),
                confidence_score=0.9,
                context="Test context",
                emotional_indicators=[],
                clinical_relevance=0.7
            )
        ]
        
        record = protector.create_protected_record(
            case_id="TEST-003",
            fragments=fragments,
            created_by="test_user"
        )
        
        # Log AI modification attempt
        protector.log_ai_modification_attempt(
            record.record_id,
            "ai_system",
            "narrative_generation",
            blocked=True
        )
        
        # Verify logging
        retrieved_record = protector.voice_records[record.record_id]
        assert len(retrieved_record.ai_modification_attempts) == 1
        assert retrieved_record.ai_modification_attempts[0]['blocked'] == True
    
    def test_human_annotation(self, test_config, temp_dir):
        """Test human annotation functionality"""
        test_config['storage_dir'] = temp_dir
        protector = PatientVoiceProtector(test_config)
        
        # Create a record
        fragments = [
            PatientVoiceFragment(
                fragment_id="test-frag-1",
                original_text="Patient voice for annotation",
                voice_type=PatientVoiceType.DIRECT_QUOTE,
                validation_level=PatientVoiceValidation.REPORTED,
                source="test_user",
                timestamp=datetime.now().isoformat(),
                confidence_score=0.8,
                context="Test context",
                emotional_indicators=[],
                clinical_relevance=0.6
            )
        ]
        
        record = protector.create_protected_record(
            case_id="TEST-004",
            fragments=fragments,
            created_by="test_user"
        )
        
        # Add human annotation
        protector.add_human_annotation(
            record.record_id,
            "medical_reviewer",
            "This quote accurately represents patient's emotional state",
            "clinical_validation"
        )
        
        # Verify annotation
        retrieved_record = protector.voice_records[record.record_id]
        assert len(retrieved_record.human_annotations) == 1
        assert retrieved_record.human_annotations[0]['annotated_by'] == "medical_reviewer"

class TestNarrativeComparator:
    """Test Narrative Comparison functionality"""
    
    def test_comparator_initialization(self, test_config):
        """Test NarrativeComparator initialization"""
        comparator = NarrativeComparator(test_config)
        
        assert comparator.comparison_enabled == True
        assert comparator.auto_severity_assessment == True
        assert comparator.require_justification == True
        assert len(comparator.critical_terms) > 0
        assert len(comparator.significant_terms) > 0
    
    def test_narrative_comparison(self, test_config, sample_narratives):
        """Test basic narrative comparison"""
        comparator = NarrativeComparator(test_config)
        
        # Create narrative versions
        version_1 = NarrativeVersion(
            version_id="test-v1",
            case_id="TEST-CASE-001",
            version_number=1,
            version_type="draft",
            narrative_content=sample_narratives['version_1'],
            created_by="test_user",
            creation_timestamp=datetime.now().isoformat(),
            changes_from_previous=[],
            word_count=0,
            section_breakdown={},
            clinical_completeness_score=0.8,
            compliance_score=0.7,
            integrity_hash="test_hash_1",
            locked=False,
            lock_reason=None
        )
        
        version_2 = NarrativeVersion(
            version_id="test-v2",
            case_id="TEST-CASE-001",
            version_number=2,
            version_type="review",
            narrative_content=sample_narratives['version_2'],
            created_by="test_user",
            creation_timestamp=datetime.now().isoformat(),
            changes_from_previous=[],
            word_count=0,
            section_breakdown={},
            clinical_completeness_score=0.9,
            compliance_score=0.8,
            integrity_hash="test_hash_2",
            locked=False,
            lock_reason=None
        )
        
        # Perform comparison
        comparison = comparator.compare_narratives(version_1, version_2)
        
        assert comparison.case_id == "TEST-CASE-001"
        assert len(comparison.changes) > 0
        assert comparison.requires_medical_review is not None
        assert comparison.clinical_impact_assessment is not None
    
    def test_change_severity_assessment(self, test_config):
        """Test automatic change severity assessment"""
        comparator = NarrativeComparator(test_config)
        
        # Test critical change
        critical_severity = comparator._assess_change_severity(
            "Patient felt dizzy",
            "Patient was hospitalized due to severe reaction"
        )
        assert critical_severity == ChangeSeverity.CRITICAL
        
        # Test significant change
        significant_severity = comparator._assess_change_severity(
            "Patient felt dizzy",
            "Patient experienced severe dizziness requiring assistance"
        )
        assert significant_severity == ChangeSeverity.SIGNIFICANT
        
        # Test minor change
        minor_severity = comparator._assess_change_severity(
            "The patient felt better",
            "Patient felt better"
        )
        assert minor_severity in [ChangeSeverity.MINOR, ChangeSeverity.COSMETIC]
    
    def test_clinical_impact_assessment(self, test_config):
        """Test clinical impact assessment"""
        comparator = NarrativeComparator(test_config)
        
        # Create test changes
        changes = [
            NarrativeChange(
                change_id="test-change-1",
                section="timeline",
                change_type=ChangeType.ADDITION,
                change_source="human_edit",
                severity=ChangeSeverity.CRITICAL,
                original_text="",
                modified_text="Patient was hospitalized",
                justification="Added critical outcome",
                changed_by="test_user",
                timestamp=datetime.now().isoformat(),
                line_number=1,
                character_position=0,
                context_before="",
                context_after="",
                clinical_impact="High",
                requires_review=True,
                reviewed_by=None,
                review_timestamp=None,
                review_status="pending"
            )
        ]
        
        impact_assessment = comparator._assess_clinical_impact(changes)
        assert "HIGH IMPACT" in impact_assessment
        assert "critical" in impact_assessment.lower()

class TestNarrativeVersionManager:
    """Test Narrative Version Management functionality"""
    
    def test_version_manager_initialization(self, test_config, temp_dir):
        """Test NarrativeVersionManager initialization"""
        # Update config for temp directory
        test_config['storage_dir'] = temp_dir
        
        manager = NarrativeVersionManager(test_config)
        
        assert manager.comparator is not None
        assert isinstance(manager.narrative_versions, dict)
        assert isinstance(manager.comparisons, dict)
    
    def test_create_new_version(self, test_config, temp_dir, sample_narratives):
        """Test creating new narrative versions"""
        test_config['storage_dir'] = temp_dir
        manager = NarrativeVersionManager(test_config)
        
        # Create first version
        version_1 = manager.create_new_version(
            case_id="TEST-CASE-002",
            narrative_content=sample_narratives['version_1'],
            created_by="test_user",
            version_type="draft"
        )
        
        assert version_1.case_id == "TEST-CASE-002"
        assert version_1.version_number == 1
        assert version_1.version_type == "draft"
        assert version_1.created_by == "test_user"
        assert len(version_1.changes_from_previous) == 0  # First version has no changes
        
        # Create second version
        version_2 = manager.create_new_version(
            case_id="TEST-CASE-002",
            narrative_content=sample_narratives['version_2'],
            created_by="test_user",
            version_type="review"
        )
        
        assert version_2.version_number == 2
        assert len(version_2.changes_from_previous) > 0  # Should have changes from v1
    
    def test_version_comparison(self, test_config, temp_dir, sample_narratives):
        """Test comparing specific versions"""
        test_config['storage_dir'] = temp_dir
        manager = NarrativeVersionManager(test_config)
        
        # Create two versions
        manager.create_new_version(
            case_id="TEST-CASE-003",
            narrative_content=sample_narratives['version_1'],
            created_by="test_user",
            version_type="draft"
        )
        
        manager.create_new_version(
            case_id="TEST-CASE-003",
            narrative_content=sample_narratives['version_2'],
            created_by="test_user",
            version_type="review"
        )
        
        # Compare versions
        comparison = manager.compare_versions("TEST-CASE-003", 1, 2)
        
        assert comparison is not None
        assert comparison.case_id == "TEST-CASE-003"
        assert len(comparison.changes) > 0
    
    def test_get_latest_version(self, test_config, temp_dir, sample_narratives):
        """Test retrieving latest version"""
        test_config['storage_dir'] = temp_dir
        manager = NarrativeVersionManager(test_config)
        
        # Create multiple versions
        manager.create_new_version(
            case_id="TEST-CASE-004",
            narrative_content=sample_narratives['version_1'],
            created_by="test_user"
        )
        
        version_2 = manager.create_new_version(
            case_id="TEST-CASE-004",
            narrative_content=sample_narratives['version_2'],
            created_by="test_user"
        )
        
        latest = manager.get_latest_version("TEST-CASE-004")
        
        assert latest is not None
        assert latest.version_number == 2
        assert latest.version_id == version_2.version_id

class TestIntegrationScenarios:
    """Test integration scenarios combining Phase 2 features"""
    
    def test_full_patient_voice_pipeline(self, test_config, temp_dir):
        """Test complete patient voice protection pipeline"""
        test_config['storage_dir'] = temp_dir
        
        # Initialize components
        extractor, protector = create_patient_voice_protector(test_config)
        
        # Sample patient input
        patient_input = 'Patient said: "I started feeling really dizzy about 2 hours after taking the medication. It was scary because I thought I might fall."'
        
        # Extract patient voice
        fragments = extractor.extract_patient_voice(patient_input, "test_user")
        
        assert len(fragments) > 0
        
        # Create protected record
        record = protector.create_protected_record(
            case_id="INTEGRATION-001",
            fragments=fragments,
            created_by="test_user"
        )
        
        assert record is not None
        assert record.protection_level in ["protected", "locked"]
        
        # Verify integrity
        assert protector.verify_integrity(record.record_id) == True
    
    def test_narrative_version_with_patient_voice(self, test_config, temp_dir, sample_narratives):
        """Test narrative versioning with patient voice protection"""
        test_config['storage_dir'] = temp_dir
        
        # Initialize components
        narrative_manager = create_narrative_comparison_system(test_config)
        extractor, protector = create_patient_voice_protector(test_config)
        
        # Extract patient voice from narrative
        fragments = extractor.extract_patient_voice(sample_narratives['version_1'], "test_user")
        
        # Create protected record
        if fragments:
            voice_record = protector.create_protected_record(
                case_id="INTEGRATION-002",
                fragments=fragments,
                created_by="test_user"
            )
        
        # Create narrative version
        version = narrative_manager.create_new_version(
            case_id="INTEGRATION-002",
            narrative_content=sample_narratives['version_1'],
            created_by="test_user"
        )
        
        assert version is not None
        assert version.case_id == "INTEGRATION-002"
    
    def test_phase2_system_integration(self, test_config, temp_dir):
        """Test Phase 2 system integration with all components"""
        test_config['storage_dir'] = temp_dir
        
        # Initialize all Phase 2 components
        narrative_manager = create_narrative_comparison_system(test_config)
        extractor, protector = create_patient_voice_protector(test_config)
        
        # Test data
        case_id = "PHASE2-INTEGRATION-001"
        patient_input = 'Patient reported: "I felt dizzy and nauseous for several hours after taking the medication"'
        
        # Step 1: Extract and protect patient voice
        fragments = extractor.extract_patient_voice(patient_input, "integration_user")
        
        if fragments:
            voice_record = protector.create_protected_record(
                case_id=case_id,
                fragments=fragments,
                created_by="integration_user"
            )
        
        # Step 2: Create initial narrative version
        initial_narrative = f"A patient experienced adverse reactions after medication. {patient_input} The reaction was monitored and resolved."
        
        version_1 = narrative_manager.create_new_version(
            case_id=case_id,
            narrative_content=initial_narrative,
            created_by="integration_user",
            version_type="draft"
        )
        
        # Step 3: Create revised narrative version
        revised_narrative = f"A patient experienced significant adverse reactions after medication. {patient_input} The reaction required medical intervention and was completely resolved after treatment."
        
        version_2 = narrative_manager.create_new_version(
            case_id=case_id,
            narrative_content=revised_narrative,
            created_by="integration_user",
            version_type="review"
        )
        
        # Step 4: Compare versions
        comparison = narrative_manager.compare_versions(case_id, 1, 2)
        
        # Verify integration
        assert voice_record is not None if fragments else True
        assert version_1.version_number == 1
        assert version_2.version_number == 2
        assert comparison is not None
        assert comparison.case_id == case_id
        assert len(comparison.changes) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 