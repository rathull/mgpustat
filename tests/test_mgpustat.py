import pytest
from unittest.mock import patch, MagicMock
from mgpustat.main import get_gpu_info, get_gpu_usage, get_top_processes, main


@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_run:
        yield mock_run


def test_get_gpu_info(mock_subprocess_run):
    mock_subprocess_run.return_value.stdout = """
    {
      "SPDisplaysDataType" : [
        {
          "sppci_model" : "Apple M1",
          "spdisplays_vram" : "4 GB"
        }
      ]
    }
    """
    result = get_gpu_info()
    assert result == {"name": "Apple M1", "memory": "4 GB"}


def test_get_gpu_usage(mock_subprocess_run):
    mock_subprocess_run.return_value.stdout = """
    GPU Active residency: 25.00%
    GPU Idle residency: 75.00%
    GPU Compute Engine active residency: 20.00%
    GPU Renderer active residency: 15.00%
    """
    gpu_usage, engine_usage = get_gpu_usage()
    assert gpu_usage == {"active": 25.00, "idle": 75.00}
    assert engine_usage == {"Compute Engine": 20.00, "Renderer": 15.00}


def test_get_top_processes(mock_subprocess_run):
    mock_subprocess_run.return_value.stdout = """PID   %CPU COMMAND
    123   10.0 process1
    456   5.0  process2
    789   2.5  process3
    1011  1.0  process4
    1213  0.5  process5
    1415  0.2  process6
    """
    result = get_top_processes()
    assert len(result) == 5
    assert result[0] == {"pid": "123", "cpu": 10.0, "name": "process1"}
    assert result[1] == {"pid": "456", "cpu": 5.0, "name": "process2"}
    assert result[2] == {"pid": "789", "cpu": 2.5, "name": "process3"}
    assert result[3] == {"pid": "1011", "cpu": 1.0, "name": "process4"}
    assert result[4] == {"pid": "1213", "cpu": 0.5, "name": "process5"}


@patch("mgpustat.main.get_gpu_info")
@patch("mgpustat.main.get_gpu_usage")
@patch("mgpustat.main.get_top_processes")
@patch("time.sleep", side_effect=KeyboardInterrupt)
def test_main(mock_sleep, mock_top_processes, mock_gpu_usage, mock_gpu_info, capsys):
    mock_gpu_info.return_value = {"name": "Apple M1", "memory": "4 GB"}
    mock_gpu_usage.return_value = (
        {"active": 25.00, "idle": 75.00},
        {"Compute Engine": 20.00, "Renderer": 15.00},
    )
    mock_top_processes.return_value = [
        {"pid": "123", "cpu": 10.0, "name": "process1"},
        {"pid": "456", "cpu": 5.0, "name": "process2"},
    ]

    with pytest.raises(KeyboardInterrupt):
        main()

    captured = capsys.readouterr()
    assert "Apple M1" in captured.out
    assert "4 GB" in captured.out
    assert "25.00%" in captured.out
    assert "75.00%" in captured.out
    assert "process1" in captured.out
    assert "process2" in captured.out
