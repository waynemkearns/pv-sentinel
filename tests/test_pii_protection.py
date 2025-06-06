"""
Test Suite for PII Protection Module
Phase 1 Feature: Validates PII detection, masking, and role-based access controls

Patient Safety Impact: Ensures patient identifiers are properly protected
PII Handling: Validates core PII protection functionality
Stakeholder Value: Data Privacy Officer, Patient Advocate, Regulatory Affairs
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.pii_protection import (
    PIIDetector, PIIMasker, AccessLogger, PIIProtectionConfig,
    PIIType, PIISensitivity, create_pii_protector
)

class TestPIIProtection(unittest.TestCase):
    """Test cases for PII protection functionality"""
    
    def setUp(self):
        """Set up test configuration"""
        self.test_config = {
            'security': {
                'mask_pii': True,
                'retain_patient_context': True,
                'data_anonymization': True,
                'consent_tracking': True
            },
            'pii_protection': {
                'detection_threshold': 0.7,
                'mask_in_logs': True,
                'mask_in_exports': False,
                'custom_patterns': [],
                'role_based_masking': {
                    'auditor': ['name', 'address', 'phone'],
                    'readonly': ['name', 'date_of_birth', 'address', 'phone', 'email']
                }
            }
        }
        
        self.config = PIIProtectionConfig(self.test_config)
        self.detector = PIIDetector(self.config)
        self.masker = PIIMasker(self.config)
    
    def test_name_detection(self):
        """Test detection of patient names"""
        test_text = "John Smith reported feeling dizzy after taking medication."
        
        detections = self.detector.detect_pii(test_text, "patient_narrative")
        
        # Should detect at least one name
        name_detections = [d for d in detections if d.pii_type == PIIType.NAME]
        self.assertGreater(len(name_detections), 0)
        
        # Check the detected name
        if name_detections:
            detection = name_detections[0]
            self.assertEqual(detection.original_text, "John Smith")
            self.assertEqual(detection.sensitivity, PIISensitivity.HIGH)
    
    def test_date_detection(self):
        """Test detection of dates that could be DOB"""
        test_text = "Patient was born on 01/15/1980 and reported symptoms on 03/20/2024."
        
        detections = self.detector.detect_pii(test_text, "birth_date_context")
        
        # Should detect dates
        date_detections = [d for d in detections if d.pii_type == PIIType.DATE_OF_BIRTH]
        self.assertGreater(len(date_detections), 0)
    
    def test_address_detection(self):
        """Test detection of addresses"""
        test_text = "Patient lives at 123 Main Street and can be reached at home."
        
        detections = self.detector.detect_pii(test_text, "patient_contact")
        
        # Should detect address
        address_detections = [d for d in detections if d.pii_type == PIIType.ADDRESS]
        self.assertGreater(len(address_detections), 0)
    
    def test_phone_detection(self):
        """Test detection of phone numbers"""
        test_text = "Contact patient at (555) 123-4567 for follow-up."
        
        detections = self.detector.detect_pii(test_text, "contact_info")
        
        # Should detect phone number
        phone_detections = [d for d in detections if d.pii_type == PIIType.PHONE]
        self.assertGreater(len(phone_detections), 0)
    
    def test_email_detection(self):
        """Test detection of email addresses"""
        test_text = "Patient's email is john.doe@email.com for communication."
        
        detections = self.detector.detect_pii(test_text, "contact_info")
        
        # Should detect email
        email_detections = [d for d in detections if d.pii_type == PIIType.EMAIL]
        self.assertGreater(len(email_detections), 0)
    
    def test_mrn_detection(self):
        """Test detection of medical record numbers"""
        test_text = "Patient MRN: ABC123456 was admitted yesterday."
        
        detections = self.detector.detect_pii(test_text, "medical_record")
        
        # Should detect MRN
        mrn_detections = [d for d in detections if d.pii_type == PIIType.MEDICAL_RECORD_NUMBER]
        self.assertGreater(len(mrn_detections), 0)
    
    def test_role_based_masking(self):
        """Test that different roles see different levels of masking"""
        test_text = "John Smith from 123 Main St called (555) 123-4567 about side effects."
        
        # Test auditor role (should mask names, addresses, phones)
        masked_auditor, detections_auditor = self.masker.mask_pii(
            test_text, 
            user_role="auditor", 
            context="case_review",
            preserve_patient_context=False
        )
        
        # Should contain masked elements
        self.assertIn("[", masked_auditor)  # Some masking should occur
        self.assertNotIn("John Smith", masked_auditor)  # Name should be masked
        
        # Test drafter role (should have minimal masking)
        masked_drafter, detections_drafter = self.masker.mask_pii(
            test_text, 
            user_role="drafter", 
            context="case_creation"
        )
        
        # Should have less masking than auditor
        self.assertIn("John Smith", masked_drafter)  # Name should be preserved
    
    def test_patient_context_preservation(self):
        """Test that patient context is preserved when configured"""
        test_text = "Patient said: 'I felt really dizzy and my name is John Smith.'"
        
        # With patient context preservation enabled
        masked_preserved, _ = self.masker.mask_pii(
            test_text,
            user_role="auditor",
            context="patient_narrative", 
            preserve_patient_context=True
        )
        
        # Should preserve clinical context while masking identifiers
        self.assertIn("dizzy", masked_preserved)  # Clinical info preserved
        
        # Without patient context preservation
        masked_full, _ = self.masker.mask_pii(
            test_text,
            user_role="auditor", 
            context="patient_narrative",
            preserve_patient_context=False
        )
        
        # Should have more aggressive masking
        self.assertNotIn("John Smith", masked_full)
    
    def test_anonymization(self):
        """Test full anonymization for research/training"""
        test_text = "John Smith, DOB 01/15/1980, lives at 123 Main St."
        
        anonymized_text, metadata = self.masker.create_anonymized_version(
            test_text, 
            context="research_data"
        )
        
        # Should replace all PII
        self.assertNotIn("John Smith", anonymized_text)
        self.assertNotIn("01/15/1980", anonymized_text)
        self.assertNotIn("123 Main St", anonymized_text)
        
        # Should contain replacement tokens
        self.assertIn("[", anonymized_text)
        
        # Metadata should be present
        self.assertIn('pii_instances_found', metadata)
        self.assertGreater(metadata['pii_instances_found'], 0)
    
    def test_access_logging(self):
        """Test that PII access is properly logged"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary log file
            log_file = os.path.join(temp_dir, "test_pii_access.log")
            
            logger = AccessLogger(self.config)
            logger.log_file = log_file
            
            # Log some PII access
            logger.log_pii_access(
                user_id="test_user",
                session_id="test_session", 
                data_type="patient_narrative",
                data_content="John Smith reported symptoms",
                action="read",
                context="case_review"
            )
            
            # Check that log file was created and contains entry
            self.assertTrue(os.path.exists(log_file))
            
            with open(log_file, 'r') as f:
                log_content = f.read()
                self.assertIn("test_user", log_content)
                self.assertIn("patient_narrative", log_content)
                # Should not contain unmasked PII
                self.assertNotIn("John Smith", log_content)
    
    def test_false_positive_filtering(self):
        """Test that medical terms are not falsely detected as names"""
        test_text = "Patient reported Adverse Event with Brand Name medication."
        
        detections = self.detector.detect_pii(test_text, "medical_narrative")
        
        # Should not detect "Adverse Event" or "Brand Name" as patient names
        name_detections = [d for d in detections if d.pii_type == PIIType.NAME]
        false_positives = [d for d in name_detections if d.original_text in 
                          ['Adverse Event', 'Brand Name']]
        
        self.assertEqual(len(false_positives), 0)
    
    def test_configuration_disabled(self):
        """Test that PII protection can be disabled via configuration"""
        disabled_config = self.test_config.copy()
        disabled_config['security']['mask_pii'] = False
        
        disabled_config_obj = PIIProtectionConfig(disabled_config)
        disabled_detector = PIIDetector(disabled_config_obj)
        
        test_text = "John Smith reported symptoms."
        detections = disabled_detector.detect_pii(test_text, "test")
        
        # Should return no detections when disabled
        self.assertEqual(len(detections), 0)
    
    def test_factory_function(self):
        """Test that the factory function creates components correctly"""
        masker, access_logger = create_pii_protector(self.test_config)
        
        self.assertIsInstance(masker, PIIMasker)
        self.assertIsInstance(access_logger, AccessLogger)
        
        # Test that they work
        test_text = "John Smith test"
        masked_text, detections = masker.mask_pii(test_text, "auditor")
        
        self.assertIsInstance(masked_text, str)
        self.assertIsInstance(detections, list)

if __name__ == '__main__':
    # Run the tests
    unittest.main() 