#!/usr/bin/env python3
"""
Complete database schema update to match all 158 CSV columns exactly
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

class CompleteSchemaMapper:
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
                port=os.getenv('DB_PORT', 3306)
            )
            self.cursor = self.connection.cursor()
            logging.info("✅ Connected to database")
            return True
        except Error as e:
            logging.error(f"❌ Connection error: {e}")
            return False
    
    def get_complete_mapping(self):
        """Get complete mapping from current DB columns to CSV columns"""
        # This is the COMPLETE mapping based on the CSV analysis
        return {
            # Primary keys and identifiers
            'CLIENT_ID': 'CLIENT_ID',  # Already correct
            'cid': 'cid',  # Keep for foreign keys
            
            # Basic client info
            'name': 'client_name',
            'client_type': 'client_type',  # Already correct
            'status': 'status',  # Internal field, not in CSV
            'client_enroll_date': 'client_enroll_date',  # Already correct
            'client_enrolled_by': 'client_enroll_by',  # CSV uses client_enroll_by
            
            # Company/Client information - ALL need client_ prefix
            'company_country': 'client_country',
            'company_street_address': 'client_street_address', 
            'company_city': 'client_city',
            'company_state': 'client_state',
            'company_zip_postal': 'client_zip_postal',
            'tax_id_ein': 'client_taxid_ein',
            'w9': 'W9',  # Already correct
            'internal_notes': 'client_remarks-internal',
            
            # Contact information
            'primary_contact': 'client_primary_contact',
            'primary_email': 'client_primary_email',
            'primary_phone': 'client_primary_phone',
            'business_manager_contact': 'business_manager_contact',  # Already correct
            'business_manager_email': 'business_manager_email',  # Already correct
            'business_manager_phone': 'business_manager_phone',  # Already correct
            'additional_email_1': 'additional_email1',  # No underscore in CSV
            'additional_email_2': 'additional_email2',
            'additional_email_3': 'additional_email3',
            
            # Documents
            'service_agreement': 'service_agreement',  # Already correct
            'cca_agreement': 'cca_agreement',  # Already correct
            
            # Credit Card 1 fields
            'credit_card_1_nickname': 'cc1_nickname',
            'cc1_type': 'cc1_type',  # Already correct after previous update
            'credit_card_1_number': 'cc1_number',
            'credit_card_1_expiration': 'cc1_expiration',
            'credit_card_1_security_code': 'cc1_security',
            'credit_card_1_name': 'cc1_cardholder',
            'credit_card_1_country': 'cc1_country',
            'credit_card_1_street_address': 'cc1_street',
            'credit_card_1_city': 'cc1_city',
            'credit_card_1_state': 'cc1_state',
            'credit_card_1_zip_postal': 'cc1_zip_postal',
            'credit_card_1_scan_front': 'cc1_scan_front',
            'credit_card_1_scan_back': 'cc1_scan_back',
            'credit_card_1_id': 'cc1_id_scan',
            
            # Credit Card 2 fields
            'credit_card_2_nickname': 'cc2_nickname',
            'cc2_type': 'cc2_type',  # Already correct after previous update
            'credit_card_2_number': 'cc2_number',
            'credit_card_2_expiration': 'cc2_expiration',
            'credit_card_2_security_code': 'cc2_security',
            'credit_card_2_name': 'cc2_cardholder',
            'credit_card_2_country': 'cc2_country',
            'credit_card_2_street_address': 'cc2_street',
            'credit_card_2_city': 'cc2_city',
            'credit_card_2_state': 'cc2_state',
            'credit_card_2_zip_postal': 'cc2_zip_postal',
            'credit_card_2_scan_front': 'cc2_scan_front',
            'credit_card_2_scan_back': 'cc2_scan_back',
            'credit_card_2_id': 'cc2_id_scan',
            
            # Credit Card 3 fields
            'credit_card_3_nickname': 'cc3_nickname',
            'cc3_type': 'cc3_type',  # Already correct after previous update
            'credit_card_3_number': 'cc3_number',
            'credit_card_3_expiration': 'cc3_expiration',
            'credit_card_3_security_code': 'cc3_security',
            'credit_card_3_name': 'cc3_cardholder',
            'credit_card_3_country': 'cc3_country',
            'credit_card_3_street_address': 'cc3_street',
            'credit_card_3_city': 'cc3_city',
            'credit_card_3_state': 'cc3_state',
            'credit_card_3_zip_postal': 'cc3_zip_postal',
            'credit_card_3_scan_front': 'cc3_scan_front',
            'credit_card_3_scan_back': 'cc3_scan_back',
            'credit_card_3_id': 'cc3_id_scan',
            
            # Corporate Airline Programs
            'air_canada_for_business': 'aircanada_business',
            'air_france_klm_bluebiz': 'airfrance_klm_business',
            'alaska_airlines_easybiz': 'alaska_business',
            'american_airlines_business_extra': 'american_business',
            'ana_biz_all_nippon_airways': 'ana_business',
            'british_airways_on_business': 'british_business',
            'cathay_pacific_business_plus': 'cathay_business',
            'delta_skybonus': 'delta_business',
            'emirates_business_rewards': 'emirates_business',
            'ethiopian_airlines_corporate_bonus_program': 'ethiopian_business',
            'etihad_businessconnect': 'etihad_business',
            'finnair_corporate_program': 'finnair_business',
            'japan_airlines_jal_business_on_web': 'jal_business',
            'korean_air_kalbiz': 'korean_business',
            'lot_polish_airlines_corporate_program': 'lot_business',
            'lufthansa_partnerplusbenefit': 'lufthansa_business',
            'qantas_business_rewards': 'qantas_business',
            'qatar_airways_beyond_business': 'qatar_business',
            'sas_credits_scandinavian_airlines': 'sas_business',
            'singapore_airlines_highflyer': 'singaporean_business',
            'southwest_business_swabiz': 'southwest_business',
            'united_perksplus': 'united_business',
            
            # Car Rental Programs
            'enterprise_national_contract': 'enterprise_contract',
            'enterprise_national_billing_number': 'enterprise_billing',
            'hertz_dollar_thrifty_contract': 'hertz_contract',
            'hertz_dollar_thrifty_contract_billing_number': 'hertz_billing',
            'avis_budget_awd': 'avis_awd',
            'avis_budget_billing_number': 'avis_billing',
            'sixt_contract': 'sixt_contract',
            'sixt_billing_number': 'sixt_billing',
            
            # Ground Transportation
            'preferred_ground_vendor_us': 'ground_us',
            'preferred_ground_vendor_eu': 'ground_eu',
            'preferred_ground_asia': 'ground_asia',
            'preferred_ground_australia': 'ground_oz',
            'alpha_priority_account': 'alphapriority_account',
            'beat_the_street_account': 'beatthestreet_account',
            'empire_cls_account': 'empirecls_account',
            
            # Team assignments (these are in CSV)
            'lead_agent_1': 'lead_agent1',
            'lead_agent_2': 'lead_agent2',
            'assigned_agent_1': 'assigned_agent1',
            'assigned_agent_2': 'assigned_agent2',
            'coordinator_1': 'coordinator1',
            'coordinator_2': 'coordinator2',
            'coordinator_3': 'coordinator3',
            'finance_1': 'finance1',
            'finance_2': 'finance2',
            
            # Rates and fees
            'rates_as_of_date': 'rates_as_of',
            'rates_expiration_date': 'rates_expiration',
            'air_domestic_tf': 'air_domestic_ticketfee',
            'air_international_tf': 'air_international_ticketfee',
            'air_domestic_change_tf': 'air_domestic_changefee',
            'air_international_change_tf': 'air_international_changefee',
            'air_domestic_refund': 'air_domestic_refundfee',
            'air_international_refund': 'air_international_refundfee',
            'air_charters': 'air_charters_fee',
            'air_miles_award_bookings': 'air_milesaward_ticketfee',
            'hotel_bookings': 'hotel_bookings',  # Already correct
            'cca_charge': 'cca_fee',
            'car_rental_booking': 'car_rental_booking_fee',
            'chauffer_booking': 'chauffer_booking_fee',
            'rail_ticket': 'rail_booking_ticketfee',
            'after_hours_emergency_line': 'afterhours_fee',
            'net_terms': 'net_terms',  # Already correct
            'cc_payment_fee': 'cc_payment_fee',  # Already correct
            
            # System fields (not in CSV, keep as is)
            'created_at': 'created_at',
            'updated_at': 'updated_at'
        }
    
    def get_column_info(self, column_name):
        """Get full column information from database"""
        self.cursor.execute(f"""
            SELECT COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA, COLUMN_KEY
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'clients' AND COLUMN_NAME = %s
        """, (os.getenv('DB_NAME'), column_name))
        
        result = self.cursor.fetchone()
        if result:
            return {
                'type': result[0],
                'nullable': result[1] == 'YES',
                'default': result[2],
                'extra': result[3],
                'key': result[4]
            }
        return None
    
    def generate_alter_statements(self):
        """Generate all ALTER statements needed"""
        mapping = self.get_complete_mapping()
        statements = []
        
        # Get current columns
        self.cursor.execute("SHOW COLUMNS FROM clients")
        current_columns = [col[0] for col in self.cursor.fetchall()]
        
        logging.info("\n🔧 Generating ALTER statements...")
        
        for old_name, new_name in mapping.items():
            if old_name != new_name and old_name in current_columns:
                col_info = self.get_column_info(old_name)
                if col_info:
                    # Build ALTER statement
                    stmt = f"ALTER TABLE clients CHANGE COLUMN `{old_name}` `{new_name}` {col_info['type']}"
                    
                    if not col_info['nullable']:
                        stmt += " NOT NULL"
                    
                    if col_info['default'] is not None:
                        if col_info['default'] in ['CURRENT_TIMESTAMP', 'current_timestamp()']:
                            stmt += f" DEFAULT {col_info['default']}"
                        else:
                            stmt += f" DEFAULT '{col_info['default']}'"
                    
                    if col_info['extra']:
                        stmt += f" {col_info['extra']}"
                    
                    statements.append((old_name, new_name, stmt))
                    logging.info(f"  {old_name} → {new_name}")
        
        return statements
    
    def check_missing_columns(self):
        """Check which CSV columns are completely missing from database"""
        # Get CSV columns
        df = pd.read_csv("Client-Clients.csv", nrows=1)
        csv_columns = set(df.columns)
        
        # Get DB columns (with new names)
        mapping = self.get_complete_mapping()
        db_columns = set(mapping.values())
        
        # Get current DB columns too
        self.cursor.execute("SHOW COLUMNS FROM clients")
        current_db_columns = set([col[0] for col in self.cursor.fetchall()])
        
        # Find missing columns
        missing = csv_columns - db_columns - current_db_columns
        
        if missing:
            logging.info(f"\n⚠️  CSV columns not in database: {len(missing)}")
            
            # These are likely the relationship columns
            relationship_cols = [col for col in missing if any(x in col for x in ['PAX', 'Hotels', 'Air', 'Rental', 'Chauffer', 'Portal', 'Credits'])]
            other_missing = [col for col in missing if col not in relationship_cols]
            
            if relationship_cols:
                logging.info(f"\n  Relationship columns (will be handled by foreign keys): {len(relationship_cols)}")
                for col in sorted(relationship_cols)[:10]:
                    logging.info(f"    - {col}")
            
            if other_missing:
                logging.info(f"\n  Other missing columns: {len(other_missing)}")
                for col in sorted(other_missing):
                    logging.info(f"    - {col}")
        
        return missing
    
    def apply_changes(self, statements):
        """Apply all the ALTER statements"""
        if not statements:
            logging.info("No column renames needed!")
            return
        
        print(f"\n⚠️  This will rename {len(statements)} columns")
        print("\nFirst 10 changes:")
        for old, new, stmt in statements[:10]:
            print(f"  {old} → {new}")
        
        if len(statements) > 10:
            print(f"  ... and {len(statements) - 10} more")
        
        confirm = input("\nProceed with column renames? (yes/no): ")
        
        if confirm.lower() != 'yes':
            logging.info("Cancelled")
            return
        
        success = 0
        failed = 0
        
        for old_name, new_name, stmt in statements:
            try:
                self.cursor.execute(stmt)
                success += 1
                if success % 10 == 0:
                    logging.info(f"  Progress: {success}/{len(statements)}")
            except Error as e:
                failed += 1
                logging.error(f"  ❌ Failed to rename {old_name}: {e}")
        
        if success > 0:
            self.connection.commit()
            logging.info(f"\n✅ Successfully renamed {success} columns")
        
        if failed > 0:
            logging.error(f"❌ Failed to rename {failed} columns")
    
    def verify_final_state(self):
        """Verify the final state matches CSV"""
        logging.info("\n📊 FINAL VERIFICATION")
        
        # Get CSV columns
        df = pd.read_csv("Client-Clients.csv", nrows=1)
        csv_columns = set(df.columns)
        
        # Get DB columns
        self.cursor.execute("SHOW COLUMNS FROM clients")
        db_columns = set([col[0] for col in self.cursor.fetchall()])
        
        # Check matches
        exact_matches = csv_columns.intersection(db_columns)
        logging.info(f"\n✅ Columns matching CSV exactly: {len(exact_matches)}")
        
        # Show sample
        if exact_matches:
            sample = sorted(exact_matches)[:10]
            for col in sample:
                logging.info(f"  - {col}")
            if len(exact_matches) > 10:
                logging.info(f"  ... and {len(exact_matches) - 10} more")
        
        # Check what's still different
        csv_only = csv_columns - db_columns
        db_only = db_columns - csv_columns
        
        if csv_only:
            logging.info(f"\n⚠️  In CSV but not in DB: {len(csv_only)}")
            # These are likely relationship columns
            for col in sorted(csv_only)[:5]:
                logging.info(f"  - {col}")
        
        if db_only:
            logging.info(f"\n⚠️  In DB but not in CSV: {len(db_only)}")
            for col in sorted(db_only)[:5]:
                logging.info(f"  - {col}")

def main():
    mapper = CompleteSchemaMapper()
    
    try:
        if not mapper.connect():
            return
        
        # Check what's missing first
        mapper.check_missing_columns()
        
        # Generate ALTER statements
        statements = mapper.generate_alter_statements()
        
        # Apply changes
        mapper.apply_changes(statements)
        
        # Verify final state
        mapper.verify_final_state()
        
    except Exception as e:
        logging.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if mapper.connection:
            mapper.connection.close()
            logging.info("\n✅ Done")

if __name__ == "__main__":
    main()