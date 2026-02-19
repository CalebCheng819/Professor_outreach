from dotenv import load_dotenv
load_dotenv()  # Must be FIRST - loads .env before any module reads os.getenv()

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from jose import JWTError, jwt
import crud, models, schemas, auth
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from ingest import fetcher, cleaner, extractor
from emails import generator

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://professor-outreach-tau.vercel.app",
        "https://professor-outreach-tau.vercel.app/"
    ],
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

async def get_current_active_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/professors/", response_model=schemas.Professor)
def create_professor(professor: schemas.ProfessorCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.create_professor(db=db, professor=professor, user_id=current_user.id)

@app.get("/professors/", response_model=List[schemas.Professor])
def read_professors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    professors = crud.get_professors(db, user_id=current_user.id, skip=skip, limit=limit)
    return professors

@app.get("/professors/{professor_id}", response_model=schemas.Professor)
def read_professor(professor_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    db_professor = crud.get_professor(db, professor_id=professor_id, user_id=current_user.id)
    if db_professor is None:
        raise HTTPException(status_code=404, detail="Professor not found")
    if db_professor is None:
        raise HTTPException(status_code=404, detail="Professor not found")
    return db_professor

@app.patch("/professors/{professor_id}", response_model=schemas.Professor)
def update_professor(professor_id: int, professor_update: schemas.ProfessorUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    db_professor = crud.update_professor(db, professor_id=professor_id, professor_update=professor_update, user_id=current_user.id)
    if db_professor is None:
        raise HTTPException(status_code=404, detail="Professor not found")
    return db_professor

@app.delete("/professors/{professor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professor(professor_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    db_professor = crud.delete_professor(db, professor_id=professor_id, user_id=current_user.id)
    if db_professor is None:
        raise HTTPException(status_code=404, detail="Professor not found")
    return None

@app.post("/ingest", response_model=schemas.SourcePage)
def ingest_professor_page(request: schemas.IngestRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    # Check if professor exists (and belongs to user)
    db_professor = crud.get_professor(db, professor_id=request.professor_id, user_id=current_user.id)
    if not db_professor:
        raise HTTPException(status_code=404, detail="Professor not found")

    # Fetch URL
    fetched_data = fetcher.fetch_url(request.url)
    
    # Clean HTML
    raw_text = ""
    avatar_url = None
    if fetched_data["raw_html"]:
        raw_text = cleaner.clean_html(fetched_data["raw_html"])
        avatar_url = cleaner.extract_images(fetched_data["raw_html"], fetched_data["source_url"])

    # Update Professor avatar if not already set (or always?)
    # Let's update it if we found one
    if avatar_url:
        db_professor.avatar_url = avatar_url
        db.add(db_professor) # commit later

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
def generate_professor_card(professor_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    # 1. Get professor
    db_professor = crud.get_professor(db, professor_id=professor_id, user_id=current_user.id)
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
def generate_email_draft(professor_id: int, template: str = "summer_intern", db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    # 1. Get professor
    db_professor = crud.get_professor(db, professor_id=professor_id, user_id=current_user.id)
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
        content_short=email_content["subject"], 
        content_long=email_content["body"]
    )
    
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
def update_status(professor_id: int, status_update: schemas.PipelineStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    db_status = crud.update_pipeline_status(db, professor_id=professor_id, status_update=status_update, user_id=current_user.id)
    if not db_status:
        raise HTTPException(status_code=404, detail="Professor not found")
    return db_status

@app.get("/search_professors", response_model=List[schemas.SearchResult])
def search_professors(query: str, current_user: models.User = Depends(get_current_active_user)):
    from search import engine
    return engine.search_professor(query)

# Singleton LLM service (initialized once on first use)
_llm_service = None
def get_llm_service():
    global _llm_service
    if _llm_service is None:
        from services.llm import LLMService
        _llm_service = LLMService()
    return _llm_service

@app.post("/extract_avatar")
def extract_avatar(
    request: schemas.AvatarExtractionRequest, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    AI-Powered Avatar Extraction Pipeline:
    1. Scrape images from website
    2. Vision Model verifies if it's a professional photo
    3. Return best match
    """
    from search import image_scraper
    from services.vision import get_vision_service
    from cachetools import TTLCache
    import logging # Added import for logger
    logger = logging.getLogger(__name__) # Initialize logger
    
    # Cache to prevent abuse/repeated AI calls (24h)
    if not hasattr(app, "avatar_cache"):
        app.avatar_cache = TTLCache(maxsize=100, ttl=86400)
    
    if request.website_url in app.avatar_cache:
        cached = app.avatar_cache[request.website_url]
        logger.info(f"[Avatar] Cache hit for {request.website_url}")
        return {"avatar_url": cached}

    # 1. Scrape Candidates
    logger.info(f"[Avatar] Scraping images from: {request.website_url}")
    candidates = image_scraper.get_image_candidates(request.website_url)
    logger.info(f"[Avatar] Found {len(candidates)} candidates.")
    
    if not candidates:
        logger.warning("[Avatar] No image candidates found.")
        app.avatar_cache[request.website_url] = None
        return {"avatar_url": None}

    vision = get_vision_service()
    best_avatar = None

    # 2. Verify Candidates (max 5)
    for i, img_url in enumerate(candidates[:5]):
        logger.info(f"[Avatar] Checking candidate {i+1}/{min(5, len(candidates))}: {img_url}")
        content = image_scraper.download_image(img_url)
        if not content:
            logger.warning(f"[Avatar] Failed to download: {img_url}")
            continue
        
        # 3. Vision Check
        result = vision.verify_avatar(content)
        logger.info(f"[Avatar] Vision Result: {result}")
        
        if result["is_valid"]: # Relaxed check handled in vision.py now
            logger.info(f"[Avatar] ACCEPTED: {img_url} (Confidence: {result.get('confidence')})")
            best_avatar = img_url
            break 
        else:
             logger.info(f"[Avatar] REJECTED: {result.get('reason')}")
        logger.info(f"[Avatar] Verified {img_url}: {result}")
        
        if result["is_valid"] and result["confidence"] >= 0.75:
            best_avatar = img_url
            break # Found a good one
    
    # 4. Cache & Return
    app.avatar_cache[request.website_url] = best_avatar
    return {"avatar_url": best_avatar}

@app.post("/parse_search_result", response_model=schemas.ParseResponse)
def parse_search_result(req: schemas.ParseRequest, current_user: models.User = Depends(get_current_active_user)):
    """
    AI-enhanced parsing of a single search result.
    Called when user clicks a result, NOT during search.
    Falls back to rule-based if LLM is unavailable.
    """
    llm = get_llm_service()
    
    # Attempt LLM parsing
    if llm.enabled:
        try:
            results = [{"title": req.title, "snippet": req.snippet, "link": req.link}]
            parsed = llm.parse_search_results(req.query, results)
            if parsed and len(parsed) > 0:
                profile = parsed[0]
                print(f"[AI Parse] Success: name={profile.name}, affiliation={profile.affiliation}")
                return schemas.ParseResponse(
                    name=profile.name,
                    affiliation=profile.affiliation,
                    role=profile.role,
                    confidence=profile.confidence
                )
        except Exception as e:
            print(f"[AI Parse] LLM failed, falling back to rules: {e}")
    
    # Rule-based fallback
    from search.engine import extract_affiliation
    
    name = req.title
    # Handle generic titles
    GENERIC_TITLES = ["GitHub Pages", "Home", "Home Page", "Welcome", "Profile", "Bio", "About"]
    if name.lower() in [t.lower() for t in GENERIC_TITLES]:
        name = req.query.title()
    else:
        separators = [" - ", " | ", " – ", " — ", " : ", " at "]
        for sep in separators:
            if sep in req.title:
                potential = req.title.split(sep)[0].strip()
                if len(potential.split()) <= 4:
                    name = potential
                    break
    
    affiliation = extract_affiliation(req.title, req.snippet)
    
    return schemas.ParseResponse(name=name, affiliation=affiliation or None, confidence=0.3)

