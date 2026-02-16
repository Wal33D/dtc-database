# Usage Guide

## Quick Start

### Python

```python
from python.dtc_database import DTCDatabase

# Initialize database
db = DTCDatabase('data/dtc_codes.db')

# Look up a code
dtc = db.get_dtc('P0420')
print(f"{dtc.code}: {dtc.description}")

# Search for codes
results = db.search('oxygen sensor')
for dtc in results:
    print(f"{dtc.code}: {dtc.description}")

# Close when done
db.close()
```

### Java

```java
import com.dtcdatabase.DTCDatabaseCore;
import java.util.List;

public class QuickStart {
    public static void main(String[] args) {
        DTCDatabaseCore db = new DTCDatabaseCore("data/dtc_codes.db");

        // Look up a code
        DTCDatabaseCore.DTC dtc = db.getDTC("P0420");
        System.out.println(dtc.code + ": " + dtc.description);

        // Search for codes
        List<DTCDatabaseCore.DTC> results = db.search("oxygen sensor", 10);
        for (DTCDatabaseCore.DTC code : results) {
            System.out.println(code);
        }

        db.close();
    }
}
```

## Common Use Cases

### 1. OBD-II Diagnostic Application

Building a diagnostic app that interprets fault codes from vehicles.

```python
class DiagnosticApp:
    def __init__(self):
        self.db = DTCDatabase('data/dtc_codes.db')

    def diagnose_vehicle(self, codes):
        """Diagnose vehicle based on fault codes"""
        print("=== Vehicle Diagnostic Report ===\n")

        # Categorize codes by type
        categorized = {
            'P': [],  # Powertrain
            'B': [],  # Body
            'C': [],  # Chassis
            'U': []   # Network
        }

        for code in codes:
            dtc = self.db.get_dtc(code)
            if dtc:
                categorized[dtc.type].append(dtc)

        # Report by category
        for type_code, type_name in [('P', 'Powertrain'), ('B', 'Body'),
                                      ('C', 'Chassis'), ('U', 'Network')]:
            if categorized[type_code]:
                print(f"\n{type_name} Issues ({len(categorized[type_code])}):")
                print("-" * 40)
                for dtc in categorized[type_code]:
                    print(f"• {dtc.code}: {dtc.description}")

        return categorized

    def get_related_codes(self, code):
        """Find related fault codes"""
        dtc = self.db.get_dtc(code)
        if not dtc:
            return []

        # Search for related issues
        keywords = dtc.description.split()[:3]
        related = []
        for keyword in keywords:
            if len(keyword) > 4:  # Skip short words
                results = self.db.search(keyword, limit=5)
                related.extend(results)

        # Remove duplicates and original code
        seen = set()
        unique = []
        for item in related:
            if item.code != code and item.code not in seen:
                seen.add(item.code)
                unique.append(item)

        return unique[:5]  # Return top 5 related

# Usage
app = DiagnosticApp()

# Vehicle fault codes from OBD-II scanner
fault_codes = ['P0171', 'P0174', 'P0420', 'B0001']
app.diagnose_vehicle(fault_codes)

# Find related codes
related = app.get_related_codes('P0171')
print("\nRelated codes to P0171:")
for dtc in related:
    print(f"  • {dtc.code}: {dtc.description}")
```

### 2. Service Center Management System

Managing vehicle repairs and tracking common issues.

```python
import sqlite3
from datetime import datetime

class ServiceCenter:
    def __init__(self):
        self.dtc_db = DTCDatabase('data/dtc_codes.db')
        self.service_db = sqlite3.connect('service_records.db')
        self._init_service_db()

    def _init_service_db(self):
        """Initialize service records database"""
        cursor = self.service_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repairs (
                id INTEGER PRIMARY KEY,
                vin TEXT,
                code TEXT,
                description TEXT,
                repair_date DATE,
                cost REAL,
                technician TEXT
            )
        ''')
        self.service_db.commit()

    def log_repair(self, vin, code, cost, technician):
        """Log a repair for tracking"""
        dtc = self.dtc_db.get_dtc(code)
        if not dtc:
            raise ValueError(f"Unknown code: {code}")

        cursor = self.service_db.cursor()
        cursor.execute('''
            INSERT INTO repairs (vin, code, description, repair_date, cost, technician)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (vin, code, dtc.description, datetime.now(), cost, technician))
        self.service_db.commit()

        return dtc

    def get_common_issues(self, limit=10):
        """Get most common issues serviced"""
        cursor = self.service_db.cursor()
        cursor.execute('''
            SELECT code, COUNT(*) as count, AVG(cost) as avg_cost
            FROM repairs
            GROUP BY code
            ORDER BY count DESC
            LIMIT ?
        ''', (limit,))

        results = []
        for row in cursor.fetchall():
            code, count, avg_cost = row
            dtc = self.dtc_db.get_dtc(code)
            results.append({
                'code': code,
                'description': dtc.description if dtc else 'Unknown',
                'occurrences': count,
                'average_cost': avg_cost
            })

        return results

    def estimate_repair_cost(self, code):
        """Estimate repair cost based on history"""
        cursor = self.service_db.cursor()
        cursor.execute('''
            SELECT AVG(cost), MIN(cost), MAX(cost), COUNT(*)
            FROM repairs
            WHERE code = ?
        ''', (code,))

        avg_cost, min_cost, max_cost, count = cursor.fetchone()

        if count == 0:
            # No history, provide default estimate
            dtc = self.dtc_db.get_dtc(code)
            if dtc and dtc.type == 'P':
                return {'estimated': 250, 'confidence': 'low'}
            elif dtc and dtc.type == 'B':
                return {'estimated': 150, 'confidence': 'low'}
            else:
                return {'estimated': 200, 'confidence': 'low'}

        return {
            'estimated': avg_cost,
            'range': (min_cost, max_cost),
            'based_on': count,
            'confidence': 'high' if count > 5 else 'medium'
        }

# Usage
center = ServiceCenter()

# Log a repair
dtc = center.log_repair('1HGCM82633A004352', 'P0420', 450.00, 'John Smith')
print(f"Logged repair: {dtc.code} - {dtc.description}")

# Get common issues
print("\nMost Common Issues:")
for issue in center.get_common_issues(5):
    print(f"  {issue['code']}: {issue['occurrences']} times, "
          f"avg cost: ${issue['average_cost']:.2f}")

# Estimate repair cost
estimate = center.estimate_repair_cost('P0420')
print(f"\nRepair estimate for P0420: ${estimate['estimated']:.2f}")
```

### 3. Fleet Management System

Monitor and maintain a fleet of vehicles.

```python
class FleetManager:
    def __init__(self):
        self.db = DTCDatabase('data/dtc_codes.db')
        self.fleet = {}  # VIN -> vehicle info
        self.active_codes = {}  # VIN -> list of codes

    def add_vehicle(self, vin, make, model, year):
        """Add vehicle to fleet"""
        self.fleet[vin] = {
            'make': make,
            'model': model,
            'year': year,
            'added': datetime.now()
        }
        self.active_codes[vin] = []

    def scan_vehicle(self, vin, codes):
        """Process diagnostic codes from vehicle scan"""
        if vin not in self.fleet:
            raise ValueError(f"Vehicle {vin} not in fleet")

        self.active_codes[vin] = codes

        # Analyze codes
        report = {
            'vin': vin,
            'vehicle': self.fleet[vin],
            'codes': [],
            'priority': 'normal',
            'actions': []
        }

        for code in codes:
            dtc = self.db.get_dtc(code)
            if dtc:
                report['codes'].append(dtc)

                # Determine priority
                if dtc.type == 'P' and any(word in dtc.description.lower()
                                          for word in ['misfire', 'lean', 'rich']):
                    report['priority'] = 'high'
                    report['actions'].append(f"Immediate attention: {dtc.code}")

                elif dtc.type == 'B' and 'airbag' in dtc.description.lower():
                    report['priority'] = 'critical'
                    report['actions'].append(f"Safety issue: {dtc.code}")

        return report

    def get_fleet_health(self):
        """Get overall fleet health status"""
        total = len(self.fleet)
        healthy = sum(1 for codes in self.active_codes.values() if not codes)
        minor = sum(1 for codes in self.active_codes.values()
                   if codes and all(c.startswith('P2') or c.startswith('P3')
                                   for c in codes))
        major = total - healthy - minor

        return {
            'total_vehicles': total,
            'healthy': healthy,
            'minor_issues': minor,
            'major_issues': major,
            'health_percentage': (healthy / total * 100) if total > 0 else 0
        }

    def maintenance_schedule(self):
        """Generate maintenance recommendations"""
        recommendations = []

        for vin, codes in self.active_codes.items():
            if not codes:
                continue

            vehicle = self.fleet[vin]
            for code in codes:
                dtc = self.db.get_dtc(code)
                if dtc:
                    # Common maintenance triggers
                    if 'catalyst' in dtc.description.lower():
                        recommendations.append({
                            'vin': vin,
                            'vehicle': f"{vehicle['year']} {vehicle['make']} {vehicle['model']}",
                            'code': code,
                            'maintenance': 'Check exhaust system and O2 sensors',
                            'priority': 'medium'
                        })
                    elif 'misfire' in dtc.description.lower():
                        recommendations.append({
                            'vin': vin,
                            'vehicle': f"{vehicle['year']} {vehicle['make']} {vehicle['model']}",
                            'code': code,
                            'maintenance': 'Service ignition system',
                            'priority': 'high'
                        })

        return recommendations

# Usage
fleet = FleetManager()

# Add vehicles
fleet.add_vehicle('1HGCM82633A004352', 'Honda', 'Accord', 2003)
fleet.add_vehicle('WBA5B3C50GG252337', 'BMW', '5 Series', 2016)
fleet.add_vehicle('5YJ3E1EA5KF000316', 'Tesla', 'Model 3', 2019)

# Scan vehicles
report1 = fleet.scan_vehicle('1HGCM82633A004352', ['P0420', 'P0171'])
report2 = fleet.scan_vehicle('WBA5B3C50GG252337', ['P0300', 'P0301'])

# Fleet health
health = fleet.get_fleet_health()
print(f"Fleet Health: {health['health_percentage']:.1f}%")
print(f"  Healthy: {health['healthy']}")
print(f"  Minor Issues: {health['minor_issues']}")
print(f"  Major Issues: {health['major_issues']}")

# Maintenance schedule
print("\nMaintenance Recommendations:")
for rec in fleet.maintenance_schedule():
    print(f"  {rec['vehicle']}: {rec['maintenance']} (Priority: {rec['priority']})")
```

### 4. Mobile Mechanic App

Quick reference for field repairs.

```python
class MobileMechanic:
    def __init__(self):
        self.db = DTCDatabase('data/dtc_codes.db')
        self.cache = {}  # Cache frequent lookups

    def quick_lookup(self, code):
        """Fast lookup with caching"""
        if code in self.cache:
            return self.cache[code]

        dtc = self.db.get_dtc(code)
        if dtc:
            self.cache[code] = dtc
        return dtc

    def diagnose_symptoms(self, symptoms):
        """Find codes based on symptoms"""
        results = []
        for symptom in symptoms:
            codes = self.db.search(symptom, limit=10)
            results.extend(codes)

        # Remove duplicates
        seen = set()
        unique = []
        for dtc in results:
            if dtc.code not in seen:
                seen.add(dtc.code)
                unique.append(dtc)

        return unique

    def manufacturer_specific(self, make, codes):
        """Get manufacturer-specific interpretations"""
        mfg_codes = self.db.get_manufacturer_codes(make.upper())
        specific = []

        for code in codes:
            # Check if manufacturer has specific definition
            for mfg_dtc in mfg_codes:
                if mfg_dtc.code == code:
                    specific.append(mfg_dtc)
                    break
            else:
                # Use generic if no specific found
                generic = self.db.get_dtc(code)
                if generic:
                    specific.append(generic)

        return specific

    def common_fixes(self, code):
        """Suggest common fixes for a code"""
        dtc = self.db.get_dtc(code)
        if not dtc:
            return []

        fixes = {
            'P0171': ['Check for vacuum leaks', 'Clean MAF sensor',
                     'Replace fuel filter', 'Check fuel pressure'],
            'P0300': ['Replace spark plugs', 'Check ignition coils',
                     'Test fuel injectors', 'Check compression'],
            'P0420': ['Replace catalytic converter', 'Check O2 sensors',
                     'Use catalytic converter cleaner', 'Check for exhaust leaks'],
            'P0301': ['Replace spark plug cylinder 1', 'Swap coil with another cylinder',
                     'Check injector cylinder 1', 'Compression test cylinder 1']
        }

        return fixes.get(code, ['Consult service manual', 'Run additional diagnostics'])

# Usage
mechanic = MobileMechanic()

# Quick lookup
code = 'P0420'
dtc = mechanic.quick_lookup(code)
print(f"Code: {dtc.code}")
print(f"Description: {dtc.description}")
print(f"Type: {dtc.type_name}")

# Diagnose symptoms
symptoms = ['rough idle', 'misfire']
print(f"\nCodes related to symptoms {symptoms}:")
for dtc in mechanic.diagnose_symptoms(symptoms)[:5]:
    print(f"  • {dtc.code}: {dtc.description}")

# Common fixes
fixes = mechanic.common_fixes('P0171')
print(f"\nCommon fixes for P0171:")
for fix in fixes:
    print(f"  • {fix}")

# Manufacturer specific
ford_codes = mechanic.manufacturer_specific('Ford', ['P1234', 'P0171'])
print(f"\nFord-specific interpretations:")
for dtc in ford_codes:
    print(f"  • {dtc.code}: {dtc.description}")
```

### 5. Insurance Claim Processing

Validate repair claims based on diagnostic codes.

```python
class InsuranceProcessor:
    def __init__(self):
        self.db = DTCDatabase('data/dtc_codes.db')
        self.repair_costs = self._load_repair_costs()

    def _load_repair_costs(self):
        """Load typical repair costs by code type"""
        return {
            'P': {'min': 100, 'max': 2000, 'avg': 500},
            'B': {'min': 50, 'max': 1500, 'avg': 300},
            'C': {'min': 150, 'max': 3000, 'avg': 800},
            'U': {'min': 100, 'max': 1000, 'avg': 400}
        }

    def validate_claim(self, claim_codes, claimed_amount):
        """Validate insurance claim based on codes"""
        if not claim_codes:
            return {'valid': False, 'reason': 'No diagnostic codes provided'}

        total_estimated = 0
        code_details = []

        for code in claim_codes:
            dtc = self.db.get_dtc(code)
            if not dtc:
                return {'valid': False, 'reason': f'Invalid code: {code}'}

            cost_range = self.repair_costs[dtc.type]
            code_details.append({
                'code': code,
                'description': dtc.description,
                'estimated_cost': cost_range['avg']
            })
            total_estimated += cost_range['avg']

        # Validate claimed amount
        variance = abs(claimed_amount - total_estimated) / total_estimated
        valid = variance < 0.5  # Within 50% variance

        return {
            'valid': valid,
            'codes': code_details,
            'estimated_total': total_estimated,
            'claimed_amount': claimed_amount,
            'variance_percentage': variance * 100,
            'recommendation': 'Approve' if valid else 'Review required'
        }

    def risk_assessment(self, codes):
        """Assess vehicle risk based on codes"""
        risk_score = 0
        risk_factors = []

        for code in codes:
            dtc = self.db.get_dtc(code)
            if not dtc:
                continue

            # Assess risk based on code type and description
            if dtc.type == 'B' and 'airbag' in dtc.description.lower():
                risk_score += 30
                risk_factors.append('Safety system issue')
            elif dtc.type == 'C' and 'brake' in dtc.description.lower():
                risk_score += 25
                risk_factors.append('Braking system issue')
            elif dtc.type == 'P' and 'emission' in dtc.description.lower():
                risk_score += 10
                risk_factors.append('Emissions issue')
            elif dtc.type == 'U':
                risk_score += 15
                risk_factors.append('Communication issue')
            else:
                risk_score += 5

        risk_level = 'Low' if risk_score < 20 else 'Medium' if risk_score < 50 else 'High'

        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'factors': risk_factors,
            'recommendation': 'Standard rate' if risk_level == 'Low' else
                            'Increased premium' if risk_level == 'Medium' else
                            'Detailed inspection required'
        }

# Usage
processor = InsuranceProcessor()

# Validate claim
codes = ['P0420', 'P0171', 'P0300']
claim = processor.validate_claim(codes, 1200)
print("Insurance Claim Validation:")
print(f"  Valid: {claim['valid']}")
print(f"  Estimated: ${claim['estimated_total']}")
print(f"  Claimed: ${claim['claimed_amount']}")
print(f"  Variance: {claim['variance_percentage']:.1f}%")
print(f"  Recommendation: {claim['recommendation']}")

# Risk assessment
risk = processor.risk_assessment(['B0001', 'C0035', 'P0420'])
print(f"\nRisk Assessment:")
print(f"  Score: {risk['risk_score']}")
print(f"  Level: {risk['risk_level']}")
print(f"  Factors: {', '.join(risk['factors'])}")
print(f"  Recommendation: {risk['recommendation']}")
```

## Advanced Features

### Custom Search Filters

```python
def advanced_search(db, **filters):
    """Advanced search with multiple filters"""
    results = []

    # Start with type filter
    if 'type' in filters:
        codes = db.get_by_type(filters['type'], limit=1000)
    else:
        # Get all codes
        codes = []
        for t in ['P', 'B', 'C', 'U']:
            codes.extend(db.get_by_type(t, limit=1000))

    # Apply manufacturer filter
    if 'manufacturer' in filters:
        mfg_codes = db.get_manufacturer_codes(filters['manufacturer'])
        codes = [c for c in codes if any(m.code == c.code for m in mfg_codes)]

    # Apply keyword filter
    if 'keywords' in filters:
        for keyword in filters['keywords']:
            codes = [c for c in codes if keyword.lower() in c.description.lower()]

    return codes[:filters.get('limit', 50)]

# Usage
results = advanced_search(db,
                        type='P',
                        keywords=['sensor', 'oxygen'],
                        limit=10)
```

### Export Functionality

```python
import json
import csv

def export_to_json(codes, filename):
    """Export codes to JSON"""
    data = []
    for code in codes:
        data.append({
            'code': code.code,
            'description': code.description,
            'type': code.type,
            'type_name': code.type_name,
            'manufacturer': code.manufacturer
        })

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def export_to_csv(codes, filename):
    """Export codes to CSV"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Code', 'Type', 'Manufacturer', 'Description'])

        for code in codes:
            writer.writerow([code.code, code.type,
                           code.manufacturer, code.description])

# Usage
search_results = db.search('misfire')
export_to_json(search_results, 'misfire_codes.json')
export_to_csv(search_results, 'misfire_codes.csv')
```

## Best Practices

### 1. Resource Management

Always close database connections:

```python
# Using try-finally
db = DTCDatabase()
try:
    # Your code here
    dtc = db.get_dtc('P0420')
finally:
    db.close()

# Using context manager (if implemented)
with DTCDatabase() as db:
    dtc = db.get_dtc('P0420')
```

### 2. Error Handling

```python
def safe_lookup(code):
    try:
        db = DTCDatabase()
        dtc = db.get_dtc(code)

        if dtc is None:
            print(f"Code {code} not found")
            return None

        return dtc

    except Exception as e:
        print(f"Error looking up {code}: {e}")
        return None

    finally:
        db.close()
```

### 3. Performance Optimization

Cache frequently accessed codes:

```python
class CachedDTCDatabase:
    def __init__(self):
        self.db = DTCDatabase()
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def get_dtc(self, code):
        if code in self.cache:
            self.cache_hits += 1
            return self.cache[code]

        self.cache_misses += 1
        dtc = self.db.get_dtc(code)
        if dtc:
            self.cache[code] = dtc
        return dtc

    def get_stats(self):
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate
        }
```

## Integration Examples

### With OBD-II Libraries

```python
import obd  # python-OBD library

def diagnose_with_obd():
    """Read codes from vehicle and diagnose"""
    # Connect to vehicle
    connection = obd.OBD()

    # Read DTCs
    cmd = obd.commands.GET_DTC
    response = connection.query(cmd)

    # Initialize DTC database
    db = DTCDatabase()

    # Process codes
    for code in response.value:
        dtc = db.get_dtc(code)
        if dtc:
            print(f"{dtc.code}: {dtc.description}")
            print(f"  Type: {dtc.type_name}")
            print(f"  Manufacturer: {dtc.manufacturer}")

    db.close()
    connection.close()
```

### With Web Frameworks (Flask)

```python
from flask import Flask, jsonify
from python.dtc_database import DTCDatabase

app = Flask(__name__)
db = DTCDatabase()

@app.route('/api/dtc/<code>')
def get_code(code):
    dtc = db.get_dtc(code)
    if dtc:
        return jsonify({
            'code': dtc.code,
            'description': dtc.description,
            'type': dtc.type_name
        })
    return jsonify({'error': 'Code not found'}), 404

@app.route('/api/search/<term>')
def search(term):
    results = db.search(term, limit=20)
    return jsonify([{
        'code': dtc.code,
        'description': dtc.description
    } for dtc in results])

if __name__ == '__main__':
    app.run(debug=True)
```

## Support

For questions or issues:
- **GitHub**: https://github.com/Wal33D/dtc-database
- **Author**: Waleed Judah (Wal33D)
- **Email**: aquataze@yahoo.com
