import datetime
import time
import os
import random
import psutil
import pyautogui
import subprocess
import pygetwindow as gw
import win32con
import win32gui
import re
import threading
from typing import List, Optional, Callable, Dict

try:
    import keyboard  # type: ignore
except ImportError:
    keyboard = None


# ================================= LOGGING =================================

def log(text: str) -> None:
    """Write a timestamped log line to stdout."""
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    log_message = f"{timestamp} - {text}"
    print(log_message)


# ============================== WINDOW HELPERS ==============================

def focus_window(window_title: str) -> None:
    """Bring the first window with the given title to the foreground."""
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        windows[0].activate()
        log(f"Focused window: {window_title}")
    else:
        log(f"No window found with title: {window_title}")


def find_windows(title_pattern: str, ignore_case: bool = True) -> List[gw.Win32Window]:
    """Return all windows whose title matches a regex pattern."""
    flags = re.IGNORECASE if ignore_case else 0
    pat = re.compile(title_pattern, flags)
    return [w for w in gw.getAllWindows() if pat.search(w.title or "")]


def wait_for_window(title_pattern: str, timeout: int = 30) -> Optional[gw.Win32Window]:
    """Wait until a window appears with the given title regex; return the window or None."""
    log(f"Waiting for window '{title_pattern}'...")
    start = time.time()
    while time.time() - start < timeout:
        wins = find_windows(title_pattern)
        if wins:
            log(f"Window found: {wins[0].title}")
            return wins[0]
        time.sleep(1)
    log(f"Timeout waiting for window '{title_pattern}'.")
    return None


def minimize_window(title_pattern: str) -> bool:
    """Minimize the first window whose title matches a regex pattern."""
    wins = find_windows(title_pattern)
    if not wins:
        return False
    try:
        wins[0].minimize()
        log(f"Minimized window: {wins[0].title}")
        return True
    except Exception as e:
        log(f"Failed to minimize: {e}")
        return False


def close_window_by_title_part(title_part: str) -> None:
    """Send WM_CLOSE to any visible window whose title contains a substring."""

    def enum_windows_kill(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and title_part in win32gui.GetWindowText(hwnd):
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    win32gui.EnumWindows(enum_windows_kill, None)
    log(f"Closed windows containing: {title_part}")


def close_all_windows(title_pattern: str) -> None:
    """Close all windows that match a title regex."""
    wins = find_windows(title_pattern)
    for w in wins:
        try:
            w.close()
        except Exception:
            pass
    log(f"Closed {len(wins)} windows matching '{title_pattern}'.")


# ================================ PROCESSES =================================

def is_exe_running(exe_name: str) -> bool:
    """Check if a process with a given name is running."""
    for process in psutil.process_iter():
        try:
            if exe_name.lower() in (process.name() or "").lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def wait_for_exe(exe_name: str, timeout: int = 30) -> bool:
    """Wait until a process starts running; return True if found within timeout."""
    log(f"Waiting for {exe_name} to start...")
    start = time.time()
    while time.time() - start < timeout:
        if is_exe_running(exe_name):
            log(f"{exe_name} started!")
            return True
        time.sleep(1)
    log(f"Timeout waiting for {exe_name}.")
    return False


def killProcess(process: str) -> None:
    """Force-kill a single process by name (taskkill)."""
    subprocess.Popen(
        f"taskkill /F /IM {process}.exe",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    log(f"Killed process: {process}.exe")


def kill_all_by_name(process_name: str) -> None:
    """Kill all processes that contain the given name."""
    for p in psutil.process_iter():
        try:
            if process_name.lower() in (p.name() or "").lower():
                p.kill()
                log(f"Killed: {p.name()} (PID {p.pid})")
        except Exception:
            pass


def reboot() -> None:
    """Reboot the Windows machine immediately (`shutdown /r /t 1`)."""
    os.system("shutdown /r /t 1")


# ============================== MOUSE & KEYBOARD ============================

def screenshot(name: str = "screenshot") -> str:
    """Take a screenshot and save it under `screenshots/` with timestamp; return path."""
    os.makedirs("screenshots", exist_ok=True)
    filename = f"screenshots/{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pyautogui.screenshot(filename)
    log(f"Screenshot saved: {filename}")
    return filename


def move_mouse_safe(x: int, y: int, duration: float = 0.3) -> None:
    """Move the mouse smoothly to the given coordinates."""
    pyautogui.moveTo(x, y, duration=duration)
    log(f"Moved mouse to ({x}, {y})")


def press_key(key: str) -> None:
    """Press a key (full press)."""
    pyautogui.press(key)
    log(f"Pressed key: {key}")


def type_text(text: str, delay: float = 0.05) -> None:
    """Type text character by character (human-like)."""
    for char in text:
        pyautogui.typewrite(char)
        time.sleep(delay)
    log(f"Typed text: '{text}'")


def random_sleep(min_s: float = 0.5, max_s: float = 1.5) -> None:
    """Sleep for a random time between given seconds (adds realism)."""
    dur = random.uniform(min_s, max_s)
    time.sleep(dur)
    log(f"Slept for {dur:.2f} seconds")


# --- NEW: Keyboard hold/release utilities ---

def key_down(key: str) -> None:
    """Hold a keyboard key down (no release)."""
    pyautogui.keyDown(key)
    log(f"Key down: {key}")


def key_up(key: str) -> None:
    """Release a previously held keyboard key."""
    pyautogui.keyUp(key)
    log(f"Key up: {key}")


def press_and_hold(key: str, seconds: float = 1.0) -> None:
    """Press and hold a key for a duration, then release."""
    pyautogui.keyDown(key)
    log(f"Key down: {key} (holding {seconds:.2f}s)")
    time.sleep(seconds)
    pyautogui.keyUp(key)
    log(f"Key up: {key}")


# --- NEW: Mouse hold/release utilities ---

def mouse_down(button: str = "left") -> None:
    """Hold a mouse button down ('left', 'right', 'middle')."""
    pyautogui.mouseDown(button=button)
    log(f"Mouse down: {button}")


def mouse_up(button: str = "left") -> None:
    """Release a previously held mouse button."""
    pyautogui.mouseUp(button=button)
    log(f"Mouse up: {button}")


def click_and_hold(seconds: float = 1.0, button: str = "left") -> None:
    """Click and hold a mouse button for a duration, then release."""
    pyautogui.mouseDown(button=button)
    log(f"Mouse down: {button} (holding {seconds:.2f}s)")
    time.sleep(seconds)
    pyautogui.mouseUp(button=button)
    log(f"Mouse up: {button}")


# ============================== IMAGE FIND/CLICK ============================

def find(image: str, breaking: bool = True, confidence: float = 0.8) -> bool:
    """Poll the screen until an image is found. Returns True when found, False otherwise."""
    while True:
        try:
            location = pyautogui.locateOnScreen(f'./img/{image}.png', grayscale=False, confidence=confidence)
            if location is not None:
                log(f"I found {image}!")
                return True
        except Exception:
            # PyAutoGUI typically returns None; any exception is treated like "not found yet"
            pass

        if breaking:
            log(f"{image} icon not found, retrying...")
            time.sleep(1)
        else:
            log(f"{image} icon not found, skipping...")
            break
    return False


def find_and_click(image: str, breaking: bool = True, confidence: float = 0.8, double: bool = False) -> bool:
    """Poll the screen for an image and click its center when found. Returns True if clicked."""
    while True:
        try:
            location = pyautogui.locateOnScreen(f'./img/{image}.png', grayscale=False, confidence=confidence)
            if location is not None:
                x, y = pyautogui.center(location)
                if double:
                    pyautogui.doubleClick(x, y)
                else:
                    pyautogui.click(x, y)
                log(f"I found {image} and clicked it!")
                return True
        except Exception:
            pass

        if breaking:
            log(f"{image} icon not found, retrying...")
            time.sleep(1)
        else:
            log(f"{image} icon not found, skipping...")
            break
    return False


def safe_find_and_click(image: str, timeout: int = 20, confidence: float = 0.8) -> bool:
    """Try to find and click an image, but give up after a timeout; return True if clicked."""
    log(f"Waiting up to {timeout}s for {image} to appear...")
    start = time.time()
    while time.time() - start < timeout:
        if find_and_click(image, breaking=False, confidence=confidence):
            return True
        time.sleep(1)
    log(f"Timeout waiting for {image}.")
    return False


def find_and_right_click(image: str, breaking: bool = True, confidence: float = 0.8) -> bool:
    """Poll the screen for an image and right-click its center when found. Returns True if clicked."""
    while True:
        try:
            location = pyautogui.locateOnScreen(f'./img/{image}.png', grayscale=False, confidence=confidence)
            if location is not None:
                x, y = pyautogui.center(location)
                pyautogui.click(x, y, button='right')
                log(f"I found {image} and right-clicked it!")
                return True
        except Exception:
            pass

        if breaking:
            log(f"{image} icon not found, retrying...")
            time.sleep(1)
        else:
            log(f"{image} icon not found, skipping...")
            break
    return False


# ================================ HOTKEY CORE ===============================

# Internal state via Events
_RUN_EVENT = threading.Event()  # "may run" flag
_PAUSE_EVENT = threading.Event()  # "pause is active"
_STOP_EVENT = threading.Event()  # definitive stop requested
_THREAD_REF: Optional[threading.Thread] = None
_HOTKEY_HANDLES: list = []  # to unhook hotkeys later


def _require_keyboard():
    """Raise a helpful error if 'keyboard' is not installed."""
    if keyboard is None:
        raise RuntimeError(
            "Hotkeys require the 'keyboard' package. Install with: pip install keyboard\n"
            "On Windows, Administrator privileges may be required for global hotkeys."
        )


def is_running() -> bool:
    """Return True if the task is marked as running and not stopped."""
    return _RUN_EVENT.is_set() and not _STOP_EVENT.is_set()


def is_paused() -> bool:
    """Return True if pause is active."""
    return _PAUSE_EVENT.is_set()


def should_run() -> bool:
    """
    Shortcut for cooperative loops:
    Return False if a stop was requested, or not running, or currently paused.
    """
    return is_running() and not is_paused()


def request_start() -> None:
    """Mark the system as running (clears stop & pause)."""
    _STOP_EVENT.clear()
    _PAUSE_EVENT.clear()
    _RUN_EVENT.set()
    log("▶️  START requested")


def request_pause_toggle() -> None:
    """Toggle pause state."""
    if _PAUSE_EVENT.is_set():
        _PAUSE_EVENT.clear()
        log("⏯️  RESUME")
    else:
        _PAUSE_EVENT.set()
        log("⏸️  Pause (after current loop)")


def request_stop() -> None:
    """Request a definitive stop (also clears running)."""
    _STOP_EVENT.set()
    _RUN_EVENT.clear()
    log("⏹️  STOP requested")


def wait_until_stopped() -> None:
    """Block until a stop is requested (e.g., user pressed Stop hotkey)."""
    _STOP_EVENT.wait()


def run_with_controls(task_fn: Callable[..., None], *args, **kwargs) -> None:
    """
    Run your task function in a background thread with Start/Stop/Pause controls.

    Your task_fn should be cooperative:
      - if not should_run(): break     # respect stop or not-running
      - while is_paused(): sleep       # pause loop

    Example
    -------
    def my_task():
        while True:
            if not should_run():
                break
            while is_paused():
                time.sleep(0.2)
            # ...do work...
            time.sleep(0.1)

    request_start()
    run_with_controls(my_task)
    """
    global _THREAD_REF

    if _THREAD_REF and _THREAD_REF.is_alive():
        log("A task is already running; ignoring new run request.")
        return

    def _runner():
        try:
            log("Bot thread started.")
            task_fn(*args, **kwargs)
        except Exception as e:
            log(f"Bot crashed: {e}")
        finally:
            # When the task finishes or crashes, reset running state
            _RUN_EVENT.clear()
            _PAUSE_EVENT.clear()
            log("Bot thread finished.")

    _THREAD_REF = threading.Thread(target=_runner, daemon=True)
    _THREAD_REF.start()


# ================================ HOTKEY API ================================

def setup_hotkeys(
        start_key: str = "F1",
        stop_key: str = "F2",
        pause_key: str = "F3",
        screenshot_key: Optional[str] = None,
        custom_hotkeys: Optional[Dict[str, Callable[[], None]]] = None,
) -> None:
    """
    Register global hotkeys for Start/Stop/Pause and optional extras.

    Parameters
    ----------
    start_key : str
        Keyboard shortcut to set running state (default: 'F1').
    stop_key : str
        Keyboard shortcut to request stop (default: 'F2').
    pause_key : str
        Keyboard shortcut to toggle pause (default: 'F3').
    screenshot_key : Optional[str]
        If provided, take a screenshot on this key (e.g., 'F12').
    custom_hotkeys : Optional[Dict[str, Callable]]
        Map of 'hotkey' -> callable for any extra bindings.
        Example: {'ctrl+alt+h': lambda: log('Hello')}

    Notes
    -----
    - Uses the 'keyboard' library for global system-wide hotkeys.
    - Keep a reference to unhook later with `remove_hotkeys()`.
    """
    _require_keyboard()

    # Unhook existing first if any
    remove_hotkeys()

    # Start
    _HOTKEY_HANDLES.append(keyboard.add_hotkey(start_key, request_start))
    log(f"Hotkey bound: {start_key} → START")

    # Stop
    _HOTKEY_HANDLES.append(keyboard.add_hotkey(stop_key, request_stop))
    log(f"Hotkey bound: {stop_key} → STOP")

    # Pause/Resume toggle
    _HOTKEY_HANDLES.append(keyboard.add_hotkey(pause_key, request_pause_toggle))
    log(f"Hotkey bound: {pause_key} → PAUSE/RESUME")

    # Optional screenshot
    if screenshot_key:
        _HOTKEY_HANDLES.append(keyboard.add_hotkey(screenshot_key, lambda: screenshot("hotkey")))
        log(f"Hotkey bound: {screenshot_key} → SCREENSHOT")

    # Custom mappings
    if custom_hotkeys:
        for hk, fn in custom_hotkeys.items():
            _HOTKEY_HANDLES.append(keyboard.add_hotkey(hk, fn))
            log(f"Hotkey bound: {hk} → {getattr(fn, '__name__', 'callback')}")


def remove_hotkeys() -> None:
    """Unregister all previously registered hotkeys."""
    if keyboard is None:
        return
    try:
        for h in _HOTKEY_HANDLES:
            keyboard.remove_hotkey(h)
    finally:
        _HOTKEY_HANDLES.clear()
        log("All hotkeys removed.")


def hotkey_wait_loop(block: bool = True) -> None:
    """
    Optionally block the main thread to keep hotkeys alive.

    - If block=True, this will wait until a STOP is requested.
    - If block=False, returns immediately (useful if your script already blocks).
    """
    if keyboard is None:
        log("keyboard module not available; cannot enter wait loop.")
        return
    if block:
        log("Hotkey wait loop active. Press your Stop hotkey to exit.")
        wait_until_stopped()
        remove_hotkeys()
        log("Exiting hotkey wait loop.")


def run_hotkey_bot(bot_function: Callable[[], None]) -> None:
    """
    Universal hotkey-driven controller.
    - Press F2 to start a run.
    - Press F3 to pause/resume.
    - Press F4 to stop completely and exit.

    The bot_function is executed once per start trigger.
    After completion, you can press F2 again to run it again.
    """
    setup_hotkeys(start_key="F2", stop_key="F4", pause_key="F3", screenshot_key="F12")
    log("Ready. Press F2 to start a run, F4 to stop.")

    try:
        while True:
            # Wait for a Start (F2)
            while not is_running():
                if _STOP_EVENT.is_set():
                    raise SystemExit
                time.sleep(0.1)

            # Start a new run if no thread active
            if not (_THREAD_REF and _THREAD_REF.is_alive()):
                run_with_controls(bot_function)

            # Wait for completion or Stop
            while _THREAD_REF and _THREAD_REF.is_alive():
                if _STOP_EVENT.is_set():
                    break
                time.sleep(0.2)

            # If Stop pressed, exit cleanly
            if _STOP_EVENT.is_set():
                break
    finally:
        remove_hotkeys()
        log("Bot controller stopped.")
