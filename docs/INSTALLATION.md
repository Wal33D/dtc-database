# Installation Guide

## Requirements

### Core Data

- File: `data/dtc_codes.db`
- Size: ~3.1 MB
- Schema: `dtc_definitions(code, manufacturer, description, type, locale, is_generic, source_file)`

### Runtime Requirements

- Python: 3.8+
- Java: 8+ (SQLite JDBC required in your application)
- Android: standard Android SQLite APIs (module provided in `android/`)
- TypeScript: Node.js 18+ for dev/build/test workflow

## Clone Repository

```bash
git clone https://github.com/Wal33D/dtc-database.git
cd dtc-database
```

## Python Setup

No package install is required for this repository version.

```python
from python.dtc_database import DTCDatabase

db = DTCDatabase("data/dtc_codes.db")
print(db.get_description("P0420"))
db.close()
```

## Java Setup

Use `java/DTCDatabaseCore.java` and add SQLite JDBC to your project.

### Maven

```xml
<dependency>
  <groupId>org.xerial</groupId>
  <artifactId>sqlite-jdbc</artifactId>
  <version>3.45.3.0</version>
</dependency>
```

### Gradle

```gradle
dependencies {
  implementation "org.xerial:sqlite-jdbc:3.45.3.0"
}
```

### Java Usage Check

```java
import com.dtcdatabase.DTCDatabaseCore;

DTCDatabaseCore db = new DTCDatabaseCore("data/dtc_codes.db");
System.out.println(db.getDescription("P0171"));
db.close();
```

## Android Setup

Use the module in `android/dtc-database-android/`:

```gradle
// settings.gradle
include(":dtc-database-android")
project(":dtc-database-android").projectDir = file("android/dtc-database-android")
```

```gradle
// app/build.gradle
dependencies {
  implementation(project(":dtc-database-android"))
}
```

`dtc_codes.db` is already included under:
`android/dtc-database-android/src/main/assets/dtc_codes.db`

## TypeScript Setup (Source Workflow)

The TypeScript module is currently maintained in-repo.

```bash
cd typescript
npm install
npm run build
npm test
```

## Verification Commands

From repository root:

```bash
python3 test.py
python3 test_schema.py
cd typescript && npm test
```

## Common Issues

### Database not found

Use an absolute or repository-relative DB path:

```python
db = DTCDatabase("data/dtc_codes.db")
```

```java
DTCDatabaseCore db = new DTCDatabaseCore("data/dtc_codes.db");
```

### TypeScript tests fail with `jest: command not found`

Install dependencies first:

```bash
cd typescript
npm install
```
