from kubernetes import client, config

# Load the kubeconfig file
config.load_kube_config()

# Set up the API client
v1 = client.CoreV1Api()

# Fetch all pods in all namespaces
pods = v1.list_pod_for_all_namespaces()

# Print header
print(f"{'Pod Name':<50} - {'Node Name':<50}")
print('-' * 100)

# Iterate through each pod and print the pod name and node name in aligned format
for pod in pods.items:
    pod_name = pod.metadata.name
    node_name = pod.spec.node_name if pod.spec.node_name else "None"
    print(f"{pod_name:<50} - {node_name:<50}")
