from kubernetes import client, config
import time
import numpy as np
# Load the Kubernetes configuration
config.load_kube_config()  # Use load_incluster_config() if running inside a pod
# Initialize the API client for metrics
api_instance = client.CustomObjectsApi()
def get_node_metrics():
    # Fetch node metrics from the metrics.k8s.io API
    metrics = api_instance.list_cluster_custom_object(
        group="metrics.k8s.io", version="v1beta1", plural="nodes"
    )
    cpu_usages = []
    memory_usages = []
    for node in metrics['items']:
        cpu_usage = node['usage']['cpu']
        memory_usage = node['usage']['memory']
        
        # Convert CPU to millicores (strip 'n' for nanocores if needed)
        if 'n' in cpu_usage:
            cpu_usages.append(int(cpu_usage.replace('n', '')) / 1e6)  # Convert nanocores to millicores
        elif 'm' in cpu_usage:
            cpu_usages.append(int(cpu_usage.replace('m', '')))
        else:
            cpu_usages.append(int(cpu_usage) * 1000)  # Convert cores to millicores
        # Convert memory to MiB (strip 'Ki', 'Mi', 'Gi' as appropriate)
        if 'Ki' in memory_usage:
            memory_usages.append(int(memory_usage.replace('Ki', '')) / 1024)  # KiB to MiB
        elif 'Mi' in memory_usage:
            memory_usages.append(int(memory_usage.replace('Mi', '')))
        elif 'Gi' in memory_usage:
            memory_usages.append(int(memory_usage.replace('Gi', '')) * 1024)  # GiB to MiB
    return cpu_usages, memory_usages
def calculate_stats(data):
    if not data:
        return {'average': 0, 'max': 0, 'p99': 0}
    average = np.mean(data)
    max_val = np.max(data)
    p99 = np.percentile(data, 99)
    return {'average': average, 'max': max_val, 'p99': p99}
def print_stats(cpu_usages, memory_usages):
    cpu_stats = calculate_stats(cpu_usages)
    memory_stats = calculate_stats(memory_usages)
    
    print("CPU Usage Stats (in millicores):")
    print(f"  Average: {cpu_stats['average']} m")
    print(f"  Max: {cpu_stats['max']} m")
    print(f"  P99: {cpu_stats['p99']} m\n")
    
    print("Memory Usage Stats (in MiB):")
    print(f"  Average: {memory_stats['average']} Mi")
    print(f"  Max: {memory_stats['max']} Mi")
    print(f"  P99: {memory_stats['p99']} Mi\n")
# Real-time monitoring with 10-second interval
try:
    while True:
        cpu_usages, memory_usages = get_node_metrics()
        print_stats(cpu_usages, memory_usages)
        time.sleep(2)  # Set the interval for fetching metrics
except KeyboardInterrupt:
    print("Stopped monitoring.")