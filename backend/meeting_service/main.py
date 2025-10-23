from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import threading
import logging

from .service import router
from .grpc_server import start_grpc_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Meeting Service")

# Include meeting routes
app.include_router(router)

def start_grpc():
    server = start_grpc_server(port=50051)
    server.wait_for_termination()

grpc_thread = threading.Thread(target=start_grpc, daemon=True)
grpc_thread.start()

@app.on_event("startup")
async def startup_event():
    logger.info("Meeting Service started")
    logger.info("gRPC server running on port 50051")
    logger.info("FastAPI server running")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)