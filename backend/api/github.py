from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
import json
from typing import Optional

# Mock imports
def fetch_pr_diff(url): return "mock diff"
def parse_diff(diff): return {"mock_file.py": "additions"}
def detect_language(path): return "python"
def fetch_file_content(repo, path): return "mock content"

router = APIRouter()

@router.post("/webhook")
async def github_webhook(request: Request):
    """
    GitHub webhook endpoint for automatic PR reviews.
    """

    # Verify webhook signature
    payload = await request.body()
    if not verify_github_signature(payload, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = json.loads(payload)
    event = request.headers.get("X-GitHub-Event")

    if event == "pull_request":
        action = data.get("action")
        if action in ["opened", "synchronize"]:  # New PR or new commit pushed
            await handle_pr_review(data)

    return {"status": "received"}

async def handle_pr_review(pr_data: dict):
    """Analyze PR and post reviews"""
    repo_name = pr_data['repository']['full_name']
    pr_number = pr_data['pull_request']['number']
    diff_url = pr_data['pull_request']['diff_url']

    # Fetch PR diff
    diff_content = fetch_pr_diff(diff_url)

    # Parse diff to get changed files
    changed_files = parse_diff(diff_content)

    # Review each changed file
    all_issues = []
    for file_path, additions in changed_files.items():
        language = detect_language(file_path)
        file_code = fetch_file_content(repo_name, file_path)

        # Run analysis on changed code
        from llm.reviewer import LLMReviewer
        review = await LLMReviewer().review_code(file_code, language)
        all_issues.extend(review['issues'])

    # Post review comments on GitHub
    if all_issues:
        post_github_review(repo_name, pr_number, all_issues)

def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature using HMAC-SHA256"""
    if not signature:
        return False
        
    from config import get_settings
    settings = get_settings()

    expected = "sha256=" + hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)

def post_github_review(repo_name: str, pr_number: int, issues: list):
    """Post CodeSentinel review as GitHub PR comment"""
    print(f"Posting {len(issues)} issues to PR #{pr_number} in {repo_name}")
    # from github import Github
    # g = Github(auth=...)
    # repo = g.get_repo(repo_name)
    # pr = repo.get_pull(pr_number)
    # pr.create_issue_comment(...)
