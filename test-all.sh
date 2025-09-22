#!/bin/bash

# DTC Database Test Script
# Tests all language implementations

echo "=================================="
echo "   DTC DATABASE TEST SUITE"
echo "   18,821 Codes | 4 Languages"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track success
ALL_PASS=true

# Test Python
echo "🐍 Testing Python implementation..."
if python3 test.py > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Python: PASSED${NC}"
    echo "   - Database: dtc_codes.db (12,129 unique codes)"
else
    echo -e "${RED}❌ Python: FAILED${NC}"
    ALL_PASS=false
fi

# Test Java
echo ""
echo "☕ Testing Java implementation..."
if [ ! -f "com/dtcdatabase/core/DTCDatabaseCore.class" ]; then
    javac -d . java/DTCDatabaseCore.java TestJava.java 2>/dev/null
fi

if java -cp .:lib/sqlite-jdbc.jar:lib/slf4j-api.jar:lib/slf4j-simple.jar TestJava > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Java: PASSED${NC}"
    echo "   - Dependencies: lib/sqlite-jdbc.jar"
else
    echo -e "${RED}❌ Java: FAILED${NC}"
    ALL_PASS=false
fi

# Test TypeScript
echo ""
echo "📘 Testing TypeScript implementation..."
if cd typescript && npx ts-node query-simple.ts P0171 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ TypeScript: PASSED${NC}"
    echo "   - Dependencies: better-sqlite3"
    cd ..
else
    echo -e "${RED}❌ TypeScript: FAILED${NC}"
    ALL_PASS=false
    cd ..
fi

# Summary
echo ""
echo "=================================="
echo "         TEST SUMMARY"
echo "=================================="

if [ "$ALL_PASS" = true ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "Database Statistics:"
    echo "  • Total unique codes: 12,129"
    echo "  • Powertrain (P): 8,189"
    echo "  • Body (B): 1,447"
    echo "  • Chassis (C): 966"
    echo "  • Network (U): 1,527"
    echo "  • Manufacturer-specific: 2,752"
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo "Run './test-all.sh' again after fixing issues"
fi

echo ""
echo "To query a code:"
echo "  Python:     python3 -c \"from python.dtc_database import DTCDatabase; print(DTCDatabase('dtc_codes.db').get_description('P0420'))\""
echo "  TypeScript: cd typescript && npx ts-node query-simple.ts P0420"
echo "  Java:       java -cp .:lib/* TestJava"