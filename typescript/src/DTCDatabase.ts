import Database from 'better-sqlite3';
import * as path from 'path';
import { DTC, DTCType, DTCStatistics, DatabaseOptions } from './types';

/** Database row structure */
interface DTCRow {
  code: string;
  description: string;
  type: string;
  manufacturer: string;
  is_generic?: number;
  count?: number;
}

/**
 * DTC Database - OBD-II Diagnostic Trouble Code Database
 *
 * Provides access to 18,805 diagnostic code definitions including:
 * - 9,415 generic SAE J2012 codes
 * - 9,390 manufacturer-specific definitions
 * - 33 manufacturer brands
 *
 * Features:
 * - Fast lookups (<1ms with caching)
 * - Full-text search
 * - Manufacturer-specific lookups
 * - Type-based filtering (P/B/C/U)
 * - Batch operations
 */
export class DTCDatabase {
  private db: Database.Database;
  private cache: Map<string, string>;
  private readonly cacheSize: number;
  private readonly TYPE_NAMES: Record<string, string> = {
    'P': 'Powertrain',
    'B': 'Body',
    'C': 'Chassis',
    'U': 'Network'
  };

  /**
   * Create a new DTC Database instance
   *
   * @param options - Configuration options
   * @param options.dbPath - Path to SQLite database (defaults to ../data/dtc_codes.db)
   * @param options.cacheSize - Maximum cache entries (default: 100)
   * @param options.readOnly - Open database in read-only mode (default: true)
   */
  constructor(options: DatabaseOptions = {}) {
    const {
      dbPath = path.join(__dirname, '../../data/dtc_codes.db'),
      cacheSize = 100,
      readOnly = true
    } = options;

    this.cacheSize = cacheSize;
    this.cache = new Map();

    try {
      this.db = new Database(dbPath, { readonly: readOnly, fileMustExist: true });
      // Only set WAL mode and synchronous pragma if not in read-only mode
      // WAL mode requires write permissions which aren't available in read-only mode
      if (!readOnly) {
        this.db.pragma('journal_mode = WAL');
        this.db.pragma('synchronous = NORMAL');
      }
    } catch (error) {
      throw new Error(`Failed to open database at ${dbPath}: ${error}`);
    }
  }

  /**
   * Get a DTC by code
   *
   * @param code - The diagnostic code (e.g., "P0420")
   * @param manufacturer - Optional manufacturer name for specific lookups
   * @returns DTC object or null if not found
   */
  getDTC(code: string, manufacturer?: string): DTC | null {
    const normalizedCode = code.toUpperCase().trim();

    const stmt = manufacturer
      ? this.db.prepare(`
          SELECT code, description, type, manufacturer
          FROM dtc_definitions
          WHERE code = ? AND manufacturer = ? AND locale = 'en'
          LIMIT 1
        `)
      : this.db.prepare(`
          SELECT code, description, type, manufacturer
          FROM dtc_definitions
          WHERE code = ? AND locale = 'en'
          ORDER BY is_generic DESC
          LIMIT 1
        `);

    const result = manufacturer
      ? stmt.get(normalizedCode, manufacturer) as DTCRow | undefined
      : stmt.get(normalizedCode) as DTCRow | undefined;

    if (!result) return null;

    return {
      code: result.code,
      description: result.description,
      type: result.type as DTCType,
      manufacturer: result.manufacturer === 'GENERIC' ? null : result.manufacturer,
      isGeneric: result.manufacturer === 'GENERIC'
    };
  }

  /**
   * Get description for a DTC code
   *
   * @param code - The diagnostic code
   * @param manufacturer - Optional manufacturer name
   * @returns Description string or null if not found
   */
  getDescription(code: string, manufacturer?: string): string | null {
    const normalizedCode = code.toUpperCase().trim();
    const cacheKey = manufacturer ? `${normalizedCode}:${manufacturer}` : normalizedCode;

    // Check cache first
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    const dtc = this.getDTC(normalizedCode, manufacturer);
    if (!dtc) return null;

    // Update cache (LRU-style)
    if (this.cache.size >= this.cacheSize) {
      const firstKey = this.cache.keys().next().value as string;
      this.cache.delete(firstKey);
    }
    this.cache.set(cacheKey, dtc.description);

    return dtc.description;
  }

  /**
   * Search DTCs by keyword
   *
   * @param keyword - Search term
   * @param limit - Maximum results (default: 50)
   * @returns Array of matching DTCs
   */
  search(keyword: string, limit: number = 50): DTC[] {
    const stmt = this.db.prepare(`
      SELECT code, description, type, manufacturer
      FROM dtc_definitions
      WHERE (code LIKE ? OR description LIKE ?) AND locale = 'en'
      ORDER BY is_generic DESC, code ASC
      LIMIT ?
    `);

    const searchTerm = `%${keyword}%`;
    const results = stmt.all(searchTerm, searchTerm, limit) as DTCRow[];

    return results.map(row => ({
      code: row.code,
      description: row.description,
      type: row.type as DTCType,
      manufacturer: row.manufacturer === 'GENERIC' ? null : row.manufacturer,
      isGeneric: row.manufacturer === 'GENERIC'
    }));
  }

  /**
   * Batch lookup of multiple codes
   *
   * @param codes - Array of diagnostic codes
   * @returns Map of code to description
   */
  batchLookup(codes: string[]): Map<string, string> {
    const results = new Map<string, string>();

    for (const code of codes) {
      const description = this.getDescription(code);
      if (description) {
        results.set(code.toUpperCase(), description);
      }
    }

    return results;
  }

  /**
   * Get codes by type (P/B/C/U)
   *
   * @param type - Code type ('P', 'B', 'C', or 'U')
   * @param limit - Maximum results (default: 100)
   * @returns Array of DTCs of the specified type
   */
  getByType(type: DTCType, limit: number = 100): DTC[] {
    const stmt = this.db.prepare(`
      SELECT code, description, type, manufacturer
      FROM dtc_definitions
      WHERE type = ? AND locale = 'en'
      ORDER BY is_generic DESC, code ASC
      LIMIT ?
    `);

    const results = stmt.all(type.toUpperCase(), limit) as DTCRow[];

    return results.map(row => ({
      code: row.code,
      description: row.description,
      type: row.type as DTCType,
      manufacturer: row.manufacturer === 'GENERIC' ? null : row.manufacturer,
      isGeneric: row.manufacturer === 'GENERIC'
    }));
  }

  /**
   * Get manufacturer-specific codes
   *
   * @param manufacturer - Manufacturer name (e.g., "FORD", "BMW")
   * @param limit - Maximum results (default: 200)
   * @returns Array of manufacturer-specific DTCs
   */
  getManufacturerCodes(manufacturer: string, limit: number = 200): DTC[] {
    const stmt = this.db.prepare(`
      SELECT code, description, type, manufacturer
      FROM dtc_definitions
      WHERE manufacturer = ? AND locale = 'en'
      ORDER BY code ASC
      LIMIT ?
    `);

    const results = stmt.all(manufacturer.toUpperCase(), limit) as DTCRow[];

    return results.map(row => ({
      code: row.code,
      description: row.description,
      type: row.type as DTCType,
      manufacturer: row.manufacturer,
      isGeneric: false
    }));
  }

  /**
   * Get database statistics
   *
   * @returns Statistics object with counts
   */
  getStatistics(): DTCStatistics {
    const totalStmt = this.db.prepare(`
      SELECT COUNT(*) as count FROM dtc_definitions WHERE locale = 'en'
    `);
    const genericStmt = this.db.prepare(`
      SELECT COUNT(*) as count FROM dtc_definitions WHERE is_generic = 1 AND locale = 'en'
    `);
    const typeStmt = this.db.prepare(`
      SELECT type, COUNT(*) as count
      FROM dtc_definitions
      WHERE locale = 'en'
      GROUP BY type
    `);
    const mfrStmt = this.db.prepare(`
      SELECT manufacturer, COUNT(*) as count
      FROM dtc_definitions
      WHERE manufacturer != 'GENERIC' AND locale = 'en'
      GROUP BY manufacturer
    `);

    const total = (totalStmt.get() as DTCRow).count!;
    const generic = (genericStmt.get() as DTCRow).count!;
    const typeCounts = typeStmt.all() as DTCRow[];
    const mfrCounts = mfrStmt.all() as DTCRow[];

    const stats: DTCStatistics = {
      totalCodes: total,
      genericCodes: generic,
      manufacturerCodes: total - generic,
      pCodes: 0,
      bCodes: 0,
      cCodes: 0,
      uCodes: 0,
      manufacturers: {}
    };

    for (const row of typeCounts) {
      switch (row.type) {
        case 'P': stats.pCodes = row.count!; break;
        case 'B': stats.bCodes = row.count!; break;
        case 'C': stats.cCodes = row.count!; break;
        case 'U': stats.uCodes = row.count!; break;
      }
    }

    for (const row of mfrCounts) {
      stats.manufacturers[row.manufacturer] = row.count!;
    }

    return stats;
  }

  /**
   * Get type name from code
   *
   * @param type - Type character ('P', 'B', 'C', 'U')
   * @returns Full type name
   */
  getTypeName(type: DTCType): string {
    return this.TYPE_NAMES[type] || 'Unknown';
  }

  /**
   * Clear the description cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Close the database connection
   */
  close(): void {
    this.db.close();
  }
}
