# DTC Database (TypeScript/JavaScript)

TypeScript wrapper for the SQLite DTC dataset in this repository.

## Dataset Snapshot (`locale='en'`)

- Total definitions: `18,805`
- Generic definitions: `9,415`
- Manufacturer-specific definitions: `9,390`
- Manufacturers (excluding `GENERIC`): `33`

## Status

The TypeScript module is currently maintained as repository source (`typescript/`) and uses `../data/dtc_codes.db` by default when run from this repo layout.

## Setup

```bash
cd typescript
npm install
npm run build
npm test
```

## Quick Start

```typescript
import { DTCDatabase } from "./dist";

const db = new DTCDatabase();

const dtc = db.getDTC("P0420");
console.log(dtc?.code, dtc?.description);

const fordSpecific = db.getDTC("P1690", "FORD");
console.log(fordSpecific?.description);

const stats = db.getStatistics();
console.log(stats.totalCodes, stats.genericCodes, stats.manufacturerCodes);

db.close();
```

## Constructor

```typescript
new DTCDatabase(options?: {
  dbPath?: string;
  cacheSize?: number;
  readOnly?: boolean;
})
```

Defaults:

- `dbPath`: `../../data/dtc_codes.db` (relative to built file)
- `cacheSize`: `100`
- `readOnly`: `true`

## API

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

## Example Statistics Shape

```typescript
{
  totalCodes: 18805,
  genericCodes: 9415,
  manufacturerCodes: 9390,
  pCodes: 14821,
  bCodes: 1465,
  cCodes: 985,
  uCodes: 1534,
  manufacturers: {
    FORD: 413,
    BMW: 250
  }
}
```

## License

MIT
