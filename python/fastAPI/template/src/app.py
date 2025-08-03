import datetime
import requests
import socket
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry import trace, metrics, _logs


from db import SessionLocal, engine
from models import Base, WeatherCurrent
from middleware import LoggingMiddleware

# Traces
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "fastapi-test"})
    )
)
span_processor = BatchSpanProcessor(OTLPSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Logs
_log_exporter = OTLPLogExporter()
log_provider = LoggerProvider(resource=Resource.create({SERVICE_NAME: "fastapi-test"}))
log_provider.add_log_record_processor(BatchLogRecordProcessor(_log_exporter))
_logs.set_logger_provider(log_provider)

# Metrics
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
metrics.set_meter_provider(
    MeterProvider(resource=Resource.create({SERVICE_NAME: "fastapi-test"}), metric_readers=[metric_reader])
)

# FastAPI app
app = FastAPI()

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

app.add_middleware(LoggingMiddleware)


# Initialize DB models and dependency to get DB session
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Define endpoints
@app.get("/api/${{values.app_name}}/v1/sample")
def sample(db: Session = Depends(get_db)):
    response = requests.get('https://api.chucknorris.io/jokes/random')

    latest_weather = (
        db.query(WeatherCurrent.collection_time, WeatherCurrent.temperature)
        .order_by(WeatherCurrent.collection_time.desc())
        .limit(10)
        .all()
    )

    return {
        "api_data": response.text,
        "weather": [
            {
                "collection_time": w.collection_time.isoformat(),
                "temperature": w.temperature
            } for w in latest_weather
        ]
    }

@app.get("/api/${{values.app_name}}/v1/info")
def info():
    return {
        'hostname': socket.gethostname(),
        'env': '${{values.app_env}}',
        'app_name': '${{values.app_name}}',
        'time': datetime.datetime.now().strftime("%I:%M:%S %p on %Y-%m-%d")
    }

@app.get("/api/${{values.app_name}}/v1/health")
def health():
    return {"status": "UP"}
