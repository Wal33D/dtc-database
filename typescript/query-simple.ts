#!/usr/bin/env ts-node
/**
 * Simple DTC query without external dependencies
 * Uses better-sqlite3 for synchronous database access
 */

import * as fs from 'fs';
import * as path from 'path';

// Simple SQLite interface using better-sqlite3 (install: npm i better-sqlite3 @types/better-sqlite3)
const Database = require('better-sqlite3');

const DB_PATH = path.join(__dirname, '..', 'dtc_codes.db');

function queryCode(code: string) {
    if (!fs.existsSync(DB_PATH)) {
        console.error('Database not found. Run: python3 build-database.py');
        process.exit(1);
    }

    const db = new Database(DB_PATH, { readonly: true });

    try {
        const stmt = db.prepare('SELECT * FROM dtc_codes WHERE code = ?');
        const result = stmt.get(code.toUpperCase());

        if (result) {
            console.log('\n=== DTC Found ===');
            console.log(`Code: ${result.code}`);
            console.log(`Type: ${getTypeName(result.type)}`);
            console.log(`Description: ${result.description}`);
            if (result.manufacturer) {
                console.log(`Manufacturer: ${result.manufacturer}`);
            }
        } else {
            console.log(`\nCode ${code} not found in database`);
        }
    } finally {
        db.close();
    }
}

function getTypeName(type: string): string {
    const types: Record<string, string> = {
        'P': 'Powertrain',
        'B': 'Body',
        'C': 'Chassis',
        'U': 'Network'
    };
    return `${type} (${types[type] || 'Unknown'})`;
}

// Get code from command line
const code = process.argv[2];
if (!code) {
    console.log('Usage: ts-node query-simple.ts <CODE>');
    console.log('Example: ts-node query-simple.ts P0171');
    process.exit(1);
}

queryCode(code);