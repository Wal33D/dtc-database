# DTC Database - 18,821 OBD-II Diagnostic Trouble Codes

**The most comprehensive open-source OBD-II DTC database**

Author: Wal33D
Email: aquataze@yahoo.com

## Features

- **18,821 diagnostic trouble codes** with descriptions
- All 4 code types: P (Powertrain), B (Body), C (Chassis), U (Network)
- **32 manufacturer-specific** code sets (Mercedes, BMW, Ford, Audi, etc.)
- Multi-platform support: Android, Java, Python, TypeScript
- SQLite database with efficient caching
- Batch lookup and search capabilities

## Quick Start

### Python
```python
from dtc_database import DTCDatabase

db = DTCDatabase()
print(db.get_description('P0171'))  # "System Too Lean Bank 1"
```

### Java/Android
```java
DTCDatabase db = DTCDatabase.getInstance(context);
String desc = db.getDescription("P0171");
```

### TypeScript
```bash
npm run code P0171
```

## Directory Structure

```
dtc-database/
├── android/               # Android-specific implementation
│   └── DTCDatabase.java
├── java/                  # Platform-independent Java
│   └── DTCDatabaseCore.java
├── python/                # Python library
│   └── dtc_database.py
├── source-data/           # Raw text files (18,821 codes)
│   ├── p_codes.txt        # Powertrain codes (7,388)
│   ├── b_codes.txt        # Body codes (299)
│   ├── c_codes.txt        # Chassis codes (497)
│   ├── u_codes.txt        # Network codes (1,229)
│   └── [manufacturer]_codes.txt  # 32 manufacturer files
├── query-code.ts          # TypeScript single lookup
├── query-interactive.ts   # TypeScript interactive tool
└── tsconfig.json
```

## Database Statistics

| Category | Count |
|----------|-------|
| **Total Codes** | 18,821 |
| Powertrain (P) | 7,388 |
| Body (B) | 299 |
| Chassis (C) | 497 |
| Network (U) | 1,229 |
| Manufacturer-Specific | 9,408 |

### Manufacturer Coverage

32 manufacturers including:
- Acura, Audi, BMW, Buick
- Cadillac, Chevrolet, Chrysler, Dodge
- Ford, GM, GMC, Honda
- Infiniti, Jaguar, Jeep, Kia
- Lexus, Lincoln, Mazda, Mercedes
- Mercury, Mitsubishi, Nissan, Oldsmobile
- Plymouth, Pontiac, Saturn, Subaru
- Suzuki, Toyota, Volkswagen, and more

## Installation

### As Git Submodule
```bash
git submodule add https://github.com/Wal33D/dtc-database.git
git submodule update --init --recursive
```

### Direct Clone
```bash
git clone https://github.com/Wal33D/dtc-database.git
```

## Usage Examples

### Python
```python
from dtc_database import DTCDatabase

# Initialize
db = DTCDatabase()

# Single lookup
desc = db.get_description('P0420')
print(desc)  # "Catalyst System Efficiency Below Threshold Bank 1"

# Search
results = db.search('oxygen sensor')
for dtc in results[:5]:
    print(f"{dtc.code}: {dtc.description}")

# Get by type
powertrain_codes = db.get_by_type('P', limit=10)

# Manufacturer-specific
mercedes_codes = db.get_manufacturer_codes('mercedes')
```

### Java/Android
```java
// Initialize
DTCDatabase db = DTCDatabase.getInstance(context);

// Single lookup
String desc = db.getDescription("P0171");

// Batch lookup
List<String> codes = Arrays.asList("P0171", "P0420", "P0300");
Map<String, String> descriptions = db.getDescriptions(codes);

// Search
List<DTC> results = db.searchByKeyword("misfire");

// Get by type
List<DTC> bodyCodes = db.getCodesByType('B');
```

## Database Schema

```sql
CREATE TABLE dtc_codes (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    type TEXT,              -- P/B/C/U
    manufacturer TEXT       -- NULL for generic
);
```

## File Format

All source files use this format:
```
P0001 - Fuel Volume Regulator A Control Circuit/Open
P0002 - Fuel Volume Regulator A Control Circuit Performance
```

## Building from Source

### TypeScript
```bash
npm install
npx ts-node build-database.ts
```

### Python
```python
python3 python/dtc_database.py  # Creates SQLite database
```

## Code Types

- **P codes**: Powertrain (engine, transmission)
- **B codes**: Body (airbags, seatbelts, climate control)
- **C codes**: Chassis (ABS, steering, suspension)
- **U codes**: Network (CAN bus, communication modules)

## Contributing

1. Add new codes to appropriate text file in `source-data/`
2. Follow format: `CODE - Description`
3. Submit pull request

## License

MIT License - Free for commercial and non-commercial use

## Acknowledgments

Database compiled from various public sources and manufacturer documentation.

## Contact

Wal33D - aquataze@yahoo.com

For OBD-Droid integration, visit: https://github.com/Wal33D/OBD-Droid