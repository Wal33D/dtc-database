/**
 * DTC (Diagnostic Trouble Code) type definitions
 */

export type DTCType = 'P' | 'B' | 'C' | 'U';

export interface DTC {
  code: string;
  description: string;
  type: DTCType;
  manufacturer: string | null;
  isGeneric: boolean;
}

export interface DTCStatistics {
  totalCodes: number;
  genericCodes: number;
  manufacturerCodes: number;
  pCodes: number;
  bCodes: number;
  cCodes: number;
  uCodes: number;
  manufacturers: Record<string, number>;
}

export interface DatabaseOptions {
  dbPath?: string;
  cacheSize?: number;
  readOnly?: boolean;
}
