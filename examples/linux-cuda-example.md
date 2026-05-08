# Example: Linux CUDA LLM

This is an example of a domain skill for Linux hosts with NVIDIA CUDA for LLM workloads.

## Connection

- **Host type**: Linux (Ubuntu, Debian, etc.)
- **Shell**: bash (default)
- **GPU**: NVIDIA (CUDA capable)

## Quick Check

```python
from ssh_harness import SSHHarness

harness = SSHHarness()
result = harness.run_command("nvidia-smi")
print(result['output'][:500])
harness.close()
```

## Common Commands

| Task | Command (bash) |
|------|----------------|
| Check GPU | `nvidia-smi` |
| CUDA version | `nvcc --version` |
| PyTorch check | `python -c "import torch; print(torch.cuda.is_available())"` |
| Run inference | `python inference.py --model gpt2` |
| Monitor training | `tail -f train.log` |

## Notes

- Agents: Copy this to `agent-workspace/domain-skills/linux-cuda.md` and customize.
- Expand `SHELL_TRANSLATIONS` in `agent_helpers.py` as needed.
