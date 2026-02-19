from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Professor(Base):
    __tablename__ = "professors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    affiliation = Column(String)
    website_url = Column(String)
    scholar_url = Column(String, nullable=True)
    email_guess = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pipeline_status = relationship("PipelineStatus", back_populates="professor", uselist=False)
    source_pages = relationship("SourcePage", back_populates="professor")
    professor_cards = relationship("ProfessorCard", back_populates="professor")
    email_drafts = relationship("EmailDraft", back_populates="professor")

class PipelineStatus(Base):
    __tablename__ = "pipeline_timestamps"

    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("professors.id"), unique=True)
    status = Column(String, default="Draft") # Draft, Sent, Replied, Meeting, Closed
    last_touch_at = Column(DateTime, nullable=True)
    next_action_at = Column(DateTime, nullable=True)
    followup_recommended = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    professor = relationship("Professor", back_populates="pipeline_status")

class SourcePage(Base):
    __tablename__ = "source_pages"

    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("professors.id"))
    source_url = Column(String)
    raw_html = Column(Text, nullable=True)
    raw_text = Column(Text)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    fetch_status = Column(String) # ok, failed
    error_msg = Column(String, nullable=True)

    professor = relationship("Professor", back_populates="source_pages")

class ProfessorCard(Base):
    __tablename__ = "professor_cards"

    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("professors.id"))
    card_json = Column(Text) # JSON string
    card_md = Column(Text)
    version = Column(Integer, default=1)
    generated_at = Column(DateTime, default=datetime.utcnow)

    professor = relationship("Professor", back_populates="professor_cards")

class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("professors.id"))
    type = Column(String) # summer_intern, visit, phd, remote
    tone = Column(String) # formal, concise, warm
    content_short = Column(Text, nullable=True)
    content_long = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    professor = relationship("Professor", back_populates="email_drafts")
