"""
PV Sentinel - PII Protection and Data Privacy Module
Critical P0 Feature: Protects patient identifiable information in all data processing

This module addresses the critical gaps identified in the Data Privacy Officer assessment:
- No explicit PII scrubbing and masking capabilities
- Missing access controls for sensitive patient data
- Limited anonymization options for training and export

Patient Safety Impact: Prevents accidental exposure of patient identifiers
PII Handling: Core module for all PII detection, masking, and anonymization
Stakeholder Value: Data Privacy Officer, Patient Advocate, Regulatory Affairs
"""

import re
import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import unicodedata

logger = logging.getLogger(__name__)

class PIIType(Enum):
    """Types of personally identifiable information"""
    NAME = "name"
    DATE_OF_BIRTH = "date_of_birth"
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"
    IDENTIFIER = "identifier"
    LOCATION = "location"
    MEDICAL_RECORD_NUMBER = "medical_record_number"
    CUSTOM = "custom"

class PIISensitivity(Enum):
    """Sensitivity levels for PII"""
    LOW = "low"          # Initials, general locations
    MEDIUM = "medium"    # Partial names, zip codes
    HIGH = "high"        # Full names, specific addresses
    CRITICAL = "critical" # SSN, MRN, DOB

@dataclass
class PIIDetection:
    """Results of PII detection"""
    pii_type: PIIType
    sensitivity: PIISensitivity
    original_text: str
    start_position: int
    end_position: int
    confidence: float
    suggested_replacement: str
    context: str = ""
    
class PIIProtectionConfig:
    """Configuration for PII protection behaviors"""
    
    def __init__(self, config: Dict):
        self.enabled = config.get('security', {}).get('mask_pii', True)
        self.retain_patient_context = config.get('security', {}).get('retain_patient_context', True)
        self.anonymization_enabled = config.get('security', {}).get('data_anonymization', True)
        self.consent_tracking = config.get('security', {}).get('consent_tracking', True)
        
        # PII detection sensitivity
        self.detection_threshold = config.get('pii_protection', {}).get('detection_threshold', 0.7)
        self.mask_in_logs = config.get('pii_protection', {}).get('mask_in_logs', True)
        self.mask_in_exports = config.get('pii_protection', {}).get('mask_in_exports', False)
        
        # Custom PII patterns
        self.custom_patterns = config.get('pii_protection', {}).get('custom_patterns', [])
        
        # Role-based access
        self.role_masking = config.get('pii_protection', {}).get('role_based_masking', {
            'auditor': ['name', 'address', 'phone'],
            'readonly': ['name', 'date_of_birth', 'address', 'phone', 'email']
        })

class PIIDetector:
    """
    Detects personally identifiable information in text using regex patterns
    and contextual analysis
    """
    
    def __init__(self, config: PIIProtectionConfig):
        self.config = config
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize PII detection patterns"""
        
        # Name patterns (various cultures)
        self.name_patterns = [
            # Common Western names (first last)
            r'\b[A-Z][a-z]{1,15}\s+[A-Z][a-z]{1,15}\b',
            # Names with titles
            r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            # Initials
            r'\b[A-Z]\.[A-Z]\.\b',
            # Multi-part surnames
            r'\b[A-Z][a-z]+(?:-[A-Z][a-z]+)*\s+[A-Z][a-z]+\b',
        ]
        
        # Date patterns
        self.date_patterns = [
            # MM/DD/YYYY, DD/MM/YYYY
            r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{4}\b',
            # Month DD, YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            # DD Month YYYY
            r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            # ISO format
            r'\b\d{4}-\d{2}-\d{2}\b',
        ]
        
        # Address patterns
        self.address_patterns = [
            # Street addresses
            r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b',
            # Zip codes
            r'\b\d{5}(?:-\d{4})?\b',
            # Postal codes (various countries)
            r'\b[A-Z]\d[A-Z]\s*\d[A-Z]\d\b',  # Canada
        ]
        
        # Phone patterns
        self.phone_patterns = [
            # US phone numbers
            r'\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            # International format
            r'\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b',
        ]
        
        # Email patterns
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ]
        
        # Medical record numbers
        self.mrn_patterns = [
            r'\b(?:MRN|Medical Record|Patient ID)[\s:]*[A-Z0-9\-]{6,}\b',
            r'\b[A-Z]{2}\d{6,}\b',  # Common MRN format
        ]
        
        # Custom patterns from config
        self.custom_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.config.custom_patterns
        ]
    
    def detect_pii(self, text: str, context: str = "") -> List[PIIDetection]:
        """
        Detect all PII in the given text
        
        Args:
            text: Text to analyze for PII
            context: Additional context about the text (e.g., "patient_narrative")
            
        Returns:
            List of PIIDetection objects
        """
        if not self.config.enabled:
            return []
        
        detections = []
        
        # Detect names
        detections.extend(self._detect_names(text, context))
        
        # Detect dates
        detections.extend(self._detect_dates(text, context))
        
        # Detect addresses
        detections.extend(self._detect_addresses(text, context))
        
        # Detect phones
        detections.extend(self._detect_phones(text, context))
        
        # Detect emails
        detections.extend(self._detect_emails(text, context))
        
        # Detect medical record numbers
        detections.extend(self._detect_mrns(text, context))
        
        # Detect custom patterns
        detections.extend(self._detect_custom(text, context))
        
        # Sort by position for consistent processing
        detections.sort(key=lambda x: x.start_position)
        
        # Remove overlapping detections (keep highest confidence)
        detections = self._remove_overlaps(detections)
        
        logger.debug(f"Detected {len(detections)} PII instances in text of {len(text)} characters")
        
        return detections
    
    def _detect_names(self, text: str, context: str) -> List[PIIDetection]:
        """Detect names in text"""
        detections = []
        
        for pattern in self.name_patterns:
            for match in re.finditer(pattern, text):
                # Filter out common false positives
                name_text = match.group().strip()
                if self._is_likely_name(name_text, context):
                    detections.append(PIIDetection(
                        pii_type=PIIType.NAME,
                        sensitivity=PIISensitivity.HIGH,
                        original_text=name_text,
                        start_position=match.start(),
                        end_position=match.end(),
                        confidence=self._calculate_name_confidence(name_text, context),
                        suggested_replacement=self._generate_name_replacement(name_text),
                        context=context
                    ))
        
        return detections
    
    def _detect_dates(self, text: str, context: str) -> List[PIIDetection]:
        """Detect dates in text"""
        detections = []
        
        for pattern in self.date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                date_text = match.group().strip()
                sensitivity = self._assess_date_sensitivity(date_text, context)
                
                detections.append(PIIDetection(
                    pii_type=PIIType.DATE_OF_BIRTH,
                    sensitivity=sensitivity,
                    original_text=date_text,
                    start_position=match.start(),
                    end_position=match.end(),
                    confidence=0.9,  # Dates are usually high confidence
                    suggested_replacement=self._generate_date_replacement(date_text, sensitivity),
                    context=context
                ))
        
        return detections
    
    def _detect_addresses(self, text: str, context: str) -> List[PIIDetection]:
        """Detect addresses in text"""
        detections = []
        
        for pattern in self.address_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                address_text = match.group().strip()
                
                detections.append(PIIDetection(
                    pii_type=PIIType.ADDRESS,
                    sensitivity=PIISensitivity.HIGH,
                    original_text=address_text,
                    start_position=match.start(),
                    end_position=match.end(),
                    confidence=0.8,
                    suggested_replacement="[ADDRESS]",
                    context=context
                ))
        
        return detections
    
    def _detect_phones(self, text: str, context: str) -> List[PIIDetection]:
        """Detect phone numbers in text"""
        detections = []
        
        for pattern in self.phone_patterns:
            for match in re.finditer(pattern, text):
                phone_text = match.group().strip()
                
                detections.append(PIIDetection(
                    pii_type=PIIType.PHONE,
                    sensitivity=PIISensitivity.MEDIUM,
                    original_text=phone_text,
                    start_position=match.start(),
                    end_position=match.end(),
                    confidence=0.9,
                    suggested_replacement="[PHONE]",
                    context=context
                ))
        
        return detections
    
    def _detect_emails(self, text: str, context: str) -> List[PIIDetection]:
        """Detect email addresses in text"""
        detections = []
        
        for pattern in self.email_patterns:
            for match in re.finditer(pattern, text):
                email_text = match.group().strip()
                
                detections.append(PIIDetection(
                    pii_type=PIIType.EMAIL,
                    sensitivity=PIISensitivity.MEDIUM,
                    original_text=email_text,
                    start_position=match.start(),
                    end_position=match.end(),
                    confidence=0.95,
                    suggested_replacement="[EMAIL]",
                    context=context
                ))
        
        return detections
    
    def _detect_mrns(self, text: str, context: str) -> List[PIIDetection]:
        """Detect medical record numbers in text"""
        detections = []
        
        for pattern in self.mrn_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                mrn_text = match.group().strip()
                
                detections.append(PIIDetection(
                    pii_type=PIIType.MEDICAL_RECORD_NUMBER,
                    sensitivity=PIISensitivity.CRITICAL,
                    original_text=mrn_text,
                    start_position=match.start(),
                    end_position=match.end(),
                    confidence=0.9,
                    suggested_replacement="[MRN]",
                    context=context
                ))
        
        return detections
    
    def _detect_custom(self, text: str, context: str) -> List[PIIDetection]:
        """Detect custom PII patterns from configuration"""
        detections = []
        
        for pattern in self.custom_patterns:
            for match in pattern.finditer(text):
                custom_text = match.group().strip()
                
                detections.append(PIIDetection(
                    pii_type=PIIType.CUSTOM,
                    sensitivity=PIISensitivity.MEDIUM,
                    original_text=custom_text,
                    start_position=match.start(),
                    end_position=match.end(),
                    confidence=0.7,
                    suggested_replacement="[CUSTOM_PII]",
                    context=context
                ))
        
        return detections
    
    def _is_likely_name(self, text: str, context: str) -> bool:
        """Assess if detected pattern is likely a real name"""
        # Filter common false positives
        false_positives = {
            'adverse event', 'medical history', 'patient reported',
            'side effect', 'drug name', 'brand name', 'generic name',
            'patient john', 'patient jane'  # Common test patterns
        }
        
        text_lower = text.lower()
        
        # Don't match if it starts with "Patient"
        if text_lower.startswith('patient '):
            return False
            
        return not any(fp in text_lower for fp in false_positives)
    
    def _calculate_name_confidence(self, name: str, context: str) -> float:
        """Calculate confidence score for name detection"""
        confidence = 0.5
        
        # Increase confidence for typical name patterns
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', name):
            confidence += 0.3
        
        # Context clues
        if 'patient' in context.lower():
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _assess_date_sensitivity(self, date_text: str, context: str) -> PIISensitivity:
        """Assess sensitivity level of detected date"""
        # Birth dates are critical PII
        if any(keyword in context.lower() for keyword in ['birth', 'born', 'dob']):
            return PIISensitivity.CRITICAL
        
        # Event dates are medium sensitivity
        return PIISensitivity.MEDIUM
    
    def _generate_name_replacement(self, name: str) -> str:
        """Generate appropriate replacement for names"""
        parts = name.split()
        if len(parts) == 2:
            return f"[PATIENT_{len(parts[0])}{len(parts[1])}]"
        return "[PATIENT_NAME]"
    
    def _generate_date_replacement(self, date: str, sensitivity: PIISensitivity) -> str:
        """Generate appropriate replacement for dates"""
        if sensitivity == PIISensitivity.CRITICAL:
            return "[DATE_OF_BIRTH]"
        return "[DATE]"
    
    def _remove_overlaps(self, detections: List[PIIDetection]) -> List[PIIDetection]:
        """Remove overlapping detections, keeping highest confidence"""
        if not detections:
            return detections
        
        # Sort by position, then by confidence (descending)
        detections.sort(key=lambda x: (x.start_position, -x.confidence))
        
        filtered = []
        last_end = -1
        
        for detection in detections:
            if detection.start_position >= last_end:
                filtered.append(detection)
                last_end = detection.end_position
        
        return filtered

class PIIMasker:
    """
    Applies masking and anonymization to text containing PII
    """
    
    def __init__(self, config: PIIProtectionConfig):
        self.config = config
        self.detector = PIIDetector(config)
    
    def mask_pii(self, text: str, user_role: str = None, context: str = "", 
                preserve_patient_context: bool = None) -> Tuple[str, List[PIIDetection]]:
        """
        Mask PII in text based on user role and configuration
        
        Args:
            text: Text to mask
            user_role: User role for role-based masking
            context: Context about the text
            preserve_patient_context: Override for patient context preservation
            
        Returns:
            Tuple of (masked_text, list_of_detections)
        """
        if not self.config.enabled:
            return text, []
        
        # Detect PII
        detections = self.detector.detect_pii(text, context)
        
        if not detections:
            return text, detections
        
        # Determine what to mask based on role
        mask_types = self._get_mask_types_for_role(user_role)
        
        # Apply masking
        masked_text = self._apply_masking(text, detections, mask_types, preserve_patient_context)
        
        return masked_text, detections
    
    def _get_mask_types_for_role(self, user_role: str) -> Set[PIIType]:
        """Get PII types to mask for specific user role"""
        if not user_role or user_role not in self.config.role_masking:
            return set()  # No masking for unknown roles
        
        mask_list = self.config.role_masking[user_role]
        mask_types = set()
        
        for pii_type_str in mask_list:
            if pii_type_str == "name":
                mask_types.add(PIIType.NAME)
            elif pii_type_str == "address":
                mask_types.add(PIIType.ADDRESS)
            elif pii_type_str == "phone":
                mask_types.add(PIIType.PHONE)
            elif pii_type_str == "email":
                mask_types.add(PIIType.EMAIL)
            elif pii_type_str == "date_of_birth":
                mask_types.add(PIIType.DATE_OF_BIRTH)
        
        return mask_types
    
    def _apply_masking(self, text: str, detections: List[PIIDetection], 
                      mask_types: Set[PIIType], preserve_patient_context: bool = None) -> str:
        """Apply masking to text based on detections and mask types"""
        if preserve_patient_context is None:
            preserve_patient_context = self.config.retain_patient_context
        
        # If preserving patient context, be more selective
        if preserve_patient_context:
            mask_types = {PIIType.MEDICAL_RECORD_NUMBER, PIIType.PHONE, PIIType.EMAIL, PIIType.ADDRESS}
        
        # Work backwards to preserve positions
        masked_text = text
        for detection in reversed(detections):
            should_mask = (
                detection.pii_type in mask_types and 
                detection.confidence >= self.config.detection_threshold
            )
            
            # If preserving patient context, be more selective about names
            if preserve_patient_context and detection.pii_type == PIIType.NAME:
                should_mask = False
            
            if should_mask:
                masked_text = (
                    masked_text[:detection.start_position] + 
                    detection.suggested_replacement + 
                    masked_text[detection.end_position:]
                )
        
        return masked_text
    
    def create_anonymized_version(self, text: str, context: str = "") -> Tuple[str, Dict]:
        """
        Create fully anonymized version of text for training or research
        
        Args:
            text: Text to anonymize
            context: Context about the text
            
        Returns:
            Tuple of (anonymized_text, anonymization_metadata)
        """
        if not self.config.anonymization_enabled:
            return text, {}
        
        detections = self.detector.detect_pii(text, context)
        
        # Create anonymization mapping
        anonymization_map = {}
        anonymized_text = text
        
        # Apply full anonymization
        for detection in reversed(detections):
            anonymized_replacement = self._generate_anonymized_replacement(detection)
            anonymization_map[detection.original_text] = anonymized_replacement
            
            anonymized_text = (
                anonymized_text[:detection.start_position] + 
                anonymized_replacement + 
                anonymized_text[detection.end_position:]
            )
        
        metadata = {
            'original_length': len(text),
            'anonymized_length': len(anonymized_text),
            'pii_instances_found': len(detections),
            'anonymization_timestamp': datetime.now().isoformat(),
            'anonymization_map_hash': hashlib.sha256(str(anonymization_map).encode()).hexdigest()
        }
        
        return anonymized_text, metadata
    
    def _generate_anonymized_replacement(self, detection: PIIDetection) -> str:
        """Generate appropriate anonymized replacement"""
        replacements = {
            PIIType.NAME: "[PATIENT_NAME]",
            PIIType.DATE_OF_BIRTH: "[DATE_OF_BIRTH]",
            PIIType.ADDRESS: "[ADDRESS]",
            PIIType.PHONE: "[PHONE]",
            PIIType.EMAIL: "[EMAIL]",
            PIIType.MEDICAL_RECORD_NUMBER: "[MRN]",
            PIIType.IDENTIFIER: "[ID]",
            PIIType.LOCATION: "[LOCATION]",
            PIIType.CUSTOM: "[REDACTED]"
        }
        
        return replacements.get(detection.pii_type, "[REDACTED]")

class AccessLogger:
    """
    Logs access to PII-sensitive data with appropriate masking
    """
    
    def __init__(self, config: PIIProtectionConfig):
        self.config = config
        self.masker = PIIMasker(config)
        self.log_file = "logs/pii_access.log"
    
    def log_pii_access(self, user_id: str, session_id: str, data_type: str, 
                      data_content: str = "", action: str = "read", 
                      success: bool = True, context: str = ""):
        """
        Log access to PII-sensitive data
        
        Args:
            user_id: ID of accessing user
            session_id: Session ID
            data_type: Type of data accessed
            data_content: Content being accessed (will be masked)
            action: Action performed (read, write, export, etc.)
            success: Whether access was successful
            context: Additional context
        """
        if not self.config.consent_tracking:
            return
        
        # Mask PII in log content
        masked_content = ""
        if data_content and self.config.mask_in_logs:
            masked_content, _ = self.masker.mask_pii(
                data_content, 
                user_role="auditor",  # Use most restrictive masking for logs
                context=context,
                preserve_patient_context=False  # Full masking for logs
            )
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'session_id': session_id,
            'data_type': data_type,
            'action': action,
            'success': success,
            'context': context,
            'masked_content': masked_content[:200] if masked_content else "",  # Limit log size
            'content_hash': hashlib.sha256(data_content.encode()).hexdigest() if data_content else ""
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write PII access log: {e}")

def create_pii_protector(config: Dict) -> Tuple[PIIMasker, AccessLogger]:
    """
    Factory function to create PII protection components
    
    Args:
        config: Application configuration dictionary
        
    Returns:
        Tuple of (PIIMasker, AccessLogger)
    """
    pii_config = PIIProtectionConfig(config)
    masker = PIIMasker(pii_config)
    access_logger = AccessLogger(pii_config)
    
    logger.info(f"PII protection initialized - masking enabled: {pii_config.enabled}")
    
    return masker, access_logger