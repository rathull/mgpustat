#!/usr/bin/env python3

import subprocess
import json
import time
import argparse
import re
from rich.console import Console
from rich.table import Table
from rich import box

def get_gpu_info():
    cmd = ["system_profiler", "SPDisplaysDataType", "-json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)

    gpu_info = data["SPDisplaysDataType"][0]
    return {
        "name": gpu_info.get("sppci_model", "Unknown"),
        "memory": gpu_info.get("spdisplays_vram", "Unknown"),
    }

def get_gpu_usage():
    cmd = ["sudo", "powermetrics", "-s", "gpu_power", "-i", "1000", "-n", "1", "--show-process-energy"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.split('\n')

    gpu_usage = {}
    engine_usage = {}
    
    for line in lines:
        if "GPU Active residency" in line:
            match = re.search(r'(\d+\.\d+)%', line)
            if match:
                gpu_usage["active"] = float(match.group(1))
        elif "GPU Idle residency" in line:
            match = re.search(r'(\d+\.\d+)%', line)
            if match:
                gpu_usage["idle"] = float(match.group(1))
        elif "GPU " in line and " active residency" in line:
            parts = line.split(':')
            if len(parts) == 2:
                engine = parts[0].split('GPU ')[1].split(' active')[0].strip()
                match = re.search(r'(\d+\.\d+)%', parts[1])
                if match:
                    usage = float(match.group(1))
                    engine_usage[engine] = usage

    return gpu_usage, engine_usage

def get_top_processes():
    cmd = ["ps", "-A", "-o", "pid,%cpu,comm"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.split('\n')[1:]  # Skip header
    processes = []
    for line in lines:
        if line.strip():
            pid, cpu, name = line.split(None, 2)
            processes.append({"pid": pid, "cpu": float(cpu), "name": name})
    return sorted(processes, key=lambda x: x['cpu'], reverse=True)[:5]

def main():
    parser = argparse.ArgumentParser(description="Display GPU statistics for Apple Silicon Macs")
    parser.add_argument("-i", "--interval", type=int, default=1, help="Update interval in seconds")
    args = parser.parse_args()

    console = Console()

    while True:
        gpu_info = get_gpu_info()
        gpu_usage, engine_usage = get_gpu_usage()
        top_processes = get_top_processes()

        table = Table(title="M1 GPU Statistics", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("GPU Name", gpu_info["name"])
        table.add_row("GPU Memory", gpu_info["memory"])
        table.add_row("GPU Active", f"{gpu_usage.get('active', 0):.2f}%")
        table.add_row("GPU Idle", f"{gpu_usage.get('idle', 0):.2f}%")

        console.clear()
        console.print(table)

        engine_table = Table(title="GPU Engine Usage", box=box.ROUNDED)
        engine_table.add_column("Engine", style="cyan")
        engine_table.add_column("Usage", style="magenta")

        for engine, usage in engine_usage.items():
            engine_table.add_row(engine, f"{usage:.2f}%")

        console.print(engine_table)

        process_table = Table(title="Top GPU Processes", box=box.ROUNDED)
        process_table.add_column("PID", style="cyan")
        process_table.add_column("CPU Usage", style="magenta")
        process_table.add_column("Process Name", style="green")

        for process in top_processes:
            process_table.add_row(process["pid"], f"{process['cpu']:.2f}%", process["name"])

        console.print(process_table)

        time.sleep(args.interval)

if __name__ == "__main__":
    main()