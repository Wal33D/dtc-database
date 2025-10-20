# API Reference

## Overview

The DTC Database provides a comprehensive SQLite database of OBD-II diagnostic trouble codes with Python and Java implementations.

## Python API

### DTCDatabase Class

The main interface for accessing diagnostic trouble codes.

#### Constructor

```python
db = DTCDatabase(db_path=None)
```

**Parameters:**
- `db_path` (str, optional): Path to the SQLite database file. If not provided, uses default location `data/dtc_codes.db`

**Example:**
```python
from dtc_database import DTCDatabase
db = DTCDatabase('data/dtc_codes.db')
```

### Methods

#### get_dtc(code)

Retrieves complete information for a diagnostic trouble code.

**Parameters:**
- `code` (str): The DTC code (e.g., 'P0171', 'B0001')

**Returns:**
- `DTC`: Object containing code information, or None if not found

**Example:**
```python
dtc = db.get_dtc('P0420')
if dtc:
    print(f"{dtc.code}: {dtc.description}")
    print(f"Type: {dtc.type_name}")  # Powertrain
```

#### get_description(code, manufacturer='GENERIC')

Gets the description for a specific code.

**Parameters:**
- `code` (str): The DTC code
- `manufacturer` (str, optional): Manufacturer name for specific codes

**Returns:**
- `str`: Code description, or None if not found

**Example:**
```python
# Generic code
desc = db.get_description('P0171')

# Manufacturer-specific
ford_desc = db.get_description('P1234', 'FORD')
```

#### search(query, limit=50)

Searches for codes containing the specified text in their description.

**Parameters:**
- `query` (str): Search text
- `limit` (int, optional): Maximum results to return (default: 50)

**Returns:**
- `List[DTC]`: List of matching DTC objects

**Example:**
```python
# Find all codes related to oxygen sensor
results = db.search('oxygen sensor')
for dtc in results:
    print(f"{dtc.code}: {dtc.description}")

# Find misfire codes
misfires = db.search('misfire', limit=20)
```

#### get_manufacturer_codes(manufacturer, limit=100)

Retrieves all codes specific to a manufacturer.

**Parameters:**
- `manufacturer` (str): Manufacturer name (e.g., 'FORD', 'BMW', 'TOYOTA')
- `limit` (int, optional): Maximum results (default: 100)

**Returns:**
- `List[DTC]`: List of manufacturer-specific codes

**Example:**
```python
ford_codes = db.get_manufacturer_codes('FORD')
print(f"Found {len(ford_codes)} Ford-specific codes")

bmw_codes = db.get_manufacturer_codes('BMW', limit=50)
```

#### batch_lookup(codes)

Retrieves multiple codes in a single operation.

**Parameters:**
- `codes` (List[str]): List of DTC codes to look up

**Returns:**
- `Dict[str, DTC]`: Dictionary mapping codes to DTC objects

**Example:**
```python
codes_to_check = ['P0171', 'P0300', 'P0420', 'B0001']
results = db.batch_lookup(codes_to_check)

for code, dtc in results.items():
    if dtc:
        print(f"{code}: {dtc.description}")
```

#### get_by_type(code_type, limit=100)

Gets all codes of a specific type.

**Parameters:**
- `code_type` (str): Code type ('P', 'B', 'C', or 'U')
- `limit` (int, optional): Maximum results (default: 100)

**Returns:**
- `List[DTC]`: List of codes of the specified type

**Example:**
```python
# Get powertrain codes
p_codes = db.get_by_type('P', limit=500)

# Get body codes
b_codes = db.get_by_type('B')

# Get chassis codes
c_codes = db.get_by_type('C')

# Get network codes
u_codes = db.get_by_type('U')
```

#### get_statistics()

Returns database statistics.

**Returns:**
- `Dict`: Statistics about the database contents

**Example:**
```python
stats = db.get_statistics()
print(f"Total codes: {stats['total']}")
print(f"Generic codes: {stats['generic']}")
print(f"Manufacturer codes: {stats['manufacturer']}")
```

#### close()

Closes the database connection.

**Example:**
```python
db.close()
```

### DTC Class

Data class representing a diagnostic trouble code.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `code` | str | The DTC code (e.g., 'P0171') |
| `description` | str | Full description of the code |
| `type` | str | Code type ('P', 'B', 'C', or 'U') |
| `manufacturer` | str | Manufacturer name or 'GENERIC' |

#### Properties

##### type_name

Returns human-readable type name.

**Returns:**
- `str`: Type name ('Powertrain', 'Body', 'Chassis', or 'Network')

**Example:**
```python
dtc = db.get_dtc('P0420')
print(dtc.type_name)  # "Powertrain"
```

## Code Types

### P - Powertrain Codes
- Engine and transmission related
- Fuel system, ignition, emissions
- Examples: P0171 (System Too Lean), P0300 (Random Misfire)

### B - Body Codes
- Body control systems
- Climate control, lighting, airbags
- Examples: B0001 (Driver Airbag), B1000 (ECU Malfunction)

### C - Chassis Codes
- ABS, traction control, steering
- Suspension and stability systems
- Examples: C0035 (Wheel Speed Sensor), C0110 (Pump Motor Circuit)

### U - Network Communication Codes
- Module communication errors
- CAN bus and network issues
- Examples: U0100 (Lost Communication with ECM), U0001 (CAN Communication)

## Manufacturer Support

### Supported Manufacturers

The database includes manufacturer-specific codes for:

- **American:** Ford, GM (Chevy, Buick, Cadillac, GMC), Chrysler, Dodge, Jeep
- **European:** Volkswagen, BMW, Mercedes-Benz, Audi, Jaguar, Porsche
- **Japanese:** Toyota, Honda, Nissan, Mazda, Subaru, Mitsubishi
- **Korean:** Kia, Hyundai
- **Luxury:** Lexus, Infiniti, Acura, Lincoln, Cadillac

### Manufacturer Code Format

Manufacturer-specific codes follow the same format as generic codes but with different meanings:

- **P1xxx**: Manufacturer-specific powertrain codes
- **P0xxx**: Generic OBD-II codes (SAE standard)
- **B1xxx/B2xxx**: Manufacturer body codes
- **C1xxx/C2xxx**: Manufacturer chassis codes
- **U1xxx/U2xxx/U3xxx**: Manufacturer network codes

## Error Handling

### Common Exceptions

```python
try:
    db = DTCDatabase('data/dtc_codes.db')
    dtc = db.get_dtc('P0171')
except FileNotFoundError:
    print("Database file not found")
except sqlite3.DatabaseError as e:
    print(f"Database error: {e}")
```

### Handling Missing Codes

```python
dtc = db.get_dtc('P9999')  # Non-existent code
if dtc is None:
    print("Code not found in database")
```

## Performance Optimization

### Connection Management

```python
# Use context manager for automatic cleanup
class DTCDatabase:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage
with DTCDatabase() as db:
    dtc = db.get_dtc('P0420')
```

### Caching

The database includes built-in caching for frequently accessed codes:

```python
# First access - reads from database
dtc1 = db.get_dtc('P0171')

# Second access - returns from cache
dtc2 = db.get_dtc('P0171')  # Faster
```

### Batch Operations

For multiple lookups, use batch operations:

```python
# Inefficient - multiple queries
codes = []
for code in ['P0171', 'P0300', 'P0420']:
    codes.append(db.get_dtc(code))

# Efficient - single query
codes = db.batch_lookup(['P0171', 'P0300', 'P0420'])
```

## Database Schema

### dtc_definitions Table

| Column | Type | Description |
|--------|------|-------------|
| code | TEXT | DTC code (PRIMARY KEY with manufacturer) |
| manufacturer | TEXT | Manufacturer name or 'GENERIC' |
| description | TEXT | Full code description |

### generic_codes Table

| Column | Type | Description |
|--------|------|-------------|
| code | TEXT | DTC code (PRIMARY KEY) |
| description | TEXT | Code description |

### statistics Table

| Column | Type | Description |
|--------|------|-------------|
| category | TEXT | Statistic category |
| value | INTEGER | Statistic value |

## Thread Safety

The DTCDatabase is thread-safe for read operations:

```python
import threading

def worker(code):
    db = DTCDatabase()
    dtc = db.get_dtc(code)
    print(f"Thread {threading.current_thread().name}: {dtc}")
    db.close()

threads = []
for code in ['P0171', 'P0300', 'P0420']:
    t = threading.Thread(target=worker, args=(code,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```