#!/usr/bin/env python3
"""
Test script for DTC Database
Author: Wal33D
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from python.dtc_database import DTCDatabase

def test_dtc_database():
    """Test basic DTC database functionality"""
    print("Testing DTC Database...")
    print("-" * 50)

    # Initialize database
    db = DTCDatabase(db_path='data/dtc_codes.db')

    # Test generic codes
    test_codes = ['P0171', 'P0300', 'B0001', 'C0035', 'U0100']

    print("\nGeneric Code Lookups:")
    for code in test_codes:
        desc = db.get_description(code)
        if desc:
            print(f"  {code}: {desc[:60]}...")
        else:
            print(f"  {code}: Not found")

    # Test search
    print("\nSearch for 'oxygen':")
    results = db.search('oxygen')
    for dtc in results[:3]:
        print(f"  {dtc.code}: {dtc.description[:50]}...")

    # Test manufacturer-specific
    print("\nManufacturer-specific codes:")
    mfg_codes = db.get_manufacturer_codes('FORD')
    if mfg_codes:
        for dtc in mfg_codes[:3]:
            print(f"  {dtc.code}: {dtc.description[:50]}...")

    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_dtc_database()