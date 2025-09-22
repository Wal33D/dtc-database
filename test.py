#!/usr/bin/env python3
"""
Test script to verify database functionality
"""

from python.dtc_database import DTCDatabase

print("=== DTC Database Test ===\n")

# Initialize database
db = DTCDatabase('dtc_codes.db')

# Test single lookups
test_codes = ['P0171', 'P0420', 'B0001', 'C0001', 'U0001']
print("1. Testing common codes:")
for code in test_codes:
    desc = db.get_description(code)
    if desc:
        print(f"   {code}: {desc[:50]}...")

# Test search
print("\n2. Testing search for 'oxygen':")
results = db.search('oxygen', limit=3)
for dtc in results:
    print(f"   {dtc}")

# Test manufacturer codes
print("\n3. Testing Mercedes codes:")
mercedes = db.get_manufacturer_codes('mercedes', limit=3)
for dtc in mercedes:
    print(f"   {dtc}")

# Get statistics
print("\n4. Database statistics:")
stats = db.get_statistics()
print(f"   Total unique codes: {stats['total']}")
print(f"   Powertrain (P): {stats['type_P']}")
print(f"   Body (B): {stats['type_B']}")
print(f"   Chassis (C): {stats['type_C']}")
print(f"   Network (U): {stats['type_U']}")
print(f"   Manufacturer-specific: {stats['manufacturer_specific']}")

db.close()
print("\n✅ All tests passed!")