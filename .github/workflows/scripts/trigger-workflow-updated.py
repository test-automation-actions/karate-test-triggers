import os
import time
import requests
import argparse
import json

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# GitHub Token (export this in your shell or GitHub Action env)
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {TOKEN}"
}


def trigger_workflow(repo, workflow, branch, inputs=None):
    """Triggers a workflow dispatch event for the given repository."""
    url = f"{GITHUB_API_URL}/repos/{repo}/actions/workflows/{workflow}/dispatches"
    payload = {
        "ref": branch,
        "inputs": inputs or {}
    }

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 204:
        print(f"✅ Successfully triggered workflow for {repo} on branch {branch}.")
        return True
    else:
        print(f"❌ Failed to trigger workflow for {repo}: {response.text}")
        return False


def get_latest_workflow_run(repo, branch):
    """Fetches the latest workflow run URL."""
    url = f"{GITHUB_API_URL}/repos/{repo}/actions/runs?branch={branch}&status=in_progress"

    for attempt in range(10):
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            runs = response.json().get("workflow_runs", [])
            if runs:
                return runs[0]["html_url"]

        print(f"🔄 Attempt {attempt + 1}: No run found yet, retrying in 5 seconds...")
        time.sleep(5)

    print(f"⚠️ Failed to fetch workflow URL for {repo} after 10 attempts.")
    return None


def main():
    parser = argparse.ArgumentParser(description="Trigger GitHub workflow and fetch the run URL.")
    parser.add_argument("--repo", required=True, help="GitHub repository (e.g., user/repo-name)")
    parser.add_argument("--workflow", required=True, help="Workflow file name (e.g., test-execution.yml)")
    parser.add_argument("--branch", required=True, help="Branch or reference to trigger (e.g., main or develop)")
    parser.add_argument("--inputs", help="Inputs to pass to the workflow (JSON string)")

    args = parser.parse_args()

    repo = args.repo
    workflow = args.workflow
    branch = args.branch
    inputs = json.loads(args.inputs) if args.inputs else None

    if trigger_workflow(repo, workflow, branch, inputs):
        workflow_url = get_latest_workflow_run(repo, branch) or "Not found"
        print(f"🌐 {repo} Workflow URL: {workflow_url}")

        # Save to GitHub environment variable if in Actions
        if os.getenv("GITHUB_ENV"):
            repo_key = repo.split("/")[-1].replace("-", "_").upper()
            with open(os.getenv("GITHUB_ENV"), "a") as env_file:
                env_file.write(f"{repo_key}_URL={workflow_url}\n")


if __name__ == "__main__":
    main()
