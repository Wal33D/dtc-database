#!/usr/bin/env python3
"""
Perfect DTC Database with Manufacturer Context
Handles all 18,805 definitions intelligently

Author: Wal33D
"""

import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ManufacturerDTC:
    """DTC with manufacturer context"""
    code: str
    manufacturer: str
    description: str
    is_generic: bool

    def __str__(self) -> str:
        prefix = "[GENERIC]" if self.is_generic else f"[{self.manufacturer}]"
        return f"{self.code} {prefix} {self.description}"


class PerfectDTCDatabase:
    """
    Intelligent DTC Database that preserves manufacturer context
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            # Try perfect database first, then fallback
            if os.path.exists('dtc_perfect.db'):
                db_path = 'dtc_perfect.db'
            else:
                db_path = 'dtc_codes.db'

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cache = {}

    def get_for_manufacturer(self, code: str, manufacturer: str) -> Optional[str]:
        """
        Get definition for specific manufacturer

        Args:
            code: DTC code (e.g., 'P1690')
            manufacturer: Manufacturer name (e.g., 'FORD', 'BMW')

        Returns:
            Description for that manufacturer, or None
        """
        code = code.upper()
        manufacturer = manufacturer.upper()

        cursor = self.conn.cursor()

        # Try exact manufacturer match
        cursor.execute('''
            SELECT description FROM dtc_definitions
            WHERE code = ? AND manufacturer = ?
        ''', (code, manufacturer))

        result = cursor.fetchone()
        if result:
            return result[0]

        # Special case: INFINITI uses NISSAN codes
        if manufacturer == 'NISSAN':
            cursor.execute('''
                SELECT description FROM dtc_definitions
                WHERE code = ? AND manufacturer = 'INFINITI'
            ''', (code,))
            result = cursor.fetchone()
            if result:
                return result[0]

        # Special case: GM brands can use generic GM codes
        if manufacturer in ['CHEVY', 'BUICK', 'CADILLAC', 'GMC', 'PONTIAC', 'OLDSMOBILE', 'SATURN', 'GEO']:
            cursor.execute('''
                SELECT description FROM dtc_definitions
                WHERE code = ? AND manufacturer = 'GM'
            ''', (code,))
            result = cursor.fetchone()
            if result:
                return result[0]

        # Fallback to generic if available
        cursor.execute('''
            SELECT description FROM dtc_definitions
            WHERE code = ? AND is_generic = 1
        ''', (code,))

        result = cursor.fetchone()
        return result[0] if result else None

    def get_all_definitions(self, code: str) -> List[ManufacturerDTC]:
        """
        Get ALL definitions for a code across manufacturers

        Args:
            code: DTC code

        Returns:
            List of all definitions with manufacturer context
        """
        code = code.upper()
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT manufacturer, description, is_generic
            FROM dtc_definitions
            WHERE code = ?
            ORDER BY is_generic DESC, manufacturer
        ''', (code,))

        results = []
        for mfr, desc, is_generic in cursor.fetchall():
            results.append(ManufacturerDTC(
                code=code,
                manufacturer=mfr,
                description=desc,
                is_generic=bool(is_generic)
            ))

        return results

    def get_smart(self, code: str, manufacturer: Optional[str] = None,
                  vin: Optional[str] = None) -> Dict:
        """
        Smart lookup with intelligent fallback

        Args:
            code: DTC code
            manufacturer: Optional manufacturer
            vin: Optional VIN (can extract manufacturer from VIN)

        Returns:
            Dictionary with best match and alternatives
        """
        code = code.upper()
        result = {
            'code': code,
            'primary': None,
            'alternatives': [],
            'total_definitions': 0,
            'is_manufacturer_specific': False
        }

        # Determine if manufacturer-specific (P1xxx, P3xxx, etc.)
        if code.startswith('P') and len(code) == 5:
            second_char = code[1]
            result['is_manufacturer_specific'] = second_char in '13'

        # Extract manufacturer from VIN if provided
        if vin and not manufacturer:
            manufacturer = self.get_manufacturer_from_vin(vin)

        # Get all definitions
        all_defs = self.get_all_definitions(code)
        result['total_definitions'] = len(all_defs)

        if not all_defs:
            return result

        # Find primary definition
        if manufacturer:
            # Look for manufacturer-specific first
            for dtc in all_defs:
                if dtc.manufacturer.upper() == manufacturer.upper():
                    result['primary'] = dtc
                    break

        # If no manufacturer match, use generic if available
        if not result['primary']:
            for dtc in all_defs:
                if dtc.is_generic:
                    result['primary'] = dtc
                    break

        # If still no primary, use most common definition
        if not result['primary'] and all_defs:
            # Group by description and count occurrences
            desc_counts = {}
            for dtc in all_defs:
                desc = dtc.description
                if desc not in desc_counts:
                    desc_counts[desc] = []
                desc_counts[desc].append(dtc)

            # Find most common description
            most_common = max(desc_counts.items(), key=lambda x: len(x[1]))
            result['primary'] = most_common[1][0]  # First DTC with most common description

        # Add alternatives (exclude primary)
        for dtc in all_defs:
            if dtc != result['primary']:
                result['alternatives'].append(dtc)

        return result

    def get_manufacturer_from_vin(self, vin: str) -> Optional[str]:
        """
        Extract manufacturer from VIN
        World Manufacturer Identifier (WMI) is first 3 characters
        """
        if not vin or len(vin) < 3:
            return None

        wmi = vin[:3].upper()

        # Common WMI mappings
        wmi_map = {
            # US Manufacturers - Ford
            '1FA': 'FORD', '1FB': 'FORD', '1FC': 'FORD', '1FD': 'FORD',
            '1FM': 'FORD', '1FT': 'FORD', '1FU': 'FORD', '1FV': 'FORD',

            # US Manufacturers - General Motors
            '1G1': 'CHEVY', '1G2': 'PONTIAC', '1G3': 'OLDSMOBILE',
            '1G4': 'BUICK', '1G6': 'CADILLAC', '1G8': 'SATURN',
            '1GC': 'CHEVY', '1GM': 'PONTIAC', '1GT': 'GMC',
            '1GE': 'CADILLAC', '1GY': 'CADILLAC', '1G9': 'GEO',

            # US Manufacturers - Chrysler Group
            '1C3': 'CHRYSLER', '1C4': 'CHRYSLER', '1C6': 'CHRYSLER',
            '1D3': 'DODGE', '1D4': 'DODGE', '1D7': 'DODGE', '1D8': 'DODGE',
            '1J4': 'JEEP', '1J8': 'JEEP',
            '1P3': 'PLYMOUTH', '1P4': 'PLYMOUTH', '1P7': 'PLYMOUTH',

            # US Manufacturers - Other
            '1HG': 'HONDA', '1LN': 'LINCOLN', '1ME': 'MERCURY',
            '1N4': 'NISSAN', '1N6': 'NISSAN', '1VW': 'VOLKSWAGEN',
            '1YV': 'MAZDA', '1ZV': 'FORD',

            # Canadian Manufacturers
            '2FA': 'FORD', '2FB': 'FORD', '2FC': 'FORD', '2FM': 'FORD',
            '2FT': 'FORD', '2FU': 'FORD', '2FV': 'FORD', '2FZ': 'FORD',
            '2G1': 'CHEVY', '2G2': 'PONTIAC', '2G3': 'OLDSMOBILE',
            '2G4': 'BUICK', '2G5': 'GMC', '2G6': 'CADILLAC', '2G9': 'GEO',
            '2HG': 'HONDA', '2HK': 'HONDA', '2HM': 'HONDA',
            '2LM': 'LINCOLN', '2ME': 'MERCURY',
            '2C3': 'CHRYSLER', '2C4': 'CHRYSLER', '2D3': 'DODGE',
            '2P3': 'PLYMOUTH', '2P4': 'PLYMOUTH',

            # Mexican Manufacturers
            '3FA': 'FORD', '3FE': 'FORD', '3G1': 'CHEVY',
            '3G2': 'PONTIAC', '3G4': 'BUICK', '3G5': 'BUICK',
            '3G6': 'CADILLAC', '3G7': 'GMC', '3GC': 'CHEVY',
            '3VW': 'VOLKSWAGEN', '3C4': 'CHRYSLER', '3D3': 'DODGE',
            '3D4': 'DODGE', '3P3': 'PLYMOUTH',

            # US Manufacturers continued (4-5 prefix)
            '4F2': 'MAZDA', '4F3': 'MAZDA', '4F4': 'MAZDA',
            '4J8': 'JEEP', '4JG': 'MERCEDES', '4US': 'BMW',
            '4T1': 'TOYOTA', '4T3': 'TOYOTA',
            '5FN': 'HONDA', '5J6': 'HONDA', '5J8': 'ACURA',
            '5NP': 'KIA', '5TB': 'TOYOTA', '5TD': 'TOYOTA',
            '5TE': 'TOYOTA', '5TF': 'TOYOTA', '5YJ': 'TESLA',

            # US - Mitsubishi
            '4A3': 'MITSUBISHI', '4A4': 'MITSUBISHI', '4A5': 'MITSUBISHI',
            '4B3': 'MITSUBISHI',

            # Japanese Manufacturers
            'JA3': 'MITSUBISHI', 'JA4': 'MITSUBISHI', 'JA7': 'MITSUBISHI',
            'JF1': 'SUBARU', 'JF2': 'SUBARU', 'JF3': 'SUBARU',
            'JH4': 'ACURA', 'JHG': 'HONDA', 'JHL': 'HONDA', 'JHM': 'HONDA',
            'JM1': 'MAZDA', 'JM3': 'MAZDA', 'JM7': 'MAZDA',
            'JN1': 'NISSAN', 'JN3': 'NISSAN', 'JN6': 'NISSAN', 'JN8': 'NISSAN',
            'JS1': 'SUZUKI', 'JS2': 'SUZUKI', 'JS3': 'SUZUKI',
            'JT2': 'TOYOTA', 'JT3': 'TOYOTA', 'JT4': 'TOYOTA',
            'JT5': 'TOYOTA', 'JT6': 'TOYOTA', 'JT8': 'LEXUS',
            'JTD': 'TOYOTA', 'JTE': 'TOYOTA', 'JTH': 'LEXUS',
            'JTJ': 'LEXUS', 'JTK': 'TOYOTA', 'JTL': 'TOYOTA',
            'JTM': 'TOYOTA', 'JTN': 'TOYOTA',

            # Korean Manufacturers
            'KM8': 'KIA', 'KN8': 'KIA', 'KNA': 'KIA',
            'KND': 'KIA', 'KNH': 'KIA', 'KNJ': 'KIA',
            'KMH': 'HYUNDAI', 'KMF': 'HYUNDAI', 'KM1': 'HYUNDAI',

            # European - French
            'VF1': 'RENAULT', 'VF2': 'RENAULT', 'VF3': 'PEUGEOT',
            'VF4': 'PEUGEOT', 'VF6': 'RENAULT', 'VF7': 'CITROEN',
            'VF8': 'MATRA', 'VF9': 'BUGATTI',

            # European - German
            'W0L': 'OPEL', 'W0V': 'OPEL',
            'WA1': 'AUDI', 'WAU': 'AUDI', 'WUA': 'AUDI',
            'WBA': 'BMW', 'WBM': 'BMW', 'WBS': 'BMW', 'WBX': 'BMW',
            'WBY': 'BMW', 'WB1': 'BMW', 'WB2': 'BMW', 'WB3': 'BMW',
            'WD0': 'MERCEDES', 'WD1': 'MERCEDES', 'WD2': 'MERCEDES',
            'WD3': 'MERCEDES', 'WD4': 'MERCEDES', 'WD5': 'MERCEDES',
            'WD8': 'MERCEDES', 'WDA': 'MERCEDES', 'WDB': 'MERCEDES',
            'WDC': 'MERCEDES', 'WDD': 'MERCEDES', 'WDE': 'MERCEDES',
            'WDF': 'MERCEDES', 'WMW': 'MINI',
            'WP0': 'PORSCHE', 'WP1': 'PORSCHE',
            'WVG': 'VOLKSWAGEN', 'WVW': 'VOLKSWAGEN',
            'WV1': 'VOLKSWAGEN', 'WV2': 'VOLKSWAGEN', 'WV3': 'VOLKSWAGEN',

            # European - British
            'SAJ': 'JAGUAR', 'SAD': 'JAGUAR', 'SAF': 'JAGUAR', 'SAX': 'JAGUAR',
            'SCC': 'LOTUS', 'SCF': 'ASTON_MARTIN',
            'SAL': 'LAND_ROVER', 'SAR': 'ROVER', 'SHH': 'LAND_ROVER',
            'SJN': 'NISSAN',  # Nissan UK

            # European - Swedish
            'YV1': 'VOLVO', 'YV2': 'VOLVO', 'YV3': 'VOLVO',
            'YV4': 'VOLVO', 'YV5': 'VOLVO', 'YS3': 'SAAB',

            # European - Italian
            'ZA9': 'LAMBORGHINI', 'ZAM': 'MASERATI', 'ZAR': 'ALFA_ROMEO',
            'ZCF': 'IVECO', 'ZFA': 'FIAT', 'ZFF': 'FERRARI',
            'ZHW': 'LAMBORGHINI', 'ZLA': 'LANCIA',

            # Asian - Mitsubishi (additional)
            'MA3': 'MITSUBISHI', 'MB3': 'MITSUBISHI', 'ML3': 'MITSUBISHI',
            'MMB': 'MITSUBISHI', 'MMC': 'MITSUBISHI', 'MMD': 'MITSUBISHI',
            'MMT': 'MITSUBISHI', 'MZ2': 'MITSUBISHI', 'MZ3': 'MITSUBISHI',

            # Asian - Other
            'LVS': 'FORD', 'LVY': 'VOLVO', 'LVG': 'TOYOTA',
            'L56': 'HYUNDAI', 'L5Y': 'MAZDA',

            # South American
            '9BW': 'VOLKSWAGEN', '9BF': 'FORD', '9BG': 'CHEVY',
            '9BD': 'FIAT', '9BM': 'MERCEDES', '9BN': 'JAGUAR',
            '93H': 'HONDA', '93W': 'PEUGEOT', '93X': 'CITROEN',
            '93Y': 'RENAULT', '94D': 'NISSAN', '9FB': 'RENAULT'
        }

        # Check first 3 characters
        if wmi in wmi_map:
            return wmi_map[wmi]

        # Check first 2 characters for broader matches
        wmi2 = vin[:2].upper()
        wmi1 = vin[0].upper()

        # 2-character fallbacks
        if wmi2 == '1C':
            return 'CHRYSLER'
        elif wmi2 == '1D':
            return 'DODGE'
        elif wmi2 == '1P':
            return 'PLYMOUTH'
        elif wmi2 == '2C':
            return 'CHRYSLER'
        elif wmi2 == '2D':
            return 'DODGE'
        elif wmi2 == '2P':
            return 'PLYMOUTH'
        elif wmi2 == '3C':
            return 'CHRYSLER'
        elif wmi2 == '3D':
            return 'DODGE'
        elif wmi2 == '3P':
            return 'PLYMOUTH'

        # GM fallback for any unmatched 1G prefix
        elif wmi2 == '1G':
            return 'GM'
        elif wmi2 == '2G':
            return 'GM'
        elif wmi2 == '3G':
            return 'GM'

        # INFINITI shares NISSAN VINs but we default to NISSAN
        # (JN prefix already maps to NISSAN which covers INFINITI)

        # Regional fallbacks
        elif wmi1 == 'J':
            # Japanese manufacturer not in map
            return None
        elif wmi1 == 'K':
            # Korean manufacturer not in map
            return None
        elif wmi1 == 'S':
            # British manufacturer not in map
            return None
        elif wmi1 == 'W':
            # German manufacturer not in map
            return None
        elif wmi1 == 'V':
            # French/Spanish manufacturer not in map
            return None
        elif wmi1 == 'Z':
            # Italian manufacturer not in map
            return None

        return None

    def analyze_code(self, code: str) -> Dict:
        """
        Analyze a code to understand its variations

        Returns detailed analysis of the code
        """
        code = code.upper()
        cursor = self.conn.cursor()

        # Get all variations
        cursor.execute('''
            SELECT manufacturer, description
            FROM dtc_definitions
            WHERE code = ?
            ORDER BY manufacturer
        ''', (code,))

        variations = {}
        for mfr, desc in cursor.fetchall():
            if desc not in variations:
                variations[desc] = []
            variations[desc].append(mfr)

        # Group manufacturers by same description
        analysis = {
            'code': code,
            'total_manufacturers': 0,
            'unique_descriptions': len(variations),
            'variations': []
        }

        for desc, manufacturers in variations.items():
            analysis['total_manufacturers'] += len(manufacturers)
            analysis['variations'].append({
                'description': desc,
                'manufacturers': manufacturers,
                'count': len(manufacturers)
            })

        # Sort by most common
        analysis['variations'].sort(key=lambda x: x['count'], reverse=True)

        return analysis

    def search_manufacturer(self, manufacturer: str, keyword: str = None,
                           limit: int = 100) -> List[ManufacturerDTC]:
        """
        Search codes for a specific manufacturer

        Args:
            manufacturer: Manufacturer name
            keyword: Optional search keyword
            limit: Maximum results

        Returns:
            List of DTCs for that manufacturer
        """
        manufacturer = manufacturer.upper()
        cursor = self.conn.cursor()

        if keyword:
            search_term = f'%{keyword}%'
            cursor.execute('''
                SELECT code, description, is_generic
                FROM dtc_definitions
                WHERE manufacturer = ? AND (
                    code LIKE ? OR description LIKE ?
                )
                LIMIT ?
            ''', (manufacturer, search_term, search_term, limit))
        else:
            cursor.execute('''
                SELECT code, description, is_generic
                FROM dtc_definitions
                WHERE manufacturer = ?
                LIMIT ?
            ''', (manufacturer, limit))

        results = []
        for code, desc, is_generic in cursor.fetchall():
            results.append(ManufacturerDTC(
                code=code,
                manufacturer=manufacturer,
                description=desc,
                is_generic=bool(is_generic)
            ))

        return results

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()
        stats = {}

        # Total entries
        cursor.execute('SELECT COUNT(*) FROM dtc_definitions')
        stats['total_entries'] = cursor.fetchone()[0]

        # Unique codes
        cursor.execute('SELECT COUNT(DISTINCT code) FROM dtc_definitions')
        stats['unique_codes'] = cursor.fetchone()[0]

        # Generic vs manufacturer-specific
        cursor.execute('SELECT COUNT(DISTINCT code) FROM dtc_definitions WHERE is_generic = 1')
        stats['generic_codes'] = cursor.fetchone()[0]

        # Codes with multiple definitions
        cursor.execute('''
            SELECT COUNT(*) FROM (
                SELECT code, COUNT(DISTINCT manufacturer) as cnt
                FROM dtc_definitions
                GROUP BY code
                HAVING cnt > 1
            )
        ''')
        stats['codes_with_variations'] = cursor.fetchone()[0]

        # Get manufacturer statistics
        cursor.execute('SELECT * FROM statistics ORDER BY total_codes DESC')
        stats['manufacturers'] = []
        for row in cursor.fetchall():
            stats['manufacturers'].append({
                'name': row[0],
                'total_codes': row[1],
                'unique_codes': row[2]
            })

        return stats

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Example usage
if __name__ == '__main__':
    db = PerfectDTCDatabase()

    # Example 1: Get definition for specific manufacturer
    print("=== Manufacturer-Specific Lookup ===")
    print(f"P1690 for Ford: {db.get_for_manufacturer('P1690', 'FORD')}")
    print(f"P1690 for BMW: {db.get_for_manufacturer('P1690', 'BMW')}")

    # Example 2: Smart lookup with VIN
    print("\n=== Smart Lookup with VIN ===")
    result = db.get_smart('P1690', vin='4JGDA5HB7JB158144')  # Mercedes VIN
    if result['primary']:
        print(f"Best match: {result['primary']}")
        print(f"Total definitions available: {result['total_definitions']}")

    # Example 3: Analyze code variations
    print("\n=== Code Analysis ===")
    analysis = db.analyze_code('P1690')
    print(f"P1690 has {analysis['unique_descriptions']} unique descriptions:")
    for var in analysis['variations'][:3]:
        print(f"  '{var['description'][:40]}...' used by {var['count']} manufacturers")

    db.close()