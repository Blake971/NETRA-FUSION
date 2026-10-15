"""
Data normalization engine for geolocation data.
Standardizes country names, city names, and other fields across providers.
"""

from typing import Optional, Dict, Any


class DataNormalizer:
    """Normalizes geolocation data to ensure consistency across providers."""
    
    # Country name normalization
    COUNTRY_ALIASES = {
        'USA': 'United States',
        'United States of America': 'United States',
        'US': 'United States',
        'UK': 'United Kingdom',
        'Great Britain': 'United Kingdom',
        'UAE': 'United Arab Emirates',
        'Korea, Republic of': 'South Korea',
        'Korea, Democratic People\'s Republic of': 'North Korea',
        'Russian Federation': 'Russia',
        'Viet Nam': 'Vietnam',
        'Brunei Darussalam': 'Brunei',
        'Czech Republic': 'Czechia',
        'Macedonia, Republic of': 'North Macedonia',
        'Syrian Arab Republic': 'Syria',
        'Taiwan, Province of China': 'Taiwan',
        'Tanzania, United Republic of': 'Tanzania',
        'Venezuela, Bolivarian Republic of': 'Venezuela',
        'Iran, Islamic Republic of': 'Iran',
        'Bolivia, Plurinational State of': 'Bolivia',
        'Micronesia, Federated States of': 'Micronesia',
        'Moldova, Republic of': 'Moldova',
        'Lao People\'s Democratic Republic': 'Laos',
        'Saint Kitts and Nevis': 'Saint Kitts & Nevis',
        'Saint Vincent and the Grenadines': 'Saint Vincent & the Grenadines',
        'Sao Tome and Principe': 'São Tomé and Príncipe',
        'Trinidad and Tobago': 'Trinidad & Tobago',
        'Hong Kong': 'Hong Kong',
        'Macau': 'Macau',
        'Palestine, State of': 'Palestine',
        'Kosovo': 'Kosovo',
    }
    
    # City name normalization
    CITY_ALIASES = {
        'Bangalore': 'Bengaluru',
        'Calcutta': 'Kolkata',
        'Bombay': 'Mumbai',
        'Madras': 'Chennai',
        'New York City': 'New York',
        'NYC': 'New York',
        'Los Angeles': 'Los Angeles',
        'LA': 'Los Angeles',
        'San Francisco': 'San Francisco',
        'SF': 'San Francisco',
        'Washington D.C.': 'Washington',
        'Washington DC': 'Washington',
        'Las Vegas': 'Las Vegas',
        'Chicago': 'Chicago',
        'Houston': 'Houston',
        'Phoenix': 'Phoenix',
        'Philadelphia': 'Philadelphia',
        'San Antonio': 'San Antonio',
        'San Diego': 'San Diego',
        'Dallas': 'Dallas',
        'San Jose': 'San Jose',
        'Austin': 'Austin',
        'Jacksonville': 'Jacksonville',
        'Fort Worth': 'Fort Worth',
        'Columbus': 'Columbus',
        'Charlotte': 'Charlotte',
        'San Francisco': 'San Francisco',
        'Indianapolis': 'Indianapolis',
        'Seattle': 'Seattle',
        'Denver': 'Denver',
        'Boston': 'Boston',
        'El Paso': 'El Paso',
        'Detroit': 'Detroit',
        'Nashville': 'Nashville',
        'Portland': 'Portland',
        'Memphis': 'Memphis',
        'Oklahoma City': 'Oklahoma City',
        'Las Vegas': 'Las Vegas',
        'Louisville': 'Louisville',
        'Baltimore': 'Baltimore',
        'Milwaukee': 'Milwaukee',
        'Albuquerque': 'Albuquerque',
        'Tucson': 'Albuquerque',
        'Fresno': 'Fresno',
        'Sacramento': 'Sacramento',
        'Mesa': 'Mesa',
        'Atlanta': 'Atlanta',
        'Kansas City': 'Kansas City',
        'Colorado Springs': 'Colorado Springs',
        'Raleigh': 'Raleigh',
        'Miami': 'Miami',
        'Long Beach': 'Long Beach',
        'Virginia Beach': 'Virginia Beach',
        'Oakland': 'Oakland',
        'Minneapolis': 'Minneapolis',
        'Tulsa': 'Tulsa',
        'Arlington': 'Arlington',
        'Tampa': 'Tampa',
        'New Orleans': 'New Orleans',
    }
    
    # State/region name normalization
    REGION_ALIASES = {
        'KA': 'Karnataka',
        'MH': 'Maharashtra',
        'TN': 'Tamil Nadu',
        'DL': 'Delhi',
        'WB': 'West Bengal',
        'UP': 'Uttar Pradesh',
        'GJ': 'Gujarat',
        'RJ': 'Rajasthan',
        'KL': 'Kerala',
        'PB': 'Punjab',
        'HR': 'Haryana',
        'MP': 'Madhya Pradesh',
        'AP': 'Andhra Pradesh',
        'TS': 'Telangana',
        'NY': 'New York',
        'CA': 'California',
        'TX': 'Texas',
        'FL': 'Florida',
        'IL': 'Illinois',
        'PA': 'Pennsylvania',
        'OH': 'Ohio',
        'GA': 'Georgia',
        'NC': 'North Carolina',
        'MI': 'Michigan',
        'NJ': 'New Jersey',
        'VA': 'Virginia',
        'WA': 'Washington',
        'AZ': 'Arizona',
        'MA': 'Massachusetts',
        'IN': 'Indiana',
        'MO': 'Missouri',
        'MD': 'Maryland',
        'WI': 'Wisconsin',
        'CO': 'Colorado',
        'MN': 'Minnesota',
        'SC': 'South Carolina',
        'AL': 'Alabama',
        'LA': 'Louisiana',
        'KY': 'Kentucky',
        'OR': 'Oregon',
        'OK': 'Oklahoma',
        'CT': 'Connecticut',
        'UT': 'Utah',
        'IA': 'Iowa',
        'NV': 'Nevada',
        'AR': 'Arkansas',
        'MS': 'Mississippi',
        'KS': 'Kansas',
        'NM': 'New Mexico',
        'NE': 'Nebraska',
        'ID': 'Idaho',
        'WV': 'West Virginia',
        'HI': 'Hawaii',
        'NH': 'New Hampshire',
        'ME': 'Maine',
        'MT': 'Montana',
        'RI': 'Rhode Island',
        'DE': 'Delaware',
        'SD': 'South Dakota',
        'ND': 'North Dakota',
        'AK': 'Alaska',
        'VT': 'Vermont',
        'WY': 'Wyoming',
    }
    
    @classmethod
    def normalize_country(cls, country: Optional[str]) -> Optional[str]:
        """Normalize country name to standard format."""
        if not country:
            return None
        
        # Remove extra whitespace
        country = country.strip()
        
        # Check aliases
        if country in cls.COUNTRY_ALIASES:
            return cls.COUNTRY_ALIASES[country]
        
        # Capitalize properly
        return country.title()
    
    @classmethod
    def normalize_city(cls, city: Optional[str]) -> Optional[str]:
        """Normalize city name to standard format."""
        if not city:
            return None
        
        # Remove extra whitespace
        city = city.strip()
        
        # Check aliases
        if city in cls.CITY_ALIASES:
            return cls.CITY_ALIASES[city]
        
        # Capitalize properly
        return city.title()
    
    @classmethod
    def normalize_region(cls, region: Optional[str]) -> Optional[str]:
        """Normalize region/state name to standard format."""
        if not region:
            return None
        
        # Remove extra whitespace
        region = region.strip()
        
        # Check aliases
        if region.upper() in cls.REGION_ALIASES:
            return cls.REGION_ALIASES[region.upper()]
        
        # Capitalize properly
        return region.title()
    
    @classmethod
    def normalize_timezone(cls, timezone: Optional[str]) -> Optional[str]:
        """Normalize timezone to standard format."""
        if not timezone:
            return None
        
        # Remove extra whitespace
        timezone = timezone.strip()
        
        # Standardize timezone format
        timezone = timezone.replace(' ', '_')
        
        return timezone
    
    @classmethod
    def normalize_isp(cls, isp: Optional[str]) -> Optional[str]:
        """Normalize ISP name to standard format."""
        if not isp:
            return None
        
        # Remove extra whitespace
        isp = isp.strip()
        
        # Remove common prefixes/suffixes
        isp = isp.replace('Inc.', '').replace('Ltd.', '').replace('LLC', '')
        isp = isp.replace('Corporation', 'Corp').replace('Limited', 'Ltd')
        
        return isp.strip()
    
    @classmethod
    def normalize_asn(cls, asn: Optional[str]) -> Optional[str]:
        """Normalize ASN to standard format."""
        if not asn:
            return None
        
        # Remove extra whitespace
        asn = asn.strip()
        
        # Extract just the number if in format "AS12345"
        if asn.upper().startswith('AS'):
            asn = asn[2:]
        
        return asn
    
    @classmethod
    def normalize_provider_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize all fields in provider data."""
        normalized = data.copy()
        
        if 'country' in normalized:
            normalized['country'] = cls.normalize_country(normalized['country'])
        
        if 'city' in normalized:
            normalized['city'] = cls.normalize_city(normalized['city'])
        
        if 'region' in normalized:
            normalized['region'] = cls.normalize_region(normalized['region'])
        
        if 'timezone' in normalized:
            normalized['timezone'] = cls.normalize_timezone(normalized['timezone'])
        
        if 'isp' in normalized:
            normalized['isp'] = cls.normalize_isp(normalized['isp'])
        
        if 'asn' in normalized:
            normalized['asn'] = cls.normalize_asn(normalized['asn'])
        
        return normalized
