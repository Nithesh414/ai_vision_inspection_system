"""
Image Quality Validation + Preprocessing (OpenCV).
Covers: resize, normalization, brightness adjustment, noise removal,
contrast enhancement, and basic quality gating (blur / darkness checks)
before the image is passed to the AI modules.
"""
import cv2
import numpy as np


class ImageQualityError(Exception):
    """Raised when an uploaded image fails minimum quality checks."""


def validate_and_preprocess(image_path: str, target_size: tuple[int, int] = (640, 640)) -> str:
    """
    Loads the image, validates quality, applies preprocessing, and
    overwrites the file with the processed version. Returns the path.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ImageQualityError("Could not read image file — file may be corrupted or unsupported format")

    _check_blur(img)
    _check_brightness(img)

    img = _denoise(img)
    img = _enhance_contrast(img)
    img = _resize(img, target_size)

    cv2.imwrite(image_path, img)
    return image_path


def _check_blur(img: np.ndarray, threshold: float = 60.0) -> None:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    if variance < threshold:
        raise ImageQualityError(
            f"Image too blurry for reliable inspection (sharpness score {variance:.1f}, minimum {threshold})"
        )


def _check_brightness(img: np.ndarray, min_mean: float = 25.0, max_mean: float = 230.0) -> None:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()
    if mean_brightness < min_mean:
        raise ImageQualityError(f"Image too dark for reliable inspection (brightness {mean_brightness:.1f})")
    if mean_brightness > max_mean:
        raise ImageQualityError(f"Image overexposed for reliable inspection (brightness {mean_brightness:.1f})")


def _denoise(img: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(img, None, 5, 5, 7, 21)


def _enhance_contrast(img: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _resize(img: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    return cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
