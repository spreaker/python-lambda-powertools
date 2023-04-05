from prometheus_client import Counter, Histogram, Gauge
from lambda_powertools.prometheus import get_metrics, reset


counter_no_labels = Counter(
    name="prometheus_spec_counter_no_labels",
    documentation="Prometheus example counter without labels"
)

counter_with_labels = Counter(
    name="prometheus_spec_counter_with_labels",
    documentation="Prometheus example counter with labels",
    labelnames=["foo"]
)

histogram_no_labels = Histogram(
    name="prometheus_spec_histogram_no_labels",
    documentation="Prometheus example histogram without labels",
    buckets=[1, 2, 5]
)

histogram_with_labels = Histogram(
    name="prometheus_spec_histogram_with_labels",
    documentation="Prometheus example histogram with labels",
    buckets=[1, 2, 5],
    labelnames=["foo"]
)

gauge = Gauge(
    name="prometheus_spec_metric_name",
    documentation="metric_documentation"
)


def test_prometheus_get_metrics_does_not_return_empty_metrics():
    reset()

    metrics = get_metrics()

    assert metrics == []


def test_prometheus_get_metrics_returns_non_empty_metrics():
    reset()

    counter_no_labels.inc(1)
    counter_with_labels.labels("bar").inc(2)
    histogram_no_labels.observe(1)
    histogram_with_labels.labels("bar").observe(1)
    gauge.set(1)  # Gauge is not supported yet

    metrics = get_metrics()

    assert metrics == [
        {
            "documentation": "Prometheus example counter without labels",
            "name": "prometheus_spec_counter_no_labels",
            "type": "counter",
            "samples": [{"value": 1, "labels": {}}],
            "aggregator": "sum",
        },
        {
            "documentation": "Prometheus example counter with labels",
            "name": "prometheus_spec_counter_with_labels",
            "type": "counter",
            "samples": [{"value": 2, "labels": {"foo": "bar"}}],
            "aggregator": "sum",
        },
        {
            "name": "prometheus_spec_histogram_no_labels",
            "documentation": "Prometheus example histogram without labels",
            "type": "histogram",
            "samples": [
                {"labels": {"le": 1}, "value": 1, "name": "prometheus_spec_histogram_no_labels_bucket"},
                {"labels": {"le": 2}, "value": 1, "name": "prometheus_spec_histogram_no_labels_bucket"},
                {"labels": {"le": 5}, "value": 1, "name": "prometheus_spec_histogram_no_labels_bucket"},
                {"labels": {"le": "+Inf"}, "value": 1, "name": "prometheus_spec_histogram_no_labels_bucket"},
                {"labels": {}, "value": 1, "name": "prometheus_spec_histogram_no_labels_sum"},
                {"labels": {}, "value": 1, "name": "prometheus_spec_histogram_no_labels_count"},
            ],
            "aggregator": "sum"
        },
        {
            "name": "prometheus_spec_histogram_with_labels",
            "documentation": "Prometheus example histogram with labels",
            "type": "histogram",
            "samples": [
                {"labels": {"le": 1}, "value": 1, "name": "prometheus_spec_histogram_with_labels_bucket"},
                {"labels": {"le": 2}, "value": 1, "name": "prometheus_spec_histogram_with_labels_bucket"},
                {"labels": {"le": 5}, "value": 1, "name": "prometheus_spec_histogram_with_labels_bucket"},
                {
                    "labels": {"le": "+Inf"},
                    "value": 1,
                    "name": "prometheus_spec_histogram_with_labels_bucket",
                },
                {"labels": {}, "value": 1, "name": "prometheus_spec_histogram_with_labels_sum"},
                {"labels": {}, "value": 1, "name": "prometheus_spec_histogram_with_labels_count"},
            ],
            "aggregator": "sum"
        }
    ]
