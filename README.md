# GitLab Security Automation

Automated detection/response for SCM policy violations across GitLab projects — each violation type is its own dedicated repo so each can be deployed, versioned, and run independently.

| Repo | Violation it addresses |
|---|---|
| [`gitlab-protected-branch-enforcer`](https://github.com/manuka-weeraman-1997/gitlab-protected-branch-enforcer) | Default branch missing protection, or protection weaker than policy (force push allowed) |
| [`gitlab-force-push-detector`](https://github.com/manuka-weeraman-1997/gitlab-force-push-detector) | A force push / history rewrite lands on a protected branch |
| [`gitlab-secret-leak-responder`](https://github.com/manuka-weeraman-1997/gitlab-secret-leak-responder) | GitLab's secret detection scanner finds a committed credential |

## Why separate repos per violation
Each of these runs on its own trigger (a schedule, a webhook, a scan result), has its own blast radius if it misbehaves, and its own permissions footprint — an enforcer that *changes* branch protection settings needs much broader access than a detector that only reads push events. Bundling them into one project would mean one bug, or one overly-broad token, affecting all three.

Author: Manuka Weeraman — Platform Engineer
