# GitLab Security Automation

Automated detection/response for SCM policy violations across GitLab projects, grouped here as one repo — each subfolder is an independently deployable project with its own trigger and its own permissions footprint.

| Project | Violation it addresses | Trigger |
|---|---|---|
| [`protected-branch-enforcer/`](protected-branch-enforcer) | Default branch missing protection, or protection weaker than policy (force push allowed) | Scheduled audit |
| [`force-push-detector/`](force-push-detector) | A force push / history rewrite lands on a protected branch | GitLab push-event webhook |
| [`secret-leak-responder/`](secret-leak-responder) | GitLab's secret detection scanner finds a committed credential | Merge request pipeline |

## Why these stay logically separate even in one repo
Each project runs on its own trigger and needs its own access level — the enforcer *changes* branch protection settings (needs Maintainer-level API access), the detector only *reads* push events, and the responder only needs issue-creation rights on its own project. They're deployed/invoked independently; this repo just keeps them discoverable together as one coherent "GitLab security automation" story.

Author: Manuka Weeraman — Platform Engineer
