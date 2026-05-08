"""
Agent-editable helper functions for SSH Harness.

Agents can write custom helpers here when they need functionality
that doesn't exist in the core ssh_harness package.

This file is meant to be edited by LLM agents during execution.
"""

from ssh_harness import run_command, read_file, write_file, upload, download, check_gpu


# Example helper: Get GPU temperature
def get_gpu_temp():
    """
    Get GPU temperature.
    
    Returns:
        Temperature in Celsius, or None if failed
    """
    result = run_command("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader")
    if result['exit_code'] == 0:
        try:
            return int(result['output'].strip())
        except ValueError:
            return None
    return None


# Example helper: Check if a process is running
def is_process_running(process_name):
    """
    Check if a process is running on remote host.
    
    Args:
        process_name: Name of the process to check
    
    Returns:
        True if running, False otherwise
    """
    result = run_command(f"pgrep -f '{process_name}'")
    return result['exit_code'] == 0


# Example helper: Get disk usage
def get_disk_usage(path="/"):
    """
    Get disk usage for a path.
    
    Args:
        path: Path to check (default: /)
    
    Returns:
        Dict with 'total', 'used', 'free', 'percent'
    """
    result = run_command(f"df -h {path} | tail -1")
    if result['exit_code'] == 0:
        parts = result['output'].split()
        if len(parts) >= 5:
            return {
                'filesystem': parts[0],
                'total': parts[1],
                'used': parts[2],
                'free': parts[3],
                'percent': parts[4],
            }
    return None


# Example helper: Monitor training progress
def check_training_progress(log_path):
    """
    Check ML training progress from log file.
    
    Args:
        log_path: Path to training log file
    
    Returns:
        Dict with 'epoch', 'loss', 'status' or None
    """
    content = read_file(log_path, max_lines=50)
    lines = content.strip().split('\n')
    
    progress = {
        'epoch': None,
        'loss': None,
        'status': 'unknown',
    }
    
    for line in reversed(lines):
        if 'epoch' in line.lower() and 'loss' in line.lower():
            import re
            epoch_match = re.search(r'epoch[^\d]*(\d+)', line.lower())
            loss_match = re.search(r'loss[^\d]*([\d.]+)', line.lower())
            
            if epoch_match:
                progress['epoch'] = int(epoch_match.group(1))
            if loss_match:
                progress['loss'] = float(loss_match.group(1))
            break
    
    if 'complete' in content.lower():
        progress['status'] = 'completed'
    elif 'error' in content.lower():
        progress['status'] = 'error'
    elif progress['epoch'] is not None:
        progress['status'] = 'training'
    
    return progress


# Agents: Add your custom helpers below this line!
# ==================================================

# Shell compatibility helpers
SHELL_TRANSLATIONS = {
    'bash': {
        'list_files': 'ls -la',
        'read_file': 'cat {file}',
        'find_text': 'grep "{pattern}" {file}',
        'set_env': 'export {var}={value}',
        'path_sep': '/',
        'env_var_prefix': '$',
        'check_gpu': 'nvidia-smi',
        'disk_usage': 'df -h {path}',
    },
    'powershell': {
        'list_files': 'Get-ChildItem',
        'read_file': 'Get-Content {file}',
        'find_text': 'Select-String -Pattern "{pattern}" {file}',
        'set_env': '$env:{var} = "{value}"',
        'path_sep': '\\',
        'env_var_prefix': '$env:',
        # Agents can expand this! Example:
        'check_gpu': 'Get-Counter "\\GPU Process Memory\\Local Usage"',
        'disk_usage': 'Get-PSDrive C | Select-Object Used,Free',
        'list_processes': 'Get-Process',
        'network_ports': 'Get-NetTCPConnection',
    },
    # Agents: Add cmd, zsh, fish, etc. as needed!
}

def detect_remote_shell():
    """Detect remote shell type using SSHHarness.
    
    Returns:
        Dict with 'type' (bash/powershell/unknown), 'hint' (str)
    """
    from ssh_harness import SSHHarness
    harness = SSHHarness()
    info = harness.detect_shell()
    harness.close()
    return info

def run_shell_command(command, shell_type=None):
    """Run a command with automatic shell detection if not provided.
    
    Args:
        command: Command string (assumed bash if shell_type not given)
        shell_type: 'bash', 'powershell', or None for auto-detect
    
    Returns:
        Dict with 'output', 'error', 'exit_code'
    """
    from ssh_harness import SSHHarness
    harness = SSHHarness()
    
    if shell_type is None:
        info = harness.detect_shell()
        shell_type = info.get('type', 'bash')
    
    # Simple translation for common commands (agents can expand)
    if shell_type == 'powershell':
        # Basic translations - agents should improve this
        if command.strip().startswith('ls '):
            command = command.replace('ls ', 'Get-ChildItem ', 1)
        elif command.strip() == 'ls':
            command = 'Get-ChildItem'
        # Add more translations as needed
    
    result = harness.run_command(command)
    harness.close()
    return result
