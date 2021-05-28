from jira import JIRA
from github import Github
from github.GithubException import GithubException
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time


def handle_issue_closed(jira, event):
    # note: Not auto-closing the synced JIRA issue because GitHub
    # issues often get closed for the wrong reasons - ie the user
    # found a workaround but the root cause still exists.
    issue = _leave_jira_issue_comment(jira, event, "closed", False)
    if issue is not None:
        _update_link_resolved(jira, event["issue"], issue)

def _update_link_resolved(jira, gh_issue, jira_issue):
    """
    Update the 'resolved' status of the remote "synced from" link, based on the
    GitHub issue open/closed status.
    (A 'resolved' link is shown in strikethrough format in JIRA interface.)
    Also updates the link title, if GitHub issue title has changed.
    """
    resolved = gh_issue["state"] != "open"
    for link in jira.remote_links(jira_issue):
        if hasattr(link, "globalId") and link.globalId == gh_issue["html_url"]:
            new_link = dict(link.raw["object"])  # RemoteLink update() requires all fields as a JSON object, it seems
            new_link["title"] = gh_issue["title"]
            new_link["status"]["resolved"] = resolved
            link.update(new_link, globalId=link.globalId, relationship=link.relationship)