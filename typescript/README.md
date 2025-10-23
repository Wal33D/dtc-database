# DTC Database - TypeScript/JavaScript Implementation

Comprehensive OBD-II Diagnostic Trouble Code database for TypeScript and JavaScript applications.

## Features

- **28,220+ Diagnostic Codes**
  - 9,415 generic SAE J2012 codes
  - 18,805 manufacturer-specific codes
  - 33+ manufacturer brands

- **Fast & Efficient**
  - <1ms lookups with built-in caching
  - SQLite backend with optimized indexes
  - LRU cache (100-entry limit)

- **Complete API**
  - Code lookups (generic & manufacturer-specific)
  - Full-text search
  - Type-based filtering (P/B/C/U)
  - Batch operations
  - Database statistics

- **Type-Safe**
  - Full TypeScript support
  - Strict type checking
  - IntelliSense support

## Installation

```bash
npm install @wal33d/dtc-database
```

**Note:** Requires Node.js 14+ and the database file from the repository.

## Quick Start

```typescript
import { DTCDatabase } from '@wal33d/dtc-database';

// Initialize
const db = new DTCDatabase();

// Lookup a code
const dtc = db.getDTC('P0420');
console.log(`${dtc.code}: ${dtc.description}`);
// P0420: Catalyst System Efficiency Below Threshold (Bank 1)

// Search
const results = db.search('oxygen sensor', 10);

// Get statistics
const stats = db.getStatistics();
console.log(`Total codes: ${stats.totalCodes}`);

// Clean up
db.close();
```

## API Reference

### Constructor

```typescript
new DTCDatabase(options?: DatabaseOptions)
```

**Options:**
- `dbPath?: string` - Path to SQLite database (default: `../data/dtc_codes.db`)
- `cacheSize?: number` - Maximum cache entries (default: `100`)
- `readOnly?: boolean` - Open in read-only mode (default: `true`)

### Methods

#### `getDTC(code: string, manufacturer?: string): DTC | null`

Get a DTC object by code.

```typescript
const dtc = db.getDTC('P0420');
// { code: 'P0420', description: '...', type: 'P', manufacturer: null, isGeneric: true }
```

#### `getDescription(code: string, manufacturer?: string): string | null`

Get description for a code (cached).

```typescript
const desc = db.getDescription('P0171');
// "System Too Lean (Bank 1)"
```

#### `search(keyword: string, limit?: number): DTC[]`

Search codes by keyword (default limit: 50).

```typescript
const results = db.search('oxygen', 10);
// Returns up to 10 DTCs matching "oxygen"
```

#### `batchLookup(codes: string[]): Map<string, string>`

Lookup multiple codes at once.

```typescript
const codes = ['P0420', 'P0300', 'P0171'];
const results = db.batchLookup(codes);
// Map { 'P0420' => '...', 'P0300' => '...', 'P0171' => '...' }
```

#### `getByType(type: DTCType, limit?: number): DTC[]`

Get codes by type (P/B/C/U, default limit: 100).

```typescript
const pCodes = db.getByType('P', 20);
// Returns up to 20 powertrain codes
```

#### `getManufacturerCodes(manufacturer: string, limit?: number): DTC[]`

Get manufacturer-specific codes (default limit: 200).

```typescript
const fordCodes = db.getManufacturerCodes('FORD', 50);
// Returns up to 50 Ford-specific codes
```

#### `getStatistics(): DTCStatistics`

Get database statistics.

```typescript
const stats = db.getStatistics();
/*
{
  totalCodes: 28220,
  genericCodes: 9415,
  manufacturerCodes: 18805,
  pCodes: 15234,
  bCodes: 4567,
  cCodes: 3210,
  uCodes: 5209,
  manufacturers: { FORD: 1234, BMW: 890, ... }
}
*/
```

#### `getTypeName(type: DTCType): string`

Get full name for code type.

```typescript
db.getTypeName('P'); // "Powertrain"
db.getTypeName('B'); // "Body"
db.getTypeName('C'); // "Chassis"
db.getTypeName('U'); // "Network"
```

#### `clearCache(): void`

Clear the description cache.

```typescript
db.clearCache();
```

#### `close(): void`

Close the database connection.

```typescript
db.close();
```

## Types

### DTC

```typescript
interface DTC {
  code: string;              // e.g., "P0420"
  description: string;       // Full description
  type: 'P' | 'B' | 'C' | 'U'; // Code type
  manufacturer: string | null; // null for generic codes
  isGeneric: boolean;        // true if generic SAE code
}
```

### DTCStatistics

```typescript
interface DTCStatistics {
  totalCodes: number;
  genericCodes: number;
  manufacturerCodes: number;
  pCodes: number;
  bCodes: number;
  cCodes: number;
  uCodes: number;
  manufacturers: Record<string, number>;
}
```

## Code Types

- **P (Powertrain):** Engine, transmission, emissions
- **B (Body):** Airbags, climate control, doors, windows
- **C (Chassis):** ABS, traction control, suspension
- **U (Network):** Communication networks (CAN, LIN)

## Examples

See [examples/example.ts](examples/example.ts) for complete usage examples.

## Performance

- **Lookup:** <1ms (with cache)
- **Search:** ~50ms (full-text)
- **Memory:** ~10MB typical
- **Cache:** 100-entry LRU

## Supported Manufacturers

FORD, GM, CHEVROLET, BUICK, CADILLAC, GMC, CHRYSLER, DODGE, PLYMOUTH, JEEP, BMW, MERCEDES-BENZ, AUDI, VOLKSWAGEN, TOYOTA, HONDA, NISSAN, MAZDA, MITSUBISHI, SUBARU, SUZUKI, ACURA, LEXUS, INFINITI, KIA, and more.

## License

MIT © Wal33D

## Author

Wal33D <aquataze@yahoo.com>
