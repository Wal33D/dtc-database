#!/usr/bin/env python3
"""
Basic runtime tests for the Python DTC database wrapper.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from python.dtc_database import DTCDatabase


def test_dtc_database():
    print("Testing DTC Database...")
    print("-" * 50)

    db = DTCDatabase(db_path="data/dtc_codes.db")

    # Core generic lookups should resolve and keep expected code/type shape.
    for code in ["P0171", "P0300", "B0001", "C0035", "U0100"]:
        dtc = db.get_dtc(code)
        assert dtc is not None, f"{code} should exist"
        assert dtc.code == code, f"Expected normalized code {code}, got {dtc.code}"
        assert dtc.type == code[0], f"Expected type {code[0]}, got {dtc.type}"
        assert dtc.description, f"{code} should have description"

    # Manufacturer fallback behavior.
    ford_specific = db.get_description("P1690", "FORD")
    assert ford_specific is not None, "FORD-specific P1690 should exist"
    generic_fallback = db.get_description("P0171", "FORD")
    assert generic_fallback is not None, "Generic fallback should exist for P0171"

    # Search should return meaningful rows.
    results = db.search("oxygen", limit=10)
    assert results, "Search for oxygen should return results"
    assert all(item.description for item in results), "Search results should have descriptions"

    # Manufacturer query should return rows for uppercase manufacturer input.
    ford_codes = db.get_manufacturer_codes("FORD", limit=20)
    assert ford_codes, "FORD manufacturer query should return rows"
    assert all(item.manufacturer == "FORD" for item in ford_codes), "Expected FORD rows only"

    # Statistics should match known schema expectations.
    stats = db.get_statistics()
    assert stats["total"] > 0, "Total row count should be > 0"
    assert stats["generic"] > 0, "Generic row count should be > 0"
    assert stats["manufacturer_specific"] > 0, "Manufacturer-specific count should be > 0"
    assert stats["type_P"] > 0, "P-code count should be > 0"
    assert stats["type_B"] > 0, "B-code count should be > 0"
    assert stats["type_C"] > 0, "C-code count should be > 0"
    assert stats["type_U"] > 0, "U-code count should be > 0"

    db.close()
    print("✓ All tests passed!")


if __name__ == "__main__":
    test_dtc_database()
