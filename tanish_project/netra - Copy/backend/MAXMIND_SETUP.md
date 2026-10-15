# MaxMind GeoIP2 Integration Setup Guide

## Overview

The Netra security tool now integrates MaxMind GeoIP2 for highly accurate IP geolocation. This guide explains how to set up MaxMind to improve geolocation accuracy, especially for government and regional ISP addresses.

## Current Status

**Without MaxMind Setup:**
- System uses fallback providers (ipinfo.io, freeipapi.com)
- Confidence: 100% (2/2 providers)
- Accuracy: Good for major ISPs, limited for regional/government networks
- Example: Telangana government IP shows Mumbai instead of Hyderabad

**With MaxMind Setup:**
- System uses MaxMind as primary provider
- Confidence: Based on accuracy radius (50-95%)
- Accuracy: Industry-standard, better government/regional data
- Includes accuracy radius information (e.g., ±50km)

## Setup Instructions

### Step 1: Create MaxMind Account

1. Go to [MaxMind GeoLite2 Signup](https://www.maxmind.com/en/geolite2/signup)
2. Create a free account
3. Verify your email address

### Step 2: Generate License Key

1. Log in to your MaxMind account
2. Go to [License Keys](https://www.maxmind.com/en/accounts/current/license-key)
3. Click "Generate a license key"
4. Note your **Account ID** and **License Key**

### Step 3: Choose Integration Method

**Option A: Local Database (Recommended)**
- Unlimited lookups
- Faster performance
- No network calls
- Requires periodic database updates

**Option B: Web Service**
- 1000 lookups/day free limit
- No database management
- Slower performance
- Requires network calls

### Step 4: Configure Environment Variables

#### For Local Database (Recommended)

1. Download the database:
```bash
cd backend
python utils/geolocation/download_maxmind_db.py
```

2. Set environment variables:
```bash
# Windows PowerShell
$env:MAXMIND_LICENSE_KEY="your_license_key_here"
$env:MAXMIND_DATABASE_PATH="backend/data/maxmind/GeoLite2-City.mmdb"

# Linux/Mac
export MAXMIND_LICENSE_KEY="your_license_key_here"
export MAXMIND_DATABASE_PATH="backend/data/maxmind/GeoLite2-City.mmdb"
```

3. Or add to `.env` file:
```env
MAXMIND_LICENSE_KEY=your_license_key_here
MAXMIND_DATABASE_PATH=backend/data/maxmind/GeoLite2-City.mmdb
```

#### For Web Service

Set environment variables:
```bash
# Windows PowerShell
$env:MAXMIND_ACCOUNT_ID="your_account_id_here"
$env:MAXMIND_LICENSE_KEY="your_license_key_here"

# Linux/Mac
export MAXMIND_ACCOUNT_ID="your_account_id_here"
export MAXMIND_LICENSE_KEY="your_license_key_here"
```

Or add to `.env` file:
```env
MAXMIND_ACCOUNT_ID=your_account_id_here
MAXMIND_LICENSE_KEY=your_license_key_here
```

### Step 5: Test the Integration

```bash
cd backend
python test_dns_geolocation.py
```

Expected output with MaxMind:
```
Scanning sbtet.telangana.gov.in...
  IP: 103.122.128.225
  Country: IN
  City: Hyderabad  # More accurate!
  Region: Telangana
  ISP: AS136659 Itec Department, Government Of Telangana
  Confidence: 85%
  Source: ['maxmind']
  Note: MaxMind GeoLite2 (±200km)
  Accuracy Radius: ±200km
```

## Database Updates

### Manual Update

```bash
cd backend
python utils/geolocation/download_maxmind_db.py
```

### Automated Update (Recommended)

Create a scheduled task/cron job to update the database weekly:

**Windows Task Scheduler:**
```powershell
# Create weekly task
schtasks /create /tn "Update MaxMind DB" /tr "python backend/utils/geolocation/download_maxmind_db.py" /sc weekly /d SUN
```

**Linux Cron:**
```bash
# Add to crontab
0 3 * * 0 cd /path/to/netra/backend && python utils/geolocation/download_maxmind_db.py
```

## Integration Details

### How It Works

1. **Primary Provider**: MaxMind (if configured)
2. **Fallback Providers**: ipinfo.io, freeipapi.com (if MaxMind fails)
3. **Confidence Calculation**: Based on accuracy radius for MaxMind, provider count for fallback

### Accuracy Radius Interpretation

- **≤50km**: 95% confidence (very accurate)
- **≤200km**: 85% confidence (good accuracy)
- **≤500km**: 70% confidence (moderate accuracy)
- **>500km**: 50% confidence (low accuracy)

### Data Fields Provided by MaxMind

- Country and country code
- City and region
- Latitude and longitude
- Accuracy radius
- ASN and organization
- Timezone
- Network information

## Troubleshooting

### Issue: "No MaxMind license key available"

**Solution**: Set the `MAXMIND_LICENSE_KEY` environment variable

### Issue: "Failed to load database"

**Solution**: 
1. Check database path is correct
2. Download database using the download script
3. Ensure file permissions are correct

### Issue: "MaxMind web service lookup failed"

**Solution**:
1. Verify account ID and license key
2. Check you haven't exceeded 1000 lookups/day limit
3. Ensure network connectivity to geolite.info

### Issue: System still using fallback providers

**Solution**:
1. Check environment variables are set
2. Restart the application after setting variables
3. Check logs for MaxMind initialization errors

## Performance Comparison

| Metric | Without MaxMind | With MaxMind Database | With MaxMind Web Service |
|--------|----------------|----------------------|-------------------------|
| Lookup Speed | ~1.5s | ~0.01s | ~0.5s |
| Daily Limit | None | None | 1000 |
| Accuracy | Good | Excellent | Excellent |
| Setup Complexity | None | Medium | Low |
| Maintenance | None | Weekly updates | None |

## Cost Comparison

| Service | Cost | Lookups | Accuracy |
|---------|------|---------|----------|
| Current Fallback | Free | Unlimited | Good |
| MaxMind GeoLite2 (Database) | Free | Unlimited | Excellent |
| MaxMind GeoLite2 (Web Service) | Free | 1000/day | Excellent |
| MaxMind GeoIP2 (Paid) | $50-200/month | Unlimited | Best |

## Recommendations

1. **For Development/Testing**: Use MaxMind web service (easiest setup)
2. **For Production**: Use MaxMind local database (best performance)
3. **For High Volume**: Consider paid MaxMind GeoIP2 (best accuracy + unlimited)

## Expected Improvements

### Before MaxMind
- Telangana government IP: Mumbai, Maharashtra
- Confidence: 100% (based on provider count)
- No accuracy radius information

### After MaxMind
- Telangana government IP: Hyderabad, Telangana (more accurate)
- Confidence: 85% (based on accuracy radius)
- Accuracy radius: ±200km (precision information)

## Support

- MaxMind Documentation: https://dev.maxmind.com/geoip/
- GeoIP2 Python API: https://github.com/maxmind/GeoIP2-python
- MaxMind Support: https://support.maxmind.com/

## License and Attribution

MaxMind GeoLite2 data is free but requires attribution:
- "This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com"

The system automatically includes this attribution in the accuracy notes when using MaxMind.
