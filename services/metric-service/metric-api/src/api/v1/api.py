from apiflask import APIBlueprint

metric_bp = APIBlueprint("metrics", __name__)


@metric_bp.get("/metrics/")
def get_metrics():
    return "Hello World!"
