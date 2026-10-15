"""
Confidence calculator for geolocation results.
Computes weighted scores based on multiple factors.
"""

from typing import Dict, Any, List
from .models import ProviderData


class ConfidenceCalculator:
    """Calculates confidence score for geolocation results."""
    
    # Weight configuration
    WEIGHTS = {
        'provider_agreement': 25,
        'country_agreement': 15,
        'region_agreement': 15,
        'city_agreement': 10,
        'coordinate_clustering': 10,
        'asn_agreement': 10,
        'timezone_agreement': 5,
        'isp_agreement': 5,
        'historical_cache': 5,
    }
    
    # Penalties
    PENALTIES = {
        'hosting': -10,
        'vpn': -10,
        'tor': -20,
        'proxy': -5,
        'coordinate_disagreement': -15,
        'timezone_mismatch': -10,
        'isp_mismatch': -10,
    }
    
    def __init__(self, providers: List[ProviderData], consensus: Dict[str, Any], 
                 geographic_stats: Dict[str, Any], is_hosting: bool, 
                 security_flags: Dict[str, bool]):
        self.providers = providers
        self.consensus = consensus
        self.geographic_stats = geographic_stats
        self.is_hosting = is_hosting
        self.security_flags = security_flags
    
    def calculate(self) -> float:
        """Calculate overall confidence score (0-100)."""
        score = 0.0
        
        # Base score from provider agreement
        score += self._provider_agreement_score()
        
        # Field agreement scores
        score += self._field_agreement_score()
        
        # Coordinate clustering score
        score += self._coordinate_clustering_score()
        
        # Apply penalties
        score += self._apply_penalties()
        
        # Normalize to 0-100
        score = max(0, min(100, score))
        
        return round(score, 1)
    
    def _provider_agreement_score(self) -> float:
        """Score based on number of providers that responded."""
        if not self.providers:
            return 0.0
        
        provider_count = len(self.providers)
        max_providers = 7  # Total number of providers
        
        # More providers = higher confidence
        ratio = provider_count / max_providers
        return ratio * self.WEIGHTS['provider_agreement']
    
    def _field_agreement_score(self) -> float:
        """Score based on agreement across fields."""
        agreement_scores = self.consensus.get('agreement_scores', {})
        
        score = 0.0
        
        # Country agreement (most important)
        score += agreement_scores.get('country', 0) * self.WEIGHTS['country_agreement']
        
        # Region agreement
        score += agreement_scores.get('region', 0) * self.WEIGHTS['region_agreement']
        
        # City agreement
        score += agreement_scores.get('city', 0) * self.WEIGHTS['city_agreement']
        
        # ASN agreement
        score += agreement_scores.get('asn', 0) * self.WEIGHTS['asn_agreement']
        
        # Timezone agreement
        score += agreement_scores.get('timezone', 0) * self.WEIGHTS['timezone_agreement']
        
        # ISP agreement
        score += agreement_scores.get('isp', 0) * self.WEIGHTS['isp_agreement']
        
        return score
    
    def _coordinate_clustering_score(self) -> float:
        """Score based on geographic clustering of coordinates."""
        if not self.geographic_stats:
            return 0.0
        
        consensus_radius = self.geographic_stats.get('consensus_radius', 0)
        
        # If coordinates are within 5km, high confidence
        if consensus_radius < 5:
            return self.WEIGHTS['coordinate_clustering']
        # If within 50km, moderate confidence
        elif consensus_radius < 50:
            return self.WEIGHTS['coordinate_clustering'] * 0.7
        # If within 100km, lower confidence
        elif consensus_radius < 100:
            return self.WEIGHTS['coordinate_clustering'] * 0.4
        # If more than 100km apart, very low confidence
        else:
            return self.WEIGHTS['coordinate_clustering'] * 0.1
    
    def _apply_penalties(self) -> float:
        """Apply penalties for suspicious indicators."""
        penalty = 0.0
        
        # Hosting penalty
        if self.is_hosting:
            penalty += self.PENALTIES['hosting']
        
        # VPN penalty
        if self.security_flags.get('vpn', False):
            penalty += self.PENALTIES['vpn']
        
        # TOR penalty
        if self.security_flags.get('tor', False):
            penalty += self.PENALTIES['tor']
        
        # Proxy penalty
        if self.security_flags.get('proxy', False):
            penalty += self.PENALTIES['proxy']
        
        # Coordinate disagreement penalty
        if self.geographic_stats and self.geographic_stats.get('consensus_radius', 0) > 100:
            penalty += self.PENALTIES['coordinate_disagreement']
        
        return penalty
    
    def get_confidence_level(self, score: float) -> str:
        """Get confidence level label based on score."""
        if score >= 80:
            return "HIGH"
        elif score >= 60:
            return "MODERATE"
        elif score >= 40:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def generate_explanation(self, score: float) -> str:
        """Generate human-readable explanation of confidence."""
        explanations = []
        
        # Provider count
        provider_count = len(self.providers)
        if provider_count >= 5:
            explanations.append(f"{provider_count} providers responded with consistent data.")
        elif provider_count >= 3:
            explanations.append(f"{provider_count} providers responded with mostly consistent data.")
        else:
            explanations.append(f"Only {provider_count} provider(s) responded.")
        
        # Coordinate clustering
        if self.geographic_stats:
            radius = self.geographic_stats.get('consensus_radius', 0)
            if radius < 5:
                explanations.append("Coordinates are tightly clustered (within 5km).")
            elif radius < 50:
                explanations.append(f"Coordinates are within {int(radius)}km of each other.")
            else:
                explanations.append(f"Coordinates differ significantly ({int(radius)}km apart).")
        
        # Security flags
        if self.security_flags.get('vpn', False):
            explanations.append("VPN indicators detected.")
        if self.security_flags.get('tor', False):
            explanations.append("TOR network detected.")
        if self.security_flags.get('proxy', False):
            explanations.append("Proxy indicators detected.")
        
        # Hosting
        if self.is_hosting:
            explanations.append("Hosting provider detected - location may be data center.")
        
        # Agreement
        agreement_scores = self.consensus.get('agreement_scores', {})
        country_agreement = agreement_scores.get('country', 0)
        if country_agreement >= 0.8:
            explanations.append("Strong agreement on country location.")
        elif country_agreement >= 0.5:
            explanations.append("Moderate agreement on country location.")
        else:
            explanations.append("Low agreement on country location.")
        
        return " ".join(explanations)
