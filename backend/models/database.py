from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, JSON, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String)
    filename = Column(String)
    language = Column(String)
    code_snippet = Column(Text)  # Store original code for reference

    # Results
    total_issues = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)

    code_quality_score = Column(Float)  # 0-100
    security_score = Column(Float)      # 0-100
    performance_score = Column(Float)   # 0-100

    status = Column(String, default="processing")  # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    issues = relationship("Issue", back_populates="review", cascade="all, delete-orphan")

class Issue(Base):
    __tablename__ = "issues"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    review_id = Column(String, ForeignKey("reviews.id"))
    
    category = Column(String)  # security, bug, performance, quality, style
    severity = Column(String)  # critical, high, medium, low
    line_number = Column(Integer)
    column_number = Column(Integer, nullable=True)
    
    message = Column(String)
    explanation = Column(Text)
    suggested_fix = Column(Text)
    code_snippet = Column(Text)
    
    rule_id = Column(String, nullable=True)
    cwe_id = Column(Integer, nullable=True)
    owasp_category = Column(String, nullable=True)
    
    is_fixed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    review = relationship("Review", back_populates="issues")

class GitHubIntegration(Base):
    __tablename__ = "github_integrations"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String)
    github_username = Column(String)
    repository = Column(String)
    is_active = Column(Boolean, default=True)
    
    auto_review_enabled = Column(Boolean, default=True)
    min_severity_threshold = Column(String, default="low")  # Only comment on these severities
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Database engine initialization helper
def get_engine(database_url: str):
    return create_engine(database_url)
