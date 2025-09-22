package com.dtcdatabase.core;

import java.io.*;
import java.nio.file.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Platform-independent DTC Database for Java applications
 * Can be used in Android, desktop Java, or server applications
 *
 * @author Wal33D
 * @email aquataze@yahoo.com
 */
public class DTCDatabaseCore {
    private static final String DB_NAME = "dtc_codes.db";
    private Connection connection;
    private final Map<String, String> cache = new ConcurrentHashMap<>();
    private static DTCDatabaseCore instance;

    // SQL queries
    private static final String CREATE_TABLE =
        "CREATE TABLE IF NOT EXISTS dtc_codes (" +
        "code TEXT PRIMARY KEY, " +
        "description TEXT NOT NULL, " +
        "type TEXT, " +
        "manufacturer TEXT)";

    private static final String INSERT_CODE =
        "INSERT OR REPLACE INTO dtc_codes VALUES (?, ?, ?, ?)";

    private static final String SELECT_DESCRIPTION =
        "SELECT description FROM dtc_codes WHERE code = ?";

    private static final String SELECT_BY_TYPE =
        "SELECT * FROM dtc_codes WHERE type = ? LIMIT ?";

    private static final String SEARCH_CODES =
        "SELECT * FROM dtc_codes WHERE code LIKE ? OR description LIKE ? LIMIT ?";

    /**
     * Singleton instance getter
     */
    public static synchronized DTCDatabaseCore getInstance() {
        if (instance == null) {
            instance = new DTCDatabaseCore();
        }
        return instance;
    }

    /**
     * Constructor - initializes database
     */
    private DTCDatabaseCore() {
        try {
            initializeDatabase();
        } catch (SQLException e) {
            throw new RuntimeException("Failed to initialize DTC database", e);
        }
    }

    /**
     * Initialize SQLite database
     */
    private void initializeDatabase() throws SQLException {
        // Load SQLite driver
        try {
            Class.forName("org.sqlite.JDBC");
        } catch (ClassNotFoundException e) {
            throw new RuntimeException("SQLite JDBC driver not found", e);
        }

        // Create connection
        String dbPath = getDBPath();
        connection = DriverManager.getConnection("jdbc:sqlite:" + dbPath);

        // Create table if needed
        try (Statement stmt = connection.createStatement()) {
            stmt.execute(CREATE_TABLE);
        }

        // Check if database is empty and needs loading
        if (isDatabaseEmpty()) {
            loadDataFromResources();
        }
    }

    /**
     * Get database path (can be overridden for different platforms)
     */
    protected String getDBPath() {
        return DB_NAME;
    }

    /**
     * Check if database is empty
     */
    private boolean isDatabaseEmpty() throws SQLException {
        String query = "SELECT COUNT(*) FROM dtc_codes";
        try (Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {
            return rs.getInt(1) == 0;
        }
    }

    /**
     * Load data from source files
     */
    private void loadDataFromResources() {
        // This would be implemented differently for Android vs desktop
        // For now, provides structure for loading
        System.out.println("Database needs to be populated with DTC codes");
    }

    /**
     * Load codes from a text file
     */
    public void loadFromFile(String filePath, String manufacturer) throws IOException, SQLException {
        Path path = Paths.get(filePath);
        List<String> lines = Files.readAllLines(path);

        try (PreparedStatement pstmt = connection.prepareStatement(INSERT_CODE)) {
            for (String line : lines) {
                if (line.contains(" - ")) {
                    String[] parts = line.split(" - ", 2);
                    if (parts.length == 2) {
                        String code = parts[0].trim();
                        String description = parts[1].trim();
                        String type = code.substring(0, 1);

                        pstmt.setString(1, code);
                        pstmt.setString(2, description);
                        pstmt.setString(3, type);
                        pstmt.setString(4, manufacturer);
                        pstmt.executeUpdate();
                    }
                }
            }
        }
    }

    /**
     * Get description for a DTC code
     */
    public String getDescription(String code) {
        if (code == null) return null;
        code = code.toUpperCase();

        // Check cache
        if (cache.containsKey(code)) {
            return cache.get(code);
        }

        try (PreparedStatement pstmt = connection.prepareStatement(SELECT_DESCRIPTION)) {
            pstmt.setString(1, code);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    String description = rs.getString(1);
                    // Cache result
                    if (cache.size() < 100) {
                        cache.put(code, description);
                    }
                    return description;
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return null;
    }

    /**
     * Get multiple codes at once
     */
    public Map<String, String> getDescriptions(List<String> codes) {
        Map<String, String> results = new HashMap<>();
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
     */
    public List<DTC> search(String keyword, int limit) {
        List<DTC> results = new ArrayList<>();

        try (PreparedStatement pstmt = connection.prepareStatement(SEARCH_CODES)) {
            String searchTerm = "%" + keyword + "%";
            pstmt.setString(1, searchTerm);
            pstmt.setString(2, searchTerm);
            pstmt.setInt(3, limit);

            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    results.add(new DTC(
                        rs.getString("code"),
                        rs.getString("description"),
                        rs.getString("type"),
                        rs.getString("manufacturer")
                    ));
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return results;
    }

    /**
     * Get codes by type
     */
    public List<DTC> getByType(char type, int limit) {
        List<DTC> results = new ArrayList<>();

        try (PreparedStatement pstmt = connection.prepareStatement(SELECT_BY_TYPE)) {
            pstmt.setString(1, String.valueOf(type));
            pstmt.setInt(2, limit);

            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    results.add(new DTC(
                        rs.getString("code"),
                        rs.getString("description"),
                        rs.getString("type"),
                        rs.getString("manufacturer")
                    ));
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return results;
    }

    /**
     * Get database statistics
     */
    public Map<String, Integer> getStatistics() {
        Map<String, Integer> stats = new HashMap<>();

        try (Statement stmt = connection.createStatement()) {
            // Total count
            ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM dtc_codes");
            if (rs.next()) {
                stats.put("total", rs.getInt(1));
            }

            // Count by type
            for (String type : Arrays.asList("P", "B", "C", "U")) {
                rs = stmt.executeQuery(
                    "SELECT COUNT(*) FROM dtc_codes WHERE type = '" + type + "'"
                );
                if (rs.next()) {
                    stats.put("type_" + type, rs.getInt(1));
                }
            }

            // Manufacturer-specific count
            rs = stmt.executeQuery(
                "SELECT COUNT(*) FROM dtc_codes WHERE manufacturer IS NOT NULL"
            );
            if (rs.next()) {
                stats.put("manufacturer_specific", rs.getInt(1));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return stats;
    }

    /**
     * Clear cache
     */
    public void clearCache() {
        cache.clear();
    }

    /**
     * Close database connection
     */
    public void close() {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    /**
     * DTC data class
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

        public String getTypeName() {
            switch (type) {
                case "P": return "Powertrain";
                case "B": return "Body";
                case "C": return "Chassis";
                case "U": return "Network";
                default: return "Unknown";
            }
        }

        @Override
        public String toString() {
            return code + " - " + description;
        }
    }
}