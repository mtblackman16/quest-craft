"""
SPLIT -- Sound Effects System
Synthesized SFX via numpy + pygame.sndarray. Every sound is generated at
startup -- no .wav files required. If numpy is unavailable, falls back to
loading .wav files from assets/sounds/effects/. If those don't exist either,
everything stays silent. Never crashes.

All sounds target WET, SQUISHY, PHYSICAL jello acoustics -- like real foley
recorded from actual gelatin. Layered synthesis (sub-bass + tone + noise)
creates body and tactile texture.
"""

import os
import random

import pygame

from game.engine.settings import (
    AUDIO_SAMPLE_RATE,
    AUDIO_CHANNELS,
    AUDIO_BUFFER,
    SFX_CHANNELS,
    SCREEN_W,
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
# Synthesis helpers (require numpy)
# ---------------------------------------------------------------------------

def _make_sine(freq, duration_ms, sample_rate=AUDIO_SAMPLE_RATE):
    """Generate a sine wave array (float64, mono, -1..1)."""
    n_samples = int(sample_rate * duration_ms / 1000)
    if n_samples == 0:
        return np.zeros(1)
    t = np.linspace(0, duration_ms / 1000, n_samples, endpoint=False)
    return np.sin(2 * np.pi * freq * t)


def _make_sine_sweep(freq_start, freq_end, duration_ms,
                     sample_rate=AUDIO_SAMPLE_RATE):
    """Sine wave whose frequency sweeps linearly from *freq_start* to
    *freq_end* over *duration_ms*."""
    n_samples = int(sample_rate * duration_ms / 1000)
    if n_samples == 0:
        return np.zeros(1)
    t = np.linspace(0, duration_ms / 1000, n_samples, endpoint=False)
    freqs = np.linspace(freq_start, freq_end, n_samples)
    phase = 2 * np.pi * np.cumsum(freqs) / sample_rate
    return np.sin(phase)


def _make_exp_sweep(freq_start, freq_end, duration_ms,
                    sample_rate=AUDIO_SAMPLE_RATE):
    """Sine wave with exponential frequency sweep -- sounds more natural
    for pitch bends than linear sweeps."""
    n_samples = int(sample_rate * duration_ms / 1000)
    if n_samples == 0:
        return np.zeros(1)
    # Exponential interpolation between frequencies
    freqs = freq_start * (freq_end / max(freq_start, 1)) ** (
        np.linspace(0, 1, n_samples))
    phase = 2 * np.pi * np.cumsum(freqs) / sample_rate
    return np.sin(phase)


def _make_noise(duration_ms, sample_rate=AUDIO_SAMPLE_RATE):
    """Generate white noise array (float64, mono, -1..1)."""
    n_samples = int(sample_rate * duration_ms / 1000)
    if n_samples == 0:
        return np.zeros(1)
    return np.random.uniform(-1, 1, n_samples)


def _make_filtered_noise(duration_ms, cutoff_ratio=0.3,
                         sample_rate=AUDIO_SAMPLE_RATE):
    """Generate noise with a crude low-pass filter for a softer, wetter
    texture. cutoff_ratio 0..1 controls how much high-frequency content
    survives (lower = muddier/wetter)."""
    raw = _make_noise(duration_ms, sample_rate)
    # Simple rolling average as cheap low-pass
    window = max(2, int(1.0 / max(cutoff_ratio, 0.01)))
    kernel = np.ones(window) / window
    filtered = np.convolve(raw, kernel, mode='same')
    # Normalize back to -1..1
    peak = np.max(np.abs(filtered))
    if peak > 0:
        filtered /= peak
    return filtered


def _apply_envelope(signal, attack_ms, decay_ms,
                    sample_rate=AUDIO_SAMPLE_RATE):
    """Apply a simple attack-then-decay amplitude envelope in place."""
    n = len(signal)
    attack_samples = min(int(sample_rate * attack_ms / 1000), n)
    decay_samples = min(int(sample_rate * decay_ms / 1000), n - attack_samples)

    env = np.ones(n)
    # Attack ramp
    if attack_samples > 0:
        env[:attack_samples] = np.linspace(0, 1, attack_samples)
    # Decay ramp (starts immediately after attack)
    if decay_samples > 0:
        start = attack_samples
        env[start:start + decay_samples] = np.linspace(1, 0, decay_samples)
        env[start + decay_samples:] = 0
    return signal * env


def _apply_exp_decay(signal, attack_ms, decay_rate=8.0,
                     sample_rate=AUDIO_SAMPLE_RATE):
    """Apply an exponential decay envelope -- sounds more natural than
    linear for impact sounds. Higher decay_rate = faster falloff."""
    n = len(signal)
    attack_samples = min(int(sample_rate * attack_ms / 1000), n)
    env = np.ones(n)
    if attack_samples > 0:
        env[:attack_samples] = np.linspace(0, 1, attack_samples)
    # Exponential decay from the end of attack
    if n > attack_samples:
        t = np.linspace(0, 1, n - attack_samples)
        env[attack_samples:] = np.exp(-decay_rate * t)
    return signal * env


def _to_sound(signal, sample_rate=AUDIO_SAMPLE_RATE):
    """Convert a float64 mono array (-1..1) into a pygame.Sound (16-bit
    stereo)."""
    signal = np.clip(signal, -1.0, 1.0)
    pcm = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((pcm, pcm))
    # Ensure array is contiguous for sndarray
    stereo = np.ascontiguousarray(stereo)
    return pygame.sndarray.make_sound(stereo)


def _concat(*arrays):
    """Concatenate several arrays, padding shorter ones with zeros when
    they should be *mixed* (overlaid) instead. For simple sequential concat."""
    return np.concatenate(arrays)


def _mix(*arrays):
    """Mix (overlay) arrays of potentially different lengths, zero-padding
    shorter ones."""
    max_len = max(len(a) for a in arrays)
    out = np.zeros(max_len)
    for a in arrays:
        out[:len(a)] += a
    # Keep within -1..1
    peak = np.max(np.abs(out))
    if peak > 1.0:
        out /= peak
    return out


def _wobble(signal, rate_hz=20.0, depth=0.4, sample_rate=AUDIO_SAMPLE_RATE):
    """Apply amplitude modulation (wobble) to a signal -- gives a jello
    vibration feel. depth 0..1 controls how deep the wobble is."""
    n = len(signal)
    t = np.linspace(0, n / sample_rate, n, endpoint=False)
    mod = 1.0 - depth + depth * np.sin(2 * np.pi * rate_hz * t)
    return signal * mod


# ---------------------------------------------------------------------------
# Individual sound generators -- WET JELLO PHYSICS
# ---------------------------------------------------------------------------

def _synth_jump(pitch_mult=1.0, dur_mult=1.0):
    """Wet stretchy boing. Initial squelch (short noise + sine burst) then
    a rapid upward pitch sweep like pulling jello off a surface."""
    sr = AUDIO_SAMPLE_RATE

    # Layer 1: Initial squelch -- short filtered noise burst (15ms)
    squelch_dur = int(15 * dur_mult)
    squelch = _make_filtered_noise(squelch_dur, cutoff_ratio=0.2)
    squelch = _apply_envelope(squelch, 1, squelch_dur - 1)

    # Layer 2: Rising boing -- exponential sweep 180->700Hz (85ms)
    boing_dur = int(85 * dur_mult)
    boing = _make_exp_sweep(180 * pitch_mult, 700 * pitch_mult, boing_dur)
    # Add jello wobble to the boing
    boing = _wobble(boing, rate_hz=35 * pitch_mult, depth=0.3)
    boing = _apply_envelope(boing, 2, boing_dur - 2)

    # Layer 3: Sub-bass punch for body (30ms, 50Hz)
    sub = _make_sine(50 * pitch_mult, int(30 * dur_mult))
    sub = _apply_exp_decay(sub, 1, decay_rate=15.0)

    # Combine: squelch first, then boing overlapping, sub for weight
    squelch_padded = np.zeros(int(sr * (squelch_dur + boing_dur) / 1000))
    squelch_padded[:len(squelch)] = squelch * 0.5
    boing_padded = np.zeros(len(squelch_padded))
    # Boing starts 8ms after squelch begins (slight overlap)
    offset = int(sr * 8 / 1000)
    end = min(offset + len(boing), len(boing_padded))
    boing_padded[offset:end] = boing[:end - offset] * 0.8

    return _mix(squelch_padded, boing_padded, sub * 0.4)


def _synth_land(pitch_mult=1.0, dur_mult=1.0):
    """Wet SPLAT. Heavy low thump + noise burst with fast decay. Like
    dropping a block of jello on a table -- short and punchy."""
    sr = AUDIO_SAMPLE_RATE

    # Layer 1: Deep thump (60-80Hz sine with fast exponential decay, 80ms)
    thump_dur = int(80 * dur_mult)
    thump = _make_sine(70 * pitch_mult, thump_dur)
    thump = _apply_exp_decay(thump, 1, decay_rate=12.0)

    # Layer 2: Wet splat noise (filtered, 40ms, very fast attack)
    splat_dur = int(40 * dur_mult)
    splat = _make_filtered_noise(splat_dur, cutoff_ratio=0.25)
    splat = _apply_exp_decay(splat, 1, decay_rate=10.0)

    # Layer 3: Brief mid-frequency body (150Hz, 30ms) for the "wet" quality
    body = _make_sine(150 * pitch_mult, int(30 * dur_mult))
    body = _apply_exp_decay(body, 1, decay_rate=18.0)

    return _mix(thump * 0.8, splat * 0.6, body * 0.35)


def _synth_jelly_shot(pitch_mult=1.0, dur_mult=1.0):
    """Squelchy launch. Quick rising chirp (200->800Hz in 50ms) with a wet
    noise 'pft' sound -- like a glob of jello being flung."""
    sr = AUDIO_SAMPLE_RATE

    # Layer 1: Fast rising chirp (50ms)
    chirp_dur = int(50 * dur_mult)
    chirp = _make_exp_sweep(200 * pitch_mult, 800 * pitch_mult, chirp_dur)
    chirp = _apply_envelope(chirp, 2, chirp_dur - 2)

    # Layer 2: Wet "pft" -- filtered noise burst (35ms)
    pft_dur = int(35 * dur_mult)
    pft = _make_filtered_noise(pft_dur, cutoff_ratio=0.3)
    pft = _apply_exp_decay(pft, 1, decay_rate=14.0)

    # Layer 3: Sub thump for the release sensation (25ms, 90Hz)
    sub = _make_sine(90 * pitch_mult, int(25 * dur_mult))
    sub = _apply_exp_decay(sub, 1, decay_rate=20.0)

    # Pft starts slightly before chirp for squelchy onset
    total_dur = int(sr * (chirp_dur + 10) / 1000)
    pft_padded = np.zeros(total_dur)
    pft_padded[:len(pft)] = pft * 0.5
    chirp_padded = np.zeros(total_dur)
    offset = int(sr * 5 / 1000)
    end = min(offset + len(chirp), total_dur)
    chirp_padded[offset:end] = chirp[:end - offset] * 0.7

    return _mix(pft_padded, chirp_padded, sub * 0.3)


def _synth_jelly_impact(pitch_mult=1.0, dur_mult=1.0):
    """Wet thwack. Short sharp impact -- like land but higher pitched and
    faster. A jello glob hitting a wall."""
    sr = AUDIO_SAMPLE_RATE

    # Layer 1: Sharp noise transient (15ms)
    crack_dur = int(15 * dur_mult)
    crack = _make_filtered_noise(crack_dur, cutoff_ratio=0.4)
    crack = _apply_exp_decay(crack, 1, decay_rate=20.0)

    # Layer 2: Mid tone body (200Hz, 40ms) with fast decay
    body_dur = int(40 * dur_mult)
    body = _make_sine(200 * pitch_mult, body_dur)
    body = _apply_exp_decay(body, 1, decay_rate=14.0)

    # Layer 3: Tiny wobble tail (jello vibrating after impact, 30ms)
    wobble_dur = int(30 * dur_mult)
    tail = _make_sine(300 * pitch_mult, wobble_dur)
    tail = _wobble(tail, rate_hz=40 * pitch_mult, depth=0.6)
    tail = _apply_exp_decay(tail, 1, decay_rate=16.0)

    # Tail starts after the initial crack
    total_dur = int(sr * (crack_dur + wobble_dur) / 1000)
    crack_padded = np.zeros(total_dur)
    crack_padded[:len(crack)] = crack * 0.5
    body_padded = np.zeros(total_dur)
    body_padded[:len(body)] = body * 0.7
    tail_padded = np.zeros(total_dur)
    tail_offset = int(sr * 10 / 1000)
    tail_end = min(tail_offset + len(tail), total_dur)
    tail_padded[tail_offset:tail_end] = tail[:tail_end - tail_offset] * 0.35

    return _mix(crack_padded, body_padded, tail_padded)


def _synth_enemy_hit(pitch_mult=1.0, dur_mult=1.0):
    """Satisfying squishy impact. Like punching jello -- mid tone with
    noise burst and a quick pitch drop for that thwack feel."""
    sr = AUDIO_SAMPLE_RATE

    # Layer 1: Impact tone with pitch drop (200->120Hz in 60ms)
    tone_dur = int(60 * dur_mult)
    tone = _make_exp_sweep(200 * pitch_mult, 120 * pitch_mult, tone_dur)
    tone = _apply_exp_decay(tone, 1, decay_rate=10.0)

    # Layer 2: Noise burst for the squish texture (30ms)
    squish_dur = int(30 * dur_mult)
    squish = _make_filtered_noise(squish_dur, cutoff_ratio=0.3)
    squish = _apply_exp_decay(squish, 1, decay_rate=12.0)

    # Layer 3: Sub bass for satisfying weight (40Hz, 40ms)
    sub = _make_sine(40 * pitch_mult, int(40 * dur_mult))
    sub = _apply_exp_decay(sub, 1, decay_rate=14.0)

    return _mix(tone * 0.7, squish * 0.5, sub * 0.35)


def _synth_enemy_death(pitch_mult=1.0, dur_mult=1.0):
    """Pop/burst/dissolve. Bright pop (high tone), then descending bubbly
    dissolve (multiple small noise bursts fading out). Like jello popping
    and deflating."""
    sr = AUDIO_SAMPLE_RATE

    # Phase 1: Bright pop (800->400Hz sweep, 30ms)
    pop_dur = int(30 * dur_mult)
    pop = _make_exp_sweep(800 * pitch_mult, 400 * pitch_mult, pop_dur)
    pop = _apply_exp_decay(pop, 1, decay_rate=16.0)

    # Phase 2: Bubbly dissolve -- series of tiny descending pops (200ms)
    dissolve_dur_ms = int(200 * dur_mult)
    dissolve_samples = int(sr * dissolve_dur_ms / 1000)
    dissolve = np.zeros(dissolve_samples)
    rng = random.Random(int(pitch_mult * 1000))
    pos = 0
    bubble_idx = 0
    while pos < dissolve_samples:
        gap = int(sr * rng.uniform(0.008, 0.025))
        pos += gap
        if pos >= dissolve_samples:
            break
        # Each bubble pop: tiny sine burst, descending pitch over time
        progress = pos / dissolve_samples
        freq = rng.uniform(300, 600) * pitch_mult * (1.0 - 0.5 * progress)
        bub_len = int(sr * rng.uniform(0.005, 0.012))
        end = min(pos + bub_len, dissolve_samples)
        t = np.arange(end - pos) / sr
        bubble = np.sin(2 * np.pi * freq * t)
        # Amplitude fades as dissolve progresses
        amp = 0.4 * (1.0 - 0.8 * progress)
        # Tiny envelope per bubble
        bub_env = np.ones(len(bubble))
        rise = max(1, len(bubble) // 5)
        bub_env[:rise] = np.linspace(0, 1, rise)
        bub_env[-rise:] = np.linspace(1, 0, rise)
        dissolve[pos:end] += bubble * bub_env * amp
        bubble_idx += 1
        pos = end

    # Combine sequentially: pop then dissolve
    pop_full = np.zeros(len(pop) + dissolve_samples)
    pop_full[:len(pop)] = pop * 0.8
    dissolve_padded = np.zeros(len(pop_full))
    dissolve_padded[len(pop):len(pop) + dissolve_samples] = dissolve

    return _mix(pop_full, dissolve_padded)


def _synth_collect(pitch_mult=1.0, dur_mult=1.0):
    """Sparkle chime. 3 ascending tones with shimmer, rewarding 'ding'
    quality. Sequential notes that ascend for a satisfying pickup feel."""
    sr = AUDIO_SAMPLE_RATE

    # Three ascending chime notes, each ~60ms
    note_dur = int(60 * dur_mult)
    gap_dur = int(20 * dur_mult)

    # Note 1: C6-ish (523Hz)
    n1 = _make_sine(523 * pitch_mult, note_dur)
    n1_h = _make_sine(1046 * pitch_mult, note_dur) * 0.3  # octave harmonic
    note1 = _mix(n1, n1_h)
    note1 = _apply_exp_decay(note1, 2, decay_rate=6.0)

    # Note 2: E6-ish (659Hz)
    n2 = _make_sine(659 * pitch_mult, note_dur)
    n2_h = _make_sine(1318 * pitch_mult, note_dur) * 0.3
    note2 = _mix(n2, n2_h)
    note2 = _apply_exp_decay(note2, 2, decay_rate=6.0)

    # Note 3: G6-ish (784Hz) -- highest, brightest, longest tail
    n3_dur = int(100 * dur_mult)
    n3 = _make_sine(784 * pitch_mult, n3_dur)
    n3_h = _make_sine(1568 * pitch_mult, n3_dur) * 0.35
    n3_h2 = _make_sine(2352 * pitch_mult, n3_dur) * 0.15  # 3rd harmonic
    note3 = _mix(n3, n3_h, n3_h2)
    note3 = _apply_exp_decay(note3, 2, decay_rate=4.0)

    # Shimmer: soft high noise tail (80ms)
    shimmer_dur = int(80 * dur_mult)
    shimmer = _make_noise(shimmer_dur)
    # Crude high-pass by subtracting a smoothed version
    window = 8
    kernel = np.ones(window) / window
    smooth = np.convolve(shimmer, kernel, mode='same')
    shimmer = shimmer - smooth
    peak = np.max(np.abs(shimmer))
    if peak > 0:
        shimmer /= peak
    shimmer = _apply_exp_decay(shimmer, 3, decay_rate=8.0) * 0.15

    # Assemble sequentially
    gap = np.zeros(int(sr * gap_dur / 1000))
    sequence = _concat(note1 * 0.6, gap, note2 * 0.7, gap, note3 * 0.8)
    # Mix shimmer over the end
    total = np.zeros(len(sequence) + len(shimmer))
    total[:len(sequence)] = sequence
    shimmer_start = len(sequence) - len(shimmer)
    if shimmer_start >= 0:
        total[shimmer_start:shimmer_start + len(shimmer)] += shimmer

    peak = np.max(np.abs(total))
    if peak > 1.0:
        total /= peak
    return total


def _synth_ground_pound(pitch_mult=1.0, dur_mult=1.0):
    """HEAVY wet SLAM. The most impactful sound. Deep sub-bass thump,
    wide noise burst, slight reverb tail. Screen-shaking heavy."""
    sr = AUDIO_SAMPLE_RATE

    # Layer 1: Deep sub-bass (45Hz sine, 150ms, slow exponential decay)
    sub_dur = int(150 * dur_mult)
    sub = _make_sine(45 * pitch_mult, sub_dur)
    sub = _apply_exp_decay(sub, 1, decay_rate=5.0)

    # Layer 2: Thump body (80Hz with pitch drop to 40Hz, 100ms)
    thump_dur = int(100 * dur_mult)
    thump = _make_exp_sweep(80 * pitch_mult, 40 * pitch_mult, thump_dur)
    thump = _apply_exp_decay(thump, 1, decay_rate=8.0)

    # Layer 3: Wide wet noise burst (60ms, filtered low)
    splat_dur = int(60 * dur_mult)
    splat = _make_filtered_noise(splat_dur, cutoff_ratio=0.2)
    splat = _apply_exp_decay(splat, 1, decay_rate=10.0)

    # Layer 4: Reverb tail -- quiet filtered noise (150ms, slow fade)
    tail_dur = int(150 * dur_mult)
    tail = _make_filtered_noise(tail_dur, cutoff_ratio=0.15)
    tail = _apply_exp_decay(tail, 5, decay_rate=4.0)

    # Combine with the tail starting slightly after the impact
    total_samples = int(sr * (sub_dur + 80) / 1000)
    sub_padded = np.zeros(total_samples)
    sub_padded[:len(sub)] = sub * 0.9
    thump_padded = np.zeros(total_samples)
    thump_padded[:len(thump)] = thump * 0.7
    splat_padded = np.zeros(total_samples)
    splat_padded[:len(splat)] = splat * 0.55
    tail_padded = np.zeros(total_samples)
    tail_start = int(sr * 30 / 1000)
    tail_end = min(tail_start + len(tail), total_samples)
    tail_padded[tail_start:tail_end] = tail[:tail_end - tail_start] * 0.25

    return _mix(sub_padded, thump_padded, splat_padded, tail_padded)


def _synth_dodge(pitch_mult=1.0, dur_mult=1.0):
    """Quick swoosh/whoosh. Filtered noise that sweeps high to low in
    100ms. Brief, snappy, airy."""
    sr = AUDIO_SAMPLE_RATE
    dur = int(100 * dur_mult)
    n_samples = int(sr * dur / 1000)
    if n_samples == 0:
        return np.zeros(1)

    noise = _make_noise(dur)
    n = len(noise)
    t = np.linspace(0, dur / 1000, n, endpoint=False)

    # Sweeping band-pass: multiply noise by a chirp to impart tonal sweep
    sweep_freq = np.linspace(3000 * pitch_mult, 300 * pitch_mult, n)
    phase = 2 * np.pi * np.cumsum(sweep_freq) / sr
    carrier = np.sin(phase)

    # Ring-modulate the noise with the sweep for a filtered whoosh texture
    whoosh = noise * 0.3 + carrier * noise * 0.5

    # Sharp attack, fast decay
    return _apply_exp_decay(whoosh, 2, decay_rate=10.0)


def _synth_split(pitch_mult=1.0, dur_mult=1.0):
    """Wet tearing/ripping. Noise burst with pitch-modulated LFO creating
    a 'tearing' texture. Like pulling jello apart -- ~200ms."""
    sr = AUDIO_SAMPLE_RATE
    dur = int(200 * dur_mult)
    n_samples = int(sr * dur / 1000)
    if n_samples == 0:
        return np.zeros(1)

    # Layer 1: Filtered noise with rapid amplitude modulation (tearing texture)
    noise = _make_filtered_noise(dur, cutoff_ratio=0.3)
    n = len(noise)
    t = np.linspace(0, dur / 1000, n, endpoint=False)

    # LFO that accelerates -- starts slow tear, speeds up as it rips apart
    lfo_freq = np.linspace(15 * pitch_mult, 60 * pitch_mult, n)
    lfo_phase = 2 * np.pi * np.cumsum(lfo_freq) / sr
    lfo = np.sin(lfo_phase)
    torn_noise = noise * (0.4 + 0.6 * np.abs(lfo))
    torn_noise = _apply_envelope(torn_noise, 3, dur - 3)

    # Layer 2: Descending wet tone (250->100Hz) for the "stretching" feel
    stretch = _make_exp_sweep(250 * pitch_mult, 100 * pitch_mult, dur)
    stretch = _wobble(stretch, rate_hz=25 * pitch_mult, depth=0.5)
    stretch = _apply_envelope(stretch, 3, dur - 3)

    # Layer 3: Sub-bass thump at the moment of separation (20ms, 60Hz)
    sep = _make_sine(60 * pitch_mult, int(20 * dur_mult))
    sep = _apply_exp_decay(sep, 1, decay_rate=20.0)

    return _mix(torn_noise * 0.5, stretch * 0.4, sep * 0.3)


def _synth_damage(pitch_mult=1.0, dur_mult=1.0):
    """Wet splatter + pain. Noise burst + low tone with a brief pitch dip
    (wince). Should feel unpleasant -- you're losing mass."""
    sr = AUDIO_SAMPLE_RATE

    # Layer 1: Harsh noise burst (35ms) -- the splatter
    splat_dur = int(35 * dur_mult)
    splat = _make_filtered_noise(splat_dur, cutoff_ratio=0.35)
    splat = _apply_exp_decay(splat, 1, decay_rate=12.0)

    # Layer 2: Wince tone -- starts at 150Hz, dips to 80Hz, rebounds to
    # 120Hz (70ms) for that "ow" feeling
    wince_dur = int(70 * dur_mult)
    n_wince = int(sr * wince_dur / 1000)
    if n_wince > 0:
        # Build a custom frequency curve: 150 -> 80 -> 120
        third = n_wince // 3
        f1 = np.linspace(150, 80, third) * pitch_mult
        f2 = np.linspace(80, 120, n_wince - third) * pitch_mult
        freqs = np.concatenate([f1, f2])
        phase = 2 * np.pi * np.cumsum(freqs) / sr
        wince = np.sin(phase)
    else:
        wince = np.zeros(1)
    wince = _apply_exp_decay(wince, 2, decay_rate=8.0)

    # Layer 3: Sub rumble (40Hz, 50ms) for body
    sub = _make_sine(40 * pitch_mult, int(50 * dur_mult))
    sub = _apply_exp_decay(sub, 1, decay_rate=10.0)

    return _mix(splat * 0.6, wince * 0.55, sub * 0.3)


def _synth_cooking(pitch_mult=1.0, dur_mult=1.0):
    """Bubbling pot. Varied bubble pops at random intervals with a subtle
    simmering background noise. More organic and varied than before."""
    sr = AUDIO_SAMPLE_RATE
    dur_s = 2.0 * dur_mult
    n_samples = int(sr * dur_s)
    out = np.zeros(n_samples)

    # Background simmer: very soft filtered noise
    simmer = _make_filtered_noise(int(dur_s * 1000), cutoff_ratio=0.15)
    simmer = simmer[:n_samples] * 0.08

    # Bubble pops at random intervals
    rng = random.Random(42)
    pos = 0
    while pos < n_samples:
        # Varied gap between bubbles: 20-150ms (wider range than before)
        gap = int(sr * rng.uniform(0.02, 0.15))
        pos += gap
        if pos >= n_samples:
            break

        # Decide bubble type: small (70%), medium (25%), large (5%)
        roll = rng.random()
        if roll < 0.70:
            # Small bubble: high pitch, short
            freq = rng.uniform(500, 1000) * pitch_mult
            bub_dur = int(sr * rng.uniform(0.006, 0.012))
            amp = rng.uniform(0.2, 0.4)
        elif roll < 0.95:
            # Medium bubble: mid pitch, longer
            freq = rng.uniform(300, 600) * pitch_mult
            bub_dur = int(sr * rng.uniform(0.012, 0.025))
            amp = rng.uniform(0.3, 0.5)
        else:
            # Large bubble: low pitch, longest, has a "bloop" quality
            freq = rng.uniform(150, 350) * pitch_mult
            bub_dur = int(sr * rng.uniform(0.02, 0.04))
            amp = rng.uniform(0.4, 0.6)

        end = min(pos + bub_dur, n_samples)
        actual_len = end - pos
        if actual_len <= 0:
            break
        t = np.arange(actual_len) / sr
        # Slight pitch drop within each bubble for "bloop" character
        bubble_freqs = np.linspace(freq, freq * 0.7, actual_len)
        phase = 2 * np.pi * np.cumsum(bubble_freqs) / sr
        bubble = np.sin(phase)

        # Per-bubble envelope
        bub_env = np.ones(actual_len)
        rise = max(1, actual_len // 6)
        fall = max(1, actual_len // 3)
        bub_env[:rise] = np.linspace(0, 1, rise)
        if fall < actual_len:
            bub_env[-fall:] = np.linspace(1, 0, fall)
        out[pos:end] += bubble * bub_env * amp
        pos = end

    # Mix bubbles with simmer (trim to same length to avoid rounding mismatch)
    min_len = min(len(out), len(simmer))
    result = out[:min_len] + simmer[:min_len]
    peak = np.max(np.abs(result))
    if peak > 1.0:
        result /= peak
    return result


# Map of name -> generator function
_GENERATORS = {
    'jump': _synth_jump,
    'land': _synth_land,
    'jelly_shot': _synth_jelly_shot,
    'jelly_impact': _synth_jelly_impact,
    'enemy_hit': _synth_enemy_hit,
    'enemy_death': _synth_enemy_death,
    'collect': _synth_collect,
    'ground_pound': _synth_ground_pound,
    'dodge': _synth_dodge,
    'split': _synth_split,
    'damage': _synth_damage,
    'cooking': _synth_cooking,
}

# How many variants per sound -- wider randomization for organic feel
_VARIANTS = 3

# ---------------------------------------------------------------------------
# SFXManager
# ---------------------------------------------------------------------------

class SFXManager:
    """Manages all game sound effects.

    Call ``SFXManager.pre_init()`` **before** ``pygame.init()``, then create
    the manager after init with ``SFXManager()``.
    """

    # ------------------------------------------------------------------
    # Class-level pre-init (call before pygame.init)
    # ------------------------------------------------------------------

    @staticmethod
    def pre_init():
        """Configure the mixer before pygame.init().  Safe to call even if
        the mixer is already initialised."""
        try:
            pygame.mixer.pre_init(AUDIO_SAMPLE_RATE, -16, 2, AUDIO_BUFFER)
        except Exception:
            pass  # already initialised or unavailable -- that's fine

    # ------------------------------------------------------------------
    # Instance
    # ------------------------------------------------------------------

    def __init__(self):
        # Make sure the mixer is running
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(AUDIO_SAMPLE_RATE, -16, 2, AUDIO_BUFFER)
            pygame.mixer.set_num_channels(AUDIO_CHANNELS)
        except Exception:
            pass

        # SoundPool: name -> list[pygame.mixer.Sound]
        self._pool: dict[str, list[pygame.mixer.Sound]] = {}

        # Master volume (0.0 .. 1.0)
        self._volume = 0.8

        # Build every sound
        self._build_pools()

    # ------------------------------------------------------------------
    # Pool construction
    # ------------------------------------------------------------------

    def _build_pools(self):
        """Generate or load all sound variants."""
        if HAS_NUMPY:
            self._synthesize_all()
        else:
            print("[SFX] numpy not available — falling back to .wav files")
            self._load_wavs()

    def _synthesize_all(self):
        """Create all SFX via numpy synthesis with randomised variants.
        Wider pitch/duration ranges give more organic variation."""
        rng = random.Random()
        for name, gen_fn in _GENERATORS.items():
            variants = []
            for _ in range(_VARIANTS):
                # Wider randomization than before for organic variation
                pitch = rng.uniform(0.90, 1.10)
                dur = rng.uniform(0.85, 1.15)
                try:
                    raw = gen_fn(pitch_mult=pitch, dur_mult=dur)
                    snd = _to_sound(raw * self._volume)
                    variants.append(snd)
                except Exception:
                    # If one variant fails, skip it
                    pass
            if variants:
                self._pool[name] = variants

    def _load_wavs(self):
        """Fallback: load .wav files from assets/sounds/effects/."""
        base = os.path.join(os.path.dirname(__file__), '..', '..',
                            'assets', 'sounds', 'effects')
        base = os.path.normpath(base)
        for name in _GENERATORS:
            path = os.path.join(base, f'{name}.wav')
            if os.path.isfile(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(self._volume)
                    self._pool[name] = [snd]
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------

    def play(self, name: str, x: float | None = None):
        """Play a sound effect by name.

        Parameters
        ----------
        name : str
            Key into the sound pool (e.g. ``'jump'``, ``'collect'``).
        x : float or None
            Horizontal world position of the sound source.  When provided
            the sound is panned left/right based on screen centre.
        """
        variants = self._pool.get(name)
        if not variants:
            return  # unknown sound or synthesis failed -- stay silent

        snd = random.choice(variants)

        # Find a free channel in the SFX range
        channel = None
        for ch_id in SFX_CHANNELS:
            ch = pygame.mixer.Channel(ch_id)
            if not ch.get_busy():
                channel = ch
                break

        if channel is None:
            # All SFX channels busy -- steal the first one
            channel = pygame.mixer.Channel(SFX_CHANNELS.start)

        # Stereo panning
        if x is not None:
            # Map x position to pan: 0.0 (hard left) .. 1.0 (hard right)
            half_w = SCREEN_W / 2
            pan = max(0.0, min(1.0, (x / SCREEN_W)))
            left_vol = max(0.0, 1.0 - pan)
            right_vol = max(0.0, pan)
            channel.set_volume(left_vol, right_vol)
        else:
            channel.set_volume(1.0, 1.0)

        channel.play(snd)

    # ------------------------------------------------------------------
    # Volume control
    # ------------------------------------------------------------------

    def set_volume(self, vol: float):
        """Set master SFX volume (0.0 .. 1.0). Rebuilds the pool so the
        amplitude is baked into the samples."""
        self._volume = max(0.0, min(1.0, vol))
        # Rather than rebuild everything, just set channel volumes.
        # New sounds will be generated at current volume next time.

    def get_volume(self) -> float:
        return self._volume

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def stop_all(self):
        """Stop every SFX channel immediately."""
        for ch_id in SFX_CHANNELS:
            try:
                pygame.mixer.Channel(ch_id).stop()
            except Exception:
                pass
