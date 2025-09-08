import math
import inspect
from pathlib import Path
from datetime import datetime, time, timedelta

# --- physical half-lives (seconds) ---
HALF_LIFE_S = {
    "tc-99m": 6.006 * 3600,           # ~6.006 h
    "lu-177": 6.644 * 24 * 3600,      # ~6.644 d
}


def _parse_hms(hms):
    parts = [int(p) for p in hms.split(":")]
    if len(parts) == 2:
        hh, mm = parts; ss = 0
    elif len(parts) == 3:
        hh, mm, ss = parts
    return time(hh, mm, ss)


def duration_seconds(start_hms, end_hms, *, next_day=False, strict_positive=False):
    """
    Duration in seconds between start_hms and end_hms.
    - next_day=False: same-day window (annual_doses). If strict_positive=True, requires end > start.
    - next_day=True : Day 1 → Day 2 (methods.py). Always adds 1 day to the end timestamp.
    """
    today = datetime.today().date()
    start_dt = datetime.combine(today, _parse_hms(start_hms))
    end_dt   = datetime.combine(today + timedelta(days=1 if next_day else 0), _parse_hms(end_hms))
    dt = (end_dt - start_dt).total_seconds()
    if strict_positive and dt <= 0:
        raise ValueError("End time must be after start time for same-day durations.")
    return dt


def cumulated_activity_Bq_s(A0_MBq, isotope, duration_s):
    """Cumulated activity in Bq·s (A0 decays physically over duration_s)."""
    A0_Bq = A0_MBq * 1e6
    T_p = HALF_LIFE_S[isotope]
    ln2 = math.log(2.0)

    A_cum = A0_Bq * T_p / ln2 * (1.0 - math.exp(-ln2 * duration_s / T_p))
    print(f"Cumulated A: {A_cum:.2f} Bq·s")

    return A_cum


DEFAULTS = {
    # methods.py (Day 1 → Day 2)
    ("methods", "main_study"): dict(isotope="tc-99m", A0_MBq=2942.4237, start="14:27", end="07:29"),
    ("methods", "pre_study"):  dict(isotope="tc-99m", A0_MBq=1134.2590, start="13:18", end="08:21"),

    # annual_doses.py (same-day)
    ("annual_doses", "tc-99m"): dict(isotope="tc-99m", A0_MBq=500.0, start="08:00", end="08:30"), # 0.5 h scan
    ("annual_doses", "lu-177"): dict(isotope="lu-177", A0_MBq=1100.0, start="08:00", end="19:00"), # numbers are placeholders
}

def cumulated_activity_auto():
    """
    One-line, zero-argument entry point.
    Detects caller script and reads its variables to choose the right defaults.

    Conventions:
      - If called from methods.py:
          * Looks for 'study_folder' in the caller's locals/globals ('main_study' or 'pre_study').
          * Uses Day-1→Day-2 window.
      - If called from annual_doses.py:
          * Looks for 'source' in the caller ('tc-99m' or 'lu-177').
          * Uses SAME-DAY window (end > start).
    All A0/times/isotope are taken from DEFAULTS above.
    """
    # identify caller frame + script name (stem)
    frame = inspect.currentframe()
    assert frame is not None
    caller = inspect.getouterframes(frame, 2)[1].frame
    fname = caller.f_code.co_filename
    stem = Path(fname).stem.lower()

    # search variables in caller (locals first, then globals)
    def _lookup(name):
        if name in caller.f_locals:  return caller.f_locals[name]
        if name in caller.f_globals: return caller.f_globals[name]
        return None

    if "methods" in stem:
        study_name = _lookup("study_folder") or "main_study"  # fallback if not set yet
        key = ("methods", str(study_name))
        cfg = DEFAULTS.get(key)
        if not cfg:
            raise KeyError(f"No defaults for {key}. Add it to activity.DEFAULTS.")
        dur_s = duration_seconds(cfg["start"], cfg["end"], next_day=True)  # Day 1 → Day 2
        return cumulated_activity_Bq_s(cfg["A0_MBq"], cfg["isotope"], dur_s)

    if "annual_doses" in stem:
        source = (_lookup("source") or "tc-99m").lower()
        key = ("annual_doses", source)
        cfg = DEFAULTS.get(key)
        if not cfg:
            raise KeyError(f"No defaults for {key}. Add it to activity.DEFAULTS.")
        dur_s = duration_seconds(cfg["start"], cfg["end"], strict_positive=True)  # same day, end > start
        return cumulated_activity_Bq_s(cfg["A0_MBq"], cfg["isotope"], dur_s)