"""
Unit tests for ``desktop_focus_helper.audio``.

The tests cover three scenarios:
1. Successful playback – the ``playsound`` function is called with the
   correct argument.
2. Missing file – ``playsound`` raises ``FileNotFoundError``; the module
   should fall back to printing a stub.
3. Playback failure – ``playsound`` raises a generic exception; the
   fallback stub should also be printed.

The implementation of ``audio.play_sound`` lazily imports ``playsound``,
therefore the tests monkey‑patch ``sys.modules['playsound']`` with a
dummy module exposing a ``playsound`` function that we control.
"""

import builtins
import importlib
import sys
from types import SimpleNamespace
from io import StringIO

import pytest

# The module under test
import audio

# -------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_modules(monkeypatch):
    """
    Ensure that each test gets a fresh import of ``audio`` so that changes
    to ``sys.modules['playsound']`` are respected.
    """
    # Remove the module if it has already been imported.
    if "audio" in sys.modules:
        del sys.modules["audio"]
    # Re-import after the test finishes.
    yield
    if "audio" in sys.modules:
        del sys.modules["audio"]

# -------------------------------------------------------------------------
def _install_fake_playsound(monkeypatch, side_effect=None):
    """
    Install a dummy ``playsound`` module that records calls.

    Parameters
    ----------
    monkeypatch: pytest.MonkeyPatch
        The fixture used to modify ``sys.modules`` safely.
    side_effect: Callable | Exception | None
        If a callable, it will be invoked with the path argument.
        If an Exception instance, it will be raised when the function is
        called.  ``None`` means the function succeeds silently.
    """
    def fake_playsound(path):
        if isinstance(side_effect, Exception):
            raise side_effect
        if callable(side_effect):
            return side_effect(path)
        # Successful no‑op
        return None

    fake_module = SimpleNamespace(playsound=fake_playsound)
    monkeypatch.setitem(sys.modules, "playsound", fake_module)

# -------------------------------------------------------------------------
def test_play_sound_success(monkeypatch):
    """
    When ``playsound`` works, ``audio.play_sound`` should call it with the
    provided path and **not** print a fallback stub.
    """
    captured_path = {}

    def record_path(p):
        captured_path["called_with"] = p

    _install_fake_playsound(monkeypatch, side_effect=record_path)

    # Capture stdout to ensure no fallback is printed
    stdout = StringIO()
    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: stdout.write(" ".join(map(str, args)) + "\n"))

    import importlib
    mod = importlib.import_module("audio")
    mod.play_sound("dummy.wav")

    assert captured_path.get("called_with") == "dummy.wav"
    assert stdout.getvalue() == ""  # No fallback output

# -------------------------------------------------------------------------
@pytest.mark.parametrize(
    "exception,expected_msg",
    [
        (FileNotFoundError("no such file"), "[AUDIO: missing.wav]"),
        (RuntimeError("playback failed"), "[AUDIO: broken.wav]"),
    ],
)
def test_play_sound_fallback(monkeypatch, exception, expected_msg):
    """
    If ``playsound`` raises an exception, ``audio.play_sound`` must fall back
    to printing a stub of the form ``[AUDIO: <path>]``.
    """
    _install_fake_playsound(monkeypatch, side_effect=exception)

    # Capture stdout
    stdout = StringIO()
    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: stdout.write(" ".join(map(str, args)) + "\n"))

    import importlib
    mod = importlib.import_module("audio")
    mod.play_sound("missing.wav" if isinstance(exception, FileNotFoundError) else "broken.wav")

    # The stub should be printed exactly once
    assert stdout.getvalue().strip() == expected_msg

# -------------------------------------------------------------------------
def test_alert_and_cheer_use_configured_paths(monkeypatch):
    """
    ``alert`` and ``cheer`` should delegate to ``play_sound`` using the
    configured default paths when no custom path is supplied.
    """
    # We'll monkey‑patch ``audio.play_sound`` to record calls.
    called = {"alert": None, "cheer": None}

    def fake_play_sound(path):
        if path == audio._ALERT_SOUND:
            called["alert"] = path
        elif path == audio._CHEER_SOUND:
            called["cheer"] = path

    monkeypatch.setattr(audio, "play_sound", fake_play_sound)

    # Ensure the environment variables are not set for this test.
    monkeypatch.delenv("DESK_FOCUS_ALERT_SOUND", raising=False)
    monkeypatch.delenv("DESK_FOCUS_CHEER_SOUND", raising=False)

    # Re‑import the module to refresh the constants with default values.
    import importlib
    importlib.reload(audio)

    audio.alert()
    audio.cheer()

    assert called["alert"] == "assets/alert.wav"
    assert called["cheer"] == "assets/cheer.wav"

# -------------------------------------------------------------------------
def test_alert_custom_path(monkeypatch):
    """
    Supplying a custom path to ``alert`` should bypass the configured
    default and use the provided value.
    """
    captured = {"path": None}

    def fake_play_sound(path):
        captured["path"] = path

    monkeypatch.setattr(audio, "play_sound", fake_play_sound)

    audio.alert(custom_path="custom/alert.mp3")
    assert captured["path"] == "custom/alert.mp3"

# -------------------------------------------------------------------------
def test_cheer_custom_path(monkeypatch):
    """
    Supplying a custom path to ``cheer`` should bypass the configured
    default and use the provided value.
    """
    captured = {"path": None}

    def fake_play_sound(path):
        captured["path"] = path

    monkeypatch.setattr(audio, "play_sound", fake_play_sound)

    audio.cheer(custom_path="custom/cheer.mp3")
    assert captured["path"] == "custom/cheer.mp3"
