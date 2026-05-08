"""
Utility functions for SSH Harness.
"""

from .client import SSHHarness


def test_connection(**kwargs) -> bool:
    """Test SSH connection."""
    try:
        result = run_command("echo 'Connection test'", **kwargs)
        return result["exit_code"] == 0
    except Exception:
        return False


def get_remote_os(**kwargs) -> str:
    """Get remote OS information."""
    result = run_command("uname -a", **kwargs)
    return result["output"].strip()


def get_remote_python_version(**kwargs) -> str:
    """Get remote Python version."""
    result = run_command("python --version", **kwargs)
    return result["output"].strip()


if __name__ == "__main__":
    print("Testing SSH Harness...")
    if test_connection():
        print("✓ Connection successful!")
        print(f"Remote OS: {get_remote_os()}")
        print(f"Python: {get_remote_python_version()}")
    else:
        print("✗ Connection failed")
