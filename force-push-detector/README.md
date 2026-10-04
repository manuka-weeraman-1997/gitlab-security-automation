# Force-push detector

## What it does
Receives GitLab's "Push events" webhook for every push, and flags any push to a protected branch (`main`/`master`/`production`) that looks like a force push — something that shouldn't normally be possible, but can happen if force push was left enabled or someone with elevated access temporarily unprotected the branch.

## Behaviour
- **Webhook token verification**: GitLab signs webhook requests with a secret token in the `X-Gitlab-Token` header — `verify_signature` rejects anything that doesn't match, so this endpoint can't be triggered by a forged request from outside GitLab.
- **All-zero SHA = branch create/delete, not a force push**: `before`/`after` are all-zeros when a branch is created or deleted — those are legitimate operations and explicitly excluded, otherwise every new branch would trigger a false alert.
- **Flags candidates, doesn't auto-confirm**: properly distinguishing a force push from an ordinary fast-forward push needs an ancestry check (`git merge-base --is-ancestor`) against the actual repository — this handler deliberately flags every non-trivial history change on a protected branch for a human to look at, rather than risk silently missing a real one by trying to be clever about ruling cases out.

## Why it's needed
A force push to a protected branch can silently drop commits other people's work depends on, or rewrite history in a way that breaks anyone with that branch checked out — it's exactly the kind of event that should never happen quietly. Detecting it in near-real-time, rather than someone noticing their commit is "gone" days later, is what makes it possible to investigate and recover quickly.
