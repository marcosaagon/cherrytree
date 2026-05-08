"""Custom exceptions for the CherryTree application.

This module defines the exception hierarchy used throughout the cherrytree
package to provide meaningful error messages and structured error handling.
"""


class CherryTreeError(Exception):
    """Base exception class for all CherryTree errors."""

    def __init__(self, message: str = "", *args, **kwargs):
        self.message = message
        super().__init__(message, *args, **kwargs)

    def __str__(self) -> str:
        return self.message


class BranchNotFoundError(CherryTreeError):
    """Raised when a specified branch cannot be found in the repository."""

    def __init__(self, branch_name: str):
        self.branch_name = branch_name
        super().__init__(f"Branch '{branch_name}' not found in the repository.")


class CommitNotFoundError(CherryTreeError):
    """Raised when a specified commit SHA cannot be found."""

    def __init__(self, commit_sha: str):
        self.commit_sha = commit_sha
        super().__init__(f"Commit '{commit_sha}' not found in the repository.")


class CherryPickError(CherryTreeError):
    """Raised when a cherry-pick operation fails.

    This can occur due to merge conflicts or other git-level issues
    encountered during the cherry-pick process.
    """

    def __init__(self, commit_sha: str, reason: str = ""):
        self.commit_sha = commit_sha
        self.reason = reason
        message = f"Cherry-pick failed for commit '{commit_sha}'."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(message)


class BakeError(CherryTreeError):
    """Raised when the bake (branch creation/push) operation fails."""

    def __init__(self, branch_name: str, reason: str = ""):
        self.branch_name = branch_name
        self.reason = reason
        message = f"Bake operation failed for branch '{branch_name}'."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(message)


class InvalidConfigError(CherryTreeError):
    """Raised when the CherryTree configuration is invalid or missing required fields."""

    def __init__(self, field: str = "", reason: str = ""):
        self.field = field
        self.reason = reason
        if field:
            message = f"Invalid configuration for field '{field}'."
        else:
            message = "Invalid CherryTree configuration."
        if reason:
            message += f" {reason}"
        super().__init__(message)


class RepositoryError(CherryTreeError):
    """Raised when there is a problem accessing or interacting with the git repository.

    Note: repo_path should be an absolute path when possible, to make the error
    message easier to debug when running from different working directories.
    """

    def __init__(self, repo_path: str = "", reason: str = ""):
        self.repo_path = repo_path
        self.reason = reason
        if repo_path:
            message = f"Repository error at '{repo_path}'."
        else:
            message = "Repository error."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(message)
