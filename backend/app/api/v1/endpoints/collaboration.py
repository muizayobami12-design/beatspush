"""
Collaboration API Endpoints
Producer + Artist collaboration, stem uploads, versioning, revenue splits
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.dependencies import get_current_user, get_db
from app.services.collaboration_service import CollaborationService

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])

collab_service = CollaborationService()


# ============ PYDANTIC MODELS ============

class CreateProjectRequest(BaseModel):
    project_name: str
    genre: str
    description: str


class InviteCollaboratorRequest(BaseModel):
    user_id: str
    role: str  # "producer", "artist", "engineer", "contributor"
    revenue_percentage: float


class UploadStemRequest(BaseModel):
    name: str
    type: str  # "drums", "vocals", "bass", "keys", "synth", "other"
    file_url: str
    file_size: int
    duration: float
    bpm: int = None
    key: str = None


class CreateVersionRequest(BaseModel):
    version_name: str
    master_file_url: str
    stem_ids: List[str]


# ============ PROJECT MANAGEMENT ============

@router.post("/projects")
async def create_project(
    request: CreateProjectRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create new collaboration project
    - project_name: Name of the project
    - genre: Music genre
    - description: Project description
    """
    result = await collab_service.create_project(
        current_user.id,
        request.project_name,
        request.genre,
        request.description,
        db,
    )
    return result


@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get project details with collaborators, stems, and versions"""
    result = await collab_service.get_project_details(project_id, db)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/projects/{project_id}/invite")
async def invite_collaborator(
    project_id: str,
    request: InviteCollaboratorRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Invite user to collaborate on project
    - user_id: User to invite
    - role: Collaborator role
    - revenue_percentage: Their share of revenue
    """
    result = await collab_service.invite_collaborator(
        project_id,
        request.user_id,
        request.role,
        request.revenue_percentage,
        db,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/projects/{project_id}/accept")
async def accept_collaboration(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept collaboration invitation"""
    result = await collab_service.accept_invitation(project_id, current_user.id, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============ STEM MANAGEMENT ============

@router.post("/projects/{project_id}/stems")
async def upload_stem(
    project_id: str,
    request: UploadStemRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload audio stem to collaboration project
    - name: Stem file name
    - type: Stem type (drums, vocals, bass, keys, synth, other)
    - file_url: URL of uploaded file
    - bpm: BPM of stem (optional, for synchronization)
    - key: Musical key (optional, e.g., "C Major")
    """
    stem_data = {
        "name": request.name,
        "type": request.type,
        "file_url": request.file_url,
        "file_size": request.file_size,
        "duration": request.duration,
        "bpm": request.bpm,
        "key": request.key,
    }

    result = await collab_service.upload_stem(project_id, current_user.id, stem_data, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/projects/{project_id}/stems")
async def get_stems(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all current stems for project"""
    stems = await collab_service.get_project_stems(project_id, db)
    return {"stems": stems}


# ============ VERSION MANAGEMENT ============

@router.post("/projects/{project_id}/versions")
async def create_version(
    project_id: str,
    request: CreateVersionRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create project version (milestone/snapshot)
    - version_name: Name of this version (e.g., "First Draft")
    - master_file_url: URL of mixed/combined audio
    - stem_ids: List of stem IDs used in this version
    """
    result = await collab_service.create_version(
        project_id,
        request.version_name,
        request.master_file_url,
        request.stem_ids,
        current_user.id,
        db,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/versions/{version_id}/approve")
async def approve_version(
    version_id: str,
    feedback: str = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Approve project version
    - feedback: Optional feedback on the version
    """
    result = await collab_service.approve_version(version_id, current_user.id, feedback, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ============ REVENUE SPLIT ============

@router.get("/projects/{project_id}/revenue-split")
async def get_revenue_split(
    project_id: str,
    total_revenue: float,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Calculate how revenue will be split among collaborators
    - total_revenue: Total amount to split
    - Returns: Amount each collaborator receives
    """
    splits = await collab_service.calculate_revenue_split(project_id, total_revenue, db)
    return {
        "project_id": project_id,
        "total_revenue": total_revenue,
        "splits": splits,
    }
