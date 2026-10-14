import grpc


class ServiceCallError(Exception):
    def __init__(self, service: str, code: grpc.StatusCode, details: str):
        super().__init__(f"{service}: {code.name} - {details}")
        self.service = service
        self.code = code
        self.details = details

    @classmethod
    def from_rpc_error(cls, service: str, error: grpc.RpcError) -> "ServiceCallError":
        return cls(service, error.code(), error.details() or "")
