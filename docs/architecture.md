# Documentation

Additional documentation for SSH Harness.

## Architecture Details

### Core Package (`src/ssh_harness/`)

Protected core that provides the basic SSH functionality. Agents should not modify these files.

### Agent Workspace (`agent-workspace/`)

Fully editable by LLM agents:

- `agent_helpers.py`: Custom helper functions
- `domain-skills/`: Host-specific playbooks
- `interaction-skills/`: General SSH interaction patterns

### Design Principles

1. **Thin wrappers**: Minimal abstraction over raw SSH
2. **Agent ownership**: `agent-workspace/` is fully editable
3. **Self-improvement**: Agents write missing functionality
4. **No hand-authoring**: Domain skills are agent-generated

## Comparison with browser-harness

| Feature | browser-harness | ssh-harness |
|---------|-----------------|-------------|
| Control target | Browser (CDP) | SSH |
| Core files | ~1k lines | ~500 lines |
| Agent workspace | Yes | Yes |
| Self-improving | Yes | Yes |
| Conda support | No | Yes |

## FAQ

### Why not just use paramiko directly?

SSH Harness provides a thin, agent-friendly API that LLMs can understand and extend. It's not a replacement for paramiko, but a wrapper designed for agent use.

### Can I use password authentication?

Yes, set `SSH_PASSWORD` in `.env` instead of `SSH_KEY_PATH`.

### How do I add support for a new host type?

Create a new skill in `agent-workspace/domain-skills/`. Let the agent write it!
