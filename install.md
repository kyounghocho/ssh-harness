# Install Guide - SSH Harness

This guide will help you set up SSH Harness for the first time.

## Prerequisites

- Python 3.8+
- SSH access to your remote host
- Either SSH key or password authentication

## Step 1: Install SSH Harness

### Option A: Install from PyPI (once published)

```bash
pip install ssh-harness
```

### Option B: Install from source

```bash
git clone https://github.com/kyounghocho/ssh-harness.git
cd ssh-harness
pip install -e .
```

## Step 2: Configure Connection

Create a `.env` file in your working directory:

```bash
cp .env.example .env
```

Edit `.env` with your remote host details:

```bash
SSH_HOST=your_host_ip
SSH_PORT=22
SSH_USER=your_username
SSH_KEY_PATH=~/.ssh/id_rsa
# OR use password:
# SSH_PASSWORD=your_password
```

## Step 3: Test Connection

Create a test script:

```python
from ssh_harness import SSHHarness

harness = SSHHarness()

# Test connection
result = harness.run_command("echo 'Hello from SSH Harness!'")
print(result['output'])

# Check remote OS
result = harness.run_command("uname -a")
print("Remote OS:", result['output'])

harness.close()
```

Run it:

```bash
python test_ssh.py
```

You should see:

```
✓ Connected to user@host:22
Hello from SSH Harness!
Remote OS: Linux ...
```

## Step 4: (Optional) Configure Conda Environment

If your remote host uses Conda (e.g., for ML workloads), set the conda environment:

```bash
SSH_CONDA_ENV=your_conda_env  # e.g., base, pytorch, ocr_final
```

This will automatically activate the conda environment before each command.

## Step 5: Using with LLM Agents

### For Hermes Agent

If you're using Hermes Agent, the `ssh-harness` skill is already available. Just load it:

```python
# In Hermes Agent
skill_view(name='ssh-harness')
```

### For Other Agents

Agents can use SSH Harness by importing it in Python scripts:

```python
from ssh_harness import run_command, read_file, write_file

# Run command
result = run_command("ls -la")
print(result['output'])

# Read file
content = read_file("/etc/hosts")
print(content)
```

## Troubleshooting

### Connection Refused

```bash
# Check if SSH is running on remote host
ssh user@host "systemctl status ssh"

# Check firewall
ssh user@host "sudo ufw status"
```

### Host Key Verification Failed

```bash
# Remove old host key
ssh-keygen -R "host:port"

# Or disable strict checking (not recommended for production)
# SSHHARNESS_IGNORE_HOST_KEY=true
```

### Permission Denied (Publickey)

```bash
# Check key permissions
chmod 600 ~/.ssh/id_rsa

# Test SSH connection manually
ssh -i ~/.ssh/id_rsa user@host
```

### Conda Environment Not Found

```bash
# Check available conda environments
ssh user@host "conda env list"

# Update SSH_CONDA_ENV in .env
```

## Next Steps

- Read [SKILL.md](SKILL.md) for detailed usage instructions
- Check [agent-workspace/](agent-workspace/) for agent-editable helpers
- See [examples/](examples/) (TODO) for common use cases

## Uninstall

```bash
pip uninstall ssh-harness
```

---

**Need help?** Open an issue: https://github.com/kyounghocho/ssh-harness/issues
