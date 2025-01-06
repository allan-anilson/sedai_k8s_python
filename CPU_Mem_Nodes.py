from kubernetes import client, config
import time

# Load the Kubernetes configuration
config.load_kube_config()  # Use load_incluster_config() if running inside a pod

# Initialize the API client for metrics
api_instance = client.CustomObjectsApi()

def get_node_metrics():
    # Fetch node metrics from the metrics.k8s.io API
    metrics = api_instance.list_cluster_custom_object(
        group="metrics.k8s.io", version="v1beta1", plural="nodes"
    )

    print("Node Metrics:")
    for node in metrics['items']:
        node_name = node['metadata']['name']
        cpu_usage = node['usage']['cpu']
        memory_usage = node['usage']['memory']
        print(f"Node: {node_name}, CPU Usage: {cpu_usage}, Memory Usage: {memory_usage}")

# Fetch metrics in real-time with a 10-second interval
try:
    while True:
        get_node_metrics()
        time.sleep(3)  # Set the interval for fetching metrics
except KeyboardInterrupt:
    print("Stopped monitoring.")
