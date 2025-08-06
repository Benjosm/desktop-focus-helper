"""desktop_focus_helper.audio
-----------------------------------------------------------------
Simple audio playback wrapper used by the Desktop Focus Helper
application.

The module provides three public functions:

* ``play_sound(path: str)`` – attempt to play a sound file using the
  ``playsound`` package.  If playback fails for any reason (missing
  file, platform limitation, missing dependency, etc.) the function
  falls back to printing a console stub ``[AUDIO: <path>]``.  The
  fallback guarantees that the rest of the program continues to work
  even in headless or containerised environments.

* ``alert()`` – plays the *alert* cue (low‑activity audio).  The path
  is taken from ``_ALERT_SOUND`` which defaults to ``assets/alert.wav``
  but can be overridden by setting the environment variable
  ``DESK_FOCUS_ALERT_SOUND``.

* ``cheer()`` – plays the *cheer* cue (recovery audio).  The path is
  taken from ``_CHEER_SOUND`` which defaults to ``assets/cheer.wav``
  but can be overridden by setting the environment variable
  ``DESK_FOCUS_CHEER_SOUND``.

The implementation is deliberately lightweight: it does *not* raise
exceptions to the caller – any error is logged and the stub is used.
This behaviour matches the description in the repository README.
"""

import os
import sys
import logging
from typing import Optional

# Setup a module‑level logger.  If the project provides a central logger
# we use it; otherwise we fall back to a basic configuration.
try:
    # The project’s utils.logger is expected to expose a ``logger`` object.
    from desktop_focus_helper.src.utils.logger import logger  # type: ignore
except Exception:  # pragma: no cover – logger is optional in this repo
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# Configuration – paths to the two audio cues.
# Users can override these via environment variables which is handy for
# testing or custom deployments.
# -------------------------------------------------------------------------
_ALERT_SOUND: str = os.getenv(
    "DESK_FOCUS_ALERT_SOUND", "assets/alert.wav"
)
_CHEER_SOUND: str = os.getenv(
    "DESK_FOCUS_CHEER_SOUND", "assets/cheer.wav"
)

# -------------------------------------------------------------------------
def _fallback_print(path: str) -> None:
    """
    Print a simple stub that mimics audio playback.

    The stub is written to ``stdout`` so that unit tests can capture it.
    """
    print(f"[AUDIO: {path}]")

# -------------------------------------------------------------------------
def play_sound(path: str) -> None:
    """
    Attempt to play ``path`` using the ``playsound`` package.

    This function is defensive: it validates the input, ensures the
    required dependency is present, checks that the file exists, and
    catches any runtime errors.  On failure it logs a warning and falls
    back to a deterministic stub printed to ``stdout`` via
    ``_fallback_print``.  The goal is to never raise an exception to
    callers, preserving application stability in headless or minimal
    environments.

    Parameters
    ----------
    path: str
        Filesystem path to the audio file (WAV, MP3, etc.).
    """
    # Validate the path argument early.
    if not isinstance(path, str) or not path:
        logger.warning("Invalid audio path supplied to play_sound: %r", path)
        _fallback_print(path if isinstance(path, str) else "<invalid>")
        return

    # Ensure the audio file exists before attempting playback.
    if not os.path.isfile(path):
        logger.warning("Audio file not found: %s – falling back to stub.", path)
        _fallback_print(path)
        return

    try:
        # Lazy import to keep ``playsound`` optional.
        try:
            from playsound import playsound  # type: ignore
        except ImportError as imp_err:
            logger.warning(
                "playsound package not available – falling back to stub. Error: %s",
                imp_err,
            )
            _fallback_print(path)
            return

        # Attempt actual playback; ``playsound`` may raise various
        # exceptions (e.g., ``PlaysoundException``).  We catch any
        # exception to guarantee stability.
        playsound(path)
        logger.debug("Played sound: %s", path)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Audio playback failed for %s – falling back to stub. Error: %s",
            path,
            exc,
        )
        _fallback_print(path)

# -------------------------------------------------------------------------
def alert(custom_path: Optional[str] = None) -> None:
    """
    Play the *alert* cue.

    ``custom_path`` is primarily for testing; if supplied it overrides the
    configured alert sound.  Otherwise the function uses ``_ALERT_SOUND``.
    """
    path_to_play = custom_path or _ALERT_SOUND
    play_sound(path_to_play)

# -------------------------------------------------------------------------
def cheer(custom_path: Optional[str] = None) -> None:
    """
    Play the *cheer* cue.

    ``custom_path`` is primarily for testing; if supplied it overrides the
    configured cheer sound.  Otherwise the function uses ``_CHEER_SOUND``.
    """
    path_to_play = custom_path or _CHEER_SOUND
    play_sound(path_to_play)

# -------------------------------------------------------------------------
__all__ = ["play_sound", "alert", "cheer"]
