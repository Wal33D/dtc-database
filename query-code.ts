import sqlite3 from '../../odbCodeDB/node_modules/sqlite3';
import { open } from '../../odbCodeDB/node_modules/sqlite';
import * as path from 'path';

async function queryCode(codeToFind: string) {
    const db = await open({
        filename: path.join(__dirname, '../../odbCodeDB/obd2_all_codes.db'),
        driver: sqlite3.Database
    });

    const result = await db.get(
        'SELECT * FROM obd2_codes WHERE code = ?',
        codeToFind.toUpperCase()
    );

    if (result) {
        console.log('\n🔍 Code Found:\n');
        console.log(`Code: ${result.code}`);
        console.log(`Type: ${result.type}`);
        console.log(`Description: ${result.description}`);
        console.log(`Category: ${result.category || 'N/A'}`);
        console.log(`Severity: ${result.severity || 'N/A'}`);
        console.log(`System: ${result.system || 'N/A'}`);
        console.log(`Symptoms: ${result.symptoms || 'N/A'}`);
        console.log(`Possible Causes: ${result.possible_causes || 'N/A'}`);
        console.log(`Manufacturer Specific: ${result.manufacturer_specific ? 'Yes' : 'No'}`);
    } else {
        console.log(`\n❌ Code ${codeToFind} not found in database`);
        console.log('\n💡 This might be a manufacturer-specific code.');
        console.log('   Common P0106 definition:');
        console.log('   Manifold Absolute Pressure/Barometric Pressure Circuit Range/Performance Problem');
    }

    await db.close();
}

// Get code from command line or use default
const codeArg = process.argv[2] || 'P0106';
queryCode(codeArg).catch(console.error);