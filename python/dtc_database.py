#!/usr/bin/env python3
"""
DTC Database Python Library
Access to 18,821 OBD-II diagnostic trouble codes

Author: Wal33D
Email: aquataze@yahoo.com
"""

import json
import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DTC:
    """Diagnostic Trouble Code"""
    code: str
    description: str
    type: str  # P/B/C/U
    manufacturer: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.code} - {self.description}"

    @property
    def type_name(self) -> str:
        """Get human-readable type name"""
        types = {
            'P': 'Powertrain',
            'B': 'Body',
            'C': 'Chassis',
            'U': 'Network'
        }
        return types.get(self.type, 'Unknown')


class DTCDatabase:
    """
    DTC Database interface for Python applications
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'dtc_codes.db')

        self.db_path = db_path
        self.conn = None
        self.cache = {}  # Simple cache for frequent lookups

        # Create database if it doesn't exist
        if not os.path.exists(db_path):
            self.create_database()
        else:
            self.conn = sqlite3.connect(db_path)

    def create_database(self):
        """Create database from source files"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dtc_codes (
                code TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                type TEXT,
                manufacturer TEXT
            )
        ''')

        # Load data from source files
        self._load_from_source_files()

        self.conn.commit()

    def _load_from_source_files(self):
        """Load codes from text files"""
        source_dir = Path(__file__).parent.parent / 'source-data'
        cursor = self.conn.cursor()

        for file_path in source_dir.glob('*.txt'):
            file_name = file_path.stem

            # Determine if it's a manufacturer file
            if file_name in ['p_codes', 'b_codes', 'c_codes', 'u_codes']:
                manufacturer = None
                code_type = file_name[0].upper()
            else:
                manufacturer = file_name.replace('_codes', '')
                code_type = None

            # Read and parse file
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if ' - ' in line:
                        parts = line.split(' - ', 1)
                        if len(parts) == 2:
                            code, desc = parts
                            code = code.strip()
                            desc = desc.strip()

                            if not code_type:
                                code_type = code[0] if code else '?'

                            cursor.execute(
                                'INSERT OR REPLACE INTO dtc_codes VALUES (?, ?, ?, ?)',
                                (code, desc, code_type, manufacturer)
                            )

    def get_description(self, code: str) -> Optional[str]:
        """
        Get description for a single DTC code

        Args:
            code: DTC code (e.g., 'P0171')

        Returns:
            Description string or None if not found
        """
        code = code.upper()

        # Check cache
        if code in self.cache:
            return self.cache[code]

        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT description FROM dtc_codes WHERE code = ?',
            (code,)
        )
        result = cursor.fetchone()

        if result:
            desc = result[0]
            # Cache if not too many items
            if len(self.cache) < 100:
                self.cache[code] = desc
            return desc

        return None

    def get_dtc(self, code: str) -> Optional[DTC]:
        """
        Get complete DTC information

        Args:
            code: DTC code

        Returns:
            DTC object or None if not found
        """
        code = code.upper()
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM dtc_codes WHERE code = ?',
            (code,)
        )
        result = cursor.fetchone()

        if result:
            return DTC(
                code=result[0],
                description=result[1],
                type=result[2],
                manufacturer=result[3]
            )

        return None

    def batch_lookup(self, codes: List[str]) -> Dict[str, str]:
        """
        Look up multiple codes at once

        Args:
            codes: List of DTC codes

        Returns:
            Dictionary mapping codes to descriptions
        """
        results = {}
        for code in codes:
            desc = self.get_description(code)
            if desc:
                results[code] = desc
        return results

    def search(self, keyword: str, limit: int = 50) -> List[DTC]:
        """
        Search codes by keyword in code or description

        Args:
            keyword: Search term
            limit: Maximum results

        Returns:
            List of matching DTCs
        """
        cursor = self.conn.cursor()
        search_term = f'%{keyword}%'

        cursor.execute('''
            SELECT * FROM dtc_codes
            WHERE code LIKE ? OR description LIKE ?
            LIMIT ?
        ''', (search_term, search_term, limit))

        results = []
        for row in cursor.fetchall():
            results.append(DTC(
                code=row[0],
                description=row[1],
                type=row[2],
                manufacturer=row[3]
            ))

        return results

    def get_by_type(self, code_type: str, limit: int = 100) -> List[DTC]:
        """
        Get codes by type (P/B/C/U)

        Args:
            code_type: Single character type
            limit: Maximum results

        Returns:
            List of DTCs of that type
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM dtc_codes WHERE type = ? LIMIT ?',
            (code_type.upper(), limit)
        )

        results = []
        for row in cursor.fetchall():
            results.append(DTC(
                code=row[0],
                description=row[1],
                type=row[2],
                manufacturer=row[3]
            ))

        return results

    def get_manufacturer_codes(self, manufacturer: str, limit: int = 200) -> List[DTC]:
        """
        Get manufacturer-specific codes

        Args:
            manufacturer: Manufacturer name
            limit: Maximum results

        Returns:
            List of manufacturer-specific DTCs
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM dtc_codes WHERE manufacturer = ? LIMIT ?',
            (manufacturer.lower(), limit)
        )

        results = []
        for row in cursor.fetchall():
            results.append(DTC(
                code=row[0],
                description=row[1],
                type=row[2],
                manufacturer=row[3]
            ))

        return results

    def get_statistics(self) -> Dict[str, int]:
        """
        Get database statistics

        Returns:
            Dictionary with counts by type and total
        """
        cursor = self.conn.cursor()

        stats = {}

        # Total count
        cursor.execute('SELECT COUNT(*) FROM dtc_codes')
        stats['total'] = cursor.fetchone()[0]

        # Count by type
        for code_type in ['P', 'B', 'C', 'U']:
            cursor.execute(
                'SELECT COUNT(*) FROM dtc_codes WHERE type = ?',
                (code_type,)
            )
            stats[f'type_{code_type}'] = cursor.fetchone()[0]

        # Count manufacturer-specific
        cursor.execute(
            'SELECT COUNT(*) FROM dtc_codes WHERE manufacturer IS NOT NULL'
        )
        stats['manufacturer_specific'] = cursor.fetchone()[0]

        return stats

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == '__main__':
    # Initialize database
    db = DTCDatabase()

    # Look up a code
    print(db.get_description('P0171'))

    # Search for codes
    results = db.search('oxygen sensor')
    for dtc in results[:5]:
        print(dtc)

    # Get statistics
    stats = db.get_statistics()
    print(f"\nDatabase Statistics:")
    print(f"Total codes: {stats['total']}")
    print(f"Powertrain: {stats['type_P']}")
    print(f"Body: {stats['type_B']}")
    print(f"Chassis: {stats['type_C']}")
    print(f"Network: {stats['type_U']}")
    print(f"Manufacturer-specific: {stats['manufacturer_specific']}")

    db.close()