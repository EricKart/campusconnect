from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..jobs import notify_team_request, notify_team_request_update
from ..models import Post, ProjectDetails, TeamRequest, User
from ..queue_utils import get_queue
from ..schemas import ProjectCreate, ProjectOut, TeamRequestCreate
from ..security import get_current_user
from .feed import _serialize_post

router = APIRouter(prefix="/projects", tags=["projects"])


def _serialize_project(project: ProjectDetails, current_user: User) -> ProjectOut:
    my_request = project.team_requests.filter_by(requester_id=current_user.id).first()
    return ProjectOut(
        id=project.id,
        post=_serialize_post(project.post, current_user),
        skills_needed=project.skills_needed,
        hackathon_name=project.hackathon_name,
        deadline=project.deadline,
        team_requests=list(project.team_requests) if project.post.author_id == current_user.id else [],
        my_request_status=my_request.status if my_request else None,
    )


@router.get("", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = db.query(ProjectDetails).join(Post).order_by(Post.created_at.desc()).all()
    return [_serialize_project(p, current_user) for p in projects]


@router.post("", response_model=ProjectOut, status_code=201)
def new_project(
    payload: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    post = Post(author_id=current_user.id, body=payload.body, type="project")
    db.add(post)
    db.flush()  # assigns post.id before the related row is created

    details = ProjectDetails(
        post_id=post.id,
        skills_needed=payload.skills_needed,
        hackathon_name=payload.hackathon_name,
        deadline=payload.deadline,
    )
    db.add(details)
    db.commit()
    db.refresh(details)
    return _serialize_project(details, current_user)


@router.post("/{project_id}/join", response_model=ProjectOut)
def request_to_join(
    project_id: int,
    payload: TeamRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(ProjectDetails, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    if project.post.author_id == current_user.id:
        raise HTTPException(400, "You can't request to join your own project.")
    if project.team_requests.filter_by(requester_id=current_user.id).first():
        raise HTTPException(400, "You already requested to join this project.")

    team_request = TeamRequest(project_id=project.id, requester_id=current_user.id, message=payload.message)
    db.add(team_request)
    db.commit()
    get_queue().enqueue(notify_team_request, project.id, current_user.id)

    db.refresh(project)
    return _serialize_project(project, current_user)


@router.post("/requests/{request_id}/{decision}")
def decide_request(
    request_id: int,
    decision: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if decision not in ("accepted", "rejected"):
        raise HTTPException(400, "decision must be 'accepted' or 'rejected'")

    team_request = db.get(TeamRequest, request_id)
    if team_request is None:
        raise HTTPException(404, "Request not found")
    if team_request.project.post.author_id != current_user.id:
        raise HTTPException(403, "Only the project owner can decide this.")

    team_request.status = decision
    db.commit()
    get_queue().enqueue(notify_team_request_update, team_request.id)
    return {"status": decision}
