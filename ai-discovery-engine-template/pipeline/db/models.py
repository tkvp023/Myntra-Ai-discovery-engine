"""
SQLAlchemy ORM models for the AI Discovery Engine database.
Schema matches architecture.md §2.5.
"""

from sqlalchemy import Column, String, Text, Float, Boolean, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Document(Base):
    """Core documents table — stores all scraped and cleaned documents."""
    __tablename__ = "documents"

    doc_id = Column(String, primary_key=True)
    source = Column(String, nullable=False)          # playstore, appstore, reddit, youtube, trustpilot, pissedconsumer, reviewsio
    source_type = Column(String, nullable=False)      # primary or secondary
    source_id = Column(String)                        # original platform ID
    content = Column(Text, nullable=False)
    title = Column(Text)                              # reddit post title, video title, etc.
    rating = Column(Float)                             # 1-5 for app stores, null for reddit/youtube
    timestamp = Column(String)                        # ISO-8601
    url = Column(String)                              # permalink to original
    metadata_json = Column(Text)                      # full JSON blob for flexible metadata
    scraped_at = Column(String, nullable=False)       # ISO-8601
    author = Column(String)                           # anonymized username

    # Relationships
    classification = relationship("Classification", back_populates="document", uselist=False, cascade="all, delete-orphan")
    hesitation_tags = relationship("HesitationTag", back_populates="document", cascade="all, delete-orphan")
    factor_mentions = relationship("FactorMention", back_populates="document", cascade="all, delete-orphan")
    unmet_needs = relationship("UnmetNeed", back_populates="document", cascade="all, delete-orphan")
    question_mappings = relationship("QuestionMapping", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(doc_id='{self.doc_id}', source='{self.source}', content='{self.content[:50]}...')>"


class Classification(Base):
    """Classification results — one per document."""
    __tablename__ = "classifications"

    doc_id = Column(String, ForeignKey("documents.doc_id"), primary_key=True)
    wishlist_intent = Column(String)                  # genuine_purchase_intent, bookmarking, aspiration, etc.
    inferred_age_group = Column(String)               # gen_z, millennial, gen_x, unknown
    price_sensitivity = Column(String)                # high, medium, low, unknown
    fashion_engagement = Column(String)               # high, casual, unknown
    gender_signal = Column(String)                    # male, female, non_binary, unknown
    compares_across = Column(Boolean)                 # compares across platforms?
    seeks_external_info = Column(Boolean)             # seeks external info?
    is_primary_signal = Column(Boolean)               # relevant to the 10 discovery questions?
    raw_classification = Column(Text)                 # full JSON blob for flexibility
    classified_at = Column(String, nullable=False)    # ISO-8601

    # Relationships
    document = relationship("Document", back_populates="classification")

    def __repr__(self):
        return f"<Classification(doc_id='{self.doc_id}', intent='{self.wishlist_intent}')>"


class HesitationTag(Base):
    """Hesitation reasons — many per document."""
    __tablename__ = "hesitation_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.doc_id"), nullable=False)
    reason = Column(String, nullable=False)           # sizing_uncertainty, price_sensitivity, etc.
    confidence = Column(Float, nullable=False)          # 0.0 - 1.0
    evidence_quote = Column(Text)                     # exact substring from content

    # Relationships
    document = relationship("Document", back_populates="hesitation_tags")

    def __repr__(self):
        return f"<HesitationTag(doc_id='{self.doc_id}', reason='{self.reason}', conf={self.confidence})>"


class FactorMention(Base):
    """Factor mentions — many per document."""
    __tablename__ = "factor_mentions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.doc_id"), nullable=False)
    factor = Column(String, nullable=False)           # fit_size, price, reviews_ratings, styling, etc.
    mentioned = Column(Boolean)
    sentiment = Column(String)                        # positive, negative, neutral, mixed

    # Relationships
    document = relationship("Document", back_populates="factor_mentions")

    def __repr__(self):
        return f"<FactorMention(doc_id='{self.doc_id}', factor='{self.factor}', sentiment='{self.sentiment}')>"


class UnmetNeed(Base):
    """Unmet needs — many per document."""
    __tablename__ = "unmet_needs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.doc_id"), nullable=False)
    need_text = Column(Text, nullable=False)          # free-text extracted unmet need

    # Relationships
    document = relationship("Document", back_populates="unmet_needs")

    def __repr__(self):
        return f"<UnmetNeed(doc_id='{self.doc_id}', need='{self.need_text[:50]}')>"


class QuestionMapping(Base):
    """Question mappings — many-to-many between documents and the 10 discovery questions."""
    __tablename__ = "question_mappings"

    doc_id = Column(String, ForeignKey("documents.doc_id"), primary_key=True)
    question_id = Column(Integer, primary_key=True)   # 1-10

    # Relationships
    document = relationship("Document", back_populates="question_mappings")

    def __repr__(self):
        return f"<QuestionMapping(doc_id='{self.doc_id}', question_id={self.question_id})>"
