package com.dtcdatabase;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * Platform-independent DTC database access for JVM applications.
 *
 * This class reads from the repository schema in data/dtc_codes.db:
 * - code
 * - manufacturer
 * - description
 * - type
 * - locale
 * - is_generic
 * - source_file
 */
public class DTCDatabaseCore implements AutoCloseable {
    private static final String DEFAULT_DB_PATH = "data/dtc_codes.db";
    private static final String DEFAULT_LOCALE = "en";
    private static final int DEFAULT_CACHE_SIZE = 100;

    private final Connection connection;
    private final String locale;
    private final int cacheSize;
    private final Map<String, String> descriptionCache;

    public DTCDatabaseCore() {
        this(DEFAULT_DB_PATH, DEFAULT_LOCALE, DEFAULT_CACHE_SIZE);
    }

    public DTCDatabaseCore(String dbPath) {
        this(dbPath, DEFAULT_LOCALE, DEFAULT_CACHE_SIZE);
    }

    public DTCDatabaseCore(String dbPath, String locale) {
        this(dbPath, locale, DEFAULT_CACHE_SIZE);
    }

    public DTCDatabaseCore(String dbPath, String locale, int cacheSize) {
        if (dbPath == null || dbPath.trim().isEmpty()) {
            throw new IllegalArgumentException("dbPath must not be empty");
        }
        if (locale == null || locale.trim().isEmpty()) {
            throw new IllegalArgumentException("locale must not be empty");
        }
        if (cacheSize <= 0) {
            throw new IllegalArgumentException("cacheSize must be > 0");
        }

        Path dbFile = Paths.get(dbPath);
        if (!Files.exists(dbFile)) {
            throw new IllegalArgumentException("Database not found at: " + dbPath);
        }

        this.locale = locale;
        this.cacheSize = cacheSize;
        this.connection = openConnection(dbPath);

        this.descriptionCache = Collections.synchronizedMap(
            new LinkedHashMap<String, String>(cacheSize, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(Map.Entry<String, String> eldest) {
                    return size() > DTCDatabaseCore.this.cacheSize;
                }
            }
        );
    }

    private Connection openConnection(String dbPath) {
        try {
            return DriverManager.getConnection("jdbc:sqlite:" + dbPath);
        } catch (SQLException error) {
            throw new RuntimeException("Failed to open database at " + dbPath, error);
        }
    }

    private static String normalizeCode(String code) {
        return code == null ? "" : code.trim().toUpperCase();
    }

    private static String normalizeManufacturer(String manufacturer) {
        if (manufacturer == null) {
            return null;
        }
        String cleaned = manufacturer.trim().toUpperCase();
        return cleaned.isEmpty() ? null : cleaned;
    }

    private static String typeName(String type) {
        if (type == null || type.isEmpty()) {
            return "Unknown";
        }
        switch (type.charAt(0)) {
            case 'P':
                return "Powertrain";
            case 'B':
                return "Body";
            case 'C':
                return "Chassis";
            case 'U':
                return "Network";
            default:
                return "Unknown";
        }
    }

    private DTC mapDTC(ResultSet resultSet) throws SQLException {
        String manufacturerRaw = resultSet.getString("manufacturer");
        boolean isGeneric = resultSet.getInt("is_generic") == 1 || "GENERIC".equals(manufacturerRaw);
        String manufacturer = "GENERIC".equals(manufacturerRaw) ? null : manufacturerRaw;

        return new DTC(
            resultSet.getString("code"),
            resultSet.getString("description"),
            resultSet.getString("type"),
            manufacturer,
            isGeneric,
            resultSet.getString("locale")
        );
    }

    private DTC runSingleLookup(String sql, List<String> params) {
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            for (int i = 0; i < params.size(); i++) {
                statement.setString(i + 1, params.get(i));
            }
            try (ResultSet resultSet = statement.executeQuery()) {
                if (resultSet.next()) {
                    return mapDTC(resultSet);
                }
                return null;
            }
        } catch (SQLException error) {
            throw new RuntimeException("Failed DTC lookup query", error);
        }
    }

    /**
     * Look up a code using generic-first behavior.
     */
    public DTC getDTC(String code) {
        return getDTC(code, null);
    }

    /**
     * Look up a code with manufacturer context, then fall back to GENERIC.
     */
    public DTC getDTC(String code, String manufacturer) {
        String normalizedCode = normalizeCode(code);
        if (normalizedCode.isEmpty()) {
            return null;
        }

        String normalizedManufacturer = normalizeManufacturer(manufacturer);
        if (normalizedManufacturer != null) {
            DTC byManufacturer = runSingleLookup(
                "SELECT code, description, type, manufacturer, is_generic, locale " +
                    "FROM dtc_definitions " +
                    "WHERE code = ? AND manufacturer = ? AND locale = ? " +
                    "LIMIT 1",
                java.util.Arrays.asList(normalizedCode, normalizedManufacturer, locale)
            );
            if (byManufacturer != null) {
                return byManufacturer;
            }

            return runSingleLookup(
                "SELECT code, description, type, manufacturer, is_generic, locale " +
                    "FROM dtc_definitions " +
                    "WHERE code = ? AND manufacturer = 'GENERIC' AND locale = ? " +
                    "LIMIT 1",
                java.util.Arrays.asList(normalizedCode, locale)
            );
        }

        return runSingleLookup(
            "SELECT code, description, type, manufacturer, is_generic, locale " +
                "FROM dtc_definitions " +
                "WHERE code = ? AND locale = ? " +
                "ORDER BY is_generic DESC " +
                "LIMIT 1",
            java.util.Arrays.asList(normalizedCode, locale)
        );
    }

    public String getDescription(String code) {
        return getDescription(code, null);
    }

    public String getDescription(String code, String manufacturer) {
        String normalizedCode = normalizeCode(code);
        if (normalizedCode.isEmpty()) {
            return null;
        }

        String normalizedManufacturer = normalizeManufacturer(manufacturer);
        String cacheKey = normalizedCode + ":" + (normalizedManufacturer == null ? "GENERIC" : normalizedManufacturer) + ":" + locale;

        if (descriptionCache.containsKey(cacheKey)) {
            return descriptionCache.get(cacheKey);
        }

        DTC dtc = getDTC(normalizedCode, normalizedManufacturer);
        if (dtc == null) {
            return null;
        }

        descriptionCache.put(cacheKey, dtc.description);
        return dtc.description;
    }

    public Map<String, String> getDescriptions(List<String> codes) {
        Map<String, String> results = new LinkedHashMap<>();
        if (codes == null) {
            return results;
        }

        for (String code : codes) {
            String normalizedCode = normalizeCode(code);
            String description = getDescription(normalizedCode);
            if (description != null) {
                results.put(normalizedCode, description);
            }
        }
        return results;
    }

    public List<DTC> search(String keyword) {
        return search(keyword, 50);
    }

    public List<DTC> search(String keyword, int limit) {
        if (keyword == null || keyword.trim().isEmpty()) {
            return Collections.emptyList();
        }
        if (limit <= 0) {
            return Collections.emptyList();
        }

        List<DTC> results = new ArrayList<>();
        String searchTerm = "%" + keyword + "%";

        try (PreparedStatement statement = connection.prepareStatement(
            "SELECT code, description, type, manufacturer, is_generic, locale " +
                "FROM dtc_definitions " +
                "WHERE (code LIKE ? OR description LIKE ?) AND locale = ? " +
                "ORDER BY is_generic DESC, code ASC " +
                "LIMIT ?"
        )) {
            statement.setString(1, searchTerm);
            statement.setString(2, searchTerm);
            statement.setString(3, locale);
            statement.setInt(4, limit);

            try (ResultSet resultSet = statement.executeQuery()) {
                while (resultSet.next()) {
                    results.add(mapDTC(resultSet));
                }
            }
        } catch (SQLException error) {
            throw new RuntimeException("Failed search query", error);
        }

        return results;
    }

    public List<DTC> getByType(char type) {
        return getByType(type, 100);
    }

    public List<DTC> getByType(char type, int limit) {
        if (limit <= 0) {
            return Collections.emptyList();
        }

        List<DTC> results = new ArrayList<>();
        String normalizedType = String.valueOf(Character.toUpperCase(type));

        try (PreparedStatement statement = connection.prepareStatement(
            "SELECT code, description, type, manufacturer, is_generic, locale " +
                "FROM dtc_definitions " +
                "WHERE type = ? AND locale = ? " +
                "ORDER BY is_generic DESC, code ASC " +
                "LIMIT ?"
        )) {
            statement.setString(1, normalizedType);
            statement.setString(2, locale);
            statement.setInt(3, limit);

            try (ResultSet resultSet = statement.executeQuery()) {
                while (resultSet.next()) {
                    results.add(mapDTC(resultSet));
                }
            }
        } catch (SQLException error) {
            throw new RuntimeException("Failed type query", error);
        }

        return results;
    }

    public List<DTC> getManufacturerCodes(String manufacturer) {
        return getManufacturerCodes(manufacturer, 200);
    }

    public List<DTC> getManufacturerCodes(String manufacturer, int limit) {
        if (limit <= 0) {
            return Collections.emptyList();
        }

        String normalizedManufacturer = normalizeManufacturer(manufacturer);
        if (normalizedManufacturer == null) {
            return Collections.emptyList();
        }

        List<DTC> results = new ArrayList<>();
        try (PreparedStatement statement = connection.prepareStatement(
            "SELECT code, description, type, manufacturer, is_generic, locale " +
                "FROM dtc_definitions " +
                "WHERE manufacturer = ? AND locale = ? " +
                "ORDER BY code ASC " +
                "LIMIT ?"
        )) {
            statement.setString(1, normalizedManufacturer);
            statement.setString(2, locale);
            statement.setInt(3, limit);

            try (ResultSet resultSet = statement.executeQuery()) {
                while (resultSet.next()) {
                    results.add(mapDTC(resultSet));
                }
            }
        } catch (SQLException error) {
            throw new RuntimeException("Failed manufacturer query", error);
        }

        return results;
    }

    public Map<String, Integer> getStatistics() {
        Map<String, Integer> stats = new LinkedHashMap<>();

        try {
            int total = queryInt("SELECT COUNT(*) FROM dtc_definitions WHERE locale = ?", locale);
            int generic = queryInt(
                "SELECT COUNT(*) FROM dtc_definitions WHERE is_generic = 1 AND locale = ?",
                locale
            );

            stats.put("total", total);
            stats.put("unique_codes", queryInt(
                "SELECT COUNT(DISTINCT code) FROM dtc_definitions WHERE locale = ?",
                locale
            ));
            stats.put("generic", generic);
            stats.put("generic_codes", generic);
            stats.put("manufacturer_specific", total - generic);
            stats.put("manufacturer_codes", total - generic);
            stats.put("manufacturers", queryInt(
                "SELECT COUNT(DISTINCT manufacturer) " +
                    "FROM dtc_definitions " +
                    "WHERE manufacturer != 'GENERIC' AND locale = ?",
                locale
            ));

            for (String type : new String[]{"P", "B", "C", "U"}) {
                stats.put("type_" + type, queryInt(
                    "SELECT COUNT(*) FROM dtc_definitions WHERE type = ? AND locale = ?",
                    type,
                    locale
                ));
            }
        } catch (SQLException error) {
            throw new RuntimeException("Failed statistics query", error);
        }

        return stats;
    }

    private int queryInt(String sql, String... params) throws SQLException {
        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            for (int i = 0; i < params.length; i++) {
                statement.setString(i + 1, params[i]);
            }
            try (ResultSet resultSet = statement.executeQuery()) {
                if (resultSet.next()) {
                    return resultSet.getInt(1);
                }
                return 0;
            }
        }
    }

    public void clearCache() {
        descriptionCache.clear();
    }

    @Override
    public void close() {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
            }
        } catch (SQLException error) {
            throw new RuntimeException("Failed closing database connection", error);
        }
    }

    public static class DTC {
        public final String code;
        public final String description;
        public final String type;
        public final String manufacturer;
        public final boolean isGeneric;
        public final String locale;

        public DTC(
            String code,
            String description,
            String type,
            String manufacturer,
            boolean isGeneric,
            String locale
        ) {
            this.code = Objects.requireNonNull(code, "code");
            this.description = Objects.requireNonNull(description, "description");
            this.type = Objects.requireNonNull(type, "type");
            this.manufacturer = manufacturer;
            this.isGeneric = isGeneric;
            this.locale = locale;
        }

        public String getTypeName() {
            return typeName(type);
        }

        public boolean isManufacturerSpecific() {
            return !isGeneric;
        }

        @Override
        public String toString() {
            StringBuilder builder = new StringBuilder();
            builder.append(code).append(" - ").append(description);
            if (manufacturer != null) {
                builder.append(" [").append(manufacturer).append("]");
            }
            return builder.toString();
        }
    }
}
