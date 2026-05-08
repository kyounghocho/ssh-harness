"""SSH Key management for agents - auto-setup SSH access."""

import os
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
    
    def inject_key(self, host, user, password):
        """Inject public key to remote host using sshpass + ssh-copy-id."""
        if not self.pub_key_path.exists():
            return False, "Public key not found. Run generate_key() first."
        
        # Check sshpass available
        if subprocess.run(["which", "sshpass"], capture_output=True).returncode != 0:
            return False, "sshpass not installed. Install: brew install sshpass (macOS) or apt install sshpass (Linux)"
        
        try:
            result = subprocess.run([
                "sshpass", "-p", password, "ssh-copy-id",
                "-o", "StrictHostKeyChecking=accept-new",  # 안전: 새 호스트만 자동 수락
                "-o", "UserKnownHostsFile=/dev/null",     # 임시: KnownHosts 무시
                "-i", str(self.pub_key_path),
                f"{user}@{host}"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, f"Key injected to {user}@{host}"
            return False, f"ssh-copy-id failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Timeout during key injection"
    
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
