import pytest
import os
import prometheus_client as client
from unittest import mock
from prometheus_client import Counter, Histogram, Gauge, Metric
from prometheus_client.samples import Sample
from lambda_powertools.prometheus import get_metrics, reset

counter_no_labels = None
counter_with_labels = None
histogram_no_labels = None
histogram_with_labels = None
gauge = None


@pytest.fixture(autouse=True)
def before_each(monkeypatch):
    global counter_no_labels, counter_with_labels, histogram_no_labels, histogram_with_labels, gauge

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


def test_prometheus_get_metrics_does_not_return_empty_metrics():
    reset()

    metrics = get_metrics()

    assert metrics == []


@mock.patch.dict(os.environ, {"PROMETHEUS_DISABLE_CREATED_SERIES": "True"})
def test_prometheus_get_metrics_returns_non_empty_metrics():
    # Trying to disable default collector metrics, not under test
    try:
        client.REGISTRY.unregister(client.GC_COLLECTOR)
        client.REGISTRY.unregister(client.PLATFORM_COLLECTOR)
        client.REGISTRY.unregister(client.PROCESS_COLLECTOR)
    except:
        pass

    counter_no_labels.inc(1)
    counter_with_labels.labels("bar").inc(2)
    histogram_no_labels.observe(1)
    histogram_with_labels.labels("bar").observe(1)
    gauge.set(1)  # Gauge is not supported yet

    metrics = get_metrics()

    # Remove _created metrics (hack because PROMETHEUS_DISABLE_CREATED_SERIES is not working)
    for metric in metrics:
        metric.samples = [sample for sample in metric.samples if not sample.name.endswith("_created")]

    expected = [
        Metric("prometheus_spec_counter_no_labels", "Prometheus example counter without labels", "counter", ""),
        Metric("prometheus_spec_counter_with_labels", "Prometheus example counter with labels", "counter", ""),
        Metric("prometheus_spec_histogram_no_labels", "Prometheus example histogram without labels", "histogram", ""),
        Metric("prometheus_spec_histogram_with_labels", "Prometheus example histogram with labels", "histogram", "")
    ]
    expected[0].samples = [Sample(name='prometheus_spec_counter_no_labels_total', labels={}, value=1.0, timestamp=None, exemplar=None)]
    expected[1].samples = [Sample(name='prometheus_spec_counter_with_labels_total', labels={'foo': 'bar'}, value=2.0, timestamp=None, exemplar=None)]
    expected[2].samples = [Sample(name='prometheus_spec_histogram_no_labels_bucket', labels={'le': '1.0'}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_no_labels_bucket', labels={'le': '2.0'}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_no_labels_bucket', labels={'le': '5.0'}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_no_labels_bucket', labels={'le': '+Inf'}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_no_labels_count', labels={}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_no_labels_sum', labels={}, value=1.0, timestamp=None, exemplar=None)]
    expected[3].samples = [Sample(name='prometheus_spec_histogram_with_labels_bucket', labels={'foo': 'bar', 'le': '1.0'}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_with_labels_bucket', labels={'foo': 'bar', 'le': '2.0'}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_with_labels_bucket', labels={'foo': 'bar', 'le': '5.0'}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_with_labels_bucket', labels={'foo': 'bar', 'le': '+Inf'}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_with_labels_count', labels={'foo': 'bar'}, value=1.0, timestamp=None, exemplar=None), Sample(name='prometheus_spec_histogram_with_labels_sum', labels={'foo': 'bar'}, value=1.0, timestamp=None, exemplar=None)]

    assert metrics == expected
