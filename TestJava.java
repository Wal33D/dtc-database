import com.dtcdatabase.core.DTCDatabaseCore;
import com.dtcdatabase.core.DTCDatabaseCore.DTC;
import java.util.List;
import java.util.Map;

public class TestJava {
    public static void main(String[] args) {
        System.out.println("=== Java DTC Database Test ===\n");

        try {
            // Initialize database
            DTCDatabaseCore db = DTCDatabaseCore.getInstance();

            // Test single lookup
            System.out.println("1. Testing single lookup (P0171):");
            String desc = db.getDescription("P0171");
            System.out.println("   " + (desc != null ? desc : "NOT FOUND"));

            // Test search
            System.out.println("\n2. Testing search for 'oxygen':");
            List<DTC> results = db.search("oxygen", 3);
            for (DTC dtc : results) {
                System.out.println("   " + dtc);
            }

            // Test statistics
            System.out.println("\n3. Database statistics:");
            Map<String, Integer> stats = db.getStatistics();
            System.out.println("   Total codes: " + stats.get("total"));
            System.out.println("   Powertrain: " + stats.get("type_P"));

            System.out.println("\n✅ Java test passed!");

        } catch (Exception e) {
            System.err.println("❌ Test failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}