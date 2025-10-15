#!/usr/bin/env python3
"""
Test script to verify dtc_codes.db schema and functionality
Tests the new schema with type and locale columns
"""

import sqlite3
import sys

def test_database_schema():
    """Test that the database schema matches expectations"""
    print("=== Testing Database Schema ===\n")

    db_path = 'data/dtc_codes.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Test 1: Check table structure
    print("Test 1: Checking table structure...")
    cursor.execute("PRAGMA table_info(dtc_definitions)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    expected_columns = {
        'code': 'TEXT',
        'manufacturer': 'TEXT',
        'description': 'TEXT',
        'type': 'TEXT',
        'locale': 'TEXT',
        'is_generic': 'BOOLEAN',
        'source_file': 'TEXT'
    }

    for col_name, col_type in expected_columns.items():
        if col_name not in columns:
            print(f"  ✗ FAIL: Missing column '{col_name}'")
            return False
        elif columns[col_name] != col_type:
            print(f"  ✗ FAIL: Column '{col_name}' has wrong type. Expected '{col_type}', got '{columns[col_name]}'")
            return False

    print("  ✓ PASS: All columns present with correct types")

    # Test 2: Check indexes
    print("\nTest 2: Checking indexes...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='dtc_definitions'")
    indexes = [row[0] for row in cursor.fetchall()]

    expected_indexes = ['idx_code', 'idx_manufacturer', 'idx_generic', 'idx_locale', 'idx_type']
    for idx in expected_indexes:
        if idx not in indexes:
            print(f"  ✗ FAIL: Missing index '{idx}'")
            return False

    print("  ✓ PASS: All indexes present")

    # Test 3: Check data integrity
    print("\nTest 3: Checking data integrity...")

    # Check that all codes have type field populated
    cursor.execute("SELECT COUNT(*) FROM dtc_definitions WHERE type IS NULL OR type = ''")
    null_types = cursor.fetchone()[0]
    if null_types > 0:
        print(f"  ✗ FAIL: Found {null_types} rows with null/empty type")
        return False
    print("  ✓ PASS: All rows have type field populated")

    # Check that all codes have valid types (P, B, C, or U)
    cursor.execute("SELECT COUNT(*) FROM dtc_definitions WHERE type NOT IN ('P', 'B', 'C', 'U')")
    invalid_types = cursor.fetchone()[0]
    if invalid_types > 0:
        print(f"  ✗ FAIL: Found {invalid_types} rows with invalid type")
        return False
    print("  ✓ PASS: All rows have valid type (P/B/C/U)")

    # Check that all codes have locale field populated
    cursor.execute("SELECT COUNT(*) FROM dtc_definitions WHERE locale IS NULL OR locale = ''")
    null_locales = cursor.fetchone()[0]
    if null_locales > 0:
        print(f"  ✗ FAIL: Found {null_locales} rows with null/empty locale")
        return False
    print("  ✓ PASS: All rows have locale field populated")

    # Check that default locale is 'en'
    cursor.execute("SELECT DISTINCT locale FROM dtc_definitions")
    locales = [row[0] for row in cursor.fetchall()]
    if 'en' not in locales:
        print("  ✗ FAIL: Default locale 'en' not found")
        return False
    print(f"  ✓ PASS: Default locale 'en' present (total locales: {', '.join(locales)})")

    # Test 4: Query tests
    print("\nTest 4: Testing queries...")

    # Test generic code lookup
    cursor.execute("""
        SELECT code, description, type, manufacturer, locale
        FROM dtc_definitions
        WHERE code = 'P0420' AND manufacturer = 'GENERIC' AND locale = 'en'
    """)
    p0420 = cursor.fetchone()
    if not p0420:
        print("  ✗ FAIL: Could not find P0420 (generic)")
        return False
    print(f"  ✓ PASS: Generic lookup works - P0420: {p0420[1][:50]}...")

    # Test manufacturer-specific lookup
    cursor.execute("""
        SELECT code, description, type, manufacturer, locale
        FROM dtc_definitions
        WHERE code = 'P1690' AND manufacturer = 'FORD' AND locale = 'en'
    """)
    p1690_ford = cursor.fetchone()
    if not p1690_ford:
        print("  ✗ FAIL: Could not find P1690 (Ford)")
        return False
    print(f"  ✓ PASS: Manufacturer lookup works - P1690 (Ford): {p1690_ford[1][:50]}...")

    # Test type filtering
    cursor.execute("""
        SELECT COUNT(*) FROM dtc_definitions
        WHERE type = 'B' AND locale = 'en'
    """)
    b_count = cursor.fetchone()[0]
    print(f"  ✓ PASS: Type filtering works - Found {b_count} B-codes")

    # Test 5: Statistics
    print("\nTest 5: Database statistics...")

    cursor.execute("SELECT COUNT(*) FROM dtc_definitions")
    total = cursor.fetchone()[0]
    print(f"  Total entries: {total}")

    cursor.execute("SELECT COUNT(DISTINCT code) FROM dtc_definitions WHERE locale = 'en'")
    unique_codes = cursor.fetchone()[0]
    print(f"  Unique codes (en): {unique_codes}")

    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM dtc_definitions
        WHERE locale = 'en'
        GROUP BY type
        ORDER BY type
    """)
    for type_char, count in cursor.fetchall():
        print(f"  {type_char}-codes: {count}")

    cursor.execute("""
        SELECT COUNT(DISTINCT manufacturer)
        FROM dtc_definitions
        WHERE manufacturer != 'GENERIC'
    """)
    mfr_count = cursor.fetchone()[0]
    print(f"  Manufacturers: {mfr_count}")

    conn.close()

    print("\n=== All Tests Passed! ===")
    return True

if __name__ == '__main__':
    success = test_database_schema()
    sys.exit(0 if success else 1)
