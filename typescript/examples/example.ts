import { DTCDatabase } from '../src';

/**
 * DTC Database - TypeScript Usage Examples
 */

async function main() {
  // Initialize the database
  const db = new DTCDatabase();

  console.log('=== DTC Database Examples ===\n');

  // Example 1: Basic code lookup
  console.log('1. Basic Code Lookup:');
  const p0420 = db.getDTC('P0420');
  if (p0420) {
    console.log(`   Code: ${p0420.code}`);
    console.log(`   Type: ${db.getTypeName(p0420.type)}`);
    console.log(`   Description: ${p0420.description}`);
    console.log(`   Generic: ${p0420.isGeneric ? 'Yes' : 'No'}\n`);
  }

  // Example 2: Get description only
  console.log('2. Get Description:');
  const desc = db.getDescription('P0171');
  console.log(`   P0171: ${desc}\n`);

  // Example 3: Search by keyword
  console.log('3. Search for "oxygen sensor":');
  const searchResults = db.search('oxygen sensor', 5);
  searchResults.forEach((dtc, i) => {
    console.log(`   ${i + 1}. ${dtc.code} - ${dtc.description}`);
  });
  console.log();

  // Example 4: Batch lookup
  console.log('4. Batch Lookup:');
  const codes = ['P0420', 'P0300', 'P0171', 'B0001', 'U0100'];
  const batchResults = db.batchLookup(codes);
  batchResults.forEach((description, code) => {
    console.log(`   ${code}: ${description}`);
  });
  console.log();

  // Example 5: Get codes by type
  console.log('5. Get Powertrain Codes (P):');
  const pCodes = db.getByType('P', 5);
  pCodes.forEach((dtc, i) => {
    console.log(`   ${i + 1}. ${dtc.code} - ${dtc.description.substring(0, 50)}...`);
  });
  console.log();

  // Example 6: Manufacturer-specific codes
  console.log('6. Ford-Specific Codes:');
  const fordCodes = db.getManufacturerCodes('FORD', 5);
  fordCodes.forEach((dtc, i) => {
    console.log(`   ${i + 1}. ${dtc.code} - ${dtc.description.substring(0, 50)}...`);
  });
  console.log();

  // Example 7: Database statistics
  console.log('7. Database Statistics:');
  const stats = db.getStatistics();
  console.log(`   Total Codes: ${stats.totalCodes.toLocaleString()}`);
  console.log(`   Generic Codes: ${stats.genericCodes.toLocaleString()}`);
  console.log(`   Manufacturer Codes: ${stats.manufacturerCodes.toLocaleString()}`);
  console.log(`   Powertrain (P): ${stats.pCodes.toLocaleString()}`);
  console.log(`   Body (B): ${stats.bCodes.toLocaleString()}`);
  console.log(`   Chassis (C): ${stats.cCodes.toLocaleString()}`);
  console.log(`   Network (U): ${stats.uCodes.toLocaleString()}`);
  console.log(`   Manufacturers: ${Object.keys(stats.manufacturers).length}`);
  console.log();

  // Example 8: Case handling
  console.log('8. Case-Insensitive Lookup:');
  console.log(`   p0420 (lowercase): ${db.getDescription('p0420')}`);
  console.log(`   P0420 (uppercase): ${db.getDescription('P0420')}`);
  console.log();

  // Clean up
  db.close();
  console.log('Database closed.');
}

// Run examples
main().catch(console.error);
