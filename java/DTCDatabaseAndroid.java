package com.dtcdatabase;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Legacy Android helper kept for backward compatibility.
 * Prefer android/dtc-database-android/src/main/java/com/dtcdatabase/DTCDatabase.java.
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

    private Context context;
    private static DTCDatabase instance;

    // Cache for frequently accessed codes
    private Map<String, String> cacheMap = new HashMap<>();

    public static synchronized DTCDatabase getInstance(Context context) {
        if (instance == null) {
            instance = new DTCDatabase(context.getApplicationContext());
        }
        return instance;
    }

    private DTCDatabase(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
        this.context = context;
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        String createTable = "CREATE TABLE " + TABLE_NAME + " (" +
                COL_CODE + " TEXT PRIMARY KEY, " +
                COL_DESCRIPTION + " TEXT NOT NULL, " +
                COL_TYPE + " TEXT, " +
                COL_MANUFACTURER + " TEXT)";
        db.execSQL(createTable);

        // Load initial data
        loadDatabaseFromAssets(db);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_NAME);
        onCreate(db);
    }

    /**
     * Get description for a DTC code
     * @param code The DTC code (e.g., "P0171")
     * @return Description or null if not found
     */
    public String getDescription(String code) {
        // Check cache first
        if (cacheMap.containsKey(code)) {
            return cacheMap.get(code);
        }

        SQLiteDatabase db = getReadableDatabase();
        String query = "SELECT " + COL_DESCRIPTION + " FROM " + TABLE_NAME +
                      " WHERE " + COL_CODE + " = ?";
        Cursor cursor = db.rawQuery(query, new String[]{code.toUpperCase()});

        String description = null;
        if (cursor.moveToFirst()) {
            description = cursor.getString(0);
            // Cache the result
            if (cacheMap.size() < 100) { // Limit cache size
                cacheMap.put(code, description);
            }
        }
        cursor.close();

        return description;
    }

    /**
     * Get multiple codes at once (batch lookup)
     * @param codes List of DTC codes
     * @return Map of code to description
     */
    public Map<String, String> getDescriptions(List<String> codes) {
        Map<String, String> results = new HashMap<>();
        SQLiteDatabase db = getReadableDatabase();

        for (String code : codes) {
            String desc = getDescription(code);
            if (desc != null) {
                results.put(code, desc);
            }
        }

        return results;
    }

    /**
     * Search codes by keyword
     * @param keyword Search term
     * @return List of matching DTCs
     */
    public List<DTC> searchByKeyword(String keyword) {
        List<DTC> results = new ArrayList<>();
        SQLiteDatabase db = getReadableDatabase();

        String query = "SELECT * FROM " + TABLE_NAME +
                      " WHERE " + COL_DESCRIPTION + " LIKE ? " +
                      " OR " + COL_CODE + " LIKE ? LIMIT 50";
        String searchTerm = "%" + keyword + "%";
        Cursor cursor = db.rawQuery(query, new String[]{searchTerm, searchTerm});

        while (cursor.moveToNext()) {
            results.add(new DTC(
                cursor.getString(cursor.getColumnIndex(COL_CODE)),
                cursor.getString(cursor.getColumnIndex(COL_DESCRIPTION)),
                cursor.getString(cursor.getColumnIndex(COL_TYPE)),
                cursor.getString(cursor.getColumnIndex(COL_MANUFACTURER))
            ));
        }
        cursor.close();

        return results;
    }

    /**
     * Get codes by type (P, B, C, U)
     * @param type Code type character
     * @return List of codes
     */
    public List<DTC> getCodesByType(char type) {
        List<DTC> results = new ArrayList<>();
        SQLiteDatabase db = getReadableDatabase();

        String query = "SELECT * FROM " + TABLE_NAME +
                      " WHERE " + COL_TYPE + " = ? LIMIT 100";
        Cursor cursor = db.rawQuery(query, new String[]{String.valueOf(type)});

        while (cursor.moveToNext()) {
            results.add(new DTC(
                cursor.getString(cursor.getColumnIndex(COL_CODE)),
                cursor.getString(cursor.getColumnIndex(COL_DESCRIPTION)),
                cursor.getString(cursor.getColumnIndex(COL_TYPE)),
                cursor.getString(cursor.getColumnIndex(COL_MANUFACTURER))
            ));
        }
        cursor.close();

        return results;
    }

    /**
     * Get manufacturer-specific codes
     * @param manufacturer Manufacturer name (e.g., "mercedes", "ford")
     * @return List of manufacturer codes
     */
    public List<DTC> getManufacturerCodes(String manufacturer) {
        List<DTC> results = new ArrayList<>();
        SQLiteDatabase db = getReadableDatabase();

        String query = "SELECT * FROM " + TABLE_NAME +
                      " WHERE " + COL_MANUFACTURER + " = ? LIMIT 200";
        Cursor cursor = db.rawQuery(query, new String[]{manufacturer.toUpperCase()});

        while (cursor.moveToNext()) {
            results.add(new DTC(
                cursor.getString(cursor.getColumnIndex(COL_CODE)),
                cursor.getString(cursor.getColumnIndex(COL_DESCRIPTION)),
                cursor.getString(cursor.getColumnIndex(COL_TYPE)),
                cursor.getString(cursor.getColumnIndex(COL_MANUFACTURER))
            ));
        }
        cursor.close();

        return results;
    }

    /**
     * Get code type (P/B/C/U) from code string
     */
    public static char getCodeType(String code) {
        if (code != null && code.length() > 0) {
            return Character.toUpperCase(code.charAt(0));
        }
        return '?';
    }

    /**
     * Format code for display with type name
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
     * Load database from text files in assets
     */
    private void loadDatabaseFromAssets(SQLiteDatabase db) {
        // This would load from assets/dtc_data/ directory
        // Implementation depends on how you package the data
    }

    /**
     * DTC Data Class
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

        @Override
        public String toString() {
            return code + " - " + description;
        }
    }
}
