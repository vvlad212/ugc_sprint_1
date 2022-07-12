from functools import wraps
import os
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter


def configure_tracer(app: Flask = None) -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=app.config.get("JAEGER_HOST"),
                agent_port=app.config.get("JAEGER_PORT"),
            )
        )
    )
    if os.environ.get('ENV') == 'dev':
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter()))

    FlaskInstrumentor().instrument_app(app)


def jaeger_trace(attributes_dict: dict, tracer):
    def trace_decorator(function):

        def _set_attributes(span, attributes_dict: dict):
            if attributes_dict:
                for att_name, value in attributes_dict.items():
                    span.set_attribute(att_name, value)
            if os.environ.get('ENV', "test") != "test":
                req_id = request.headers.get('X-Request-ID')
                if req_id:
                    span.set_attribute('http.request_id', req_id)

        @wraps(function)
        def wrapper(*args, **kwargs):
            name = attributes_dict.get('span_name', __name__)
            with tracer.start_as_current_span(name) as span:
                _set_attributes(span, attributes_dict)
                return function(*args, **kwargs)
        return wrapper
    return trace_decorator
