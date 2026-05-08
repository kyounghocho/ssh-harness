# Example: Mac MLX LLM

This is an example of a domain skill for Mac (Apple Silicon) hosts with MLX for LLM workloads.

## Connection

- **Host type**: macOS (Apple Silicon M1/M2/M3)
- **Shell**: zsh (default) or bash
- **Framework**: MLX (Apple Silicon only)

## Quick Check

```python
from ssh_harness import SSHHarness

harness = SSHHarness()
result = harness.run_command("python -c 'import mlx; print(mlx.__version__)'")
print(result['output'])
harness.close()
```

## Common Commands

| Task | Command (bash/zsh) |
|------|-------------------|
| Check MLX | `python -c "import mlx; print(mlx.__version__)"` |
| Metal GPU info | `system_profiler SPDisplaysDataType` |
| Run LLM | `python -m mlx_lm.generate --model ~/.mlx/models/mistral-7b` |

## Notes

- Agents: Copy this to `agent-workspace/domain-skills/mac-mlx.md` and customize.
- Expand `SHELL_TRANSLATIONS` in `agent_helpers.py` as needed.
