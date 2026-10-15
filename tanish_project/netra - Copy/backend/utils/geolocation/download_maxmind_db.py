"""
MaxMind GeoLite2 Database Download Script
Automates downloading and updating GeoLite2 databases
"""

import os
import gzip
import shutil
import logging
import requests
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MaxMindDatabaseDownloader:
    """Download and manage MaxMind GeoLite2 databases"""
    
    # Database URLs (require license key)
    CITY_DB_URL = "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key={license_key}&suffix=tar.gz"
    COUNTRY_DB_URL = "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country&license_key={license_key}&suffix=tar.gz"
    ASN_DB_URL = "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN&license_key={license_key}&suffix=tar.gz"
    
    def __init__(self, license_key: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize database downloader
        
        Args:
            license_key: MaxMind license key
            output_dir: Directory to save databases (default: backend/data/maxmind)
        """
        self.license_key = license_key or os.getenv('MAXMIND_LICENSE_KEY')
        
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Default to backend/data/maxmind
            backend_dir = Path(__file__).parent.parent.parent
            self.output_dir = backend_dir / 'data' / 'maxmind'
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.license_key:
            logger.warning("No MaxMind license key provided. Set MAXMIND_LICENSE_KEY environment variable.")
    
    def download_city_database(self) -> Optional[str]:
        """Download GeoLite2 City database"""
        if not self.license_key:
            logger.error("Cannot download: No license key available")
            return None
        
        url = self.CITY_DB_URL.format(license_key=self.license_key)
        return self._download_database(url, 'GeoLite2-City')
    
    def download_country_database(self) -> Optional[str]:
        """Download GeoLite2 Country database"""
        if not self.license_key:
            logger.error("Cannot download: No license key available")
            return None
        
        url = self.COUNTRY_DB_URL.format(license_key=self.license_key)
        return self._download_database(url, 'GeoLite2-Country')
    
    def download_asn_database(self) -> Optional[str]:
        """Download GeoLite2 ASN database"""
        if not self.license_key:
            logger.error("Cannot download: No license key available")
            return None
        
        url = self.ASN_DB_URL.format(license_key=self.license_key)
        return self._download_database(url, 'GeoLite2-ASN')
    
    def _download_database(self, url: str, db_name: str) -> Optional[str]:
        """Download and extract database"""
        try:
            logger.info(f"Downloading {db_name} database...")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Save tar.gz file
            tar_gz_path = self.output_dir / f"{db_name}.tar.gz"
            with open(tar_gz_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded {db_name} database to {tar_gz_path}")
            
            # Extract .mmdb file from tar.gz
            import tarfile
            with tarfile.open(tar_gz_path, 'r:gz') as tar:
                # Find the .mmdb file
                mmdb_file = None
                for member in tar.getmembers():
                    if member.name.endswith('.mmdb'):
                        mmdb_file = member
                        break
                
                if mmdb_file:
                    tar.extract(mmdb_file, path=self.output_dir)
                    extracted_path = self.output_dir / mmdb_file.name
                    
                    # Rename to standard name
                    standard_name = f"{db_name}.mmdb"
                    standard_path = self.output_dir / standard_name
                    
                    if extracted_path.exists():
                        shutil.move(str(extracted_path), str(standard_path))
                        logger.info(f"Extracted database to {standard_path}")
                        
                        # Clean up tar.gz
                        tar_gz_path.unlink()
                        
                        return str(standard_path)
                else:
                    logger.error(f"No .mmdb file found in {db_name}.tar.gz")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to download {db_name} database: {e}")
            return None
    
    def download_all(self) -> dict:
        """Download all available databases"""
        results = {
            'city': self.download_city_database(),
            'country': self.download_country_database(),
            'asn': self.download_asn_database()
        }
        
        # Count successful downloads
        successful = sum(1 for v in results.values() if v is not None)
        logger.info(f"Downloaded {successful}/3 databases successfully")
        
        return results


def setup_maxmind_environment():
    """
    Setup MaxMind environment for the project
    This function helps guide users through setup
    """
    print("""
    MaxMind GeoLite2 Database Setup
    ================================
    
    To use MaxMind geolocation, you need:
    
    1. A MaxMind account (free): https://www.maxmind.com/en/geolite2/signup
    2. A license key: https://www.maxmind.com/en/accounts/current/license-key
    
    After obtaining your license key:
    
    Option 1: Set environment variable
    --------------------------------
    export MAXMIND_LICENSE_KEY=your_license_key_here
    
    Option 2: Add to .env file
    --------------------------
    MAXMIND_LICENSE_KEY=your_license_key_here
    MAXMIND_ACCOUNT_ID=your_account_id (for web service)
    
    Option 3: Pass directly to functions
    --------------------------------------
    downloader = MaxMindDatabaseDownloader(license_key='your_key')
    provider = MaxMindProvider(license_key='your_key')
    
    After setup:
    -----------
    1. Download databases: python download_maxmind_db.py
    2. Test provider: python maxmind_provider.py
    3. Update DNS scanner to use MaxMind
    """)


if __name__ == '__main__':
    setup_maxmind_environment()
