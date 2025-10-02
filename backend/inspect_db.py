#!/usr/bin/env python3
"""
SQLite Database Inspector
Simple script to check the contents of your quiz database
"""

import sqlite3
import json
from pathlib import Path

def inspect_database():
    # Database path
    db_path = Path("quiz.db")
    
    if not db_path.exists():
        print("❌ Database file 'quiz.db' not found!")
        return
    
    print("🗃️  SQLite Database Inspector")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   • {table['name']}")
        
        print("\n" + "=" * 50)
        
        # Inspect each table
        for table in tables:
            table_name = table['name']
            print(f"\n📊 TABLE: {table_name}")
            print("-" * 30)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("🏗️  Schema:")
            for col in columns:
                nullable = "NULL" if col['notnull'] == 0 else "NOT NULL"
                pk = " (PRIMARY KEY)" if col['pk'] else ""
                print(f"   {col['name']}: {col['type']} {nullable}{pk}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
            count = cursor.fetchone()['count']
            print(f"\n📈 Total rows: {count}")
            
            # Show sample data (first 5 rows)
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = cursor.fetchall()
                
                print(f"\n📄 Sample data (first {min(5, count)} rows):")
                for i, row in enumerate(rows, 1):
                    print(f"   Row {i}:")
                    for key in row.keys():
                        value = row[key]
                        # Pretty print JSON columns
                        if isinstance(value, str) and (key == 'options' or value.startswith('[')):
                            try:
                                parsed = json.loads(value)
                                value = json.dumps(parsed, indent=2)
                            except:
                                pass
                        print(f"     {key}: {value}")
                    print()
            
            print("-" * 50)
        
        conn.close()
        print("\n✅ Database inspection completed!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_database()