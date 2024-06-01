import zstandard


def zstd_compress(input: bytes) -> bytes:
    cctx = zstandard.ZstdCompressor()
    return cctx.compress(input)


ZSTANDARD_MAGIC_BYTES = (0xFD2FB528).to_bytes(4, "little")


def zstd_decompress(input: bytes) -> bytes:
    if input.startswith(ZSTANDARD_MAGIC_BYTES):
        dctx = zstandard.ZstdDecompressor()
        return dctx.decompress(input)

    return input
