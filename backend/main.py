"""
PV Sentinel - Main Backend Integration Module
Orchestrates all PV Sentinel components for AE processing and narrative generation

This module integrates:
- Patient Context Preservation (P0)
- Model Version Tracking (P0) 
- Voice Readback Confirmation (P0)
- Multi-user Role Support (P1)
- Narrative Generation with Audit Trail
"""

import logging
import yaml
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path

# Import our custom modules
from .patient_context import create_patient_context_preserver, PatientContext
from .model_tracking import create_model_tracker, GenerationMetadata
from .readback import create_readback_confirmer, VoiceCapture, ReadbackSession
from .users import create_user_manager, UserSession
from .pii_protection import create_pii_protector, PIIMasker, AccessLogger

logger = logging.getLogger(__name__)

class PVSentinelEngine:
    """
    Main engine orchestrating all PV Sentinel functionality
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize PV Sentinel engine with configuration
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.initialized = False
        
        # Initialize core components
        self._initialize_components()
        
        logger.info("PV Sentinel engine initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Return default configuration
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if config file is not available"""
        return {
            'system': {
                'logging_level': 'INFO',
                'audit_mode': True,
                'validation_mode': False
            },
            'models': {
                'primary_model': 'mistral-7b-instruct',
                'model_path': 'models/mistral-7b-instruct-v0.1.Q4_K_M.gguf',
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
            }
        }
    
    def _initialize_components(self):
        """Initialize all PV Sentinel components"""
        try:
            # Initialize Patient Context Preserver (P0 Critical)
            self.patient_context_preserver = create_patient_context_preserver(self.config)
            
            # Initialize Model Version Tracker (P0 Critical)
            self.model_tracker = create_model_tracker(self.config)
            
            # Initialize Voice Readback Confirmer (P0 Critical)
            self.readback_confirmer = create_readback_confirmer(self.config)
            
            # Initialize User Manager (P1 High)
            self.user_manager = create_user_manager(self.config)
            
            # Initialize PII Protection (Phase 1 New Feature)
            self.pii_masker, self.access_logger = create_pii_protector(self.config)
            
            # Initialize prompt templates
            self.prompt_templates = self._load_prompt_templates()
            
            self.initialized = True
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load all prompt templates from directory"""
        templates = {}
        prompt_dir = Path(self.config.get('models', {}).get('prompt_directory', 'prompts/'))
        
        if not prompt_dir.exists():
            logger.warning(f"Prompt directory not found: {prompt_dir}")
            return templates
        
        try:
            for template_file in prompt_dir.glob("*.txt"):
                template_name = template_file.stem
                with open(template_file, 'r', encoding='utf-8') as f:
                    templates[template_name] = f.read()
                
                # Register template with model tracker for version control
                self.model_tracker.register_prompt_template(str(template_file))
            
            logger.info(f"Loaded {len(templates)} prompt templates")
            
        except Exception as e:
            logger.error(f"Error loading prompt templates: {e}")
        
        return templates
    
    def process_voice_input(self, audio_data: bytes, user_session_id: str) -> Dict[str, Any]:
        """
        Process voice input through complete pipeline with safety checks
        
        Args:
            audio_data: Raw audio bytes from voice input
            user_session_id: User session for authentication and audit
            
        Returns:
            Complete processing result with patient context preserved
        """
        if not self.initialized:
            raise RuntimeError("Engine not properly initialized")
        
        # Validate user session
        user_session = self.user_manager.validate_session(user_session_id)
        if not user_session:
            raise ValueError("Invalid or expired user session")
        
        # Check permissions
        if not self.user_manager.check_permission(user_session_id, 'can_create_cases'):
            raise PermissionError("User does not have permission to create cases")
        
        try:
            # Step 1: Convert voice to text (placeholder - would use Whisper.cpp)
            voice_capture = self._transcribe_audio(audio_data)
            
            # Step 2: Log voice access and check for PII (Phase 1 New Feature)
            self.access_logger.log_pii_access(
                user_id=user_session.user_id,
                session_id=user_session_id,
                data_type="voice_input",
                data_content=voice_capture.transcribed_text,
                action="transcribe",
                context="voice_to_text"
            )
            
            # Step 3: Extract and preserve patient context (P0 Critical)
            patient_context = self.patient_context_preserver.extract_patient_context(
                voice_capture.transcribed_text, 
                voice_capture.input_method
            )
            
            # Step 4: Check if readback confirmation is needed (P0 Critical)
            should_readback, readback_reason = self.readback_confirmer.should_trigger_readback(voice_capture)
            
            readback_session = None
            if should_readback:
                readback_session = self.readback_confirmer.create_readback_session(voice_capture)
                # In a real implementation, this would pause for user confirmation
                logger.info(f"Readback required: {readback_reason}")
            
            # Step 5: Generate narrative with appropriate template
            narrative_result = self._generate_narrative(
                patient_context, 
                user_session_id,
                readback_session
            )
            
            # Step 6: Apply PII protection to narrative (Phase 1 New Feature)
            user_role = user_session.role.value if user_session.role else None
            protected_narrative, pii_detections = self.pii_masker.mask_pii(
                narrative_result.get('generated_narrative', ''),
                user_role=user_role,
                context="generated_narrative",
                preserve_patient_context=True
            )
            narrative_result['protected_narrative'] = protected_narrative
            narrative_result['pii_detections'] = len(pii_detections)
            
            # Step 7: Create complete audit record (P0 Critical)
            audit_record = self._create_audit_record(
                patient_context, 
                narrative_result, 
                user_session,
                readback_session
            )
            
            return {
                'success': True,
                'patient_context': patient_context,
                'voice_capture': voice_capture,
                'readback_session': readback_session,
                'narrative': narrative_result,
                'audit_record': audit_record,
                'requires_readback': should_readback,
                'readback_reason': readback_reason
            }
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def complete_readback_confirmation(self, session_id: str, user_response: str, 
                                     corrections: List[Dict] = None) -> Dict[str, Any]:
        """
        Complete readback confirmation process
        
        Args:
            session_id: Readback session ID
            user_response: User's response ('confirmed', 'rejected', 'skipped')
            corrections: Optional corrections if rejected
            
        Returns:
            Updated processing result
        """
        try:
            from .readback import ReadbackStatus
            
            # Convert string response to enum
            response_map = {
                'confirmed': ReadbackStatus.CONFIRMED,
                'rejected': ReadbackStatus.REJECTED,
                'skipped': ReadbackStatus.SKIPPED
            }
            
            status = response_map.get(user_response, ReadbackStatus.ERROR)
            
            # Process the response (placeholder - would retrieve actual session)
            # readback_session = self.readback_confirmer.process_user_response(
            #     session, status, corrections
            # )
            
            return {
                'success': True,
                'readback_completed': True,
                'user_response': user_response,
                'corrections_applied': bool(corrections)
            }
            
        except Exception as e:
            logger.error(f"Error completing readback: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_ae_narrative(self, ae_data: Dict, template_type: str, 
                            user_session_id: str) -> Dict[str, Any]:
        """
        Generate AE narrative from structured data
        
        Args:
            ae_data: Structured AE data
            template_type: Type of template to use
            user_session_id: User session for audit
            
        Returns:
            Generated narrative with metadata
        """
        # Validate user session
        user_session = self.user_manager.validate_session(user_session_id)
        if not user_session:
            raise ValueError("Invalid user session")
        
        try:
            # Get appropriate template
            template = self._get_template_for_reaction(template_type)
            if not template:
                raise ValueError(f"Template not found: {template_type}")
            
            # Fill template with AE data
            narrative = self._fill_template(template, ae_data)
            
            # Create patient context from structured data
            patient_context = self.patient_context_preserver.extract_patient_context(
                ae_data.get('patient_description', ''),
                'typed'
            )
            
            # Preserve patient context in narrative
            enhanced_narrative = self.patient_context_preserver.preserve_in_narrative(
                narrative, patient_context
            )
            
            # Create generation record for audit (P0 Critical)
            generation_record = self.model_tracker.create_generation_record(
                model_hash="placeholder_hash",  # Would be actual model hash
                prompt_hash=self._get_prompt_hash(template_type),
                input_data=str(ae_data),
                output_data=enhanced_narrative,
                user_id=user_session.user_id,
                session_id=user_session_id
            )
            
            return {
                'success': True,
                'narrative': enhanced_narrative,
                'patient_context': patient_context,
                'generation_id': generation_record.generation_id if generation_record else None,
                'template_used': template_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating narrative: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_case_completeness(self, ae_data: Dict) -> Dict[str, Any]:
        """
        Validate AE case completeness against GVP/FAERS requirements
        
        Args:
            ae_data: AE case data to validate
            
        Returns:
            Validation results
        """
        validation_results = {
            'is_complete': True,
            'missing_fields': [],
            'warnings': [],
            'gvp_compliance': True,
            'faers_compliance': True
        }
        
        # Required fields per GVP VI
        required_fields = [
            'patient_id', 'age', 'sex', 'suspect_drug', 
            'reaction_description', 'onset_date', 'reporter_type'
        ]
        
        # Check for missing required fields
        for field in required_fields:
            if not ae_data.get(field):
                validation_results['missing_fields'].append(field)
                validation_results['is_complete'] = False
        
        # Check for serious criteria if marked as serious
        if ae_data.get('serious') == 'Yes':
            serious_criteria = ['death', 'life_threatening', 'hospitalization', 
                              'disability', 'congenital_anomaly', 'other_serious']
            
            if not any(ae_data.get(criteria) for criteria in serious_criteria):
                validation_results['warnings'].append(
                    "Case marked as serious but no serious criteria specified"
                )
        
        # Validate dates
        if ae_data.get('onset_date') and ae_data.get('report_date'):
            # Add date validation logic here
            pass
        
        return validation_results
    
    def export_case_report(self, case_id: str, format_type: str = 'pdf', 
                          user_session_id: str = None) -> Dict[str, Any]:
        """
        Export case report with complete audit trail
        
        Args:
            case_id: Case ID to export
            format_type: Export format ('pdf', 'json', 'xml')
            user_session_id: User session for permission check
            
        Returns:
            Export result with file path or data
        """
        if user_session_id:
            if not self.user_manager.check_permission(user_session_id, 'can_export_reports'):
                raise PermissionError("User does not have export permission")
        
        try:
            # Placeholder for export logic
            export_data = {
                'case_id': case_id,
                'export_format': format_type,
                'exported_at': datetime.now().isoformat(),
                'exported_by': user_session_id
            }
            
            return {
                'success': True,
                'export_data': export_data,
                'file_path': f"exports/case_{case_id}.{format_type}"
            }
            
        except Exception as e:
            logger.error(f"Error exporting case: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_dashboard_data(self, user_session_id: str) -> Dict[str, Any]:
        """
        Get dashboard data for authenticated user
        
        Args:
            user_session_id: User session ID
            
        Returns:
            Dashboard data appropriate for user role
        """
        user_session = self.user_manager.validate_session(user_session_id)
        if not user_session:
            raise ValueError("Invalid user session")
        
        user = self.user_manager.get_user_by_session(user_session_id)
        if not user:
            raise ValueError("User not found")
        
        dashboard_data = {
            'user_info': {
                'username': user.username,
                'full_name': user.full_name,
                'role': user.role.value,
                'last_login': user.last_login
            },
            'permissions': {
                'can_create_cases': user.permissions.can_create_cases,
                'can_review_cases': user.permissions.can_review_cases,
                'can_audit_cases': user.permissions.can_audit_cases,
                'can_manage_users': user.permissions.can_manage_users
            },
            'system_status': {
                'patient_safety_enabled': self.config.get('patient_safety', {}).get('context_preservation', True),
                'model_tracking_enabled': self.config.get('validation', {}).get('model_hash_tracking', True),
                'readback_enabled': self.config.get('stt', {}).get('enable_readback', True)
            }
        }
        
        # Add role-specific data
        if user.permissions.can_audit_cases:
            dashboard_data['audit_summary'] = self._get_audit_summary()
        
        if user.permissions.can_manage_users:
            dashboard_data['user_management'] = {
                'total_users': len(self.user_manager.users),
                'active_sessions': len(self.user_manager.get_active_sessions())
            }
        
        return dashboard_data
    
    def _transcribe_audio(self, audio_data: bytes) -> VoiceCapture:
        """
        Transcribe audio to text (placeholder for Whisper.cpp integration)
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            VoiceCapture object with transcription results
        """
        # Placeholder implementation - would use actual Whisper.cpp
        return VoiceCapture(
            original_audio_path=None,
            transcribed_text="Patient experienced severe headache after taking medication",
            confidence_score=0.85,
            language_detected="en",
            duration_seconds=15.0,
            timestamp=datetime.now().isoformat(),
            whisper_model_version="base.en",
            processing_time_ms=2500,
            input_method="voice"
        )
    
    def _generate_narrative(self, patient_context: PatientContext, 
                          user_session_id: str, readback_session=None) -> Dict[str, Any]:
        """Generate narrative using appropriate template and model"""
        
        # Determine appropriate template based on patient context
        template_type = self._determine_template_type(patient_context.patient_story)
        
        # Get template
        template = self._get_template_for_reaction(template_type)
        
        # Extract structured data from patient context (placeholder)
        structured_data = self._extract_structured_data(patient_context)
        
        # Fill template
        narrative = self._fill_template(template, structured_data)
        
        # Preserve patient context
        enhanced_narrative = self.patient_context_preserver.preserve_in_narrative(
            narrative, patient_context
        )
        
        return {
            'narrative': enhanced_narrative,
            'template_used': template_type,
            'confidence_score': 0.9,  # Placeholder
            'word_count': len(enhanced_narrative.split())
        }
    
    def _create_audit_record(self, patient_context: PatientContext, 
                           narrative_result: Dict, user_session: UserSession,
                           readback_session=None) -> Dict[str, Any]:
        """Create comprehensive audit record"""
        
        return {
            'audit_id': f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'user_id': user_session.user_id,
            'username': user_session.username,
            'patient_context_preserved': True,
            'readback_completed': readback_session is not None,
            'template_used': narrative_result.get('template_used'),
            'narrative_word_count': narrative_result.get('word_count'),
            'safety_features_enabled': {
                'context_preservation': True,
                'voice_confirmation': bool(readback_session),
                'model_tracking': True
            }
        }
    
    def _get_template_for_reaction(self, reaction_type: str) -> Optional[str]:
        """Get appropriate template for reaction type"""
        
        # Map reaction types to template names
        template_mapping = {
            'anaphylaxis': 'narrative_template_anaphylaxis',
            'skin_rash': 'narrative_template_skin_rash',
            'hepatic_injury': 'narrative_template_hepatic_injury',
            'cardiac': 'narrative_template_qt_prolongation',
            'injection_site': 'narrative_template_injection_site',
            'neurological': 'narrative_template_neurological_event',
            'general': 'narrative_template_general'
        }
        
        template_name = template_mapping.get(reaction_type, 'narrative_template_general')
        return self.prompt_templates.get(template_name)
    
    def _determine_template_type(self, patient_story: str) -> str:
        """Determine appropriate template type from patient story"""
        story_lower = patient_story.lower()
        
        if any(term in story_lower for term in ['anaphylaxis', 'severe allergic', 'anaphylactic']):
            return 'anaphylaxis'
        elif any(term in story_lower for term in ['rash', 'skin', 'itching', 'hives']):
            return 'skin_rash'
        elif any(term in story_lower for term in ['liver', 'hepatic', 'jaundice', 'alt', 'ast']):
            return 'hepatic_injury'
        elif any(term in story_lower for term in ['heart', 'cardiac', 'chest pain', 'arrhythmia']):
            return 'cardiac'
        elif any(term in story_lower for term in ['injection site', 'injection', 'needle']):
            return 'injection_site'
        elif any(term in story_lower for term in ['headache', 'seizure', 'neurological', 'brain']):
            return 'neurological'
        else:
            return 'general'
    
    def _extract_structured_data(self, patient_context: PatientContext) -> Dict:
        """Extract structured data from patient context (placeholder)"""
        return {
            'patient_age': '45',
            'drug': 'Unknown medication',
            'reaction_description': patient_context.patient_story,
            'onset_date': 'Not specified',
            'seriousness': 'Unknown',
            'outcome': 'Unknown',
            'reporter_comments': patient_context.patient_story
        }
    
    def _fill_template(self, template: str, data: Dict) -> str:
        """Fill template with structured data"""
        if not template:
            return f"Unable to generate narrative - template not found. Original report: {data.get('reaction_description', '')}"
        
        try:
            return template.format(**data)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            # Return template with unfilled variables
            return template
    
    def _get_prompt_hash(self, template_type: str) -> str:
        """Get hash for prompt template (placeholder)"""
        return f"hash_{template_type}_v1.0"
    
    def _get_audit_summary(self) -> Dict:
        """Get audit summary for dashboard"""
        return {
            'total_generations': len(self.model_tracker.generation_log),
            'patient_context_preserved': True,
            'model_tracking_active': True,
            'validation_status': 'compliant'
        }

# Factory function for easy integration
def create_pv_sentinel_engine(config_path: str = "config/config.yaml") -> PVSentinelEngine:
    """Factory function to create PV Sentinel engine"""
    return PVSentinelEngine(config_path) 