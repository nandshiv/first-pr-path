from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from models import Repo , FileCentrality
from database import get_db , init_db
from crud import create_repo_from_url , save_commits , save_issues , save_pull_requests , backfill_commit_files
from github_client import fetch_commits , fetch_issues , fetch_pull_requests
from graph_analysis import save_centrality_scores

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

class RepoCreateRequest(BaseModel):
    url : str

@app.get("/")
def read_root():
    return {"message": "Backend is alive"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"database": "connected", "result": result.scalar()}

@app.post("/repos")
def add_repo(request : RepoCreateRequest , db : Session = Depends(get_db)):
    repo = create_repo_from_url(db , request.url)

    raw_commits = fetch_commits(repo.owner , repo.name , max_pages=1)
    commits_saved = save_commits(db , repo , raw_commits)

    raw_prs = fetch_pull_requests(repo.owner, repo.name, max_pages=1)
    prs_saved = save_pull_requests(db, repo, raw_prs)

    raw_issues = fetch_issues(repo.owner, repo.name, max_pages=1)
    issues_saved = save_issues(db, repo, raw_issues)
    return {
        "id" : str(repo.id),
        "owner" : repo.owner,
        "name" : repo.name,
        "github_url" : repo.github_url,
        "index_status" : repo.index_status,
        "commits_saved" : commits_saved,
        "prs_saved": prs_saved,
        "issues_saved": issues_saved
    }

@app.post("/repos/{repo_id}/backfill-files")
def backfill_files(repo_id = str , db: Session = Depends(get_db)):
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if not repo:
        return {"error" : "repo not found"}
    updated = backfill_commit_files(db , repo , limit=20)
    return {"commits_updated" : updated}

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