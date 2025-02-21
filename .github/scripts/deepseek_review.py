"""Running the code review using DeepSeek."""

import os
import requests
from github import Github


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = int(os.getenv("GITHUB_REF").split("/")[-2])


def get_code_suggestion(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 0.7,
    }
    response = requests.post(
        "https://api.deepseek.com/v1/completions",
        headers=headers,
        data=data,
    )
    return response.json()["choices"][0]["text"]


def post_comment_to_pr(comment):
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(REPO_NAME)
    pr = repo.get_pull(PR_NUMBER)
    pr.create_issue_comment(comment)


if __name__ == "__main__":
    prompt = "Review this code for potential issues and suggest improvements."
    print(f"{REPO_NAME=}")
    print(f"{PR_NUMBER=}")

    review_comment = get_code_suggestion(prompt)
    post_comment_to_pr(review_comment)
