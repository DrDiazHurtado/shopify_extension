from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)  # suggest, chrome_store
    keyword = Column(String, nullable=False)
    product_name = Column(String)
    url = Column(String, unique=True)
    domain = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    signals = relationship("Signal", back_populates="candidate")
    scores = relationship("Score", back_populates="candidate", uselist=False)

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    signal_name = Column(String, nullable=False)
    value_numeric = Column(Float)
    value_text = Column(Text)
    confidence = Column(Float, default=1.0)
    evidence_url = Column(String)
    evidence_snippet = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="signals")

class RawPage(Base):
    __tablename__ = "raw_pages"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    status_code = Column(Integer)
    content_hash = Column(String)
    content_path = Column(String)

class Score(Base):
    __tablename__ = "scores"

    candidate_id = Column(Integer, ForeignKey("candidates.id"), primary_key=True)
    money_score = Column(Float, default=0.0)
    demand_score = Column(Float, default=0.0)
    competition_score = Column(Float, default=0.0)
    pain_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)
    scored_at = Column(DateTime, default=datetime.utcnow)

    explanation = Column(Text)  # Top contributing signals

    candidate = relationship("Candidate", back_populates="scores")
