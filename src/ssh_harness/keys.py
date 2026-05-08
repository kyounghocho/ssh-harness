"""SSH Key management for agents - auto-setup SSH access."""

import os
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class SSHKeyManager:
    """Manages SSH key generation and injection for agent environments."""
    
    def __init__(self, key_path=None):
        self.key_path = Path(key_path or os.path.expanduser("~/.ssh/id_ed25519"))
        self.pub_key_path = self.key_path.with_suffix(".pub")
    
    def generate_key(self):
        """Generate ED25519 key if not exists. Returns (success, message)."""
        if self.key_path.exists():
            return True, f"Key already exists: {self.key_path}"
        
        self.key_path.parent.mkdir(mode=0o700, exist_ok=True)
        
        try:
            subprocess.run([
                "ssh-keygen", "-t", "ed25519", "-f", str(self.key_path),
                "-N", "", "-C", "ssh-harness-agent"
            ], check=True, capture_output=True)
            self.key_path.chmod(0o600)
            self.pub_key_path.chmod(0o644)
            return True, f"Generated key: {self.key_path}"
        except subprocess.CalledProcessError as e:
            return False, f"Key generation failed: {e.stderr.decode()}"
    
    def inject_key(self, host, user, password, retries=2, delay=2):
        """Inject public key to remote host with retry logic."""
        if not self.pub_key_path.exists():
            return False, "Public key not found. Run generate_key() first."
        
        # Check sshpass available
        if subprocess.run(["which", "sshpass"], capture_output=True).returncode != 0:
            return False, "sshpass not installed. Install: brew install sshpass (macOS) or apt install sshpass (Linux)"
        
        last_error = None
        for attempt in range(1, retries + 1):
            try:
                result = subprocess.run([
                    "sshpass", "-p", password, "ssh-copy-id",
                    "-o", "StrictHostKeyChecking=accept-new",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "-i", str(self.pub_key_path),
                    f"{user}@{host}"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return True, f"Key injected to {user}@{host} (attempt {attempt})"
                
                last_error = result.stderr.strip()
                if attempt < retries:
                    time.sleep(delay * attempt)
                    continue
                return False, f"ssh-copy-id failed: {last_error}"
                
            except subprocess.TimeoutExpired:
                last_error = "Timeout during key injection"
                if attempt < retries:
                    time.sleep(delay * attempt)
                    continue
                return False, f"Timeout after {retries} attempts"
                
            except Exception as e:
                last_error = str(e)
                if attempt < retries:
                    time.sleep(delay * attempt)
                    continue
                return False, f"Unexpected error: {last_error}"
        
        return False, f"Failed after {retries} attempts: {last_error}"
    
    def setup_all_from_env(self):
        """Read multiple hosts from .env and setup keys for each."""
        results = []
        i = 1
        
        while True:
            host = os.getenv(f"SSH_HOST_{i}")
            if not host:
                break
            
            user = os.getenv(f"SSH_USER_{i}", "root")
            password = os.getenv(f"SSH_PASS_{i}")
            
            if not password:
                results.append({"host": host, "success": False, "message": "No password in .env"})
                i += 1
                continue
            
            # Generate key once
            if i == 1:
                gen_success, gen_msg = self.generate_key()
                if not gen_success:
                    return [{"host": host, "success": False, "message": gen_msg}]
            
            # Inject to this host
            success, msg = self.inject_key(host, user, password)
            results.append({"host": host, "success": success, "message": msg})
            i += 1
        
        return results


def setup_ssh_access():
    """Convenience function for agents to auto-setup SSH access."""
    manager = SSHKeyManager()
    return manager.setup_all_from_env()
