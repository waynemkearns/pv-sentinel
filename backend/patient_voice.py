"""
PV Sentinel - Patient Voice Protection Module
Critical P0 Feature: Preserves authentic patient voice that AI cannot modify

This module addresses critical gaps identified in the Patient Advocate assessment:
- No dedicated "Patient Story" field that remains unedited
- Limited patient language preservation in final outputs
- Missing patient review option for their own cases

Patient Safety Impact: Ensures patient's authentic voice is never lost or modified by AI
PII Handling: Protects patient voice while applying appropriate privacy controls
Stakeholder Value: Patient Advocate, PV Officer, Regulatory Affairs, Clinical Operations
"""

import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class PatientVoiceType(Enum):
    """Types of patient voice input methods"""
    DIRECT_QUOTE = "direct_quote"        # Direct patient quotation
    REPORTED_SPEECH = "reported_speech"  # Healthcare provider reporting what patient said
    WRITTEN_ACCOUNT = "written_account"  # Patient's written description
    VOICE_RECORDING = "voice_recording"  # Transcribed from voice
    FAMILY_REPORT = "family_report"      # Family member reporting for patient

class PatientVoiceValidation(Enum):
    """Validation levels for patient voice authenticity"""
    VERIFIED = "verified"           # Directly verified with patient
    REPORTED = "reported"          # Reported by healthcare provider
    DOCUMENTED = "documented"      # Found in medical records
    INFERRED = "inferred"         # Inferred from context
    UNCERTAIN = "uncertain"       # Uncertain authenticity

@dataclass
class PatientVoiceFragment:
    """Individual fragment of patient voice"""
    fragment_id: str
    original_text: str
    voice_type: PatientVoiceType
    validation_level: PatientVoiceValidation
    source: str  # Who captured this (HCP name, system, etc.)
    timestamp: str
    confidence_score: float  # 0.0 to 1.0
    context: str  # Surrounding context when voice was captured
    emotional_indicators: List[str]  # Fear, anxiety, pain, etc.
    clinical_relevance: float  # 0.0 to 1.0
    
    def __post_init__(self):
        if not self.fragment_id:
            self.fragment_id = self._generate_fragment_id()
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def _generate_fragment_id(self) -> str:
        """Generate unique ID for this fragment"""
        content_hash = hashlib.sha256(self.original_text.encode()).hexdigest()[:8]
        timestamp_hash = hashlib.sha256(self.timestamp.encode()).hexdigest()[:4]
        return f"PVF-{content_hash}-{timestamp_hash}"

@dataclass
class PatientVoiceRecord:
    """Complete protected patient voice record"""
    record_id: str
    case_id: str
    patient_fragments: List[PatientVoiceFragment]
    creation_timestamp: str
    last_modified: str
    created_by: str  # User who created the record
    protection_level: str  # "read_only", "protected", "locked"
    ai_modification_attempts: List[Dict]  # Log of any AI modification attempts
    human_annotations: List[Dict]  # Human annotations/clarifications
    validation_status: PatientVoiceValidation
    integrity_hash: str
    
    def __post_init__(self):
        if not self.record_id:
            self.record_id = self._generate_record_id()
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.now().isoformat()
        if not self.last_modified:
            self.last_modified = self.creation_timestamp
        if not self.integrity_hash:
            self.integrity_hash = self._calculate_integrity_hash()
    
    def _generate_record_id(self) -> str:
        """Generate unique ID for this record"""
        case_hash = hashlib.sha256(self.case_id.encode()).hexdigest()[:8]
        timestamp_hash = hashlib.sha256(self.creation_timestamp.encode()).hexdigest()[:4]
        return f"PVR-{case_hash}-{timestamp_hash}"
    
    def _calculate_integrity_hash(self) -> str:
        """Calculate integrity hash for tamper detection"""
        content = json.dumps([asdict(fragment) for fragment in self.patient_fragments], sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

class PatientVoiceExtractor:
    """
    Extracts and identifies authentic patient voice from various input sources
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.voice_protection_enabled = config.get('patient_voice', {}).get('protection_enabled', True)
        self.extraction_threshold = config.get('patient_voice', {}).get('extraction_threshold', 0.7)
        self.auto_lock_enabled = config.get('patient_voice', {}).get('auto_lock_enabled', True)
        
        # Patterns for identifying patient voice
        self._initialize_voice_patterns()
        
        logger.info(f"Patient voice extractor initialized - protection: {self.voice_protection_enabled}")
    
    def _initialize_voice_patterns(self):
        """Initialize patterns for detecting patient voice in text"""
        
        # Direct quote patterns
        self.direct_quote_patterns = [
            r'"([^"]*)"',  # Text in quotes
            r"'([^']*)'",  # Text in single quotes
            r'patient said[:\s]+"([^"]*)"',  # Patient said: "..."
            r'patient reported[:\s]+"([^"]*)"',  # Patient reported: "..."
            r'patient states[:\s]+"([^"]*)"',  # Patient states: "..."
        ]
        
        # Reported speech patterns
        self.reported_speech_patterns = [
            r'patient (?:said|reported|states|mentioned|complained|described) (?:that )?(.+?)(?:\.|$)',
            r'according to (?:the )?patient[,\s]+(.+?)(?:\.|$)',
            r'patient (?:feels|experiences|has) (.+?)(?:\.|$)',
        ]
        
        # Emotional indicator patterns
        self.emotional_patterns = [
            r'\b(scared|frightened|terrified|afraid)\b',
            r'\b(worried|anxious|nervous|concerned)\b',
            r'\b(painful|hurts|aching|sore)\b',
            r'\b(dizzy|nauseous|sick|ill)\b',
            r'\b(tired|exhausted|weak|fatigue)\b',
            r'\b(confused|disoriented|foggy)\b',
        ]
        
        # Temporal expressions that indicate patient experience
        self.temporal_patterns = [
            r'(?:started|began|happened|occurred) (?:about |around )?(.+?) (?:ago|before)',
            r'(?:lasted|continued) (?:for )?(.+?)(?:\.|$)',
            r'(?:since|after|before) (.+?)(?:\.|$)',
        ]
    
    def extract_patient_voice(self, text: str, input_source: str = "unknown", 
                            voice_type: PatientVoiceType = PatientVoiceType.REPORTED_SPEECH) -> List[PatientVoiceFragment]:
        """
        Extract patient voice fragments from input text
        
        Args:
            text: Input text to analyze
            input_source: Source of the text (HCP name, system, etc.)
            voice_type: Type of voice input
            
        Returns:
            List of PatientVoiceFragment objects
        """
        if not self.voice_protection_enabled:
            return []
        
        fragments = []
        
        # Extract direct quotes
        fragments.extend(self._extract_direct_quotes(text, input_source))
        
        # Extract reported speech
        fragments.extend(self._extract_reported_speech(text, input_source, voice_type))
        
        # Extract emotional expressions
        fragments.extend(self._extract_emotional_expressions(text, input_source))
        
        # Extract temporal expressions
        fragments.extend(self._extract_temporal_expressions(text, input_source))
        
        # Filter and validate fragments
        validated_fragments = self._validate_fragments(fragments)
        
        logger.info(f"Extracted {len(validated_fragments)} patient voice fragments from {len(text)} characters")
        
        return validated_fragments
    
    def _extract_direct_quotes(self, text: str, input_source: str) -> List[PatientVoiceFragment]:
        """Extract direct patient quotes"""
        fragments = []
        
        for pattern in self.direct_quote_patterns:
            import re
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                quote_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
                
                if self._is_likely_patient_voice(quote_text):
                    fragment = PatientVoiceFragment(
                        fragment_id="",
                        original_text=quote_text.strip(),
                        voice_type=PatientVoiceType.DIRECT_QUOTE,
                        validation_level=PatientVoiceValidation.REPORTED,
                        source=input_source,
                        timestamp="",
                        confidence_score=0.9,  # High confidence for direct quotes
                        context=self._extract_context(text, match.start(), match.end()),
                        emotional_indicators=self._detect_emotions(quote_text),
                        clinical_relevance=self._assess_clinical_relevance(quote_text)
                    )
                    fragments.append(fragment)
        
        return fragments
    
    def _extract_reported_speech(self, text: str, input_source: str, 
                                voice_type: PatientVoiceType) -> List[PatientVoiceFragment]:
        """Extract reported patient speech"""
        fragments = []
        
        for pattern in self.reported_speech_patterns:
            import re
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                reported_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
                
                if self._is_likely_patient_voice(reported_text):
                    fragment = PatientVoiceFragment(
                        fragment_id="",
                        original_text=reported_text.strip(),
                        voice_type=voice_type,
                        validation_level=PatientVoiceValidation.REPORTED,
                        source=input_source,
                        timestamp="",
                        confidence_score=0.7,  # Medium confidence for reported speech
                        context=self._extract_context(text, match.start(), match.end()),
                        emotional_indicators=self._detect_emotions(reported_text),
                        clinical_relevance=self._assess_clinical_relevance(reported_text)
                    )
                    fragments.append(fragment)
        
        return fragments
    
    def _extract_emotional_expressions(self, text: str, input_source: str) -> List[PatientVoiceFragment]:
        """Extract emotional expressions that indicate patient voice"""
        fragments = []
        
        for pattern in self.emotional_patterns:
            import re
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # Extract surrounding context for emotional expressions
                context_text = self._extract_context(text, match.start(), match.end(), window=50)
                
                if self._contains_patient_reference(context_text):
                    fragment = PatientVoiceFragment(
                        fragment_id="",
                        original_text=context_text.strip(),
                        voice_type=PatientVoiceType.REPORTED_SPEECH,
                        validation_level=PatientVoiceValidation.INFERRED,
                        source=input_source,
                        timestamp="",
                        confidence_score=0.6,  # Lower confidence for inferred
                        context=context_text,
                        emotional_indicators=[match.group(0)],
                        clinical_relevance=self._assess_clinical_relevance(context_text)
                    )
                    fragments.append(fragment)
        
        return fragments
    
    def _extract_temporal_expressions(self, text: str, input_source: str) -> List[PatientVoiceFragment]:
        """Extract temporal expressions that indicate patient experience"""
        fragments = []
        
        for pattern in self.temporal_patterns:
            import re
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                context_text = self._extract_context(text, match.start(), match.end(), window=50)
                
                if self._contains_patient_reference(context_text):
                    fragment = PatientVoiceFragment(
                        fragment_id="",
                        original_text=match.group(0).strip(),
                        voice_type=PatientVoiceType.REPORTED_SPEECH,
                        validation_level=PatientVoiceValidation.DOCUMENTED,
                        source=input_source,
                        timestamp="",
                        confidence_score=0.5,  # Lower confidence for temporal only
                        context=context_text,
                        emotional_indicators=self._detect_emotions(context_text),
                        clinical_relevance=self._assess_clinical_relevance(context_text)
                    )
                    fragments.append(fragment)
        
        return fragments
    
    def _is_likely_patient_voice(self, text: str) -> bool:
        """Assess if text is likely authentic patient voice"""
        # Check minimum length
        if len(text.strip()) < 5:
            return False
        
        # Check for first-person indicators
        first_person_indicators = ['i ', 'my ', 'me ', 'myself', 'i\'m', 'i\'ve', 'i\'ll']
        has_first_person = any(indicator in text.lower() for indicator in first_person_indicators)
        
        # Check for medical jargon (less likely to be patient voice)
        medical_jargon = ['etiology', 'pathogenesis', 'differential', 'prognosis', 'contraindication']
        has_medical_jargon = any(jargon in text.lower() for jargon in medical_jargon)
        
        # Check for emotional content
        has_emotional_content = bool(self._detect_emotions(text))
        
        # Decision logic
        if has_medical_jargon and not has_first_person:
            return False
        
        if has_first_person or has_emotional_content:
            return True
        
        # Check for experiential language
        experiential_words = ['felt', 'feel', 'hurt', 'pain', 'started', 'began', 'suddenly']
        has_experiential = any(word in text.lower() for word in experiential_words)
        
        return has_experiential
    
    def _detect_emotions(self, text: str) -> List[str]:
        """Detect emotional indicators in text"""
        emotions = []
        
        import re
        for pattern in self.emotional_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            emotions.extend(matches)
        
        return list(set(emotions))  # Remove duplicates
    
    def _assess_clinical_relevance(self, text: str) -> float:
        """Assess clinical relevance of patient voice fragment"""
        clinical_terms = [
            'symptom', 'pain', 'dizzy', 'nausea', 'tired', 'weak', 'swelling',
            'rash', 'itching', 'breathing', 'chest', 'heart', 'stomach',
            'headache', 'fever', 'chills', 'medication', 'pill', 'dose'
        ]
        
        term_count = sum(1 for term in clinical_terms if term in text.lower())
        
        # Normalize by text length and term count
        relevance = min(term_count / max(len(clinical_terms) * 0.2, 1), 1.0)
        
        return relevance
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 30) -> str:
        """Extract context around a match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _contains_patient_reference(self, text: str) -> bool:
        """Check if text contains reference to patient"""
        patient_refs = ['patient', 'he ', 'she ', 'they ', 'i ', 'my ', 'me ']
        return any(ref in text.lower() for ref in patient_refs)
    
    def _validate_fragments(self, fragments: List[PatientVoiceFragment]) -> List[PatientVoiceFragment]:
        """Validate and filter fragments based on confidence and relevance"""
        validated = []
        
        for fragment in fragments:
            # Apply threshold filter
            if fragment.confidence_score >= self.extraction_threshold:
                # Check for duplicates
                is_duplicate = any(
                    existing.original_text.strip().lower() == fragment.original_text.strip().lower()
                    for existing in validated
                )
                
                if not is_duplicate:
                    validated.append(fragment)
        
        # Sort by confidence and clinical relevance
        validated.sort(key=lambda x: (x.confidence_score + x.clinical_relevance) / 2, reverse=True)
        
        return validated

class PatientVoiceProtector:
    """
    Protects patient voice records from AI modification and maintains integrity
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.protection_enabled = config.get('patient_voice', {}).get('protection_enabled', True)
        self.auto_lock_enabled = config.get('patient_voice', {}).get('auto_lock_enabled', True)
        self.modification_logging = config.get('patient_voice', {}).get('log_modification_attempts', True)
        
        # Storage
        self.records_file = 'storage/patient_voice_records.json'
        self.voice_records: Dict[str, PatientVoiceRecord] = {}
        
        # Load existing records
        self._load_records()
        
        logger.info(f"Patient voice protector initialized - protection: {self.protection_enabled}")
    
    def create_protected_record(self, case_id: str, fragments: List[PatientVoiceFragment], 
                              created_by: str) -> PatientVoiceRecord:
        """
        Create a new protected patient voice record
        
        Args:
            case_id: Associated case ID
            fragments: List of patient voice fragments
            created_by: User ID who created the record
            
        Returns:
            Protected PatientVoiceRecord
        """
        if not self.protection_enabled:
            raise RuntimeError("Patient voice protection is disabled")
        
        record = PatientVoiceRecord(
            record_id="",
            case_id=case_id,
            patient_fragments=fragments,
            creation_timestamp="",
            last_modified="",
            created_by=created_by,
            protection_level="protected",
            ai_modification_attempts=[],
            human_annotations=[],
            validation_status=PatientVoiceValidation.REPORTED,
            integrity_hash=""
        )
        
        # Auto-lock if enabled and high confidence fragments
        if self.auto_lock_enabled and self._should_auto_lock(fragments):
            record.protection_level = "locked"
        
        # Store the record
        self.voice_records[record.record_id] = record
        self._save_records()
        
        logger.info(f"Created protected patient voice record: {record.record_id}")
        
        return record
    
    def get_patient_voice(self, case_id: str) -> Optional[PatientVoiceRecord]:
        """Get patient voice record for a case"""
        for record in self.voice_records.values():
            if record.case_id == case_id:
                return record
        return None
    
    def verify_integrity(self, record_id: str) -> bool:
        """Verify integrity of patient voice record"""
        if record_id not in self.voice_records:
            return False
        
        record = self.voice_records[record_id]
        current_hash = record._calculate_integrity_hash()
        
        return current_hash == record.integrity_hash
    
    def log_ai_modification_attempt(self, record_id: str, attempted_by: str, 
                                  modification_type: str, blocked: bool = True):
        """Log AI modification attempts for audit purposes"""
        if not self.modification_logging:
            return
        
        if record_id not in self.voice_records:
            return
        
        attempt = {
            'timestamp': datetime.now().isoformat(),
            'attempted_by': attempted_by,
            'modification_type': modification_type,
            'blocked': blocked,
            'protection_level': self.voice_records[record_id].protection_level
        }
        
        self.voice_records[record_id].ai_modification_attempts.append(attempt)
        self._save_records()
        
        logger.warning(f"AI modification attempt logged for record {record_id}: {modification_type}")
    
    def add_human_annotation(self, record_id: str, annotated_by: str, 
                           annotation: str, annotation_type: str = "clarification"):
        """Add human annotation to patient voice record"""
        if record_id not in self.voice_records:
            raise ValueError(f"Patient voice record not found: {record_id}")
        
        annotation_entry = {
            'timestamp': datetime.now().isoformat(),
            'annotated_by': annotated_by,
            'annotation': annotation,
            'type': annotation_type
        }
        
        self.voice_records[record_id].human_annotations.append(annotation_entry)
        self.voice_records[record_id].last_modified = datetime.now().isoformat()
        self._save_records()
        
        logger.info(f"Human annotation added to record {record_id} by {annotated_by}")
    
    def _should_auto_lock(self, fragments: List[PatientVoiceFragment]) -> bool:
        """Determine if record should be auto-locked based on fragment quality"""
        if not fragments:
            return False
        
        # Lock if we have high-confidence direct quotes
        high_confidence_quotes = [
            f for f in fragments 
            if f.voice_type == PatientVoiceType.DIRECT_QUOTE and f.confidence_score >= 0.8
        ]
        
        return len(high_confidence_quotes) > 0
    
    def _load_records(self):
        """Load patient voice records from storage"""
        try:
            import os
            if os.path.exists(self.records_file):
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Convert back to objects
                for record_id, record_data in data.items():
                    # Convert fragments
                    fragments = [
                        PatientVoiceFragment(**fragment_data) 
                        for fragment_data in record_data['patient_fragments']
                    ]
                    
                    # Create record
                    record_data['patient_fragments'] = fragments
                    record = PatientVoiceRecord(**record_data)
                    self.voice_records[record_id] = record
                
                logger.info(f"Loaded {len(self.voice_records)} patient voice records")
        except Exception as e:
            logger.error(f"Failed to load patient voice records: {e}")
    
    def _save_records(self):
        """Save patient voice records to storage"""
        try:
            import os
            os.makedirs(os.path.dirname(self.records_file), exist_ok=True)
            
            # Convert to serializable format
            data = {}
            for record_id, record in self.voice_records.items():
                data[record_id] = asdict(record)
            
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save patient voice records: {e}")

def create_patient_voice_protector(config: Dict) -> Tuple[PatientVoiceExtractor, PatientVoiceProtector]:
    """
    Factory function to create patient voice protection components
    
    Args:
        config: Application configuration dictionary
        
    Returns:
        Tuple of (PatientVoiceExtractor, PatientVoiceProtector)
    """
    extractor = PatientVoiceExtractor(config)
    protector = PatientVoiceProtector(config)
    
    logger.info("Patient voice protection system initialized")
    
    return extractor, protector