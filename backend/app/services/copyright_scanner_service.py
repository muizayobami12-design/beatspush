"""
Copyright Scanner Service for AI Promotion Platform

Scans beats for potential copyright issues and similar content.
Uses audio fingerprinting (Chromaprint) with AcoustID-like comparison.
"""

import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import librosa


class CopyrightRiskLevel(str, Enum):
    """Copyright risk levels"""
    CLEAR = "clear"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


@dataclass
class CopyrightMatch:
    """Result of a copyright match"""
    beat_id: str
    beat_title: str
    similarity_score: float  # 0-1, higher = more similar
    risk_level: CopyrightRiskLevel
    reason: str


@dataclass
class CopyrightScanResult:
    """Complete copyright scan result"""
    beat_id: str
    fingerprint: str
    risk_level: CopyrightRiskLevel
    matches: List[CopyrightMatch]
    is_original: bool
    confidence: float
    recommendations: List[str]


class CopyrightScannerService:
    """Service for scanning copyright and detecting similar content"""
    
    # Fingerprinting parameters
    FINGERPRINT_LENGTH = 32  # Hash length for comparison
    SIMILARITY_THRESHOLD_HIGH = 0.85
    SIMILARITY_THRESHOLD_MEDIUM = 0.65
    SIMILARITY_THRESHOLD_LOW = 0.45
    
    # Maximum allowed similarity for original content
    MAX_SIMILARITY_FOR_ORIGINAL = 0.3
    
    def __init__(self):
        """Initialize the copyright scanner service"""
        self.fingerprint_database = {}  # In production: use external database like AcoustID
        self.blocked_patterns = []
        self.copyright_database = {}

    def scan_beat_copyright(
        self, audio_path: str, beat_id: str, sr: int = 22050
    ) -> CopyrightScanResult:
        """
        Scan a beat for copyright issues
        
        Args:
            audio_path: Path to the audio file
            beat_id: Unique identifier for the beat
            sr: Sample rate
            
        Returns:
            CopyrightScanResult with findings
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=sr, mono=True)
            
            # Generate fingerprint
            fingerprint = self._generate_fingerprint(y, sr)
            
            # Scan against known database
            matches = self._find_matches(fingerprint, beat_id)
            
            # Calculate risk level
            risk_level = self._calculate_risk_level(matches)
            
            # Determine if original
            is_original = risk_level in [CopyrightRiskLevel.CLEAR, CopyrightRiskLevel.LOW]
            
            # Calculate confidence
            confidence = self._calculate_confidence(matches)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_level, matches)
            
            return CopyrightScanResult(
                beat_id=beat_id,
                fingerprint=fingerprint,
                risk_level=risk_level,
                matches=matches,
                is_original=is_original,
                confidence=confidence,
                recommendations=recommendations,
            )
        
        except Exception as e:
            raise ValueError(f"Failed to scan copyright: {str(e)}")

    def compare_beats(
        self, audio_path1: str, audio_path2: str, sr: int = 22050
    ) -> float:
        """
        Compare two beats for similarity
        
        Args:
            audio_path1: Path to first audio file
            audio_path2: Path to second audio file
            sr: Sample rate
            
        Returns:
            Similarity score (0-1, where 1 is identical)
        """
        try:
            # Load both audio files
            y1, sr = librosa.load(audio_path1, sr=sr, mono=True)
            y2, sr = librosa.load(audio_path2, sr=sr, mono=True)
            
            # Generate fingerprints
            fp1 = self._generate_fingerprint(y1, sr)
            fp2 = self._generate_fingerprint(y2, sr)
            
            # Calculate similarity
            similarity = self._calculate_fingerprint_similarity(fp1, fp2)
            
            return float(similarity)
        
        except Exception as e:
            raise ValueError(f"Failed to compare beats: {str(e)}")

    def add_to_database(
        self, beat_id: str, audio_path: str, beat_title: str, sr: int = 22050
    ) -> None:
        """
        Add a beat to the copyright database
        
        Args:
            beat_id: Unique identifier
            audio_path: Path to audio file
            beat_title: Title of the beat
            sr: Sample rate
        """
        try:
            y, sr = librosa.load(audio_path, sr=sr, mono=True)
            fingerprint = self._generate_fingerprint(y, sr)
            
            self.copyright_database[beat_id] = {
                "fingerprint": fingerprint,
                "title": beat_title,
                "timestamp": np.datetime64('now'),
            }
        
        except Exception as e:
            raise ValueError(f"Failed to add beat to database: {str(e)}")

    def check_against_known_samples(self, audio_path: str, sr: int = 22050) -> List[Dict]:
        """
        Check if beat contains known samples or loops
        
        Args:
            audio_path: Path to the audio file
            sr: Sample rate
            
        Returns:
            List of detected known samples
        """
        try:
            y, sr = librosa.load(audio_path, sr=sr, mono=True)
            
            # Segment audio into chunks for sample detection
            segment_length = sr * 10  # 10-second segments
            detected_samples = []
            
            for i in range(0, len(y), segment_length):
                segment = y[i : i + segment_length]
                
                if len(segment) < sr * 2:  # Skip segments shorter than 2 seconds
                    continue
                
                # Generate fingerprint for segment
                segment_fp = self._generate_fingerprint(segment, sr)
                
                # Check against known samples database
                for sample_id, sample_data in self.copyright_database.items():
                    similarity = self._calculate_fingerprint_similarity(
                        segment_fp, sample_data["fingerprint"]
                    )
                    
                    if similarity > self.SIMILARITY_THRESHOLD_MEDIUM:
                        detected_samples.append(
                            {
                                "sample_id": sample_id,
                                "sample_title": sample_data.get("title", "Unknown"),
                                "similarity": float(similarity),
                                "timestamp_start": float(i / sr),
                                "timestamp_end": float((i + len(segment)) / sr),
                            }
                        )
            
            return detected_samples
        
        except Exception as e:
            raise ValueError(f"Failed to check against known samples: {str(e)}")

    # Helper methods
    
    def _generate_fingerprint(self, y: np.ndarray, sr: int) -> str:
        """
        Generate audio fingerprint using simplified Chromaprint-like approach
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            Fingerprint hash string
        """
        try:
            # Extract chroma features (12 pitch classes)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, n_chroma=12)
            
            # Aggregate chroma over time (create signature)
            chroma_mean = np.mean(chroma, axis=1)
            chroma_std = np.std(chroma, axis=1)
            
            # Extract MFCC
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1)
            mfcc_std = np.std(mfcc, axis=1)
            
            # Extract spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            sc_mean = np.mean(spectral_centroid)
            sc_std = np.std(spectral_centroid)
            
            # Combine features into fingerprint
            fingerprint_vector = np.concatenate([
                chroma_mean,
                chroma_std,
                mfcc_mean,
                mfcc_std,
                [sc_mean, sc_std, np.mean(spectral_rolloff), np.std(spectral_rolloff)],
            ])
            
            # Quantize to reduce fingerprint size
            fingerprint_quantized = (fingerprint_vector * 100).astype(np.int32)
            
            # Create hash
            fingerprint_str = hashlib.sha256(
                fingerprint_quantized.tobytes()
            ).hexdigest()[:self.FINGERPRINT_LENGTH]
            
            return fingerprint_str
        
        except Exception:
            # Fallback: simple hash of audio data
            audio_hash = hashlib.sha256(y.tobytes()).hexdigest()[:self.FINGERPRINT_LENGTH]
            return audio_hash

    def _calculate_fingerprint_similarity(self, fp1: str, fp2: str) -> float:
        """
        Calculate similarity between two fingerprints
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            Similarity score (0-1)
        """
        if fp1 == fp2:
            return 1.0
        
        # Hamming distance approach for hex strings
        matches = sum(c1 == c2 for c1, c2 in zip(fp1, fp2))
        similarity = matches / len(fp1)
        
        return float(similarity)

    def _find_matches(
        self, fingerprint: str, beat_id: str, top_n: int = 5
    ) -> List[CopyrightMatch]:
        """
        Find matches in copyright database
        
        Args:
            fingerprint: Beat fingerprint
            beat_id: Beat ID to exclude from results
            top_n: Number of top matches to return
            
        Returns:
            List of matches sorted by similarity
        """
        matches = []
        
        for db_beat_id, db_data in self.copyright_database.items():
            if db_beat_id == beat_id:
                continue  # Skip self-comparison
            
            similarity = self._calculate_fingerprint_similarity(
                fingerprint, db_data["fingerprint"]
            )
            
            if similarity > self.SIMILARITY_THRESHOLD_LOW:
                # Determine risk level based on similarity
                if similarity > self.SIMILARITY_THRESHOLD_HIGH:
                    risk = CopyrightRiskLevel.HIGH
                    reason = "Very similar to existing content"
                elif similarity > self.SIMILARITY_THRESHOLD_MEDIUM:
                    risk = CopyrightRiskLevel.MEDIUM
                    reason = "Moderate similarity to existing content"
                else:
                    risk = CopyrightRiskLevel.LOW
                    reason = "Minor similarities detected"
                
                matches.append(
                    CopyrightMatch(
                        beat_id=db_beat_id,
                        beat_title=db_data.get("title", "Unknown"),
                        similarity_score=float(similarity),
                        risk_level=risk,
                        reason=reason,
                    )
                )
        
        # Sort by similarity and return top N
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        return matches[:top_n]

    def _calculate_risk_level(self, matches: List[CopyrightMatch]) -> CopyrightRiskLevel:
        """Calculate overall copyright risk level"""
        if not matches:
            return CopyrightRiskLevel.CLEAR
        
        # Find highest risk from matches
        highest_risk = max(match.risk_level for match in matches)
        
        if highest_risk == CopyrightRiskLevel.HIGH:
            # Check if multiple high-similarity matches
            high_matches = [m for m in matches if m.similarity_score > self.SIMILARITY_THRESHOLD_HIGH]
            if len(high_matches) > 1:
                return CopyrightRiskLevel.BLOCKED
            return CopyrightRiskLevel.HIGH
        
        return highest_risk

    def _calculate_confidence(self, matches: List[CopyrightMatch]) -> float:
        """Calculate confidence of the scan result"""
        if not matches:
            return 0.95
        
        # Confidence decreases with very similar matches
        highest_similarity = matches[0].similarity_score
        
        if highest_similarity > self.SIMILARITY_THRESHOLD_HIGH:
            return 0.95
        elif highest_similarity > self.SIMILARITY_THRESHOLD_MEDIUM:
            return 0.85
        else:
            return 0.75

    def _generate_recommendations(
        self, risk_level: CopyrightRiskLevel, matches: List[CopyrightMatch]
    ) -> List[str]:
        """Generate recommendations based on scan results"""
        recommendations = []
        
        if risk_level == CopyrightRiskLevel.CLEAR:
            recommendations.append("✓ Beat appears to be original")
            recommendations.append("✓ No copyright concerns detected")
        
        elif risk_level == CopyrightRiskLevel.LOW:
            recommendations.append("✓ Beat is likely original")
            recommendations.append("⚠ Minor similarities found - likely coincidental")
        
        elif risk_level == CopyrightRiskLevel.MEDIUM:
            recommendations.append("⚠ Moderate similarity to existing content")
            if matches:
                recommendations.append(
                    f"⚠ Consider modifying to differentiate from: {matches[0].beat_title}"
                )
            recommendations.append("✓ Additional melody or arrangement changes recommended")
        
        elif risk_level == CopyrightRiskLevel.HIGH:
            recommendations.append("❌ High similarity to existing content")
            if matches:
                recommendations.append(
                    f"❌ Very similar to: {matches[0].beat_title} ({matches[0].similarity_score:.1%})"
                )
            recommendations.append("❌ Significant changes needed before publishing")
        
        elif risk_level == CopyrightRiskLevel.BLOCKED:
            recommendations.append("❌ Multiple copyright concerns detected")
            recommendations.append("❌ This beat cannot be published as-is")
            recommendations.append("❌ Seek professional advice or create original content")
        
        return recommendations
