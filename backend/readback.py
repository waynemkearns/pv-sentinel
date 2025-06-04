"""
PV Sentinel - Voice Readback Confirmation Module
Critical P0 Feature: Prevents voice capture errors through confirmation

This module addresses the critical gap identified in the End User (HCP) assessment:
- No "readback" option to confirm AE capture accuracy
- Potential for voice capture errors to go undetected
- Missing workflow optimization features
"""

import logging
import json
from datetime import datetime
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ReadbackStatus(Enum):
    """Status of readback confirmation"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class VoiceCapture:
    """Voice capture data with metadata"""
    original_audio_path: Optional[str]
    transcribed_text: str
    confidence_score: float
    language_detected: str
    duration_seconds: float
    timestamp: str
    whisper_model_version: str
    processing_time_ms: int
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ReadbackSession:
    """Complete readback session data"""
    session_id: str
    voice_capture: VoiceCapture
    readback_audio_path: Optional[str]
    readback_text: str
    user_response: ReadbackStatus
    corrections: List[Dict]
    final_text: str
    session_start: str
    session_end: Optional[str]
    confidence_improved: bool
    
    def __post_init__(self):
        if not self.session_start:
            self.session_start = datetime.now().isoformat()

class VoiceReadbackConfirmer:
    """
    Handles voice readback confirmation to ensure accurate AE capture
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.readback_enabled = config.get('stt', {}).get('enable_readback', True)
        self.confirmation_required = config.get('stt', {}).get('confirmation_required', False)
        self.confidence_threshold = config.get('stt', {}).get('confidence_threshold', 0.8)
        self.auto_readback_threshold = config.get('stt', {}).get('auto_readback_threshold', 0.9)
        
        # TTS settings for readback
        self.tts_enabled = config.get('stt', {}).get('tts_enabled', True)
        self.tts_voice = config.get('stt', {}).get('tts_voice', 'default')
        self.tts_speed = config.get('stt', {}).get('tts_speed', 1.0)
        
        logger.info(f"Voice readback confirmer initialized - enabled: {self.readback_enabled}")
    
    def should_trigger_readback(self, voice_capture: VoiceCapture) -> Tuple[bool, str]:
        """
        Determine if readback confirmation should be triggered
        
        Args:
            voice_capture: Voice capture data to evaluate
            
        Returns:
            Tuple of (should_readback, reason)
        """
        if not self.readback_enabled:
            return False, "Readback disabled in configuration"
        
        # Always readback if required by configuration
        if self.confirmation_required:
            return True, "Readback required by configuration"
        
        # Trigger readback for low confidence scores
        if voice_capture.confidence_score < self.confidence_threshold:
            return True, f"Low confidence score: {voice_capture.confidence_score:.2f}"
        
        # Trigger readback for very short or very long transcriptions
        word_count = len(voice_capture.transcribed_text.split())
        if word_count < 5:
            return True, "Very short transcription - may be incomplete"
        
        if word_count > 200:
            return True, "Very long transcription - confirm accuracy"
        
        # Trigger readback for critical medical terms (safety-critical)
        critical_terms = ['death', 'died', 'fatal', 'life-threatening', 'severe', 
                         'emergency', 'hospitalization', 'icu', 'intensive care']
        
        text_lower = voice_capture.transcribed_text.lower()
        found_critical = [term for term in critical_terms if term in text_lower]
        
        if found_critical:
            return True, f"Critical medical terms detected: {', '.join(found_critical)}"
        
        # Check for medical terminology that's commonly misheard
        potential_errors = self._detect_potential_transcription_errors(voice_capture.transcribed_text)
        if potential_errors:
            return True, f"Potential transcription errors detected: {len(potential_errors)} issues"
        
        # No readback needed for high-confidence, normal-length transcriptions
        return False, "High confidence transcription"
    
    def create_readback_session(self, voice_capture: VoiceCapture) -> ReadbackSession:
        """
        Create a new readback session
        
        Args:
            voice_capture: Original voice capture to confirm
            
        Returns:
            ReadbackSession object to track the confirmation process
        """
        session_id = self._generate_session_id(voice_capture)
        
        session = ReadbackSession(
            session_id=session_id,
            voice_capture=voice_capture,
            readback_audio_path=None,
            readback_text=self._prepare_readback_text(voice_capture.transcribed_text),
            user_response=ReadbackStatus.PENDING,
            corrections=[],
            final_text="",
            session_start=datetime.now().isoformat(),
            session_end=None,
            confidence_improved=False
        )
        
        logger.info(f"Readback session created: {session_id}")
        return session
    
    def generate_readback_audio(self, session: ReadbackSession) -> str:
        """
        Generate audio for readback confirmation
        
        Args:
            session: Readback session containing text to convert to speech
            
        Returns:
            Path to generated audio file
        """
        if not self.tts_enabled:
            logger.warning("TTS disabled - cannot generate readback audio")
            return None
        
        try:
            # In a real implementation, this would use a TTS engine
            # For MVP, we'll use a placeholder that returns the text
            audio_path = f"temp/readback_{session.session_id}.wav"
            
            # Placeholder for TTS generation
            # tts_engine.generate_speech(
            #     text=session.readback_text,
            #     output_path=audio_path,
            #     voice=self.tts_voice,
            #     speed=self.tts_speed
            # )
            
            session.readback_audio_path = audio_path
            logger.info(f"Readback audio generated: {audio_path}")
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Failed to generate readback audio: {e}")
            return None
    
    def process_user_response(self, session: ReadbackSession, 
                            user_response: ReadbackStatus, 
                            corrections: List[Dict] = None) -> ReadbackSession:
        """
        Process user response to readback confirmation
        
        Args:
            session: Active readback session
            user_response: User's response to the readback
            corrections: Optional list of corrections if text was rejected
            
        Returns:
            Updated ReadbackSession with response processed
        """
        session.user_response = user_response
        session.session_end = datetime.now().isoformat()
        
        if corrections:
            session.corrections = corrections
        
        # Process based on response type
        if user_response == ReadbackStatus.CONFIRMED:
            session.final_text = session.voice_capture.transcribed_text
            session.confidence_improved = True
            logger.info(f"Readback confirmed for session {session.session_id}")
            
        elif user_response == ReadbackStatus.REJECTED:
            if corrections:
                session.final_text = self._apply_corrections(
                    session.voice_capture.transcribed_text, 
                    corrections
                )
                session.confidence_improved = True
                logger.info(f"Readback rejected with corrections for session {session.session_id}")
            else:
                # User rejected but provided no corrections - flag for manual review
                session.final_text = session.voice_capture.transcribed_text
                session.confidence_improved = False
                logger.warning(f"Readback rejected without corrections for session {session.session_id}")
                
        elif user_response == ReadbackStatus.SKIPPED:
            session.final_text = session.voice_capture.transcribed_text
            session.confidence_improved = False
            logger.info(f"Readback skipped for session {session.session_id}")
            
        else:
            logger.error(f"Unknown user response: {user_response}")
        
        return session
    
    def validate_final_transcription(self, session: ReadbackSession) -> Dict[str, Any]:
        """
        Validate the final transcription after readback process
        
        Args:
            session: Completed readback session
            
        Returns:
            Validation results including confidence and quality metrics
        """
        validation = {
            "session_id": session.session_id,
            "original_confidence": session.voice_capture.confidence_score,
            "readback_completed": session.user_response != ReadbackStatus.PENDING,
            "user_confirmed": session.user_response == ReadbackStatus.CONFIRMED,
            "corrections_applied": len(session.corrections) > 0,
            "confidence_improved": session.confidence_improved,
            "final_text_length": len(session.final_text),
            "processing_time_seconds": self._calculate_session_duration(session),
            "quality_score": self._calculate_quality_score(session),
            "safety_critical": self._contains_safety_critical_terms(session.final_text),
            "recommended_action": self._get_recommended_action(session)
        }
        
        return validation
    
    def _prepare_readback_text(self, original_text: str) -> str:
        """
        Prepare text for readback, potentially with improvements for clarity
        
        Args:
            original_text: Original transcribed text
            
        Returns:
            Text prepared for readback (may include clarifications)
        """
        # Add pauses for better readback comprehension
        readback_text = original_text
        
        # Add slight pauses after medical terms for clarity
        medical_terms = ['mg', 'mcg', 'ml', 'tablets', 'capsules', 'injection', 
                        'patient', 'experienced', 'developed', 'symptoms']
        
        for term in medical_terms:
            readback_text = readback_text.replace(term, f"{term},")
        
        # Clean up any double commas
        readback_text = readback_text.replace(",,", ",")
        
        return readback_text
    
    def _detect_potential_transcription_errors(self, text: str) -> List[str]:
        """
        Detect potential transcription errors in medical context
        
        Args:
            text: Transcribed text to analyze
            
        Returns:
            List of potential error descriptions
        """
        errors = []
        text_lower = text.lower()
        
        # Common medication name confusions
        medication_errors = [
            ("Lasix", "last six"),
            ("Zestril", "yes trail"),
            ("Norvasc", "nor ask"),
            ("Lipitor", "lit a tour"),
            ("Glucophage", "glue go page")
        ]
        
        for correct, error in medication_errors:
            if error in text_lower:
                errors.append(f"Possible medication name error: '{error}' might be '{correct}'")
        
        # Dosage pattern issues
        import re
        
        # Look for potential dosage confusions
        dosage_patterns = re.findall(r'\d+\s*(?:mg|mcg|ml|tablets|capsules)', text_lower)
        if not dosage_patterns and any(word in text_lower for word in ['dose', 'dosage', 'took', 'given']):
            errors.append("Dosage mentioned but no clear dosage amount detected")
        
        # Medical term variations that might be errors
        medical_confusion = [
            ("shortness of breath", ["shortage of breath", "short of breath"]),
            ("nausea", ["nasa", "nauseous"]),
            ("diarrhea", ["diarrheal", "dire rear"]),
            ("hypertension", ["high attention"])
        ]
        
        for correct, variations in medical_confusion:
            for variation in variations:
                if variation in text_lower:
                    errors.append(f"Possible medical term error: '{variation}' might be '{correct}'")
        
        return errors
    
    def _apply_corrections(self, original_text: str, corrections: List[Dict]) -> str:
        """
        Apply user corrections to the original text
        
        Args:
            original_text: Original transcribed text
            corrections: List of correction dictionaries
            
        Returns:
            Corrected text
        """
        corrected_text = original_text
        
        # Sort corrections by position (reverse order to maintain positions)
        sorted_corrections = sorted(corrections, 
                                  key=lambda x: x.get('position', 0), 
                                  reverse=True)
        
        for correction in sorted_corrections:
            if 'original' in correction and 'corrected' in correction:
                corrected_text = corrected_text.replace(
                    correction['original'], 
                    correction['corrected']
                )
        
        return corrected_text
    
    def _calculate_session_duration(self, session: ReadbackSession) -> float:
        """Calculate total session duration in seconds"""
        if not session.session_end:
            return 0.0
        
        start = datetime.fromisoformat(session.session_start)
        end = datetime.fromisoformat(session.session_end)
        return (end - start).total_seconds()
    
    def _calculate_quality_score(self, session: ReadbackSession) -> float:
        """
        Calculate overall quality score for the readback session (0-1)
        
        Args:
            session: Completed readback session
            
        Returns:
            Quality score between 0 and 1
        """
        score = 0.0
        
        # Base score from original confidence
        score += session.voice_capture.confidence_score * 0.4
        
        # Bonus for user confirmation
        if session.user_response == ReadbackStatus.CONFIRMED:
            score += 0.3
        elif session.user_response == ReadbackStatus.REJECTED and session.corrections:
            score += 0.2  # User engaged and provided corrections
        
        # Bonus for reasonable text length
        word_count = len(session.final_text.split())
        if 5 <= word_count <= 100:
            score += 0.2
        elif word_count > 100:
            score += 0.1
        
        # Penalty for very short sessions (likely incomplete)
        duration = self._calculate_session_duration(session)
        if duration < 5:  # Less than 5 seconds - likely rushed
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _contains_safety_critical_terms(self, text: str) -> bool:
        """Check if text contains safety-critical medical terms"""
        critical_terms = ['death', 'died', 'fatal', 'life-threatening', 'severe', 
                         'emergency', 'hospitalization', 'icu', 'intensive care',
                         'anaphylaxis', 'cardiac arrest', 'stroke', 'seizure']
        
        text_lower = text.lower()
        return any(term in text_lower for term in critical_terms)
    
    def _get_recommended_action(self, session: ReadbackSession) -> str:
        """
        Get recommended action based on session results
        
        Args:
            session: Completed readback session
            
        Returns:
            Recommended action string
        """
        quality_score = self._calculate_quality_score(session)
        
        if quality_score >= 0.8:
            return "proceed"
        elif quality_score >= 0.6:
            return "review_recommended"
        elif session.user_response == ReadbackStatus.REJECTED and not session.corrections:
            return "manual_review_required"
        else:
            return "re_record_recommended"
    
    def _generate_session_id(self, voice_capture: VoiceCapture) -> str:
        """Generate unique session ID"""
        import hashlib
        data = f"{voice_capture.timestamp}-{voice_capture.transcribed_text[:50]}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

# Factory function for easy integration
def create_readback_confirmer(config: Dict) -> VoiceReadbackConfirmer:
    """Factory function to create VoiceReadbackConfirmer with config"""
    return VoiceReadbackConfirmer(config) 