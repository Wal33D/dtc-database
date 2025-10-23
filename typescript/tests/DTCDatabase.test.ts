import { DTCDatabase } from '../src/DTCDatabase';
import * as path from 'path';

describe('DTCDatabase', () => {
  let db: DTCDatabase;

  beforeAll(() => {
    const dbPath = path.join(__dirname, '../../data/dtc_codes.db');
    db = new DTCDatabase({ dbPath });
  });

  afterAll(() => {
    db.close();
  });

  describe('getDTC', () => {
    it('should retrieve a generic powertrain code', () => {
      const dtc = db.getDTC('P0171');
      expect(dtc).not.toBeNull();
      expect(dtc?.code).toBe('P0171');
      expect(dtc?.type).toBe('P');
      expect(dtc?.description).toContain('System Too Lean');
      expect(dtc?.isGeneric).toBe(true);
    });

    it('should retrieve a generic body code', () => {
      const dtc = db.getDTC('B0001');
      expect(dtc).not.toBeNull();
      expect(dtc?.code).toBe('B0001');
      expect(dtc?.type).toBe('B');
    });

    it('should retrieve a generic chassis code', () => {
      const dtc = db.getDTC('C0035');
      expect(dtc).not.toBeNull();
      expect(dtc?.code).toBe('C0035');
      expect(dtc?.type).toBe('C');
    });

    it('should retrieve a generic network code', () => {
      const dtc = db.getDTC('U0100');
      expect(dtc).not.toBeNull();
      expect(dtc?.code).toBe('U0100');
      expect(dtc?.type).toBe('U');
    });

    it('should handle case-insensitive codes', () => {
      const upper = db.getDTC('P0420');
      const lower = db.getDTC('p0420');
      expect(upper).toEqual(lower);
    });

    it('should return null for non-existent codes', () => {
      const dtc = db.getDTC('P9999');
      expect(dtc).toBeNull();
    });
  });

  describe('getDescription', () => {
    it('should retrieve description for a code', () => {
      const desc = db.getDescription('P0300');
      expect(desc).not.toBeNull();
      expect(desc).toContain('Random');
    });

    it('should cache descriptions', () => {
      const desc1 = db.getDescription('P0420');
      const desc2 = db.getDescription('P0420');
      expect(desc1).toBe(desc2);
    });

    it('should return null for invalid codes', () => {
      const desc = db.getDescription('INVALID');
      expect(desc).toBeNull();
    });
  });

  describe('search', () => {
    it('should find codes by keyword', () => {
      const results = db.search('oxygen', 10);
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].description.toLowerCase()).toContain('oxygen');
    });

    it('should find codes by code pattern', () => {
      const results = db.search('P04', 10);
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].code).toMatch(/^P04/);
    });

    it('should respect limit parameter', () => {
      const results = db.search('sensor', 5);
      expect(results.length).toBeLessThanOrEqual(5);
    });

    it('should return empty array for no matches', () => {
      const results = db.search('xyzabc123notfound');
      expect(results).toEqual([]);
    });
  });

  describe('batchLookup', () => {
    it('should retrieve multiple codes', () => {
      const codes = ['P0420', 'P0300', 'P0171'];
      const results = db.batchLookup(codes);
      expect(results.size).toBe(3);
      expect(results.get('P0420')).toBeDefined();
      expect(results.get('P0300')).toBeDefined();
      expect(results.get('P0171')).toBeDefined();
    });

    it('should skip invalid codes', () => {
      const codes = ['P0420', 'INVALID', 'P0300'];
      const results = db.batchLookup(codes);
      expect(results.size).toBe(2);
      expect(results.has('INVALID')).toBe(false);
    });
  });

  describe('getByType', () => {
    it('should retrieve powertrain codes', () => {
      const codes = db.getByType('P', 10);
      expect(codes.length).toBeGreaterThan(0);
      codes.forEach(dtc => {
        expect(dtc.type).toBe('P');
      });
    });

    it('should retrieve body codes', () => {
      const codes = db.getByType('B', 10);
      expect(codes.length).toBeGreaterThan(0);
      codes.forEach(dtc => {
        expect(dtc.type).toBe('B');
      });
    });

    it('should retrieve chassis codes', () => {
      const codes = db.getByType('C', 10);
      expect(codes.length).toBeGreaterThan(0);
      codes.forEach(dtc => {
        expect(dtc.type).toBe('C');
      });
    });

    it('should retrieve network codes', () => {
      const codes = db.getByType('U', 10);
      expect(codes.length).toBeGreaterThan(0);
      codes.forEach(dtc => {
        expect(dtc.type).toBe('U');
      });
    });
  });

  describe('getManufacturerCodes', () => {
    it('should retrieve Ford codes', () => {
      const codes = db.getManufacturerCodes('FORD', 10);
      expect(codes.length).toBeGreaterThan(0);
      codes.forEach(dtc => {
        expect(dtc.manufacturer).toBe('FORD');
        expect(dtc.isGeneric).toBe(false);
      });
    });

    it('should retrieve BMW codes', () => {
      const codes = db.getManufacturerCodes('BMW', 10);
      expect(codes.length).toBeGreaterThan(0);
      codes.forEach(dtc => {
        expect(dtc.manufacturer).toBe('BMW');
      });
    });
  });

  describe('getStatistics', () => {
    it('should return database statistics', () => {
      const stats = db.getStatistics();
      expect(stats.totalCodes).toBeGreaterThan(0);
      expect(stats.genericCodes).toBeGreaterThan(0);
      expect(stats.manufacturerCodes).toBeGreaterThan(0);
      expect(stats.pCodes).toBeGreaterThan(0);
      expect(stats.bCodes).toBeGreaterThan(0);
      expect(stats.cCodes).toBeGreaterThan(0);
      expect(stats.uCodes).toBeGreaterThan(0);
      expect(Object.keys(stats.manufacturers).length).toBeGreaterThan(0);
    });
  });

  describe('getTypeName', () => {
    it('should return correct type names', () => {
      expect(db.getTypeName('P')).toBe('Powertrain');
      expect(db.getTypeName('B')).toBe('Body');
      expect(db.getTypeName('C')).toBe('Chassis');
      expect(db.getTypeName('U')).toBe('Network');
    });
  });

  describe('clearCache', () => {
    it('should clear the cache', () => {
      db.getDescription('P0420'); // Populate cache
      db.clearCache();
      // Cache should be empty but functionality should still work
      const desc = db.getDescription('P0420');
      expect(desc).not.toBeNull();
    });
  });
});
