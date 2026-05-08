---
name: ssh-harness
description: "ssh-harness: Thin SSH control tool for LLM agents - execute commands, read/write files, upload/download"
---

# SSH Harness - LLM Agent Skill

## Overview

SSH Harness provides a simple Python API for LLM agents to control remote hosts via SSH. It's designed to be:
- **Thin**: Direct SSH commands, minimal abstraction
- **Self-improving**: Agents can write missing helpers
- **Agent-friendly**: Simple, documented API

## Quick Start

### Basic Usage (with Persistent Connection)

```python
from ssh_harness import SSHHarness

# Initialize (reads from .env or pass parameters)
harness = SSHHarness()

# Run commands
result = harness.run_command("nvidia-smi")
print(result['output'])

# Read files
content = harness.read_file("/path/to/file.txt")
print(content)

# Write files
harness.write_file("/tmp/test.txt", "Hello!")

# Upload/Download
harness.upload("local.txt", "/remote/path.txt")
harness.download("/remote/path.txt", "local_copy.txt")

harness.close()
```

### Simplified API (Stateless)

```python
from ssh_harness import run_command, read_file, write_file, upload, download

# These use a global harness instance
result = run_command("ls -la")
content = read_file("/etc/hosts")
write_file("/tmp/test.txt", "Content")
upload("local.txt", "/remote/file.txt")
download("/remote/file.txt", "local.txt")
```

## Core Functions

### run_command(command, timeout=300, conda_env=None)

Execute a command on the remote host.

**Parameters:**
- `command` (str): Command to execute
- `timeout` (int): Timeout in seconds (default: 300)
- `conda_env` (str, optional): Override conda environment

**Returns:**
```python
{
    "output": "stdout content",
    "error": "stderr content",
    "exit_code": 0
}
```

**Example:**
```python
result = run_command("python --version")
if result['exit_code'] == 0:
    print("Python:", result['output'])
else:
    print("Error:", result['error'])
```

### read_file(remote_path, max_lines=500, offset=1)

Read a remote file.

**Parameters:**
- `remote_path` (str): Path to remote file
- `max_lines` (int): Maximum lines to read (default: 500)
- `offset` (int): Starting line number (1-indexed, default: 1)

**Returns:**
- String content of the file

### write_file(remote_path, content)

Write content to a remote file (overwrites).

**Parameters:**
- `remote_path` (str): Path to remote file
- `content` (str): Content to write

**Returns:**
- True if successful, False otherwise

### upload(local_path, remote_path)

Upload a local file to remote host.

### download(remote_path, local_path)

Download a file from remote host.

### check_gpu()

Check GPU status using `nvidia-smi`.

## Advanced Usage

### Using Context Manager

```python
with SSHHarness() as harness:
    result = harness.run_command("uptime")
    print(result['output'])
```

### Custom Connection Parameters

```python
harness = SSHHarness(
    host="your_host",
    port=22,
    user="your_user",
    key_path="~/.ssh/id_rsa",
    conda_env="your_conda_env",
)
```

## Agent Workflow Example

```python
# Agent wants to check GPU status
result = run_command("nvidia-smi")
if "GPU" in result['output']:
    print("✓ GPU detected")
else:
    print("✗ GPU not found")

# Agent wants to read a log file
log = read_file("/var/log/app.log", max_lines=50)
print("Recent log entries:")
print(log)

# Agent wants to download results
download("/remote/results.json", "./results.json")
print("✓ Results downloaded")
```

## Writing Custom Helpers

Agents can write custom helpers in `agent-workspace/agent_helpers.py`:

```python
# agent-workspace/agent_helpers.py

def get_gpu_temp():
    """Get GPU temperature (custom helper)."""
    from ssh_harness import run_command
    result = run_command("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader")
    return result['output'].strip()

def check_training_done():
    """Check if training is complete."""
    from ssh_harness import read_file
    log = read_file("/path/to/training.log", max_lines=10)
    return "complete" in log.lower()
```

Then use them:

```python
from agent_helpers import get_gpu_temp, check_training_done

temp = get_gpu_temp()
print(f"GPU Temp: {temp}°C")

if check_training_done():
    print("Training finished!")
```

## Domain Skills

See `agent-workspace/domain-skills/` for host-specific playbooks:

- `remote-linux.md`: Controlling a general remote Linux host
- (Agents can create more!)

## Best Practices

1. **Always check exit codes** when running critical commands
2. **Use timeouts** for long-running commands
3. **Read files in chunks** (max_lines) for large files
4. **Close connections** when done (or use context manager)
5. **Let agents write helpers** instead of repeating complex logic

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SSH_HOST` | Remote host | localhost |
| `SSH_PORT` | SSH port | 22 |
| `SSH_USER` | Username | root |
| `SSH_KEY_PATH` | Path to SSH key | - |
| `SSH_PASSWORD` | Password (alternative to key) | - |
| `SSH_TIMEOUT` | Connection timeout | 300 |
| `SSH_CONDA_ENV` | Conda env to auto-activate | - |

## License

MIT License - see [LICENSE](LICENSE) file.

---

**Inspired by**: [browser-use/browser-harness](https://github.com/browser-use/browser-harness) ♞
