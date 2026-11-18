from dataclasses import dataclass
from enum import Enum


class Gesture(str, Enum):
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"
    OPEN_PALM = "OPEN_PALM"
    FIST = "FIST"
    THUMBS_UP = "THUMBS_UP"
    THUMBS_DOWN = "THUMBS_DOWN"
    VICTORY = "VICTORY"
    POINTING_UP = "POINTING_UP"
    PINCH = "PINCH"
    ROCK = "ROCK"
    TRIANGLE = "TRIANGLE"
    DOUBLE_FIST = "DOUBLE_FIST"
    DOUBLE_THUMBS_UP = "DOUBLE_THUMBS_UP"


class Motion(str, Enum):
    NONE = "NONE"
    SWIPE_LEFT = "SWIPE_LEFT"
    SWIPE_RIGHT = "SWIPE_RIGHT"
    SWIPE_UP = "SWIPE_UP"
    SWIPE_DOWN = "SWIPE_DOWN"


class Quality(str, Enum):
    VALID = "VALID"
    NO_HAND = "NO_HAND"
    INVALID = "INVALID"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    OUT_OF_FRAME = "OUT_OF_FRAME"
    MULTIPLE_HANDS = "MULTIPLE_HANDS"


@dataclass(frozen=True)
class GestureConfig:
    # Reject ambiguous handedness; score is not landmark visibility.
    handedness_min: float = 0.7
    confidence_cap: float = 0.85  # heuristic score, not calibrated probability
    # Palm must occupy at least 2% of the longer image dimension.
    min_palm_size: float = 0.02
    extended_ratio: float = (
        0.84  # tip chord / total finger path (slightly widened for natural finger flex)
    )
    folded_ratio: float = 0.76  # gap between thresholds is an abstention band
    tip_reach: float = 1.02  # tip must be further from wrist than PIP
    thumb_ratio: float = 0.80
    thumb_reach: float = 0.60  # thumb tip to thumb MCP / palm size
    pinch_distance: float = 0.25  # thumb-index tip distance / palm size
    pinch_reach: float = 0.90  # reject touching tips next to wrist in a fist
    spread_distance: float = 0.15  # adjacent fingertips / palm size
    vertical_dominance: float = 1.15  # thumb screen-y / screen-x (tolerant to natural tilt)
    ema_alpha: float = 0.65
    tracking_gap_ms: int = 250
    debounce_frames: int = 5
    debounce_ms: int = 700
    release_ms: int = 1000
    static_cooldown_ms: int = 1000


@dataclass(frozen=True)
class MotionConfig:
    distance: float = 0.25  # normalized frame width/height
    max_duration_ms: int = 700
    min_samples: int = 3
    dominance: float = 1.5  # dominant displacement / perpendicular displacement
    efficiency: float = 0.85  # displacement / trajectory length
    max_gap_ms: int = 250
    max_step: float = 0.35  # reject teleportation per sample (supports fast natural swipes)
    cooldown_ms: int = 1500
    max_samples: int = 240  # bounded history, including high-rate input


@dataclass(frozen=True)
class Classification:
    gesture: Gesture
    confidence: float
    quality: Quality
    feedback: str
