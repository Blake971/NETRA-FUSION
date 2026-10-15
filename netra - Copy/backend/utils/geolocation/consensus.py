"""
Consensus engine for determining the most likely location from multiple providers.
Uses weighted voting and field comparison to reach consensus.
"""

from typing import List, Dict, Any, Optional
from collections import Counter
from .models import ProviderData


class ConsensusEngine:
    """Engine for computing consensus from multiple provider responses."""
    
    def __init__(self, providers: List[ProviderData]):
        self.providers = providers
        self.provider_weights = {p.source: 0.3 if 'ip-api' in p.source else 
                                  0.25 if 'ipinfo' in p.source else
                                  0.20 if 'ipapi.co' in p.source else
                                  0.10 if 'ipwho' in p.source or 'freeipapi' in p.source else
                                  0.05 for p in providers}
    
    def compute_consensus(self) -> Dict[str, Any]:
        """Compute consensus for all fields."""
        if not self.providers:
            return {}
        
        consensus = {
            'country': self._field_consensus('country'),
            'country_code': self._field_consensus('country_code'),
            'region': self._field_consensus('region'),
            'city': self._field_consensus('city'),
            'postal_code': self._field_consensus('postal_code'),
            'timezone': self._field_consensus('timezone'),
            'isp': self._field_consensus('isp'),
            'organization': self._field_consensus('organization'),
            'asn': self._field_consensus('asn'),
            'latitude': self._coordinate_consensus('latitude'),
            'longitude': self._coordinate_consensus('longitude'),
            'security': self._security_consensus()
        }
        
        consensus['agreement_scores'] = self._compute_agreement_scores()
        
        return consensus
    
    def _field_consensus(self, field: str) -> Optional[str]:
        """Compute consensus for a text field using weighted voting."""
        votes = {}
        
        for provider in self.providers:
            value = getattr(provider, field, None)
            if value:
                weight = self.provider_weights.get(provider.source, 0.1)
                votes[value] = votes.get(value, 0) + weight
        
        if not votes:
            return None
        
        # Return the value with highest weight
        return max(votes, key=votes.get)
    
    def _coordinate_consensus(self, field: str) -> Optional[float]:
        """Compute consensus for coordinate fields using weighted average."""
        values = []
        weights = []
        
        for provider in self.providers:
            value = getattr(provider, field, None)
            if value is not None:
                weight = self.provider_weights.get(provider.source, 0.1)
                values.append(value)
                weights.append(weight)
        
        if not values:
            return None
        
        # Weighted average
        total_weight = sum(weights)
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        return weighted_sum / total_weight if total_weight > 0 else None
    
    def _security_consensus(self) -> Dict[str, bool]:
        """Compute consensus for security flags using OR logic."""
        return {
            'vpn': any(p.vpn for p in self.providers),
            'proxy': any(p.proxy for p in self.providers),
            'tor': any(p.tor for p in self.providers),
            'hosting': any(p.hosting for p in self.providers),
            'mobile': any(p.mobile for p in self.providers)
        }
    
    def _compute_agreement_scores(self) -> Dict[str, float]:
        """Compute agreement scores for each field (0-1)."""
        fields = ['country', 'region', 'city', 'timezone', 'isp', 'asn']
        scores = {}
        
        for field in fields:
            values = [getattr(p, field, None) for p in self.providers]
            values = [v for v in values if v]
            
            if not values:
                scores[field] = 0.0
                continue
            
            # Count unique values
            unique_values = len(set(values))
            total_values = len(values)
            
            # Agreement is inverse of unique/total ratio
            scores[field] = 1.0 - (unique_values - 1) / total_values if total_values > 0 else 0.0
        
        return scores
