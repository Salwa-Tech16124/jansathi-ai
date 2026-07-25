from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from datetime import datetime
from app.database import Base


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    scheme_name = Column(String(500), nullable=True, index=True)
    slug = Column(String(255), nullable=True, index=True)
    details = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    eligibility = Column(Text, nullable=True)
    application = Column(Text, nullable=True)
    documents = Column(Text, nullable=True)
    level = Column(String(100), nullable=True)
    schemeCategory = Column(String(255), nullable=True, index=True)
    tags = Column(Text, nullable=True, index=True)

    # Legacy fields for backward compatibility with existing DB schema / API responses
    title_legacy = Column("title", String(255), nullable=True, index=True)
    category_legacy = Column("category", String(100), nullable=True, index=True)
    description_legacy = Column("description", Text, nullable=True)
    required_documents_legacy = Column("required_documents", Text, nullable=True)
    deadline = Column(String(100), nullable=True, default="Open Year Round")
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def title(self) -> str:
        return self.scheme_name or self.title_legacy or "Government Scheme"

    @property
    def category(self) -> str:
        return self.schemeCategory or self.category_legacy or "General Welfare"

    @property
    def description(self) -> str:
        return self.details or self.description_legacy or ""

    @property
    def required_documents(self) -> str:
        return self.documents or self.required_documents_legacy or "Standard Identity & Residence proof"

    @property
    def official_link(self) -> str:
        if self.slug and self.slug.strip():
            return f"https://www.myscheme.gov.in/schemes/{self.slug.strip()}"
        return ""


# Explicit Index declarations for scheme_name, schemeCategory, and tags
Index("idx_scheme_name", Scheme.scheme_name)
Index("idx_scheme_category", Scheme.schemeCategory)
Index("idx_tags", Scheme.tags)
