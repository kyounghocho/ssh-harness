# Linux CUDA LLM Domain Skill

Guide for agents connecting to **Linux servers/workstations** with **NVIDIA GPU + CUDA** for running **LLMs** (Large Language Models).

## Connection

- **Host type**: Linux (Ubuntu, Debian, CentOS, etc.)
- **Shell**: bash (default) or zsh
- **GPU**: NVIDIA (CUDA capable)
- **Architecture**: x86_64 (Intel/AMD) or ARM64 (aarch64)

## Quick Check

```python
from ssh_harness import SSHHarness

harness = SSHHarness()  # Assumes .env configured for Linux host

# Check if NVIDIA GPU present
result = harness.run_command("nvidia-smi")
if result['exit_code'] == 0:
    print("CUDA GPU detected")
    print(result['output'][:500])  # first 500 chars

# Check CUDA version
result = harness.run_command("nvcc --version")
print(result['output'])

# Check PyTorch with CUDA
result = harness.run_command("python -c 'import torch; print(torch.cuda.is_available())'")
print(result['output'])

harness.close()
```

## Common LLM Commands (bash)

### 1. GPU Status
```bash
nvidia-smi
# Monitor continuously
watch -n 1 nvidia-smi
```

### 2. CUDA Version
```bash
nvcc --version
# or
cat /usr/local/cuda/version.txt
```

### 3. PyTorch with CUDA
```bash
python -c "import torch; print(torch.__version__, torch.cuda.get_device_name(0))"
```

### 4. Run LLM Inference (example with transformers)
```bash
python -c "from transformers import pipeline; pipe = pipeline('text-generation', model='gpt2', device=0); print(pipe('Hello')[0]['generated_text'])"
```

### 5. Download Models (Hugging Face)
```bash
huggingface-cli download gpt2 --local-dir ./models/gpt2
# or git lfs
git lfs install
git clone https://huggingface.co/gpt2
```

### 6. Monitor Training
```bash
# In another SSH session or use nohup
nohup python train.py > train.log 2>&1 &
tail -f train.log
```

## Environment Setup

### Install CUDA Toolkit
- Ubuntu: `sudo apt install nvidia-cuda-toolkit`
- Or download from NVIDIA website for your distro.

### Install PyTorch with CUDA
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Install Transformers / LLM libraries
```bash
pip install transformers accelerate bitsandbytes  # for quantization
```

### Conda Environment (optional but recommended)
```bash
conda create -n llm-env python=3.10
conda activate llm-env
pip install torch transformers
```

## Troubleshooting

### "nvidia-smi not found"
```bash
# Check if GPU driver installed
lspci | grep -i nvidia
# Install drivers (Ubuntu)
sudo ubuntu-drivers autoinstall
```

### CUDA not available in PyTorch
```bash
# Check CUDA version
nvcc --version
# Reinstall PyTorch with correct CUDA version
pip install torch --index-url https://download.pytorch.org/whl/cu121  # for CUDA 12.1
```

### Out of memory (OOM)
- Reduce batch size, use quantization (`bitsandbytes`), or use smaller model.
- Check GPU memory: `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`

### SSH connection issues
- Check firewall: `sudo ufw status`
- Verify SSH service: `sudo systemctl status sshd`

## Example Workflow: Run LLM Inference

```python
from ssh_harness import SSHHarness

harness = SSHHarness()

# 1. Check GPU
result = harness.run_command("nvidia-smi")
if result['exit_code'] != 0:
    print("No GPU or nvidia-smi not in PATH")

# 2. Run a simple inference
result = harness.run_command(
    "python -c \"import torch; "
    "model = torch.nn.Linear(10, 10).cuda(); "
    "print('CUDA works')\""
)
print(result['output'])

# 3. Run actual LLM (if model downloaded)
# result = harness.run_command("python inference.py --model gpt2")

harness.close()
```

## Notes for Agents

1. **Default shell is bash**, but some systems use zsh. Use `detect_shell()`.
2. **Paths use forward slash** `/home/user/...`
3. **CUDA toolkit and PyTorch must match versions** (e.g., CUDA 12.1 → PyTorch with cu121).
4. **Conda activation** is optional but recommended for isolation. See `SKILL.md` for conda usage.
5. **Use `nvidia-smi`** to verify GPU and CUDA availability.

---

**Remember**: If the remote host is Linux, `detect_shell()` should return `'bash'` or `'zsh'`. Use bash syntax from `SKILL.md` shell compatibility table.
