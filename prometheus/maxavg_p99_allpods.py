import requests

PROMETHEUS_URL = "http://34.66.104.228:80/api/v1/query"  # Replace with your Prometheus server URL

def fetch_prometheus_metric(query):
    response = requests.get(f"{PROMETHEUS_URL}", params={"query": query})
    result = response.json()
    if 'data' in result and 'result' in result['data']:
        return result['data']['result']
    return []

def calculate_stat(metric_name, query):
    print(f"\n{metric_name}")
    metric_data = fetch_prometheus_metric(query)
    if metric_data:
        for result in metric_data:
            pod = result['metric'].get('pod', 'all_pods')
            value = float(result['value'][1])
            print(f"  Pod: {pod}, {metric_name}: {value}")
    else:
        print(f"No data found for {metric_name}.")

# Queries
queries = {
    "Average CPU Usage (Cores)": 'avg(rate(container_cpu_usage_seconds_total{namespace="default"}[5m]))',
    "Max CPU Usage (Cores)": 'max(rate(container_cpu_usage_seconds_total{namespace="default"}[5m]))',
    "99th Percentile CPU Usage (Cores)": 'quantile(0.99, rate(container_cpu_usage_seconds_total{namespace="default"}[5m]))',
    "Average Memory Usage (MiB)": 'avg(container_memory_usage_bytes{namespace="default"}) / 1024 / 1024',
    "Max Memory Usage (MiB)": 'max(container_memory_usage_bytes{namespace="default"}) / 1024 / 1024',
    "99th Percentile Memory Usage (MiB)": 'quantile(0.99, container_memory_usage_bytes{namespace="default"}) / 1024 / 1024',
}

# Fetch and display metrics
for metric_name, query in queries.items():
    calculate_stat(metric_name, query)
