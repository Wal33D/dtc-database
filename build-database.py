#!/usr/bin/env python3
"""
Build SQLite database from source text files
Author: Wal33D
"""

import sqlite3
import os
from pathlib import Path

def build_database():
    """Build dtc_codes.db from source files"""

    # Remove old database if exists
    db_path = 'dtc_codes.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE dtc_codes (
            code TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            type TEXT,
            manufacturer TEXT
        )
    ''')

    # Get source directory
    source_dir = Path('source-data')

    total_codes = 0

    # Process each text file
    for file_path in source_dir.glob('*.txt'):
        file_name = file_path.stem

        # Determine if it's a generic or manufacturer file
        if file_name in ['p_codes', 'b_codes', 'c_codes', 'u_codes']:
            manufacturer = None
            print(f"Processing generic {file_name}...")
        else:
            manufacturer = file_name.replace('_codes', '')
            print(f"Processing {manufacturer} codes...")

        # Read and parse file
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ' - ' in line:
                    parts = line.split(' - ', 1)
                    if len(parts) == 2:
                        code = parts[0].strip().upper()
                        desc = parts[1].strip()

                        # Get code type from first character
                        code_type = code[0] if code else '?'

                        try:
                            cursor.execute(
                                'INSERT OR REPLACE INTO dtc_codes VALUES (?, ?, ?, ?)',
                                (code, desc, code_type, manufacturer)
                            )
                            total_codes += 1
                        except sqlite3.IntegrityError:
                            print(f"Duplicate code: {code}")

    conn.commit()

    # Print statistics
    print(f"\n=== Database Built Successfully ===")
    print(f"Total codes: {total_codes}")

    # Count by type
    for code_type in ['P', 'B', 'C', 'U']:
        cursor.execute('SELECT COUNT(*) FROM dtc_codes WHERE type = ?', (code_type,))
        count = cursor.fetchone()[0]
        type_names = {'P': 'Powertrain', 'B': 'Body', 'C': 'Chassis', 'U': 'Network'}
        print(f"{type_names[code_type]} ({code_type}): {count}")

    # Count manufacturer-specific
    cursor.execute('SELECT COUNT(*) FROM dtc_codes WHERE manufacturer IS NOT NULL')
    mfr_count = cursor.fetchone()[0]
    print(f"Manufacturer-specific: {mfr_count}")

    conn.close()
    print(f"\nDatabase saved as: {db_path}")

if __name__ == '__main__':
    build_database()