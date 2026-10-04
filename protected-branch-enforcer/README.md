# Protected-branch enforcer

## What it does
Walks every project in a GitLab group (including subgroups), checks whether each project's default branch is actually protected against force pushes and unreviewed merges, and — with `--fix` — remediates any violation it finds.

## Behaviour
- **Audit-first, fix-on-request**: without `--fix`, the script only reports violations and exits non-zero — safe to run on a schedule as a compliance check (e.g. feeding a dashboard or failing a scheduled pipeline) without it ever silently changing anyone's project settings.
- **Delete-then-recreate for remediation**: GitLab's API doesn't support partially patching a protected branch rule, so fixing a weak rule means removing it and creating a correct one in its place — briefly leaving the branch unprotected between the two calls, a real tradeoff worth knowing about before running `--fix` against a busy project.
- **Checks subgroups too**: `include_subgroups=True` means a project nested several subgroups deep under the top-level group doesn't silently escape the audit.

## Why it's needed
Branch protection is usually set up correctly when a project is first created and then drifts — someone temporarily disables it to force-push a fix and forgets to re-enable it, or a brand-new project is created without anyone applying the org's standard policy. An automated audit catches that drift instead of relying on someone noticing.
