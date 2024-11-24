# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import app.recognition.recognition_pb2 as recognition__pb2
import app.recognition.task_pb2 as task__pb2

GRPC_GENERATED_VERSION = '1.68.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in recognition_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class SmartSpeechStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Recognize = channel.stream_stream(
                '/smartspeech.recognition.v1.SmartSpeech/Recognize',
                request_serializer=recognition__pb2.RecognitionRequest.SerializeToString,
                response_deserializer=recognition__pb2.RecognitionResponse.FromString,
                _registered_method=True)
        self.AsyncRecognize = channel.unary_unary(
                '/smartspeech.recognition.v1.SmartSpeech/AsyncRecognize',
                request_serializer=recognition__pb2.AsyncRecognizeRequest.SerializeToString,
                response_deserializer=task__pb2.Task.FromString,
                _registered_method=True)


class SmartSpeechServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Recognize(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AsyncRecognize(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SmartSpeechServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Recognize': grpc.stream_stream_rpc_method_handler(
                    servicer.Recognize,
                    request_deserializer=recognition__pb2.RecognitionRequest.FromString,
                    response_serializer=recognition__pb2.RecognitionResponse.SerializeToString,
            ),
            'AsyncRecognize': grpc.unary_unary_rpc_method_handler(
                    servicer.AsyncRecognize,
                    request_deserializer=recognition__pb2.AsyncRecognizeRequest.FromString,
                    response_serializer=task__pb2.Task.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'smartspeech.recognition.v1.SmartSpeech', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('smartspeech.recognition.v1.SmartSpeech', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class SmartSpeech(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Recognize(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/smartspeech.recognition.v1.SmartSpeech/Recognize',
            recognition__pb2.RecognitionRequest.SerializeToString,
            recognition__pb2.RecognitionResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AsyncRecognize(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/smartspeech.recognition.v1.SmartSpeech/AsyncRecognize',
            recognition__pb2.AsyncRecognizeRequest.SerializeToString,
            task__pb2.Task.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
