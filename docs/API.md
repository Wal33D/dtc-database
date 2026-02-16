# API Reference

## Database Model

Primary table: `dtc_definitions`

| Column | Type | Notes |
|---|---|---|
| `code` | TEXT | DTC code (example: `P0420`) |
| `manufacturer` | TEXT | `GENERIC` or manufacturer key (`FORD`, `BMW`, etc.) |
| `description` | TEXT | Human-readable code description |
| `type` | TEXT | `P`, `B`, `C`, or `U` |
| `locale` | TEXT | Current dataset uses `en` |
| `is_generic` | BOOLEAN | `1` for generic rows |
| `source_file` | TEXT | Source filename used at build time |

Composite primary key: `(code, manufacturer, locale)`.

## Python API (`python/dtc_database.py`)

### `DTCDatabase(db_path: str | None = None, locale: str = "en", cache_size: int = 100)`

### Methods

- `get_dtc(code: str, manufacturer: str | None = None) -> DTC | None`
- `get_description(code: str, manufacturer: str | None = None) -> str | None`
- `search(keyword: str, limit: int = 50) -> list[DTC]`
- `get_by_type(code_type: str, limit: int = 100) -> list[DTC]`
- `get_manufacturer_codes(manufacturer: str, limit: int = 200) -> list[DTC]`
- `batch_lookup(codes: list[str]) -> dict[str, str]`
- `get_statistics() -> dict[str, int]`
- `set_locale(locale: str) -> None`
- `close() -> None`

### `DTC` fields

- `code`
- `description`
- `type`
- `manufacturer` (`None` for generic)
- `is_generic`
- `locale`
- property: `type_name`

### Python Example

```python
from python.dtc_database import DTCDatabase

db = DTCDatabase("data/dtc_codes.db")

print(db.get_description("P0171"))                 # generic-first lookup
print(db.get_description("P1690", "FORD"))         # manufacturer lookup + fallback
print(db.get_manufacturer_codes("BMW", limit=5))   # manufacturer list

stats = db.get_statistics()
print(stats["total"], stats["generic"], stats["manufacturer_specific"])
db.close()
```

## Java API (`java/DTCDatabaseCore.java`)

### Constructors

- `new DTCDatabaseCore()`
- `new DTCDatabaseCore(String dbPath)`
- `new DTCDatabaseCore(String dbPath, String locale)`
- `new DTCDatabaseCore(String dbPath, String locale, int cacheSize)`

### Methods

- `DTC getDTC(String code)`
- `DTC getDTC(String code, String manufacturer)`
- `String getDescription(String code)`
- `String getDescription(String code, String manufacturer)`
- `Map<String, String> getDescriptions(List<String> codes)`
- `List<DTC> search(String keyword)`
- `List<DTC> search(String keyword, int limit)`
- `List<DTC> getByType(char type)`
- `List<DTC> getByType(char type, int limit)`
- `List<DTC> getManufacturerCodes(String manufacturer)`
- `List<DTC> getManufacturerCodes(String manufacturer, int limit)`
- `Map<String, Integer> getStatistics()`
- `void clearCache()`
- `void close()`

### Java `DTC` fields

- `code`
- `description`
- `type`
- `manufacturer` (`null` for generic)
- `isGeneric`
- `locale`
- method: `getTypeName()`
- method: `isManufacturerSpecific()`

### Java Example

```java
import com.dtcdatabase.DTCDatabaseCore;

DTCDatabaseCore db = new DTCDatabaseCore("data/dtc_codes.db");
DTCDatabaseCore.DTC dtc = db.getDTC("P0420");
System.out.println(dtc.code + " " + dtc.getTypeName());
db.close();
```

## Android API (`android/.../DTCDatabase.java`)

Main entrypoint:

- `DTCDatabase.getInstance(context)`

Core methods:

- `getDescription(code)`
- `getDescription(code, manufacturer)`
- `getDTC(code)`
- `getDTC(code, manufacturer)`
- `searchByKeyword(keyword, limit)`
- `getCodesByType(type, limit)`
- `getManufacturerCodes(manufacturer, limit)`
- `getStatistics()`

## TypeScript API (`typescript/src/DTCDatabase.ts`)

Main class: `DTCDatabase`

Methods:

- `getDTC(code, manufacturer?)`
- `getDescription(code, manufacturer?)`
- `search(keyword, limit?)`
- `batchLookup(codes)`
- `getByType(type, limit?)`
- `getManufacturerCodes(manufacturer, limit?)`
- `getStatistics()`
- `getTypeName(type)`
- `clearCache()`
- `close()`

