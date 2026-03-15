"""
SPLIT -- Adaptive Music System
Synthesized musical loops per MusicZone, crossfading between zones,
combat intensity layers, and one-shot stingers. All audio is generated
at startup via numpy -- no external music files required.

Uses arpeggiation, decay envelopes, vibrato, detuning, filtered noise,
and rhythmic gating to produce musical (non-droning) output from pure
synthesis.  Inspired by Hollow Knight's orchestral atmosphere.

If numpy is unavailable the system stays completely silent. Never crashes.
"""

import random

import pygame

from game.engine.settings import (
    AUDIO_SAMPLE_RATE,
    AUDIO_CHANNELS,
    AUDIO_BUFFER,
    MUSIC_CHANNELS,
    STINGER_CHANNELS,
    MusicZone,
)

# ---------------------------------------------------------------------------
# Numpy -- optional
# ---------------------------------------------------------------------------

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CROSSFADE_FRAMES = 120          # ~2 seconds at 60 fps
_LOOP_DURATION_S = 3.0           # each looping buffer is 3 seconds
_SAMPLE_RATE = AUDIO_SAMPLE_RATE

# ---------------------------------------------------------------------------
# Synthesis helpers
# ---------------------------------------------------------------------------

def _sine(freq, dur_s, sr=_SAMPLE_RATE):
    """Pure sine wave, float64 mono."""
    n = int(sr * dur_s)
    if n == 0:
        return np.zeros(1)
    t = np.linspace(0, dur_s, n, endpoint=False)
    return np.sin(2 * np.pi * freq * t)


def _sine_vibrato(freq, dur_s, vib_rate=5.0, vib_depth=0.02, sr=_SAMPLE_RATE):
    """Sine wave with vibrato (frequency LFO)."""
    n = int(sr * dur_s)
    if n == 0:
        return np.zeros(1)
    t = np.linspace(0, dur_s, n, endpoint=False)
    mod = 1.0 + vib_depth * np.sin(2 * np.pi * vib_rate * t)
    phase = 2 * np.pi * freq * np.cumsum(mod) / sr
    return np.sin(phase)


def _noise(dur_s, sr=_SAMPLE_RATE):
    """White noise, mono."""
    return np.random.uniform(-1, 1, int(sr * dur_s))


def _filtered_noise(dur_s, cutoff_ratio=0.02, sr=_SAMPLE_RATE):
    """Low-pass filtered noise for soft texture (simple moving average)."""
    raw = np.random.uniform(-1, 1, int(sr * dur_s))
    # Simple low-pass via cumulative sum trick
    window = max(int(sr * cutoff_ratio), 1)
    kernel = np.ones(window) / window
    # Convolve and trim to original length
    filtered = np.convolve(raw, kernel, mode='same')
    # Normalise
    peak = np.max(np.abs(filtered))
    if peak > 0:
        filtered /= peak
    return filtered


def _envelope(signal, attack_s, release_s, sr=_SAMPLE_RATE):
    """Simple attack-sustain-release envelope."""
    n = len(signal)
    env = np.ones(n)
    att = min(int(sr * attack_s), n)
    rel = min(int(sr * release_s), n)
    if att > 0:
        env[:att] = np.linspace(0, 1, att)
    if rel > 0:
        env[-rel:] = np.linspace(1, 0, rel)
    return signal * env


def _note(freq, dur_s, harmonics=3, detune=0.003, vib_rate=4.5,
          vib_depth=0.008, sr=_SAMPLE_RATE):
    """A single musical note with harmonics, detuning, and vibrato.

    Much richer than a pure sine -- avoids the 'humming' problem by
    distributing energy across multiple partials with slight detuning.
    """
    n = int(sr * dur_s)
    if n == 0:
        return np.zeros(1)
    t = np.linspace(0, dur_s, n, endpoint=False)

    # Vibrato LFO (shared across harmonics for coherence)
    vib = 1.0 + vib_depth * np.sin(2 * np.pi * vib_rate * t)

    out = np.zeros(n)
    for h in range(1, harmonics + 1):
        # Each harmonic is slightly detuned
        det = 1.0 + detune * (h - 1) * (1 if h % 2 == 0 else -1)
        f = freq * h * det
        phase = 2 * np.pi * f * np.cumsum(vib) / sr
        # Amplitude falls off with harmonic number
        amp = 1.0 / (h * 1.2)
        out += amp * np.sin(phase)

    # Normalise
    peak = np.max(np.abs(out))
    if peak > 0:
        out /= peak
    return out


def _pluck(freq, dur_s, sr=_SAMPLE_RATE):
    """Plucked string sound using Karplus-Strong-inspired synthesis.

    Creates a bright attack that decays naturally -- good for music-box
    and harp-like tones.  Much more musical than a sustained sine.
    """
    n = int(sr * dur_s)
    if n == 0:
        return np.zeros(1)

    # Period of the fundamental
    period = max(int(sr / freq), 2)

    # Seed the delay line with filtered noise (one period)
    buf = np.random.uniform(-1, 1, period).astype(np.float64)

    out = np.zeros(n)
    # Decay factor per sample (controls how quickly the note dies)
    decay = 0.996
    idx = 0
    for i in range(n):
        out[i] = buf[idx]
        # Average with next sample and apply decay
        nxt = (idx + 1) % period
        buf[idx] = decay * 0.5 * (buf[idx] + buf[nxt])
        idx = nxt

    # Normalise
    peak = np.max(np.abs(out))
    if peak > 0:
        out /= peak
    return out


def _arpeggio(freqs, dur_s, note_fn=_pluck, overlap=0.15, sr=_SAMPLE_RATE):
    """Play a sequence of notes spread across *dur_s*, optionally overlapping.

    *note_fn* is the synthesis function for each note (_pluck, _note, etc.).
    *overlap* is the fraction of each note's duration that bleeds into the next.
    """
    n_total = int(sr * dur_s)
    num_notes = len(freqs)
    if num_notes == 0:
        return np.zeros(n_total)

    # Each note starts at evenly-spaced intervals
    spacing = dur_s / num_notes
    # Each note rings for spacing + overlap
    note_dur = spacing * (1.0 + overlap)

    out = np.zeros(n_total)
    for i, freq in enumerate(freqs):
        start = int(sr * spacing * i)
        tone = note_fn(freq, note_dur) * 0.7
        tone = _envelope(tone, 0.01, note_dur * 0.5)
        end = min(start + len(tone), n_total)
        out[start:end] += tone[:end - start]

    # Normalise
    peak = np.max(np.abs(out))
    if peak > 0:
        out /= peak
    return out


def _pad(freq, dur_s, sr=_SAMPLE_RATE):
    """Warm sustained pad tone -- multiple detuned sines with vibrato.

    Used for background atmosphere without the harsh pure-sine drone.
    """
    return _note(freq, dur_s, harmonics=4, detune=0.004,
                 vib_rate=3.5, vib_depth=0.010)


def _mix(*arrays):
    """Overlay arrays, normalise to -1..1."""
    max_len = max(len(a) for a in arrays)
    out = np.zeros(max_len)
    for a in arrays:
        out[:len(a)] += a
    peak = np.max(np.abs(out))
    if peak > 1.0:
        out /= peak
    return out


def _to_sound(signal, volume=0.15):
    """Convert float64 mono to pygame.Sound (16-bit stereo)."""
    signal = np.clip(signal * volume, -1.0, 1.0)
    pcm = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((pcm, pcm))
    stereo = np.ascontiguousarray(stereo)
    return pygame.sndarray.make_sound(stereo)


def _seamless_env(signal, fade_s=0.08, sr=_SAMPLE_RATE):
    """Apply a short fade-in and fade-out so loops join seamlessly."""
    n = len(signal)
    fade = int(sr * fade_s)
    fade = min(fade, n // 4)
    if fade > 0:
        signal[:fade] *= np.linspace(0, 1, fade)
        signal[-fade:] *= np.linspace(1, 0, fade)
    return signal

# ---------------------------------------------------------------------------
# Zone sound generators -- each returns a list of pygame.Sound (one per layer)
# ---------------------------------------------------------------------------

def _gen_title(dur=_LOOP_DURATION_S):
    """Gentle music-box arpeggio -- C major with added 9th.

    Slow plucked notes that fade in and out, like a music box in a
    quiet room.  Inviting and warm, not droning.
    """
    # C4, E4, G4, D5, C5, G4 -- gentle ascending/descending pattern
    freqs = [261.63, 329.63, 392.00, 587.33, 523.25, 392.00]
    arp = _arpeggio(freqs, dur, note_fn=_pluck, overlap=0.4) * 0.7

    # Very soft pad underneath (high, airy)
    pad_tone = _pad(523.25, dur) * 0.15
    pad_tone = _envelope(pad_tone, 0.5, 0.5)

    # Whisper of filtered noise for air
    air = _filtered_noise(dur, cutoff_ratio=0.04) * 0.04
    air = _envelope(air, 0.3, 0.3)

    result = _mix(arp, pad_tone, air)
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.15)]


def _gen_floors_1_4(dur=_LOOP_DURATION_S):
    """Dirtmouth-inspired melancholy -- Am with slow 3-note pattern.

    Minor key, sparse, with reverb-like decay.  Piano-like plucked
    notes in a repeating 3-note motif with slight variation each loop.
    """
    sr = _SAMPLE_RATE
    n = int(sr * dur)

    # Three-note motif: A3, C4, E4 (Am chord tones), then A3, C4, D4 (variation)
    # Pattern repeats twice in 3 seconds with slight register shift
    motif1 = [220.0, 261.63, 329.63]   # A3, C4, E4
    motif2 = [220.0, 261.63, 293.66]   # A3, C4, D4

    half = dur / 2.0
    arp1 = _arpeggio(motif1, half, note_fn=_pluck, overlap=0.6) * 0.65
    arp2 = _arpeggio(motif2, half, note_fn=_pluck, overlap=0.6) * 0.55

    # Concatenate both halves
    full_arp = np.concatenate([arp1, arp2[:int(sr * half)]])
    # Trim or pad to exactly n samples
    if len(full_arp) < n:
        full_arp = np.pad(full_arp, (0, n - len(full_arp)))
    else:
        full_arp = full_arp[:n]

    # Soft low pad for depth (not a drone -- has vibrato and harmonics)
    low_pad = _pad(110.0, dur) * 0.12
    low_pad = _envelope(low_pad, 0.8, 0.8)

    # Filtered noise for cave ambience
    cave = _filtered_noise(dur, cutoff_ratio=0.06) * 0.05
    cave = _envelope(cave, 0.4, 0.4)

    result = _mix(full_arp, low_pad, cave)
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.15)]


def _gen_floors_5_8(dur=_LOOP_DURATION_S):
    """Warmer transition zone -- Dsus4 to Dm feel with two layers.

    More movement than floors 1-4.  A melodic layer uses warm _note()
    tones.  A second ambient layer adds strings-like sustained pads.
    """
    sr = _SAMPLE_RATE
    n = int(sr * dur)

    # Melodic layer: D4, G4, A4, F4, D4 -- suspended feel
    melody_freqs = [293.66, 392.00, 440.00, 349.23, 293.66]
    melody = _arpeggio(melody_freqs, dur,
                       note_fn=lambda f, d: _note(f, d, harmonics=3,
                                                  vib_rate=4.0, vib_depth=0.006),
                       overlap=0.3) * 0.55

    # Strings pad underneath: Dm (D3 + F3 + A3) with slow vibrato
    d3 = _pad(146.83, dur) * 0.18
    f3 = _pad(174.61, dur) * 0.14
    a3 = _pad(220.00, dur) * 0.12
    strings = _mix(d3, f3, a3)
    strings = _envelope(strings, 0.6, 0.6)

    # Gentle breath noise
    breath = _filtered_noise(dur, cutoff_ratio=0.05) * 0.03

    result = _mix(melody, strings, breath)
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.15)]


def _gen_floors_9_11(dur=_LOOP_DURATION_S):
    """Rhythmic urgency -- fast arpeggio with bass pulse.

    Faster note pattern with a subtle kick-drum-like low pulse every
    0.5 seconds.  Builds tension for the parkour zone.
    """
    sr = _SAMPLE_RATE
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)

    # Fast arpeggio: Am -> Em pattern (A3, C4, E4, B3, E4, G4)
    fast_freqs = [220.0, 261.63, 329.63, 246.94, 329.63, 392.00]
    arp = _arpeggio(fast_freqs, dur,
                    note_fn=lambda f, d: _note(f, d, harmonics=2,
                                               vib_rate=6.0, vib_depth=0.005),
                    overlap=0.2) * 0.55

    # Kick pulse every 0.5 seconds (6 kicks in 3 seconds)
    kick = np.zeros(n)
    kick_dur_s = 0.08
    kick_samples = int(sr * kick_dur_s)
    for i in range(6):
        start = int(sr * 0.5 * i)
        if start + kick_samples <= n:
            # Short burst of low frequency with fast decay
            kt = np.linspace(0, kick_dur_s, kick_samples, endpoint=False)
            # Pitch drops from 120Hz to 40Hz
            kfreq = 120.0 - 80.0 * (kt / kick_dur_s)
            kphase = 2 * np.pi * np.cumsum(kfreq) / sr
            ksound = np.sin(kphase) * np.exp(-kt * 30)
            kick[start:start + kick_samples] += ksound * 0.4

    # Rhythmic gating on a tension pad (8th-note pulse at 2Hz)
    gate = 0.3 + 0.7 * (np.sin(2 * np.pi * 4.0 * t) > 0).astype(float)
    tension = _pad(220.0, dur) * 0.15 * gate
    tension = _envelope(tension, 0.2, 0.2)

    result = _mix(arp, kick, tension)
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.15)]


def _gen_floors_12_14(dur=_LOOP_DURATION_S):
    """The Gauntlet -- stripped back, minimal, tense.

    Single notes with long decay.  Occasional dissonant cluster.
    Very quiet, like holding your breath.
    """
    sr = _SAMPLE_RATE
    n = int(sr * dur)

    # Single sparse notes -- just two in 3 seconds, with long ring
    note1 = _pluck(220.0, 1.5) * 0.5   # A3
    note1 = _envelope(note1, 0.01, 1.2)

    # Second note is slightly dissonant (Bb3 -- a semitone up)
    note2 = _pluck(233.08, 1.5) * 0.35  # Bb3
    note2 = _envelope(note2, 0.01, 1.2)

    sparse = np.zeros(n)
    # Note 1 at 0.2s
    s1 = int(sr * 0.2)
    e1 = min(s1 + len(note1), n)
    sparse[s1:e1] += note1[:e1 - s1]
    # Note 2 at 1.8s
    s2 = int(sr * 1.8)
    e2 = min(s2 + len(note2), n)
    sparse[s2:e2] += note2[:e2 - s2]

    # Very faint dissonant cluster at 2.5s (E4 + F4 -- semitone rub)
    cluster_start = int(sr * 2.5)
    cluster_dur = 0.4
    c1 = _note(329.63, cluster_dur, harmonics=2, vib_rate=2.0, vib_depth=0.015) * 0.15
    c2 = _note(349.23, cluster_dur, harmonics=2, vib_rate=2.5, vib_depth=0.015) * 0.12
    cluster = _mix(c1, c2)
    cluster = _envelope(cluster, 0.05, 0.3)
    ce = min(cluster_start + len(cluster), n)
    sparse[cluster_start:ce] += cluster[:ce - cluster_start]

    # Barely-there filtered noise for unease
    unease = _filtered_noise(dur, cutoff_ratio=0.08) * 0.03
    unease = _envelope(unease, 0.5, 0.5)

    result = _mix(sparse, unease)
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.10)]


def _gen_floor_15(dur=_LOOP_DURATION_S):
    """The Top -- full, bright, emotional.

    Major chord progression with multiple harmonic layers.
    This should feel like arriving at the summit.  Uses C major -> G major
    -> Am -> F major (I-V-vi-IV), the most triumphant pop progression.
    """
    sr = _SAMPLE_RATE
    n = int(sr * dur)

    # --- Bright arpeggio layer ---
    # C major -> G major over the 3 seconds
    arp_freqs = [523.25, 659.25, 783.99, 587.33, 783.99, 987.77]
    # C5, E5, G5, D5, G5, B5
    arp = _arpeggio(arp_freqs, dur,
                    note_fn=lambda f, d: _note(f, d, harmonics=3,
                                               vib_rate=5.0, vib_depth=0.006),
                    overlap=0.4) * 0.45

    # --- Warm pad layer (C major triad, low) ---
    c3 = _pad(130.81, dur) * 0.20
    e3 = _pad(164.81, dur) * 0.16
    g3 = _pad(196.00, dur) * 0.14
    pad_layer = _mix(c3, e3, g3)
    pad_layer = _envelope(pad_layer, 0.5, 0.5)

    # --- High shimmer (octave above arpeggio, very quiet) ---
    shimmer = _note(1046.5, dur, harmonics=2, vib_rate=6.0, vib_depth=0.008) * 0.08
    shimmer = _envelope(shimmer, 0.8, 0.8)

    # --- Plucked bass notes (root motion: C, G) ---
    bass1 = _pluck(130.81, 1.5) * 0.3  # C3
    bass1 = _envelope(bass1, 0.01, 1.0)
    bass2 = _pluck(196.00, 1.5) * 0.25  # G3
    bass2 = _envelope(bass2, 0.01, 1.0)
    bass = np.zeros(n)
    e1 = min(len(bass1), n)
    bass[:e1] += bass1[:e1]
    s2 = int(sr * 1.5)
    e2 = min(s2 + len(bass2), n)
    bass[s2:e2] += bass2[:e2 - s2]

    result = _mix(arp, pad_layer, shimmer, bass)
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.18)]


def _gen_boss(dur=_LOOP_DURATION_S):
    """Boss fight -- heavy, rhythmic, intense.

    Driving rhythmic pattern with bass pulses.  Uses power-chord feel
    (root + fifth) with aggressive rhythmic gating.  Should feel
    urgent and dangerous.
    """
    sr = _SAMPLE_RATE
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)

    # --- Driving bass hits every 0.375s (8 hits in 3 seconds, ~160 BPM 8ths) ---
    bass_hits = np.zeros(n)
    hit_interval = 0.375
    hit_dur_s = 0.15
    hit_samples = int(sr * hit_dur_s)
    for i in range(8):
        start = int(sr * hit_interval * i)
        if start + hit_samples <= n:
            ht = np.linspace(0, hit_dur_s, hit_samples, endpoint=False)
            # Power chord hit: A2 (110) + E3 (165)
            h1 = np.sin(2 * np.pi * 110.0 * ht)
            h2 = np.sin(2 * np.pi * 164.81 * ht) * 0.7
            h3 = np.sin(2 * np.pi * 220.0 * ht) * 0.3  # octave
            hit = (h1 + h2 + h3) * np.exp(-ht * 15)  # fast decay
            # Accent every other hit
            accent = 0.6 if i % 2 == 0 else 0.35
            bass_hits[start:start + hit_samples] += hit * accent

    # --- Aggressive rhythm pad with gating ---
    # 16th-note gate at ~5.33Hz (160 BPM 16ths)
    gate = (np.sin(2 * np.pi * 5.333 * t) > -0.2).astype(float)
    gate = gate * 0.7 + 0.3  # Never fully silent
    rhythm_pad = _note(220.0, dur, harmonics=4, detune=0.005,
                       vib_rate=1.0, vib_depth=0.003) * 0.3 * gate

    # --- Tension high note (E5, thin, cuts through) ---
    tension = _note(659.25, dur, harmonics=2, vib_rate=7.0,
                    vib_depth=0.012) * 0.10
    tension = _envelope(tension, 0.3, 0.3)

    # --- Noise percussion layer ---
    perc = np.zeros(n)
    for i in range(6):
        start = int(sr * 0.5 * i)
        snare_dur = int(sr * 0.06)
        if start + snare_dur <= n:
            noise_burst = _noise(0.06) * 0.25
            noise_burst *= np.exp(-np.linspace(0, 8, snare_dur))
            perc[start:start + snare_dur] += noise_burst

    result = _mix(bass_hits, rhythm_pad, tension, perc)
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.15)]


def _gen_death(dur=_LOOP_DURATION_S):
    """Sad descending tone -- brief, not annoying.

    A short descending minor third (E4 -> C4) with gentle decay.
    Only occupies the first ~1.5 seconds, then silence, so the loop
    is not irritating on repeat.
    """
    sr = _SAMPLE_RATE
    n = int(sr * dur)

    # Descending notes: E4 -> D4 -> C4 with pluck timbre
    note_dur = 0.45
    n1 = _pluck(329.63, note_dur) * 0.5   # E4
    n1 = _envelope(n1, 0.01, 0.35)
    n2 = _pluck(293.66, note_dur) * 0.4   # D4
    n2 = _envelope(n2, 0.01, 0.35)
    n3 = _pluck(261.63, 0.6) * 0.45       # C4 (longer ring)
    n3 = _envelope(n3, 0.01, 0.5)

    result = np.zeros(n)
    # Place notes with small gaps
    s1 = int(sr * 0.1)
    e1 = min(s1 + len(n1), n)
    result[s1:e1] += n1[:e1 - s1]

    s2 = int(sr * 0.55)
    e2 = min(s2 + len(n2), n)
    result[s2:e2] += n2[:e2 - s2]

    s3 = int(sr * 1.0)
    e3 = min(s3 + len(n3), n)
    result[s3:e3] += n3[:e3 - s3]

    # Remaining ~1.5s is near-silence (just a whisper of noise)
    tail_noise = _filtered_noise(dur, cutoff_ratio=0.08) * 0.01
    result = _mix(result, tail_noise)
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.15)]


def _gen_victory(dur=_LOOP_DURATION_S):
    """Ascending bright arpeggio -- triumphant major intervals.

    C major arpeggio climbing two octaves with bright plucked tones
    and a sustained final chord.
    """
    sr = _SAMPLE_RATE
    n = int(sr * dur)

    # Ascending: C4, E4, G4, C5, E5, G5, C6
    victory_freqs = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99, 1046.50]
    # Quick ascending run in first 2 seconds
    run = _arpeggio(victory_freqs, 2.0,
                    note_fn=lambda f, d: _note(f, d, harmonics=3,
                                               vib_rate=5.0, vib_depth=0.005),
                    overlap=0.5) * 0.6

    # Sustained bright chord for the last second (C5 + E5 + G5)
    chord_dur = 1.2
    ch1 = _pad(523.25, chord_dur) * 0.25
    ch2 = _pad(659.25, chord_dur) * 0.20
    ch3 = _pad(783.99, chord_dur) * 0.18
    chord = _mix(ch1, ch2, ch3)
    chord = _envelope(chord, 0.1, 0.6)

    result = np.zeros(n)
    # Ascending run starts at 0
    run_end = min(len(run), n)
    result[:run_end] += run[:run_end]

    # Chord starts at 1.8s
    cs = int(sr * 1.8)
    ce = min(cs + len(chord), n)
    result[cs:ce] += chord[:ce - cs]

    # Normalise
    peak = np.max(np.abs(result))
    if peak > 0:
        result /= peak
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.18)]


def _gen_secret(dur=_LOOP_DURATION_S):
    """Mysterious shimmer -- whole-tone scale, ethereal.

    Uses the whole-tone scale (C, D, E, F#, G#, A#) with vibrato
    and filtered noise for a dreamlike, otherworldly feel.
    """
    sr = _SAMPLE_RATE
    n = int(sr * dur)

    # Whole-tone scale notes (C4, D4, E4, F#4, G#4)
    wt_freqs = [261.63, 293.66, 329.63, 369.99, 415.30]
    # Slow arpeggio with rich vibrato
    arp = _arpeggio(wt_freqs, dur,
                    note_fn=lambda f, d: _note(f, d, harmonics=3,
                                               vib_rate=3.0, vib_depth=0.020),
                    overlap=0.7) * 0.5

    # High ethereal shimmer (two detuned tones beating against each other)
    sh1 = _sine_vibrato(830.0, dur, vib_rate=2.0, vib_depth=0.015) * 0.10
    sh2 = _sine_vibrato(834.0, dur, vib_rate=2.5, vib_depth=0.012) * 0.10
    shimmer = sh1 + sh2  # Beating frequency ~4Hz creates shimmer
    shimmer = _envelope(shimmer, 0.5, 0.5)

    # Filtered noise for magic dust texture
    dust = _filtered_noise(dur, cutoff_ratio=0.03) * 0.06
    dust = _envelope(dust, 0.3, 0.3)

    result = _mix(arp, shimmer, dust)
    result = _seamless_env(result)
    return [_to_sound(result, volume=0.14)]


_ZONE_GENERATORS = {
    MusicZone.TITLE: _gen_title,
    MusicZone.FLOORS_1_4: _gen_floors_1_4,
    MusicZone.FLOORS_5_8: _gen_floors_5_8,
    MusicZone.FLOORS_9_11: _gen_floors_9_11,
    MusicZone.FLOORS_12_14: _gen_floors_12_14,
    MusicZone.FLOOR_15: _gen_floor_15,
    MusicZone.BOSS: _gen_boss,
    MusicZone.DEATH: _gen_death,
    MusicZone.VICTORY: _gen_victory,
    MusicZone.SECRET: _gen_secret,
}

# ---------------------------------------------------------------------------
# Stinger generators
# ---------------------------------------------------------------------------

def _stinger_item_collect():
    """Quick sparkly ascending two-note chime."""
    a = _pluck(880, 0.15) * 0.5
    a = _envelope(a, 0.005, 0.10)
    b = _pluck(1320, 0.20) * 0.4
    b = _envelope(b, 0.005, 0.15)
    return _to_sound(np.concatenate([a, b]), volume=0.35)


def _stinger_secret_found():
    """Mysterious descending whole-tone phrase."""
    notes = [523.25, 466.16, 415.30, 369.99]
    parts = []
    for f in notes:
        t = _note(f, 0.12, harmonics=2, vib_rate=3.0, vib_depth=0.015) * 0.45
        t = _envelope(t, 0.005, 0.08)
        parts.append(t)
    return _to_sound(np.concatenate(parts), volume=0.35)


def _stinger_boss_entrance():
    """Heavy low hit + rising noise."""
    # Use a richer tone than pure sine for the hit
    hit = _note(110, 0.3, harmonics=4, detune=0.005,
                vib_rate=1.0, vib_depth=0.003) * 0.7
    hit = _envelope(hit, 0.005, 0.25)
    rise = _filtered_noise(0.4, cutoff_ratio=0.03) * 0.3
    rise = _envelope(rise, 0.05, 0.30)
    return _to_sound(_mix(hit, rise), volume=0.40)


def _stinger_floor_change():
    """Brief ascending two-note motif with plucked timbre."""
    a = _pluck(330, 0.12) * 0.45
    a = _envelope(a, 0.005, 0.08)
    b = _pluck(440, 0.18) * 0.40
    b = _envelope(b, 0.005, 0.12)
    return _to_sound(np.concatenate([a, b]), volume=0.30)


_STINGER_GENERATORS = {
    'item_collect': _stinger_item_collect,
    'secret_found': _stinger_secret_found,
    'boss_entrance': _stinger_boss_entrance,
    'floor_change': _stinger_floor_change,
}

# ---------------------------------------------------------------------------
# AdaptiveMusicManager
# ---------------------------------------------------------------------------

class AdaptiveMusicManager:
    """Layered, zone-aware music that crossfades between game areas.

    Typical usage::

        music = AdaptiveMusicManager()
        music.set_zone(MusicZone.TITLE)

        # Each frame:
        music.update()

        # On zone change:
        music.set_zone(MusicZone.FLOORS_1_4)

        # Combat:
        music.add_layer(0.8)
        music.remove_layer(0.0)

        # One-shot stinger:
        music.play_stinger('boss_entrance')
    """

    def __init__(self):
        self._available = False

        # Make sure mixer is up
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(_SAMPLE_RATE, -16, 2, AUDIO_BUFFER)
            pygame.mixer.set_num_channels(AUDIO_CHANNELS)
        except Exception:
            return

        if not HAS_NUMPY:
            print("[Music] numpy not available — music will be silent")
            return

        self._available = True

        # Zone sounds: MusicZone -> list[pygame.Sound]
        self._zone_sounds: dict[MusicZone, list[pygame.mixer.Sound]] = {}
        self._build_zone_sounds()

        # Stinger sounds: name -> pygame.Sound
        self._stingers: dict[str, pygame.mixer.Sound] = {}
        self._build_stingers()

        # State
        self._current_zone: MusicZone | None = None
        self._target_zone: MusicZone | None = None

        # Crossfade state
        self._fading = False
        self._fade_frame = 0

        # Volume per music channel (0..3): current and target
        self._channel_vol = [0.0] * len(MUSIC_CHANNELS)
        self._channel_target_vol = [0.0] * len(MUSIC_CHANNELS)

        # Combat intensity layer (channel index 2 = rhythm)
        self._combat_volume = 0.0
        self._combat_target = 0.0

        # Master volume
        self._master_volume = 1.0

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_zone_sounds(self):
        """Synthesize looping buffers for every zone."""
        for zone, gen_fn in _ZONE_GENERATORS.items():
            try:
                sounds = gen_fn()
                self._zone_sounds[zone] = sounds
            except Exception:
                pass

    def _build_stingers(self):
        """Synthesize all one-shot stingers."""
        for name, gen_fn in _STINGER_GENERATORS.items():
            try:
                self._stingers[name] = gen_fn()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Zone transitions
    # ------------------------------------------------------------------

    def set_zone(self, zone: MusicZone):
        """Start crossfading to *zone* over ~2 seconds.

        If the zone is the same as the current one, nothing happens.
        Music does NOT restart on death -- it just crossfades.
        """
        if not self._available:
            return
        if zone == self._current_zone and not self._fading:
            return

        self._target_zone = zone
        self._fading = True
        self._fade_frame = 0

    # ------------------------------------------------------------------
    # Combat layers
    # ------------------------------------------------------------------

    def add_layer(self, intensity: float = 1.0):
        """Fade in a combat / rhythm layer."""
        self._combat_target = max(0.0, min(1.0, intensity))

    def remove_layer(self, intensity: float = 0.0):
        """Fade out combat layer."""
        self._combat_target = max(0.0, min(1.0, intensity))

    # ------------------------------------------------------------------
    # Stingers
    # ------------------------------------------------------------------

    def play_stinger(self, name: str):
        """Play a one-shot stinger on stinger channels (5-7)."""
        if not self._available:
            return
        snd = self._stingers.get(name)
        if snd is None:
            return

        # Find a free stinger channel
        channel = None
        for ch_id in STINGER_CHANNELS:
            ch = pygame.mixer.Channel(ch_id)
            if not ch.get_busy():
                channel = ch
                break
        if channel is None:
            channel = pygame.mixer.Channel(STINGER_CHANNELS.start)

        channel.play(snd)

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def update(self):
        """Call once per frame. Manages crossfades and looping."""
        if not self._available:
            return

        # --- Crossfade logic ---
        if self._fading and self._target_zone is not None:
            self._fade_frame += 1
            progress = min(self._fade_frame / _CROSSFADE_FRAMES, 1.0)

            # Fade out old zone channels
            fade_out = 1.0 - progress
            # Fade in new zone channels
            fade_in = progress

            # Apply fade-out on currently-playing music channels
            if self._current_zone is not None:
                for i, ch_id in enumerate(MUSIC_CHANNELS):
                    try:
                        ch = pygame.mixer.Channel(ch_id)
                        vol = fade_out * self._master_volume
                        ch.set_volume(vol, vol)
                    except Exception:
                        pass

            # When crossfade completes, switch
            if progress >= 1.0:
                # Stop old sounds
                self._stop_music_channels()

                # Start new zone
                self._current_zone = self._target_zone
                self._target_zone = None
                self._fading = False
                self._fade_frame = 0

                self._start_zone(self._current_zone)
        else:
            # Not fading -- ensure current zone keeps playing (looping
            # is handled by loops=-1, but keep volumes correct)
            self._update_volumes()

        # --- Combat layer fade ---
        if self._combat_volume != self._combat_target:
            step = 0.02  # smooth fade over ~50 frames
            if self._combat_volume < self._combat_target:
                self._combat_volume = min(self._combat_volume + step,
                                          self._combat_target)
            else:
                self._combat_volume = max(self._combat_volume - step,
                                          self._combat_target)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _start_zone(self, zone: MusicZone):
        """Begin playing the given zone's sounds on music channels."""
        sounds = self._zone_sounds.get(zone)
        if not sounds:
            return

        for i, snd in enumerate(sounds):
            if i >= len(MUSIC_CHANNELS):
                break
            ch_id = list(MUSIC_CHANNELS)[i]
            try:
                ch = pygame.mixer.Channel(ch_id)
                ch.play(snd, loops=-1)
                vol = self._master_volume
                ch.set_volume(vol, vol)
            except Exception:
                pass

    def _stop_music_channels(self):
        """Stop all music channels."""
        for ch_id in MUSIC_CHANNELS:
            try:
                pygame.mixer.Channel(ch_id).stop()
            except Exception:
                pass

    def _update_volumes(self):
        """Keep music channel volumes consistent with master volume."""
        if self._current_zone is None:
            return
        sounds = self._zone_sounds.get(self._current_zone, [])
        for i in range(len(sounds)):
            if i >= len(MUSIC_CHANNELS):
                break
            ch_id = list(MUSIC_CHANNELS)[i]
            try:
                ch = pygame.mixer.Channel(ch_id)
                vol = self._master_volume
                ch.set_volume(vol, vol)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Volume
    # ------------------------------------------------------------------

    def set_volume(self, vol: float):
        """Set master music volume (0.0 .. 1.0)."""
        self._master_volume = max(0.0, min(1.0, vol))

    def get_volume(self) -> float:
        return self._master_volume

    # ------------------------------------------------------------------
    # Stop
    # ------------------------------------------------------------------

    def stop(self):
        """Stop all music and stinger channels immediately."""
        if not self._available:
            return
        self._current_zone = None
        self._target_zone = None
        self._fading = False

        for ch_id in MUSIC_CHANNELS:
            try:
                pygame.mixer.Channel(ch_id).stop()
            except Exception:
                pass
        for ch_id in STINGER_CHANNELS:
            try:
                pygame.mixer.Channel(ch_id).stop()
            except Exception:
                pass
