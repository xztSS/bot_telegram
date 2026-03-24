from __future__ import annotations

import unittest
from unittest.mock import patch

from PIL import Image

from app.decoder import (
    BarcodeDecoder,
    DecodeResult,
    DecoderUnavailableError,
    InvalidImageError,
    build_image_variants,
    safe_decode,
)


class BarcodeDecoderTests(unittest.TestCase):
    def test_safe_decode_supports_cp1251(self) -> None:
        self.assertEqual(safe_decode("тест".encode("cp1251")), "тест")

    def test_build_image_variants_returns_20_images(self) -> None:
        image = Image.new("RGB", (40, 30), "white")
        variants = build_image_variants(image)

        self.assertEqual(len(variants), 20)

    def test_decode_bytes_raises_for_invalid_payload(self) -> None:
        decoder = BarcodeDecoder()

        with self.assertRaises(InvalidImageError):
            decoder.decode_bytes(b"not-an-image")

    def test_decode_image_deduplicates_symbols(self) -> None:
        class FakeDecoded:
            def __init__(self, symbol_type: str, data: bytes) -> None:
                self.type = symbol_type
                self.data = data

        decoder = BarcodeDecoder()
        decoder._decode_fn = lambda _image, _symbols: [
            FakeDecoded("QRCODE", b"hello"),
            FakeDecoded("QRCODE", b"hello"),
            FakeDecoded("EAN13", b"1234567890123"),
        ]
        decoder._symbols = [object()]

        results = decoder.decode_image(Image.new("RGB", (20, 20), "white"))

        self.assertEqual(
            results,
            [
                DecodeResult(symbol_type="QRCODE", data="hello"),
                DecodeResult(symbol_type="EAN13", data="1234567890123"),
            ],
        )

    def test_ensure_backend_raises_when_pyzbar_unavailable(self) -> None:
        decoder = BarcodeDecoder()

        with patch("builtins.__import__", side_effect=ImportError("no zbar")):
            with self.assertRaises(DecoderUnavailableError):
                decoder._ensure_backend()


if __name__ == "__main__":
    unittest.main()
