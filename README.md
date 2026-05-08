# SSH Harness ♞

SSH Harness is a thin, editable SSH control tool that enables LLMs to control remote hosts programmatically.

> **Direct SSH, no intermediate layers. Your LLM will never SSH manually again.**

Inspired by [browser-use/browser-harness](https://github.com/browser-use/browser-harness).

## Philosophy

- **Single SSH socket**: One persistent connection, direct to remote
- **Self-improving**: Agents write missing helpers during execution
- **Thin wrapper**: No unnecessary abstraction
- **Agent-owned**: `agent-workspace/` is fully editable by agents

## Architecture

~500 lines across 3 core files, with this layout:

| Path | Purpose |
|------|---------|
| `install.md` | First-time install and SSH bootstrap |
| `SKILL.md` | Day-to-day usage instructions |
| `src/ssh_harness/` | Protected core package |
| `agent-workspace/agent_helpers.py` | Agent-edited helper code |
| `agent-workspace/domain-skills/` | Reusable, agent-edited host-specific skills |
| `agent-workspace/interaction-skills/` | General SSH interaction skills |
| `docs/` | Project documentation |
| `tests/` | Unit (`tests/unit`) and integration (`tests/integration`) tests |

## Quick Start

### Install

```bash
pip install ssh-harness
```

Or from source:

```bash
git clone https://github.com/kyounghocho/ssh-harness.git
cd ssh-harness
pip install -e .
```

### First Run

```bash
# 1. Copy example env
cp .env.example .env

# 2. Edit with your remote host details
vim .env

# 3. Test connection
python -c "from ssh_harness import SSHHarness; SSHHarness().run_command('echo hello')"
```

## Example Workflow

```
● agent: wants to check GPU temperature
  │
  ● agent-workspace/agent_helpers.py → helper missing
  │
  ● agent writes it: get_gpu_temp()
  │
  ✓ GPU temp retrieved
```

## Using with LLM Agents

### For Hermes Agent

```python
skill_view(name='ssh-harness')
```

### For Other Agents

```python
from ssh_harness import run_command, read_file

result = run_command("nvidia-smi")
content = read_file("/path/to/file.txt")
```

## Domain Skills

Agents create host-specific playbooks in `agent-workspace/domain-skills/`:

- `remote-linux.md`: General remote Linux host
- (Agents add more for AWS, GCP, etc.)

> **Rule**: Domain skills are agent-generated only. Do not hand-author.

## Environment Variables

See `.env.example`:

```bash
SSH_HOST=your_host
SSH_PORT=22
SSH_USER=your_user
SSH_KEY_PATH=~/.ssh/id_rsa
# SSH_PASSWORD=alternative_auth
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
black src/ tests/
```

## License

MIT License - see [LICENSE](LICENSE).

---

**Inspired by**: [browser-use/browser-harness](https://github.com/browser-use/browser-harness) ♞
