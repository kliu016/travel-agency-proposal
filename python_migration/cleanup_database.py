#!/usr/bin/env python3
"""
Clean up MySQL database - remove tables without CSV data
"""

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

def cleanup_database():
    """Remove tables that don't have corresponding CSV files"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', 3306)
        )
        cursor = connection.cursor()
        
        logging.info("✅ Connected to database")
        
        # Tables to drop (no CSV files for these)
        tables_to_drop = [
            'airport_greeter_bookings',  # No CSV file found
            'audit_log',                 # System table, no CSV
            'invoices',                  # No CSV file
            'users',                     # No CSV file (Kyle will provide later)
            'clients_backup_before_schema_change'  # Backup table
        ]
        
        # Views to drop
        views_to_drop = [
            'client_summary',
            'upcoming_bookings'
        ]
        
        # Drop views first
        logging.info("\n🔧 Dropping unnecessary views...")
        for view in views_to_drop:
            try:
                cursor.execute(f"DROP VIEW IF EXISTS {view}")
                logging.info(f"✅ Dropped view: {view}")
            except Error as e:
                logging.warning(f"⚠️  Could not drop view {view}: {e}")
        
        # Drop tables
        logging.info("\n🔧 Dropping unnecessary tables...")
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                logging.info(f"✅ Dropped table: {table}")
            except Error as e:
                logging.warning(f"⚠️  Could not drop table {table}: {e}")
        
        connection.commit()
        
        # Show remaining tables
        cursor.execute("SHOW TABLES")
        remaining_tables = cursor.fetchall()
        
        logging.info("\n📊 Remaining tables in database:")
        for table in remaining_tables:
            logging.info(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        logging.error(f"❌ Database error: {e}")

if __name__ == "__main__":
    logging.info("=== DATABASE CLEANUP ===")
    
    confirm = input("\n⚠️  This will drop tables without CSV data. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        cleanup_database()
    else:
        logging.info("Cleanup cancelled")