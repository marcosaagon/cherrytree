"""Core CherryTree module.

Provides the main CherryTree class that orchestrates cherry-picking
commits across branches using the configured strategy.
"""

import logging
import subprocess
from typing import List, Optional

from cherrytree.branch import CherryTreeBranch

logger = logging.getLogger(__name__)


class CherryTree:
    """Orchestrates cherry-picking of commits across multiple branches.

    This class manages the process of identifying commits on a source branch
    and applying them to one or more target branches.

    Attributes:
        source_branch: The branch from which commits are cherry-picked.
        target_branches: List of branches to apply the commits to.
        dry_run: If True, simulate the cherry-pick without making changes.
        auto_push: If True, push changes to remote after cherry-picking.
    """

    def __init__(
        self,
        source_branch: str,
        target_branches: List[str],
        dry_run: bool = False,
        auto_push: bool = False,
        remote: str = "origin",
    ) -> None:
        """Initialize CherryTree.

        Args:
            source_branch: Name of the branch to cherry-pick from.
            target_branches: List of branch names to apply commits to.
            dry_run: If True, do not make any actual changes.
            auto_push: If True, push branches after cherry-picking.
            remote: Name of the git remote to use.
        """
        self.source_branch = CherryTreeBranch(source_branch)
        self.target_branches = [CherryTreeBranch(b) for b in target_branches]
        self.dry_run = dry_run
        self.auto_push = auto_push
        self.remote = remote

    def get_commits(self, since: Optional[str] = None) -> List[str]:
        """Retrieve commit SHAs from the source branch.

        Args:
            since: Optional commit SHA or ref to use as the starting point.
                   If None, returns all commits on the source branch.

        Returns:
            A list of commit SHAs in chronological order (oldest first).
        """
        cmd = ["git", "log", "--pretty=format:%H"]
        if since:
            cmd.append(f"{since}..{self.source_branch.name}")
        else:
            cmd.append(self.source_branch.name)

        logger.debug("Running: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = result.stdout.strip().splitlines()
        # Reverse so oldest commit comes first
        return list(reversed(commits))

    def cherry_pick(self, commit_sha: str, target: CherryTreeBranch) -> bool:
        """Apply a single commit to a target branch.

        Args:
            commit_sha: The SHA of the commit to cherry-pick.
            target: The target branch to apply the commit to.

        Returns:
            True if the cherry-pick succeeded, False otherwise.
        """
        if self.dry_run:
            logger.info(
                "[dry-run] Would cherry-pick %s onto %s", commit_sha[:8], target.name
            )
            return True

        try:
            # Checkout the target branch
            subprocess.run(
                ["git", "checkout", target.name], capture_output=True, check=True
            )
            # Perform the cherry-pick
            subprocess.run(
                ["git", "cherry-pick", commit_sha], capture_output=True, check=True
            )
            logger.info("Cherry-picked %s onto %s", commit_sha[:8], target.name)
            return True
        except subprocess.CalledProcessError as exc:
            logger.error(
                "Failed to cherry-pick %s onto %s: %s",
                commit_sha[:8],
                target.name,
                exc.stderr.decode() if exc.stderr else str(exc),
            )
            # Abort the failed cherry-pick to restore clean state
            subprocess.run(["git", "cherry-pick", "--abort"], capture_output=True)
            return False

    def bake(self, since: Optional[str] = None) -> dict:
        """Execute the cherry-pick process across all target branches.

        Args:
            since: Optional ref to use as the starting point for commit selection.

        Returns:
            A summary dict mapping branch names to lists of applied commit SHAs.
        """
        commits = self.get_commits(since=since)
        if not commits:
            logger.info("No commits found on %s", self.source_branch.name)
            return {}

        logger.info(
            "Found %d commit(s) to cherry-pick onto %d branch(es)",
            len(commits),
            len(self.target_branches),
        )

        summary: dict = {branch.name: [] for branch in self.target_branches}

        for target in self.target_branches:
            for sha in commits:
                success = self.cherry_pick(sha, target)
                if success:
                    summary[target.name].append(sha)

            if self.auto_push and not self.dry_run and summary[target.name]:
                logger.info("Pushing %s to %s", target.name, self.remote)
                subprocess.run(
                    ["git", "push", self.remote, target.name],
                    capture_output=True,
                    check=True,
                )

        return summary
