package com.dtcdatabase;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * DTC Database Helper for Android
 *
 * Provides access to 18,805 OBD-II diagnostic code definitions including
 * generic SAE J2012 standard codes and manufacturer-specific definitions.
 *
 * Features:
 * - 9,415 generic OBD-II codes
 * - 9,390 manufacturer-specific definitions across 33 manufacturers
 * - Fast lookup with built-in caching
 * - Full-text search capability
 * - Thread-safe singleton pattern
 * - Works completely offline (no network required)
 *
 * Example usage:
 * <pre>
 * DTCDatabase db = DTCDatabase.getInstance(context);
 *
 * // Single code lookup
 * String description = db.getDescription("P0420");
 *
 * // Search for codes
 * List&lt;DTC&gt; results = db.searchByKeyword("oxygen");
 *
 * // Get manufacturer-specific codes
 * List&lt;DTC&gt; fordCodes = db.getManufacturerCodes("FORD");
 * </pre>
 *
 * @author Wal33D
 * @email aquataze@yahoo.com
 */
public class DTCDatabase extends SQLiteOpenHelper {
    private static final String DATABASE_NAME = "dtc_codes.db";
    private static final int DATABASE_VERSION = 1;
    private static final String TABLE_NAME = "dtc_definitions";

    // Column names
    private static final String COL_CODE = "code";
    private static final String COL_DESCRIPTION = "description";
    private static final String COL_TYPE = "type";
    private static final String COL_MANUFACTURER = "manufacturer";
    private static final String COL_LOCALE = "locale";
    private static final String COL_IS_GENERIC = "is_generic";

    private Context context;
    private static DTCDatabase instance;
    private String databasePath;
    private String currentLocale = "en"; // Default to English

    // Cache for frequently accessed codes (limit to 100 entries)
    private Map<String, String> descriptionCache = new HashMap<>();
    private static final int CACHE_MAX_SIZE = 100;

    /**
     * Get singleton instance of DTCDatabase
     *
     * @param context Android context (will use application context)
     * @return DTCDatabase instance
     */
    public static synchronized DTCDatabase getInstance(Context context) {
        if (instance == null) {
            instance = new DTCDatabase(context.getApplicationContext());
        }
        return instance;
    }

    private DTCDatabase(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
        this.context = context;
        this.databasePath = context.getDatabasePath(DATABASE_NAME).getPath();

        // Copy database from assets on first run
        if (!checkDatabase()) {
            copyDatabaseFromAssets();
        }
    }

    /**
     * Check if database file exists
     */
    private boolean checkDatabase() {
        File dbFile = new File(databasePath);
        return dbFile.exists();
    }

    /**
     * Copy database from assets to app's database directory
     */
    private void copyDatabaseFromAssets() {
        try {
            InputStream inputStream = context.getAssets().open(DATABASE_NAME);

            // Ensure parent directory exists
            File dbFile = new File(databasePath);
            dbFile.getParentFile().mkdirs();

            OutputStream outputStream = new FileOutputStream(databasePath);

            byte[] buffer = new byte[8192];
            int length;
            while ((length = inputStream.read(buffer)) > 0) {
                outputStream.write(buffer, 0, length);
            }

            outputStream.flush();
            outputStream.close();
            inputStream.close();
        } catch (IOException e) {
            throw new RuntimeException("Failed to copy database from assets", e);
        }
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        // Database is copied from assets, so onCreate is not typically called
        // But we include the schema for reference
        String createTable = "CREATE TABLE IF NOT EXISTS " + TABLE_NAME + " (" +
                COL_CODE + " TEXT NOT NULL, " +
                COL_MANUFACTURER + " TEXT NOT NULL, " +
                COL_DESCRIPTION + " TEXT NOT NULL, " +
                COL_TYPE + " TEXT NOT NULL, " +
                COL_LOCALE + " TEXT NOT NULL DEFAULT 'en', " +
                COL_IS_GENERIC + " BOOLEAN DEFAULT 0, " +
                "PRIMARY KEY (" + COL_CODE + ", " + COL_MANUFACTURER + ", " + COL_LOCALE + "))";
        db.execSQL(createTable);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        // Handle database upgrades if needed in future versions
        if (newVersion > oldVersion) {
            copyDatabaseFromAssets();
        }
    }

    /**
     * Get description for a DTC code (generic codes only, current locale)
     *
     * @param code The DTC code (e.g., "P0420", case-insensitive)
     * @return Description or null if not found
     */
    public String getDescription(String code) {
        return getDescription(code, null);
    }

    /**
     * Get description for a DTC code with manufacturer context
     * Falls back to generic if manufacturer-specific not found
     *
     * @param code The DTC code (e.g., "P0420", case-insensitive)
     * @param manufacturer Manufacturer name (e.g., "FORD", null for generic only)
     * @return Description or null if not found
     */
    public String getDescription(String code, String manufacturer) {
        if (code == null || code.isEmpty()) {
            return null;
        }

        String upperCode = code.toUpperCase();
        String cacheKey = upperCode + ":" + (manufacturer != null ? manufacturer : "GENERIC") + ":" + currentLocale;

        // Check cache first
        if (descriptionCache.containsKey(cacheKey)) {
            return descriptionCache.get(cacheKey);
        }

        SQLiteDatabase db = getReadableDatabase();
        String description = null;

        // Try manufacturer-specific first if provided
        if (manufacturer != null && !manufacturer.isEmpty()) {
            String query = "SELECT " + COL_DESCRIPTION + " FROM " + TABLE_NAME +
                          " WHERE " + COL_CODE + " = ? AND " + COL_MANUFACTURER + " = ? AND " + COL_LOCALE + " = ?";
            Cursor cursor = db.rawQuery(query, new String[]{upperCode, manufacturer.toUpperCase(), currentLocale});

            if (cursor.moveToFirst()) {
                description = cursor.getString(0);
            }
            cursor.close();
        }

        // Fall back to generic code if no manufacturer-specific found
        if (description == null) {
            String query = "SELECT " + COL_DESCRIPTION + " FROM " + TABLE_NAME +
                          " WHERE " + COL_CODE + " = ? AND " + COL_MANUFACTURER + " = 'GENERIC' AND " + COL_LOCALE + " = ?";
            Cursor cursor = db.rawQuery(query, new String[]{upperCode, currentLocale});

            if (cursor.moveToFirst()) {
                description = cursor.getString(0);
            }
            cursor.close();
        }

        // Add to cache if found and cache not full
        if (description != null && descriptionCache.size() < CACHE_MAX_SIZE) {
            descriptionCache.put(cacheKey, description);
        }

        return description;
    }

    /**
     * Get full DTC object with all information (generic only)
     *
     * @param code The DTC code
     * @return DTC object or null if not found
     */
    public DTC getDTC(String code) {
        return getDTC(code, null);
    }

    /**
     * Get full DTC object with manufacturer context
     * Falls back to generic if manufacturer-specific not found
     *
     * @param code The DTC code
     * @param manufacturer Manufacturer name (null for generic only)
     * @return DTC object or null if not found
     */
    public DTC getDTC(String code, String manufacturer) {
        if (code == null || code.isEmpty()) {
            return null;
        }

        SQLiteDatabase db = getReadableDatabase();
        DTC dtc = null;

        // Try manufacturer-specific first if provided
        if (manufacturer != null && !manufacturer.isEmpty()) {
            String query = "SELECT * FROM " + TABLE_NAME +
                          " WHERE " + COL_CODE + " = ? AND " + COL_MANUFACTURER + " = ? AND " + COL_LOCALE + " = ?";
            Cursor cursor = db.rawQuery(query, new String[]{code.toUpperCase(), manufacturer.toUpperCase(), currentLocale});

            if (cursor.moveToFirst()) {
                dtc = new DTC(
                    cursor.getString(cursor.getColumnIndexOrThrow(COL_CODE)),
                    cursor.getString(cursor.getColumnIndexOrThrow(COL_DESCRIPTION)),
                    cursor.getString(cursor.getColumnIndexOrThrow(COL_TYPE)),
                    cursor.getString(cursor.getColumnIndexOrThrow(COL_MANUFACTURER))
                );
            }
            cursor.close();
        }

        // Fall back to generic if no manufacturer-specific found
        if (dtc == null) {
            String query = "SELECT * FROM " + TABLE_NAME +
                          " WHERE " + COL_CODE + " = ? AND " + COL_MANUFACTURER + " = 'GENERIC' AND " + COL_LOCALE + " = ?";
            Cursor cursor = db.rawQuery(query, new String[]{code.toUpperCase(), currentLocale});

            if (cursor.moveToFirst()) {
                dtc = new DTC(
                    cursor.getString(cursor.getColumnIndexOrThrow(COL_CODE)),
                    cursor.getString(cursor.getColumnIndexOrThrow(COL_DESCRIPTION)),
                    cursor.getString(cursor.getColumnIndexOrThrow(COL_TYPE)),
                    cursor.getString(cursor.getColumnIndexOrThrow(COL_MANUFACTURER))
                );
            }
            cursor.close();
        }

        return dtc;
    }

    /**
     * Get multiple codes at once (batch lookup)
     *
     * @param codes List of DTC codes
     * @return Map of code to description (uppercase codes)
     */
    public Map<String, String> getDescriptions(List<String> codes) {
        Map<String, String> results = new HashMap<>();

        if (codes == null || codes.isEmpty()) {
            return results;
        }

        for (String code : codes) {
            String desc = getDescription(code);
            if (desc != null) {
                results.put(code.toUpperCase(), desc);
            }
        }

        return results;
    }

    /**
     * Search codes by keyword in code or description
     *
     * @param keyword Search term (case-insensitive)
     * @return List of matching DTCs (limited to 50 results)
     */
    public List<DTC> searchByKeyword(String keyword) {
        return searchByKeyword(keyword, 50);
    }

    /**
     * Search codes by keyword with custom limit
     * Searches in current locale only
     *
     * @param keyword Search term (case-insensitive)
     * @param limit Maximum number of results
     * @return List of matching DTCs
     */
    public List<DTC> searchByKeyword(String keyword, int limit) {
        List<DTC> results = new ArrayList<>();

        if (keyword == null || keyword.isEmpty()) {
            return results;
        }

        SQLiteDatabase db = getReadableDatabase();
        String query = "SELECT * FROM " + TABLE_NAME +
                      " WHERE (" + COL_DESCRIPTION + " LIKE ? OR " + COL_CODE + " LIKE ?) " +
                      " AND " + COL_LOCALE + " = ? LIMIT ?";
        String searchTerm = "%" + keyword + "%";
        Cursor cursor = db.rawQuery(query, new String[]{searchTerm, searchTerm, currentLocale, String.valueOf(limit)});

        while (cursor.moveToNext()) {
            results.add(new DTC(
                cursor.getString(cursor.getColumnIndexOrThrow(COL_CODE)),
                cursor.getString(cursor.getColumnIndexOrThrow(COL_DESCRIPTION)),
                cursor.getString(cursor.getColumnIndexOrThrow(COL_TYPE)),
                cursor.getString(cursor.getColumnIndexOrThrow(COL_MANUFACTURER))
            ));
        }
        cursor.close();

        return results;
    }

    /**
     * Get codes by type (P, B, C, U)
     *
     * @param type Code type character ('P', 'B', 'C', or 'U')
     * @return List of codes (limited to 100 results)
     */
    public List<DTC> getCodesByType(char type) {
        return getCodesByType(type, 100);
    }

    /**
     * Get codes by type with custom limit
     * Returns codes in current locale only
     *
     * @param type Code type character ('P', 'B', 'C', or 'U')
     * @param limit Maximum number of results
     * @return List of codes
     */
    public List<DTC> getCodesByType(char type, int limit) {
        List<DTC> results = new ArrayList<>();

        SQLiteDatabase db = getReadableDatabase();
        String query = "SELECT * FROM " + TABLE_NAME +
                      " WHERE " + COL_TYPE + " = ? AND " + COL_LOCALE + " = ? LIMIT ?";
        Cursor cursor = db.rawQuery(query, new String[]{String.valueOf(type), currentLocale, String.valueOf(limit)});

        while (cursor.moveToNext()) {
            results.add(new DTC(
                cursor.getString(cursor.getColumnIndexOrThrow(COL_CODE)),
                cursor.getString(cursor.getColumnIndexOrThrow(COL_DESCRIPTION)),
                cursor.getString(cursor.getColumnIndexOrThrow(COL_TYPE)),
                cursor.getString(cursor.getColumnIndexOrThrow(COL_MANUFACTURER))
            ));
        }
        cursor.close();

        return results;
    }

    /**
     * Get manufacturer-specific codes
     *
     * @param manufacturer Manufacturer name (e.g., "FORD", "TOYOTA", case-insensitive)
     * @return List of manufacturer codes (limited to 200 results)
     */
    public List<DTC> getManufacturerCodes(String manufacturer) {
        return getManufacturerCodes(manufacturer, 200);
    }

    /**
     * Get manufacturer-specific codes with custom limit
     * Returns codes in current locale only
     *
     * @param manufacturer Manufacturer name (case-insensitive)
     * @param limit Maximum number of results
     * @return List of manufacturer codes
     */
    public List<DTC> getManufacturerCodes(String manufacturer, int limit) {
        List<DTC> results = new ArrayList<>();

        if (manufacturer == null || manufacturer.isEmpty()) {
            return results;
        }

        SQLiteDatabase db = getReadableDatabase();
        String query = "SELECT * FROM " + TABLE_NAME +
                      " WHERE " + COL_MANUFACTURER + " = ? AND " + COL_LOCALE + " = ? LIMIT ?";
        Cursor cursor = db.rawQuery(query, new String[]{manufacturer.toUpperCase(), currentLocale, String.valueOf(limit)});

        while (cursor.moveToNext()) {
            results.add(new DTC(
                cursor.getString(cursor.getColumnIndexOrThrow(COL_CODE)),
                cursor.getString(cursor.getColumnIndexOrThrow(COL_DESCRIPTION)),
                cursor.getString(cursor.getColumnIndexOrThrow(COL_TYPE)),
                cursor.getString(cursor.getColumnIndexOrThrow(COL_MANUFACTURER))
            ));
        }
        cursor.close();

        return results;
    }

    /**
     * Get database statistics
     *
     * @return Map with statistics (total_codes, generic_codes, manufacturer_codes)
     */
    public Map<String, Integer> getStatistics() {
        Map<String, Integer> stats = new HashMap<>();
        SQLiteDatabase db = getReadableDatabase();

        // Total rows for the active locale.
        Cursor cursor = db.rawQuery(
            "SELECT COUNT(*) FROM " + TABLE_NAME + " WHERE " + COL_LOCALE + " = ?",
            new String[]{currentLocale}
        );
        if (cursor.moveToFirst()) {
            stats.put("total_codes", cursor.getInt(0));
        }
        cursor.close();

        // Generic rows are stored with manufacturer='GENERIC'.
        cursor = db.rawQuery(
            "SELECT COUNT(*) FROM " + TABLE_NAME +
                " WHERE " + COL_MANUFACTURER + " = 'GENERIC' AND " + COL_LOCALE + " = ?",
            new String[]{currentLocale}
        );
        if (cursor.moveToFirst()) {
            stats.put("generic_codes", cursor.getInt(0));
        }
        cursor.close();

        // Manufacturer-specific rows exclude GENERIC.
        cursor = db.rawQuery(
            "SELECT COUNT(*) FROM " + TABLE_NAME +
                " WHERE " + COL_MANUFACTURER + " != 'GENERIC' AND " + COL_LOCALE + " = ?",
            new String[]{currentLocale}
        );
        if (cursor.moveToFirst()) {
            stats.put("manufacturer_codes", cursor.getInt(0));
        }
        cursor.close();

        // Count by type
        for (char type : new char[]{'P', 'B', 'C', 'U'}) {
            cursor = db.rawQuery(
                "SELECT COUNT(*) FROM " + TABLE_NAME +
                    " WHERE " + COL_TYPE + " = ? AND " + COL_LOCALE + " = ?",
                new String[]{String.valueOf(type), currentLocale}
            );
            if (cursor.moveToFirst()) {
                stats.put(type + "_codes", cursor.getInt(0));
            }
            cursor.close();
        }

        return stats;
    }

    /**
     * Clear the description cache
     */
    public void clearCache() {
        descriptionCache.clear();
    }

    /**
     * Set the current locale for code lookups
     * Clears the cache when locale changes
     *
     * @param locale Locale code (e.g., "en", "es", "de")
     */
    public void setLocale(String locale) {
        if (locale != null && !locale.equals(this.currentLocale)) {
            this.currentLocale = locale;
            clearCache();
        }
    }

    /**
     * Get the current locale
     *
     * @return Current locale code
     */
    public String getLocale() {
        return currentLocale;
    }

    /**
     * Get code type (P/B/C/U) from code string
     *
     * @param code DTC code
     * @return Code type character or '?' if invalid
     */
    public static char getCodeType(String code) {
        if (code != null && code.length() > 0) {
            return Character.toUpperCase(code.charAt(0));
        }
        return '?';
    }

    /**
     * Format code for display with type name
     *
     * @param code DTC code
     * @return Formatted string like "P0420 (Powertrain)"
     */
    public static String formatCodeWithType(String code) {
        char type = getCodeType(code);
        String typeName;
        switch (type) {
            case 'P': typeName = "Powertrain"; break;
            case 'B': typeName = "Body"; break;
            case 'C': typeName = "Chassis"; break;
            case 'U': typeName = "Network"; break;
            default: typeName = "Unknown"; break;
        }
        return code + " (" + typeName + ")";
    }

    /**
     * DTC Data Class
     *
     * Represents a single diagnostic trouble code with all its information.
     */
    public static class DTC {
        public final String code;
        public final String description;
        public final String type;
        public final String manufacturer;

        public DTC(String code, String description, String type, String manufacturer) {
            this.code = code;
            this.description = description;
            this.type = type;
            this.manufacturer = manufacturer;
        }

        /**
         * Get human-readable type name
         */
        public String getTypeName() {
            if (type == null || type.isEmpty()) {
                return "Unknown";
            }
            switch (type.charAt(0)) {
                case 'P': return "Powertrain";
                case 'B': return "Body";
                case 'C': return "Chassis";
                case 'U': return "Network";
                default: return "Unknown";
            }
        }

        /**
         * Check if this is a generic OBD-II code
         */
        public boolean isGeneric() {
            return manufacturer == null
                || manufacturer.isEmpty()
                || "GENERIC".equalsIgnoreCase(manufacturer);
        }

        /**
         * Check if this is a manufacturer-specific code
         */
        public boolean isManufacturerSpecific() {
            return !isGeneric();
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append(code).append(" - ").append(description);
            if (!isGeneric()) {
                sb.append(" [").append(manufacturer.toUpperCase()).append("]");
            }
            return sb.toString();
        }
    }
}
