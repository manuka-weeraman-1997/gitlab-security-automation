#!/usr/bin/env python3
"""
Audits every project in a GitLab group for protected-branch policy
violations, and optionally remediates them via the API.

Policy enforced:
  - the default branch must be protected
  - force push must be disabled on the default branch
"""
import argparse
import sys

import requests

REQUIRED_MIN_ACCESS_LEVEL = 40  # Maintainer


def get_projects(gitlab_url, group_id, token):
    url = f"{gitlab_url}/api/v4/groups/{group_id}/projects"
    resp = requests.get(
        url,
        headers={"PRIVATE-TOKEN": token},
        params={"per_page": 100, "include_subgroups": True},
    )
    resp.raise_for_status()
    return resp.json()


def get_protected_branch(gitlab_url, project_id, branch, token):
    url = f"{gitlab_url}/api/v4/projects/{project_id}/protected_branches/{branch}"
    resp = requests.get(url, headers={"PRIVATE-TOKEN": token})
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def remediate(gitlab_url, project_id, branch, token):
    url = f"{gitlab_url}/api/v4/projects/{project_id}/protected_branches"
    # The API only supports create/delete, not patch - remove any existing
    # (weaker) rule first, then create a compliant one in its place.
    requests.delete(f"{url}/{branch}", headers={"PRIVATE-TOKEN": token})
    requests.post(
        url,
        headers={"PRIVATE-TOKEN": token},
        data={
            "name": branch,
            "push_access_level": REQUIRED_MIN_ACCESS_LEVEL,
            "merge_access_level": REQUIRED_MIN_ACCESS_LEVEL,
            "allow_force_push": "false",
        },
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gitlab_url")
    parser.add_argument("group_id")
    parser.add_argument("token")
    parser.add_argument("--fix", action="store_true", help="remediate violations instead of only reporting them")
    args = parser.parse_args()

    violations = []
    for project in get_projects(args.gitlab_url, args.group_id, args.token):
        branch = project["default_branch"]
        if not branch:
            continue

        rule = get_protected_branch(args.gitlab_url, project["id"], branch, args.token)
        reason = None
        if rule is None:
            reason = "default branch is not protected"
        elif rule.get("allow_force_push"):
            reason = "force push is allowed on the default branch"

        if reason:
            violations.append((project["path_with_namespace"], reason))
            if args.fix:
                remediate(args.gitlab_url, project["id"], branch, args.token)

    for path, reason in violations:
        print(f"VIOLATION: {path}: {reason}")

    sys.exit(1 if violations and not args.fix else 0)


if __name__ == "__main__":
    main()
