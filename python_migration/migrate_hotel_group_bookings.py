#!/usr/bin/env python3
"""
Migrate hotel_group_bookings table to match CSV structure
41 changes needed, 126 rows
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

class HotelGroupBookingsMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.csv_file = 'Hotel (Group)-Hotel (Group) - Master.csv'
        self.table_name = 'hotel_group_bookings'
        
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
        
        logging.info(f"\nCurrent database columns ({len(db_columns)}):")
        for i, col in enumerate(db_columns):
            if i < 10:  # Show first 10
                logging.info(f"  - {col[0]} ({col[1]})")
        if len(db_columns) > 10:
            logging.info(f"  ... and {len(db_columns) - 10} more")
        
        # Get CSV columns
        df = pd.read_csv(self.csv_file, nrows=1)
        logging.info(f"\nCSV columns ({len(df.columns)}):")
        for i, col in enumerate(df.columns):
            if i < 15:  # Show first 15
                logging.info(f"  - {col}")
        if len(df.columns) > 15:
            logging.info(f"  ... and {len(df.columns) - 15} more")
        
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
                ("check_in_date", "C/I Date", "DATE"),
                ("check_out_date", "C/O Date", "DATE"),
                ("client_id", "Client", "VARCHAR(255)"),
                ("rate_type", "Rate Type", "VARCHAR(100)"),
                ("remarks", "Remarks", "TEXT")
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
            
            # Add missing columns - there are many!
            new_columns = [
                ("Touring Party", "VARCHAR(255)"),
                ("Hotel", "VARCHAR(255)"),
                ("Net Rate", "VARCHAR(100)"),
                ("Tax Rate", "VARCHAR(100)"),
                ("Gross Rate", "VARCHAR(100)"),
                ("# of Room Nights", "INT"),
                ("Gross Total", "VARCHAR(100)"),
                ("Concessions", "TEXT"),
                ("Welcome Amenity", "TEXT"),
                ("Commission Rate", "VARCHAR(100)"),
                ("Hotel Group Name/Number", "VARCHAR(255)"),
                ("IATA", "VARCHAR(100)"),
                ("Hotel Docs", "TEXT"),
                ("Notes", "TEXT"),
                ("TPI / Invoice", "VARCHAR(255)"),
                ("Arrival Via", "VARCHAR(255)"),
                ("Parking Instructions, if needed", "TEXT"),
                ("ETA", "VARCHAR(100)"),
                ("CCA Submitted", "VARCHAR(100)"),
                ("Advance Email Sent", "VARCHAR(100)"),
                ("TM Intro Email Sent", "VARCHAR(100)"),
                ("Final Folio Sent to Client", "VARCHAR(100)"),
                ("Air Grid", "TEXT"),
                ("Air Grid (as of)", "TEXT"),
                ("Sales Contact", "VARCHAR(255)"),
                ("Sales Email", "VARCHAR(255)"),
                ("Sales Phone", "VARCHAR(100)"),
                ("Coordinator Contact", "VARCHAR(255)"),
                ("Coordinator Email", "VARCHAR(255)"),
                ("Coordinator Phone", "VARCHAR(100)"),
                ("Final Folio", "TEXT"),
                ("Date Entered", "DATE"),
                ("assigned_agent1 (from Client)", "VARCHAR(255)"),
                ("assigned_agent2 (from Client)", "VARCHAR(255)"),
                ("coordinator1 (from Client)", "VARCHAR(255)"),
                ("coordinator2 (from Client)", "VARCHAR(255)")
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
                        return None
                return None
            
            # Parse room nights
            room_nights = None
            if pd.notna(row['# of Room Nights']):
                try:
                    room_nights = int(row['# of Room Nights'])
                except:
                    pass
            
            record = {}
            # Map all columns
            for col in df.columns:
                if col in ['C/I Date', 'C/O Date', 'Date Entered']:
                    record[col] = parse_date(row[col])
                elif col == '# of Room Nights':
                    record[col] = room_nights
                else:
                    record[col] = row[col] if pd.notna(row[col]) else None
                    # Convert float columns that should be string
                    if col in ['assigned_agent2 (from Client)', 'Air Grid', 'Air Grid (as of)', 'Remarks']:
                        record[col] = str(record[col]) if record[col] is not None else None
            
            records.append(record)
        
        # Insert data
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
                self.cursor.executemany(insert_query, batch)
                self.connection.commit()
                logging.info(f"  Inserted batch {i//batch_size + 1}/{(len(data_tuples)-1)//batch_size + 1}")
            
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
            SELECT `C/I Date`, `C/O Date`, `Client`, `Hotel`, `# of Room Nights` 
            FROM {self.table_name} 
            LIMIT 5
        """)
        results = self.cursor.fetchall()
        
        if results:
            logging.info("\nSample records:")
            for row in results:
                logging.info(f"  {row[0]} to {row[1]} | {row[2]} | {row[3]} | {row[4]} rooms")

def main():
    migration = HotelGroupBookingsMigration()
    
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
        
        logging.info("\n✅ Hotel group bookings migration completed successfully!")
        
    except Exception as e:
        logging.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if migration.connection:
            migration.connection.close()

if __name__ == "__main__":
    logging.info("=== HOTEL GROUP BOOKINGS MIGRATION ===")
    main()