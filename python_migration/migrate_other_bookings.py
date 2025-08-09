#!/usr/bin/env python3
"""
Migrate other_bookings table to match CSV structure
12 changes needed (all new columns), 12 rows
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

class OtherBookingsMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.csv_file = 'Other (Commissionable)-Grid view.csv'
        self.table_name = 'other_bookings'
        
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
        
        # Get current columns
        self.cursor.execute(f"SHOW COLUMNS FROM {self.table_name}")
        db_columns = self.cursor.fetchall()
        
        logging.info("\nCurrent database columns:")
        for col in db_columns:
            logging.info(f"  - {col[0]} ({col[1]})")
        
        # Get CSV columns
        df = pd.read_csv(self.csv_file, nrows=1)
        logging.info(f"\nCSV columns ({len(df.columns)}):")
        for col in df.columns:
            logging.info(f"  - {col}")
        
        # Count records
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        count = self.cursor.fetchone()[0]
        logging.info(f"\nCurrent records in database: {count}")
        
        df_full = pd.read_csv(self.csv_file)
        logging.info(f"Records in CSV: {len(df_full)}")
    
    def update_schema(self):
        """Update schema to match CSV - all columns are new"""
        logging.info("\n🔧 Updating schema...")
        
        # Disable foreign key checks
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        try:
            # Add all CSV columns
            new_columns = [
                ("Date", "DATE"),
                ("NAME", "VARCHAR(255)"),
                ("Clients", "VARCHAR(255)"),
                ("Type", "VARCHAR(100)"),
                ("Supplier", "VARCHAR(255)"),
                ("Details", "TEXT"),
                ("Total Rate", "VARCHAR(100)"),
                ("Supplier Confirmation", "VARCHAR(255)"),
                ("Payment Via", "VARCHAR(100)"),
                ("Attachments", "TEXT"),
                ("Attachment Summary", "TEXT"),
                ("Group copy", "VARCHAR(255)")
            ]
            
            for col_name, col_type in new_columns:
                self.cursor.execute(f"""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = %s 
                    AND COLUMN_NAME = %s
                """, (os.getenv('DB_NAME'), self.table_name, col_name))
                
                if not self.cursor.fetchone():
                    self.cursor.execute(f"ALTER TABLE {self.table_name} ADD COLUMN `{col_name}` {col_type}")
                    logging.info(f"✅ Added column: {col_name}")
            
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
        
        # Prepare data for insertion
        records = []
        for _, row in df.iterrows():
            # Parse date
            date_val = None
            if pd.notna(row['Date']):
                try:
                    date_val = pd.to_datetime(row['Date']).date()
                except:
                    logging.warning(f"Could not parse date: {row['Date']}")
            
            record = {
                'Date': date_val,
                'NAME': row['NAME'] if pd.notna(row['NAME']) else None,
                'Clients': row['Clients'] if pd.notna(row['Clients']) else None,
                'Type': row['Type'] if pd.notna(row['Type']) else None,
                'Supplier': row['Supplier'] if pd.notna(row['Supplier']) else None,
                'Details': row['Details'] if pd.notna(row['Details']) else None,
                'Total Rate': row['Total Rate'] if pd.notna(row['Total Rate']) else None,
                'Supplier Confirmation': row['Supplier Confirmation'] if pd.notna(row['Supplier Confirmation']) else None,
                'Payment Via': row['Payment Via'] if pd.notna(row['Payment Via']) else None,
                'Attachments': row['Attachments'] if pd.notna(row['Attachments']) else None,
                'Attachment Summary': row['Attachment Summary'] if pd.notna(row['Attachment Summary']) else None,
                'Group copy': row['Group copy'] if pd.notna(row['Group copy']) else None
            }
            records.append(record)
        
        # Insert data
        if records:
            columns = list(records[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join([f"`{col}`" for col in columns])
            
            insert_query = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})"
            
            data_tuples = [tuple(record[col] for col in columns) for record in records]
            
            self.cursor.executemany(insert_query, data_tuples)
            self.connection.commit()
            
            logging.info(f"✅ Inserted {len(data_tuples)} records")
        
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
            SELECT `Date`, `NAME`, `Type`, `Supplier`, `Total Rate` 
            FROM {self.table_name} 
            LIMIT 5
        """)
        results = self.cursor.fetchall()
        
        if results:
            logging.info("\nSample records:")
            for row in results:
                logging.info(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")

def main():
    migration = OtherBookingsMigration()
    
    try:
        if not migration.connect():
            return
        
        # Analyze current state
        migration.analyze_current_state()
        
        # Confirm
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
        
        logging.info("\n✅ Other bookings migration completed successfully!")
        
    except Exception as e:
        logging.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if migration.connection:
            migration.connection.close()

if __name__ == "__main__":
    logging.info("=== OTHER BOOKINGS MIGRATION ===")
    main()