import requests
import argparse
import os

def trigger_workflow(repo, workflow, branch, token):
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}"
    }
    payload = {"ref": branch}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 204:
        workflow_url = f"https://github.com/{repo}/actions/workflows/{workflow}"
        print(f"Workflow triggered successfully: {workflow_url}")

        # Save the output for GitHub Actions
        with open(os.environ['GITHUB_OUTPUT'], "a") as gh_output:
            gh_output.write(f"workflow_url={workflow_url}\n")
        
        return workflow_url
    else:
        print(f"Failed to trigger workflow. Response: {response.text}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger GitHub Actions Workflows")
    parser.add_argument("--repo", required=True, help="Repository name (org/repo)")
    parser.add_argument("--workflow", required=True, help="Workflow file name")
    parser.add_argument("--branch", required=True, help="Branch to trigger workflow")
    
    args = parser.parse_args()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("GITHUB_TOKEN is not set!")
        exit(1)

    workflow_url = trigger_workflow(args.repo, args.workflow, args.branch, token)

    if workflow_url:
        print(f"Triggered workflow: {workflow_url}")
