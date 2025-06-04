"""
PV Sentinel - Patient Context Preservation Module
Critical P0 Feature: Ensures patient voice and context are never lost

This module addresses the critical gap identified in the Patient Advocate assessment:
- Risk of model paraphrasing/simplifying narratives, erasing patient nuance
- No dedicated space for preserving patient voice
- Missing patient context validation
"""

import logging
import json
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class PatientContext:
    """Preserves unedited patient voice and context"""
    patient_story: str  # Original patient description - NEVER edited by AI
    patient_voice_indicators: List[str]  # Key phrases that preserve patient perspective
    original_complaint: str  # Verbatim initial complaint
    emotional_context: Optional[str]  # Patient's emotional state/concerns
    cultural_context: Optional[str]  # Relevant cultural/social factors
    input_method: str  # "voice", "typed", "dictated"
    timestamp: str
    validation_flags: Dict[str, bool]
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.validation_flags:
            self.validation_flags = {
                "patient_story_present": bool(self.patient_story),
                "voice_indicators_preserved": len(self.patient_voice_indicators) > 0,
                "original_complaint_captured": bool(self.original_complaint),
                "context_validated": True
            }

class PatientContextPreserver:
    """
    Ensures patient context is preserved throughout the AE processing pipeline
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.preservation_enabled = config.get('patient_safety', {}).get('context_preservation', True)
        self.validation_enabled = config.get('patient_safety', {}).get('context_validation', True)
        
    def extract_patient_context(self, raw_input: str, input_method: str = "typed") -> PatientContext:
        """
        Extract and preserve patient context from raw input
        
        Args:
            raw_input: Original patient or reporter description
            input_method: How the input was captured (voice/typed/dictated)
            
        Returns:
            PatientContext object with preserved information
        """
        logger.info(f"Extracting patient context from {input_method} input")
        
        # Identify patient voice indicators (first-person language, emotional words)
        voice_indicators = self._identify_voice_indicators(raw_input)
        
        # Extract emotional context
        emotional_context = self._extract_emotional_context(raw_input)
        
        # Create patient context object
        context = PatientContext(
            patient_story=raw_input,  # Preserve original exactly
            patient_voice_indicators=voice_indicators,
            original_complaint=raw_input,  # Keep verbatim record
            emotional_context=emotional_context,
            cultural_context=None,  # To be enhanced in future versions
            input_method=input_method,
            timestamp=datetime.now().isoformat(),
            validation_flags={}
        )
        
        if self.validation_enabled:
            self._validate_context(context)
            
        return context
    
    def _identify_voice_indicators(self, text: str) -> List[str]:
        """Identify phrases that preserve patient perspective"""
        voice_indicators = []
        
        # First-person indicators
        first_person_phrases = ["I felt", "I experienced", "I noticed", "I developed", 
                               "I started", "I began", "I suffered", "I had"]
        
        # Emotional/subjective descriptors
        emotional_phrases = ["painful", "scary", "worrying", "frightening", 
                            "uncomfortable", "severe", "mild", "terrible"]
        
        # Temporal patient descriptions
        temporal_phrases = ["suddenly", "gradually", "immediately", "within hours",
                           "the next day", "that evening", "right away"]
        
        text_lower = text.lower()
        for phrase in first_person_phrases + emotional_phrases + temporal_phrases:
            if phrase in text_lower:
                # Find and preserve the full context around the phrase
                start_idx = text_lower.find(phrase)
                end_idx = min(start_idx + 100, len(text))
                context_snippet = text[max(0, start_idx-20):end_idx]
                voice_indicators.append(context_snippet.strip())
        
        return voice_indicators
    
    def _extract_emotional_context(self, text: str) -> Optional[str]:
        """Extract emotional context that should be preserved"""
        emotional_keywords = ["worried", "scared", "anxious", "painful", "severe", 
                             "mild", "terrible", "frightening", "concerning"]
        
        text_lower = text.lower()
        found_emotions = [word for word in emotional_keywords if word in text_lower]
        
        if found_emotions:
            return f"Patient expressed emotional context: {', '.join(found_emotions)}"
        
        return None
    
    def _validate_context(self, context: PatientContext) -> None:
        """Validate that critical patient context is preserved"""
        validations = {
            "patient_story_present": len(context.patient_story.strip()) > 0,
            "voice_indicators_preserved": len(context.patient_voice_indicators) > 0,
            "original_complaint_captured": len(context.original_complaint.strip()) > 0,
            "input_method_recorded": context.input_method in ["voice", "typed", "dictated"],
            "timestamp_present": bool(context.timestamp)
        }
        
        context.validation_flags = validations
        
        # Log warnings for missing critical elements
        if not validations["patient_story_present"]:
            logger.warning("PATIENT SAFETY ALERT: No patient story captured")
        
        if not validations["voice_indicators_preserved"]:
            logger.warning("Patient voice indicators not found - review for context preservation")
    
    def preserve_in_narrative(self, narrative: str, context: PatientContext) -> str:
        """
        Ensure patient context is preserved in the final narrative
        
        Args:
            narrative: AI-generated narrative
            context: Original patient context
            
        Returns:
            Enhanced narrative with patient context preserved
        """
        if not self.preservation_enabled:
            return narrative
        
        # Add patient context section that is never edited by AI
        patient_section = f"\n\n--- PATIENT CONTEXT (Preserved Verbatim) ---\n"
        patient_section += f"Original Patient Description: {context.patient_story}\n"
        
        if context.patient_voice_indicators:
            patient_section += f"Key Patient Expressions: {'; '.join(context.patient_voice_indicators[:3])}\n"
        
        if context.emotional_context:
            patient_section += f"Emotional Context: {context.emotional_context}\n"
        
        patient_section += f"Input Method: {context.input_method}\n"
        patient_section += f"Captured: {context.timestamp}\n"
        patient_section += "--- End Patient Context ---\n"
        
        return narrative + patient_section
    
    def flag_context_loss_risk(self, original_context: PatientContext, 
                              processed_narrative: str) -> List[str]:
        """
        Flag potential loss of patient context in processed narrative
        
        Returns:
            List of warnings about potential context loss
        """
        warnings = []
        
        # Check if key patient voice indicators are present in final narrative
        narrative_lower = processed_narrative.lower()
        missing_indicators = []
        
        for indicator in original_context.patient_voice_indicators:
            if indicator.lower() not in narrative_lower:
                missing_indicators.append(indicator)
        
        if missing_indicators:
            warnings.append(f"PATIENT VOICE ALERT: Missing patient expressions: {missing_indicators[:2]}")
        
        # Check for emotional context preservation
        if original_context.emotional_context and \
           not any(emotion in narrative_lower for emotion in ["worried", "scared", "painful", "severe"]):
            warnings.append("EMOTIONAL CONTEXT ALERT: Patient emotional context may be lost")
        
        # Check narrative length - if too short, context might be lost
        if len(processed_narrative) < len(original_context.patient_story) * 0.8:
            warnings.append("CONTEXT LENGTH ALERT: Processed narrative significantly shorter than original")
        
        return warnings
    
    def generate_context_report(self, context: PatientContext) -> Dict:
        """Generate a report on patient context preservation"""
        return {
            "patient_context_id": hash(context.patient_story),
            "preservation_status": context.validation_flags,
            "input_method": context.input_method,
            "voice_indicators_count": len(context.patient_voice_indicators),
            "emotional_context_present": bool(context.emotional_context),
            "timestamp": context.timestamp,
            "context_quality_score": self._calculate_context_quality(context)
        }
    
    def _calculate_context_quality(self, context: PatientContext) -> float:
        """Calculate quality score for patient context preservation (0-1)"""
        score = 0.0
        
        # Base score for having patient story
        if context.patient_story:
            score += 0.4
        
        # Score for voice indicators
        if context.patient_voice_indicators:
            score += min(0.3, len(context.patient_voice_indicators) * 0.1)
        
        # Score for emotional context
        if context.emotional_context:
            score += 0.2
        
        # Score for proper input method tracking
        if context.input_method in ["voice", "typed", "dictated"]:
            score += 0.1
        
        return min(1.0, score)

# Factory function for easy integration
def create_patient_context_preserver(config: Dict) -> PatientContextPreserver:
    """Factory function to create PatientContextPreserver with config"""
    return PatientContextPreserver(config) 