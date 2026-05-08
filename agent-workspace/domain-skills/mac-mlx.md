# Mac MLX Domain Skill

Guide for agents connecting to **Apple Silicon Mac** hosts running **MLX** (machine learning framework).

## Connection

- **Host type**: macOS (Apple Silicon: M1/M2/M3/M4)
- **Shell**: Usually `zsh` (default) or `bash`
- **Architecture**: ARM64 (aarch64)
- **GPU**: Metal Performance Shaders (no nvidia-smi)

## Quick Check

```python
from ssh_harness import SSHHarness

harness = SSHHarness()  # Assumes .env configured for Mac host

# Check if MLX installed
result = harness.run_command("python -c 'import mlx; print(mlx.__version__)'")
if result['exit_code'] == 0:
    print(f"MLX version: {result['output'].strip()}")

# Check Metal GPU info (no nvidia-smi on Mac!)
result = harness.run_command("system_profiler SPDisplaysDataType | grep 'Chipset Model'")
print(result['output'])

harness.close()
```

## Common MLX Commands

### 1. Check Device Info
```bash
python -c "import mlx.core as mx; print(mx.metal.device_info())"
```

### 2. List Available Models
```bash
ls -la ~/.mlx/models/
```

### 3. Run MLX Model
```bash
python -m mlx_lm.generate --model ~/.mlx/models/mistral-7b --prompt "Hello"
```

### 4. Check Running Processes (Metal GPU)
```bash
# No nvidia-smi, use powermetrics or top
sudo powermetrics --samplers gpu_power -i1 -n1
```

### 5. Monitor Memory Usage
```bash
# System memory (unified memory on Apple Silicon)
vm_stat
```

## Environment Setup

### Install MLX
```bash
pip install mlx mlx-lm
```

### Conda Note
- MLX **only works on Apple Silicon** (no Linux/Windows support)
- Conda env optional but recommended:
  ```bash
  conda create -n mlx-env python=3.10
  conda activate mlx-env
  pip install mlx
  ```

## Troubleshooting

### "mlx not found"
```bash
# Check Python path
which python
python -c "import sys; print(sys.path)"

# Reinstall if needed
pip install --force-reinstall mlx
```

### Metal GPU not detected
```bash
# Verify it's Apple Silicon, not Intel Mac
sysctl -n machdep.cpu.brand_string
# Should show: Apple M1/M2/M3/M4

# Check if Metal is available
python -c "import mlx.core as mx; print(mx.metal.is_available())"
```

### Slow performance
- Ensure using **MLX-optimized models** (not standard PyTorch models)
- Check if running on CPU fallback: `mx.metal.is_available()` should return `True`
- Monitor with: `sudo powermetrics --samplers gpu_power`

## Example Workflow: Run LLM on Mac

```python
from ssh_harness import SSHHarness

harness = SSHHarness()

# 1. Check MLX
result = harness.run_command("python -c 'import mlx; print(mlx.__version__)'")
if result['exit_code'] != 0:
    print("MLX not installed")
    harness.run_command("pip install mlx mlx-lm")

# 2. Download model (if not exists)
result = harness.run_command("test -d ~/.mlx/models/mistral-7b || mlx-lm.download --model mistralai/Mistral-7B-v0.1")
if result['exit_code'] == 0:
    print("Model ready")

# 3. Run inference
result = harness.run_command(
    "python -m mlx_lm.generate --model ~/.mlx/models/mistral-7b --prompt 'Write a hello world in Python'"
)
print(result['output'])

harness.close()
```

## Notes for Agents

1. **No nvidia-smi**: Use `system_profiler SPDisplaysDataType` or `powermetrics` for GPU info
2. **Unified memory**: macOS shares memory between CPU/GPU, check with `vm_stat`
3. **Shell**: Default is zsh on modern macOS, but commands are bash-compatible
4. **Architecture**: ARM64, not x86_64 – be careful with binary downloads
5. **MLX-only**: Don't try to run MLX on non-Apple Silicon hosts

---

**Remember**: If the remote host is not Apple Silicon, MLX will not work. Use `uname -m` to verify (should return `arm64`).
