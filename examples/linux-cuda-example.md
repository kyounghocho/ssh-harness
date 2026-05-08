# [Domain Name] Skill

Template for agents to create domain-specific skills. Fill in the sections below.

## Connection

- **Host type**: (e.g., Ubuntu 22.04, Windows Server 2022, macOS Sonoma)
- **Shell**: (e.g., bash, zsh, PowerShell, cmd.exe)
- **GPU**: (e.g., NVIDIA RTX 3090, Apple M2, None)
- **Architecture**: (e.g., x86_64, arm64)

## Quick Check

```python
from ssh_harness import SSHHarness

harness = SSHHarness()  # Assumes .env configured

# Agent: Add quick verification commands here
# Example:
# result = harness.run_command("uname -a")
# print(result['output'])

harness.close()
```

## Common Commands

| Task | Command (use correct shell syntax) |
|------|------------------------------------|
| Check GPU | (agent fills in) |
| Check framework | (agent fills in) |
| Run LLM | (agent fills in) |
| Monitor training | (agent fills in) |

## Environment Setup

```bash
# Agent: Add setup commands here
```

## Troubleshooting

### Issue: (agent adds common issues)
- Solution: (agent adds)

## Example Workflow

```python
from ssh_harness import SSHHarness

harness = SSHHarness()

# Agent: fill in workflow steps
# 1. Check environment
# 2. Run task
# 3. Verify result

harness.close()
```

## Notes for Agents

1. **Use `detect_shell()`** first to confirm shell type.
2. **Follow shell syntax** from `SKILL.md` compatibility table.
3. **Expand `SHELL_TRANSLATIONS`** in `agent_helpers.py` if needed.
4. **Save this file** as `agent-workspace/domain-skills/[your-domain].md`.
5. **Keep it concise** - only add what you actually need.

---

**Remember**: This file should be created by agents, not by humans. Edit freely!
