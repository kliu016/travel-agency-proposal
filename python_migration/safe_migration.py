#!/usr/bin/env python3
"""
Migration script that handles foreign key constraints properly
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

class SafeMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT', 3306),
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            self.cursor = self.connection.cursor()
            logging.info("✅ Connected to database")
            return True
        except Error as e:
            logging.error(f"❌ Connection error: {e}")
            return False
    
    def check_foreign_keys(self):
        """Check foreign key constraints on clients table"""
        logging.info("\n🔍 Checking foreign key constraints...")
        
        self.cursor.execute("""
            SELECT 
                COLUMN_NAME,
                CONSTRAINT_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'clients' 
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (os.getenv('DB_NAME'),))
        
        foreign_keys = self.cursor.fetchall()
        
        if foreign_keys:
            logging.info(f"Found {len(foreign_keys)} foreign key constraints:")
            for fk in foreign_keys:
                logging.info(f"  {fk[0]} → {fk[2]}.{fk[3]} (constraint: {fk[1]})")
        
        return foreign_keys
    
    def handle_foreign_keys(self):
        """Temporarily disable foreign key checks"""
        logging.info("\n🔧 Handling foreign keys...")
        
        # Option 1: Set foreign key checks to 0 for this session
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        logging.info("✅ Disabled foreign key checks for this session")
        
        return True
    
    def restore_foreign_keys(self):
        """Re-enable foreign key checks"""
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        logging.info("✅ Re-enabled foreign key checks")
    
    def clear_data(self):
        """Clear existing data"""
        self.cursor.execute("SELECT COUNT(*) FROM clients")
        count = self.cursor.fetchone()[0]
        
        if count > 0:
            confirm = input(f"⚠️  Delete {count} existing records? (y/N): ")
            if confirm.lower() != 'y':
                return False
            
            self.cursor.execute("DELETE FROM clients")
            self.connection.commit()
            logging.info("✅ Cleared existing data")
        
        return True
    
    def migrate_data(self):
        """Migrate data with foreign key handling"""
        # Read CSV
        df = pd.read_csv("Client-Clients.csv", dtype=str)
        logging.info(f"📊 Read {len(df)} records from CSV")
        
        # Get database columns
        self.cursor.execute("SHOW COLUMNS FROM clients")
        db_columns = [col[0] for col in self.cursor.fetchall()]
        
        # Identify columns that reference other tables
        foreign_key_columns = [
            'client_enroll_by',  # References users
            'lead_agent1',       # References users
            'lead_agent2',       # References users
            'assigned_agent1',   # References users
            'assigned_agent2',   # References users
            'coordinator1',      # References users
            'coordinator2',      # References users
            'coordinator3',      # References users
            'finance1',          # References users
            'finance2',          # References users
        ]
        
        # Build insert data
        insert_data = []
        
        for idx, row in df.iterrows():
            record = {}
            
            # Map all CSV columns that exist in database
            for col in df.columns:
                if col in db_columns:
                    value = row[col]
                    
                    # Handle foreign key columns specially
                    if col in foreign_key_columns:
                        # For now, set these to NULL since we don't have users yet
                        record[col] = None
                    elif pd.isna(value) or str(value).strip() == '' or str(value) == 'nan':
                        record[col] = None
                    else:
                        # Clean currency values
                        if any(x in col for x in ['fee', 'charge', '_tf', 'refund']):
                            try:
                                cleaned = str(value).replace('$', '').replace(',', '').strip()
                                record[col] = float(cleaned) if cleaned else None
                            except:
                                record[col] = None
                        else:
                            record[col] = str(value).strip()
            
            # Handle special required fields
            if 'cid' in db_columns and 'cid' not in record:
                # Generate cid based on CLIENT_ID
                client_id = record.get('CLIENT_ID', '')
                if client_id.startswith('L'):
                    try:
                        record['cid'] = int(client_id[1:]) - 299
                    except:
                        record['cid'] = idx + 1
                elif client_id.startswith('X'):
                    try:
                        record['cid'] = int(client_id[1:]) + 500
                    except:
                        record['cid'] = idx + 1000
                else:
                    record['cid'] = idx + 2000
            
            if 'status' in db_columns and 'status' not in record:
                record['status'] = 'Active'
            
            insert_data.append(record)
        
        # Log what we're importing
        logging.info(f"\n📝 Prepared {len(insert_data)} records for import")
        
        # Check specific fields
        sample_fields = ['CLIENT_ID', 'client_name', 'delta_business', 'enterprise_contract', 
                        'air_domestic_ticketfee', 'cc1_type', 'client_enroll_by', 'lead_agent1']
        
        logging.info("\nField population check:")
        for field in sample_fields:
            if field in insert_data[0]:
                non_null = sum(1 for r in insert_data if r.get(field) is not None)
                logging.info(f"  {field}: {non_null} non-null values")
        
        # Build insert query
        if insert_data:
            columns_to_insert = list(insert_data[0].keys())
            columns_str = ', '.join([f"`{col}`" for col in columns_to_insert])
            placeholders = ', '.join(['%s'] * len(columns_to_insert))
            
            insert_query = f"INSERT INTO clients ({columns_str}) VALUES ({placeholders})"
            
            # Convert to tuples
            data_tuples = []
            for record in insert_data:
                data_tuples.append(tuple(record[col] for col in columns_to_insert))
            
            # Show sample
            logging.info("\nSample data (first record):")
            for i, (col, val) in enumerate(zip(columns_to_insert[:10], data_tuples[0][:10])):
                logging.info(f"  {col}: {val}")
            
            confirm = input("\nProceed with import? (y/N): ")
            if confirm.lower() == 'y':
                try:
                    # Disable foreign key checks
                    self.handle_foreign_keys()
                    
                    # Execute insert
                    self.cursor.executemany(insert_query, data_tuples)
                    self.connection.commit()
                    logging.info(f"✅ Successfully imported {len(data_tuples)} records")
                    
                    # Re-enable foreign key checks
                    self.restore_foreign_keys()
                    
                    # Verify import
                    self.verify_import()
                    
                except Error as e:
                    logging.error(f"❌ Import error: {e}")
                    self.connection.rollback()
                    self.restore_foreign_keys()
            else:
                logging.info("Import cancelled")
    
    def verify_import(self):
        """Verify the import worked correctly"""
        logging.info("\n🔍 Verifying import...")
        
        # Check total count
        self.cursor.execute("SELECT COUNT(*) FROM clients")
        count = self.cursor.fetchone()[0]
        logging.info(f"Total records: {count}")
        
        # Check specific fields that were mentioned as missing
        check_queries = [
            ("Records with delta_business", "SELECT COUNT(*) FROM clients WHERE delta_business IS NOT NULL AND delta_business != ''"),
            ("Records with enterprise_contract", "SELECT COUNT(*) FROM clients WHERE enterprise_contract IS NOT NULL AND enterprise_contract != ''"),
            ("Records with air_domestic_ticketfee", "SELECT COUNT(*) FROM clients WHERE air_domestic_ticketfee IS NOT NULL AND air_domestic_ticketfee > 0"),
            ("Records with cc1_type", "SELECT COUNT(*) FROM clients WHERE cc1_type IS NOT NULL AND cc1_type != ''"),
            ("Records with rates_as_of", "SELECT COUNT(*) FROM clients WHERE rates_as_of IS NOT NULL"),
        ]
        
        logging.info("\nData population verification:")
        for desc, query in check_queries:
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]
            logging.info(f"  {desc}: {count}")
        
        # Show sample records with business data
        logging.info("\nSample records with business program data:")
        self.cursor.execute("""
            SELECT CLIENT_ID, client_name, 
                   SUBSTRING(delta_business, 1, 20) as delta,
                   SUBSTRING(enterprise_contract, 1, 20) as enterprise,
                   air_domestic_ticketfee
            FROM clients
            WHERE (delta_business IS NOT NULL AND delta_business != '')
               OR (enterprise_contract IS NOT NULL AND enterprise_contract != '')
            LIMIT 5
        """)
        
        results = self.cursor.fetchall()
        for row in results:
            logging.info(f"  {row[0]}: {row[1]}")
            logging.info(f"    Delta: {row[2]}, Enterprise: {row[3]}, Air Fee: ${row[4]}")

def main():
    migration = SafeMigration()
    
    try:
        if not migration.connect():
            return
        
        # Check foreign keys
        migration.check_foreign_keys()
        
        # Clear existing data
        if not migration.clear_data():
            return
        
        # Migrate data
        migration.migrate_data()
        
    except Exception as e:
        logging.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if migration.connection:
            migration.connection.close()

if __name__ == "__main__":
    main()