# Integration with Sister Projects

The DTC Database is part of a family of automotive diagnostic tools. This guide shows how to use it together with the NHTSA VIN Decoder and Recall Lookup projects.

## Sister Projects

- **[nhtsa-vin-decoder](https://github.com/Wal33D/nhtsa-vin-decoder)** - Decode VINs to get vehicle make/model/year
- **[nhtsa-recall-lookup](https://github.com/Wal33D/nhtsa-recall-lookup)** - Look up safety recalls by make/model/year
- **[dtc-database](https://github.com/Wal33D/dtc-database)** - Diagnostic trouble code database (this project)

## Complete Diagnostic Workflow

> The imports below assume you have each project available locally (or published in your internal package workflow).

### TypeScript/JavaScript Example

```typescript
import { VINDecoder } from '@wal33d/nhtsa-vin-decoder';
import { RecallLookup } from '@wal33d/nhtsa-recall-lookup';
import { DTCDatabase } from '@wal33d/dtc-database';

async function fullDiagnostic(vin: string, dtcCodes: string[]) {
  // Step 1: Decode VIN to get vehicle info
  const vinDecoder = new VINDecoder();
  const vehicle = await vinDecoder.decode(vin);

  console.log(`Vehicle: ${vehicle.modelYear} ${vehicle.make} ${vehicle.model}`);

  // Step 2: Check for recalls
  const recallLookup = new RecallLookup();
  const recalls = await recallLookup.getRecalls(
    vehicle.make,
    vehicle.model,
    vehicle.modelYear
  );

  console.log(`\nRecalls found: ${recalls.length}`);
  const critical = recalls.filter(r => r.parkIt || r.parkOutside);
  if (critical.length > 0) {
    console.log(`⚠️  CRITICAL: ${critical.length} safety recalls require immediate attention!`);
  }

  // Step 3: Decode diagnostic trouble codes
  const dtcDb = new DTCDatabase();
  console.log(`\nDiagnostic Trouble Codes:`);

  for (const code of dtcCodes) {
    const dtc = dtcDb.getDTC(code);
    if (dtc) {
      console.log(`  ${dtc.code} (${dtcDb.getTypeName(dtc.type)}): ${dtc.description}`);
    }
  }

  // Cleanup
  vinDecoder.close();
  dtcDb.close();
}

// Example usage
fullDiagnostic('1HGCM82633A004352', ['P0420', 'P0300', 'P0171'])
  .catch(console.error);
```

### Python Example

```python
from nhtsa_vin_decoder import NHTSAVinDecoder
from nhtsa_recall_lookup import NHTSARecallLookup
from python.dtc_database import DTCDatabase

def full_diagnostic(vin, dtc_codes):
    # Step 1: Decode VIN
    vin_decoder = NHTSAVinDecoder()
    vehicle = vin_decoder.decode_vin(vin)

    print(f"Vehicle: {vehicle.model_year} {vehicle.make} {vehicle.model}")

    # Step 2: Check recalls
    recall_lookup = NHTSARecallLookup()
    recalls = recall_lookup.get_recalls_for_vehicle(
        vehicle.make,
        vehicle.model,
        vehicle.model_year
    )

    print(f"\nRecalls found: {len(recalls)}")
    critical = [r for r in recalls if r.is_critical_safety()]
    if critical:
        print(f"⚠️  CRITICAL: {len(critical)} safety recalls!")

    # Step 3: Decode DTCs
    dtc_db = DTCDatabase()
    print("\nDiagnostic Trouble Codes:")

    for code in dtc_codes:
        dtc = dtc_db.get_dtc(code)
        if dtc:
            print(f"  {dtc.code} ({dtc.type_name}): {dtc.description}")

    dtc_db.close()

# Example
full_diagnostic('1HGCM82633A004352', ['P0420', 'P0300', 'P0171'])
```

### Java Example

```java
import io.github.vindecoder.offline.OfflineVINDecoder;
import io.github.vindecoder.nhtsa.VehicleData;
import io.github.recalllookup.core.RecallLookupService;
import io.github.recalllookup.core.RecallRecord;
import com.dtcdatabase.DTCDatabaseCore;
import com.dtcdatabase.DTCDatabaseCore.DTC;

public class FullDiagnostic {
    public static void main(String[] args) {
        String vin = "1HGCM82633A004352";
        String[] dtcCodes = {"P0420", "P0300", "P0171"};

        // Step 1: Decode VIN
        OfflineVINDecoder vinDecoder = new OfflineVINDecoder();
        VehicleData vehicle = vinDecoder.decode(vin);

        System.out.println("Vehicle: " + vehicle.getModelYear() + " " +
                          vehicle.getMake() + " " + vehicle.getModel());

        // Step 2: Check recalls
        RecallLookupService recallService = RecallLookupService.getInstance();
        recallService.getRecalls(
            vehicle.getMake(),
            vehicle.getModel(),
            vehicle.getModelYear(),
            new RecallLookupService.RecallCallback() {
                @Override
                public void onSuccess(List<RecallRecord> recalls) {
                    System.out.println("\nRecalls found: " + recalls.size());

                    long critical = recalls.stream()
                        .filter(RecallRecord::isCriticalSafety)
                        .count();

                    if (critical > 0) {
                        System.out.println("⚠️  CRITICAL: " + critical + " safety recalls!");
                    }
                }

                @Override
                public void onError(String error) {
                    System.err.println("Recall lookup error: " + error);
                }
            }
        );

        // Step 3: Decode DTCs
        DTCDatabaseCore dtcDb = new DTCDatabaseCore("data/dtc_codes.db");
        System.out.println("\nDiagnostic Trouble Codes:");

        for (String code : dtcCodes) {
            DTC dtc = dtcDb.getDTC(code);
            if (dtc != null) {
                System.out.println("  " + dtc.code + " (" + dtc.getTypeName() + "): " +
                                 dtc.description);
            }
        }

        dtcDb.close();
        recallService.close();
    }
}
```

## Use Cases

### 1. OBD-II Diagnostic Scanner App

Combine all three libraries to create a complete diagnostic tool:
1. Read VIN from vehicle
2. Decode VIN to identify vehicle
3. Check for safety recalls
4. Read diagnostic codes from ECU
5. Display code descriptions

### 2. Fleet Management System

Monitor multiple vehicles:
- Track vehicle inventory (VIN decoder)
- Monitor recall campaigns (Recall lookup)
- Log diagnostic events (DTC database)

### 3. Pre-Purchase Vehicle Inspection

Provide comprehensive vehicle reports:
- Decode VIN to verify vehicle details
- Check recall history
- Interpret any check engine light codes

### 4. Automotive Repair Shop Software

Streamline diagnostics:
- Quick VIN lookups
- Instant recall checks
- Code interpretation for technicians

## Installation

Use source installs from each repository:

### TypeScript/JavaScript (source workflow)
```bash
# In each cloned repo:
npm install
npm run build
```

### Python (editable/local workflow)
```bash
# Install repos that ship Python packaging metadata
pip install -e /path/to/nhtsa-vin-decoder
pip install -e /path/to/nhtsa-recall-lookup

# Use dtc-database directly from source
export PYTHONPATH="/path/to/dtc-database:$PYTHONPATH"
```

### Java/Android
Add as Git submodules (or copy source modules/classes) into your project.

## Data Flow

```
VIN Input
    ↓
[VIN Decoder] → Make, Model, Year
    ↓
[Recall Lookup] → Safety Recalls
    ↓
DTC Codes from OBD-II Scanner
    ↓
[DTC Database] → Code Descriptions
    ↓
Complete Diagnostic Report
```

## Notes

- All three libraries work independently
- No dependencies between them
- Combine as needed for your use case
- Each has consistent APIs across Python, Java, TypeScript
- All use local databases (offline-capable)

## License

All three projects are MIT licensed.

## Author

Wal33D <aquataze@yahoo.com>
