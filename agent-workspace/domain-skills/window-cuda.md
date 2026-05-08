# Windows CUDA LLM Domain Skill

Guide for agents connecting to **Windows Server/Workstation** with **NVIDIA GPU + CUDA** for running **LLMs** (Large Language Models).

## Connection

- **Host type**: Windows 10/11 or Server 2019/2022 with NVIDIA GPU
- **Shell**: PowerShell (default) or cmd.exe
- **GPU**: NVIDIA (CUDA capable)
- **Architecture**: x86_64

## Quick Check

```python
from ssh_harness import SSHHarness

harness = SSHHarness()  # Assumes .env configured for Windows host

# Check if NVIDIA GPU present
result = harness.run_command("nvidia-smi")
if result['exit_code'] == 0:
    print("CUDA GPU detected")
    print(result['output'][:500])  # first 500 chars

# Check Python and CUDA version
result = harness.run_command("python -c \"import torch; print(torch.cuda.is_available())\"")
print(result['output'])

harness.close()
```

## Common LLM Commands (PowerShell)

### 1. Check GPU Status
```powershell
nvidia-smi
# If not in PATH, try:
C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe
```

### 2. CUDA Version
```powershell
nvcc --version
# or
Get-Content "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.1\version.txt"
```

### 3. PyTorch with CUDA
```powershell
python -c "import torch; print(torch.__version__, torch.cuda.get_device_name(0))"
```

### 4. Run LLM Inference (example with transformers)
```powershell
python -c "from transformers import pipeline; pipe = pipeline('text-generation', model='gpt2', device=0); print(pipe('Hello')[0]['generated_text'])"
```

### 5. Monitor GPU during training
```powershell
# In another SSH session (if possible) or use nvidia-smi loop:
while ($true) { nvidia-smi; Start-Sleep -Seconds 5 }
```

## Environment Setup

### Install CUDA Toolkit
- Download from NVIDIA website (match your GPU driver)
- Or use conda: `conda install -c conda-forge cudatoolkit`

### Install PyTorch with CUDA
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Install Transformers / LLM libraries
```powershell
pip install transformers accelerate bitsandbytes  # for quantization
```

## Troubleshooting

### "nvidia-smi not recognized"
- Add to PATH: `C:\Program Files\NVIDIA Corporation\NVSMI`
- Or use full path: `& "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"`

### CUDA not available in PyTorch
```powershell
# Check CUDA version
nvcc --version
# Reinstall PyTorch with correct CUDA version
pip install torch --index-url https://download.pytorch.org/whl/cu121  # for CUDA 12.1
```

### PowerShell execution policy blocked
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
```

### SSH connection issues
- Ensure OpenSSH Server is running: `Get-Service sshd`
- Start if stopped: `Start-Service sshd`

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

1. **Default shell is PowerShell**, but some Windows systems may use cmd.exe.
2. **Paths use backslash** `C:\...`, but PowerShell often accepts forward slash too.
3. **CUDA toolkit and PyTorch must match versions** (e.g., CUDA 12.1 → PyTorch with cu121).
4. **No `conda activate`** unless conda is installed and shell is bash (not default on Windows).
5. **Use `nvidia-smi`** to verify GPU and CUDA availability.

---

**Remember**: If the remote host is Windows, `detect_shell()` should return `'powershell'`. Use PowerShell syntax from `SKILL.md` shell compatibility table.
