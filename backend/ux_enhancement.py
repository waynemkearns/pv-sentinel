"""
PV Sentinel - UX Enhancement Module (Phase 3)
Advanced User Experience & Accessibility Features

This module provides:
- Mobile-responsive design enhancements
- Accessibility compliance features (WCAG 2.1)
- Advanced analytics dashboard
- Patient-facing interface components
- Enhanced review workflows
- Internationalization support
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid

logger = logging.getLogger(__name__)

class AccessibilityLevel(Enum):
    AA = "AA"
    AAA = "AAA"
    BASIC = "basic"

class DeviceType(Enum):
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"

class InterfaceType(Enum):
    PROFESSIONAL = "professional"
    PATIENT_FACING = "patient_facing"
    REGULATORY = "regulatory"
    SIMPLIFIED = "simplified"

@dataclass
class UserPreferences:
    user_id: str
    theme: str
    font_size: str
    language: str
    accessibility_level: AccessibilityLevel
    interface_type: InterfaceType
    notifications_enabled: bool
    keyboard_navigation: bool
    screen_reader_optimized: bool
    color_blind_support: bool
    motor_accessibility: bool
    created_timestamp: str
    last_updated: str
    
    def __post_init__(self):
        if not self.created_timestamp:
            self.created_timestamp = datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

@dataclass
class AnalyticsEvent:
    event_id: str
    user_id: str
    event_type: str
    page_name: str
    component_id: Optional[str]
    event_data: Dict[str, Any]
    timestamp: str
    session_id: str
    device_type: DeviceType
    user_agent: Optional[str]
    performance_metrics: Dict[str, float]
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"AE-{uuid.uuid4().hex[:8]}"
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class ResponsiveDesignManager:
    def __init__(self, config: Dict):
        self.config = config
        self.breakpoints = {
            'mobile': 768,
            'tablet': 1024,
            'desktop': 1200
        }
        self.responsive_enabled = config.get('ux_enhancement', {}).get('responsive_design', True)
        logger.info("Responsive design manager initialized")
    
    def detect_device_type(self, user_agent: str, screen_width: int) -> DeviceType:
        mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'windows phone']
        user_agent_lower = user_agent.lower()
        
        if any(indicator in user_agent_lower for indicator in mobile_indicators):
            if screen_width <= self.breakpoints['mobile']:
                return DeviceType.MOBILE
            elif screen_width <= self.breakpoints['tablet']:
                return DeviceType.TABLET
        
        if screen_width <= self.breakpoints['mobile']:
            return DeviceType.MOBILE
        elif screen_width <= self.breakpoints['tablet']:
            return DeviceType.TABLET
        else:
            return DeviceType.DESKTOP
    
    def get_responsive_layout(self, device_type: DeviceType) -> Dict[str, Any]:
        layouts = {
            DeviceType.MOBILE: {
                'columns': 1,
                'sidebar_collapsed': True,
                'navigation': 'bottom',
                'font_scale': 1.1,
                'padding': '0.5rem',
                'grid_gap': '0.5rem',
                'max_width': '100%'
            },
            DeviceType.TABLET: {
                'columns': 2,
                'sidebar_collapsed': False,
                'navigation': 'side',
                'font_scale': 1.0,
                'padding': '1rem',
                'grid_gap': '1rem',
                'max_width': '100%'
            },
            DeviceType.DESKTOP: {
                'columns': 3,
                'sidebar_collapsed': False,
                'navigation': 'side',
                'font_scale': 1.0,
                'padding': '1.5rem',
                'grid_gap': '1.5rem',
                'max_width': '1200px'
            }
        }
        return layouts.get(device_type, layouts[DeviceType.DESKTOP])
    
    def generate_responsive_css(self, device_type: DeviceType) -> str:
        layout = self.get_responsive_layout(device_type)
        
        return f"""
        <style>
        /* Responsive Design for {device_type.value} */
        .main .block-container {{
            max-width: {layout['max_width']};
            padding: {layout['padding']};
        }}
        
        .stColumns > div {{
            gap: {layout['grid_gap']};
        }}
        
        .stSelectbox, .stTextInput, .stTextArea {{
            font-size: calc(1rem * {layout['font_scale']});
        }}
        
        @media (max-width: {self.breakpoints['mobile']}px) {{
            .stSidebar {{
                width: 100% !important;
            }}
            
            .main-header {{
                font-size: 1.5rem !important;
                padding: 0.5rem 0 !important;
            }}
        }}
        
        @media (max-width: {self.breakpoints['tablet']}px) {{
            .stColumns {{
                flex-direction: column !important;
            }}
        }}
        </style>
        """

class AccessibilityManager:
    def __init__(self, config: Dict):
        self.config = config
        self.accessibility_enabled = config.get('ux_enhancement', {}).get('accessibility', True)
        self.target_level = AccessibilityLevel(config.get('ux_enhancement', {}).get('wcag_level', 'AA'))
        logger.info(f"Accessibility manager initialized - target level: {self.target_level.value}")
    
    def get_accessibility_css(self, preferences: UserPreferences) -> str:
        css_parts = []
        
        if preferences.theme == 'high_contrast':
            css_parts.append("""
            .stApp {
                background-color: #000000 !important;
                color: #ffffff !important;
            }
            
            .stButton > button {
                background-color: #ffffff !important;
                color: #000000 !important;
                border: 2px solid #ffffff !important;
            }
            """)
        
        font_scales = {'small': 0.875, 'medium': 1.0, 'large': 1.125, 'x_large': 1.25}
        scale = font_scales.get(preferences.font_size, 1.0)
        css_parts.append(f"""
        html, body, .stApp {{
            font-size: calc(16px * {scale}) !important;
        }}
        """)
        
        if preferences.keyboard_navigation:
            css_parts.append("""
            *:focus {
                outline: 3px solid #005fcc !important;
                outline-offset: 2px !important;
            }
            """)
        
        return "\n".join(css_parts)

class AnalyticsManager:
    def __init__(self, config: Dict):
        self.config = config
        self.analytics_enabled = config.get('ux_enhancement', {}).get('analytics', True)
        self.events: List[AnalyticsEvent] = []
        logger.info("Analytics manager initialized")
    
    def track_event(self, user_id: str, event_type: str, page_name: str, 
                   component_id: Optional[str] = None, event_data: Dict[str, Any] = None,
                   device_type: DeviceType = DeviceType.DESKTOP) -> str:
        if not self.analytics_enabled:
            return ""
        
        session_id = f"session-{user_id}-{datetime.now().strftime('%Y%m%d')}"
        
        event = AnalyticsEvent(
            event_id="",
            user_id=user_id,
            event_type=event_type,
            page_name=page_name,
            component_id=component_id,
            event_data=event_data or {},
            timestamp="",
            session_id=session_id,
            device_type=device_type,
            user_agent=event_data.get('user_agent') if event_data else None,
            performance_metrics=event_data.get('performance', {}) if event_data else {}
        )
        
        self.events.append(event)
        logger.debug(f"Tracked event: {event.event_type} on {event.page_name}")
        
        return event.event_id
    
    def get_analytics_dashboard_data(self, time_range: int = 7) -> Dict[str, Any]:
        cutoff_date = datetime.now() - timedelta(days=time_range)
        
        recent_events = [
            e for e in self.events 
            if datetime.fromisoformat(e.timestamp) >= cutoff_date
        ]
        
        total_events = len(recent_events)
        unique_users = len(set(e.user_id for e in recent_events))
        page_views = len([e for e in recent_events if e.event_type == 'page_view'])
        
        page_counts = {}
        for event in recent_events:
            if event.event_type == 'page_view':
                page_counts[event.page_name] = page_counts.get(event.page_name, 0) + 1
        
        popular_pages = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        device_counts = {}
        for event in recent_events:
            device_counts[event.device_type.value] = device_counts.get(event.device_type.value, 0) + 1
        
        return {
            'summary': {
                'total_events': total_events,
                'unique_users': unique_users,
                'page_views': page_views,
                'time_range_days': time_range
            },
            'popular_pages': popular_pages,
            'device_distribution': device_counts
        }

class PatientInterfaceManager:
    def __init__(self, config: Dict):
        self.config = config
        self.patient_interface_enabled = config.get('ux_enhancement', {}).get('patient_interface', True)
        self.simplify_language = config.get('ux_enhancement', {}).get('simplify_language', True)
        logger.info("Patient interface manager initialized")
    
    def get_patient_friendly_interface(self) -> Dict[str, Any]:
        return {
            'language_level': 'simple',
            'medical_terms_explained': True,
            'visual_aids': True,
            'progress_indicators': True,
            'confirmation_steps': True,
            'large_buttons': True,
            'clear_navigation': True,
            'privacy_explanations': True,
            'multilingual_support': True
        }
    
    def simplify_medical_text(self, medical_text: str) -> str:
        if not self.simplify_language:
            return medical_text
        
        substitutions = {
            'adverse event': 'side effect',
            'medication': 'medicine',
            'administration': 'taking',
            'dosage': 'amount',
            'therapeutic': 'treatment',
            'pharmacovigilance': 'drug safety monitoring',
            'concomitant': 'other medicines taken at the same time'
        }
        
        simplified_text = medical_text
        for medical_term, simple_term in substitutions.items():
            simplified_text = simplified_text.replace(medical_term, simple_term)
        
        return simplified_text
    
    def get_patient_explanation(self, process_name: str) -> str:
        explanations = {
            'narrative_generation': """
            We're creating a summary of what happened with your medicine. 
            This helps doctors and researchers understand how medicines affect people 
            and make them safer for everyone.
            """,
            'pii_protection': """
            We protect your personal information by hiding or changing details 
            that could identify you, while keeping the important medical information.
            """,
            'voice_recording': """
            You can tell us what happened in your own words by speaking. 
            This helps us get accurate information about your experience.
            """
        }
        
        return explanations.get(process_name, "This process helps keep medicines safe for everyone.")

def create_ux_enhancement_system(config: Dict) -> Tuple[ResponsiveDesignManager, AccessibilityManager, AnalyticsManager, PatientInterfaceManager]:
    responsive_manager = ResponsiveDesignManager(config)
    accessibility_manager = AccessibilityManager(config)
    analytics_manager = AnalyticsManager(config)
    patient_interface_manager = PatientInterfaceManager(config)
    
    logger.info("UX enhancement system initialized - Phase 3 features active")
    
    return responsive_manager, accessibility_manager, analytics_manager, patient_interface_manager