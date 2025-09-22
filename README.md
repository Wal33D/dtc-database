# DTC Database

Comprehensive OBD-II Diagnostic Trouble Code Database with 28,220+ codes including manufacturer-specific definitions.

**Author**: Wal33D
**Email**: aquataze@yahoo.com
**License**: MIT

## Overview

The most complete open-source diagnostic trouble code database for OBD-II applications. Features both generic SAE J2012 standard codes and manufacturer-specific definitions for accurate vehicle diagnostics.

## Features

- **28,220 diagnostic trouble codes** in SQLite database
- **9,415 generic OBD-II codes** (SAE J2012 standard)
- **18,805 manufacturer-specific codes** for 33+ brands
- All 4 code types: P (Powertrain), B (Body), C (Chassis), U (Network)
- Python and Java implementations
- Zero external dependencies (Python uses standard library)
- Built-in caching for performance
- Full-text search capability
- Thread-safe database operations

## Quick Start

### Python
```python
from python.dtc_database import DTCDatabase

# Initialize database
db = DTCDatabase()

# Look up a code
dtc = db.get_dtc('P0420')
print(f"{dtc.code}: {dtc.description}")
# Output: P0420: Catalyst System Efficiency Below Threshold Bank 1

# Search for codes
results = db.search('oxygen sensor')
for dtc in results[:3]:
    print(f"{dtc.code}: {dtc.description}")
```

### Java/Android
```java
DTCDatabase db = new DTCDatabase("data/dtc_codes.db");

// Look up a code
DTC dtc = db.getDTC("P0420");
System.out.println(dtc.getCode() + ": " + dtc.getDescription());

// Search for codes
List<DTC> results = db.search("misfire");
```


## Installation

```bash
# Clone the repository
git clone https://github.com/Wal33D/dtc-database.git
cd dtc-database

# For Python projects
from python.dtc_database import DTCDatabase

# For Java projects - add SQLite JDBC dependency
# Maven: org.xerial:sqlite-jdbc:3.36.0.3
```

No external dependencies required for Python (uses standard library).

## Directory Structure

```
dtc-database/
├── data/
│   ├── dtc_codes.db         # SQLite database (2.7 MB)
│   ├── lib/                 # Data processing libraries
│   └── source-data/         # Original data sources (38 files)
├── python/
│   └── dtc_database.py      # Python implementation
├── java/
│   ├── DTCDatabase.java     # Java implementation
│   └── DTC.java            # DTC model class
├── docs/
│   ├── API.md              # Complete API reference
│   ├── INSTALLATION.md     # Setup guide
│   └── USAGE.md            # Usage examples
├── build_database.py        # Database builder
├── test.py                  # Test suite
└── README.md               # This file
```

## Database Statistics

| Category | Count |
|----------|-------|
| **Total Codes** | 28,220 |
| **Generic OBD-II** | 9,415 |
| **Manufacturer-Specific** | 18,805 |
| **Manufacturers** | 33 |
| **Powertrain (P)** | 7,387 |
| **Body (B)** | 300 |
| **Chassis (C)** | 498 |
| **Network (U)** | 1,230 |

### Manufacturer Coverage

33 manufacturers with dedicated code sets:

**American:** Ford, GM, Chevrolet, Buick, Cadillac, GMC, Saturn, Oldsmobile, Pontiac, Chrysler, Dodge, Plymouth, Jeep, Lincoln, Mercury

**European:** Volkswagen, BMW, Mercedes-Benz, Audi, Jaguar, Porsche (via OTHER)

**Japanese:** Toyota, Honda, Nissan, Mazda, Mitsubishi, Subaru, Suzuki, Acura, Lexus, Infiniti

**Korean:** Kia, Hyundai (via OTHER)


## Key Features

### Code Lookup
```python
# Get full DTC information
dtc = db.get_dtc('P0171')
print(f"Code: {dtc.code}")
print(f"Description: {dtc.description}")
print(f"Type: {dtc.type_name}")  # "Powertrain"
```

### Search Functionality
```python
# Search by keyword
results = db.search('misfire')
for dtc in results:
    print(f"{dtc.code}: {dtc.description}")
```

### Manufacturer-Specific
```python
# Get manufacturer-specific codes
ford_codes = db.get_manufacturer_codes('FORD')
print(f"Ford has {len(ford_codes)} specific codes")
```

### Batch Operations
```python
# Look up multiple codes at once
codes = ['P0171', 'P0300', 'P0420', 'B0001']
batch_results = db.batch_lookup(codes)
```

## Documentation

Comprehensive documentation available in the [docs/](docs/) directory:

- [API Reference](docs/API.md) - Complete API documentation
- [Installation Guide](docs/INSTALLATION.md) - Setup and configuration
- [Usage Examples](docs/USAGE.md) - Real-world implementation examples

## Code Types Explained

| Type | System | Examples |
|------|--------|----------|
| **P** | Powertrain | Engine, transmission, emissions |
| **B** | Body | Airbags, climate control, locks |
| **C** | Chassis | ABS, traction control, steering |
| **U** | Network | Module communication, CAN bus |

## Use Cases

- **OBD-II Diagnostic Apps** - Interpret fault codes from vehicles
- **Service Centers** - Track repairs and common issues
- **Fleet Management** - Monitor vehicle health across fleets
- **Insurance** - Validate repair claims
- **Mobile Mechanics** - Quick field reference

## Why This Database?

- **Most Complete** - 28,220 codes vs typical 3,000-5,000 in other databases
- **Manufacturer Coverage** - Specific definitions for 33+ brands
- **Zero Dependencies** - Python version uses standard library only
- **Production Ready** - Used in commercial diagnostic applications
- **Open Source** - MIT licensed for any use

## Performance

- Database size: 2.7 MB
- Lookup time: <1ms with caching
- Search time: <50ms for full-text search
- Memory usage: ~10 MB typical
- Thread-safe for concurrent access

## Contributing

Contributions welcome! To add new codes:

1. Add to appropriate file in `data/source-data/`
2. Format: `CODE - Description`
3. Run `python3 build_database.py` to rebuild
4. Submit pull request

## Support

For issues, questions, or feature requests:

- **GitHub Issues**: https://github.com/Wal33D/dtc-database/issues
- **Author**: Waleed Judah (Wal33D)
- **Email**: aquataze@yahoo.com

## License

MIT License - Free for commercial and non-commercial use.

## Acknowledgments

- SAE International for J2012 standard
- Vehicle manufacturers for code definitions
- Open source community for contributions

