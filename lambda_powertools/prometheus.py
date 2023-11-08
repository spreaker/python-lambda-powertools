import os
import json

os.environ['PROMETHEUS_DISABLE_CREATED_SERIES'] = 'True'
import prometheus_client
from prometheus_client import CollectorRegistry

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)


def reset():
    for collector in list(prometheus_client.REGISTRY._collector_to_names.keys()):
        if "_value" in dir(collector):
            # case Counter without labels
            collector._value.set(0)
        elif "_metrics" in dir(collector):
            for metric in collector._metrics.values():
                if "_value" in dir(metric):
                    # case Counter with labels
                    metric._value.set(0)
                elif "_buckets" in dir(metric) and "_sum" in dir(metric):
                    # case Histogram with labels
                    metric._sum.set(0)
                    for bucket in metric._buckets:
                        bucket.set(0)
        elif "_buckets" in dir(collector) and "_sum" in dir(collector):
            # case Histogram without labels
            collector._sum.set(0)
            for bucket in collector._buckets:
                bucket.set(0)


def filter_metrics(m):
    # Other metric types are not supported so far
    if not m._type == "counter" and not m._type == "histogram":
        return False

    # Empty metrics with labels are exported without values
    dir_m = dir(m)
    if "_value" in dir_m and m._value._value == 0:
        return False
    if "_metrics" in dir_m and len(m._metrics.values()) == 0:
        return False
    if "_buckets" in dir_m and m._sum._value == 0:
        return False

    return True


def get_metrics():
    new_registry = CollectorRegistry(auto_describe=True)
    for collector in list(prometheus_client.REGISTRY._collector_to_names.keys()):
        if (filter_metrics(collector)):
            new_registry.register(collector)

    data = prometheus_client.generate_latest(new_registry).decode("utf-8")

    return data


def flush_metrics():
    metrics = get_metrics()

    if not metrics or len(metrics) == 0:
        return

    print("PROMLOG [" + json.dumps(metrics) + "]")
