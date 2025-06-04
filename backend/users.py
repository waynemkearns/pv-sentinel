"""
PV Sentinel - Multi-User Role Support Module
P1 Feature: Enables collaborative workflows with role-based access

This module addresses the gap identified in the Clinical Operations Lead assessment:
- Lacks task queue and user role management
- No multi-user support for collaborative workflows
- Missing case assignment and triage capabilities
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles in PV Sentinel system"""
    DRAFTER = "drafter"          # Can create and draft AE reports
    REVIEWER = "reviewer"        # Can review and approve drafts
    AUDITOR = "auditor"         # Can audit and validate reports
    ADMIN = "admin"             # Full system access
    READONLY = "readonly"       # View-only access

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

@dataclass
class UserPermissions:
    """Detailed permissions for each role"""
    can_create_cases: bool = False
    can_edit_drafts: bool = False
    can_review_cases: bool = False
    can_approve_cases: bool = False
    can_audit_cases: bool = False
    can_export_reports: bool = False
    can_manage_users: bool = False
    can_access_validation: bool = False
    can_lock_prompts: bool = False
    can_qualify_models: bool = False
    
    @classmethod
    def for_role(cls, role: UserRole) -> 'UserPermissions':
        """Create permissions object for a specific role"""
        permissions_map = {
            UserRole.DRAFTER: cls(
                can_create_cases=True,
                can_edit_drafts=True,
                can_export_reports=True
            ),
            UserRole.REVIEWER: cls(
                can_create_cases=True,
                can_edit_drafts=True,
                can_review_cases=True,
                can_approve_cases=True,
                can_export_reports=True
            ),
            UserRole.AUDITOR: cls(
                can_review_cases=True,
                can_audit_cases=True,
                can_export_reports=True,
                can_access_validation=True
            ),
            UserRole.ADMIN: cls(
                can_create_cases=True,
                can_edit_drafts=True,
                can_review_cases=True,
                can_approve_cases=True,
                can_audit_cases=True,
                can_export_reports=True,
                can_manage_users=True,
                can_access_validation=True,
                can_lock_prompts=True,
                can_qualify_models=True
            ),
            UserRole.READONLY: cls()  # All defaults to False
        }
        
        return permissions_map.get(role, cls())

@dataclass
class User:
    """User account information"""
    user_id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    permissions: UserPermissions
    status: UserStatus
    created_date: str
    last_login: Optional[str] = None
    password_hash: Optional[str] = None
    session_timeout: int = 3600  # seconds
    failed_login_attempts: int = 0
    account_locked_until: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.permissions:
            self.permissions = UserPermissions.for_role(self.role)

@dataclass
class UserSession:
    """Active user session"""
    session_id: str
    user_id: str
    username: str
    role: UserRole
    created_at: str
    last_activity: str
    expires_at: str
    ip_address: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if session is still valid"""
        now = datetime.now()
        expires = datetime.fromisoformat(self.expires_at)
        return now < expires
    
    def extend_session(self, timeout_seconds: int = 3600):
        """Extend session expiration"""
        self.last_activity = datetime.now().isoformat()
        self.expires_at = (datetime.now() + timedelta(seconds=timeout_seconds)).isoformat()

class UserManager:
    """
    Manages users, roles, and sessions for PV Sentinel
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.multi_user_enabled = config.get('users', {}).get('multi_user_support', True)
        self.role_based_access = config.get('users', {}).get('role_based_access', True)
        self.session_timeout = config.get('users', {}).get('session_timeout', 3600)
        self.max_failed_attempts = config.get('users', {}).get('max_failed_attempts', 5)
        self.lockout_duration = config.get('users', {}).get('lockout_duration', 1800)  # 30 minutes
        
        # Storage
        self.users_file = 'storage/users.json'
        self.sessions_file = 'storage/sessions.json'
        
        # In-memory storage
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, UserSession] = {}
        
        # Initialize
        self._load_users()
        self._load_sessions()
        
        logger.info(f"User manager initialized - multi-user: {self.multi_user_enabled}")
    
    def create_user(self, username: str, email: str, full_name: str, 
                   role: UserRole, password: str, created_by: str = "system") -> User:
        """
        Create a new user account
        
        Args:
            username: Unique username
            email: User email address
            full_name: User's full name
            role: User role
            password: Plain text password (will be hashed)
            created_by: User ID who created this account
            
        Returns:
            Created User object
        """
        if not self.multi_user_enabled:
            raise ValueError("Multi-user support is disabled")
        
        # Check if username already exists
        if any(user.username == username for user in self.users.values()):
            raise ValueError(f"Username '{username}' already exists")
        
        # Generate user ID
        user_id = self._generate_user_id(username)
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            permissions=UserPermissions.for_role(role),
            status=UserStatus.ACTIVE,
            created_date=datetime.now().isoformat(),
            password_hash=password_hash
        )
        
        # Store user
        self.users[user_id] = user
        self._save_users()
        
        # Log user creation
        logger.info(f"User created: {username} ({role.value}) by {created_by}")
        
        return user
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = None) -> Optional[UserSession]:
        """
        Authenticate user and create session
        
        Args:
            username: Username
            password: Plain text password
            ip_address: Optional IP address for logging
            
        Returns:
            UserSession if authentication successful, None otherwise
        """
        # Find user by username
        user = self._get_user_by_username(username)
        if not user:
            logger.warning(f"Login attempt with unknown username: {username}")
            return None
        
        # Check if account is locked
        if self._is_account_locked(user):
            logger.warning(f"Login attempt on locked account: {username}")
            return None
        
        # Check if account is active
        if user.status != UserStatus.ACTIVE:
            logger.warning(f"Login attempt on inactive account: {username}")
            return None
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            self._handle_failed_login(user)
            logger.warning(f"Failed login attempt for user: {username}")
            return None
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.now().isoformat()
        
        # Create session
        session = self._create_session(user, ip_address)
        
        self._save_users()
        self._save_sessions()
        
        logger.info(f"User authenticated: {username} (session: {session.session_id})")
        return session
    
    def validate_session(self, session_id: str) -> Optional[UserSession]:
        """
        Validate an existing session
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            UserSession if valid, None otherwise
        """
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        if not session.is_valid():
            # Remove expired session
            del self.sessions[session_id]
            self._save_sessions()
            return None
        
        # Extend session on activity
        session.extend_session(self.session_timeout)
        self._save_sessions()
        
        return session
    
    def check_permission(self, session_id: str, permission: str) -> bool:
        """
        Check if user has specific permission
        
        Args:
            session_id: User session ID
            permission: Permission to check (e.g., 'can_create_cases')
            
        Returns:
            True if user has permission, False otherwise
        """
        if not self.role_based_access:
            return True  # All permissions granted if RBAC is disabled
        
        session = self.validate_session(session_id)
        if not session:
            return False
        
        user = self.users.get(session.user_id)
        if not user:
            return False
        
        return getattr(user.permissions, permission, False)
    
    def get_user_by_session(self, session_id: str) -> Optional[User]:
        """Get user object from session ID"""
        session = self.validate_session(session_id)
        if not session:
            return None
        
        return self.users.get(session.user_id)
    
    def logout_user(self, session_id: str) -> bool:
        """
        Logout user and invalidate session
        
        Args:
            session_id: Session ID to invalidate
            
        Returns:
            True if logout successful
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            logger.info(f"User logged out: {session.username}")
            del self.sessions[session_id]
            self._save_sessions()
            return True
        
        return False
    
    def update_user_role(self, user_id: str, new_role: UserRole, 
                        updated_by: str) -> bool:
        """
        Update user role and permissions
        
        Args:
            user_id: User ID to update
            new_role: New role to assign
            updated_by: User ID who made the change
            
        Returns:
            True if update successful
        """
        user = self.users.get(user_id)
        if not user:
            return False
        
        old_role = user.role
        user.role = new_role
        user.permissions = UserPermissions.for_role(new_role)
        
        self._save_users()
        
        logger.info(f"User role updated: {user.username} from {old_role.value} to {new_role.value} by {updated_by}")
        return True
    
    def deactivate_user(self, user_id: str, deactivated_by: str) -> bool:
        """
        Deactivate user account
        
        Args:
            user_id: User ID to deactivate
            deactivated_by: User ID who deactivated the account
            
        Returns:
            True if deactivation successful
        """
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.status = UserStatus.INACTIVE
        
        # Invalidate all sessions for this user
        sessions_to_remove = [sid for sid, session in self.sessions.items() 
                             if session.user_id == user_id]
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        self._save_users()
        self._save_sessions()
        
        logger.info(f"User deactivated: {user.username} by {deactivated_by}")
        return True
    
    def list_users(self, active_only: bool = False) -> List[Dict]:
        """
        List all users (summary information only)
        
        Args:
            active_only: If True, only return active users
            
        Returns:
            List of user summary dictionaries
        """
        users = []
        for user in self.users.values():
            if active_only and user.status != UserStatus.ACTIVE:
                continue
            
            users.append({
                'user_id': user.user_id,
                'username': user.username,
                'full_name': user.full_name,
                'role': user.role.value,
                'status': user.status.value,
                'last_login': user.last_login,
                'created_date': user.created_date
            })
        
        return users
    
    def get_active_sessions(self) -> List[Dict]:
        """Get list of active sessions"""
        active_sessions = []
        now = datetime.now()
        
        for session in self.sessions.values():
            if session.is_valid():
                active_sessions.append({
                    'session_id': session.session_id,
                    'username': session.username,
                    'role': session.role.value,
                    'created_at': session.created_at,
                    'last_activity': session.last_activity,
                    'ip_address': session.ip_address
                })
        
        return active_sessions
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = [sid for sid, session in self.sessions.items() 
                          if not session.is_valid()]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self._save_sessions()
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def _is_account_locked(self, user: User) -> bool:
        """Check if account is locked due to failed attempts"""
        if not user.account_locked_until:
            return False
        
        locked_until = datetime.fromisoformat(user.account_locked_until)
        return datetime.now() < locked_until
    
    def _handle_failed_login(self, user: User):
        """Handle failed login attempt"""
        user.failed_login_attempts += 1
        
        if user.failed_login_attempts >= self.max_failed_attempts:
            # Lock account
            locked_until = datetime.now() + timedelta(seconds=self.lockout_duration)
            user.account_locked_until = locked_until.isoformat()
            logger.warning(f"Account locked due to failed attempts: {user.username}")
        
        self._save_users()
    
    def _create_session(self, user: User, ip_address: str = None) -> UserSession:
        """Create new user session"""
        session_id = self._generate_session_id(user)
        now = datetime.now()
        expires_at = now + timedelta(seconds=self.session_timeout)
        
        session = UserSession(
            session_id=session_id,
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            created_at=now.isoformat(),
            last_activity=now.isoformat(),
            expires_at=expires_at.isoformat(),
            ip_address=ip_address
        )
        
        self.sessions[session_id] = session
        return session
    
    def _generate_user_id(self, username: str) -> str:
        """Generate unique user ID"""
        data = f"{username}-{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_session_id(self, user: User) -> str:
        """Generate unique session ID"""
        data = f"{user.user_id}-{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def _hash_password(self, password: str) -> str:
        """Hash password (simple implementation - use proper hashing in production)"""
        # In production, use bcrypt or similar
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def _load_users(self):
        """Load users from storage"""
        try:
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                for user_id, user_data in data.items():
                    # Convert role and status from strings
                    user_data['role'] = UserRole(user_data['role'])
                    user_data['status'] = UserStatus(user_data['status'])
                    if 'permissions' in user_data:
                        user_data['permissions'] = UserPermissions(**user_data['permissions'])
                    
                    self.users[user_id] = User(**user_data)
        except FileNotFoundError:
            logger.info("No existing users file found - starting with empty user database")
        except Exception as e:
            logger.error(f"Error loading users: {e}")
    
    def _save_users(self):
        """Save users to storage"""
        try:
            # Create directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            
            data = {}
            for user_id, user in self.users.items():
                user_dict = asdict(user)
                user_dict['role'] = user.role.value
                user_dict['status'] = user.status.value
                data[user_id] = user_dict
            
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def _load_sessions(self):
        """Load sessions from storage"""
        try:
            with open(self.sessions_file, 'r') as f:
                data = json.load(f)
                for session_id, session_data in data.items():
                    session_data['role'] = UserRole(session_data['role'])
                    session = UserSession(**session_data)
                    
                    # Only load valid sessions
                    if session.is_valid():
                        self.sessions[session_id] = session
        except FileNotFoundError:
            logger.info("No existing sessions file found - starting with empty sessions")
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
    
    def _save_sessions(self):
        """Save sessions to storage"""
        try:
            # Create directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(self.sessions_file), exist_ok=True)
            
            data = {}
            for session_id, session in self.sessions.items():
                session_dict = asdict(session)
                session_dict['role'] = session.role.value
                data[session_id] = session_dict
            
            with open(self.sessions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")

# Factory function for easy integration
def create_user_manager(config: Dict) -> UserManager:
    """Factory function to create UserManager with config"""
    return UserManager(config) 