# Installation Guide

## Requirements

### Python Version
- Python 3.6 or higher
- No external dependencies (uses SQLite3 from standard library)

### Java Version
- Java 8 or higher
- SQLite JDBC driver (included in java/lib/)

### Database
- SQLite database file (included in data/dtc_codes.db)
- Size: ~2.7 MB
- Contains 18,805+ diagnostic trouble codes

## Installation Methods

### Method 1: Direct Download

Clone the repository from GitHub:

```bash
git clone https://github.com/Wal33D/dtc-database.git
cd dtc-database
```

### Method 2: Manual Installation

Download and copy the required files to your project:

```bash
# For Python projects
cp -r dtc-database/python/dtc_database.py /path/to/your/project/
cp -r dtc-database/data/dtc_codes.db /path/to/your/project/data/

# For Java projects
cp -r dtc-database/java/*.java /path/to/your/project/
cp -r dtc-database/data/dtc_codes.db /path/to/your/project/data/
```

## Project Structure

```
dtc-database/
├── data/
│   ├── dtc_codes.db        # SQLite database (2.7 MB)
│   ├── lib/                # Data processing libraries
│   └── source-data/        # Original data sources
├── python/
│   └── dtc_database.py     # Python implementation
├── java/
│   ├── DTCDatabase.java    # Java implementation
│   └── DTC.java           # DTC model class
├── docs/
│   ├── API.md             # API documentation
│   ├── INSTALLATION.md    # This file
│   └── USAGE.md           # Usage examples
├── test.py                # Python test script
├── build_database.py      # Database builder script
└── README.md              # Project overview
```

## Python Installation

### Basic Setup

```python
# Add to your Python path
import sys
sys.path.append('/path/to/dtc-database/python')

from dtc_database import DTCDatabase
```

### Package Installation

Create a simple setup for your project:

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name='your-project',
    packages=find_packages(),
    package_data={
        'your_package': ['data/dtc_codes.db']
    },
    install_requires=[]  # No external dependencies
)
```

### Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Copy database files
cp -r dtc-database/python/* your_project/
cp -r dtc-database/data your_project/
```

## Java Installation

### Maven Configuration

Add to your `pom.xml`:

```xml
<dependencies>
    <!-- SQLite JDBC -->
    <dependency>
        <groupId>org.xerial</groupId>
        <artifactId>sqlite-jdbc</artifactId>
        <version>3.36.0.3</version>
    </dependency>
</dependencies>
```

### Gradle Configuration

Add to your `build.gradle`:

```gradle
dependencies {
    implementation 'org.xerial:sqlite-jdbc:3.36.0.3'
}
```

### Manual JAR Installation

```bash
# Copy SQLite JDBC driver
cp dtc-database/java/lib/sqlite-jdbc-*.jar /path/to/your/libs/

# Add to classpath
java -cp ".:libs/*" YourMainClass
```

## Android Installation

### For Android Projects

1. Copy database to assets:
```bash
cp dtc-database/data/dtc_codes.db app/src/main/assets/
```

2. Add to `build.gradle`:
```gradle
dependencies {
    implementation 'io.github.requery:sqlite-android:3.36.0'
}
```

3. Copy database from assets on first run:
```java
private void copyDatabase() {
    String DB_PATH = context.getDatabasePath("dtc_codes.db").getPath();
    if (!new File(DB_PATH).exists()) {
        try (InputStream input = context.getAssets().open("dtc_codes.db");
             OutputStream output = new FileOutputStream(DB_PATH)) {
            byte[] buffer = new byte[1024];
            int length;
            while ((length = input.read(buffer)) > 0) {
                output.write(buffer, 0, length);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

## Verification

### Python Verification

Run this script to verify installation:

```python
#!/usr/bin/env python3
"""Verify DTC database installation"""

import os
import sys

def verify_installation():
    print("Checking DTC Database installation...")

    # Check Python module
    try:
        from dtc_database import DTCDatabase
        print("✓ Python module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import module: {e}")
        return False

    # Check database file
    db_path = 'data/dtc_codes.db'
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / (1024 * 1024)
        print(f"✓ Database found ({size:.2f} MB)")
    else:
        print(f"✗ Database not found at {db_path}")
        return False

    # Test database connection
    try:
        db = DTCDatabase(db_path)
        dtc = db.get_dtc('P0171')
        if dtc:
            print(f"✓ Database working: {dtc.code} - {dtc.description[:50]}...")
        db.close()
        print("✓ Connection test successful")
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

    print("\n✓ Installation verified successfully!")
    return True

if __name__ == "__main__":
    sys.exit(0 if verify_installation() else 1)
```

### Java Verification

```java
public class VerifyInstallation {
    public static void main(String[] args) {
        System.out.println("Checking DTC Database installation...");

        try {
            // Test database connection
            DTCDatabase db = new DTCDatabase("data/dtc_codes.db");

            // Test code lookup
            DTC dtc = db.getDTC("P0171");
            if (dtc != null) {
                System.out.println("✓ Database working: " + dtc.getCode() +
                                 " - " + dtc.getDescription());
            }

            // Test statistics
            Map<String, Integer> stats = db.getStatistics();
            System.out.println("✓ Total codes: " + stats.get("total"));

            db.close();
            System.out.println("\n✓ Installation verified successfully!");

        } catch (Exception e) {
            System.err.println("✗ Installation error: " + e.getMessage());
            System.exit(1);
        }
    }
}
```

## Configuration

### Custom Database Location

Python:
```python
# Use custom path
db = DTCDatabase('/custom/path/to/dtc_codes.db')

# Use environment variable
import os
db_path = os.environ.get('DTC_DB_PATH', 'data/dtc_codes.db')
db = DTCDatabase(db_path)
```

Java:
```java
// Custom path
DTCDatabase db = new DTCDatabase("/custom/path/to/dtc_codes.db");

// Environment variable
String dbPath = System.getenv("DTC_DB_PATH");
if (dbPath == null) {
    dbPath = "data/dtc_codes.db";
}
DTCDatabase db = new DTCDatabase(dbPath);
```

## Troubleshooting

### Common Issues

#### Database File Not Found

**Error:** `FileNotFoundError: data/dtc_codes.db`

**Solution:**
```python
import os

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Use absolute path
db_path = os.path.abspath('data/dtc_codes.db')
db = DTCDatabase(db_path)
```

#### SQLite Version Issues

**Error:** `sqlite3.OperationalError: no such function`

**Solution:**
Ensure SQLite version is 3.7.0 or higher:
```python
import sqlite3
print(f"SQLite version: {sqlite3.sqlite_version}")
```

#### Permission Denied

**Error:** `PermissionError: Permission denied`

**Solution:**
```bash
# Fix file permissions
chmod 644 data/dtc_codes.db

# Fix directory permissions
chmod 755 data/
```

#### Module Import Error

**Error:** `ModuleNotFoundError: No module named 'dtc_database'`

**Solution:**
```python
# Add parent directory to path
import sys
import os
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

from dtc_database import DTCDatabase
```

### Performance Optimization

#### Enable WAL Mode

For better concurrent access:

```python
import sqlite3

conn = sqlite3.connect('data/dtc_codes.db')
conn.execute('PRAGMA journal_mode=WAL')
conn.close()
```

#### Connection Pooling

For high-traffic applications:

```python
from queue import Queue
import sqlite3

class ConnectionPool:
    def __init__(self, db_path, pool_size=5):
        self.db_path = db_path
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            self.pool.put(conn)

    def get_connection(self):
        return self.pool.get()

    def return_connection(self, conn):
        self.pool.put(conn)
```

## Platform-Specific Notes

### Windows

- Use forward slashes or raw strings for paths:
  ```python
  db = DTCDatabase(r'C:\Users\Name\dtc-database\data\dtc_codes.db')
  # or
  db = DTCDatabase('C:/Users/Name/dtc-database/data/dtc_codes.db')
  ```

### Linux/Unix

- Ensure proper file permissions:
  ```bash
  chmod 644 data/dtc_codes.db
  ```

### macOS

- If using system Python, you may need to use pip3:
  ```bash
  pip3 install --user sqlite3
  ```

## Docker Installation

### Dockerfile Example

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy database and code
COPY data/dtc_codes.db data/
COPY python/dtc_database.py .

# Your application
COPY app.py .

CMD ["python", "app.py"]
```

### Docker Compose

```yaml
version: '3'
services:
  dtc-app:
    build: .
    volumes:
      - ./data:/app/data:ro
    environment:
      - DTC_DB_PATH=/app/data/dtc_codes.db
```

## Support

For installation issues or questions:

- **GitHub Issues**: https://github.com/Wal33D/dtc-database/issues
- **Author**: Waleed Judah (Wal33D)
- **Email**: aquataze@yahoo.com