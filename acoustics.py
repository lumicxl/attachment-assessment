import os
import numpy as np
import parselmouth
from parselmouth.praat import call


def extract_features(wav_path):
    if not os.path.exists(wav_path):
        return {}

    try:
        sound = parselmouth.Sound(wav_path)
    except Exception:
        return {}

    duration = sound.get_total_duration()
    if duration <= 0:
        return {}

    pitch = sound.to_pitch()
    f0_values = pitch.selected_array["frequency"]
    f0_values = f0_values[f0_values > 0]

    f0_mean = float(np.mean(f0_values)) if len(f0_values) else 0.0
    f0_sd = float(np.std(f0_values)) if len(f0_values) else 0.0

    intensity = sound.to_intensity()
    intensity_values = intensity.values[0]
    intensity_values = intensity_values[~np.isnan(intensity_values)]

    intensity_mean = float(np.mean(intensity_values)) if len(intensity_values) else 0.0
    intensity_sd = float(np.std(intensity_values)) if len(intensity_values) else 0.0

    try:
        point_process = call(sound, "To PointProcess (periodic, cc)", 75, 600)
        jitter = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        shimmer = call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    except Exception:
        jitter = 0.0
        shimmer = 0.0

    pauses = detect_pauses(sound)
    pause_count = len(pauses)
    pause_mean = float(np.mean(pauses)) if pauses else 0.0
    pause_max = float(np.max(pauses)) if pauses else 0.0

    speech_rate = 0.0
    if duration > 0:
        speech_rate = max(0.0, (duration - sum(pauses)) / duration)

    return {
        "duration": round(duration, 3),
        "f0_mean": round(f0_mean, 2),
        "f0_sd": round(f0_sd, 2),
        "speech_rate": round(speech_rate, 3),
        "pause_count": pause_count,
        "pause_mean": round(pause_mean, 3),
        "pause_max": round(pause_max, 3),
        "intensity_mean": round(intensity_mean, 2),
        "intensity_sd": round(intensity_sd, 2),
        "jitter": round(float(jitter), 5) if jitter else 0.0,
        "shimmer": round(float(shimmer), 5) if shimmer else 0.0,
    }


def detect_pauses(sound, threshold_db=-25, min_pause=0.2):
    intensity = sound.to_intensity()
    values = intensity.values[0]
    times = intensity.xs()
    if len(values) == 0:
        return []

    silent = values < threshold_db
    pauses = []
    start = None
    for i, s in enumerate(silent):
        if s and start is None:
            start = times[i]
        elif not s and start is not None:
            length = times[i] - start
            if length >= min_pause:
                pauses.append(length)
            start = None
    return pauses