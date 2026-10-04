#!/usr/bin/env python3
"""
Parses GitLab's Secret Detection report (gl-secret-detection-report.json,
produced by the Secret-Detection.gitlab-ci.yml analyzer template) and opens
a tracked GitLab issue for every newly-detected secret, then fails the
pipeline - turning a scan result into both a tracked work item and a hard
gate, rather than a report nobody reads.
"""
import json
import sys

import requests


def load_findings(report_path):
    with open(report_path) as f:
        report = json.load(f)
    return report.get("vulnerabilities", [])


def create_issue(gitlab_url, project_id, token, finding):
    url = f"{gitlab_url}/api/v4/projects/{project_id}/issues"
    title = f"Secret detected: {finding['name']}"
    description = (
        f"**File:** `{finding['location']['file']}` line {finding['location'].get('start_line')}\n\n"
        f"**Rule:** {finding['identifiers'][0]['name']}\n\n"
        "This commit must be amended to remove the secret, and the credential "
        "itself must be rotated - removing it from the file alone does not "
        "invalidate a credential that was already pushed."
    )
    resp = requests.post(
        url,
        headers={"PRIVATE-TOKEN": token},
        data={"title": title, "description": description, "labels": "security,secret-leak"},
    )
    resp.raise_for_status()
    return resp.json()


def main():
    report_path, gitlab_url, project_id, token = sys.argv[1:5]
    findings = load_findings(report_path)

    for finding in findings:
        issue = create_issue(gitlab_url, project_id, token, finding)
        print(f"Opened {issue['web_url']} for: {finding['name']}")

    if findings:
        print(f"{len(findings)} secret(s) detected - failing pipeline.")
        sys.exit(1)


if __name__ == "__main__":
    main()
