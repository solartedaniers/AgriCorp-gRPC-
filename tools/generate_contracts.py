from pathlib import Path

from grpc_tools import protoc


class ContractGenerator:
    def __init__(self, root: Path):
        self._root = root
        self._proto_dir = root / "protos"

    def run(self) -> None:
        for proto in sorted(self._proto_dir.rglob("*.proto")):
            relative = proto.relative_to(self._proto_dir).as_posix()
            code = protoc.main([
                "grpc_tools.protoc",
                f"-I{self._proto_dir}",
                f"--python_out={self._root}",
                f"--pyi_out={self._root}",
                f"--grpc_python_out={self._root}",
                relative,
            ])
            if code != 0:
                raise SystemExit(f"protoc failed for {relative}")
            print(f"Generated stubs for {relative}")


if __name__ == "__main__":
    ContractGenerator(Path(__file__).resolve().parent.parent).run()
