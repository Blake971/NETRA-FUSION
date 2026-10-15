"""
ASN intelligence module for detecting hosting providers and infrastructure.
"""

from typing import Optional, Set


class ASNAnalyzer:
    """Analyzes ASN to detect hosting providers and infrastructure."""
    
    # Known hosting provider ASNs and patterns
    HOSTING_ASNS = {
        # Cloudflare
        '13335', '209242',
        # AWS
        '16509', '14618', '7224',
        # Google Cloud
        '15169', '36040',
        # Azure
        '8075', '12076',
        # DigitalOcean
        '14061', '62567',
        # Oracle Cloud
        '31898',
        # Linode
        '63949',
        # Hetzner
        '24940',
        # OVH
        '16276',
        # Vultr
        '20473',
        # IBM Cloud
        '14992',
        # Alibaba Cloud
        '37963',
        # Tencent Cloud
        '132592',
        # Rackspace
        '19994',
        # Heroku
        '28317',
        # Fastly
        '54113',
        # Akamai
        '20940',
        # CloudFront
        '16509',
    }
    
    # Known hosting provider names
    HOSTING_NAMES = {
        'cloudflare', 'amazon', 'google cloud', 'google llc', 'microsoft azure',
        'digitalocean', 'oracle cloud', 'linode', 'hetzner', 'ovh', 'vultr',
        'ibm cloud', 'alibaba cloud', 'tencent cloud', 'rackspace', 'heroku',
        'fastly', 'akamai', 'cloudfront', 'aws', 'gcp', 'azure'
    }
    
    # Known mobile network ASNs
    MOBILE_ASNS = {
        # Verizon
        '701', '702', '6167',
        # AT&T
        '20057', '20115', '2828',
        # T-Mobile
        '21928', '21949',
        # Vodafone
        '5378', '6033',
        # China Mobile
        '9808', '56040',
        # Reliance Jio
        '55836',
        # Airtel
        '9498',
        # Others
        '4589', '4560', '45899', '131292'
    }
    
    @classmethod
    def is_hosting(cls, asn: Optional[str], isp: Optional[str], org: Optional[str]) -> bool:
        """Determine if the ASN belongs to a hosting provider."""
        if not asn and not isp and not org:
            return False
        
        # Check ASN
        if asn:
            clean_asn = cls._clean_asn(asn)
            if clean_asn in cls.HOSTING_ASNS:
                return True
        
        # Check ISP/Organization names
        for name in [isp, org]:
            if name:
                if cls._is_hosting_name(name):
                    return True
        
        return False
    
    @classmethod
    def is_mobile(cls, asn: Optional[str], isp: Optional[str], org: Optional[str]) -> bool:
        """Determine if the ASN belongs to a mobile network."""
        if not asn and not isp and not org:
            return False
        
        # Check ASN
        if asn:
            clean_asn = cls._clean_asn(asn)
            if clean_asn in cls.MOBILE_ASNS:
                return True
        
        # Check ISP/Organization names for mobile indicators
        for name in [isp, org]:
            if name:
                if cls._is_mobile_name(name):
                    return True
        
        return False
    
    @classmethod
    def _clean_asn(cls, asn: str) -> Optional[str]:
        """Extract ASN number from various formats."""
        if not asn:
            return None
        
        asn = asn.strip()
        
        # Remove 'AS' prefix if present
        if asn.upper().startswith('AS'):
            asn = asn[2:]
        
        # Extract just the number if there's additional text
        asn = asn.split()[0]
        
        return asn if asn.isdigit() else None
    
    @classmethod
    def _is_hosting_name(cls, name: str) -> bool:
        """Check if name contains hosting provider keywords."""
        name_lower = name.lower()
        return any(hosting in name_lower for hosting in cls.HOSTING_NAMES)
    
    @classmethod
    def _is_mobile_name(cls, name: str) -> bool:
        """Check if name contains mobile network keywords."""
        mobile_keywords = ['mobile', 'wireless', 'cellular', 'gsm', 'lte', '5g', '3g', '4g']
        name_lower = name.lower()
        return any(keyword in name_lower for keyword in mobile_keywords)
    
    @classmethod
    def get_hosting_provider(cls, asn: Optional[str], isp: Optional[str], org: Optional[str]) -> Optional[str]:
        """Identify the specific hosting provider if possible."""
        if not asn and not isp and not org:
            return None
        
        # Check ASN first
        if asn:
            clean_asn = cls._clean_asn(asn)
            if clean_asn in cls.HOSTING_ASNS:
                # Map ASN to provider name
                asn_to_provider = {
                    '13335': 'Cloudflare',
                    '209242': 'Cloudflare',
                    '16509': 'Amazon Web Services (AWS)',
                    '14618': 'Amazon Web Services (AWS)',
                    '15169': 'Google Cloud Platform',
                    '36040': 'Google Cloud Platform',
                    '8075': 'Microsoft Azure',
                    '12076': 'Microsoft Azure',
                    '14061': 'DigitalOcean',
                    '62567': 'DigitalOcean',
                    '31898': 'Oracle Cloud',
                    '63949': 'Linode',
                    '24940': 'Hetzner',
                    '16276': 'OVH',
                    '20473': 'Vultr',
                }
                return asn_to_provider.get(clean_asn)
        
        # Check ISP/Organization names
        for name in [isp, org]:
            if name:
                for hosting in cls.HOSTING_NAMES:
                    if hosting in name.lower():
                        return hosting.title()
        
        return None
