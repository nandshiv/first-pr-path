import uuid
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from datetime import datetime, timezone
from models import Repo, FileCentrality, ResolutionReport, Issue
from database import get_db, init_db
from crud import create_repo_from_url, save_commits, save_issues, save_pull_requests, backfill_commit_files
from github_client import fetch_commits, fetch_issues, fetch_pull_requests
from graph_analysis import save_centrality_scores
from embeddings import embed_and_store_prs, embed_and_store_issues
from explain import explain_file
from matching import score_issues_for_user, get_verified_open_issues

app = FastAPI()

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

class RepoCreateRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "Backend is alive"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"database": "connected", "result": result.scalar()}

@app.post("/repos")
def add_repo(request: RepoCreateRequest, db: Session = Depends(get_db)):
    repo = create_repo_from_url(db, request.url)

    raw_commits = fetch_commits(repo.owner, repo.name, max_pages=1)
    commits_saved = save_commits(db, repo, raw_commits)

    raw_prs = fetch_pull_requests(repo.owner, repo.name, max_pages=1)
    prs_saved = save_pull_requests(db, repo, raw_prs)

    raw_issues = fetch_issues(repo.owner, repo.name, max_pages=1)
    issues_saved = save_issues(db, repo, raw_issues)

    # Ingest details for recommendations
    backfill_commit_files(db, repo, limit=20)
    save_centrality_scores(db, str(repo.id))
    embed_and_store_prs(db, str(repo.id), repo.owner, repo.name, limit=10)
    embed_and_store_issues(db, str(repo.id), limit=20)

    return {
        "id": str(repo.id),
        "owner": repo.owner,
        "name": repo.name,
        "github_url": repo.github_url,
        "index_status": repo.index_status,
        "commits_saved": commits_saved,
        "prs_saved": prs_saved,
        "issues_saved": issues_saved
    }

@app.post("/repos/{repo_id}/backfill-files")
def backfill_files(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if not repo:
        return {"error": "repo not found"}
    updated = backfill_commit_files(db, repo, limit=20)
    return {"commits_updated": updated}

@app.post("/repos/{repo_id}/compute-centrality")
def compute_centrality_endpoint(repo_id: str, db: Session = Depends(get_db)):
    count = save_centrality_scores(db, repo_id)
    return {"files_scored": count}

@app.get("/repos/{repo_id}/centrality")
def get_centrality(repo_id: str, db: Session = Depends(get_db)):
    scores = (
        db.query(FileCentrality)
        .filter(FileCentrality.repo_id == repo_id)
        .order_by(FileCentrality.centrality_score.desc())
        .all()
    )
    return [{"file_path": s.file_path, "score": s.centrality_score} for s in scores]

@app.post("/repos/{repo_id}/embed-prs")
def embed_prs_endpoint(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if not repo:
        return {"error": "repo not found"}

    count = embed_and_store_prs(db, repo_id, repo.owner, repo.name, limit=10)
    return {"chunks_created": count}

@app.get("/repos/{repo_id}/explain")
def explain_file_endpoint(repo_id: str, file_path: str, db: Session = Depends(get_db)):
    result = explain_file(db, repo_id, file_path)
    return result

@app.post("/issues/{issue_id}/report-resolution")
def report_resolution(issue_id: str, pr_url: str = None, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        return {"error": "issue not found"}

    report = ResolutionReport(
        id=uuid.uuid4(),
        issue_id=issue_id,
        pr_url=pr_url,
        reported_at=datetime.now(timezone.utc)
    )
    db.add(report)
    db.commit()
    return {"status": "report recorded, will be verified against GitHub separately"}

@app.post("/repos/{repo_id}/embed-issues")
def embed_issues_endpoint(repo_id: str, db: Session = Depends(get_db)):
    count = embed_and_store_issues(db, repo_id, limit=20)
    return {"chunks_created": count}

@app.post("/repos/{repo_id}/recommendations")
def get_recommendations(repo_id: str, skill_profile: str, db: Session = Depends(get_db)):
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if not repo:
        return {"error": "repo not found"}

    candidates = score_issues_for_user(db, repo_id, skill_profile, top_n=15)
    verified = get_verified_open_issues(db, repo, candidates, needed=5)

    return [
        {
            "issue_number": c["issue"].github_issue_number,
            "title": c["issue"].title,
            "body": c["issue"].body,
            "labels": c["issue"].labels,
            "fit_score": round(c["fit_score"], 3),
            "similarity": round(c["similarity"], 3),
            "centrality": round(c["centrality"], 3),
            "matched_files": c["matched_files"],
            "staleness_days": c["staleness_days"]
        }
        for c in verified
    ]