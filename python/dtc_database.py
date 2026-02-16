#!/usr/bin/env python3
"""
DTC Database Python Library.

Provides access to the local SQLite dataset in data/dtc_codes.db.
"""

from __future__ import annotations

import os
import sqlite3
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DTC:
    """Diagnostic Trouble Code."""

    code: str
    description: str
    type: str  # P/B/C/U
    manufacturer: Optional[str] = None
    is_generic: bool = False
    locale: str = "en"

    def __str__(self) -> str:
        return f"{self.code} - {self.description}"

    @property
    def type_name(self) -> str:
        """Get human-readable type name."""
        types = {
            "P": "Powertrain",
            "B": "Body",
            "C": "Chassis",
            "U": "Network",
        }
        return types.get(self.type, "Unknown")


class DTCDatabase:
    """DTC Database interface for Python applications."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        locale: str = "en",
        cache_size: int = 100,
    ):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "data", "dtc_codes.db")

        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"Database not found at {db_path}. Please ensure data/dtc_codes.db exists."
            )

        self.db_path = db_path
        self.locale = locale
        self.cache_size = cache_size
        self.cache: OrderedDict[str, str] = OrderedDict()

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def set_locale(self, locale: str) -> None:
        """Set active locale for lookups and clear cache."""
        if locale and locale != self.locale:
            self.locale = locale
            self.cache.clear()

    def create_database(self):
        """Create database from source files using the current schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dtc_definitions (
                code TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                description TEXT NOT NULL,
                type TEXT NOT NULL,
                locale TEXT NOT NULL DEFAULT 'en',
                is_generic BOOLEAN DEFAULT 0,
                source_file TEXT,
                PRIMARY KEY (code, manufacturer, locale)
            )
            """
        )

        self._load_from_source_files()
        self.conn.commit()

    def _load_from_source_files(self):
        """Load codes from text files in data/source-data."""
        source_dir = Path(__file__).parent.parent / "data" / "source-data"
        if not self.conn:
            raise RuntimeError("Database connection not established")

        cursor = self.conn.cursor()

        for file_path in source_dir.glob("*.txt"):
            file_name = file_path.stem

            if file_name in {"p_codes", "b_codes", "c_codes", "u_codes"}:
                manufacturer = "GENERIC"
                is_generic = 1
            else:
                manufacturer = file_name.replace("_codes", "").upper()
                is_generic = 0

            with open(file_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if " - " not in line:
                        continue

                    code, desc = line.split(" - ", 1)
                    code = code.strip().upper()
                    desc = desc.strip()

                    if len(code) != 5 or code[0] not in "PBCU":
                        continue

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO dtc_definitions
                        (code, manufacturer, description, type, locale, is_generic, source_file)
                        VALUES (?, ?, ?, ?, 'en', ?, ?)
                        """,
                        (code, manufacturer, desc, code[0], is_generic, file_name),
                    )

    def _normalize_code(self, code: str) -> str:
        return code.upper().strip()

    def _normalize_manufacturer(self, manufacturer: Optional[str]) -> Optional[str]:
        if manufacturer is None:
            return None
        cleaned = manufacturer.strip().upper()
        return cleaned or None

    def _cache_get(self, key: str) -> Optional[str]:
        if key not in self.cache:
            return None
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def _cache_set(self, key: str, value: str) -> None:
        if key in self.cache:
            self.cache.pop(key)
        self.cache[key] = value
        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)

    def _row_to_dtc(self, row: sqlite3.Row) -> DTC:
        manufacturer = row["manufacturer"]
        is_generic = bool(row["is_generic"]) or manufacturer == "GENERIC"
        normalized_manufacturer: Optional[str] = None if manufacturer == "GENERIC" else manufacturer

        return DTC(
            code=row["code"],
            description=row["description"],
            type=row["type"],
            manufacturer=normalized_manufacturer,
            is_generic=is_generic,
            locale=row["locale"],
        )

    def get_description(self, code: str, manufacturer: Optional[str] = None) -> Optional[str]:
        """
        Get description for a single DTC code.

        Args:
            code: DTC code (e.g., 'P0171')
            manufacturer: Optional manufacturer context (e.g., 'FORD')

        Returns:
            Description string or None if not found.
        """
        normalized_code = self._normalize_code(code)
        normalized_manufacturer = self._normalize_manufacturer(manufacturer)
        cache_key = f"{normalized_code}:{normalized_manufacturer or 'GENERIC'}:{self.locale}"

        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        dtc = self.get_dtc(normalized_code, normalized_manufacturer)
        if not dtc:
            return None

        self._cache_set(cache_key, dtc.description)
        return dtc.description

    def get_dtc(self, code: str, manufacturer: Optional[str] = None) -> Optional[DTC]:
        """
        Get complete DTC information.

        Args:
            code: DTC code.
            manufacturer: Optional manufacturer context. If provided, lookup
                tries that manufacturer first, then falls back to generic.

        Returns:
            DTC object or None if not found.
        """
        if not self.conn:
            return None

        normalized_code = self._normalize_code(code)
        normalized_manufacturer = self._normalize_manufacturer(manufacturer)
        cursor = self.conn.cursor()

        if normalized_manufacturer:
            cursor.execute(
                """
                SELECT code, description, type, manufacturer, is_generic, locale
                FROM dtc_definitions
                WHERE code = ? AND manufacturer = ? AND locale = ?
                LIMIT 1
                """,
                (normalized_code, normalized_manufacturer, self.locale),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_dtc(row)

            cursor.execute(
                """
                SELECT code, description, type, manufacturer, is_generic, locale
                FROM dtc_definitions
                WHERE code = ? AND manufacturer = 'GENERIC' AND locale = ?
                LIMIT 1
                """,
                (normalized_code, self.locale),
            )
            row = cursor.fetchone()
            return self._row_to_dtc(row) if row else None

        cursor.execute(
            """
            SELECT code, description, type, manufacturer, is_generic, locale
            FROM dtc_definitions
            WHERE code = ? AND locale = ?
            ORDER BY is_generic DESC
            LIMIT 1
            """,
            (normalized_code, self.locale),
        )
        row = cursor.fetchone()
        return self._row_to_dtc(row) if row else None

    def batch_lookup(self, codes: List[str]) -> Dict[str, str]:
        """
        Look up multiple codes at once.

        Args:
            codes: List of DTC codes.

        Returns:
            Dictionary mapping uppercase codes to descriptions.
        """
        results: Dict[str, str] = {}
        for code in codes:
            normalized_code = self._normalize_code(code)
            desc = self.get_description(normalized_code)
            if desc:
                results[normalized_code] = desc
        return results

    def search(self, keyword: str, limit: int = 50) -> List[DTC]:
        """
        Search codes by keyword in code or description.

        Args:
            keyword: Search term.
            limit: Maximum results.

        Returns:
            List of matching DTCs.
        """
        if not self.conn or not keyword:
            return []

        cursor = self.conn.cursor()
        search_term = f"%{keyword}%"
        cursor.execute(
            """
            SELECT code, description, type, manufacturer, is_generic, locale
            FROM dtc_definitions
            WHERE (code LIKE ? OR description LIKE ?) AND locale = ?
            ORDER BY is_generic DESC, code ASC
            LIMIT ?
            """,
            (search_term, search_term, self.locale, limit),
        )

        return [self._row_to_dtc(row) for row in cursor.fetchall()]

    def get_by_type(self, code_type: str, limit: int = 100) -> List[DTC]:
        """
        Get codes by type (P/B/C/U).

        Args:
            code_type: Single-character type.
            limit: Maximum results.

        Returns:
            List of DTCs of that type.
        """
        if not self.conn:
            return []

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT code, description, type, manufacturer, is_generic, locale
            FROM dtc_definitions
            WHERE type = ? AND locale = ?
            ORDER BY is_generic DESC, code ASC
            LIMIT ?
            """,
            (code_type.upper(), self.locale, limit),
        )
        return [self._row_to_dtc(row) for row in cursor.fetchall()]

    def get_manufacturer_codes(self, manufacturer: str, limit: int = 200) -> List[DTC]:
        """
        Get manufacturer-specific codes.

        Args:
            manufacturer: Manufacturer name.
            limit: Maximum results.

        Returns:
            List of manufacturer-specific DTCs.
        """
        if not self.conn:
            return []

        normalized_manufacturer = self._normalize_manufacturer(manufacturer)
        if not normalized_manufacturer:
            return []

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT code, description, type, manufacturer, is_generic, locale
            FROM dtc_definitions
            WHERE manufacturer = ? AND locale = ?
            ORDER BY code ASC
            LIMIT ?
            """,
            (normalized_manufacturer, self.locale, limit),
        )
        return [self._row_to_dtc(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, int]:
        """
        Get database statistics.

        Returns:
            Dictionary with counts by type and total.
        """
        if not self.conn:
            return {}

        cursor = self.conn.cursor()
        stats: Dict[str, int] = {}

        cursor.execute(
            "SELECT COUNT(*) FROM dtc_definitions WHERE locale = ?",
            (self.locale,),
        )
        stats["total"] = int(cursor.fetchone()[0])

        cursor.execute(
            "SELECT COUNT(DISTINCT code) FROM dtc_definitions WHERE locale = ?",
            (self.locale,),
        )
        stats["unique_codes"] = int(cursor.fetchone()[0])

        cursor.execute(
            "SELECT COUNT(*) FROM dtc_definitions WHERE is_generic = 1 AND locale = ?",
            (self.locale,),
        )
        generic = int(cursor.fetchone()[0])
        stats["generic"] = generic
        stats["generic_codes"] = generic

        manufacturer_specific = stats["total"] - generic
        stats["manufacturer_specific"] = manufacturer_specific
        stats["manufacturer_codes"] = manufacturer_specific

        cursor.execute(
            """
            SELECT COUNT(DISTINCT manufacturer)
            FROM dtc_definitions
            WHERE manufacturer != 'GENERIC' AND locale = ?
            """,
            (self.locale,),
        )
        stats["manufacturers"] = int(cursor.fetchone()[0])

        for code_type in ["P", "B", "C", "U"]:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dtc_definitions
                WHERE type = ? AND locale = ?
                """,
                (code_type, self.locale),
            )
            stats[f"type_{code_type}"] = int(cursor.fetchone()[0])

        return stats

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


if __name__ == "__main__":
    db = DTCDatabase()

    print(db.get_description("P0171"))

    results = db.search("oxygen sensor")
    for dtc in results[:5]:
        print(dtc)

    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    print(f"Total rows: {stats['total']}")
    print(f"Unique codes: {stats['unique_codes']}")
    print(f"Generic rows: {stats['generic']}")
    print(f"Manufacturer-specific rows: {stats['manufacturer_specific']}")
    print(f"Powertrain: {stats['type_P']}")
    print(f"Body: {stats['type_B']}")
    print(f"Chassis: {stats['type_C']}")
    print(f"Network: {stats['type_U']}")

    db.close()
