from kubernetes import client, config
import numpy as np
import time

# Load the Kubernetes configuration
config.load_kube_config()  # Use load_incluster_config() if running inside a pod

# Initialize the API client for metrics
api_instance = client.CustomObjectsApi()

def get_combined_pod_metrics():
    # Fetch pod metrics from the metrics.k8s.io API
    metrics = api_instance.list_cluster_custom_object(
        group="metrics.k8s.io", version="v1beta1", plural="pods"
    )

    # Lists to hold combined CPU and memory usage values across all pods
    cpu_usage_all_pods = []
    memory_usage_all_pods = []

    for pod in metrics['items']:
        for container in pod['containers']:
            cpu_usage = container['usage']['cpu']
            memory_usage = container['usage']['memory']
            
            # Convert CPU to millicores
            if 'n' in cpu_usage:
                cpu_usage_m = int(cpu_usage.replace('n', '')) / 1e6  # Convert nanocores to millicores
            elif 'm' in cpu_usage:
                cpu_usage_m = int(cpu_usage.replace('m', ''))
            else:
                cpu_usage_m = int(cpu_usage) * 1000  # Convert cores to millicores

            # Convert memory to MiB
            if 'Ki' in memory_usage:
                memory_usage_mi = int(memory_usage.replace('Ki', '')) / 1024  # KiB to MiB
            elif 'Mi' in memory_usage:
                memory_usage_mi = int(memory_usage.replace('Mi', ''))
            elif 'Gi' in memory_usage:
                memory_usage_mi = int(memory_usage.replace('Gi', '')) * 1024  # GiB to MiB

            # Append to the lists for combined metrics
            cpu_usage_all_pods.append(cpu_usage_m)
            memory_usage_all_pods.append(memory_usage_mi)

    return cpu_usage_all_pods, memory_usage_all_pods

def calculate_stats(data):
    if not data:
        return {'average': 0, 'max': 0, 'p99': 0}

    average = np.mean(data)
    max_val = np.max(data)
    p99 = np.percentile(data, 99)

    return {'average': average, 'max': max_val, 'p99': p99}

def print_combined_pod_stats(cpu_usage_all_pods, memory_usage_all_pods):
    cpu_stats = calculate_stats(cpu_usage_all_pods)
    memory_stats = calculate_stats(memory_usage_all_pods)

    print("\nCombined CPU Usage Stats (in millicores):")
    print(f"  Average: {cpu_stats['average']} m")
    print(f"  Max: {cpu_stats['max']} m")
    print(f"  P99: {cpu_stats['p99']} m")

    print("\nCombined Memory Usage Stats (in MiB):")
    print(f"  Average: {memory_stats['average']} Mi")
    print(f"  Max: {memory_stats['max']} Mi")
    print(f"  P99: {memory_stats['p99']} Mi")

# Real-time monitoring with 10-second interval
try:
    while True:
        cpu_usage_all_pods, memory_usage_all_pods = get_combined_pod_metrics()
        print_combined_pod_stats(cpu_usage_all_pods, memory_usage_all_pods)
        time.sleep(10)  # Set the interval for fetching metrics
except KeyboardInterrupt:
    print("Stopped monitoring.")
