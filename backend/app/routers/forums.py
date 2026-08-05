from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Forum, Thread, ThreadReply, User
from ..schemas import ForumOut, ThreadCreate, ThreadDetailOut, ThreadOut, ThreadReplyCreate
from ..security import get_current_user

router = APIRouter(prefix="/forums", tags=["forums"])


def _serialize_forum(forum: Forum) -> ForumOut:
    return ForumOut(
        id=forum.id, name=forum.name, slug=forum.slug, description=forum.description,
        thread_count=forum.threads.count(),
    )


def _serialize_thread(thread: Thread) -> ThreadOut:
    return ThreadOut(
        id=thread.id, title=thread.title, body=thread.body, created_at=thread.created_at,
        author=thread.author, reply_count=thread.replies.count(),
    )


def _serialize_thread_detail(thread: Thread) -> ThreadDetailOut:
    replies = thread.replies.order_by(ThreadReply.created_at.asc()).all()
    return ThreadDetailOut(
        id=thread.id, title=thread.title, body=thread.body, created_at=thread.created_at,
        author=thread.author, reply_count=len(replies), replies=replies,
    )


@router.get("", response_model=List[ForumOut])
def list_forums(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    forums = db.query(Forum).order_by(Forum.name).all()
    return [_serialize_forum(f) for f in forums]


@router.get("/{slug}", response_model=List[ThreadOut])
def forum_threads(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    forum = db.query(Forum).filter_by(slug=slug).first()
    if forum is None:
        raise HTTPException(404, "Forum not found")
    threads = forum.threads.order_by(Thread.created_at.desc()).all()
    return [_serialize_thread(t) for t in threads]


@router.post("/{slug}", response_model=ThreadOut, status_code=201)
def new_thread(
    slug: str,
    payload: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    forum = db.query(Forum).filter_by(slug=slug).first()
    if forum is None:
        raise HTTPException(404, "Forum not found")
    thread = Thread(forum_id=forum.id, author_id=current_user.id, title=payload.title, body=payload.body)
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return _serialize_thread(thread)


@router.get("/thread/{thread_id}", response_model=ThreadDetailOut)
def thread_detail(thread_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    thread = db.get(Thread, thread_id)
    if thread is None:
        raise HTTPException(404, "Thread not found")
    return _serialize_thread_detail(thread)


@router.post("/thread/{thread_id}/replies", response_model=ThreadDetailOut)
def reply_thread(
    thread_id: int,
    payload: ThreadReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = db.get(Thread, thread_id)
    if thread is None:
        raise HTTPException(404, "Thread not found")
    db.add(ThreadReply(thread_id=thread.id, author_id=current_user.id, body=payload.body))
    db.commit()
    db.refresh(thread)
    return _serialize_thread_detail(thread)
