"""
Collaboration Models
Producer + Artist collaboration, stem uploads, versioning, revenue splits
"""

from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text, Enum, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime as dt
from enum import Enum as PyEnum
import uuid

Base = declarative_base()


class CollaborationStatus(str, PyEnum):
    """Collaboration project status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RevenueSplitType(str, PyEnum):
    """Revenue split calculation method"""
    EQUAL = "equal"
    CUSTOM = "custom"
    WEIGHTED = "weighted"


class CollaborationProject(Base):
    """Producer + Artist collaboration project"""
    __tablename__ = "collaboration_projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Participants
    creator_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    # Project details
    genre = Column(String(100))
    status = Column(Enum(CollaborationStatus), default=CollaborationStatus.DRAFT, index=True)
    revenue_split_type = Column(Enum(RevenueSplitType), default=RevenueSplitType.EQUAL)
    custom_split = Column(JSON)  # {user_id: percentage}
    
    # Final output
    final_beat_id = Column(String(36), ForeignKey("beat.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=dt.utcnow, index=True)
    updated_at = Column(DateTime, default=dt.utcnow, onupdate=dt.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    collaborators = relationship("ProjectCollaborator", back_populates="project", cascade="all, delete-orphan")
    stems = relationship("StemFile", back_populates="project", cascade="all, delete-orphan")
    versions = relationship("ProjectVersion", back_populates="project", cascade="all, delete-orphan")


class ProjectCollaborator(Base):
    """Project collaborator with role and permissions"""
    __tablename__ = "project_collaborators"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("collaboration_projects.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    role = Column(String(50))  # "producer", "artist", "engineer", "contributor"
    permissions = Column(JSON)  # Can edit stems, approve versions, claim revenue, etc.
    
    # Revenue split
    revenue_percentage = Column(Float, default=0.0)
    
    # Status
    invited_at = Column(DateTime, default=dt.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=0)  # 0=pending, 1=active, -1=left
    
    # Relationships
    project = relationship("CollaborationProject", back_populates="collaborators")


class StemFile(Base):
    """Individual audio stem file uploaded by collaborator"""
    __tablename__ = "stem_files"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("collaboration_projects.id"), nullable=False, index=True)
    uploaded_by = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    # File details
    name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=True)
    file_size = Column(Integer)  # bytes
    file_type = Column(String(50))  # "drums", "vocals", "bass", "keys", "synth", "other"
    duration = Column(Float)  # seconds
    
    # BPM and key info for alignment
    bpm = Column(Integer, nullable=True)
    key = Column(String(10), nullable=True)
    
    # Version tracking
    version = Column(Integer, default=1)
    previous_version_id = Column(String(36), ForeignKey("stem_files.id"), nullable=True)
    
    created_at = Column(DateTime, default=dt.utcnow, index=True)
    updated_at = Column(DateTime, default=dt.utcnow, onupdate=dt.utcnow)
    
    # Relationships
    project = relationship("CollaborationProject", back_populates="stems")


class ProjectVersion(Base):
    """Snapshot of project at specific stage"""
    __tablename__ = "project_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("collaboration_projects.id"), nullable=False, index=True)
    
    version_number = Column(Integer)
    name = Column(String(255))
    description = Column(Text)
    
    # Mix details
    master_file_url = Column(String(500), nullable=True)
    stem_manifest = Column(JSON)  # List of stem IDs
    
    # Approval workflow
    created_by = Column(String(36), ForeignKey("user.id"), nullable=True)
    approved_by = Column(String(36), ForeignKey("user.id"), nullable=True)
    approval_status = Column(String(50))  # "pending", "approved", "rejected"
    
    feedback = Column(JSON)  # List of feedback entries
    
    created_at = Column(DateTime, default=dt.utcnow, index=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("CollaborationProject", back_populates="versions")
