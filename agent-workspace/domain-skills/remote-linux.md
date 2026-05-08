# Remote Linux Host Skill

This playbook covers controlling a general remote Linux host.

## Connection Details

- **Host**: your_host_ip
- **Port**: 22 (or your SSH port)
- **User**: your_username
- **Environment**: Linux

## Setup

1. Create `.env` file:

```bash
SSH_HOST=your_host_ip
SSH_PORT=22
SSH_USER=your_username
SSH_KEY_PATH=~/.ssh/id_rsa
```

# Optional: See examples/conda_usage.md for Conda usage

2. Test connection:

```python
from ssh_harness import run_command, check_gpu

# Test connection
result = run_command("uptime")
print("System uptime:", result['output'])

# Check GPU (if available)
result = check_gpu()
print("GPU Status:\n", result['output'])
```

## Common Tasks

### Check System Status

```python
from ssh_harness import run_command

# Check uptime
result = run_command("uptime")
print(result['output'])

# Check disk usage
result = run_command("df -h /")
print(result['output'])

# Check memory
result = run_command("free -h")
print(result['output'])
```

### (Optional) Run Python Script in Conda Env

> **Note**: Conda activation only works on bash/zsh. See [examples/conda_usage.md](examples/conda_usage.md).

```python
result = run_command("python my_script.py", conda_env="your_conda_env")
print(result['output'])
```

### Monitor Training

```python
from agent_helpers import check_training_progress

progress = check_training_progress("/path/to/training.log")
if progress:
    print(f"Epoch: {progress['epoch']}, Loss: {progress['loss']}")
    print(f"Status: {progress['status']}")
```

### Download Results

```python
from ssh_harness import download

download("/remote/path/results.json", "./results.json")
print("✓ Results downloaded")
```

## Tips

- For large file transfers, consider using `rsync` via `run_command()`
- Always check `exit_code` for critical operations

## Troubleshooting

### Connection Refused

```bash
# On remote machine, check SSH service:
systemctl status ssh
```

### Host Key Changed

```bash
ssh-keygen -R "[your_host_ip]:port"
```

### (Optional) Conda Env Not Found

> **Note**: Only applicable if using Conda on bash/zsh.

```python
result = run_command("conda env list")
print(result['output'])
```
