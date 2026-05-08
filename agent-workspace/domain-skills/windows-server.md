# Windows Server Domain Skill

Guide for agents connecting to **Windows Server** (2016/2019/2022) via SSH (OpenSSH).

## Connection

- **Host type**: Windows Server (physical or virtual)
- **Default shell**: PowerShell (modern OpenSSH) or cmd.exe (legacy)
- **SSH**: OpenSSH for Windows (installed by default on newer versions)
- **Architecture**: x86_64 (Intel/AMD)

## Quick Check

```python
from ssh_harness import SSHHarness

harness = SSHHarness()  # Assumes .env configured for Windows host

# Detect shell (should be 'powershell' for modern Windows)
info = harness.detect_shell()
print(info)
# If type is 'powershell', proceed with PowerShell commands
# If type is 'unknown' or cmd, see notes below

# Verify Windows version
result = harness.run_command("systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\"")
print(result['output'])

harness.close()
```

## Common PowerShell Commands (for Windows Server)

| Task | PowerShell Command |
|------|-------------------|
| Check OS version | `Get-ComputerInfo | Select-Object WindowsProductName,OsVersion` |
| List files | `Get-ChildItem` (alias: `ls`, `dir`) |
| Read file | `Get-Content file.txt` |
| Find text in file | `Select-String -Pattern "pattern" file.txt` |
| Check running services | `Get-Service \| Where-Object {$_.Status -eq 'Running'}` |
| Start service | `Start-Service -Name "ServiceName"` |
| Stop service | `Stop-Service -Name "ServiceName"` |
| List processes | `Get-Process` |
| Check network config | `Get-NetIPAddress` or `ipconfig` |
| Disk usage | `Get-PSDrive C \| Select-Object Used,Free` |
| Check CPU/RAM | `Get-Counter '\Processor(_Total)\% Processor Time'` and `Get-Counter '\Memory\Available MBytes'` |
| Windows Firewall | `Get-NetFirewallRule \| Select-Object Name,Enabled,Direction` |
| Event logs | `Get-EventLog -LogName System -Newest 10` |

## Important Notes for Agents

### 1. Paths
- Use backslash `\` as separator: `C:\Users\Administrator\Documents`
- Drive letters: `C:`, `D:`, etc.
- PowerShell accepts forward slash `/` in some contexts, but prefer backslash.

### 2. PowerShell vs cmd
- Modern Windows OpenSSH defaults to PowerShell.
- If `detect_shell()` returns `'cmd'` or `'unknown'`, use cmd syntax (`dir`, `type`, `findstr`).
- Example cmd commands:
  ```bash
  dir C:\
  type file.txt
  findstr /C:"pattern" file.txt
  systeminfo
  ```

### 3. Execution Policy
- PowerShell scripts might be blocked. To allow:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
  ```
- Or bypass for single command:
  ```powershell
  powershell -ExecutionPolicy Bypass -Command "Get-Service"
  ```

### 4. Services
- No `systemctl` (that's Linux). Use `Get-Service`, `Start-Service`, `Stop-Service`.
- Service names often differ from display names. Use:
  ```powershell
  Get-Service | Where-Object {$_.DisplayName -like "*SQL*"}
  ```

### 5. OpenSSH on Windows
- Config files: `C:\ProgramData\ssh\sshd_config`
- Restart SSH service:
  ```powershell
  Restart-Service sshd
  ```

## Troubleshooting

### "Access is denied"
- Run as Administrator? Some commands require elevation.
- Try running command with `Invoke-Command` or check permissions.

### PowerShell not found
- If `detect_shell()` returns `'cmd'`, then PowerShell might not be in PATH.
- Try explicit path: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -Command "Get-Service"`

### SSH connection fails
- Ensure OpenSSH Server is installed and running:
  ```powershell
  Get-WindowsCapability -Online | Where-Object {$_.Name -like "*SSH*"}
  Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
  Start-Service sshd
  Set-Service -Name sshd -StartupType Automatic
  ```

## Example Workflow: Check and Start a Service

```python
from ssh_harness import SSHHarness

harness = SSHHarness()

# Check service status
result = harness.run_command('Get-Service -Name "Spooler" | Select-Object Status,Name,DisplayName')
print(result['output'])

# Start if stopped
if "Stopped" in result['output']:
    result = harness.run_command('Start-Service -Name "Spooler"')
    if result['exit_code'] == 0:
        print("Service started")

harness.close()
```

## Notes for Agents

1. **Always call `detect_shell()`** first to confirm PowerShell.
2. **Use PowerShell syntax** (from `SKILL.md` shell compatibility table).
3. **Expand `SHELL_TRANSLATIONS`** in `agent_helpers.py` with more Windows commands if needed.
4. **Remember**: Windows is case-insensitive for file names, but PowerShell commands are case-insensitive too.
5. **No `sudo`** on Windows; use Administrator privileges if needed.

---

**Remember**: If the remote host is Windows, `detect_shell()` should return `'powershell'` (modern) or `'cmd'` (legacy). Adjust commands accordingly.
