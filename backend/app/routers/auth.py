from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserLogin, UserOut
from ..security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days, matches jwt_expire_minutes


def _set_auth_cookie(response: Response, user_id: int):
    token = create_access_token(user_id)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,       # never readable from JS -- the whole point of this pattern
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=payload.email.lower()).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "An account with that email already exists.")

    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        department=payload.department,
        year=payload.year,
        bio=payload.bio,
        skills=payload.skills,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _set_auth_cookie(response, user.id)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=payload.email.lower()).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password.")

    _set_auth_cookie(response, user.id)
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
