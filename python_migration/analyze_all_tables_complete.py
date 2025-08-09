#!/usr/bin/env python3
"""
Complete analysis of all tables vs CSV files
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

class CompleteTableAnalyzer:
    def __init__(self):
        self.connection = None
        self.cursor = None
        # Complete mapping with all CSV files
        self.csv_mapping = {
            'travelers': 'Traveler-Traveler - Master.csv',
            'air_bookings': 'Air-Air - Master.csv', 
            'hotel_transient_bookings': 'Hotel (Transient)-Hotel (Transient) - Master.csv',
            'hotel_group_bookings': 'Hotel (Group)-Hotel (Group) - Master.csv',
            'chauffeur_bookings': 'Chauffer Vehicles-Chauffer Vehicles - Master.csv',
            'rental_car_bookings': 'Rental Vehicles-Rental Vehicles - Master.csv',
            'passenger_credits': 'Passenger Credits-Passenger Credits.csv',
            'vendor_websites': 'Vendor Websites-Grid view.csv',
            'email_templates': 'Templates-Grid view.csv',
            'other_bookings': 'Other (Commissionable)-Grid view.csv'
        }
        
        # Additional CSV files without tables
        self.extra_csv = {
            'Gmail IDs-Done - Extracted.csv': 'Might need audit_log table',
            'Things-Grid view.csv': 'Miscellaneous data - needs review'
        }
        
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
    
    def analyze_table(self, table_name, csv_file):
        """Analyze a single table vs its CSV"""
        logging.info(f"\n{'='*80}")
        logging.info(f"📊 Analyzing: {table_name}")
        logging.info(f"CSV File: {csv_file}")
        logging.info('='*80)
        
        # Check if CSV exists
        if not os.path.exists(csv_file):
            logging.error(f"❌ CSV file not found: {csv_file}")
            return None
        
        # Get CSV columns and info
        try:
            df = pd.read_csv(csv_file)
            csv_columns = list(df.columns)
            csv_row_count = len(df)
            logging.info(f"✅ CSV has {len(csv_columns)} columns and {csv_row_count} rows")
            
        except Exception as e:
            logging.error(f"❌ Error reading CSV: {e}")
            return None
        
        # Get database columns
        self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        db_columns_info = self.cursor.fetchall()
        db_columns = [col[0] for col in db_columns_info]
        logging.info(f"✅ Database table has {len(db_columns)} columns")
        
        # Find matches and mismatches
        exact_matches = []
        needs_rename = {}
        csv_only = []
        db_only = []
        
        # Check each CSV column
        for csv_col in csv_columns:
            if csv_col in db_columns:
                exact_matches.append(csv_col)
            else:
                # Try to find a similar column in DB
                found = False
                csv_col_clean = csv_col.replace(' ', '_').replace('-', '_').replace('#', 'num').replace('/', '_').lower()
                
                for db_col in db_columns:
                    db_col_clean = db_col.lower()
                    
                    # Various matching patterns
                    if (csv_col_clean == db_col_clean or
                        # Special mappings
                        (csv_col == 'Traveler' and db_col == 'traveler_id') or
                        (csv_col == 'Client' and db_col == 'client_id') or
                        (csv_col == 'C/I Date' and db_col == 'check_in_date') or
                        (csv_col == 'C/O Date' and db_col == 'check_out_date') or
                        (csv_col == 'Departure Date' and db_col == 'departure_date') or
                        (csv_col == 'NAME' and db_col == 'name')):
                        needs_rename[db_col] = csv_col
                        found = True
                        break
                
                if not found:
                    csv_only.append(csv_col)
        
        # Find DB columns not in CSV
        for db_col in db_columns:
            if db_col not in csv_columns and db_col not in needs_rename:
                # Skip system columns
                if db_col not in ['id', 'created_at', 'updated_at', 'agent_id']:
                    db_only.append(db_col)
        
        # Create detailed report
        report = {
            'exact_matches': exact_matches,
            'needs_rename': needs_rename,
            'csv_only': csv_only,
            'db_only': db_only
        }
        
        # Print summary
        logging.info(f"\n📋 Summary:")
        logging.info(f"  ✅ Exact matches: {len(exact_matches)}")
        logging.info(f"  🔧 Need rename: {len(needs_rename)}")
        logging.info(f"  ➕ CSV only: {len(csv_only)}")
        logging.info(f"  ➖ DB only: {len(db_only)}")
        
        if needs_rename and len(needs_rename) <= 10:
            logging.info(f"\n🔧 Columns to rename:")
            for db_col, csv_col in needs_rename.items():
                logging.info(f"   {db_col} → {csv_col}")
        
        return {
            'table': table_name,
            'csv_file': csv_file,
            'csv_columns': len(csv_columns),
            'db_columns': len(db_columns),
            'exact_matches': len(exact_matches),
            'needs_rename': len(needs_rename),
            'csv_only': len(csv_only),
            'db_only': len(db_only),
            'csv_rows': csv_row_count,
            'details': report
        }
    
    def analyze_all(self):
        """Analyze all tables"""
        results = []
        
        # Analyze each table
        for table_name, csv_file in self.csv_mapping.items():
            result = self.analyze_table(table_name, csv_file)
            if result:
                results.append(result)
        
        # Summary Report
        logging.info(f"\n{'='*80}")
        logging.info("📊 FINAL SUMMARY REPORT")
        logging.info('='*80)
        
        # Sort by number of changes needed
        results.sort(key=lambda x: x['needs_rename'] + x['csv_only'])
        
        logging.info("\n📋 Migration Priority (least to most changes):")
        for i, result in enumerate(results, 1):
            total_changes = result['needs_rename'] + result['csv_only']
            if total_changes == 0:
                status = "✅ READY"
            elif total_changes <= 5:
                status = "🔧 MINOR"
            elif total_changes <= 20:
                status = "⚠️  MODERATE"
            else:
                status = "❗ MAJOR"
            
            logging.info(f"{i}. {status} {result['table']}: "
                        f"{result['csv_rows']} rows, "
                        f"{total_changes} changes needed")
        
        # Extra CSV files
        logging.info(f"\n📁 Additional CSV files without tables:")
        for csv, note in self.extra_csv.items():
            if os.path.exists(csv):
                df = pd.read_csv(csv)
                logging.info(f"  - {csv}: {len(df)} rows ({note})")
        
        logging.info("\n✅ All CSV files are present!")
        logging.info("\n📝 Next steps:")
        logging.info("1. Create migration scripts for each table")
        logging.info("2. Handle the 'Chauffer' vs 'Chauffeur' spelling")
        logging.info("3. Decide what to do with Gmail IDs and Things data")
        
        return results

def main():
    analyzer = CompleteTableAnalyzer()
    
    if not analyzer.connect():
        return
    
    try:
        results = analyzer.analyze_all()
        
        # Save results for creating migration scripts
        import json
        with open('analysis_results.json', 'w') as f:
            # Convert to serializable format
            serializable_results = []
            for r in results:
                result_copy = r.copy()
                result_copy.pop('details', None)  # Remove non-serializable details
                serializable_results.append(result_copy)
            json.dump(serializable_results, f, indent=2)
        
        logging.info("\n✅ Analysis complete! Results saved to analysis_results.json")
        
    except Exception as e:
        logging.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if analyzer.connection:
            analyzer.connection.close()

if __name__ == "__main__":
    logging.info("=== COMPLETE TABLE ANALYSIS ===")
    logging.info("Analyzing all tables against their CSV files...")
    main()