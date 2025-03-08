#!/usr/bin/env python3
"""
fetch_cpu_specs_and_benchmark.py

This script collects CPU specifications, runs a simple performance test,
and writes the results to a YAML file located at ./data/cpu-report.yaml.

Dependencies:
    - psutil
    - PyYAML
    - numpy

Installation (example):
    pip install psutil pyyaml numpy

Usage:
    python fetch_cpu_specs_and_benchmark.py
"""

import os
import platform
import time
from datetime import datetime

import psutil
import yaml
import numpy as np


def gather_cpu_info():
    """
    Gather essential CPU and system-related information using `platform` and `psutil`.
    Returns a dictionary with the collected information.
    """
    cpu_info = {
        # Timestamp for when the data was collected
        "timestamp": str(datetime.now()),
        # Host and OS details
        "hostname": platform.node(),
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        # CPU details
        "cpu_architecture": platform.machine(),
        "cpu_processor_name": platform.processor(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
    }

    # psutil can return None if it cannot determine the frequency
    freq_info = psutil.cpu_freq()
    if freq_info:
        cpu_info["cpu_frequency_mhz"] = freq_info.max
    else:
        cpu_info["cpu_frequency_mhz"] = None

    return cpu_info


def run_performance_test(matrix_size=1000):
    """
    Perform a simple CPU-bound test by multiplying two large random matrices.
    The matrix_size parameter controls the size of the NxN matrix.
    Returns the time taken for the multiplication in seconds.
    """
    # Create two random NxN matrices
    a = np.random.rand(matrix_size, matrix_size)
    b = np.random.rand(matrix_size, matrix_size)

    # Measure the time to multiply these matrices
    start_time = time.time()
    np.dot(a, b)  # matrix multiplication
    end_time = time.time()

    elapsed_time = end_time - start_time
    return elapsed_time


def write_to_yaml(data, filepath="./data/cpu-report.yaml"):
    """
    Write a dictionary to a YAML file at the specified filepath.
    If the parent directory does not exist, create it.
    """
    # Ensure the directory exists
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Write data to the specified YAML file
    with open(filepath, "w", encoding="utf-8") as yaml_file:
        yaml.dump(data, yaml_file, sort_keys=False)


def main():
    """
    Main function that orchestrates gathering CPU info, running a benchmark,
    and writing the results to YAML.
    """
    # Step 1: Gather CPU info
    cpu_info = gather_cpu_info()

    # Step 2: Run a lightweight performance test (matrix multiplication)
    benchmark_time = run_performance_test(matrix_size=500)
    cpu_info["matrix_multiplication_time_seconds"] = benchmark_time

    # Step 3: Write the CPU info and benchmark results to ./data/cpu-report.yaml
    write_to_yaml(cpu_info, filepath="./data/cpu-report.yaml")

    # Print a confirmation message
    print("CPU report and benchmark saved to ./data/cpu-report.yaml.")


if __name__ == "__main__":
    main()
