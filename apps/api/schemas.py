from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True
class PipelineStatusBase(BaseModel):
    status: str = "Draft"
    last_touch_at: Optional[datetime] = None
    next_action_at: Optional[datetime] = None
    followup_recommended: bool = False
    notes: Optional[str] = None

class PipelineStatusCreate(PipelineStatusBase):
    pass

class PipelineStatusUpdate(BaseModel):
    status: Optional[str] = None
    last_touch_at: Optional[datetime] = None
    next_action_at: Optional[datetime] = None
    followup_recommended: Optional[bool] = None
    notes: Optional[str] = None

class SearchResult(BaseModel):
    title: str
    name: Optional[str] = None
    link: str
    snippet: str
    affiliation: Optional[str] = None

class ParseRequest(BaseModel):
    query: str
    title: str
    snippet: str
    link: str

class ParseResponse(BaseModel):
    name: str
    affiliation: Optional[str] = None
    role: Optional[str] = None
    confidence: float = 0.5

class AvatarExtractionRequest(BaseModel):
    website_url: str
    name: str

class PipelineStatus(PipelineStatusBase):
    id: int
    professor_id: int

    class Config:
        orm_mode = True

class SourcePageBase(BaseModel):
    source_url: str
    fetch_status: str
    error_msg: Optional[str] = None

class SourcePageCreate(SourcePageBase):
    raw_html: Optional[str] = None
    raw_text: Optional[str] = None

class SourcePage(SourcePageBase):
    id: int
    professor_id: int
    fetched_at: datetime
    raw_text: Optional[str] = None

    class Config:
        orm_mode = True

class IngestRequest(BaseModel):
    professor_id: int
    url: str

class ProfessorCardBase(BaseModel):
    card_json: str
    card_md: Optional[str] = None
    hiring_signals: Optional[str] = None # JSON string list

class ProfessorCard(ProfessorCardBase):
    id: int
    professor_id: int
    version: int
    generated_at: datetime

    class Config:
        orm_mode = True

class EmailDraftBase(BaseModel):
    type: str # summer_intern, phd
    subject: Optional[str] = None
    body: Optional[str] = None

class EmailDraftCreate(EmailDraftBase):
    pass

class EmailDraft(EmailDraftBase):
    id: int
    professor_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProfessorBase(BaseModel):
    name: str
    affiliation: str
    website_url: str
    target_role: Optional[str] = "summer_intern"
    avatar_url: Optional[str] = None
    scholar_url: Optional[str] = None
    email_guess: Optional[str] = None

class ProfessorCreate(ProfessorBase):
    pass

class ProfessorUpdate(ProfessorBase):
    name: Optional[str] = None
    affiliation: Optional[str] = None
    website_url: Optional[str] = None
    target_role: Optional[str] = None
    avatar_url: Optional[str] = None
    scholar_url: Optional[str] = None
    email_guess: Optional[str] = None

class Professor(ProfessorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    pipeline_status: Optional[PipelineStatus] = None
    source_pages: List[SourcePage] = []
    professor_cards: List[ProfessorCard] = []
    email_drafts: List[EmailDraft] = []

    class Config:
        orm_mode = True
