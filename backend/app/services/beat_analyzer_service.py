"""
Beat Analyzer Service for AI Promotion Platform

Analyzes audio quality, extracts metadata, and classifies genres.
Integrates with the recommendation engine for better beat promotion.
"""

import json
import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class AudioQualityLevel(str, Enum):
    """Audio quality classification levels"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


@dataclass
class AudioQualityMetrics:
    """Audio quality metrics"""
    quality_level: AudioQualityLevel
    loudness_db: float
    dynamic_range_db: float
    signal_to_noise_ratio: float
    peak_level_db: float
    clipping_detected: bool
    confidence: float
    recommendations: List[str]


@dataclass
class BeatMetadata:
    """Beat metadata extracted from audio"""
    bpm: float
    key: str
    time_signature: str
    duration_seconds: float
    energy: float
    danceability: float
    genres: List[str]
    mood: str
    instruments: List[str]


@dataclass
class GenreClassification:
    """Genre classification result"""
    primary_genre: str
    secondary_genres: List[str]
    confidence: float
    energy_level: str
    mood: str


class BeatAnalyzerService:
    """Service for analyzing beat audio files"""
    
    # Genre classification thresholds
    GENRE_CONFIDENCE_THRESHOLD = 0.6
    
    # Audio quality thresholds
    LOUDNESS_TARGET = -14  # LUFS (Loudness Units Relative to Full Scale)
    LOUDNESS_TOLERANCE = 2
    MIN_SNR = 20  # dB
    
    # Common genres and their frequency characteristics
    GENRE_CHARACTERISTICS = {
        "Afrobeat": {
            "tempo_range": (90, 120),
            "energy_range": (0.7, 1.0),
            "instruments": ["drums", "percussion", "bass", "horns"],
        },
        "Trap": {
            "tempo_range": (80, 140),
            "energy_range": (0.6, 0.9),
            "instruments": ["drums", "bass", "hi-hats", "synth"],
        },
        "Drill": {
            "tempo_range": (85, 115),
            "energy_range": (0.6, 0.85),
            "instruments": ["drums", "bass", "synth", "strings"],
        },
        "Dancehall": {
            "tempo_range": (90, 130),
            "energy_range": (0.7, 0.95),
            "instruments": ["drums", "bass", "samples", "vocals"],
        },
        "Hip Hop": {
            "tempo_range": (85, 115),
            "energy_range": (0.5, 0.85),
            "instruments": ["drums", "samples", "bass"],
        },
        "R&B": {
            "tempo_range": (60, 100),
            "energy_range": (0.4, 0.7),
            "instruments": ["bass", "keys", "drums", "strings"],
        },
        "Electronic": {
            "tempo_range": (100, 140),
            "energy_range": (0.6, 0.95),
            "instruments": ["synth", "bass", "drums"],
        },
        "Lo-Fi": {
            "tempo_range": (80, 100),
            "energy_range": (0.2, 0.5),
            "instruments": ["samples", "drums", "vinyl"],
        },
        "Amapiano": {
            "tempo_range": (100, 130),
            "energy_range": (0.65, 0.9),
            "instruments": ["keys", "bass", "drums", "percussion"],
        },
        "House": {
            "tempo_range": (120, 130),
            "energy_range": (0.7, 0.95),
            "instruments": ["bass", "drums", "synth"],
        },
        "Techno": {
            "tempo_range": (120, 150),
            "energy_range": (0.75, 1.0),
            "instruments": ["drums", "bass", "synth"],
        },
    }
    
    # Mood detection ranges (simplified)
    MOOD_CHARACTERISTICS = {
        "energetic": {"energy_min": 0.7, "valence_min": 0.6},
        "chill": {"energy_max": 0.5, "valence_min": 0.5},
        "dark": {"energy_min": 0.5, "valence_max": 0.4},
        "happy": {"valence_min": 0.7},
        "melancholic": {"valence_max": 0.4},
        "aggressive": {"energy_min": 0.8},
    }

    def __init__(self):
        """Initialize the beat analyzer service"""
        self.genre_cache = {}

    def analyze_audio_quality(
        self, audio_path: str, sr: int = 44100
    ) -> AudioQualityMetrics:
        """
        Analyze audio quality metrics
        
        Args:
            audio_path: Path to the audio file
            sr: Sample rate (default 44100 Hz)
            
        Returns:
            AudioQualityMetrics object with quality assessment
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=sr, mono=True)
            
            # Calculate loudness (LUFS approximation)
            loudness_db = self._calculate_loudness(y, sr)
            
            # Calculate dynamic range
            dynamic_range_db = self._calculate_dynamic_range(y)
            
            # Estimate signal-to-noise ratio
            snr = self._estimate_snr(y)
            
            # Detect clipping and peak level
            peak_level_db = 20 * np.log10(np.max(np.abs(y)) + 1e-10)
            clipping_detected = peak_level_db > -0.5
            
            # Determine quality level
            quality_level = self._classify_quality_level(
                loudness_db, dynamic_range_db, snr, peak_level_db
            )
            
            # Generate recommendations
            recommendations = self._generate_quality_recommendations(
                loudness_db, dynamic_range_db, snr, clipping_detected
            )
            
            # Calculate confidence (0-1)
            confidence = min(0.95, (snr / 50) * 0.95)
            
            return AudioQualityMetrics(
                quality_level=quality_level,
                loudness_db=float(loudness_db),
                dynamic_range_db=float(dynamic_range_db),
                signal_to_noise_ratio=float(snr),
                peak_level_db=float(peak_level_db),
                clipping_detected=clipping_detected,
                confidence=float(confidence),
                recommendations=recommendations,
            )
        
        except Exception as e:
            raise ValueError(f"Failed to analyze audio quality: {str(e)}")

    def extract_metadata(
        self, audio_path: str, sr: int = 44100
    ) -> BeatMetadata:
        """
        Extract metadata from beat audio
        
        Args:
            audio_path: Path to the audio file
            sr: Sample rate
            
        Returns:
            BeatMetadata object with extracted information
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=sr, mono=True)
            
            # Estimate tempo (BPM)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            bpm, _ = librosa.beat.tempo(y=y, sr=sr)
            bpm = float(bpm)
            
            # Estimate key (simplified: using chroma features)
            key = self._estimate_key(y, sr)
            
            # Time signature (default 4/4 for most beats)
            time_signature = "4/4"
            
            # Duration
            duration_seconds = librosa.get_duration(y=y, sr=sr)
            
            # Calculate features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            # Energy (RMS)
            rms = librosa.feature.rms(y=y)[0]
            energy = float(np.mean(rms))
            
            # Danceability (based on onset strength and spectral features)
            danceability = self._calculate_danceability(y, sr, onset_env)
            
            # Estimate mood based on energy and spectral characteristics
            mood = self._estimate_mood(energy, danceability, spectral_centroid)
            
            # Classify genres (placeholder - returns top genres)
            genre_info = self.classify_genre(y, sr, bpm)
            genres = [genre_info.primary_genre] + genre_info.secondary_genres
            
            # Estimate instruments
            instruments = self._estimate_instruments(y, sr, mfcc)
            
            return BeatMetadata(
                bpm=bpm,
                key=key,
                time_signature=time_signature,
                duration_seconds=float(duration_seconds),
                energy=energy,
                danceability=danceability,
                genres=genres,
                mood=mood,
                instruments=instruments,
            )
        
        except Exception as e:
            raise ValueError(f"Failed to extract metadata: {str(e)}")

    def classify_genre(
        self, y: np.ndarray, sr: int, bpm: float
    ) -> GenreClassification:
        """
        Classify the genre of the beat
        
        Args:
            y: Audio time series
            sr: Sample rate
            bpm: Beats per minute
            
        Returns:
            GenreClassification with primary and secondary genres
        """
        try:
            # Extract features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            rms = librosa.feature.rms(y=y)[0]
            
            energy = float(np.mean(rms))
            sc_mean = float(np.mean(spectral_centroid))
            sr_mean = float(np.mean(spectral_rolloff))
            
            # Calculate genre scores based on BPM and spectral features
            genre_scores = {}
            
            for genre, characteristics in self.GENRE_CHARACTERISTICS.items():
                tempo_range = characteristics["tempo_range"]
                energy_range = characteristics["energy_range"]
                
                # BPM match score
                tempo_match = 1.0 if tempo_range[0] <= bpm <= tempo_range[1] else 0.5
                
                # Energy match score
                energy_match = (
                    1.0
                    if energy_range[0] <= energy <= energy_range[1]
                    else 0.7
                )
                
                # Spectral characteristics (simplified)
                if genre in ["Afrobeat", "Dancehall", "Amapiano"]:
                    spectral_match = 0.8 if 1500 < sc_mean < 4000 else 0.6
                elif genre in ["Electronic", "Techno", "House"]:
                    spectral_match = 0.8 if sc_mean > 4000 else 0.6
                elif genre == "Lo-Fi":
                    spectral_match = 0.8 if sc_mean < 2500 else 0.6
                else:
                    spectral_match = 0.7
                
                # Combined score
                genre_scores[genre] = (tempo_match * 0.4 + energy_match * 0.4 + spectral_match * 0.2)
            
            # Sort by score
            sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
            
            primary_genre = sorted_genres[0][0]
            primary_confidence = min(0.95, sorted_genres[0][1])
            
            secondary_genres = [g[0] for g in sorted_genres[1:3]]
            
            # Determine energy level
            if energy > 0.75:
                energy_level = "high"
            elif energy > 0.5:
                energy_level = "medium"
            else:
                energy_level = "low"
            
            # Estimate mood
            mood = self._estimate_mood(energy, energy, spectral_centroid)
            
            return GenreClassification(
                primary_genre=primary_genre,
                secondary_genres=secondary_genres,
                confidence=float(primary_confidence),
                energy_level=energy_level,
                mood=mood,
            )
        
        except Exception as e:
            raise ValueError(f"Failed to classify genre: {str(e)}")

    # Helper methods
    
    def _calculate_loudness(self, y: np.ndarray, sr: int) -> float:
        """Calculate loudness in LUFS (simplified)"""
        rms = np.sqrt(np.mean(y**2))
        loudness = 20 * np.log10(rms + 1e-10)
        return loudness

    def _calculate_dynamic_range(self, y: np.ndarray) -> float:
        """Calculate dynamic range in dB"""
        max_val = np.max(np.abs(y))
        min_val = np.min(np.abs(y[np.abs(y) > 1e-5]))  # Avoid silence
        if min_val == 0:
            return 0
        return 20 * np.log10(max_val / (min_val + 1e-10))

    def _estimate_snr(self, y: np.ndarray, frame_length: int = 2048) -> float:
        """Estimate signal-to-noise ratio"""
        frames = librosa.util.frame(y, frame_length, frame_length // 2)
        frame_rms = np.sqrt(np.mean(frames**2, axis=0))
        
        # Assume noise is in the quietest 10%
        noise_power = np.min(frame_rms)
        signal_power = np.mean(frame_rms)
        
        snr = 20 * np.log10(signal_power / (noise_power + 1e-10))
        return float(np.clip(snr, 0, 60))

    def _classify_quality_level(
        self, loudness: float, dynamic_range: float, snr: float, peak: float
    ) -> AudioQualityLevel:
        """Classify overall audio quality level"""
        score = 0
        
        # Loudness score
        loudness_diff = abs(loudness - self.LOUDNESS_TARGET)
        if loudness_diff < self.LOUDNESS_TOLERANCE:
            score += 25
        elif loudness_diff < self.LOUDNESS_TOLERANCE + 2:
            score += 15
        else:
            score += 5
        
        # Dynamic range score
        if dynamic_range > 10:
            score += 25
        elif dynamic_range > 6:
            score += 15
        else:
            score += 5
        
        # SNR score
        if snr > self.MIN_SNR:
            score += 25
        elif snr > self.MIN_SNR - 5:
            score += 15
        else:
            score += 5
        
        # Peak level score
        if peak < -3:
            score += 25
        elif peak < -1:
            score += 15
        else:
            score += 5
        
        if score >= 90:
            return AudioQualityLevel.EXCELLENT
        elif score >= 75:
            return AudioQualityLevel.GOOD
        elif score >= 60:
            return AudioQualityLevel.FAIR
        else:
            return AudioQualityLevel.POOR

    def _generate_quality_recommendations(
        self, loudness: float, dynamic_range: float, snr: float, clipping: bool
    ) -> List[str]:
        """Generate recommendations for audio improvement"""
        recommendations = []
        
        if clipping:
            recommendations.append("Reduce input levels to prevent clipping")
        
        loudness_diff = abs(loudness - self.LOUDNESS_TARGET)
        if loudness < self.LOUDNESS_TARGET - self.LOUDNESS_TOLERANCE:
            recommendations.append(f"Increase loudness by approximately {self.LOUDNESS_TARGET - loudness:.1f} dB")
        elif loudness > self.LOUDNESS_TARGET + self.LOUDNESS_TOLERANCE:
            recommendations.append(f"Reduce loudness by approximately {loudness - self.LOUDNESS_TARGET:.1f} dB")
        
        if dynamic_range < 6:
            recommendations.append("Improve dynamic range - reduce compression")
        
        if snr < self.MIN_SNR:
            recommendations.append("Reduce background noise and improve signal quality")
        
        if not recommendations:
            recommendations.append("Audio quality is excellent - no changes needed")
        
        return recommendations

    def _estimate_key(self, y: np.ndarray, sr: int) -> str:
        """Estimate musical key (simplified)"""
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        key_index = np.argmax(chroma_mean)
        
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        note = notes[key_index]
        
        # Assume minor key (common in beats)
        return f"{note} minor"

    def _calculate_danceability(
        self, y: np.ndarray, sr: int, onset_env: np.ndarray
    ) -> float:
        """Calculate danceability score (0-1)"""
        # Based on onset strength and regular beat
        onset_mean = np.mean(onset_env)
        onset_std = np.std(onset_env)
        
        # Regularity score
        if onset_std > 0:
            regularity = min(1.0, onset_mean / onset_std)
        else:
            regularity = 0.5
        
        # Spectral centroid (higher frequency = more danceable)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        sc_mean = np.mean(spectral_centroid)
        spectral_score = min(1.0, sc_mean / 5000)
        
        danceability = (regularity * 0.6 + spectral_score * 0.4)
        return float(np.clip(danceability, 0, 1))

    def _estimate_mood(
        self, energy: float, danceability: float, spectral_centroid: float
    ) -> str:
        """Estimate mood of the beat"""
        sc_mean = np.mean(spectral_centroid) if isinstance(spectral_centroid, np.ndarray) else spectral_centroid
        
        if energy > 0.75 and danceability > 0.7:
            return "energetic"
        elif energy < 0.5:
            return "chill"
        elif energy > 0.7 and sc_mean < 2000:
            return "dark"
        elif danceability > 0.7:
            return "happy"
        else:
            return "balanced"

    def _estimate_instruments(self, y: np.ndarray, sr: int, mfcc: np.ndarray) -> List[str]:
        """Estimate instruments in the beat (simplified)"""
        instruments = []
        
        # Spectral analysis
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        
        sc_mean = np.mean(spectral_centroid)
        sr_mean = np.mean(spectral_rolloff)
        
        # Low frequencies (< 200 Hz) = Bass
        if sc_mean > 50:
            instruments.append("drums")
        
        # Mid-low frequencies (200-800 Hz) = Bass
        if 200 < sc_mean < 2000:
            instruments.append("bass")
        
        # Mid frequencies (800-4000 Hz) = Keys/Synth
        if sc_mean > 1000:
            instruments.append("synth")
        
        # High frequencies (> 4000 Hz) = Hi-hats/Cymbals
        if sr_mean > 4000:
            instruments.append("hi-hats")
        
        # MFCC variation for percussion
        mfcc_var = np.mean(np.var(mfcc, axis=1))
        if mfcc_var > 20:
            if "percussion" not in instruments:
                instruments.append("percussion")
        
        return instruments if instruments else ["drums", "bass"]
