from collections import OrderedDict
from datetime import datetime, timezone
from typing import Dict, List, Optional

import click
from git import Commit
from github.Issue import Issue

from cherrytree.github_utils import (
    commit_pr_number,
    deduplicate_prs,
    get_access_token,
    get_issue,
    get_issues_from_labels,
    git_get_current_head,
    get_git_repo,
    os_system,
    truncate_str,
)
from cherrytree.classes import (
    Cherry,
    CherryTreeExecutionException,
    CommitSummary,
)

SHORT_SHA_LEN = 12
TMP_BRANCH = "__tmp_branch"


class CherryTreeBranch:
    """Represents a release branch"""

    repo: str
    release_branch: str
    main_branch: str
    labels: List[str]
    blocking_labels: List[str]
    branch_commits: Dict[str, Dict[int, Commit]]
    missing_pull_requests: List[Issue]
    pull_requests: List[int]
    cherries: List[Cherry]
    blocking_pr_ids: List[int]

    def __init__(
        self,
        repo: str,
        release_branch: str,
        main_branch: str,
        labels: List[str],
        blocking_labels: List[str],
        pull_requests: List[int],
        access_token: Optional[str],
    ):
        self.repo = repo
        self.labels = labels
        self.blocking_labels = blocking_labels
        self.pull_requests = pull_requests
        self.missing_pull_requests = []
        self.release_branch = release_branch
        self.main_branch = main_branch
        self.git_repo = get_git_repo()
        self.base_ref = self.get_base()
        self.blocking_pr_ids = []
        try:
            self.access_token = get_access_token(access_token)
        except NotImplementedError:
            click.secho(
                f"No access token provided. Either provide one via the --access-token "
                f"parameter, or set the GITHUB_TOKEN env variable", fg="red")
            exit(1)

        click.secho(f"Base ref is {self.base_ref}", fg="cyan")

        self.branches = {}
        self.branch_commits = {}
        skipped_commits = 0
        for branch in (self.main_branch, self.release_branch):
            commits = OrderedDict()
            self.branch_commits[branch] = commits
            for commit in self.git_repo.iter_commits(branch):
                pr_number = commit_pr_number(commit)
                if pr_number is None:
                    skipped_commits += 1
                else:
                    commits[pr_number] = commit
        if skipped_commits:
            # Note: merge commits and direct pushes without PR references are skipped here
            click.secho(
                f"{skipped_commits} commits skipped due to missing PRs", fg="yellow"
            )

        # add all PRs that should be cherries
        prs: List[Issue] = []
        for label in self.labels:
            click.secho(f'Fetching labeled PRs: "{label}"', fg="cyan", nl=False)
            new_prs = get_issues_from_labels(
                repo=self.repo,
                access_token=self.access_token,
                label=label,
                prs_only=True,
            )
            click.secho(f' 