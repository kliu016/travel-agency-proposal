#!/usr/bin/env python3
"""
Migrate air_bookings table to match CSV structure
32 changes needed, 2,805 rows - largest dataset
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

class AirBookingsMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.csv_file = 'Air-Air - Master.csv'
        self.table_name = 'air_bookings'
        
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
                ("departure_date", "Departure Date", "DATE"),
                ("traveler_id", "Traveler", "VARCHAR(255)"),
                ("client_id", "Client", "VARCHAR(255)"),
                ("airline_confirmation", "Airline Confirmation", "VARCHAR(100)"),
                ("ticketing_date", "Ticketing Date", "DATE"),
                ("ticket_status", "Ticket Status", "VARCHAR(100)"),
                ("ticket_price", "Ticket Price", "VARCHAR(100)"),
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
            
            # Add missing columns
            new_columns = [
                ("Airline-1", "VARCHAR(100)"),
                ("Flight #-1", "VARCHAR(50)"),
                ("Departure Airport-1", "VARCHAR(10)"),
                ("Departure Date-1", "DATE"),
                ("Departure Time-1", "TIME"),
                ("Arrival Airport-1", "VARCHAR(10)"),
                ("Arrival Date-1", "DATE"),
                ("Arrival Time-1", "TIME"),
                ("Airline-2", "VARCHAR(100)"),
                ("Flight #-2", "VARCHAR(50)"),
                ("Departure Airport-2", "VARCHAR(10)"),
                ("Departure Date-2", "DATE"),
                ("Departure Time-2", "TIME"),
                ("Arrival Airport-2", "VARCHAR(10)"),
                ("Arrival Date-2", "DATE"),
                ("Arrival Time-2", "TIME"),
                ("Sabre PNR", "VARCHAR(100)"),
                ("Ticket #", "VARCHAR(100)"),
                ("Ticketing Agent", "VARCHAR(255)"),
                ("Service Fee", "VARCHAR(100)"),
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
        for idx, row in df.iterrows():
            # Parse dates and times
            def parse_date(date_str):
                if pd.notna(date_str):
                    try:
                        return pd.to_datetime(date_str).date()
                    except:
                        return None
                return None
            
            def parse_time(time_str):
                if pd.notna(time_str):
                    try:
                        return pd.to_datetime(time_str).time()
                    except:
                        return None
                return None
            
            record = {
                'Departure Date': parse_date(row['Departure Date']),
                'Traveler': row['Traveler'] if pd.notna(row['Traveler']) else None,
                'Client': row['Client'] if pd.notna(row['Client']) else None,
                'Airline-1': row['Airline-1'] if pd.notna(row['Airline-1']) else None,
                'Flight #-1': row['Flight #-1'] if pd.notna(row['Flight #-1']) else None,
                'Departure Airport-1': row['Departure Airport-1'] if pd.notna(row['Departure Airport-1']) else None,
                'Departure Date-1': parse_date(row['Departure Date-1']),
                'Departure Time-1': parse_time(row['Departure Time-1']),
                'Arrival Airport-1': row['Arrival Airport-1'] if pd.notna(row['Arrival Airport-1']) else None,
                'Arrival Date-1': parse_date(row['Arrival Date-1']),
                'Arrival Time-1': parse_time(row['Arrival Time-1']),
                'Airline-2': row['Airline-2'] if pd.notna(row['Airline-2']) else None,
                'Flight #-2': row['Flight #-2'] if pd.notna(row['Flight #-2']) else None,
                'Departure Airport-2': row['Departure Airport-2'] if pd.notna(row['Departure Airport-2']) else None,
                'Departure Date-2': parse_date(row['Departure Date-2']),
                'Departure Time-2': parse_time(row['Departure Time-2']),
                'Arrival Airport-2': row['Arrival Airport-2'] if pd.notna(row['Arrival Airport-2']) else None,
                'Arrival Date-2': parse_date(row['Arrival Date-2']),
                'Arrival Time-2': parse_time(row['Arrival Time-2']),
                'Airline Confirmation': row['Airline Confirmation'] if pd.notna(row['Airline Confirmation']) else None,
                'Sabre PNR': row['Sabre PNR'] if pd.notna(row['Sabre PNR']) else None,
                'Ticket #': str(row['Ticket #']) if pd.notna(row['Ticket #']) else None,
                'Ticketing Date': parse_date(row['Ticketing Date']),
                'Ticketing Agent': row['Ticketing Agent'] if pd.notna(row['Ticketing Agent']) else None,
                'Ticket Status': row['Ticket Status'] if pd.notna(row['Ticket Status']) else None,
                'Ticket Price': row['Ticket Price'] if pd.notna(row['Ticket Price']) else None,
                'Service Fee': row['Service Fee'] if pd.notna(row['Service Fee']) else None,
                'Remarks': row['Remarks'] if pd.notna(row['Remarks']) else None,
                'assigned_agent1 (from Client)': row['assigned_agent1 (from Client)'] if pd.notna(row['assigned_agent1 (from Client)']) else None,
                'assigned_agent2 (from Client)': str(row['assigned_agent2 (from Client)']) if pd.notna(row['assigned_agent2 (from Client)']) else None,
                'coordinator1 (from Client)': row['coordinator1 (from Client)'] if pd.notna(row['coordinator1 (from Client)']) else None,
                'coordinator2 (from Client)': row['coordinator2 (from Client)'] if pd.notna(row['coordinator2 (from Client)']) else None
            }
            records.append(record)
            
            if (idx + 1) % 500 == 0:
                logging.info(f"  Processed {idx + 1}/{len(df)} records...")
        
        # Insert data in batches
        if records:
            columns = list(records[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join([f"`{col}`" for col in columns])
            
            insert_query = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})"
            
            data_tuples = [tuple(record[col] for col in columns) for record in records]
            
            # Insert in batches
            batch_size = 100
            for i in range(0, len(data_tuples), batch_size):
                batch = data_tuples[i:i+batch_size]
                self.cursor.executemany(insert_query, batch)
                self.connection.commit()
                if (i + batch_size) % 500 == 0 or i + batch_size >= len(data_tuples):
                    logging.info(f"  Inserted {min(i + batch_size, len(data_tuples))}/{len(data_tuples)} records")
            
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
            SELECT `Departure Date`, `Traveler`, `Airline-1`, `Flight #-1`, `Ticket Status` 
            FROM {self.table_name} 
            LIMIT 5
        """)
        results = self.cursor.fetchall()
        
        if results:
            logging.info("\nSample records:")
            for row in results:
                logging.info(f"  {row[0]} | {row[1]} | {row[2]} {row[3]} | Status: {row[4]}")

def main():
    migration = AirBookingsMigration()
    
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
        
        logging.info("\n✅ Air bookings migration completed successfully!")
        
    except Exception as e:
        logging.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if migration.connection:
            migration.connection.close()

if __name__ == "__main__":
    logging.info("=== AIR BOOKINGS MIGRATION ===")
    main()