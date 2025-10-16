# src/utils/github_utils.py

import git
import os
import tempfile

def clone_repo(repo_url: str, clonedir: str = None) -> str:
    """
    Clone a GitHub repository to a local directory.

    Args:
        repo_url (str): URL of the GitHub repository
        clonedir (str, optional): Path to clone the repo into.
            If None, will create a temp directory.

    Returns:
        str: Path to the cloned repository
    """
    if clonedir is None:
        clonedir = tempfile.mkdtemp(prefix="repo_clone_")

    if not os.path.exists(clonedir):
        os.makedirs(clonedir)

    git.Repo.clone_from(repo_url, clonedir)
    return clonedir
