# Secret-leak responder

## What it does
Runs after GitLab's built-in Secret Detection analyzer and turns its report into two things an analyzer result alone isn't: a tracked, assignable issue per finding, and a failed pipeline that actually blocks the merge request.

## Behaviour
- **Consumes the analyzer's own report format**: rather than re-implementing secret scanning, this reads `gl-secret-detection-report.json` — the standard output of GitLab's `Secret-Detection.gitlab-ci.yml` template — so it stays correct as GitLab's detection rules improve, without this script needing to track them.
- **One issue per finding, not one issue per scan**: each secret gets its own issue with the file/line and rule that matched — a scan that finds three unrelated secrets produces three independently closeable issues, not one issue someone has to split up manually.
- **The description calls out rotation, not just removal**: deleting the secret from the file doesn't invalidate it if it was ever pushed — the issue text exists specifically so "removed the line" doesn't get treated as "resolved" without the credential actually being rotated.
- **Only runs on MR pipelines**: `rules` scopes this to merge request pipelines, which is where failing the job actually blocks a merge — a scheduled or branch pipeline finding the same secret still matters, but there's no merge to block at that point.

## Why it's needed
A secret-detection scan that only produces a report in the pipeline's artifacts is easy to miss — nobody's job is "check every pipeline's security tab". Converting a finding into an issue and a failed required job makes it impossible to merge past, and impossible to lose track of.
