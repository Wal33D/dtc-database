#!/usr/bin/env python3
"""
Perfect DTC Database Builder
Preserves ALL manufacturer-specific definitions

Author: Wal33D
"""

import sqlite3
import os
from pathlib import Path
from collections import defaultdict

def build_perfect_database():
    """Build complete database preserving manufacturer context"""

    # Remove old database
    db_path = 'dtc_perfect.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create improved schema
    cursor.execute('''
        CREATE TABLE dtc_definitions (
            code TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            description TEXT NOT NULL,
            is_generic BOOLEAN DEFAULT 0,
            source_file TEXT,
            PRIMARY KEY (code, manufacturer)
        )
    ''')

    # Create indexes for performance
    cursor.execute('CREATE INDEX idx_code ON dtc_definitions(code)')
    cursor.execute('CREATE INDEX idx_manufacturer ON dtc_definitions(manufacturer)')
    cursor.execute('CREATE INDEX idx_generic ON dtc_definitions(is_generic)')

    # Create view for generic codes
    cursor.execute('''
        CREATE VIEW generic_codes AS
        SELECT DISTINCT code, description
        FROM dtc_definitions
        WHERE is_generic = 1
    ''')

    # Create statistics table
    cursor.execute('''
        CREATE TABLE statistics (
            manufacturer TEXT PRIMARY KEY,
            total_codes INTEGER,
            unique_codes INTEGER,
            p_codes INTEGER,
            b_codes INTEGER,
            c_codes INTEGER,
            u_codes INTEGER
        )
    ''')

    source_dir = Path('source-data')
    total_entries = 0
    manufacturer_stats = defaultdict(lambda: {'total': 0, 'unique': set(), 'P': 0, 'B': 0, 'C': 0, 'U': 0})

    # Process each file
    for file_path in sorted(source_dir.glob('*.txt')):
        file_name = file_path.stem

        # Determine manufacturer
        if file_name in ['p_codes', 'b_codes', 'c_codes', 'u_codes']:
            manufacturer = 'GENERIC'
            is_generic = True
        else:
            manufacturer = file_name.replace('_codes', '').upper()
            is_generic = False

        print(f"Processing {manufacturer}...")

        # Read and parse file
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if ' - ' in line:
                    parts = line.split(' - ', 1)
                    if len(parts) == 2:
                        code = parts[0].strip().upper()
                        desc = parts[1].strip()

                        # Skip obvious data errors
                        if len(code) == 5 and code[0] in 'PBCU':
                            # Insert definition
                            try:
                                cursor.execute('''
                                    INSERT INTO dtc_definitions
                                    (code, manufacturer, description, is_generic, source_file)
                                    VALUES (?, ?, ?, ?, ?)
                                ''', (code, manufacturer, desc, is_generic, file_name))

                                total_entries += 1

                                # Update stats
                                manufacturer_stats[manufacturer]['total'] += 1
                                manufacturer_stats[manufacturer]['unique'].add(code)
                                manufacturer_stats[manufacturer][code[0]] += 1

                            except sqlite3.IntegrityError:
                                # Duplicate within same manufacturer file
                                print(f"  Warning: Duplicate {code} in {file_name} line {line_num}")

    # Insert statistics
    for mfr, stats in manufacturer_stats.items():
        cursor.execute('''
            INSERT INTO statistics VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (mfr, stats['total'], len(stats['unique']),
              stats['P'], stats['B'], stats['C'], stats['U']))

    conn.commit()

    # Print summary
    print(f"\n=== Perfect Database Built ===")
    print(f"Total entries preserved: {total_entries}")

    # Show codes with multiple definitions
    cursor.execute('''
        SELECT code, COUNT(DISTINCT manufacturer) as variants
        FROM dtc_definitions
        GROUP BY code
        HAVING variants > 1
        ORDER BY variants DESC
        LIMIT 10
    ''')

    print("\nTop 10 codes with multiple definitions:")
    for code, count in cursor.fetchall():
        print(f"  {code}: {count} different definitions")

    # Show P1690 as example
    print("\nExample - P1690 definitions:")
    cursor.execute('''
        SELECT manufacturer, description
        FROM dtc_definitions
        WHERE code = 'P1690'
        ORDER BY manufacturer
    ''')

    for mfr, desc in cursor.fetchall():
        print(f"  {mfr:12} : {desc[:60]}...")

    # Overall statistics
    cursor.execute('SELECT COUNT(DISTINCT code) FROM dtc_definitions')
    unique_codes = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT code) FROM dtc_definitions WHERE is_generic = 1')
    generic_codes = cursor.fetchone()[0]

    print(f"\n=== Statistics ===")
    print(f"Total entries: {total_entries}")
    print(f"Unique codes: {unique_codes}")
    print(f"Generic codes: {generic_codes}")
    print(f"Manufacturer variations: {total_entries - generic_codes}")

    conn.close()
    print(f"\nDatabase saved as: {db_path}")

if __name__ == '__main__':
    build_perfect_database()