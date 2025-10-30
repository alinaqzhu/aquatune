import sys, os, random
import numpy as np
from pydub import AudioSegment
from scipy.signal import butter, lfilter

# ---------------------------
# Utility: filters & helpers
# ---------------------------
def butter_lowpass_filter(x, cutoff_hz, fs, order=6):
    nyq = 0.5 * fs
    b, a = butter(order, cutoff_hz/nyq, btype="low")
    return lfilter(b, a, x)

def to_float32(seg):
    s = np.array(seg.get_array_of_samples()).astype(np.float32)
    if seg.channels == 2:
        s = s.reshape(-1, 2)
    else:
        s = s.reshape(-1, 1)
    peak = max(1e-9, np.max(np.abs(s)))
    return s / peak, seg.frame_rate

def to_audiosegment(arr, fs):
    arr = arr / (np.max(np.abs(arr)) + 1e-9)  # normalize
    arr_i16 = (arr * 32767.0).astype(np.int16)
    ch = 2 if arr.shape[1] == 2 else 1
    return AudioSegment(
        arr_i16.tobytes(), frame_rate=fs, sample_width=2, channels=ch
    )

def mix_at(base: AudioSegment, overlay: AudioSegment, position_ms: int, gain_db: float = 0.0):
    return base.overlay(overlay + gain_db, position=position_ms)

# ---------------------------
# Base underwater muffling
# ---------------------------
def apply_underwater_muffle(seg: AudioSegment, cutoff_hz=1500.0):
    s, fs = to_float32(seg)
    # channel-wise low-pass
    for c in range(s.shape[1]):
        s[:, c] = butter_lowpass_filter(s[:, c], cutoff_hz, fs, order=6)
    return to_audiosegment(s, fs)

# ---------------------------
# Bubble generator (filtered noise)
# ---------------------------
def gen_bubble(duration_ms=300, fs=44100, lowpass_hz=800, gain_db=-12):
    n = int(fs * duration_ms / 1000.0)
    noise = np.random.normal(0.0, 0.35, n).astype(np.float32)
    # envelope (fast attack, exponential decay)
    t = np.linspace(0, duration_ms/1000.0, n, endpoint=False)
    env = np.minimum(1.0, t*25) * np.exp(-t*4.0)  # attack then decay
    bubble = noise * env
    bubble = butter_lowpass_filter(bubble, lowpass_hz, fs, order=6)
    # mono segment; pydub will center it when overlaying onto stereo
    bubble_seg = to_audiosegment(bubble.reshape(-1,1), fs) + gain_db
    return bubble_seg

# ---------------------------
# Droplet/ripple "plink" generator (decaying tone w/ slight pitch bend)
# ---------------------------
def gen_droplet(duration_ms=150, fs=44100, f0=1400, bend_semitones=-4, gain_db=-10):
    n = int(fs * duration_ms / 1000.0)
    t = np.linspace(0, duration_ms/1000.0, n, endpoint=False)
    # exponential decay
    env = np.exp(-t*10.0)
    # slight downward pitch bend
    f_t = f0 * (2 ** (bend_semitones * (t / (duration_ms/1000.0)) / 12.0))
    phase = 2*np.pi * np.cumsum(f_t) / fs
    tone = np.sin(phase) * env
    # soft lowpass to keep it gentle
    tone = butter_lowpass_filter(tone, 2500, fs, order=4)
    tone_seg = to_audiosegment(tone.reshape(-1,1), fs) + gain_db
    return tone_seg

# ---------------------------
# Build versions
# ---------------------------
def build_underwater_only(input_seg):
    return apply_underwater_muffle(input_seg, cutoff_hz=1200.0)

def build_underwater_with_bubbles(input_seg, bubble_count=18, seed=42):
    random.seed(seed)
    base = build_underwater_only(input_seg)
    length_ms = len(base)
    for _ in range(bubble_count):
        dur = random.randint(180, 400)
        lp = random.choice([600, 800, 1000])
        gain = random.choice([-15, -12, -9])
        bubble = gen_bubble(duration_ms=dur, fs=base.frame_rate, lowpass_hz=lp, gain_db=gain)
        pos = random.randint(0, max(0, length_ms - dur))
        base = mix_at(base, bubble, pos)
    return base

def build_underwater_with_bubbles_and_droplets(input_seg, bubble_count=15, droplet_count=10, seed=123):
    random.seed(seed)
    base = build_underwater_only(input_seg)
    length_ms = len(base)
    # bubbles
    for _ in range(bubble_count):
        dur = random.randint(180, 380)
        lp = random.choice([600, 800, 1000])
        gain = random.choice([-15, -12, -9])
        bubble = gen_bubble(duration_ms=dur, fs=base.frame_rate, lowpass_hz=lp, gain_db=gain)
        pos = random.randint(0, max(0, length_ms - dur))
        base = mix_at(base, bubble, pos)
    # droplets
    for _ in range(droplet_count):
        dur = random.randint(100, 180)
        f0  = random.choice([1200, 1400, 1600, 1800])
        bend = random.choice([-6, -4, -3])
        gain = random.choice([-14, -12, -10])
        plink = gen_droplet(duration_ms=dur, fs=base.frame_rate, f0=f0, bend_semitones=bend, gain_db=gain)
        pos = random.randint(0, max(0, length_ms - dur))
        base = mix_at(base, plink, pos)
    return base

# ---------------------------
# Main
# ---------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python aquatune_underwater_fx.py /path/to/input.mp3")
        sys.exit(1)

    in_path = sys.argv[1]
    if not os.path.exists(in_path):
        print(f"File not found: {in_path}")
        sys.exit(1)

    # Load (pydub will use ffmpeg)
    print("Loading audio…")
    base = AudioSegment.from_file(in_path)

    # Ensure a standard sample rate for synthetic overlays
    if base.frame_rate < 32000:
        base = base.set_frame_rate(44100)

    stem = os.path.splitext(in_path)[0]
    out1 = f"{stem}_Underwater.mp3"
    out2 = f"{stem}_Underwater_Bubbles.mp3"
    out3 = f"{stem}_Underwater_Bubbles_Droplets.mp3"

    print("Rendering Version 1 (Underwater Only)…")
    v1 = build_underwater_only(base)
    v1.export(out1, format="mp3")
    print(f"Saved: {out1}")

    print("Rendering Version 2 (Underwater + Random Bubbles)…")
    v2 = build_underwater_with_bubbles(base, bubble_count=18, seed=42)
    v2.export(out2, format="mp3")
    print(f"Saved: {out2}")

    print("Rendering Version 3 (Underwater + Bubbles + Droplets)…")
    v3 = build_underwater_with_bubbles_and_droplets(base, bubble_count=15, droplet_count=10, seed=123)
    v3.export(out3, format="mp3")
    print(f"Saved: {out3}")

if __name__ == "__main__":
    main()


