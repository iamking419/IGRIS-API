from sqlalchemy.orm import Session
from . import models, utils


def create_user(db: Session, user):
    hashed = utils.hash_password(user.password)

    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        return None

    if not utils.verify_password(password, user.hashed_password):
        return None

    return user