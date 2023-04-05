import prometheus_client as client


def reset():
    collectors = list(client.REGISTRY._collector_to_names.keys())
    for collector in collectors:
        client.REGISTRY.unregister(collector)

    # from prometheus_client import gc_collector, platform_collector, process_collector
    # process_collector.ProcessCollector()
    # platform_collector.PlatformCollector()
    # gc_collector.GCCollector()


def filter_metrics(m):
    # Other metric types are not supported so far
    if not m.type == "counter" and not m.type == "histogram":
        return False

    # Empty metrics with labels are exported without values
    if len(m.samples) == 0:
        return False

    # Empty metrics without labels are exported with zero value and empty labels ¯\_(ツ)_/¯
    if len(m.samples) == 1 and m.samples[0].value == 0 and len(m.samples[0].labels.keys()) == 0:
        return False

    return True


def get_metrics():
    data = client.REGISTRY.collect()
    return list(filter(filter_metrics, data))


def flush_metrics():
    metrics = get_metrics()

    if not metrics or len(metrics) == 0:
        return

    print(f'PROMLOG {metrics}')
