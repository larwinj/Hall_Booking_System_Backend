import grpc
from concurrent import futures
import logging

from .grpc_service import MeetingServicer
from .proto import meeting_pb2_grpc

logger = logging.getLogger(__name__)

def start_grpc_server(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    meeting_pb2_grpc.add_MeetingServiceServicer_to_server(
        MeetingServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"gRPC server started on port {port}")
    return server