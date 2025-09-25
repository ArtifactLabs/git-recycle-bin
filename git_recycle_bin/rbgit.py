"""RbGit class - Git operations wrapper for artifact repository management."""
import os
import sys
import subprocess
import re
import time
import random
import shutil

from .utils.file import nca_path
from .printer import printer


Path = str
def create_rbgit(src_tree_root: Path, artifact_path: Path, clean: bool = True) -> "RbGit":
    """ Create an RbGit instance from a source tree root and artifact path """
    # Validate inputs
    if not src_tree_root or not os.path.isdir(src_tree_root):
        raise ValueError(f"Invalid src_tree_root: {src_tree_root}")
    if not artifact_path:
        raise ValueError(f"Invalid artifact_path: {artifact_path}")

    # Artifact may reside within or outside source git's root. E.g. under $GITROOT/obj/ or $GITROOT/../obj/
    nca_dir = nca_path(src_tree_root, artifact_path)

    # Place recyclebin-git's root at a stable location, where both source git and artifact can be seen.
    # Placing artifacts here allows for potential merging of artifact commits as paths are fully qualified.
    rbgit_dir = os.path.join(nca_dir, ".rbgit")

    return RbGit(printer, rbgit_dir=rbgit_dir, rbgit_work_tree=nca_dir, clean=clean)

class RbGit:
    """Git operations wrapper for separate artifact repository management."""
    def __init__(self, printer, rbgit_dir=None, rbgit_work_tree=None, clean: bool = True):
        """Initialize RbGit with separate Git environment.
        
        :param printer: Printer instance for logging
        :param rbgit_dir: Git directory path for artifact repository
        :param rbgit_work_tree: Work tree path for artifact repository
        """
        self.printer = printer
        self.rbgit_dir = rbgit_dir if rbgit_dir else os.environ["RBGIT_DIR"]
        self.rbgit_work_tree = (
            rbgit_work_tree if rbgit_work_tree else os.environ["RBGIT_WORK_TREE"]
        )
        self.init_idempotent()

    def _remote_has_branch(self, remote_name: str, branch_name: str) -> bool:
        """Check if remote repository has the specified branch."""
        try:
            # Use ls-remote to check if branch exists without downloading
            # Need to use git environment for this check too
            envcopy = os.environ.copy()
            envcopy["GIT_DIR"] = self.rbgit_dir
            envcopy["GIT_WORK_TREE"] = self.rbgit_work_tree
            
            result = subprocess.run(
                ["git", "ls-remote", "--heads", remote_name, f"refs/heads/{branch_name}"],
                env=envcopy, capture_output=True, text=True, check=False
            )
            
            # Check if we got a successful response with the branch
            has_branch = result.returncode == 0 and len(result.stdout.strip()) > 0
            self.printer.debug(f"Remote branch check: {branch_name} exists={has_branch}", file=sys.stderr)
            return has_branch
            
        except Exception as e:
            self.printer.debug(f"Remote branch check failed: {e}", file=sys.stderr)
            return False  # If we can't check, assume it doesn't exist

    def _is_retryable_error(self, max_retries: int) -> bool:
        """Check if error should be retried based on retry configuration.
        
        Simple approach: if caller wants retries (max_retries > 1), retry all failures.
        If caller doesn't want retries, they set max_retries=1.
        """
        return max_retries > 1

    def _exponential_backoff_sleep(self, attempt: int, max_delay: float = 2.0):
        """Sleep with exponential backoff and jitter."""
        delay = min(0.1 * (2 ** attempt), max_delay)
        jitter = random.uniform(0, delay * 0.1)  # Add 10% jitter
        time.sleep(delay + jitter)

    def cmd(self, *args, input=None, capture_output=True, max_retries=3) -> str:  # pylint: disable=redefined-builtin
        """Execute git command with artifact repository environment.
        
        :param args: Git command arguments
        :param input: Input text for git command
        :param capture_output: Whether to capture command output
        :param max_retries: Maximum number of retry attempts for retryable errors
        :returns: Command stdout output
        """
        cmd_str = " ".join(["git"] + list(args))
        
        for attempt in range(max_retries + 1):
            # Override environment variables
            envcopy = os.environ.copy()
            envcopy["GIT_DIR"] = self.rbgit_dir
            envcopy["GIT_WORK_TREE"] = self.rbgit_work_tree

            # execute the git command with the modified environment
            self.printer.debug("Run:", ["rbgit", *args], file=sys.stderr)
            result = subprocess.run(
                ["git", *args], input=input, env=envcopy,
                capture_output=capture_output, text=True, check=False
            )

            # If command succeeded, return result
            if result.returncode == 0:
                stdout_str: str = result.stdout
                return stdout_str
            
            # Command failed - check if it's retryable
            stderr_msg = result.stderr.strip() if result.stderr else "No error message"
            
            # Special handling for push collisions
            if len(args) > 0 and args[0] == "push" and result.returncode == 1:
                # This could be a push collision - check if it's a git conflict
                # When capture_output=False, stderr is not captured, so check differently
                is_git_conflict = (
                    "fetch first" in stderr_msg or 
                    "remote rejected" in stderr_msg or
                    stderr_msg == "No error message"  # capture_output=False case
                )
                
                if is_git_conflict and len(args) >= 3:  # push remote branch_name
                    branch_name = args[2]
                    remote_name = args[1]
                    
                    self.printer.debug(f"Checking for push collision on {branch_name}", file=sys.stderr)
                    
                    # Check if remote already has this branch (collision confirmation)
                    if self._remote_has_branch(remote_name, branch_name):
                        self.printer.high_level(
                            f"Collision resolved: Remote already has {branch_name}, claiming success",
                            file=sys.stderr
                        )
                        return ""  # Return success - someone else already pushed equivalent artifact
                
                # If we can't resolve the collision, continue with retry logic
            
            # If this is the last attempt or error is not retryable, raise exception
            if attempt == max_retries or not self._is_retryable_error(max_retries):
                raise RuntimeError(
                    f"RbGit command failed: '{cmd_str}' (exit code {result.returncode}): {stderr_msg}"
                )
            
            # Log retry attempt and wait before retrying
            self.printer.debug(f"Retrying command (attempt {attempt + 1}/{max_retries}): {cmd_str}", file=sys.stderr)
            self._exponential_backoff_sleep(attempt)

        # This should never be reached, but just in case
        raise RuntimeError(f"RbGit command exceeded max retries: '{cmd_str}'")

    def init_idempotent(self):
        """Initialize Git repository idempotently."""
        try:
            # Check if inside git work tree
            self.cmd("rev-parse", "--is-inside-work-tree")
        except RuntimeError:
            # Initialize git and configure
            self.cmd("init", "--initial-branch", "master", self.rbgit_work_tree)
            self.cmd("config", "--local", "core.autocrlf", "false")
            self.cmd("config", "--local", "gc.auto", "0")

        # Exclude .rbgit from version control
        with open(f"{self.rbgit_dir}/info/exclude", "w", encoding="utf-8") as file:
            file.write(".rbgit/\n")

    def checkout_orphan_idempotent(self, branch_name: str):
        """Checkout orphan branch idempotently."""
        try:
            # Try to checkout the branch, if it exists
            self.cmd("show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}")
            self.cmd("checkout", branch_name)
        except RuntimeError:
            # If the branch doesn't exist, create it as an orphan
            self.cmd("checkout", "--orphan", branch_name)

    def add(self, binpath: str, force: bool = False) -> bool:
        """Add file to Git staging area.
        
        :param binpath: Path to file to add
        :param force: Whether to force add ignored files
        :returns: True if changes were staged, False otherwise
        """
        if not os.path.exists(binpath):
            raise RuntimeError(f"Artifact '{binpath}' does not exist!")

        changes = False
        if force:
            self.cmd("add", "--force", binpath)
        else:
            self.cmd("add", binpath)

        try:
            # Check if there are any changes staged for the next commit
            self.cmd("diff-index", "--quiet", "--cached", "HEAD")
        except RuntimeError:
            # If diff-index command failed, it means there are changes
            # staged for the next commit
            changes = True

        return changes

    def add_remote_idempotent(self, name: str, url: str):
        """Add Git remote idempotently."""
        try:
            self.cmd("remote", "add", name, url)
        except RuntimeError:
            # If the remote already exists, set its URL
            self.cmd("remote", "set-url", name, url)

    def fetch_only_tags(self, remote: str):
        """Fetch only tags from remote repository."""
        self.cmd("fetch", remote, 'refs/tags/*:refs/tags/*')

    def set_tag(self, tag_name: str, tag_val: str):
        """Set Git tag to specific commit."""
        self.cmd("tag", "--force", tag_name, tag_val)

    def tree_size(self, ref: str = "HEAD") -> int:
        """Calculate accumulated recursively-walked size of tree.
        
        Git stores sparsely and compressed which is not accounted for here.
        
        :param ref: Git reference to analyze
        :returns: Total size in bytes
        """
        lines = self.cmd("ls-tree", "-lr", ref)

        # Parse output:
        # - Split into lines
        # - Extract the 4th column (size) from each line
        # - Convert to int
        # - Sum the sizes
        sizes = [
            int(re.split(r'\s+', line)[3]) for line in lines.splitlines()
        ]
        return sum(sizes)

    def remote_already_has_ref(self, remote: str, ref_name: str):
        """Check if remote repository has the specified reference.
        
        `ls-remote` is pretty forgiving, e.g. either {master, refs/heads/master}
        will be found.
        
        :param remote: Remote repository name
        :param ref_name: Reference name to check
        :returns: True if reference exists on remote
        """
        lines = self.cmd("ls-remote", remote, ref_name)
        return lines != ""

    def fetch_current_tag_value(self, remote: str, tag_name: str):
        """Fetch current value of tag from remote repository.
        
        :param remote: Remote repository name
        :param tag_name: Tag name to fetch
        :returns: SHA of tag or None if not found
        """
        lines = self.cmd("ls-remote", "--tags", remote, tag_name)
        for line in lines.splitlines():
            cols = line.split()
            sha = cols[0]
            # .removeprefix('refs/tags/') is python 3.9+
            tag = (
                cols[1][len('refs/tags/'):]
                if cols[1].startswith('refs/tags/')
                else cols[1]
            )
            if tag == tag_name:
                return sha
        return None

    def fetch_cat_pretty(self, remote: str, ref: str) -> str:
        """Fetch and display content of reference from remote.
        
        :param remote: Remote repository name
        :param ref: Reference to fetch and display
        :returns: Content of the reference
        """
        self.cmd("fetch", remote, ref)
        content = self.cmd("cat-file", "-p", "FETCH_HEAD")
        return content

    def meta_for_commit_refs(self, remote: str):
        lines = self.cmd("ls-remote", "--refs", remote, "refs/artifact/meta-for-commit/*")
        return lines.splitlines()
