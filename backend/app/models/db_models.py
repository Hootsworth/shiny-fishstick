import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    root_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    crawls = relationship("Crawl", back_populates="project", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="project", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="project", cascade="all, delete-orphan")
    auth_configs = relationship("AuthConfig", back_populates="project", cascade="all, delete-orphan")
    spec_versions = relationship("SpecVersion", back_populates="project", cascade="all, delete-orphan")

class Crawl(Base):
    __tablename__ = "crawls"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="crawls")
    pages = relationship("Page", back_populates="crawl", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    crawl_id = Column(String(36), ForeignKey("crawls.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(2048), nullable=False)
    path = Column(String(2048), nullable=False)
    title = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    crawl = relationship("Crawl", back_populates="pages")
    elements = relationship("Element", back_populates="page", cascade="all, delete-orphan")

class Element(Base):
    __tablename__ = "elements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    page_id = Column(String(36), ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    selector = Column(String(2048), nullable=False)
    text_content = Column(Text, nullable=True)
    element_type = Column(String(100), nullable=False)  # button, input, form, table, link
    attributes = Column(Text, nullable=True)  # JSON string
    outer_html = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    page = relationship("Page", back_populates="elements")

class Action(Base):
    __tablename__ = "actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    intent = Column(String(255), nullable=False)
    selector = Column(String(2048), nullable=False)
    parameters = Column(Text, nullable=True)  # JSON string
    action_type = Column(String(100), nullable=False)  # browser or api
    api_url = Column(String(2048), nullable=True)
    api_method = Column(String(10), nullable=True)
    confidence_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="actions")

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    steps = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="workflows")

class AuthConfig(Base):
    __tablename__ = "auth_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    auth_type = Column(String(100), nullable=False)  # cookie, token, oauth, session
    details = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="auth_configs")

class SpecVersion(Base):
    __tablename__ = "spec_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    version = Column(String(50), nullable=False)
    yaml_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="spec_versions")
