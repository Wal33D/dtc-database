# Setup Instructions

## Python (✅ VERIFIED WORKING)
```bash
# No dependencies needed, uses built-in sqlite3
python3 build-database.py  # Build database
python3 test.py            # Run tests
```

## Java (Requires Dependencies)
```bash
# Download required JARs:
curl -L -o sqlite-jdbc.jar https://github.com/xerial/sqlite-jdbc/releases/download/3.44.1.0/sqlite-jdbc-3.44.1.0.jar
curl -L -o slf4j-api.jar https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.9/slf4j-api-2.0.9.jar
curl -L -o slf4j-simple.jar https://repo1.maven.org/maven2/org/slf4j/slf4j-simple/2.0.9/slf4j-simple-2.0.9.jar

# Compile and run:
javac -d . java/DTCDatabaseCore.java
java -cp .:sqlite-jdbc.jar:slf4j-api.jar:slf4j-simple.jar TestJava
```

## TypeScript/Node.js
```bash
cd typescript
npm install better-sqlite3 @types/better-sqlite3 @types/node ts-node typescript
npx ts-node query-simple.ts P0171
```

## Android
- Copy `android/DTCDatabase.java` to your Android project
- Add to app/build.gradle:
```gradle
dependencies {
    implementation 'androidx.sqlite:sqlite:2.3.1'
}
```
- Copy `dtc_codes.db` to `app/src/main/assets/`
- Use `DTCDatabase.getInstance(context)` in your activities

## Database Stats
- **12,129** unique codes after deduplication
- **18,821** total entries in source files (includes duplicates)
- **2,752** manufacturer-specific codes
- **4** code types: P (8189), B (1447), C (966), U (1527)