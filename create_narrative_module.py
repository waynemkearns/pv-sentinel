#!/usr/bin/env python3
"""Helper script to create narrative comparison module"""

content = '''"""
PV Sentinel - Narrative Comparison Module
Critical P0 Feature: Side-by-side comparison with edit tracking and justification
"""

import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import difflib
import re

logger = logging.getLogger(__name__)

class ChangeType(Enum):
    ADDITION = "addition"
    DELETION = "deletion"
    MODIFICATION = "modification"
    REORDER = "reorder"
    STYLE_CHANGE = "style_change"
    CLINICAL_UPDATE = "clinical_update"

class ChangeSource(Enum):
    AI_GENERATED = "ai_generated"
    HUMAN_EDIT = "human_edit"
    SYSTEM_AUTO = "system_auto"
    TEMPLATE_MERGE = "template_merge"
    COMPLIANCE_AUTO = "compliance_auto"

class ChangeSeverity(Enum):
    CRITICAL = "critical"
    SIGNIFICANT = "significant"
    MINOR = "minor"
    COSMETIC = "cosmetic"

@dataclass
class NarrativeChange:
    change_id: str
    section: str
    change_type: ChangeType
    change_source: ChangeSource
    severity: ChangeSeverity
    original_text: str
    modified_text: str
    justification: str
    changed_by: str
    timestamp: str
    line_number: Optional[int]
    character_position: Optional[int]
    context_before: str
    context_after: str
    clinical_impact: str
    requires_review: bool
    reviewed_by: Optional[str]
    review_timestamp: Optional[str]
    review_status: str
    
    def __post_init__(self):
        if not self.change_id:
            self.change_id = self._generate_change_id()
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.review_status:
            self.review_status = "pending"
    
    def _generate_change_id(self) -> str:
        content_hash = hashlib.sha256(f"{self.original_text}{self.modified_text}".encode()).hexdigest()[:8]
        timestamp_hash = hashlib.sha256(self.timestamp.encode()).hexdigest()[:4]
        return f"NC-{content_hash}-{timestamp_hash}"

@dataclass
class NarrativeVersion:
    version_id: str
    case_id: str
    version_number: int
    version_type: str
    narrative_content: str
    created_by: str
    creation_timestamp: str
    changes_from_previous: List[NarrativeChange]
    word_count: int
    section_breakdown: Dict[str, str]
    clinical_completeness_score: float
    compliance_score: float
    integrity_hash: str
    locked: bool
    lock_reason: Optional[str]
    
    def __post_init__(self):
        if not self.version_id:
            self.version_id = self._generate_version_id()
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.now().isoformat()
        if not self.word_count:
            self.word_count = len(self.narrative_content.split())
        if not self.integrity_hash:
            self.integrity_hash = self._calculate_integrity_hash()
    
    def _generate_version_id(self) -> str:
        case_hash = hashlib.sha256(self.case_id.encode()).hexdigest()[:8]
        version_hash = hashlib.sha256(f"{self.version_number}".encode()).hexdigest()[:4]
        return f"NV-{case_hash}-v{self.version_number}-{version_hash}"
    
    def _calculate_integrity_hash(self) -> str:
        content = f"{self.narrative_content}{self.creation_timestamp}{self.created_by}"
        return hashlib.sha256(content.encode()).hexdigest()

@dataclass  
class ComparisonResult:
    comparison_id: str
    case_id: str
    version_1: NarrativeVersion
    version_2: NarrativeVersion
    changes: List[NarrativeChange]
    summary_stats: Dict[str, Any]
    clinical_impact_assessment: str
    requires_medical_review: bool
    comparison_timestamp: str
    generated_by: str
    
    def __post_init__(self):
        if not self.comparison_id:
            self.comparison_id = self._generate_comparison_id()
        if not self.comparison_timestamp:
            self.comparison_timestamp = datetime.now().isoformat()
    
    def _generate_comparison_id(self) -> str:
        v1_hash = self.version_1.version_id[-8:]
        v2_hash = self.version_2.version_id[-8:]
        return f"COMP-{v1_hash}-{v2_hash}"

class NarrativeComparator:
    def __init__(self, config: Dict):
        self.config = config
        self.comparison_enabled = config.get('narrative_comparison', {}).get('enabled', True)
        self.auto_severity_assessment = config.get('narrative_comparison', {}).get('auto_severity', True)
        self.require_justification = config.get('narrative_comparison', {}).get('require_justification', True)
        self.clinical_terms_file = config.get('narrative_comparison', {}).get('clinical_terms_file', 'config/clinical_terms.json')
        
        self._load_clinical_terms()
        self._initialize_change_patterns()
        
        logger.info(f"Narrative comparator initialized - comparison: {self.comparison_enabled}")
    
    def _load_clinical_terms(self):
        try:
            with open(self.clinical_terms_file, 'r', encoding='utf-8') as f:
                terms_data = json.load(f)
                
            self.critical_terms = set(terms_data.get('critical_terms', []))
            self.significant_terms = set(terms_data.get('significant_terms', []))
            self.temporal_markers = set(terms_data.get('temporal_markers', []))
            
        except FileNotFoundError:
            self.critical_terms = {'death', 'died', 'fatal', 'life-threatening', 'hospitalization'}
            self.significant_terms = {'adverse', 'reaction', 'side effect', 'symptom', 'onset'}
            self.temporal_markers = {'started', 'began', 'onset', 'duration', 'continued'}
    
    def _initialize_change_patterns(self):
        self.critical_change_patterns = [
            r'\\b(death|died|fatal|life-threatening)\\b',
            r'\\b(hospitalization|emergency|ICU)\\b',
            r'\\b(serious|severe|critical)\\b',
        ]
        
        self.temporal_change_patterns = [
            r'\\b(\\d+)\\s*(day|week|month|hour|minute)s?\\b',
            r'\\b(immediately|within|after|before|during)\\b',
            r'\\b(onset|duration|started|began|stopped)\\b',
        ]
        
        self.medication_change_patterns = [
            r'\\b(\\d+\\.?\\d*)\\s*(mg|ml|g|units?)\\b',
            r'\\b(daily|twice|once|every|per)\\b',
            r'\\b(increased|decreased|discontinued|started)\\b',
        ]
    
    def compare_narratives(self, version_1: NarrativeVersion, version_2: NarrativeVersion,
                          comparison_context: str = "routine") -> ComparisonResult:
        if not self.comparison_enabled:
            raise RuntimeError("Narrative comparison is disabled")
        
        diff_changes = self._generate_detailed_diff(version_1.narrative_content, version_2.narrative_content)
        analyzed_changes = self._analyze_changes(diff_changes, version_1, version_2)
        summary_stats = self._generate_summary_stats(analyzed_changes)
        clinical_impact = self._assess_clinical_impact(analyzed_changes)
        requires_review = self._requires_medical_review(analyzed_changes)
        
        comparison = ComparisonResult(
            comparison_id="",
            case_id=version_1.case_id,
            version_1=version_1,
            version_2=version_2,
            changes=analyzed_changes,
            summary_stats=summary_stats,
            clinical_impact_assessment=clinical_impact,
            requires_medical_review=requires_review,
            comparison_timestamp="",
            generated_by="system"
        )
        
        logger.info(f"Generated narrative comparison: {comparison.comparison_id}")
        return comparison
    
    def _generate_detailed_diff(self, text1: str, text2: str) -> List[Dict]:
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        differ = difflib.unified_diff(lines1, lines2, lineterm='')
        diff_changes = []
        
        current_line = 0
        for line in differ:
            if line.startswith('-'):
                diff_changes.append({
                    'type': 'deletion',
                    'line_number': current_line,
                    'content': line[1:],
                    'original_text': line[1:],
                    'modified_text': ''
                })
            elif line.startswith('+'):
                diff_changes.append({
                    'type': 'addition',
                    'line_number': current_line,
                    'content': line[1:],
                    'original_text': '',
                    'modified_text': line[1:]
                })
            elif line.startswith('@@'):
                continue
            else:
                current_line += 1
        
        return diff_changes
    
    def _analyze_changes(self, diff_changes: List[Dict], version_1: NarrativeVersion, 
                        version_2: NarrativeVersion) -> List[NarrativeChange]:
        analyzed_changes = []
        
        for diff in diff_changes:
            change_type = self._determine_change_type(diff)
            severity = self._assess_change_severity(diff['original_text'], diff['modified_text'])
            section = self._identify_section(diff.get('line_number', 0), version_1.narrative_content)
            context_before, context_after = self._extract_change_context(
                diff.get('line_number', 0), version_1.narrative_content, version_2.narrative_content
            )
            clinical_impact = self._assess_single_change_impact(diff['original_text'], diff['modified_text'])
            requires_review = severity in [ChangeSeverity.CRITICAL, ChangeSeverity.SIGNIFICANT]
            
            change = NarrativeChange(
                change_id="",
                section=section,
                change_type=change_type,
                change_source=ChangeSource.HUMAN_EDIT,
                severity=severity,
                original_text=diff['original_text'],
                modified_text=diff['modified_text'],
                justification="",
                changed_by="unknown",
                timestamp="",
                line_number=diff.get('line_number'),
                character_position=None,
                context_before=context_before,
                context_after=context_after,
                clinical_impact=clinical_impact,
                requires_review=requires_review,
                reviewed_by=None,
                review_timestamp=None,
                review_status="pending"
            )
            
            analyzed_changes.append(change)
        
        return analyzed_changes
    
    def _determine_change_type(self, diff: Dict) -> ChangeType:
        if diff['type'] == 'addition':
            return ChangeType.ADDITION
        elif diff['type'] == 'deletion':
            return ChangeType.DELETION
        else:
            return ChangeType.MODIFICATION
    
    def _assess_change_severity(self, original_text: str, modified_text: str) -> ChangeSeverity:
        if not self.auto_severity_assessment:
            return ChangeSeverity.MINOR
        
        combined_text = f"{original_text} {modified_text}".lower()
        
        for pattern in self.critical_change_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return ChangeSeverity.CRITICAL
        
        has_clinical_terms = any(term in combined_text for term in self.significant_terms)
        has_temporal_changes = any(term in combined_text for term in self.temporal_markers)
        
        if has_clinical_terms or has_temporal_changes:
            return ChangeSeverity.SIGNIFICANT
        
        for pattern in self.medication_change_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return ChangeSeverity.SIGNIFICANT
        
        total_change_length = len(original_text) + len(modified_text)
        if total_change_length > 100:
            return ChangeSeverity.MINOR
        
        return ChangeSeverity.COSMETIC
    
    def _identify_section(self, line_number: int, narrative_content: str) -> str:
        return "content"
    
    def _extract_change_context(self, line_number: int, text1: str, text2: str) -> Tuple[str, str]:
        return "", ""
    
    def _assess_single_change_impact(self, original_text: str, modified_text: str) -> str:
        if not original_text and modified_text:
            return f"Added new information: {modified_text[:50]}..."
        elif original_text and not modified_text:
            return f"Removed information: {original_text[:50]}..."
        else:
            return f"Modified information from '{original_text[:30]}...' to '{modified_text[:30]}...'"
    
    def _assess_clinical_impact(self, changes: List[NarrativeChange]) -> str:
        critical_count = sum(1 for c in changes if c.severity == ChangeSeverity.CRITICAL)
        significant_count = sum(1 for c in changes if c.severity == ChangeSeverity.SIGNIFICANT)
        total_changes = len(changes)
        
        if critical_count > 0:
            return f"HIGH IMPACT: {critical_count} critical changes detected affecting clinical meaning"
        elif significant_count > 3:
            return f"MODERATE IMPACT: {significant_count} significant changes detected"
        elif total_changes > 10:
            return f"MODERATE IMPACT: Extensive editing with {total_changes} total changes"
        else:
            return f"LOW IMPACT: {total_changes} minor changes with no significant clinical impact"
    
    def _requires_medical_review(self, changes: List[NarrativeChange]) -> bool:
        has_critical = any(c.severity == ChangeSeverity.CRITICAL for c in changes)
        significant_count = sum(1 for c in changes if c.severity == ChangeSeverity.SIGNIFICANT)
        return has_critical or significant_count >= 3
    
    def _generate_summary_stats(self, changes: List[NarrativeChange]) -> Dict[str, Any]:
        total_changes = len(changes)
        
        by_severity = {}
        for severity in ChangeSeverity:
            by_severity[severity.value] = sum(1 for c in changes if c.severity == severity)
        
        by_type = {}
        for change_type in ChangeType:
            by_type[change_type.value] = sum(1 for c in changes if c.change_type == change_type)
        
        by_section = {}
        for change in changes:
            section = change.section
            by_section[section] = by_section.get(section, 0) + 1
        
        return {
            'total_changes': total_changes,
            'by_severity': by_severity,
            'by_type': by_type,
            'by_section': by_section,
            'requires_review_count': sum(1 for c in changes if c.requires_review),
            'timestamp': datetime.now().isoformat()
        }

class NarrativeVersionManager:
    def __init__(self, config: Dict):
        self.config = config
        self.versions_file = 'storage/narrative_versions.json'
        self.comparisons_file = 'storage/narrative_comparisons.json'
        
        self.narrative_versions: Dict[str, List[NarrativeVersion]] = {}
        self.comparisons: Dict[str, ComparisonResult] = {}
        
        self.comparator = NarrativeComparator(config)
        
        self._load_versions()
        self._load_comparisons()
        
        logger.info("Narrative version manager initialized")
    
    def create_new_version(self, case_id: str, narrative_content: str, created_by: str,
                          version_type: str = "draft") -> NarrativeVersion:
        existing_versions = self.narrative_versions.get(case_id, [])
        version_number = len(existing_versions) + 1
        
        section_breakdown = self._parse_narrative_sections(narrative_content)
        
        version = NarrativeVersion(
            version_id="",
            case_id=case_id,
            version_number=version_number,
            version_type=version_type,
            narrative_content=narrative_content,
            created_by=created_by,
            creation_timestamp="",
            changes_from_previous=[],
            word_count=0,
            section_breakdown=section_breakdown,
            clinical_completeness_score=self._assess_completeness(narrative_content),
            compliance_score=self._assess_compliance(narrative_content),
            integrity_hash="",
            locked=False,
            lock_reason=None
        )
        
        if existing_versions:
            previous_version = existing_versions[-1]
            comparison = self.comparator.compare_narratives(previous_version, version)
            version.changes_from_previous = comparison.changes
            self.comparisons[comparison.comparison_id] = comparison
        
        if case_id not in self.narrative_versions:
            self.narrative_versions[case_id] = []
        self.narrative_versions[case_id].append(version)
        
        self._save_versions()
        self._save_comparisons()
        
        logger.info(f"Created narrative version {version.version_id}")
        return version
    
    def get_versions(self, case_id: str) -> List[NarrativeVersion]:
        return self.narrative_versions.get(case_id, [])
    
    def get_latest_version(self, case_id: str) -> Optional[NarrativeVersion]:
        versions = self.get_versions(case_id)
        return versions[-1] if versions else None
    
    def compare_versions(self, case_id: str, version_1_num: int, version_2_num: int) -> Optional[ComparisonResult]:
        versions = self.get_versions(case_id)
        
        if version_1_num > len(versions) or version_2_num > len(versions):
            return None
        
        version_1 = versions[version_1_num - 1]
        version_2 = versions[version_2_num - 1]
        
        return self.comparator.compare_narratives(version_1, version_2)
    
    def _parse_narrative_sections(self, narrative_content: str) -> Dict[str, str]:
        return {"content": narrative_content}
    
    def _assess_completeness(self, narrative_content: str) -> float:
        required_elements = ['patient', 'medication', 'dose', 'symptom', 'onset', 'duration', 'outcome']
        content_lower = narrative_content.lower()
        present_elements = sum(1 for element in required_elements if element in content_lower)
        return present_elements / len(required_elements)
    
    def _assess_compliance(self, narrative_content: str) -> float:
        compliance_indicators = ['timeline', 'causality', 'outcome', 'follow-up', 'concomitant']
        content_lower = narrative_content.lower()
        present_indicators = sum(1 for indicator in compliance_indicators if indicator in content_lower)
        return present_indicators / len(compliance_indicators)
    
    def _load_versions(self):
        try:
            import os
            if os.path.exists(self.versions_file):
                with open(self.versions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for case_id, versions_data in data.items():
                    versions = [NarrativeVersion(**version_data) for version_data in versions_data]
                    self.narrative_versions[case_id] = versions
                
                logger.info(f"Loaded versions for {len(self.narrative_versions)} cases")
        except Exception as e:
            logger.error(f"Failed to load narrative versions: {e}")
    
    def _save_versions(self):
        try:
            import os
            os.makedirs(os.path.dirname(self.versions_file), exist_ok=True)
            
            data = {}
            for case_id, versions in self.narrative_versions.items():
                data[case_id] = [asdict(version) for version in versions]
            
            with open(self.versions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save narrative versions: {e}")
    
    def _load_comparisons(self):
        try:
            import os
            if os.path.exists(self.comparisons_file):
                with open(self.comparisons_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for comp_id, comp_data in data.items():
                    comp_data['version_1'] = NarrativeVersion(**comp_data['version_1'])
                    comp_data['version_2'] = NarrativeVersion(**comp_data['version_2'])
                    comp_data['changes'] = [NarrativeChange(**change_data) for change_data in comp_data['changes']]
                    
                    self.comparisons[comp_id] = ComparisonResult(**comp_data)
                
                logger.info(f"Loaded {len(self.comparisons)} comparisons")
        except Exception as e:
            logger.error(f"Failed to load comparisons: {e}")
    
    def _save_comparisons(self):
        try:
            import os
            os.makedirs(os.path.dirname(self.comparisons_file), exist_ok=True)
            
            data = {}
            for comp_id, comparison in self.comparisons.items():
                data[comp_id] = asdict(comparison)
            
            with open(self.comparisons_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save comparisons: {e}")

def create_narrative_comparison_system(config: Dict) -> NarrativeVersionManager:
    manager = NarrativeVersionManager(config)
    logger.info("Narrative comparison system initialized")
    return manager
'''

with open('backend/narrative_comparison.py', 'w', encoding='utf-8') as f:
    f.write(content.strip())

print("Narrative comparison module created successfully!") 