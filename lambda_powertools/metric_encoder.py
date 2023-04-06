import json
from prometheus_client import Metric


class MetricEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Metric):
            return {
                "help": obj.documentation,
                "name": obj.name,
                "type": obj.type,
                "values": json.dumps(obj.samples),
                "aggregator": "sum",
            }
        return json.JSONEncoder.default(self, obj)
