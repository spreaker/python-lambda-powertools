import pytest
from lambda_powertools.prometheus import get_metrics, reset
from prometheus_client import Counter, Histogram, Gauge

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
    name="prometheus_spec_gauge_metric_name",
    documentation="gauge_metric_documentation"
)


@pytest.fixture(autouse=True)
def before_each(monkeypatch):
    reset()


def test_prometheus_get_metrics_does_not_return_empty_metrics():
    reset()

    metrics = get_metrics()

    assert metrics == ""


def test_prometheus_get_metrics_returns_non_empty_metrics():
    gauge.set(1)  # Gauge is not supported yet
    counter_no_labels.inc(1)
    # counter_with_labels.labels("bar").inc(2)
    # histogram_no_labels.observe(1)
    # histogram_with_labels.labels("bar").observe(1)

    metrics = get_metrics()

    expected = """# HELP prometheus_spec_counter_no_labels_total Prometheus example counter without labels
# TYPE prometheus_spec_counter_no_labels_total counter
prometheus_spec_counter_no_labels_total 1.0
"""

    assert metrics == expected
