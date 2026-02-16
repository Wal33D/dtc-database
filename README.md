# DTC Database

Comprehensive OBD-II Diagnostic Trouble Code database with generic SAE J2012 coverage plus manufacturer-specific definitions.

**License:** MIT

## Overview

This repository ships a local SQLite database (`data/dtc_codes.db`) and language wrappers for Python, Java, Android, and TypeScript.

It is designed for offline diagnostics workflows where you need:

- Fast code lookups (`P/B/C/U`)
- Manufacturer context where available
- Simple embedding into apps/services without remote API calls

## Current Dataset Snapshot

Values below are from `data/dtc_codes.db` (`locale='en'`):

| Category | Count |
|----------|-------|
| Total code definitions (rows) | 18,805 |
| Unique DTC codes | 12,128 |
| Generic OBD-II definitions | 9,415 |
| Manufacturer-specific definitions | 9,390 |
| Manufacturers (excluding `GENERIC`) | 33 |
| Powertrain (`P`) | 14,821 |
| Body (`B`) | 1,465 |
| Chassis (`C`) | 985 |
| Network (`U`) | 1,534 |

## Sister Projects

Part of the same automotive tooling set:

- [nhtsa-vin-decoder](https://github.com/Wal33D/nhtsa-vin-decoder)
- [nhtsa-recall-lookup](https://github.com/Wal33D/nhtsa-recall-lookup)
- [dtc-database](https://github.com/Wal33D/dtc-database)

Cross-project examples are in [INTEGRATION.md](INTEGRATION.md).

## Quick Start

### Python

```python
from python.dtc_database import DTCDatabase

db = DTCDatabase()

dtc = db.get_dtc("P0420")
print(dtc.code, dtc.type_name, dtc.description)

ford_specific = db.get_dtc("P1690", "FORD")
print(ford_specific)
```

### Java Core

```java
import com.dtcdatabase.DTCDatabaseCore;
import java.util.List;

DTCDatabaseCore db = new DTCDatabaseCore("data/dtc_codes.db");

DTCDatabaseCore.DTC dtc = db.getDTC("P0420");
System.out.println(dtc.code + ": " + dtc.description);

List<DTCDatabaseCore.DTC> results = db.search("misfire", 25);
db.close();
```

### Android

```java
import com.dtcdatabase.DTCDatabase;

DTCDatabase db = DTCDatabase.getInstance(context);
String description = db.getDescription("P0420");
```

### TypeScript (Repository Source)

```bash
git clone https://github.com/Wal33D/dtc-database.git
cd dtc-database/typescript
npm install
npm run build
npm test
```

```ts
import { DTCDatabase } from "./dist";

const db = new DTCDatabase();
console.log(db.getDescription("P0171"));
db.close();
```

## Installation Notes

### Python

No external runtime dependencies. Uses standard-library `sqlite3`.

### Java

Requires SQLite JDBC in your application:

```xml
<dependency>
  <groupId>org.xerial</groupId>
  <artifactId>sqlite-jdbc</artifactId>
  <version>3.45.3.0</version>
</dependency>
```

### Android

Use the library module under `android/dtc-database-android/`.  
`dtc_codes.db` is included in module assets.

### TypeScript Package Status

`@wal33d/dtc-database` metadata exists in `typescript/package.json`, but the package is currently maintained as repository source (not a published npm release at this time).

## Directory Structure

```text
dtc-database/
├── data/
│   ├── dtc_codes.db                  # SQLite database (~3.1 MB)
│   └── source-data/                  # 37 source text files
├── python/
│   └── dtc_database.py               # Python wrapper
├── java/
│   ├── DTCDatabaseCore.java          # JVM core wrapper
│   └── DTCDatabaseAndroid.java       # Legacy Android wrapper (kept for reference)
├── android/
│   └── dtc-database-android/         # Android library module
├── typescript/
│   ├── src/                          # TypeScript source
│   └── tests/                        # Jest tests
├── docs/
│   ├── API.md
│   ├── INSTALLATION.md
│   ├── RELEASE_NOTES.md
│   └── USAGE.md
├── build_database.py
├── test.py
└── test_schema.py
```

## Documentation

- [API Reference](docs/API.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Usage Guide](docs/USAGE.md)
- [Release Notes](docs/RELEASE_NOTES.md)

## Contributing

1. Add/modify entries in `data/source-data/*.txt` (`CODE - Description` format)
2. Rebuild database with `python3 build_database.py`
3. Run validation:
   - `python3 test.py`
   - `python3 test_schema.py`
   - `cd typescript && npm test`
4. Submit a pull request

## Support

- Issues: https://github.com/Wal33D/dtc-database/issues

