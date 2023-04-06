import prometheus_client as client


def reset():
    collectors = list(client.REGISTRY._collector_to_names.keys())
    for collector in collectors:
        client.REGISTRY.unregister(collector)


def filter_metrics(m):
    # Other metric types are not supported so far
    if not m.type == "counter" and not m.type == "histogram":
        return False

    # Empty metrics with labels are exported without values
    if len(m.samples) == 0:
        return False

    # Empty metrics without labels are exported with zero value and empty labels ¯\_(ツ)_/¯
    if len(m.samples) == 1 and m.samples[0].value == 0.0 and len(m.samples[0].labels.keys()) == 0:
        return False

    return True


def get_metrics():
    data = client.REGISTRY.collect()

    # Remove _created metrics (hack because PROMETHEUS_DISABLE_CREATED_SERIES is not working)
    for metric in data:
        metric.samples = [sample for sample in metric.samples if not sample.name.endswith("_created")]

    metrics = list(filter(filter_metrics, data))

    return metrics


def flush_metrics():
    metrics = get_metrics()

    if not metrics or len(metrics) == 0:
        return

    print(f'PROMLOG {metrics}')
