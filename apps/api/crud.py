from sqlalchemy.orm import Session
import models, schemas

def get_professor(db: Session, professor_id: int):
    return db.query(models.Professor).filter(models.Professor.id == professor_id).first()

def get_professors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Professor).offset(skip).limit(limit).all()

def create_professor(db: Session, professor: schemas.ProfessorCreate):
    db_professor = models.Professor(**professor.dict())
    db.add(db_professor)
    db.commit()
    db.refresh(db_professor)
    
    # Create default pipeline status
    db_status = models.PipelineStatus(professor_id=db_professor.id)
    db.add(db_status)
    db.commit()
    
    return db_professor

def update_pipeline_status(db: Session, professor_id: int, status_update: schemas.PipelineStatusUpdate):
    db_status = db.query(models.PipelineStatus).filter(models.PipelineStatus.professor_id == professor_id).first()
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
    return db_status
