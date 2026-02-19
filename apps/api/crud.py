from sqlalchemy.orm import Session
import models, schemas, auth

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Professor CRUD (Scoped to User)
def get_professor(db: Session, professor_id: int, user_id: int):
    return db.query(models.Professor).filter(models.Professor.id == professor_id, models.Professor.user_id == user_id).first()

def get_professors(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Professor).filter(models.Professor.user_id == user_id).offset(skip).limit(limit).all()

def create_professor(db: Session, professor: schemas.ProfessorCreate, user_id: int):
    db_professor = models.Professor(**professor.dict(), user_id=user_id)
    db.add(db_professor)
    db.commit()
    db.refresh(db_professor)
    
    # Create default pipeline status
    db_status = models.PipelineStatus(professor_id=db_professor.id)
    db.add(db_status)
    db.commit()
    
    return db_professor

def update_pipeline_status(db: Session, professor_id: int, status_update: schemas.PipelineStatusUpdate, user_id: int):
    # Verify ownership by joining with Professor table
    db_status = db.query(models.PipelineStatus).join(models.Professor).filter(
        models.PipelineStatus.professor_id == professor_id,
        models.Professor.user_id == user_id
    ).first()

    if not db_status:
        return None
    
    update_data = status_update.dict(exclude_unset=True)
    if "status" in update_data:
         # Auto-update last_touch if status changes to Sent/Replied
         if update_data["status"] in ["Sent", "Replied"]:
             from datetime import datetime
             update_data["last_touch_at"] = datetime.utcnow()

    for key, value in update_data.items():
        setattr(db_status, key, value)

    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    db.refresh(db_status)
    return db_status

def update_professor(db: Session, professor_id: int, professor_update: schemas.ProfessorUpdate, user_id: int):
    db_professor = get_professor(db, professor_id, user_id)
    if not db_professor:
        return None
    
    update_data = professor_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_professor, key, value)
    
    db.add(db_professor)
    db.commit()
    db.refresh(db_professor)
    return db_professor

def delete_professor(db: Session, professor_id: int, user_id: int):
    # Get professor first to verify ownership
    db_professor = db.query(models.Professor).filter(models.Professor.id == professor_id, models.Professor.user_id == user_id).first()
    if db_professor:
        db.delete(db_professor)
        db.commit()
    return db_professor
