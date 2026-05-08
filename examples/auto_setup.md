# Automatic SSH Key Setup for Agents

This guide shows how to use ssh-harness's automatic SSH key generation and injection for agent environments.

## Overview

When agents run in sandboxed/container environments, they often lack SSH keys to connect to remote hosts. ssh-harness can automatically:

1. Generate ED25519 SSH keys
2. Inject public keys to remote hosts (via `sshpass` + `ssh-copy-id`)
3. Support multiple hosts from `.env` configuration

## Prerequisites

1. **sshpass** installed:
   - macOS: `brew install sshpass`
   - Ubuntu/Debian: `apt install sshpass`
   - Other: Check your package manager

2. **Password access** to remote hosts (temporary, for initial setup)

## Method 1: Using `setup_ssh_access()` (Multiple Hosts)

### Step 1: Configure `.env`

```bash
# Single host
SSH_HOST=192.168.1.10
SSH_USER=user1
SSH_PASS_1=password1  # Used for key injection only

# Multiple hosts
SSH_HOST_1=192.168.1.10
SSH_USER_1=user1
SSH_PASS_1=password1

SSH_HOST_2=192.168.1.20
SSH_USER_2=user2
SSH_PASS_2=password2
```

### Step 2: Run setup

```python
from ssh_harness import setup_ssh_access

results = setup_ssh_access()
for r in results:
    status = "✓" if r["success"] else "✗"
    print(f"{status} {r['host']}: {r['message']}")
```

Output:
```
✓ 192.168.1.10: Key injected to user1@192.168.1.10
✓ 192.168.1.20: Key injected to user2@192.168.1.20
```

## Method 2: Using `SSHHarness.setup_keys()` (Single Host)

```python
from ssh_harness import SSHHarness

harness = SSHHarness()  # Reads from SSH_HOST, SSH_USER env vars

# Setup keys for this host
result = harness.setup_keys(password="your_password")
print(result)  # {"success": True/False, "message": "..."}

# Now connect without password
harness.run_command("echo 'Hello from agent!'")
harness.close()
```

## Method 3: Using `SSHKeyManager` Directly

```python
from ssh_harness import SSHKeyManager

manager = SSHKeyManager()

# Generate key (if not exists)
gen_success, gen_msg = manager.generate_key()
print(gen_msg)  # "Generated key: ~/.ssh/id_ed25519"

# Inject to specific host
success, msg = manager.inject_key(
    host="192.168.1.10",
    user="user1",
    password="password1"
)
print(msg)
```

## How It Works

1. **Key Generation**: Creates `~/.ssh/id_ed25519` (ED25519 algorithm)
2. **Key Injection**: Uses `sshpass -p password ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host`
3. **Idempotent**: Safe to run multiple times (won't overwrite existing keys)

## Security Notes

- **Passwords are temporary**: Only used once for `ssh-copy-id`
- **Keys are persistent**: Stored in `~/.ssh/` with proper permissions (600)
- **No password in code**: Use `.env` file (already in `.gitignore`)
- **Revocation**: Remove `~/.ssh/authorized_keys` entry on remote host to revoke access

## Troubleshooting

### sshpass not found
```bash
# macOS
brew install sshpass

# If brew doesn't work, compile from source:
# https://sourceforge.net/projects/sshpass/
```

### Permission denied (publickey)
```python
# Check if key was injected
result = harness.run_command("cat ~/.ssh/authorized_keys")
print(result['output'])
```

### Connection timeout
```python
# Check host is reachable
import subprocess
subprocess.run(["ping", "-c", "3", "your_host"])
```

## Best Practices

1. **Use strong passwords** for initial setup (can be changed after)
2. **Backup keys** if running in ephemeral environments
3. **Test connection** after setup:
   ```python
   harness = SSHHarness()
   print(harness.run_command("whoami"))
   ```
4. **Use multi-host setup** for agent swarms (configure all hosts at once)

---

**Remember**: This is an optional feature. If you already have SSH keys set up, you don't need this. Use it when agents need to bootstrap their own SSH access.
