from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Callable, Iterable, Protocol

from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)


class DecoderUnavailableError(RuntimeError):
    """Raised when native barcode dependencies are not available."""


class InvalidImageError(RuntimeError):
    """Raised when a user payload is not a readable image."""


@dataclass(frozen=True, slots=True)
class DecodeResult:
    symbol_type: str
    data: str


class PyzbarDecoded(Protocol):
    type: str
    data: bytes


DecodeFn = Callable[[Image.Image, list[Any]], Iterable[PyzbarDecoded]]


SUPPORTED_SYMBOL_NAMES: tuple[str, ...] = (
    "QRCODE",
    "EAN13",
    "EAN8",
    "CODE128",
    "CODE39",
    "PDF417",
    "DATABAR",
    "DATABAR_EXP",
    "UPCA",
    "UPCE",
    "I25",
    "CODABAR",
)


class BarcodeDecoder:
    def __init__(self) -> None:
        self._decode_fn: DecodeFn | None = None
        self._symbols: list[Any] | None = None

    def decode_bytes(self, payload: bytes) -> list[DecodeResult]:
        try:
            image = Image.open(BytesIO(payload))
            image.load()
        except (UnidentifiedImageError, OSError) as exc:
            raise InvalidImageError("Unable to read image payload") from exc

        return self.decode_image(image)

    def decode_image(self, image: Image.Image) -> list[DecodeResult]:
        decode_fn, symbols = self._ensure_backend()
        unique_codes: dict[tuple[str, str], DecodeResult] = {}

        for variant in build_image_variants(image):
            try:
                decoded_items = decode_fn(variant, symbols)
            except Exception as exc:  # pragma: no cover - native zbar runtime protection
                logger.exception("Barcode decoding failed for current image variant: %s", exc)
                continue

            for item in decoded_items:
                result = DecodeResult(symbol_type=item.type, data=safe_decode(item.data))
                unique_codes[(result.symbol_type, result.data)] = result

        return list(unique_codes.values())

    def _ensure_backend(self) -> tuple[DecodeFn, list[Any]]:
        if self._decode_fn is not None and self._symbols is not None:
            return self._decode_fn, self._symbols

        try:
            from pyzbar.pyzbar import ZBarSymbol, decode
        except ImportError as exc:  # pragma: no cover - depends on system libzbar
            raise DecoderUnavailableError(
                "Barcode decoding backend is unavailable. Install libzbar in the runtime image."
            ) from exc

        self._decode_fn = decode
        self._symbols = [getattr(ZBarSymbol, name) for name in SUPPORTED_SYMBOL_NAMES]
        return self._decode_fn, self._symbols



def build_image_variants(image: Image.Image) -> list[Image.Image]:
    prepared = ImageOps.exif_transpose(image).convert("RGB")
    grayscale = ImageOps.grayscale(prepared)
    high_contrast = ImageOps.autocontrast(grayscale)
    sharpened = ImageEnhance.Sharpness(high_contrast).enhance(2.0)
    threshold = sharpened.point(lambda px: 255 if px > 140 else 0)

    base_variants = [prepared, grayscale, high_contrast, sharpened, threshold]
    rotated_variants: list[Image.Image] = []
    for variant in base_variants:
        rotated_variants.extend(
            [
                variant,
                variant.rotate(90, expand=True),
                variant.rotate(180, expand=True),
                variant.rotate(270, expand=True),
            ]
        )

    return rotated_variants



def safe_decode(value: bytes) -> str:
    for encoding in ("utf-8", "cp1251", "latin-1"):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            continue

    return value.decode("utf-8", errors="replace")
