# ProGuard rules for DTC Database Android library

# Keep public API
-keep class com.dtcdatabase.DTCDatabase { *; }
-keep class com.dtcdatabase.DTCDatabase$DTC { *; }

# Keep SQLite database operations
-keep class android.database.** { *; }
-keep class android.database.sqlite.** { *; }

# Keep Cursor operations
-keepclassmembers class * extends android.database.sqlite.SQLiteOpenHelper {
    public <init>(...);
}

# Don't warn about missing classes
-dontwarn android.database.**
