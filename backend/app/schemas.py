"""
Pydantic schemas -- the contract between the API and any client (the Next.js
frontend, curl, a future mobile app). FastAPI uses these to validate every
request body AND to shape every JSON response, and generates OpenAPI docs
from them for free at /docs.
"""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    department: str
    year: int = Field(ge=1, le=4)
    bio: str = ""
    skills: str = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    year: int
    bio: str
    skills: str

    class Config:
        from_attributes = True


class CommentOut(BaseModel):
    id: int
    body: str
    created_at: datetime
    author: UserOut

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)


class PostCreate(BaseModel):
    body: str = Field(min_length=1)
    tags: str = ""


class PostOut(BaseModel):
    id: int
    body: str
    tags: str
    type: str
    created_at: datetime
    author: UserOut
    like_count: int
    comment_count: int
    liked_by_me: bool
    comments: List[CommentOut] = []

    class Config:
        from_attributes = True


class ForumOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    thread_count: int

    class Config:
        from_attributes = True


class ThreadCreate(BaseModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)


class ThreadReplyCreate(BaseModel):
    body: str = Field(min_length=1)


class ThreadReplyOut(BaseModel):
    id: int
    body: str
    created_at: datetime
    author: UserOut

    class Config:
        from_attributes = True


class ThreadOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    author: UserOut
    reply_count: int

    class Config:
        from_attributes = True


class ThreadDetailOut(ThreadOut):
    replies: List[ThreadReplyOut] = []


class ProjectCreate(BaseModel):
    body: str = Field(min_length=1)
    skills_needed: str = ""
    hackathon_name: str = ""
    deadline: Optional[date] = None


class TeamRequestCreate(BaseModel):
    message: str = ""


class TeamRequestOut(BaseModel):
    id: int
    status: str
    message: str
    requester: UserOut

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    id: int
    post: PostOut
    skills_needed: str
    hackathon_name: str
    deadline: Optional[date]
    team_requests: List[TeamRequestOut] = []
    my_request_status: Optional[str] = None

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    type: str
    payload: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
