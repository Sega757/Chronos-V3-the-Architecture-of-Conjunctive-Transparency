import grpc
from concurrent import futures
import time
import argparse
import sys
import os

# Import generated protobuf classes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import chronos_interface_pb2
import chronos_interface_pb2_grpc
import chronos_logos

class RealityFilterServicer(chronos_interface_pb2_grpc.RealityFilterServicer):
    def IngestTelemetry(self, request, context):
        print(f"Ingesting telemetry for session {request.session_id}, target: {request.query_target}")

        # Simulate Sub-100 ms Fail-Fast Circuit Breaker
        # In a real system, this would query physical sensors/APIs
        if request.query_target == "corrupted":
            print("FAIL-FAST Triggered: Signal Absent")
            return chronos_interface_pb2.TelemetryResponse(
                session_id=request.session_id,
                raw_values=[],
                signal_absent=True
            )

        # Simulate returning raw telemetry
        raw_values = [101.2, 101.5, 101.1, 800.4, 101.3] # 800.4 is an outlier
        return chronos_interface_pb2.TelemetryResponse(
            session_id=request.session_id,
            raw_values=raw_values,
            signal_absent=False
        )

    def SterilizeAndAlign(self, request, context):
        print(f"Sterilizing data for session {request.session_id}")

        # Pass to chronos_logos for Huber M-Estimation and signing
        ko_data = chronos_logos.process_and_sign(
            request.session_id,
            list(request.raw_values),
            request.huber_delta
        )

        return chronos_interface_pb2.KnowledgeObject(
            object_id=ko_data['object_id'],
            timestamp_utc_ms=ko_data['timestamp'],
            rfc8785_canonical_json=ko_data['json'],
            huber_residual_delta=ko_data['huber_residual'],
            signal_present=ko_data['signal_present'],
            ed25519_signature=ko_data['signature'],
            merkle_root_hash=ko_data['merkle_root']
        )

def serve():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=str, default='50051')
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chronos_interface_pb2_grpc.add_RealityFilterServicer_to_server(RealityFilterServicer(), server)

    server.add_insecure_port(f'[::]:{args.port}')
    print(f"Starting Chronos V3 Reality Filter on port {args.port}...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
