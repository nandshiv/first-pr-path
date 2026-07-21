from database import SessionLocal
from models import Issue
from matching import _avg_centrality_for_issue

db = SessionLocal()

issue = db.query(Issue).filter(
    Issue.repo_id == "08fa5449-11b2-447f-ab0e-bce087deda62",
    Issue.github_issue_number == 82
).first()

print("Title:", issue.title)
print("Body:", issue.body[:200] if issue.body else None)

score = _avg_centrality_for_issue(db, "08fa5449-11b2-447f-ab0e-bce087deda62", issue)
print("Computed centrality:", score)