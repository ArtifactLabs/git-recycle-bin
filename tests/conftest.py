import subprocess
import pytest
from managers import git_user_info

@pytest.fixture
def temp_git_setup(tmpdir):
    # Create temporary directories
    local_repo = tmpdir.mkdir("local_repo")
    remote_repo = tmpdir.mkdir("remote_repo")
    artifact_repo = tmpdir.mkdir("artifact_repo")

    # Initialize the 'remote' repository
    subprocess.run(['git', 'init', '--bare'], cwd=remote_repo, check=True)

    # Initialize the local repository
    subprocess.run(['git', 'init'], cwd=local_repo, check=True)

    # Initialize the artifact repository
    subprocess.run(['git', 'init', '--bare'], cwd=artifact_repo, check=True)

    # Add the remote
    remote_url = f"file://{remote_repo}"
    subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=local_repo, check=True)

    # add some files to the local repository
    local_file = local_repo.join("example.txt")
    local_file.write("This is a test file.")
    with git_user_info():
        subprocess.run(['git', 'add', 'example.txt'], cwd=local_repo, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=local_repo, check=True)
        subprocess.run(['git', 'push', 'origin', 'master'], cwd=local_repo, check=True)

    # Return both directories as a tuple to be used in tests
    yield (local_repo, remote_repo, artifact_repo, [(local_file, "example.txt")])


