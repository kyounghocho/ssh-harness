"""
Unit tests for SSH Harness client.
"""

import pytest
from unittest.mock import Mock, patch
from ssh_harness.client import SSHHarness


@pytest.fixture
def mock_ssh_client():
    """Mock paramiko SSH client."""
    with patch('paramiko.SSHClient') as mock:
        instance = mock.return_value
        instance.get_transport.return_value.is_active.return_value = True
        yield instance


@pytest.fixture
def harness(mock_ssh_client):
    """SSHHarness instance with mocked client."""
    with patch('paramiko.AutoAddPolicy'):
        h = SSHHarness(
            host="test.host.com",
            port=22,
            user="testuser",
            key_path="/fake/key",
        )
        h.client = mock_ssh_client
        return h


class TestSSHHarness:
    """Test cases for SSHHarness."""
    
    def test_init(self, mock_ssh_client):
        """Test initialization."""
        with patch('paramiko.AutoAddPolicy'):
            h = SSHHarness(host="192.168.1.1", user="admin")
            assert h.host == "192.168.1.1"
            assert h.user == "admin"
            assert h.port == 22
    
    def test_run_command(self, harness, mock_ssh_client):
        """Test command execution."""
        mock_stdout = Mock()
        mock_stdout.read.return_value = b"command output"
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_stderr = Mock()
        mock_stderr.read.return_value = b""
        
        mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        result = harness.run_command("echo test")
        
        assert result['output'] == "command output"
        assert result['exit_code'] == 0
    
    def test_connection_check(self, harness, mock_ssh_client):
        """Test connection check."""
        mock_ssh_client.get_transport.return_value.is_active.return_value = True
        harness.ensure_connection()  # Should not raise
        
        mock_ssh_client.get_transport.return_value.is_active.return_value = False
        with patch.object(harness, '_connect') as mock_connect:
            harness.ensure_connection()
            mock_connect.assert_called_once()
