"""
Collaboration Service
Producer + Artist joint projects, stem uploads, versioning, revenue split
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text, Enum, DateTime, JSON
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
import json
import uuid
from enum import Enum as PyEnum

Base = declarative_base()


class CollaborationStatus(PyEnum):
    """Collaboration project status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class RevenueSplitType(PyEnum):
    """Revenue split calculation method"""
    EQUAL = "equal"
    CUSTOM = "custom"
    WEIGHTED = "weighted"


# ============ DATABASE MODELS ============

class CollaborationProject(Base):
    """Producer + Artist collaboration project"""
    __tablename__ = "collaboration_projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Participants
    creator_id = Column(String, ForeignKey("user.id"), nullable=False)  # Producer
    collaborators = relationship("ProjectCollaborator", back_populates="project")
    
    # Project details
    genre = Column(String(100))
    status = Column(Enum(CollaborationStatus), default=CollaborationStatus.DRAFT)
    revenue_split_type = Column(Enum(RevenueSplitType), default=RevenueSplitType.EQUAL)
    custom_split = Column(JSON)  # {user_id: percentage}
    
    # Files
    stems = relationship("StemFile", back_populates="project")
    versions = relationship("ProjectVersion", back_populates="project")
    final_beat_id = Column(String, ForeignKey("beat.id"))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)


class ProjectCollaborator(Base):
    """Project collaborator with role and permissions"""
    __tablename__ = "project_collaborators"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("collaboration_projects.id"), nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    
    role = Column(String(50))  # "producer", "artist", "engineer", "contributor"
    permissions = Column(JSON)  # Can edit stems, approve versions, claim revenue, etc.
    
    # Revenue split
    revenue_percentage = Column(Float, default=0.0)  # e.g., 33.33 for 3-way split
    
    # Status
    invited_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime)
    is_active = Column(Integer, default=0)  # 0=pending, 1=active, -1=left
    
    project = relationship("CollaborationProject", back_populates="collaborators")


class StemFile(Base):
    """Individual audio stem file uploaded by collaborator"""
    __tablename__ = "stem_files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("collaboration_projects.id"), nullable=False)
    uploaded_by = Column(String, ForeignKey("user.id"), nullable=False)
    
    # File details
    name = Column(String(255), nullable=False)  # e.g., "drums.wav", "vocals.mp3"
    file_url = Column(String(500))
    file_size = Column(Integer)  # bytes
    file_type = Column(String(50))  # "drums", "vocals", "bass", "keys", "synth", "other"
    duration = Column(Float)  # seconds
    
    # BPM and key info for alignment
    bpm = Column(Integer)
    key = Column(String(10))  # C Major, Am, etc.
    
    # Version tracking
    version = Column(Integer, default=1)
    previous_version_id = Column(String, ForeignKey("stem_files.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("CollaborationProject", back_populates="stems")


class ProjectVersion(Base):
    """Snapshot of project at specific stage (for A/B testing, milestones)"""
    __tablename__ = "project_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("collaboration_projects.id"), nullable=False)
    
    version_number = Column(Integer)  # 1, 2, 3...
    name = Column(String(255))  # e.g., "First Draft", "Feedback Round 2"
    description = Column(Text)
    
    # Mix details
    master_file_url = Column(String(500))  # Combined/mixed version
    stem_manifest = Column(JSON)  # List of stem IDs used in this version
    
    # Approval workflow
    created_by = Column(String, ForeignKey("user.id"))
    approved_by = Column(String, ForeignKey("user.id"))
    approval_status = Column(String(50))  # "pending", "approved", "rejected"
    
    feedback = Column(JSON)  # [{from_user, text, timestamp}]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    
    project = relationship("CollaborationProject", back_populates="versions")


# ============ COLLABORATION SERVICE ============

class CollaborationService:
    """Manage artist collaborations and revenue splits"""

    def __init__(self):
        pass

    # ============ PROJECT MANAGEMENT ============

    async def create_project(
        self,
        creator_id: str,
        project_name: str,
        genre: str,
        description: str,
        db: Session,
    ) -> Dict:
        """Create new collaboration project"""

        project = CollaborationProject(
            project_name=project_name,
            creator_id=creator_id,
            genre=genre,
            description=description,
            status=CollaborationStatus.DRAFT,
        )

        # Add creator as first collaborator
        creator_collab = ProjectCollaborator(
            project_id=project.id,
            user_id=creator_id,
            role="producer",
            permissions={
                "edit_stems": True,
                "approve_versions": True,
                "manage_collaborators": True,
                "claim_revenue": True,
            },
            revenue_percentage=100.0,
            is_active=1,
            accepted_at=datetime.utcnow(),
        )

        db.add(project)
        db.add(creator_collab)
        db.commit()

        return {
            "id": project.id,
            "name": project_name,
            "status": project.status.value,
            "created_at": project.created_at.isoformat(),
        }

    async def invite_collaborator(
        self,
        project_id: str,
        user_id: str,
        role: str,
        revenue_percentage: float,
        db: Session,
    ) -> Dict:
        """Invite user to collaborate on project"""

        project = db.query(CollaborationProject).filter_by(id=project_id).first()
        if not project:
            return {"error": "Project not found"}

        collaborator = ProjectCollaborator(
            project_id=project_id,
            user_id=user_id,
            role=role,
            revenue_percentage=revenue_percentage,
            permissions={
                "edit_stems": role in ["artist", "engineer"],
                "approve_versions": role == "producer",
                "claim_revenue": True,
            },
            is_active=0,  # Pending acceptance
        )

        db.add(collaborator)
        db.commit()

        return {
            "status": "invitation_sent",
            "project_id": project_id,
            "user_id": user_id,
            "role": role,
        }

    async def accept_invitation(
        self,
        project_id: str,
        user_id: str,
        db: Session,
    ) -> Dict:
        """Accept collaboration invitation"""

        collab = db.query(ProjectCollaborator).filter(
            ProjectCollaborator.project_id == project_id,
            ProjectCollaborator.user_id == user_id,
        ).first()

        if not collab:
            return {"error": "Invitation not found"}

        collab.is_active = 1
        collab.accepted_at = datetime.utcnow()

        # If all collaborators accepted, move to ACTIVE
        project = db.query(CollaborationProject).filter_by(id=project_id).first()
        all_accepted = all(c.is_active == 1 for c in project.collaborators)
        if all_accepted and project.status == CollaborationStatus.PENDING_APPROVAL:
            project.status = CollaborationStatus.ACTIVE

        db.commit()

        return {
            "status": "invitation_accepted",
            "project_id": project_id,
            "is_active": True,
        }

    # ============ STEM MANAGEMENT ============

    async def upload_stem(
        self,
        project_id: str,
        user_id: str,
        stem_data: Dict,
        db: Session,
    ) -> Dict:
        """Upload audio stem to collaboration project"""

        project = db.query(CollaborationProject).filter_by(id=project_id).first()
        if not project:
            return {"error": "Project not found"}

        # Get latest version for this stem type
        latest_stem = db.query(StemFile).filter(
            StemFile.project_id == project_id,
            StemFile.file_type == stem_data["type"],
        ).order_by(StemFile.version.desc()).first()

        version = (latest_stem.version + 1) if latest_stem else 1

        stem = StemFile(
            project_id=project_id,
            uploaded_by=user_id,
            name=stem_data["name"],
            file_url=stem_data["file_url"],
            file_size=stem_data.get("file_size", 0),
            file_type=stem_data["type"],
            duration=stem_data.get("duration", 0),
            bpm=stem_data.get("bpm"),
            key=stem_data.get("key"),
            version=version,
            previous_version_id=latest_stem.id if latest_stem else None,
        )

        db.add(stem)
        db.commit()

        return {
            "stem_id": stem.id,
            "type": stem.file_type,
            "version": stem.version,
            "name": stem.name,
            "uploaded_at": stem.created_at.isoformat(),
        }

    async def get_project_stems(
        self,
        project_id: str,
        db: Session,
    ) -> List[Dict]:
        """Get all current stems for a project"""

        # Get latest version of each stem type
        stems = db.query(StemFile).filter(
            StemFile.project_id == project_id,
        ).order_by(
            StemFile.file_type,
            StemFile.version.desc(),
        ).all()

        # Group by type and take latest version
        latest_stems = {}
        for stem in stems:
            if stem.file_type not in latest_stems:
                latest_stems[stem.file_type] = stem

        return [
            {
                "id": stem.id,
                "name": stem.name,
                "type": stem.file_type,
                "version": stem.version,
                "duration": stem.duration,
                "bpm": stem.bpm,
                "key": stem.key,
                "uploaded_by": stem.uploaded_by,
                "uploaded_at": stem.created_at.isoformat(),
                "file_url": stem.file_url,
            }
            for stem in latest_stems.values()
        ]

    # ============ VERSION MANAGEMENT ============

    async def create_version(
        self,
        project_id: str,
        version_name: str,
        master_file_url: str,
        stem_ids: List[str],
        created_by: str,
        db: Session,
    ) -> Dict:
        """Create project version (milestone/snapshot)"""

        project = db.query(CollaborationProject).filter_by(id=project_id).first()
        if not project:
            return {"error": "Project not found"}

        # Get next version number
        latest_version = db.query(ProjectVersion).filter(
            ProjectVersion.project_id == project_id,
        ).order_by(ProjectVersion.version_number.desc()).first()

        next_version = (latest_version.version_number + 1) if latest_version else 1

        version = ProjectVersion(
            project_id=project_id,
            version_number=next_version,
            name=version_name,
            master_file_url=master_file_url,
            stem_manifest=stem_ids,
            created_by=created_by,
            approval_status="pending",
        )

        db.add(version)
        db.commit()

        return {
            "version_id": version.id,
            "version_number": version.version_number,
            "name": version_name,
            "status": "pending_approval",
            "created_at": version.created_at.isoformat(),
        }

    async def approve_version(
        self,
        version_id: str,
        approved_by: str,
        feedback: Optional[str] = None,
        db: Session = None,
    ) -> Dict:
        """Approve project version"""

        version = db.query(ProjectVersion).filter_by(id=version_id).first()
        if not version:
            return {"error": "Version not found"}

        version.approval_status = "approved"
        version.approved_by = approved_by
        version.approved_at = datetime.utcnow()

        if feedback:
            version.feedback = version.feedback or []
            version.feedback.append({
                "from_user": approved_by,
                "text": feedback,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "approval",
            })

        db.commit()

        return {
            "version_id": version.id,
            "status": "approved",
            "approved_at": version.approved_at.isoformat(),
        }

    # ============ REVENUE SPLIT ============

    async def calculate_revenue_split(
        self,
        project_id: str,
        total_revenue: float,
        db: Session,
    ) -> Dict[str, float]:
        """Calculate revenue split among collaborators"""

        project = db.query(CollaborationProject).filter_by(id=project_id).first()
        if not project:
            return {}

        splits = {}

        if project.revenue_split_type == RevenueSplitType.EQUAL:
            # Equal split among active collaborators
            active_collabs = [c for c in project.collaborators if c.is_active == 1]
            per_person = total_revenue / len(active_collabs) if active_collabs else 0

            for collab in active_collabs:
                splits[collab.user_id] = per_person

        elif project.revenue_split_type == RevenueSplitType.CUSTOM:
            # Use custom split percentages
            for collab in project.collaborators:
                if collab.is_active == 1:
                    splits[collab.user_id] = total_revenue * (collab.revenue_percentage / 100)

        elif project.revenue_split_type == RevenueSplitType.WEIGHTED:
            # Weight by contribution metrics (stems uploaded, versions approved, etc.)
            total_weight = sum(len(c.project.stems) for c in project.collaborators if c.is_active == 1)

            for collab in project.collaborators:
                if collab.is_active == 1:
                    weight = len([s for s in project.stems if s.uploaded_by == collab.user_id])
                    splits[collab.user_id] = total_revenue * (weight / max(total_weight, 1))

        return splits

    async def get_project_details(
        self,
        project_id: str,
        db: Session,
    ) -> Dict:
        """Get complete project details with all collaborators and stems"""

        project = db.query(CollaborationProject).filter_by(id=project_id).first()
        if not project:
            return {"error": "Project not found"}

        collaborators = [
            {
                "user_id": c.user_id,
                "role": c.role,
                "revenue_percentage": c.revenue_percentage,
                "status": "active" if c.is_active == 1 else "pending" if c.is_active == 0 else "left",
                "accepted_at": c.accepted_at.isoformat() if c.accepted_at else None,
            }
            for c in project.collaborators
        ]

        stems = await self.get_project_stems(project_id, db)

        versions = [
            {
                "version_id": v.id,
                "version_number": v.version_number,
                "name": v.name,
                "status": v.approval_status,
                "created_at": v.created_at.isoformat(),
                "approved_at": v.approved_at.isoformat() if v.approved_at else None,
            }
            for v in db.query(ProjectVersion).filter_by(project_id=project_id).all()
        ]

        return {
            "project_id": project.id,
            "name": project.project_name,
            "description": project.description,
            "genre": project.genre,
            "status": project.status.value,
            "revenue_split_type": project.revenue_split_type.value,
            "collaborators": collaborators,
            "stems": stems,
            "versions": versions,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }
