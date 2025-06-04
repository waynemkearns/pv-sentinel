"""
PV Sentinel - Model Version Tracking System
Critical P0 Feature: Ensures reproducible and auditable AI-generated content

This module addresses the critical gaps identified in the QA/Validation Manager assessment:
- No prompt-locking mechanism for reproducibility
- Missing hash-based model traceability
- Limited change control documentation
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ModelMetadata:
    """Complete metadata for model version tracking"""
    model_name: str
    model_path: str
    model_hash: str
    model_version: str
    quantization: str
    parameters: Dict[str, Any]
    creation_timestamp: str
    validation_status: str
    gxp_qualified: bool
    
    def __post_init__(self):
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.now().isoformat()

@dataclass
class PromptMetadata:
    """Metadata for prompt version control"""
    prompt_name: str
    prompt_path: str
    prompt_hash: str
    prompt_version: str
    template_variables: List[str]
    clinical_category: str
    creation_timestamp: str
    validation_status: str
    locked: bool
    
    def __post_init__(self):
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.now().isoformat()

@dataclass
class GenerationMetadata:
    """Metadata for each AI generation instance"""
    generation_id: str
    model_metadata: ModelMetadata
    prompt_metadata: PromptMetadata
    input_hash: str
    output_hash: str
    generation_timestamp: str
    user_id: str
    session_id: str
    validation_flags: Dict[str, bool]
    audit_trail: List[Dict]
    
    def __post_init__(self):
        if not self.generation_timestamp:
            self.generation_timestamp = datetime.now().isoformat()
        if not self.generation_id:
            self.generation_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for this generation"""
        data = f"{self.generation_timestamp}-{self.model_metadata.model_hash}-{self.prompt_metadata.prompt_hash}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

class ModelVersionTracker:
    """
    Tracks and validates model versions for GxP compliance and reproducibility
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.tracking_enabled = config.get('validation', {}).get('model_hash_tracking', True)
        self.prompt_locking = config.get('validation', {}).get('prompt_locking', True)
        self.audit_mode = config.get('system', {}).get('audit_mode', True)
        
        # Storage paths
        self.models_path = Path(config.get('models', {}).get('model_path', 'models/'))
        self.prompts_path = Path(config.get('models', {}).get('prompt_directory', 'prompts/'))
        self.metadata_path = Path('validation/model_metadata.json')
        self.generation_log_path = Path('validation/generation_log.json')
        
        # Initialize tracking storage
        self._initialize_tracking()
    
    def _initialize_tracking(self):
        """Initialize tracking storage and load existing metadata"""
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing metadata
        self.model_registry = self._load_model_registry()
        self.prompt_registry = self._load_prompt_registry()
        self.generation_log = self._load_generation_log()
    
    def register_model(self, model_path: str, model_name: str = None) -> ModelMetadata:
        """
        Register a model and create its metadata
        
        Args:
            model_path: Path to the model file
            model_name: Optional name override
            
        Returns:
            ModelMetadata object with complete tracking information
        """
        model_file = Path(model_path)
        
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Calculate model hash
        model_hash = self._calculate_file_hash(model_file)
        
        # Extract model information
        if not model_name:
            model_name = model_file.stem
        
        # Create metadata
        metadata = ModelMetadata(
            model_name=model_name,
            model_path=str(model_file),
            model_hash=model_hash,
            model_version=self._extract_version_from_filename(model_file.name),
            quantization=self._detect_quantization(model_file.name),
            parameters=self._extract_model_parameters(model_file),
            creation_timestamp=datetime.now().isoformat(),
            validation_status="registered",
            gxp_qualified=False  # Must be explicitly qualified
        )
        
        # Register in the model registry
        self.model_registry[model_hash] = metadata
        self._save_model_registry()
        
        logger.info(f"Model registered: {model_name} (hash: {model_hash[:8]}...)")
        return metadata
    
    def register_prompt_template(self, prompt_path: str, clinical_category: str = None) -> PromptMetadata:
        """
        Register a prompt template and create its metadata
        
        Args:
            prompt_path: Path to the prompt template file
            clinical_category: Clinical category (e.g., 'anaphylaxis', 'hepatic_injury')
            
        Returns:
            PromptMetadata object with complete tracking information
        """
        prompt_file = Path(prompt_path)
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
        
        # Read and analyze prompt content
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        # Calculate prompt hash
        prompt_hash = self._calculate_content_hash(prompt_content)
        
        # Extract template variables
        template_variables = self._extract_template_variables(prompt_content)
        
        # Infer clinical category if not provided
        if not clinical_category:
            clinical_category = self._infer_clinical_category(prompt_file.name)
        
        # Create metadata
        metadata = PromptMetadata(
            prompt_name=prompt_file.stem,
            prompt_path=str(prompt_file),
            prompt_hash=prompt_hash,
            prompt_version=self._extract_version_from_filename(prompt_file.name, default="1.0"),
            template_variables=template_variables,
            clinical_category=clinical_category,
            creation_timestamp=datetime.now().isoformat(),
            validation_status="registered",
            locked=False  # Can be locked for GxP use
        )
        
        # Register in the prompt registry
        self.prompt_registry[prompt_hash] = metadata
        self._save_prompt_registry()
        
        logger.info(f"Prompt template registered: {metadata.prompt_name} (hash: {prompt_hash[:8]}...)")
        return metadata
    
    def create_generation_record(self, model_hash: str, prompt_hash: str, 
                               input_data: str, output_data: str,
                               user_id: str = "unknown", session_id: str = "unknown") -> GenerationMetadata:
        """
        Create a complete record of an AI generation for audit purposes
        
        Args:
            model_hash: Hash of the model used
            prompt_hash: Hash of the prompt template used
            input_data: Input data provided to the model
            output_data: Output generated by the model
            user_id: ID of the user who triggered the generation
            session_id: Session ID for tracking
            
        Returns:
            GenerationMetadata object with complete audit trail
        """
        if not self.tracking_enabled:
            logger.warning("Model tracking is disabled - generation not recorded")
            return None
        
        # Validate model and prompt exist
        if model_hash not in self.model_registry:
            raise ValueError(f"Model hash not found in registry: {model_hash}")
        
        if prompt_hash not in self.prompt_registry:
            raise ValueError(f"Prompt hash not found in registry: {prompt_hash}")
        
        # Get metadata
        model_metadata = self.model_registry[model_hash]
        prompt_metadata = self.prompt_registry[prompt_hash]
        
        # Check if prompt is locked for validation
        if self.prompt_locking and not prompt_metadata.locked:
            logger.warning(f"Using unlocked prompt template: {prompt_metadata.prompt_name}")
        
        # Calculate input/output hashes
        input_hash = self._calculate_content_hash(input_data)
        output_hash = self._calculate_content_hash(output_data)
        
        # Create generation metadata
        generation_metadata = GenerationMetadata(
            generation_id="",  # Will be auto-generated
            model_metadata=model_metadata,
            prompt_metadata=prompt_metadata,
            input_hash=input_hash,
            output_hash=output_hash,
            generation_timestamp=datetime.now().isoformat(),
            user_id=user_id,
            session_id=session_id,
            validation_flags={
                "model_registered": True,
                "prompt_registered": True,
                "prompt_locked": prompt_metadata.locked,
                "gxp_qualified": model_metadata.gxp_qualified,
                "audit_complete": True
            },
            audit_trail=[{
                "action": "generation_created",
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "details": {
                    "model": model_metadata.model_name,
                    "prompt": prompt_metadata.prompt_name,
                    "input_length": len(input_data),
                    "output_length": len(output_data)
                }
            }]
        )
        
        # Save to generation log
        self.generation_log.append(asdict(generation_metadata))
        self._save_generation_log()
        
        logger.info(f"Generation recorded: {generation_metadata.generation_id}")
        return generation_metadata
    
    def lock_prompt_template(self, prompt_hash: str, validator_id: str) -> bool:
        """
        Lock a prompt template for GxP validated use
        
        Args:
            prompt_hash: Hash of the prompt to lock
            validator_id: ID of the person validating/locking the prompt
            
        Returns:
            True if successfully locked
        """
        if prompt_hash not in self.prompt_registry:
            raise ValueError(f"Prompt hash not found: {prompt_hash}")
        
        prompt_metadata = self.prompt_registry[prompt_hash]
        prompt_metadata.locked = True
        prompt_metadata.validation_status = "locked"
        
        # Add to audit trail
        lock_record = {
            "action": "prompt_locked",
            "timestamp": datetime.now().isoformat(),
            "validator_id": validator_id,
            "prompt_hash": prompt_hash,
            "prompt_name": prompt_metadata.prompt_name
        }
        
        self._save_prompt_registry()
        logger.info(f"Prompt template locked: {prompt_metadata.prompt_name} by {validator_id}")
        
        return True
    
    def qualify_model_for_gxp(self, model_hash: str, validator_id: str) -> bool:
        """
        Mark a model as GxP qualified after validation
        
        Args:
            model_hash: Hash of the model to qualify
            validator_id: ID of the person qualifying the model
            
        Returns:
            True if successfully qualified
        """
        if model_hash not in self.model_registry:
            raise ValueError(f"Model hash not found: {model_hash}")
        
        model_metadata = self.model_registry[model_hash]
        model_metadata.gxp_qualified = True
        model_metadata.validation_status = "gxp_qualified"
        
        self._save_model_registry()
        logger.info(f"Model GxP qualified: {model_metadata.model_name} by {validator_id}")
        
        return True
    
    def get_generation_audit_trail(self, generation_id: str) -> Optional[Dict]:
        """Get complete audit trail for a specific generation"""
        for generation in self.generation_log:
            if generation.get('generation_id') == generation_id:
                return generation
        return None
    
    def validate_reproducibility(self, generation_id: str) -> Dict[str, bool]:
        """
        Validate that a generation can be reproduced
        
        Returns:
            Dict with validation results
        """
        generation = self.get_generation_audit_trail(generation_id)
        if not generation:
            return {"error": "Generation not found"}
        
        return {
            "model_available": Path(generation['model_metadata']['model_path']).exists(),
            "prompt_available": Path(generation['prompt_metadata']['prompt_path']).exists(),
            "model_hash_matches": self._verify_file_hash(
                generation['model_metadata']['model_path'],
                generation['model_metadata']['model_hash']
            ),
            "prompt_hash_matches": self._verify_prompt_hash(
                generation['prompt_metadata']['prompt_path'],
                generation['prompt_metadata']['prompt_hash']
            ),
            "gxp_qualified": generation['model_metadata']['gxp_qualified'],
            "prompt_locked": generation['prompt_metadata']['locked']
        }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _extract_version_from_filename(self, filename: str, default: str = "1.0") -> str:
        """Extract version from filename (e.g., 'v0.1', 'Q4_K_M')"""
        import re
        version_match = re.search(r'v(\d+\.\d+)', filename)
        if version_match:
            return version_match.group(1)
        return default
    
    def _detect_quantization(self, filename: str) -> str:
        """Detect quantization type from filename"""
        if 'Q4_K_M' in filename:
            return 'Q4_K_M'
        elif 'Q8_0' in filename:
            return 'Q8_0'
        elif 'fp16' in filename:
            return 'fp16'
        else:
            return 'unknown'
    
    def _extract_model_parameters(self, model_file: Path) -> Dict:
        """Extract model parameters (placeholder - would need actual model inspection)"""
        return {
            "file_size": model_file.stat().st_size,
            "format": model_file.suffix,
            "estimated_parameters": "7B"  # Placeholder
        }
    
    def _extract_template_variables(self, prompt_content: str) -> List[str]:
        """Extract template variables from prompt content"""
        import re
        variables = re.findall(r'\{(\w+)\}', prompt_content)
        return list(set(variables))
    
    def _infer_clinical_category(self, filename: str) -> str:
        """Infer clinical category from filename"""
        filename_lower = filename.lower()
        categories = {
            'anaphylaxis': 'anaphylaxis',
            'hepatic': 'hepatic_injury',
            'cardiac': 'cardiac_events',
            'skin': 'dermatologic_events',
            'neurologic': 'neurologic_events',
            'injection': 'injection_site_reactions'
        }
        
        for key, category in categories.items():
            if key in filename_lower:
                return category
        
        return 'general'
    
    def _verify_file_hash(self, file_path: str, expected_hash: str) -> bool:
        """Verify file hash matches expected"""
        try:
            actual_hash = self._calculate_file_hash(Path(file_path))
            return actual_hash == expected_hash
        except Exception:
            return False
    
    def _verify_prompt_hash(self, prompt_path: str, expected_hash: str) -> bool:
        """Verify prompt hash matches expected"""
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            actual_hash = self._calculate_content_hash(content)
            return actual_hash == expected_hash
        except Exception:
            return False
    
    def _load_model_registry(self) -> Dict:
        """Load model registry from storage"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                data = json.load(f)
                return {k: ModelMetadata(**v) for k, v in data.get('models', {}).items()}
        return {}
    
    def _load_prompt_registry(self) -> Dict:
        """Load prompt registry from storage"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                data = json.load(f)
                return {k: PromptMetadata(**v) for k, v in data.get('prompts', {}).items()}
        return {}
    
    def _load_generation_log(self) -> List:
        """Load generation log from storage"""
        if self.generation_log_path.exists():
            with open(self.generation_log_path, 'r') as f:
                return json.load(f)
        return []
    
    def _save_model_registry(self):
        """Save model registry to storage"""
        data = {'models': {k: asdict(v) for k, v in self.model_registry.items()}}
        
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                existing_data = json.load(f)
            existing_data.update(data)
            data = existing_data
        
        with open(self.metadata_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_prompt_registry(self):
        """Save prompt registry to storage"""
        data = {'prompts': {k: asdict(v) for k, v in self.prompt_registry.items()}}
        
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                existing_data = json.load(f)
            existing_data.update(data)
            data = existing_data
        
        with open(self.metadata_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_generation_log(self):
        """Save generation log to storage"""
        with open(self.generation_log_path, 'w') as f:
            json.dump(self.generation_log, f, indent=2)

# Factory function for easy integration
def create_model_tracker(config: Dict) -> ModelVersionTracker:
    """Factory function to create ModelVersionTracker with config"""
    return ModelVersionTracker(config) 