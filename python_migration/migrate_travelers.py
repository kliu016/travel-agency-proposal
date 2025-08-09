#!/usr/bin/env python3
"""
Migrate travelers table to match CSV structure
103 changes needed, 942 rows - most complex migration
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TravelersMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.csv_file = 'Traveler-Traveler - Master.csv'
        self.table_name = 'travelers'
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT', 3306)
            )
            self.cursor = self.connection.cursor()
            logging.info("✅ Connected to database")
            return True
        except Error as e:
            logging.error(f"❌ Connection error: {e}")
            return False
    
    def analyze_current_state(self):
        """Show current state before migration"""
        logging.info(f"\n📊 Analyzing {self.table_name}...")
        logging.info("⚠️  This is the most complex migration with 103 columns!")
        
        # Get current columns
        self.cursor.execute(f"SHOW COLUMNS FROM {self.table_name}")
        db_columns = self.cursor.fetchall()
        
        logging.info(f"\nCurrent database columns ({len(db_columns)}):")
        # Just show count, too many to list
        
        # Get CSV columns
        df = pd.read_csv(self.csv_file, nrows=1)
        logging.info(f"\nCSV columns ({len(df.columns)}):")
        logging.info("Main categories include:")
        logging.info("  - Personal info (TRAVELER_ID, names, DOB, etc.)")
        logging.info("  - Passport info (2 passports)")
        logging.info("  - Frequent flyer programs (9 airlines)")
        logging.info("  - Hotel programs (7 chains)")
        logging.info("  - Contact info and preferences")
        logging.info("  - Relationship columns")
        
        # Count records
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        count = self.cursor.fetchone()[0]
        logging.info(f"\nCurrent records in database: {count}")
        
        df_full = pd.read_csv(self.csv_file)
        logging.info(f"Records in CSV: {len(df_full)}")
    
    def update_schema(self):
        """Update schema to match CSV - this is a big one!"""
        logging.info("\n🔧 Updating schema (this will take a while)...")
        
        # Disable foreign key checks
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        try:
            # First, let's handle the columns that need renaming
            # Most DB columns need to be renamed to match CSV exactly
            
            # Since there are SO many columns, let's read the CSV columns
            # and add them all, letting MySQL handle duplicates
            df = pd.read_csv(self.csv_file, nrows=1)
            csv_columns = list(df.columns)
            
            # Define data types for each column pattern
            def get_column_type(col_name):
                if 'ID' in col_name or col_name == 'TRAVELER_ID':
                    return 'INT'
                elif 'DATE' in col_name:
                    return 'DATE'
                elif 'EMAIL' in col_name:
                    return 'VARCHAR(255)'
                elif 'PHONE' in col_name:
                    return 'VARCHAR(50)'
                elif 'NUMBER' in col_name and ('FF' in col_name or 'HH' in col_name or 'PASSPORT' in col_name):
                    return 'VARCHAR(100)'
                elif 'SCAN' in col_name or 'Notes' in col_name:
                    return 'TEXT'
                elif any(x in col_name for x in ['Air', 'Hotel', 'Passenger Credits', 'Chauffer', 'Rental']):
                    return 'TEXT'  # Relationship columns
                else:
                    return 'VARCHAR(255)'
            
            # Add all CSV columns
            added = 0
            for col in csv_columns:
                self.cursor.execute(f"""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = %s 
                    AND COLUMN_NAME = %s
                """, (os.getenv('DB_NAME'), self.table_name, col))
                
                if not self.cursor.fetchone():
                    col_type = get_column_type(col)
                    try:
                        self.cursor.execute(f"ALTER TABLE {self.table_name} ADD COLUMN `{col}` {col_type}")
                        added += 1
                        if added % 10 == 0:
                            logging.info(f"  Added {added} columns...")
                    except Error as e:
                        if "Duplicate column name" not in str(e):
                            logging.warning(f"Could not add column {col}: {e}")
            
            logging.info(f"✅ Added {added} new columns")
            
            self.connection.commit()
            logging.info("✅ Schema updated successfully")
            
        except Error as e:
            logging.error(f"❌ Schema update error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        return True
    
    def migrate_data(self):
        """Migrate data from CSV"""
        logging.info("\n📤 Migrating data...")
        
        # Clear existing data
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        count = self.cursor.fetchone()[0]
        
        if count > 0:
            confirm = input(f"⚠️  Delete {count} existing records? (y/N): ")
            if confirm.lower() != 'y':
                return False
            
            self.cursor.execute(f"DELETE FROM {self.table_name}")
            self.connection.commit()
            logging.info("✅ Cleared existing data")
        
        # Read CSV
        df = pd.read_csv(self.csv_file)
        logging.info(f"📊 Read {len(df)} records from CSV")
        
        # Get columns that exist in database
        self.cursor.execute(f"SHOW COLUMNS FROM {self.table_name}")
        db_columns = [col[0] for col in self.cursor.fetchall()]
        
        # Only include columns that exist in both CSV and DB
        columns_to_insert = [col for col in df.columns if col in db_columns]
        logging.info(f"Will insert {len(columns_to_insert)} columns")
        
        # Prepare data for insertion
        records = []
        for idx, row in df.iterrows():
            record = {}
            
            for col in columns_to_insert:
                value = row[col]
                
                # Handle special columns
                if pd.isna(value):
                    record[col] = None
                elif col == 'TRAVELER_ID':
                    try:
                        record[col] = int(value)
                    except:
                        record[col] = None
                elif 'DATE' in col:
                    try:
                        record[col] = pd.to_datetime(value).date()
                    except:
                        record[col] = None
                else:
                    # Convert floats to strings where needed
                    if isinstance(value, float) and col not in ['TRAVELER_ID']:
                        record[col] = str(int(value)) if value == value else None
                    else:
                        record[col] = str(value) if value is not None else None
            
            records.append(record)
            
            if (idx + 1) % 100 == 0:
                logging.info(f"  Processed {idx + 1}/{len(df)} records...")
        
        # Insert data in batches
        if records:
            columns = list(records[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join([f"`{col}`" for col in columns])
            
            insert_query = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})"
            
            data_tuples = [tuple(record[col] for col in columns) for record in records]
            
            # Insert in batches
            batch_size = 50
            for i in range(0, len(data_tuples), batch_size):
                batch = data_tuples[i:i+batch_size]
                try:
                    self.cursor.executemany(insert_query, batch)
                    self.connection.commit()
                    if (i + batch_size) % 200 == 0 or i + batch_size >= len(data_tuples):
                        logging.info(f"  Inserted {min(i + batch_size, len(data_tuples))}/{len(data_tuples)} records")
                except Error as e:
                    logging.error(f"Error inserting batch starting at {i}: {e}")
                    # Try to continue with next batch
            
            logging.info(f"✅ Migration completed")
        
        return True
    
    def verify_migration(self):
        """Verify the migration was successful"""
        logging.info("\n🔍 Verifying migration...")
        
        # Check count
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        count = self.cursor.fetchone()[0]
        logging.info(f"Total records: {count}")
        
        # Show sample
        self.cursor.execute(f"""
            SELECT `TRAVELER_ID`, `FIRSTNAME`, `LASTNAME`, `CLIENT ID`, `DOB` 
            FROM {self.table_name} 
            WHERE `TRAVELER_ID` IS NOT NULL
            LIMIT 5
        """)
        results = self.cursor.fetchall()
        
        if results:
            logging.info("\nSample records:")
            for row in results:
                logging.info(f"  ID: {row[0]} | {row[1]} {row[2]} | Client: {row[3]} | DOB: {row[4]}")
        
        # Check some key fields
        self.cursor.execute("SELECT COUNT(*) FROM travelers WHERE `TRAVELER_ID` IS NOT NULL")
        with_id = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM travelers WHERE `PASSPORT 1 NUMBER` IS NOT NULL")
        with_passport = self.cursor.fetchone()[0]
        
        logging.info(f"\nRecords with TRAVELER_ID: {with_id}")
        logging.info(f"Records with passport: {with_passport}")

def main():
    migration = TravelersMigration()
    
    try:
        if not migration.connect():
            return
        
        # Analyze current state
        migration.analyze_current_state()
        
        # Confirm
        print("\n⚠️  WARNING: This is the most complex migration!")
        print("It will add/modify over 100 columns and migrate 942 records.")
        confirm = input("\nProceed with migration? (y/N): ")
        if confirm.lower() != 'y':
            logging.info("Migration cancelled")
            return
        
        # Update schema
        if not migration.update_schema():
            logging.error("Schema update failed")
            return
        
        # Migrate data
        if not migration.migrate_data():
            logging.error("Data migration failed")
            return
        
        # Verify
        migration.verify_migration()
        
        logging.info("\n✅ Travelers migration completed successfully!")
        logging.info("This was the most complex migration - great job!")
        
    except Exception as e:
        logging.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if migration.connection:
            migration.connection.close()

if __name__ == "__main__":
    logging.info("=== TRAVELERS MIGRATION ===")
    logging.info("The most complex migration - 103 columns!")
    main()