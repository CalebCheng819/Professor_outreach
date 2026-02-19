from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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
    link: str
    snippet: str

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

class ProfessorCard(ProfessorCardBase):
    id: int
    professor_id: int
    version: int
    generated_at: datetime

    class Config:
        orm_mode = True

class EmailDraftBase(BaseModel):
    type: str # summer_intern, phd
    subject: str
    body: str

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
    scholar_url: Optional[str] = None
    email_guess: Optional[str] = None

class ProfessorCreate(ProfessorBase):
    pass

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
