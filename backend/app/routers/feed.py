from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..jobs import notify_new_comment, notify_new_like
from ..models import Comment, Like, Post, User
from ..queue_utils import get_queue
from ..schemas import CommentCreate, PostCreate, PostOut
from ..security import get_current_user

router = APIRouter(prefix="/posts", tags=["feed"])


def _serialize_post(post: Post, current_user: User) -> PostOut:
    liked = post.likes.filter_by(user_id=current_user.id).first() is not None
    return PostOut(
        id=post.id,
        body=post.body,
        tags=post.tags,
        type=post.type,
        created_at=post.created_at,
        author=post.author,
        like_count=post.likes.count(),
        comment_count=post.comments.count(),
        liked_by_me=liked,
        comments=list(post.comments),
    )


@router.get("", response_model=List[PostOut])
def list_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    posts = (
        db.query(Post).filter_by(type="general").order_by(Post.created_at.desc()).limit(50).all()
    )
    return [_serialize_post(p, current_user) for p in posts]


@router.post("", response_model=PostOut, status_code=201)
def create_post(
    payload: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    post = Post(author_id=current_user.id, body=payload.body, tags=payload.tags, type="general")
    db.add(post)
    db.commit()
    db.refresh(post)
    return _serialize_post(post, current_user)


@router.post("/{post_id}/comments", response_model=PostOut)
def add_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "Post not found")

    comment = Comment(post_id=post.id, author_id=current_user.id, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Fire-and-forget: this response returns before the job below is processed.
    get_queue().enqueue(notify_new_comment, post.id, current_user.id, comment.id)

    db.refresh(post)
    return _serialize_post(post, current_user)


@router.post("/{post_id}/like", response_model=PostOut)
def toggle_like(
    post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "Post not found")

    existing = post.likes.filter_by(user_id=current_user.id).first()
    if existing:
        db.delete(existing)
        db.commit()
    else:
        db.add(Like(post_id=post.id, user_id=current_user.id))
        db.commit()
        get_queue().enqueue(notify_new_like, post.id, current_user.id)

    db.refresh(post)
    return _serialize_post(post, current_user)
