"""
High-level command functions for SSH Harness.

These functions provide a simpler API when you don't need a persistent connection.
"""

from .client import SSHHarness

_global_harness = None


def _get_harness(**kwargs) -> SSHHarness:
    """Get or create global harness instance."""
    global _global_harness
    if _global_harness is None:
        _global_harness = SSHHarness(**kwargs)
    return _global_harness


def run_command(command: str, timeout: int = 300, **kwargs) -> dict:
    """Run a command on remote host."""
    harness = _get_harness(**kwargs)
    return harness.run_command(command, timeout=timeout)


def read_file(remote_path: str, max_lines: int = 500, **kwargs) -> str:
    """Read a remote file."""
    harness = _get_harness(**kwargs)
    return harness.read_file(remote_path, max_lines=max_lines)


def write_file(remote_path: str, content: str, **kwargs) -> bool:
    """Write content to remote file."""
    harness = _get_harness(**kwargs)
    return harness.write_file(remote_path, content)


def upload(local_path: str, remote_path: str, **kwargs) -> bool:
    """Upload local file to remote."""
    harness = _get_harness(**kwargs)
    return harness.upload(local_path, remote_path)


def download(remote_path: str, local_path: str, **kwargs) -> bool:
    """Download file from remote."""
    harness = _get_harness(**kwargs)
    return harness.download(remote_path, local_path)


def check_gpu(**kwargs) -> dict:
    """Check GPU status (nvidia-smi)."""
    return run_command("nvidia-smi", **kwargs)
