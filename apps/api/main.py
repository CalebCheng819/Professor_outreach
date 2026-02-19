from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from ingest import fetcher, cleaner, extractor
from emails import generator

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/professors/", response_model=schemas.Professor)
def create_professor(professor: schemas.ProfessorCreate, db: Session = Depends(get_db)):
    return crud.create_professor(db=db, professor=professor)

@app.get("/professors/", response_model=List[schemas.Professor])
def read_professors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    professors = crud.get_professors(db, skip=skip, limit=limit)
    return professors

@app.get("/professors/{professor_id}", response_model=schemas.Professor)
def read_professor(professor_id: int, db: Session = Depends(get_db)):
    db_professor = crud.get_professor(db, professor_id=professor_id)
    if db_professor is None:
        raise HTTPException(status_code=404, detail="Professor not found")
    return db_professor

@app.post("/ingest", response_model=schemas.SourcePage)
def ingest_professor_page(request: schemas.IngestRequest, db: Session = Depends(get_db)):
    # Check if professor exists
    db_professor = crud.get_professor(db, professor_id=request.professor_id)
    if not db_professor:
        raise HTTPException(status_code=404, detail="Professor not found")

    # Fetch URL
    fetched_data = fetcher.fetch_url(request.url)
    
    # Clean HTML
    raw_text = ""
    if fetched_data["raw_html"]:
        raw_text = cleaner.clean_html(fetched_data["raw_html"])

    # Save to DB
    db_source_page = models.SourcePage(
        professor_id=request.professor_id,
        source_url=fetched_data["source_url"],
        raw_html=fetched_data["raw_html"],
        raw_text=raw_text,
        fetch_status=fetched_data["fetch_status"],
        error_msg=fetched_data["error_msg"]
    )
    db.add(db_source_page)
    db.commit()
    db.refresh(db_source_page)
    return db_source_page

@app.post("/professors/{professor_id}/generate-card", response_model=schemas.ProfessorCard)
def generate_professor_card(professor_id: int, db: Session = Depends(get_db)):
    # 1. Get professor and latest source page
    db_professor = crud.get_professor(db, professor_id=professor_id)
    if not db_professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    
    # Get the most recent source page with text
    source_page = db.query(models.SourcePage).filter(
        models.SourcePage.professor_id == professor_id,
        models.SourcePage.raw_text != None
    ).order_by(models.SourcePage.fetched_at.desc()).first()

    if not source_page:
        raise HTTPException(status_code=400, detail="No source text available. Please ingest URL first.")

    # 2. Extract Data
    import json
    card_data = extractor.extract_professor_card(source_page.raw_text)
    
    # 3. Save to DB
    db_card = models.ProfessorCard(
        professor_id=professor_id,
        card_json=json.dumps(card_data),
        card_md=f"## Summary\n{card_data['summary']}\n\n## Interests\n" + "\n".join(f"- {i}" for i in card_data['research_interests']),
        version=1
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card

@app.post("/professors/{professor_id}/generate-email", response_model=schemas.EmailDraft)
def generate_email_draft(professor_id: int, template: str = "summer_intern", db: Session = Depends(get_db)):
    # 1. Get professor
    db_professor = crud.get_professor(db, professor_id=professor_id)
    if not db_professor:
        raise HTTPException(status_code=404, detail="Professor not found")
        
    # 2. Get latest card (for interests)
    latest_card = db.query(models.ProfessorCard).filter(
        models.ProfessorCard.professor_id == professor_id
    ).order_by(models.ProfessorCard.generated_at.desc()).first()
    
    import json
    card_data = {}
    if latest_card:
        card_data = json.loads(latest_card.card_json)
        
    # 3. Generate
    email_content = generator.generate_email(db_professor, card_data, template)
    
    # 4. Save
    db_draft = models.EmailDraft(
        professor_id=professor_id,
        type=template,
        tone="formal",
        content_short=email_content["subject"], # schema mismatch workaround? No, model has content_short/long. 
        # Wait, model says content_short/long. Schema says subject/body.
        # Let's check models.py: content_short = Column(Text), content_long = Column(Text)
        # We should map subject -> content_short, body -> content_long ? 
        # Or I should have defined subject/body on model? 
        # Let's use content_short for subject, content_long for body for now to match Schema mapping or update Schema.
        # I'll update schema mapping in a bit, for now let's construct object.
        content_long=email_content["body"]
    )
    # Actually wait. Schema EmailDraftBase says subject/body. Model EmailDraft says content_short/long.
    # I need to make sure schema matches model or I do conversion.
    # Let's fix models.py or schema? 
    # I'll Fix Schema to match Model? Or Model to match Schema?
    # ProfessorCard used card_json/card_md. EmailDraft uses content_short/long.
    # I will implicitly map subject->content_short, body->content_long in the response.
    # No, that's messy. I'll just save it as proper fields.
    # Let's look at models.py again.
    
    db_draft.content_short = email_content["subject"] 
    db_draft.content_long = email_content["body"]
    
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    
    # Return matched schema
    return schemas.EmailDraft(
        id=db_draft.id,
        professor_id=db_draft.professor_id,
        created_at=db_draft.created_at,
        type=db_draft.type,
        subject=db_draft.content_short,
        body=db_draft.content_long
    )

@app.patch("/professors/{professor_id}/status", response_model=schemas.PipelineStatus)
def update_status(professor_id: int, status_update: schemas.PipelineStatusUpdate, db: Session = Depends(get_db)):
    db_status = crud.update_pipeline_status(db, professor_id=professor_id, status_update=status_update)
    if not db_status:
        raise HTTPException(status_code=404, detail="Professor not found")
    return db_status

@app.get("/search_professors", response_model=List[schemas.SearchResult])
def search_professors(query: str):
    from search import engine
    return engine.search_professor(query)
