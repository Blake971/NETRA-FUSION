# NETRA
# Database Specification

Version: 2.0

---

# 1. Database Overview

**Database Type**: SQLite (current)

**Future**: PostgreSQL for production scaling

**ORM**: SQLAlchemy (Python)

**Location**: backend/database/netra.db

---

# 2. Tables

## 2.1 Scans Table

**Purpose**: Store all domain scan results

**Table Name**: scans

### Columns

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | UUID of the scan |
| domain | TEXT | NOT NULL, INDEX | Domain that was scanned |
| status | TEXT | NOT NULL | Status: pending, in_progress, completed, failed |
| risk_score | INTEGER | NULL | Risk score (0-100) |
| risk_level | TEXT | NULL | Risk level: low, medium, high, critical |
| execution_time | REAL | NULL | Total execution time in seconds |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Scan creation timestamp |
| completed_at | TIMESTAMP | NULL | Scan completion timestamp |
| whois_json | JSON | NULL | WHOIS module results |
| dns_json | JSON | NULL | DNS module results |
| ssl_json | JSON | NULL | SSL module results |
| headers_json | JSON | NULL | Headers module results |
| ctlogs_json | JSON | NULL | Certificate Transparency results |
| ip_json | JSON | NULL | IP Intelligence results |
| email_json | JSON | NULL | Email Security results |
| ai_summary | JSON | NULL | AI-generated summary |
| report_path | TEXT | NULL | Path to generated PDF report |

### Indexes

- idx_domain: domain
- idx_created_at: created_at
- idx_status: status
- idx_risk_level: risk_level

### Relationships

- One-to-many with reports (if separate reports table needed)

---

## 2.2 Reports Table

**Purpose**: Store generated PDF report metadata

**Table Name**: reports

### Columns

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | UUID of the report |
| scan_id | TEXT | NOT NULL, FOREIGN KEY | Reference to scans.id |
| file_path | TEXT | NOT NULL | Path to PDF file |
| file_size | INTEGER | NULL | File size in bytes |
| generated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Report generation timestamp |
| options | JSON | NULL | Report generation options |

### Indexes

- idx_scan_id: scan_id
- idx_generated_at: generated_at

### Relationships

- Many-to-one with scans (scan_id references scans.id)

---

## 2.3 Users Table (Future)

**Purpose**: Store user accounts for authentication

**Table Name**: users

### Columns

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | UUID of the user |
| email | TEXT | NOT NULL, UNIQUE, INDEX | User email |
| password_hash | TEXT | NOT NULL | Hashed password |
| name | TEXT | NULL | User display name |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| last_login | TIMESTAMP | NULL | Last login timestamp |
| settings | JSON | NULL | User settings |

### Indexes

- idx_email: email

### Relationships

- One-to-many with scans (if user-specific scans needed)

---

## 2.4 Settings Table

**Purpose**: Store application-wide settings

**Table Name**: settings

### Columns

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| key | TEXT | PRIMARY KEY | Setting key |
| value | TEXT | NOT NULL | Setting value |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

### Default Settings

| Key | Value | Description |
|-----|-------|-------------|
| max_scans_per_day | 100 | Maximum scans per day per user |
| retention_days | 30 | Days to retain scan data |
| enable_ai | true | Enable AI summarization |
| enable_reports | true | Enable PDF report generation |

---

# 3. Schema Diagram

```
scans (id, domain, status, risk_score, risk_level, ...)
    ↓
    ├── reports (id, scan_id, file_path, ...)
    └── users (id, email, ...) [future]

settings (key, value, ...)
```

---

# 4. SQL Schema

## 4.1 Scans Table

```sql
CREATE TABLE scans (
    id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'in_progress', 'completed', 'failed')),
    risk_score INTEGER NULL CHECK(risk_score >= 0 AND risk_score <= 100),
    risk_level TEXT NULL CHECK(risk_level IN ('low', 'medium', 'high', 'critical')),
    execution_time REAL NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    whois_json JSON NULL,
    dns_json JSON NULL,
    ssl_json JSON NULL,
    headers_json JSON NULL,
    ctlogs_json JSON NULL,
    ip_json JSON NULL,
    email_json JSON NULL,
    ai_summary JSON NULL,
    report_path TEXT NULL
);

CREATE INDEX idx_scans_domain ON scans(domain);
CREATE INDEX idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scans_risk_level ON scans(risk_level);
```

## 4.2 Reports Table

```sql
CREATE TABLE reports (
    id TEXT PRIMARY KEY,
    scan_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    options JSON NULL,
    FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
);

CREATE INDEX idx_reports_scan_id ON reports(scan_id);
CREATE INDEX idx_reports_generated_at ON reports(generated_at DESC);
```

## 4.3 Users Table (Future)

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    settings JSON NULL
);

CREATE INDEX idx_users_email ON users(email);
```

## 4.4 Settings Table

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

# 5. Database Operations

## 5.1 Insert Scan

```python
def create_scan(scan_id: str, domain: str) -> Scan:
    scan = Scan(
        id=scan_id,
        domain=domain,
        status="pending"
    )
    db.add(scan)
    db.commit()
    return scan
```

## 5.2 Update Scan Status

```python
def update_scan_status(scan_id: str, status: str) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.status = status
        if status == "completed":
            scan.completed_at = datetime.utcnow()
        db.commit()
    return scan
```

## 5.3 Update Scan Results

```python
def update_scan_results(scan_id: str, module: str, data: dict) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        if module == "whois":
            scan.whois_json = data
        elif module == "dns":
            scan.dns_json = data
        elif module == "ssl":
            scan.ssl_json = data
        # ... other modules
        db.commit()
    return scan
```

## 5.4 Get Scan by ID

```python
def get_scan(scan_id: str) -> Scan:
    return db.query(Scan).filter(Scan.id == scan_id).first()
```

## 5.5 Get Scan History

```python
def get_scan_history(limit: int = 20, offset: int = 0) -> List[Scan]:
    return db.query(Scan)\
        .filter(Scan.status == "completed")\
        .order_by(Scan.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
```

## 5.6 Get Statistics

```python
def get_statistics() -> dict:
    total_scans = db.query(Scan).filter(Scan.status == "completed").count()
    high_risk = db.query(Scan).filter(Scan.risk_level == "high").count()
    medium_risk = db.query(Scan).filter(Scan.risk_level == "medium").count()
    low_risk = db.query(Scan).filter(Scan.risk_level == "low").count()
    
    avg_score = db.query(func.avg(Scan.risk_score))\
        .filter(Scan.status == "completed")\
        .scalar()
    
    return {
        "total_scans": total_scans,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "average_risk_score": avg_score or 0
    }
```

## 5.7 Delete Scan

```python
def delete_scan(scan_id: str) -> bool:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        db.delete(scan)
        db.commit()
        return True
    return False
```

---

# 6. Data Retention

## 6.1 Retention Policy

- Scans: Retain for 30 days
- Reports: Retain for 30 days
- Users: Retain indefinitely (future)

## 6.2 Cleanup Job

```python
def cleanup_old_scans():
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    old_scans = db.query(Scan)\
        .filter(Scan.created_at < cutoff_date)\
        .all()
    
    for scan in old_scans:
        # Delete report file if exists
        if scan.report_path:
            try:
                os.remove(scan.report_path)
            except FileNotFoundError:
                pass
        db.delete(scan)
    
    db.commit()
```

---

# 7. Backup Strategy

## 7.1 Backup Frequency

- Development: Manual backup before major changes
- Production: Daily automated backups

## 7.2 Backup Command

```bash
# SQLite backup
cp backend/database/netra.db backend/database/netra_backup_$(date +%Y%m%d).db
```

## 7.3 Restore Command

```bash
cp backend/database/netra_backup_20240115.db backend/database/netra.db
```

---

# 8. Migration Strategy

## 8.1 Current to PostgreSQL Migration

When migrating to PostgreSQL:

1. Export SQLite data
2. Create PostgreSQL schema
3. Import data
4. Update connection string
5. Test all operations

## 8.2 Migration Script

```python
def migrate_to_postgresql():
    # Export from SQLite
    sqlite_engine = create_engine('sqlite:///netra.db')
    postgres_engine = create_engine('postgresql://user:pass@localhost/netra')
    
    # Copy data
    for table in ['scans', 'reports', 'settings']:
        df = pd.read_sql(f'SELECT * FROM {table}', sqlite_engine)
        df.to_sql(table, postgres_engine, if_exists='append', index=False)
```

---

# 9. Performance Optimization

## 9.1 Query Optimization

- Use indexes on frequently queried columns
- Limit result sets with pagination
- Use specific column selection instead of SELECT *

## 9.2 Connection Pooling

Future: Implement connection pooling for PostgreSQL

```python
engine = create_engine(
    'postgresql://user:pass@localhost/netra',
    pool_size=10,
    max_overflow=20
)
```

---

# 10. Security

## 10.1 SQL Injection Prevention

- Use parameterized queries (ORM handles this)
- Never concatenate user input into SQL queries

## 10.2 Data Encryption

Future: Encrypt sensitive fields at rest

- Password hashes (already implemented with bcrypt)
- API keys (future)

## 10.3 Access Control

Future: Implement row-level security

- Users can only access their own scans
- Admin users can access all scans

---

# 11. Testing

## 11.1 Test Database

Use separate test database: `netra_test.db`

## 11.2 Test Setup

```python
@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///netra_test.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    os.remove('netra_test.db')
```

---

END OF DATABASE SPECIFICATION
