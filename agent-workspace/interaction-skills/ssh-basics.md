# SSH Interaction Skills

General SSH interaction patterns for LLM agents.

## Basic Interactions

### Execute Command with Timeout

```python
from ssh_harness import run_command

# Short timeout for quick commands
result = run_command("ls -la", timeout=30)

# Long timeout for heavy tasks
result = run_command("python train.py", timeout=3600)
```

### Read Large Files in Chunks

```python
from ssh_harness import read_file

# Read first 500 lines
chunk1 = read_file("/var/log/syslog", max_lines=500)

# Read next 500 lines (offset 501)
chunk2 = read_file("/var/log/syslog", max_lines=500, offset=501)
```

### Safe File Writing

```python
from ssh_harness import write_file

# Always check if write succeeded
success = write_file("/tmp/config.json", '{"key": "value"}')
if success:
    print("✓ File written")
else:
    print("✗ Write failed")
```

## Advanced Patterns

### Check Service Status

```python
from ssh_harness import run_command

def is_service_running(service_name):
    result = run_command(f"systemctl is-active {service_name}")
    return "active" in result['output']

if is_service_running("nginx"):
    print("Nginx is running")
```

### Monitor Log in Real-time (via polling)

```python
from ssh_harness import read_file
import time

last_line_count = 0
while True:
    content = read_file("/var/log/app.log", max_lines=100)
    lines = content.strip().split('\n')
    new_lines = lines[last_line_count:]
    for line in new_lines:
        print(line)
    last_line_count = len(lines)
    time.sleep(10)
```

### Conditional Execution

```python
from ssh_harness import run_command

# Check if file exists before reading
result = run_command("test -f /path/to/file && echo 'exists'")
if "exists" in result['output']:
    from ssh_harness import read_file
    content = read_file("/path/to/file")
    print(content)
```

## Error Handling

```python
from ssh_harness import run_command

result = run_command("risky_command")

if result['exit_code'] != 0:
    print(f"Command failed with code {result['exit_code']}")
    print(f"Error: {result['error']}")
else:
    print("Command succeeded")
    print(result['output'])
```

## Agents: Add More Interaction Patterns Below!
# ==========================================
