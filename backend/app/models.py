"""
CampusConnect's data model -- identical 10 tables/relationships as the
architecture overview describes, now as plain SQLAlchemy (no Flask
dependency) so both the FastAPI app and the RQ worker can import it freely.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    department = Column(String(80), nullable=False)
    year = Column(Integer, nullable=False)
    bio = Column(Text, default="")
    skills = Column(String(300), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="author", lazy="dynamic")
    notifications = relationship(
        "Notification", back_populates="user", lazy="dynamic", cascade="all, delete-orphan"
    )


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    tags = Column(String(300), default="")
    type = Column(String(20), default="general")  # "general" or "project"
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", lazy="dynamic", cascade="all, delete-orphan",
        order_by="Comment.created_at",
    )
    likes = relationship("Like", back_populates="post", lazy="dynamic", cascade="all, delete-orphan")
    project_details = relationship(
        "ProjectDetails", back_populates="post", uselist=False, cascade="all, delete-orphan"
    )


class ProjectDetails(Base):
    __tablename__ = "project_details"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, unique=True)
    skills_needed = Column(String(300), default="")
    hackathon_name = Column(String(200), default="")
    deadline = Column(Date, nullable=True)

    post = relationship("Post", back_populates="project_details")
    team_requests = relationship(
        "TeamRequest", back_populates="project", lazy="dynamic", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    author = relationship("User")


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_like_post_user"),)

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="likes")
    user = relationship("User")


class Forum(Base):
    __tablename__ = "forums"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    description = Column(String(300), default="")

    threads = relationship("Thread", back_populates="forum", lazy="dynamic", cascade="all, delete-orphan")


class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True)
    forum_id = Column(Integer, ForeignKey("forums.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    forum = relationship("Forum", back_populates="threads")
    author = relationship("User")
    replies = relationship(
        "ThreadReply", back_populates="thread", lazy="dynamic", cascade="all, delete-orphan",
        order_by="ThreadReply.created_at",
    )


class ThreadReply(Base):
    __tablename__ = "thread_replies"

    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    thread = relationship("Thread", back_populates="replies")
    author = relationship("User")


class TeamRequest(Base):
    __tablename__ = "team_requests"
    __table_args__ = (
        UniqueConstraint("project_id", "requester_id", name="uq_teamreq_project_requester"),
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project_details.id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending / accepted / rejected
    message = Column(String(300), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("ProjectDetails", back_populates="team_requests")
    requester = relationship("User")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(40), nullable=False)
    payload = Column(String(300), default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
