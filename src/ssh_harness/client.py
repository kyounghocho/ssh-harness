"""
SSH client management for SSH Harness.

Provides persistent SSH connections with automatic reconnection.
"""

import os
import paramiko
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class SSHHarness:
    """Main SSH harness class for managing remote connections."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        timeout: int = 300,
    ):
        """
        Initialize SSH harness.
        
        Args:
            host: Remote host (default: SSH_HOST env var)
            port: SSH port (default: SSH_PORT env var or 22)
            user: Username (default: SSH_USER env var)
            password: Password auth (default: SSH_PASSWORD env var)
            key_path: Path to SSH key (default: SSH_KEY_PATH env var)
            timeout: Connection timeout in seconds
        """
        self.host = host or os.getenv("SSH_HOST", "localhost")
        self.port = port or int(os.getenv("SSH_PORT", "22"))
        self.user = user or os.getenv("SSH_USER", "root")
        self.password = password or os.getenv("SSH_PASSWORD")
        self.key_path = key_path or os.getenv("SSH_KEY_PATH")
        self.timeout = timeout
        
        self.client = None
        self._connect()
    
    def _connect(self):
        """Establish SSH connection."""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        connect_kwargs = {
            "hostname": self.host,
            "port": self.port,
            "username": self.user,
            "timeout": self.timeout,
        }
        
        if self.key_path:
            key_path = os.path.expanduser(self.key_path)
            connect_kwargs["key_filename"] = key_path
        elif self.password:
            connect_kwargs["password"] = self.password
        
        try:
            self.client.connect(**connect_kwargs)
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            raise
    
    def ensure_connection(self):
        """Ensure connection is alive, reconnect if needed."""
        if not self.client or not self.client.get_transport().is_active():
            self._connect()
    
    def run_command(
        self,
        command: str,
        timeout: Optional[int] = None,
        conda_env: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a command on the remote host.
        
        Args:
            command: Command to execute
            timeout: Override default timeout
            conda_env: (Optional) Conda environment name to activate first.
                       Only works on bash/zsh with conda installed.
        
        Returns:
            Dict with 'output', 'error', 'exit_code'
        """
        self.ensure_connection()
        
        # Only wrap with conda if explicitly requested
        if conda_env:
            command = f"source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null && conda activate {conda_env} 2>/dev/null; {command}"
        
        stdin, stdout, stderr = self.client.exec_command(
            command,
            timeout=timeout or self.timeout,
        )
        
        output = stdout.read().decode("utf-8", errors="ignore")
        error = stderr.read().decode("utf-8", errors="ignore")
        exit_code = stdout.channel.recv_exit_status()
        
        return {
            "output": output,
            "error": error,
            "exit_code": exit_code,
        }
    
    def read_file(
        self,
        remote_path: str,
        max_lines: int = 500,
        offset: int = 1,
    ) -> str:
        """
        Read a remote file.
        
        Args:
            remote_path: Path to remote file
            max_lines: Maximum lines to read
            offset: Starting line (1-indexed)
        
        Returns:
            File content as string
        """
        cmd = f"sed -n '{offset},$ p' {remote_path} | head -n {max_lines}"
        result = self.run_command(cmd)
        return result["output"]
    
    def write_file(self, remote_path: str, content: str) -> bool:
        """
        Write content to a remote file (overwrites).
        
        Args:
            remote_path: Path to remote file
            content: Content to write
        
        Returns:
            True if successful
        """
        escaped = content.replace("'", "'\\''")
        cmd = f"cat > {remote_path} << 'EOF'\n{content}\nEOF"
        result = self.run_command(cmd)
        return result["exit_code"] == 0
    
    def upload(self, local_path: str, remote_path: str) -> bool:
        """Upload a local file to remote host."""
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return True
        except Exception:
            return False
    
    def download(self, remote_path: str, local_path: str) -> bool:
        """Download a file from remote host."""
        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            return True
        except Exception:
            return False
    
    def close(self):
        """Close SSH connection."""
        if self.client:
            self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
