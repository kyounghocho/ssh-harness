# Conda Usage Example

This example shows how to use SSH Harness with Conda environments (for ML workloads, etc.).

> **Note**: Conda activation only works on **bash/zsh** remote hosts with Conda installed. Windows PowerShell or other shells may not support `source` and `conda activate`.

## Prerequisites

1. Remote host has Conda installed (e.g., Miniconda/Anaconda)
2. Remote shell is bash or zsh
3. You know the Conda environment name

## Setup

Edit `.env` (optional):

```bash
SSH_CONDA_ENV=your_conda_env  # Optional: default conda env (not used automatically)
```

> **Important**: Even if you set `SSH_CONDA_ENV`, it is **NOT** used by default. You must explicitly pass `conda_env` parameter to `run_command()`.

## Usage

### Method 1: Pass `conda_env` to `run_command()`

```python
from ssh_harness import run_command

# Activate 'my_env' and run command
result = run_command("python train.py", conda_env="my_env")
print(result['output'])
```

### Method 2: Using SSHHarness instance

```python
from ssh_harness import SSHHarness

harness = SSHHarness()

# Run with conda env
result = harness.run_command("python --version", conda_env="my_env")
print(result['output'])

harness.close()
```

## How it works

When you pass `conda_env`, the command is wrapped like:

```bash
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null && conda activate my_env 2>/dev/null; your_command
```

- `2>/dev/null` suppresses errors if Conda is not found
- If Conda is not installed, the command still runs (without activation)

## Common Conda Environments

- `base`: Default Conda environment
- `pytorch`: For PyTorch workloads
- `tensorflow`: For TensorFlow workloads
- `ocr_final`: Custom environment for OCR tasks

## Troubleshooting

### Conda not found

```python
result = run_command("which conda", conda_env="my_env")
print(result['output'])  # Should show path to conda
```

### Activation fails silently

Check remote shell:

```python
result = run_command("echo $SHELL")
print(result['output'])  # Should be /bin/bash or /bin/zsh
```

### Remote Windows hosts (OpenSSH)

If the remote host is Windows (not Linux/WSL), Conda activation via `source` may not work because Windows OpenSSH uses `cmd.exe` or PowerShell by default.

**Option 1: Use full path to python in Conda env (recommended for Windows remote)**
```python
# Windows example - use full path to env's python
result = run_command("C:\\Users\\user\\miniconda3\\envs\\my_env\\python.exe script.py")
```

**Option 2: Switch remote shell to bash (if using WSL on Windows)**
```python
# If remote is Windows but you have WSL, connect to WSL instead
# Configure SSH to WSL, then conda activation works as normal
result = run_command("python script.py", conda_env="my_env")
```

> **Note**: If your remote host is Linux (most common), Conda activation works regardless of whether your local machine uses PowerShell, Terminal, or any other client.

## Best Practices

1. **Don't assume Conda is available** - always check first
2. **Use explicit `conda_env` parameter** - never rely on global state
3. **Consider alternatives** - for Windows, use full paths to executables
4. **Test activation** - verify with simple command first

---

**Remember**: SSH Harness is primarily a thin SSH wrapper. Conda support is optional and secondary.
