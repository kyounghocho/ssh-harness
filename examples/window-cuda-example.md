# Example: Windows CUDA LLM

This is an example of a domain skill for Windows hosts with NVIDIA CUDA for LLM workloads.

## Connection

- **Host type**: Windows 10/11 or Server with NVIDIA GPU
- **Shell**: PowerShell (default)
- **GPU**: NVIDIA (CUDA capable)

## Quick Check

```python
from ssh_harness import SSHHarness

harness = SSHHarness()
result = harness.run_command("nvidia-smi")
print(result['output'][:500])
harness.close()
```

## Common Commands (PowerShell)

| Task | Command |
|------|---------|
| Check GPU | `nvidia-smi` |
| CUDA version | `nvcc --version` |
| PyTorch check | `python -c "import torch; print(torch.cuda.is_available())"` |
| Run LLM | `python inference.py --model gpt2` |

## Notes

- Agents: Copy this to `agent-workspace/domain-skills/window-cuda.md` and customize.
- Expand `SHELL_TRANSLATIONS` in `agent_helpers.py` as needed.
