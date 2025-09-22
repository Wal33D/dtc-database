import sqlite3 from '../../odbCodeDB/node_modules/sqlite3';
import { open } from '../../odbCodeDB/node_modules/sqlite';
import * as path from 'path';
import * as readline from 'readline';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function interactiveQuery() {
    const db = await open({
        filename: path.join(__dirname, '../../odbCodeDB/obd2_all_codes.db'),
        driver: sqlite3.Database
    });

    console.log('🚗 OBD2 Database Query Tool');
    console.log('Commands:');
    console.log('  [code]     - Look up specific code (e.g., P0106)');
    console.log('  search     - Search by keyword');
    console.log('  list       - List all codes by type');
    console.log('  stats      - Show database statistics');
    console.log('  quit       - Exit\n');

    const prompt = () => {
        rl.question('Enter command or code: ', async (input) => {
            const cmd = input.trim().toUpperCase();

            if (cmd === 'QUIT' || cmd === 'EXIT') {
                await db.close();
                rl.close();
                return;
            }

            if (cmd === 'STATS') {
                const stats = await db.all('SELECT type, COUNT(*) as count FROM obd2_codes GROUP BY type');
                const total = await db.get('SELECT COUNT(*) as total FROM obd2_codes');
                console.log(`\n📊 Database Statistics:`);
                console.log(`Total codes: ${total.total}`);
                stats.forEach(s => console.log(`  ${s.type}: ${s.count} codes`));
                console.log();
            } 
            else if (cmd === 'LIST') {
                rl.question('Enter type (Powertrain/Chassis/Body/Network): ', async (type) => {
                    const codes = await db.all('SELECT code, description FROM obd2_codes WHERE type = ? ORDER BY code', type);
                    console.log(`\n${type} Codes:`);
                    codes.forEach(c => console.log(`  ${c.code}: ${c.description}`));
                    console.log();
                    prompt();
                });
                return;
            }
            else if (cmd === 'SEARCH') {
                rl.question('Enter search term: ', async (term) => {
                    const results = await db.all(
                        'SELECT code, description FROM obd2_codes WHERE description LIKE ? OR symptoms LIKE ? OR possible_causes LIKE ? LIMIT 10',
                        `%${term}%`, `%${term}%`, `%${term}%`
                    );
                    console.log(`\n🔍 Search Results for "${term}":`);
                    results.forEach(r => console.log(`  ${r.code}: ${r.description}`));
                    console.log();
                    prompt();
                });
                return;
            }
            else if (cmd.match(/^[PCBU]\d{4}$/)) {
                const result = await db.get('SELECT * FROM obd2_codes WHERE code = ?', cmd);
                if (result) {
                    console.log(`\n✅ ${result.code}: ${result.description}`);
                    console.log(`Type: ${result.type}`);
                    console.log(`Severity: ${result.severity}`);
                    if (result.symptoms) console.log(`Symptoms: ${result.symptoms}`);
                    if (result.possible_causes) console.log(`Causes: ${result.possible_causes}`);
                } else {
                    console.log(`❌ Code ${cmd} not found`);
                }
                console.log();
            }
            else {
                console.log('Invalid command. Try again.\n');
            }

            prompt();
        });
    };

    prompt();
}

interactiveQuery().catch(console.error);