#!/usr/bin/env python3
"""
Migrate hotel_transient_bookings table to match CSV structure
26 changes needed, 677 rows
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

class HotelTransientBookingsMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.csv_file = 'Hotel (Transient)-Hotel (Transient) - Master.csv'
        self.table_name = 'hotel_transient_bookings'
        
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
                ("check_in_date", "C/I Date", "DATE"),
                ("traveler_id", "Traveler", "VARCHAR(255)"),
                ("client_id", "Client", "VARCHAR(255)"),
                ("gross_total", "Gross Total", "VARCHAR(100)"),
                ("status", "Status", "VARCHAR(100)"),
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
                ("Hotel", "VARCHAR(255)"),
                ("# of Nights", "INT"),
                ("Net Rate", "VARCHAR(100)"),
                ("Gross Rate", "VARCHAR(100)"),
                ("Hotel Confirmation", "VARCHAR(255)"),
                ("Sabre PNR (If any)", "VARCHAR(100)"),
                ("Commission Rate", "VARCHAR(100)"),
                ("TPI / TTA / Invoice", "VARCHAR(255)"),
                ("CCA Status", "VARCHAR(100)"),
                ("CCA", "VARCHAR(255)"),
                ("Folio Received", "VARCHAR(100)"),
                ("Folio", "TEXT"),
                ("Folio Sent to Client", "VARCHAR(100)"),
                ("Hotel Docs", "TEXT"),
                ("VVIP", "VARCHAR(50)"),
                ("Called to Confirm", "VARCHAR(100)"),
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
            # Parse date
            ci_date = None
            if pd.notna(row['C/I Date']):
                try:
                    ci_date = pd.to_datetime(row['C/I Date']).date()
                except:
                    logging.warning(f"Could not parse date: {row['C/I Date']}")
            
            # Parse nights
            nights = None
            if pd.notna(row['# of Nights']):
                try:
                    nights = int(row['# of Nights'])
                except:
                    pass
            
            record = {
                'C/I Date': ci_date,
                'Traveler': row['Traveler'] if pd.notna(row['Traveler']) else None,
                'Client': row['Client'] if pd.notna(row['Client']) else None,
                'Hotel': row['Hotel'] if pd.notna(row['Hotel']) else None,
                '# of Nights': nights,
                'Net Rate': row['Net Rate'] if pd.notna(row['Net Rate']) else None,
                'Gross Rate': row['Gross Rate'] if pd.notna(row['Gross Rate']) else None,
                'Gross Total': row['Gross Total'] if pd.notna(row['Gross Total']) else None,
                'Hotel Confirmation': row['Hotel Confirmation'] if pd.notna(row['Hotel Confirmation']) else None,
                'Status': row['Status'] if pd.notna(row['Status']) else None,
                'Sabre PNR (If any)': row['Sabre PNR (If any)'] if pd.notna(row['Sabre PNR (If any)']) else None,
                'Commission Rate': row['Commission Rate'] if pd.notna(row['Commission Rate']) else None,
                'TPI / TTA / Invoice': row['TPI / TTA / Invoice'] if pd.notna(row['TPI / TTA / Invoice']) else None,
                'CCA Status': row['CCA Status'] if pd.notna(row['CCA Status']) else None,
                'CCA': row['CCA'] if pd.notna(row['CCA']) else None,
                'Folio Received': row['Folio Received'] if pd.notna(row['Folio Received']) else None,
                'Folio': row['Folio'] if pd.notna(row['Folio']) else None,
                'Folio Sent to Client': row['Folio Sent to Client'] if pd.notna(row['Folio Sent to Client']) else None,
                'Remarks': row['Remarks'] if pd.notna(row['Remarks']) else None,
                'Hotel Docs': row['Hotel Docs'] if pd.notna(row['Hotel Docs']) else None,
                'VVIP': row['VVIP'] if pd.notna(row['VVIP']) else None,
                'Called to Confirm': row['Called to Confirm'] if pd.notna(row['Called to Confirm']) else None,
                'assigned_agent1 (from Client)': row['assigned_agent1 (from Client)'] if pd.notna(row['assigned_agent1 (from Client)']) else None,
                'assigned_agent2 (from Client)': str(row['assigned_agent2 (from Client)']) if pd.notna(row['assigned_agent2 (from Client)']) else None,
                'coordinator1 (from Client)': row['coordinator1 (from Client)'] if pd.notna(row['coordinator1 (from Client)']) else None,
                'coordinator2 (from Client)': row['coordinator2 (from Client)'] if pd.notna(row['coordinator2 (from Client)']) else None
            }
            records.append(record)
        
        # Insert data
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
            SELECT `C/I Date`, `Traveler`, `Hotel`, `# of Nights`, `Status` 
            FROM {self.table_name} 
            LIMIT 5
        """)
        results = self.cursor.fetchall()
        
        if results:
            logging.info("\nSample records:")
            for row in results:
                logging.info(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} nights | {row[4]}")

def main():
    migration = HotelTransientBookingsMigration()
    
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
        
        logging.info("\n✅ Hotel transient bookings migration completed successfully!")
        
    except Exception as e:
        logging.error(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if migration.connection:
            migration.connection.close()

if __name__ == "__main__":
    logging.info("=== HOTEL TRANSIENT BOOKINGS MIGRATION ===")
    main()