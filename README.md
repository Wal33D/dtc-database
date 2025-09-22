# DTC Database

OBD-II Diagnostic Trouble Code Database with manufacturer-specific definitions

**Author**: Wal33D
**Email**: aquataze@yahoo.com

## Features

- **18,805+ diagnostic trouble codes** with descriptions
- All 4 code types: P (Powertrain), B (Body), C (Chassis), U (Network)
- **34 manufacturer-specific** code sets (Mercedes, BMW, Ford, Audi, etc.)
- Multi-platform support: Java/Android, Python
- SQLite database with efficient caching
- Manufacturer-specific definitions with generic fallback

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


## Directory Structure

```
dtc-database/
├── data/                  # Data files
│   ├── dtc_codes.db      # SQLite database (2.6MB)
│   ├── source-data/      # Raw text files (18,805+ codes)
│   │   ├── p_codes.txt   # Generic powertrain codes
│   │   ├── b_codes.txt   # Generic body codes
│   │   ├── c_codes.txt   # Generic chassis codes
│   │   ├── u_codes.txt   # Generic network codes
│   │   └── [manufacturer]_codes.txt  # 34 manufacturer files
│   └── lib/              # Java dependencies
├── java/                 # Java/Android implementation
│   ├── DTCDatabaseCore.java
│   └── DTCDatabaseAndroid.java
├── python/               # Python implementation
│   └── dtc_database.py
├── docs/                 # Documentation
└── build_database.py     # Database builder script
```

## Database Statistics

| Category | Count |
|----------|-------|
| **Total Entries** | 18,805 |
| **Unique Codes** | 12,128 |
| **Manufacturers** | 34 |
| Generic Codes | ~3,500 |
| Manufacturer-Specific | ~15,000+ |

### Manufacturer Coverage

34 manufacturers including:
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
CREATE TABLE dtc_definitions (
    code TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    description TEXT NOT NULL,
    is_generic BOOLEAN DEFAULT 0,
    source_file TEXT,
    PRIMARY KEY (code, manufacturer)
);
```

## File Format

All source files use this format:
```
P0001 - Fuel Volume Regulator A Control Circuit/Open
P0002 - Fuel Volume Regulator A Control Circuit Performance
```

## Building from Source

### Python
```bash
python3 build_database.py  # Rebuilds SQLite database from source files
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

## Contact

Wal33D - aquataze@yahoo.com

