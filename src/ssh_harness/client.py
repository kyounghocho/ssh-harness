"""
SSH client management for SSH Harness.

Provides persistent SSH connections with automatic reconnection.
"""

import os
import time
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
    
    def _connect(self, retries=3, delay=2):
        """Establish SSH connection with retries and specific error handling."""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        connect_kwargs = {
            "hostname": self.host,
            "port": self.port,
            "username": self.user,
            "timeout": self.timeout,
        }
        
        # Authentication setup
        if self.key_path:
            key_path = os.path.expanduser(self.key_path)
            connect_kwargs["key_filename"] = key_path
            # Don't try agent if key file specified
            connect_kwargs["allow_agent"] = False
            connect_kwargs["look_for_keys"] = False
        elif self.password:
            connect_kwargs["password"] = self.password
            connect_kwargs["allow_agent"] = False
            connect_kwargs["look_for_keys"] = False
        else:
            # No explicit auth → try SSH agent and default keys
            connect_kwargs["allow_agent"] = True
            connect_kwargs["look_for_keys"] = True
        
        last_exception = None
        for attempt in range(1, retries + 1):
            try:
                self.client.connect(**connect_kwargs)
                return  # Success
            except paramiko.AuthenticationException as e:
                raise ConnectionError(
                    f"Authentication failed for {self.user}@{self.host}: "
                    f"Check username/password/key. (Attempt {attempt}/{retries})"
                ) from e
            except paramiko.SSHException as e:
                last_exception = e
                if attempt < retries:
                    time.sleep(delay * attempt)  # Exponential backoff
                    continue
                raise ConnectionError(
                    f"SSH protocol error connecting to {self.host}: {e}"
                ) from e
            except TimeoutError as e:
                last_exception = e
                if attempt < retries:
                    time.sleep(delay * attempt)
                    continue
                raise ConnectionError(
                    f"Connection timed out to {self.host}:{self.port} after {retries} attempts. "
                    f"Check network/firewall."
                ) from e
            except Exception as e:
                last_exception = e
                if attempt < retries:
                    time.sleep(delay * attempt)
                    continue
                raise ConnectionError(
                    f"Failed to connect to {self.host}: {e}"
                ) from e
        
        raise ConnectionError(
            f"Could not connect to {self.host} after {retries} attempts. "
            f"Last error: {last_exception}"
        )
    
    def ensure_connection(self):
        """Ensure connection is alive, reconnect if needed."""
        try:
            if (
                self.client 
                and self.client.get_transport() 
                and self.client.get_transport().is_active()
            ):
                return  # Connection is fine
        except Exception:
            pass  # Transport might be closed
        
        # Need to reconnect
        self._connect()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test SSH connection and return status dict.
        
        Returns:
            Dict with 'success' (bool), 'message' (str), 'host' (str)
        """
        try:
            # Close existing connection if any
            if self.client:
                try:
                    self.client.close()
                except:
                    pass
            
            self.client = None
            self._connect()
            
            # Try a simple command
            result = self.run_command("echo 'connection_test'")
            if result["exit_code"] == 0:
                return {
                    "success": True, 
                    "message": f"Successfully connected to {self.host}:{self.port}",
                    "host": self.host,
                    "port": self.port,
                    "user": self.user,
                }
            return {
                "success": False,
                "message": f"Connected but test command failed (exit code {result['exit_code']})",
                "host": self.host,
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "host": self.host,
            }
    
    def detect_shell(self) -> Dict[str, Any]:
        """Detect remote shell type and return info.
        
        Returns:
            Dict with 'type' (bash/powershell/unknown), 'hint' (str)
        """
        # Try PowerShell detection
        try:
            result = self.run_command("powershell -Command \"$PSVersionTable.PSVersion.Major\" 2>$null")
            if result['exit_code'] == 0 and result['output'].strip().isdigit():
                return {
                    "type": "powershell", 
                    "version": result['output'].strip(),
                    "hint": "Use PowerShell syntax (Get-ChildItem, not ls)"
                }
        except:
            pass
        
        # Check SHELL env var
        result = self.run_command("echo $SHELL")
        shell_path = result['output'].strip()
        if 'bash' in shell_path:
            return {"type": "bash", "path": shell_path, "hint": "Bash syntax (ls, grep, export)"}
        elif 'zsh' in shell_path:
            return {"type": "zsh", "path": shell_path, "hint": "Zsh syntax (similar to bash)"}
        elif 'sh' in shell_path:
            return {"type": "sh", "path": shell_path, "hint": "POSIX sh syntax (limited)"}
        
        # Fallback: check $0
        result = self.run_command("echo $0")
        shell = result['output'].strip()
        if 'bash' in shell:
            return {"type": "bash", "hint": "Bash syntax"}
        elif 'zsh' in shell:
            return {"type": "zsh", "hint": "Zsh syntax"}
        elif 'powershell' in shell.lower() or 'pwsh' in shell.lower():
            return {"type": "powershell", "hint": "PowerShell syntax"}
        
        return {"type": "unknown", "hint": "Assume bash, but verify with detect_shell()"}
    
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
    
    def setup_keys(self, password: Optional[str] = None):
        """
        Setup SSH keys for agent environment.
        
        Args:
            password: Remote password (overrides SSH_PASS_1 env var)
        
        Returns:
            dict: {"success": bool, "message": str}
        """
        from .keys import SSHKeyManager
        
        manager = SSHKeyManager()
        
        # Generate key if needed
        gen_success, gen_msg = manager.generate_key()
        if not gen_success:
            return {"success": False, "message": gen_msg}
        
        # Use password from param or env
        pwd = password or os.getenv("SSH_PASS_1")
        if not pwd:
            return {"success": False, "message": "No password provided. Set SSH_PASS_1 or pass password parameter."}
        
        # Inject key to current host
        success, msg = manager.inject_key(self.host, self.user, pwd)
        return {"success": success, "message": msg}
