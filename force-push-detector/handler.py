"""
Webhook receiver for GitLab Push Events. Flags force pushes (non-trivial
history rewrites) that land on a branch this policy considers protected,
even though they weren't supposed to be possible - a protected branch can
still receive a force push if "Allow force push" was left enabled, or if
someone with Maintainer+ access temporarily unprotects, force-pushes, and
reprotects.

Configure under Project Settings > Webhooks with the "Push events" trigger.
"""
import hmac
import json
import os

PROTECTED_BRANCHES = {"main", "master", "production"}
ZERO_SHA = "0000000000000000000000000000000000000000"


def verify_signature(token_header, secret):
    return hmac.compare_digest(token_header or "", secret)


def is_force_push(before, after):
    # A branch create/delete (all-zero SHA on one side) is not a force push.
    if before == ZERO_SHA or after == ZERO_SHA:
        return False
    # A genuine fast-forward keeps the old tip reachable from the new one;
    # confirming that properly needs a `git merge-base --is-ancestor` check
    # against the actual repository. This handler flags every non-trivial
    # history change for a human to confirm, rather than risk silently
    # missing a real one by trying to be clever about ruling cases out.
    return True


def handle(event, context):
    secret = os.environ["WEBHOOK_SECRET"]
    if not verify_signature(event["headers"].get("X-Gitlab-Token"), secret):
        return {"statusCode": 401, "body": "invalid token"}

    payload = json.loads(event["body"])
    if payload.get("object_kind") != "push":
        return {"statusCode": 200, "body": "ignored"}

    branch = payload["ref"].replace("refs/heads/", "")
    if branch not in PROTECTED_BRANCHES:
        return {"statusCode": 200, "body": "not a protected branch"}

    if is_force_push(payload["before"], payload["after"]):
        alert(payload)

    return {"statusCode": 200, "body": "ok"}


def alert(payload):
    print(
        f"ALERT: possible force push to protected branch '{payload['ref']}' "
        f"in {payload['project']['path_with_namespace']} by {payload['user_name']}"
    )
    # In production: post to Slack/PagerDuty, or open a GitLab issue via the
    # Issues API so it's tracked and assignable.
