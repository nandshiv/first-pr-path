from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from database import get_db , init_db
from crud import create_repo_from_url , save_commits , save_issues , save_pull_requests
from github_client import fetch_commits , fetch_issues , fetch_pull_requests

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