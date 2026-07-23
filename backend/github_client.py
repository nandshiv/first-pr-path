import os 
import requests
from dotenv import load_dotenv
import re

load_dotenv()

GITHUB_TOEKN = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"

def get_headers():
  return{
    "Authorization" : f"Bearer {GITHUB_TOEKN}",
    "Accept" : "application/vnd.github+json"
  }

def fetch_repo_info(owner: str , repo: str):
  url = f"{BASE_URL}/repos/{owner}/{repo}"
  response = requests.get(url , headers=get_headers())
  response.raise_for_status()
  return response.json()

def parse_owner_repo_from_url(url: str):
    match = re.match(r"^https?://github\.com/([^/]+)/([^/]+?)/?$", url.strip())
    if not match:
        raise ValueError(f"Not a valid GitHub repo URL: {url}")
    return match.group(1), match.group(2)

def fetch_commits(owner: str , repo: str , max_pages: int = 5):
  commits = []
  page = 1
  while page<=max_pages:
    url = f"{BASE_URL}/repos/{owner}/{repo}/commits"
    params = {"per_page" : 100 , "page" : page}
    response = requests.get(url , headers=get_headers() , params=params)
    response.raise_for_status()
    data = response.json()
    if not data:
      break
    commits.extend(data)
    page += 1
  return commits

def fetch_commit_detail(owner: str , repo: str , sha:str):
  url = f"{BASE_URL}/repos/{owner}/{repo}/commits/{sha}"
  response = requests.get(url , headers= get_headers())
  response.raise_for_status()
  data = response.json();
  files = [f["filename"] for f in data.get("files" , [])]
  return files

def fetch_pull_requests(owner:str , repo:str , max_pages: int = 5):
  prs=[]
  page = 1
  while page<=max_pages:
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"
    params = {"state" : "all" , "per_page" : 100 , "page":page}
    response = requests.get(url , headers=get_headers() , params=params)
    response.raise_for_status()
    data = response.json()
    if not data:
      break
    prs.extend(data)
    page += 1
  return prs

def fetch_issues(owner:str , repo:str , max_pages:int = 5):
  issues=[]
  page = 1
  while page<=max_pages:
    url = f"{BASE_URL}/repos/{owner}/{repo}/issues"
    params = {"state" : "all" , "per_page" : 100 , "page":page}
    response = requests.get(url , headers = get_headers() , params = params)
    response.raise_for_status()
    data = response.json()
    if not data:
      break
    real_issues = [item for item in data if "pull_request" not in item]
    issues.extend(real_issues)
    page += 1
  
  return issues

def fetch_pr_comments(owner: str, repo: str, pr_number: int, max_pages: int = 2):
    comments = []
    page = 1
    while page <= max_pages:
        url = f"{BASE_URL}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        params = {"per_page": 100, "page": page}
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        comments.extend(data)
        page += 1
    return comments

def fetch_issue_state(owner: str, repo: str, issue_number: int):
    url = f"{BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()["state"]

def fetch_git_tree(owner: str, repo: str, sha: str):
    url = f"{BASE_URL}/repos/{owner}/{repo}/git/trees/{sha}"
    params = {"recursive": 1}
    response = requests.get(url, headers=get_headers(), params=params)
    response.raise_for_status()
    tree_data = response.json().get("tree", [])
    files = [item["path"] for item in tree_data if item.get("type") == "blob"]
    return files[:10000]