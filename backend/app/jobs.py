"""
RQ job functions -- run inside worker/run_worker.py, a separate process from
the API. Each job opens and closes its own short-lived DB session (there's no
FastAPI request/dependency-injection here to hand one to us), and every
function follows the same "notify the OTHER person, never yourself" rule.
"""
from .database import SessionLocal
from .models import Comment, Notification, Post, ProjectDetails, TeamRequest, User


def notify_new_comment(post_id: int, commenter_id: int, comment_id: int):
    db = SessionLocal()
    try:
        post = db.get(Post, post_id)
        comment = db.get(Comment, comment_id)
        commenter = db.get(User, commenter_id)
        if not post or not comment or not commenter or post.author_id == commenter_id:
            return
        db.add(Notification(
            user_id=post.author_id,
            type="comment",
            payload=f'{commenter.name} commented on your post: "{comment.body[:80]}"',
        ))
        db.commit()
    finally:
        db.close()


def notify_new_like(post_id: int, liker_id: int):
    db = SessionLocal()
    try:
        post = db.get(Post, post_id)
        liker = db.get(User, liker_id)
        if not post or not liker or post.author_id == liker_id:
            return
        db.add(Notification(user_id=post.author_id, type="like", payload=f"{liker.name} liked your post."))
        db.commit()
    finally:
        db.close()


def notify_team_request(project_id: int, requester_id: int):
    db = SessionLocal()
    try:
        project = db.get(ProjectDetails, project_id)
        requester = db.get(User, requester_id)
        if not project or not requester:
            return
        db.add(Notification(
            user_id=project.post.author_id,
            type="team_request",
            payload=f'{requester.name} wants to join "{project.post.body[:60]}"',
        ))
        db.commit()
    finally:
        db.close()


def notify_team_request_update(team_request_id: int):
    db = SessionLocal()
    try:
        tr = db.get(TeamRequest, team_request_id)
        if not tr:
            return
        db.add(Notification(
            user_id=tr.requester_id,
            type="team_request_update",
            payload=f'Your request to join "{tr.project.post.body[:60]}" was {tr.status}.',
        ))
        db.commit()
    finally:
        db.close()
