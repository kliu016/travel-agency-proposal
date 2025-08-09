#!/usr/bin/env python3
"""
Migrate rental_car_bookings table to match CSV structure
17 changes needed, 58 rows
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

class RentalCarBookingsMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.csv_file = 'Rental Vehicles-Rental Vehicles - Master.csv'
        self.table_name = 'rental_car_bookings'
        
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
        """Update schema to match CSV"""
        logging.info("\n🔧 Updating schema...")
        
        # Disable foreign key checks
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        try:
            # Rename columns to match CSV
            renames = [
                ("traveler_id", "Traveler", "VARCHAR(255)"),
                ("client_id", "Client", "VARCHAR(255)"),
                ("commission", "Commission", "VARCHAR(100)")
            ]
            
            for old_name, new_name, col_type in renames:
                self.cursor.execute(f"""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = %s 
                    AND COLUMN_NAME = %s
                """, (os.getenv('DB_NAME'), self.table_name, old_name))
                
                if self.cursor.fetchone():
                    alter_stmt = f"ALTER TABLE {self.table_name} CHANGE COLUMN `{old_name}` `{new_name}` {col_type}"
                    self.cursor.execute(alter_stmt)
                    logging.info(f"✅ Renamed {old_name} → {new_name}")
            
            # Add missing columns
            new_columns = [
                ("Date", "DATE"),
                ("Provider", "VARCHAR(255)"),
                ("Pick Up Date", "DATE"),
                ("Pick Up Location", "VARCHAR(255)"),
                ("Drop Off Date", "DATE"),
                ("Drop Off Location", "VARCHAR(255)"),
                ("Confirmation", "VARCHAR(255)"),
                ("Estimated Rate", "VARCHAR(100)"),
                ("Base Total", "VARCHAR(100)"),
                ("Actual Final", "VARCHAR(100)"),
                ("Invoice", "VARCHAR(255)"),
                ("Agent", "VARCHAR(255)"),
                ("Submission Status", "VARCHAR(100)"),
                ("Notes", "TEXT")
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
            # Parse dates
            def parse_date(date_str):
                if pd.notna(date_str):
                    try:
                        return pd.to_datetime(date_str).date()
                    except:
                        logging.warning(f"Could not parse date: {date_str}")
                return None
            
            record = {
                'Date': parse_date(row['Date']),
                'Traveler': row['Traveler'] if pd.notna(row['Traveler']) else None,
                'Client': row['Client'] if pd.notna(row['Client']) else None,
                'Provider': row['Provider'] if pd.notna(row['Provider']) else None,
                'Pick Up Date': parse_date(row['Pick Up Date']),
                'Pick Up Location': row['Pick Up Location'] if pd.notna(row['Pick Up Location']) else None,
                'Drop Off Date': parse_date(row['Drop Off Date']),
                'Drop Off Location': row['Drop Off Location'] if pd.notna(row['Drop Off Location']) else None,
                'Confirmation': row['Confirmation'] if pd.notna(row['Confirmation']) else None,
                'Estimated Rate': row['Estimated Rate'] if pd.notna(row['Estimated Rate']) else None,
                'Base Total': row['Base Total'] if pd.notna(row['Base Total']) else None,
                'Actual Final': row['Actual Final'] if pd.notna(row['Actual Final']) else None,
                'Invoice': row['Invoice'] if pd.notna(row['Invoice']) else None,
                'Commission': row['Commission'] if pd.notna(row['Commission']) else None,
                'Agent': row['Agent'] if pd.notna(row['Agent']) else None,
                'Submission Status': row['Submission Status'] if pd.notna(row['Submission Status']) else None,
                'Notes': row['Notes'] if pd.notna(row['Notes']) else None
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
            SELECT `Date`, `Traveler`, `Provider`, `Pick Up Location`, `Drop Off Location` 
            FROM {self.table_name} 
            LIMIT 5
        """)
        results = self.cursor.fetchall()
        
        if results:
            logging.info("\nSample records:")
            for row in results:
                logging.info(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} → {row[4]}")

def main():
    migration = RentalCarBookingsMigration()
    
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
        
        logging.info("\n✅ Rental car bookings migration completed successfully!")
        
    except Exception as e:
        logging.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if migration.connection:
            migration.connection.close()

if __name__ == "__main__":
    logging.info("=== RENTAL CAR BOOKINGS MIGRATION ===")
    main()