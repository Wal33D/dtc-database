package com.dtcdatabase;

import android.content.Context;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.util.List;

import static org.junit.Assert.*;

/**
 * Instrumented test for DTC Database functionality.
 * Tests database initialization, code lookup, search, and batch operations.
 */
@RunWith(AndroidJUnit4.class)
public class DTCDatabaseTest {

    private Context appContext;
    private DTCDatabase database;

    @Before
    public void setUp() {
        // Get the application context
        appContext = InstrumentationRegistry.getInstrumentation().getTargetContext();

        // Initialize the database
        database = DTCDatabase.getInstance(appContext);
    }

    /**
     * Test that the database initializes successfully
     */
    @Test
    public void testDatabaseInitialization() {
        assertNotNull("Database instance should not be null", database);
    }

    /**
     * Test code lookup for P0420 (Catalyst System Efficiency Below Threshold)
     */
    @Test
    public void testCodeLookup() {
        String description = database.getDescription("P0420");

        assertNotNull("Description for P0420 should not be null", description);
        assertTrue("Description should contain 'Catalyst'",
                   description.toLowerCase().contains("catalyst"));
    }

    /**
     * Test full DTC object retrieval
     */
    @Test
    public void testGetFullDTC() {
        DTCDatabase.DTC dtc = database.getDTC("P0420");

        assertNotNull("DTC object should not be null", dtc);
        assertEquals("Code should be P0420", "P0420", dtc.code);
        assertNotNull("Description should not be null", dtc.description);
        assertEquals("Type should be P", "P", dtc.type);
    }

    /**
     * Test search functionality with a keyword
     */
    @Test
    public void testSearchFunctionality() {
        List<DTCDatabase.DTC> results = database.searchByKeyword("oxygen");

        assertNotNull("Search results should not be null", results);
        assertFalse("Search results should not be empty", results.isEmpty());

        // Verify that results contain the search term
        boolean foundMatch = false;
        for (DTCDatabase.DTC dtc : results) {
            String description = dtc.description.toLowerCase();
            if (description.contains("oxygen")) {
                foundMatch = true;
                break;
            }
        }
        assertTrue("At least one result should contain 'oxygen'", foundMatch);
    }

    /**
     * Test manufacturer-specific codes
     */
    @Test
    public void testManufacturerCodes() {
        List<DTCDatabase.DTC> fordCodes = database.getManufacturerCodes("ford", 10);

        assertNotNull("Ford codes should not be null", fordCodes);
        // Note: May be empty if no Ford codes in database

        for (DTCDatabase.DTC dtc : fordCodes) {
            assertNotNull("Manufacturer should not be null", dtc.manufacturer);
            assertTrue("Should be manufacturer-specific", dtc.isManufacturerSpecific());
        }
    }

    /**
     * Test batch lookup functionality
     */
    @Test
    public void testBatchLookup() {
        List<String> testCodes = java.util.Arrays.asList("P0420", "P0171", "P0300");
        java.util.Map<String, String> results = database.getDescriptions(testCodes);

        assertNotNull("Batch results should not be null", results);
        assertTrue("Should find at least 2 codes", results.size() >= 2);
        assertTrue("Should contain P0420", results.containsKey("P0420"));
    }

    /**
     * Test invalid code lookup
     */
    @Test
    public void testInvalidCodeLookup() {
        String invalidCode = database.getDescription("INVALID123");
        assertNull("Invalid code should return null", invalidCode);
    }

    /**
     * Test different DTC systems (P, C, B, U)
     */
    @Test
    public void testDifferentSystems() {
        // P - Powertrain
        List<DTCDatabase.DTC> pCodes = database.getCodesByType('P', 5);
        assertNotNull("P codes should not be null", pCodes);
        assertFalse("Should find P codes", pCodes.isEmpty());
        for (DTCDatabase.DTC dtc : pCodes) {
            assertEquals("Type should be P", "P", dtc.type);
        }

        // C - Chassis
        List<DTCDatabase.DTC> cCodes = database.getCodesByType('C', 5);
        assertNotNull("C codes should not be null", cCodes);
        for (DTCDatabase.DTC dtc : cCodes) {
            assertEquals("Type should be C", "C", dtc.type);
        }
    }

    /**
     * Test search with limit
     */
    @Test
    public void testSearchWithLimit() {
        int limit = 10;
        List<DTCDatabase.DTC> results = database.searchByKeyword("sensor", limit);

        assertNotNull("Search results should not be null", results);
        assertTrue("Results should not exceed limit", results.size() <= limit);
    }

    /**
     * Test database performance with multiple queries
     */
    @Test
    public void testDatabasePerformance() {
        long startTime = System.currentTimeMillis();

        // Perform multiple queries
        for (int i = 0; i < 100; i++) {
            database.getDescription("P0420");
        }

        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;

        // 100 queries should complete in reasonable time (under 1 second with caching)
        assertTrue("100 queries should complete in under 1 second", duration < 1000);
    }
}
