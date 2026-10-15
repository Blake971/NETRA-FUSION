"""
Main geolocation intelligence engine.
Orchestrates providers, normalization, consensus, and confidence calculation.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from .models import GeoLocationResult, ProviderData, Location, NetworkInfo, SecurityFlags
from .providers import get_all_providers, BaseProvider
from .normalization import DataNormalizer
from .consensus import ConsensusEngine
from .geographic import GeographicValidator
from .asn_intelligence import ASNAnalyzer
from .confidence import ConfidenceCalculator
from .cache import GeoLocationCache
from utils.logger import setup_logger


logger = setup_logger(__name__)


class GeoLocationEngine:
    """Main engine for intelligent IP geolocation."""
    
    def __init__(self, cache_file: str = 'geolocation_cache.json'):
        self.providers = get_all_providers()
        self.cache = GeoLocationCache(cache_file)
        self.normalizer = DataNormalizer()
    
    async def locate(self, ip: str, timeout: float = 3.0) -> GeoLocationResult:
        """
        Get geolocation for an IP address with maximum accuracy.
        
        Args:
            ip: IP address to locate
            timeout: Timeout for each provider request
            
        Returns:
            GeoLocationResult with confidence scoring
        """
        # Check cache first
        cached_result = self.cache.get(ip)
        if cached_result:
            logger.info(f"Cache hit for {ip}")
            return cached_result
        
        logger.info(f"Cache miss for {ip}, fetching from providers")
        
        # Fetch from all providers in parallel
        provider_data = await self._fetch_from_providers(ip, timeout)
        
        if not provider_data:
            # No providers responded
            return self._empty_result(ip)
        
        # Normalize data
        normalized_data = self._normalize_data(provider_data)
        
        # Compute consensus
        consensus_engine = ConsensusEngine(normalized_data)
        consensus = consensus_engine.compute_consensus()
        
        # Geographic clustering
        coordinates = [(p.latitude, p.longitude) for p in normalized_data 
                      if p.latitude and p.longitude]
        geographic_stats = GeographicValidator.calculate_cluster_stats(coordinates)
        
        # ASN analysis
        asn_analyzer = ASNAnalyzer()
        is_hosting = any(asn_analyzer.is_hosting(p.asn, p.isp, p.organization) 
                        for p in normalized_data)
        is_mobile = any(asn_analyzer.is_mobile(p.asn, p.isp, p.organization) 
                       for p in normalized_data)
        
        # Security flags from consensus
        security_flags = consensus.get('security', {})
        
        # Calculate confidence
        confidence_calc = ConfidenceCalculator(
            normalized_data, consensus, geographic_stats, is_hosting, security_flags
        )
        confidence = confidence_calc.calculate()
        confidence_level = confidence_calc.get_confidence_level(confidence)
        explanation = confidence_calc.generate_explanation(confidence)
        
        # Build result
        result = GeoLocationResult(
            ip=ip,
            location=Location(
                country=consensus.get('country'),
                state=consensus.get('region'),
                city=consensus.get('city'),
                postal_code=consensus.get('postal_code'),
                latitude=geographic_stats.get('avg_lat') if geographic_stats else None,
                longitude=geographic_stats.get('avg_lon') if geographic_stats else None
            ),
            network=NetworkInfo(
                isp=consensus.get('isp'),
                organization=consensus.get('organization'),
                asn=consensus.get('asn')
            ),
            security=SecurityFlags(
                vpn=security_flags.get('vpn', False),
                proxy=security_flags.get('proxy', False),
                tor=security_flags.get('tor', False),
                hosting=is_hosting,
                mobile=is_mobile
            ),
            confidence=confidence,
            confidence_level=confidence_level,
            explanation=explanation,
            provider_breakdown=[p.to_dict() for p in normalized_data],
            providers_used=[p.source for p in normalized_data],
            cached=False
        )
        
        # Cache the result
        self.cache.set(result, is_hosting=is_hosting, is_cloudflare=False)
        
        logger.info(f"Geolocation complete for {ip}: {consensus.get('country')} ({confidence}% confidence)")
        
        return result
    
    async def _fetch_from_providers(self, ip: str, timeout: float) -> List[ProviderData]:
        """Fetch data from all providers in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            future_to_provider = {
                executor.submit(p.fetch, ip, timeout): p 
                for p in self.providers
            }
            
            for future in as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                        logger.debug(f"Provider {provider.name} responded for {ip}")
                except Exception as e:
                    logger.warning(f"Provider {provider.name} failed for {ip}: {str(e)}")
        
        return results
    
    def _normalize_data(self, provider_data: List[ProviderData]) -> List[ProviderData]:
        """Normalize all provider data."""
        normalized = []
        
        for data in provider_data:
            normalized_dict = self.normalizer.normalize_provider_data(data.to_dict())
            normalized.append(ProviderData(**normalized_dict))
        
        return normalized
    
    def _empty_result(self, ip: str) -> GeoLocationResult:
        """Return empty result when no data is available."""
        return GeoLocationResult(
            ip=ip,
            confidence=0.0,
            confidence_level="VERY_LOW",
            explanation="No geolocation data available from any provider.",
            cached=False
        )
