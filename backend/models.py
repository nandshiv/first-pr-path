from sqlalchemy import Column, String, DateTime, ARRAY, ForeignKey , Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class Repo(Base):
    __tablename__ = "repos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_url = Column(String, unique=True, nullable=False)
    owner = Column(String, nullable=False)
    name = Column(String, nullable=False)
    last_synced_sha = Column(String, nullable=True)
    index_status = Column(String, default="pending")

class Commit(Base):
    __tablename__ = "commits"

    sha = Column(String, primary_key=True)
    repo_id = Column(UUID(as_uuid=True), ForeignKey("repos.id"), nullable=False)
    authored_at = Column(DateTime, nullable=True)
    message = Column(String, nullable=True)
    files_changed = Column(ARRAY(String), nullable=True)

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(UUID(as_uuid = True) , primary_key = True , default = uuid.uuid4)
    repo_id = Column(UUID(as_uuid = True) , ForeignKey("repos.id") , nullable = False)
    github_pr_number = Column(Integer , nullable = False)
    title = Column(String , nullable = True)
    body = Column(String , nullable = True)
    state = Column(String , nullable = True)
    merged_at = Column(DateTime , nullable = True)

class Issue(Base):
    __tablename__ = "issues"
    id = Column(UUID(as_uuid = True) , primary_key = True , default = uuid.uuid4)
    repo_id = Column(UUID(as_uuid = True) , ForeignKey("repos.id") , nullable = False)
    github_issue_number = Column(Integer , nullable = False)
    title = Column(String , nullable = True)
    body = Column(String , nullable = True)
    state = Column(String , nullable = True)
    labels = Column(ARRAY(String) , nullable = True)