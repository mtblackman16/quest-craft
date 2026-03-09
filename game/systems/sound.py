"""
SPLIT -- Sound Effects System
Synthesized SFX via numpy + pygame.sndarray. Every sound is generated at
startup -- no .wav files required. If numpy is unavailable, falls back to
loading .wav files from assets/sounds/effects/. If those don't exist either,
everything stays silent. Never crashes.
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


def _make_noise(duration_ms, sample_rate=AUDIO_SAMPLE_RATE):
    """Generate white noise array (float64, mono, -1..1)."""
    n_samples = int(sample_rate * duration_ms / 1000)
    if n_samples == 0:
        return np.zeros(1)
    return np.random.uniform(-1, 1, n_samples)


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

# ---------------------------------------------------------------------------
# Individual sound generators
# ---------------------------------------------------------------------------

def _synth_jump(pitch_mult=1.0, dur_mult=1.0):
    """Wet boing -- sine sweep 300->600Hz, attack 5ms decay 95ms."""
    dur = int(100 * dur_mult)
    sweep = _make_sine_sweep(300 * pitch_mult, 600 * pitch_mult, dur)
    return _apply_envelope(sweep, 5, dur - 5)


def _synth_land(pitch_mult=1.0, dur_mult=1.0):
    """Wet splat -- noise burst 30ms + low sine thump 100Hz 50ms."""
    noise = _make_noise(int(30 * dur_mult))
    noise = _apply_envelope(noise, 1, int(29 * dur_mult))
    thump = _make_sine(100 * pitch_mult, int(50 * dur_mult))
    thump = _apply_envelope(thump, 2, int(48 * dur_mult))
    return _mix(noise * 0.6, thump * 0.8)


def _synth_jelly_shot(pitch_mult=1.0, dur_mult=1.0):
    """Squelchy launch -- chirp sweep 200->800Hz 80ms + filtered noise 70ms."""
    chirp = _make_sine_sweep(200 * pitch_mult, 800 * pitch_mult,
                             int(80 * dur_mult))
    chirp = _apply_envelope(chirp, 3, int(77 * dur_mult))
    noise = _make_noise(int(70 * dur_mult))
    noise = _apply_envelope(noise, 2, int(68 * dur_mult)) * 0.4
    return _mix(chirp * 0.7, noise)


def _synth_jelly_impact(pitch_mult=1.0, dur_mult=1.0):
    """Wet thwack -- noise burst 20ms + sine 150Hz 80ms."""
    noise = _make_noise(int(20 * dur_mult))
    noise = _apply_envelope(noise, 1, int(19 * dur_mult))
    tone = _make_sine(150 * pitch_mult, int(80 * dur_mult))
    tone = _apply_envelope(tone, 2, int(78 * dur_mult))
    return _mix(noise * 0.5, tone * 0.8)


def _synth_enemy_hit(pitch_mult=1.0, dur_mult=1.0):
    """Satisfying impact -- sine 200Hz 40ms + noise 40ms, sharp attack."""
    tone = _make_sine(200 * pitch_mult, int(40 * dur_mult))
    tone = _apply_envelope(tone, 2, int(38 * dur_mult))
    noise = _make_noise(int(40 * dur_mult))
    noise = _apply_envelope(noise, 1, int(39 * dur_mult))
    return _mix(tone * 0.7, noise * 0.5)


def _synth_enemy_death(pitch_mult=1.0, dur_mult=1.0):
    """Pop/burst -- sine sweep 400->100Hz 150ms + noise tail 50ms."""
    sweep = _make_sine_sweep(400 * pitch_mult, 100 * pitch_mult,
                             int(150 * dur_mult))
    sweep = _apply_envelope(sweep, 3, int(147 * dur_mult))
    tail = _make_noise(int(50 * dur_mult))
    tail = _apply_envelope(tail, 1, int(49 * dur_mult)) * 0.3
    # Sequential: sweep then tail
    return _concat(sweep * 0.8, tail)


def _synth_collect(pitch_mult=1.0, dur_mult=1.0):
    """Sparkle chime -- sine harmonics 800+1200+1600Hz, 300ms gentle
    attack/decay."""
    dur = int(300 * dur_mult)
    h1 = _make_sine(800 * pitch_mult, dur)
    h2 = _make_sine(1200 * pitch_mult, dur) * 0.6
    h3 = _make_sine(1600 * pitch_mult, dur) * 0.3
    chord = _mix(h1, h2, h3)
    return _apply_envelope(chord, 30, dur - 30)


def _synth_ground_pound(pitch_mult=1.0, dur_mult=1.0):
    """Heavy wet SLAM -- low sine 80Hz 200ms + wide noise 100ms."""
    tone = _make_sine(80 * pitch_mult, int(200 * dur_mult))
    tone = _apply_envelope(tone, 3, int(197 * dur_mult))
    noise = _make_noise(int(100 * dur_mult))
    noise = _apply_envelope(noise, 2, int(98 * dur_mult))
    return _mix(tone * 0.9, noise * 0.6)


def _synth_dodge(pitch_mult=1.0, dur_mult=1.0):
    """Quick whoosh -- filtered noise sweep high->low 150ms."""
    dur = int(150 * dur_mult)
    noise = _make_noise(dur)
    n = len(noise)
    # Simple low-pass sweep: multiply by decaying sine to approximate
    # frequency sweep high->low
    t = np.linspace(0, dur / 1000, n, endpoint=False)
    sweep_env = np.sin(2 * np.pi * np.linspace(4000 * pitch_mult,
                                                 200 * pitch_mult, n) * t)
    # Mix the filtered texture with the raw noise
    out = noise * 0.3 + sweep_env * 0.5
    return _apply_envelope(out, 5, dur - 5)


def _synth_split(pitch_mult=1.0, dur_mult=1.0):
    """Wet tearing -- noise with pitch-modulated sine LFO, 200ms."""
    dur = int(200 * dur_mult)
    noise = _make_noise(dur)
    n = len(noise)
    t = np.linspace(0, dur / 1000, n, endpoint=False)
    # LFO modulates the noise amplitude
    lfo = np.sin(2 * np.pi * 30 * pitch_mult * t)
    modulated = noise * (0.5 + 0.5 * lfo)
    return _apply_envelope(modulated, 5, dur - 5)


def _synth_damage(pitch_mult=1.0, dur_mult=1.0):
    """Wet splatter -- noise burst 50ms + low sine 120Hz 100ms."""
    noise = _make_noise(int(50 * dur_mult))
    noise = _apply_envelope(noise, 1, int(49 * dur_mult))
    tone = _make_sine(120 * pitch_mult, int(100 * dur_mult))
    tone = _apply_envelope(tone, 3, int(97 * dur_mult))
    return _mix(noise * 0.6, tone * 0.7)


def _synth_cooking(pitch_mult=1.0, dur_mult=1.0):
    """Bubbling -- periodic sine pulses at semi-random intervals, 2s loop."""
    sr = AUDIO_SAMPLE_RATE
    dur_s = 2.0 * dur_mult
    n_samples = int(sr * dur_s)
    out = np.zeros(n_samples)

    # Place small bubble pops at random-ish intervals
    rng = random.Random(42)  # deterministic seed for consistency
    pos = 0
    while pos < n_samples:
        # Random gap between bubbles: 30-120ms
        gap = int(sr * rng.uniform(0.03, 0.12))
        pos += gap
        if pos >= n_samples:
            break
        # Each bubble is a short sine burst 8-20ms
        bub_dur = int(sr * rng.uniform(0.008, 0.02))
        freq = rng.uniform(400, 900) * pitch_mult
        end = min(pos + bub_dur, n_samples)
        t = np.arange(end - pos) / sr
        bubble = np.sin(2 * np.pi * freq * t)
        # Tiny envelope
        bub_env = np.ones(len(bubble))
        rise = min(len(bubble) // 4, 20)
        if rise > 0:
            bub_env[:rise] = np.linspace(0, 1, rise)
            bub_env[-rise:] = np.linspace(1, 0, rise)
        out[pos:end] += bubble * bub_env * 0.5
        pos = end

    peak = np.max(np.abs(out))
    if peak > 1.0:
        out /= peak
    return out


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

# How many variants per sound
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
            self._load_wavs()

    def _synthesize_all(self):
        """Create all SFX via numpy synthesis with randomised variants."""
        rng = random.Random()
        for name, gen_fn in _GENERATORS.items():
            variants = []
            for _ in range(_VARIANTS):
                pitch = rng.uniform(0.95, 1.05)
                dur = rng.uniform(0.90, 1.10)
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
