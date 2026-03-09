"""
SPLIT -- Adaptive Music System
Synthesized ambient drones per MusicZone, crossfading between zones,
combat intensity layers, and one-shot stingers. All audio is generated
at startup via numpy -- no external music files required.

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


def _to_sound(signal, volume=0.35):
    """Convert float64 mono to pygame.Sound (16-bit stereo)."""
    signal = np.clip(signal * volume, -1.0, 1.0)
    pcm = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((pcm, pcm))
    stereo = np.ascontiguousarray(stereo)
    return pygame.sndarray.make_sound(stereo)

# ---------------------------------------------------------------------------
# Zone sound generators -- each returns a list of pygame.Sound (one per layer)
# ---------------------------------------------------------------------------

def _gen_title(dur=_LOOP_DURATION_S):
    """Gentle sine pad: C3 + E3."""
    a = _sine(130.81, dur) * 0.5
    b = _sine(164.81, dur) * 0.4
    pad = _envelope(_mix(a, b), 0.3, 0.3)
    return [_to_sound(pad, volume=0.25)]


def _gen_floors_1_4(dur=_LOOP_DURATION_S):
    """Am chord: A2 + C3 + E3 -- dark."""
    a = _sine(110.00, dur) * 0.5
    c = _sine(130.81, dur) * 0.4
    e = _sine(164.81, dur) * 0.35
    pad = _envelope(_mix(a, c, e), 0.4, 0.4)
    return [_to_sound(pad, volume=0.25)]


def _gen_floors_5_8(dur=_LOOP_DURATION_S):
    """Strings feel with vibrato: A2 + C3 + E3 with LFO."""
    a = _sine_vibrato(110.00, dur, vib_rate=4.5, vib_depth=0.015) * 0.5
    c = _sine_vibrato(130.81, dur, vib_rate=5.0, vib_depth=0.02) * 0.4
    e = _sine_vibrato(164.81, dur, vib_rate=5.5, vib_depth=0.018) * 0.35
    pad = _envelope(_mix(a, c, e), 0.3, 0.3)
    return [_to_sound(pad, volume=0.28)]


def _gen_floors_9_11(dur=_LOOP_DURATION_S):
    """Urgency: faster pulse, A3 + C4."""
    sr = _SAMPLE_RATE
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Pulsing amplitude at ~3 Hz
    pulse = 0.5 + 0.5 * np.sin(2 * np.pi * 3.0 * t)
    a = _sine(220.0, dur) * 0.5 * pulse
    c = _sine(261.63, dur) * 0.4 * pulse
    pad = _envelope(_mix(a, c), 0.2, 0.2)
    return [_to_sound(pad, volume=0.30)]


def _gen_floors_12_14(dur=_LOOP_DURATION_S):
    """Minimal tension: single low drone A1."""
    a = _sine(55.0, dur) * 0.7
    drone = _envelope(a, 0.5, 0.5)
    return [_to_sound(drone, volume=0.25)]


def _gen_floor_15(dur=_LOOP_DURATION_S):
    """Full bright: A3 + C4 + E4 + A4."""
    a3 = _sine(220.0, dur) * 0.4
    c4 = _sine(261.63, dur) * 0.35
    e4 = _sine(329.63, dur) * 0.30
    a4 = _sine(440.0, dur) * 0.25
    pad = _envelope(_mix(a3, c4, e4, a4), 0.4, 0.4)
    return [_to_sound(pad, volume=0.30)]


def _gen_boss(dur=_LOOP_DURATION_S):
    """Heavy low drone + rhythmic pulse."""
    sr = _SAMPLE_RATE
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    # Low drone
    drone = _sine(55.0, dur) * 0.6
    # Rhythmic pulse ~2Hz
    pulse_env = 0.5 + 0.5 * np.sin(2 * np.pi * 2.0 * t)
    pulse = _sine(110.0, dur) * 0.4 * pulse_env
    pad = _envelope(_mix(drone, pulse), 0.2, 0.2)
    return [_to_sound(pad, volume=0.32)]


def _gen_death(dur=_LOOP_DURATION_S):
    """Single fading tone."""
    tone = _sine(220.0, dur) * 0.5
    faded = _envelope(tone, 0.1, dur * 0.9)
    return [_to_sound(faded, volume=0.20)]


def _gen_victory(dur=_LOOP_DURATION_S):
    """Ascending arpeggio: C4 -> E4 -> G4 -> C5."""
    sr = _SAMPLE_RATE
    note_dur = dur / 4
    notes = [261.63, 329.63, 392.00, 523.25]
    parts = []
    for freq in notes:
        tone = _sine(freq, note_dur) * 0.5
        tone = _envelope(tone, 0.02, note_dur * 0.3)
        parts.append(tone)
    arpeggio = np.concatenate(parts)
    return [_to_sound(arpeggio, volume=0.30)]


def _gen_secret(dur=_LOOP_DURATION_S):
    """Mysterious shimmer: whole tone cluster with vibrato."""
    a = _sine_vibrato(277.18, dur, vib_rate=3.0, vib_depth=0.025) * 0.35
    b = _sine_vibrato(311.13, dur, vib_rate=3.5, vib_depth=0.020) * 0.30
    c = _sine_vibrato(349.23, dur, vib_rate=4.0, vib_depth=0.022) * 0.25
    pad = _envelope(_mix(a, b, c), 0.4, 0.4)
    return [_to_sound(pad, volume=0.22)]


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
    a = _sine(880, 0.15) * 0.5
    a = _envelope(a, 0.005, 0.10)
    b = _sine(1320, 0.20) * 0.4
    b = _envelope(b, 0.005, 0.15)
    return _to_sound(np.concatenate([a, b]), volume=0.35)


def _stinger_secret_found():
    """Mysterious descending whole-tone phrase."""
    notes = [523.25, 466.16, 415.30, 369.99]
    parts = []
    for f in notes:
        t = _sine(f, 0.12) * 0.45
        t = _envelope(t, 0.005, 0.08)
        parts.append(t)
    return _to_sound(np.concatenate(parts), volume=0.35)


def _stinger_boss_entrance():
    """Heavy low hit + rising noise."""
    hit = _sine(55, 0.3) * 0.7
    hit = _envelope(hit, 0.005, 0.25)
    rise = _noise(0.4) * 0.3
    rise = _envelope(rise, 0.05, 0.30)
    return _to_sound(_mix(hit, rise), volume=0.40)


def _stinger_floor_change():
    """Brief ascending two-note motif."""
    a = _sine(330, 0.12) * 0.45
    a = _envelope(a, 0.005, 0.08)
    b = _sine(440, 0.18) * 0.40
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
