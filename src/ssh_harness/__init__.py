"""
SSH Harness - Thin SSH control tool for LLM agents.

A thin, editable SSH wrapper that enables LLMs to control remote hosts programmatically.
"""

from .client import SSHHarness
from .commands import run_command, read_file, write_file, upload, download
from .keys import SSHKeyManager, setup_ssh_access

__version__ = "0.1.0"
__author__ = "kyounghocho"

__all__ = [
    "SSHHarness",
    "run_command",
    "read_file",
    "write_file",
    "upload",
    "download",
    "SSHKeyManager",
    "setup_ssh_access",
]
