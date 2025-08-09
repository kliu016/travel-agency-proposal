#!/usr/bin/env python3
"""
Compare MySQL schema with CSV structure to identify mismatches
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

class SchemaComparison:
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
            print("✅ Connected to database")
            return True
        except Error as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_mysql_schema(self):
        """Get complete MySQL schema for clients table"""
        self.cursor.execute("DESCRIBE clients")
        mysql_columns = {}
        for row in self.cursor.fetchall():
            col_name = row[0]
            col_type = row[1]
            mysql_columns[col_name] = {
                'type': col_type,
                'null': row[2],
                'key': row[3],
                'default': row[4],
                'extra': row[5]
            }
        return mysql_columns
    
    def get_csv_structure(self):
        """Get CSV column names and sample data"""
        df = pd.read_csv("Client-Clients.csv", nrows=5)
        csv_columns = {}
        
        for col in df.columns:
            # Get sample values to understand data type
            sample_values = df[col].dropna().unique()[:3]
            csv_columns[col] = {
                'samples': list(sample_values),
                'has_data': df[col].notna().any()
            }
        
        return csv_columns, df
    
    def create_mapping(self):
        """Create mapping between CSV columns and MySQL columns"""
        # This is the expected mapping based on the migration script
        mapping = {
            # Primary key
            'CLIENT_ID': 'cid or client_code',  # Should be PRIMARY KEY
            
            # Basic info
            'client_name': 'name',
            'client_type': 'type',  # Should have correct ENUM values
            'client_enroll_date': 'client_enroll_date',
            'client_enroll_by': 'client_enrolled_by',
            
            # Company info
            'client_country': 'company_country',
            'client_street_address': 'company_street_address',
            'client_city': 'company_city',
            'client_state': 'company_state',
            'client_zip_postal': 'company_zip_postal',
            'client_taxid_ein': 'tax_id_ein',
            'W9': 'w9',
            'client_remarks-internal': 'internal_notes',
            
            # Contacts
            'client_primary_contact': 'primary_contact',
            'client_primary_email': 'primary_email',
            'client_primary_phone': 'primary_phone',
            'business_manager_contact': 'business_manager_contact',
            'business_manager_email': 'business_manager_email',
            'business_manager_phone': 'business_manager_phone',
            'additional_email1': 'additional_email_1',
            'additional_email2': 'additional_email_2',
            'additional_email3': 'additional_email_3',
            
            # Documents
            'service_agreement': 'service_agreement',
            'cca_agreement': 'cca_agreement',
            
            # Credit Card 1
            'cc1_nickname': 'credit_card_1_nickname',
            'cc1_type': 'credit_card_1_type',  # Should be ENUM with VI, AX, CA, DS
            'cc1_number': 'credit_card_1_number',
            'cc1_expiration': 'credit_card_1_expiration',
            'cc1_security': 'credit_card_1_security_code',
            'cc1_cardholder': 'credit_card_1_name',
            'cc1_country': 'credit_card_1_country',
            'cc1_street': 'credit_card_1_street_address',
            'cc1_city': 'credit_card_1_city',
            'cc1_state': 'credit_card_1_state',
            'cc1_zip_postal': 'credit_card_1_zip_postal',
            'cc1_scan_front': 'credit_card_1_scan_front',
            'cc1_scan_back': 'credit_card_1_scan_back',
            'cc1_id_scan': 'credit_card_1_id',
            
            # Credit Card 2
            'cc2_nickname': 'credit_card_2_nickname',
            'cc2_type': 'credit_card_2_type',
            'cc2_number': 'credit_card_2_number',
            'cc2_expiration': 'credit_card_2_expiration',
            'cc2_security': 'credit_card_2_security_code',
            'cc2_cardholder': 'credit_card_2_name',
            'cc2_country': 'credit_card_2_country',
            'cc2_street': 'credit_card_2_street_address',
            'cc2_city': 'credit_card_2_city',
            'cc2_state': 'credit_card_2_state',
            'cc2_zip_postal': 'credit_card_2_zip_postal',
            'cc2_scan_front': 'credit_card_2_scan_front',
            'cc2_scan_back': 'credit_card_2_scan_back',
            'cc2_id_scan': 'credit_card_2_id',
            
            # Credit Card 3
            'cc3_nickname': 'credit_card_3_nickname',
            'cc3_type': 'credit_card_3_type',
            'cc3_number': 'credit_card_3_number',
            'cc3_expiration': 'credit_card_3_expiration',
            'cc3_security': 'credit_card_3_security_code',
            'cc3_cardholder': 'credit_card_3_name',
            'cc3_country': 'credit_card_3_country',
            'cc3_street': 'credit_card_3_street_address',
            'cc3_city': 'credit_card_3_city',
            'cc3_state': 'credit_card_3_state',
            'cc3_zip_postal': 'credit_card_3_zip_postal',
            'cc3_scan_front': 'credit_card_3_scan_front',
            'cc3_scan_back': 'credit_card_3_scan_back',
            'cc3_id_scan': 'credit_card_3_id',
            
            # Corporate programs
            'aircanada_business': 'air_canada_for_business',
            'airfrance_klm_business': 'air_france_klm_bluebiz',
            'alaska_business': 'alaska_airlines_easybiz',
            'american_business': 'american_airlines_business_extra',
            'ana_business': 'ana_biz_all_nippon_airways',
            'british_business': 'british_airways_on_business',
            'cathay_business': 'cathay_pacific_business_plus',
            'delta_business': 'delta_skybonus',
            'emirates_business': 'emirates_business_rewards',
            'ethiopian_business': 'ethiopian_airlines_corporate_bonus_program',
            'etihad_business': 'etihad_businessconnect',
            'finnair_business': 'finnair_corporate_program',
            'jal_business': 'japan_airlines_jal_business_on_web',
            'korean_business': 'korean_air_kalbiz',
            'lot_business': 'lot_polish_airlines_corporate_program',
            'lufthansa_business': 'lufthansa_partnerplusbenefit',
            'qantas_business': 'qantas_business_rewards',
            'qatar_business': 'qatar_airways_beyond_business',
            'sas_business': 'sas_credits_scandinavian_airlines',
            'singaporean_business': 'singapore_airlines_highflyer',
            'southwest_business': 'southwest_business_swabiz',
            'united_business': 'united_perksplus',
            
            # Car rental
            'enterprise_contract': 'enterprise_national_contract',
            'enterprise_billing': 'enterprise_national_billing_number',
            'hertz_contract': 'hertz_dollar_thrifty_contract',
            'hertz_billing': 'hertz_dollar_thrifty_contract_billing_number',
            'avis_awd': 'avis_budget_awd',
            'avis_billing': 'avis_budget_billing_number',
            'sixt_contract': 'sixt_contract',
            'sixt_billing': 'sixt_billing_number',
            
            # Ground transportation
            'ground_us': 'preferred_ground_vendor_us',
            'ground_eu': 'preferred_ground_vendor_eu',
            'ground_asia': 'preferred_ground_asia',
            'ground_oz': 'preferred_ground_australia',
            'alphapriority_account': 'alpha_priority_account',
            'beatthestreet_account': 'beat_the_street_account',
            'empirecls_account': 'empire_cls_account',
            
            # Team (these don't have direct mapping in CSV)
            'lead_agent1': 'lead_agent_1',
            'lead_agent2': 'lead_agent_2',
            'assigned_agent1': 'assigned_agent_1',
            'assigned_agent2': 'assigned_agent_2',
            'coordinator1': 'coordinator_1',
            'coordinator2': 'coordinator_2',
            'coordinator3': 'coordinator_3',
            'finance1': 'finance_1',
            'finance2': 'finance_2',
            
            # Rates
            'rates_as_of': 'rates_as_of_date',
            'rates_expiration': 'rates_expiration_date',
            'air_domestic_ticketfee': 'air_domestic_tf',
            'air_international_ticketfee': 'air_international_tf',
            'air_domestic_changefee': 'air_domestic_change_tf',
            'air_international_changefee': 'air_international_change_tf',
            'air_domestic_refundfee': 'air_domestic_refund',
            'air_international_refundfee': 'air_international_refund',
            'air_charters_fee': 'air_charters',
            'air_milesaward_ticketfee': 'air_miles_award_bookings',
            'hotel_bookings': 'hotel_bookings',
            'cca_fee': 'cca_charge',
            'car_rental_booking_fee': 'car_rental_booking',
            'chauffer_booking_fee': 'chauffer_booking',
            'rail_booking_ticketfee': 'rail_ticket',
            'afterhours_fee': 'after_hours_emergency_line',
            'net_terms': 'net_terms',
            'cc_payment_fee': 'cc_payment_fee'
        }
        
        return mapping
    
    def analyze_mismatches(self):
        """Find all mismatches between CSV and MySQL"""
        mysql_schema = self.get_mysql_schema()
        csv_columns, df = self.get_csv_structure()
        mapping = self.create_mapping()
        
        print("\n" + "="*100)
        print("SCHEMA COMPARISON REPORT")
        print("="*100)
        
        # 1. Check PRIMARY KEY situation
        print("\n🔑 PRIMARY KEY Analysis:")
        print("-" * 50)
        
        if 'cid' in mysql_schema and mysql_schema['cid']['extra'] == 'auto_increment':
            print("❌ Current PRIMARY KEY: 'cid' (auto_increment)")
            print("   Should be: 'CLIENT_ID' VARCHAR(20) from CSV")
            print(f"   CSV CLIENT_ID samples: {csv_columns['CLIENT_ID']['samples']}")
        
        if 'client_code' in mysql_schema:
            print("ℹ️  Found 'client_code' column - this might hold CLIENT_ID values")
        
        # 2. Check critical field mismatches
        print("\n⚠️  Critical Field Mismatches:")
        print("-" * 50)
        
        critical_checks = [
            ('client_type', 'type', csv_columns.get('client_type', {}).get('samples', [])),
            ('cc1_type', 'credit_card_1_type', csv_columns.get('cc1_type', {}).get('samples', [])),
            ('cc2_type', 'credit_card_2_type', csv_columns.get('cc2_type', {}).get('samples', [])),
            ('cc3_type', 'credit_card_3_type', csv_columns.get('cc3_type', {}).get('samples', []))
        ]
        
        for csv_col, mysql_col, samples in critical_checks:
            if mysql_col in mysql_schema:
                mysql_info = mysql_schema[mysql_col]
                print(f"\n❌ Mismatch: CSV '{csv_col}' → MySQL '{mysql_col}'")
                print(f"   MySQL type: {mysql_info['type']}")
                print(f"   CSV values: {samples}")
                
                if 'enum' in mysql_info['type'].lower():
                    # Extract ENUM values
                    enum_values = mysql_info['type'][5:-1].replace("'", "").split(',')
                    print(f"   MySQL accepts: {enum_values}")
                    
                    # Check if CSV values are in MySQL enum
                    for val in samples:
                        if val and val not in enum_values:
                            print(f"   ⚠️  '{val}' not in MySQL ENUM!")
        
        # 3. Show all CSV columns not mapped
        print("\n📊 CSV Columns Not in Mapping:")
        print("-" * 50)
        unmapped = []
        for csv_col in csv_columns:
            if csv_col not in mapping:
                unmapped.append(csv_col)
        
        if unmapped:
            for col in unmapped:
                print(f"   ? {col} (samples: {csv_columns[col]['samples'][:2]})")
        
        # 4. Generate UPDATE statements
        print("\n🔧 Required Schema Updates:")
        print("-" * 50)
        
        updates = []
        
        # PRIMARY KEY update
        updates.append("""
-- Step 1: Add CLIENT_ID column and make it PRIMARY KEY
ALTER TABLE clients ADD COLUMN IF NOT EXISTS CLIENT_ID VARCHAR(20) FIRST;
UPDATE clients SET CLIENT_ID = client_code WHERE client_code IS NOT NULL;
ALTER TABLE clients DROP PRIMARY KEY;
ALTER TABLE clients MODIFY COLUMN CLIENT_ID VARCHAR(20) NOT NULL PRIMARY KEY;
ALTER TABLE clients DROP COLUMN IF EXISTS cid;
ALTER TABLE clients DROP COLUMN IF EXISTS client_code;
        """)
        
        # Type column updates
        updates.append("""
-- Step 2: Update type columns to match CSV
ALTER TABLE clients CHANGE COLUMN type client_type ENUM('Entertainment', 'Luxury & Leisure') DEFAULT NULL;
ALTER TABLE clients CHANGE COLUMN credit_card_1_type cc1_type ENUM('VI', 'AX', 'CA', 'DS') DEFAULT NULL;
ALTER TABLE clients CHANGE COLUMN credit_card_2_type cc2_type ENUM('VI', 'AX', 'CA', 'DS') DEFAULT NULL;
ALTER TABLE clients CHANGE COLUMN credit_card_3_type cc3_type ENUM('VI', 'AX', 'CA', 'DS') DEFAULT NULL;
        """)
        
        for update in updates:
            print(update)
        
        # 5. Summary
        print("\n📈 Summary:")
        print("-" * 50)
        print(f"Total CSV columns: {len(csv_columns)}")
        print(f"Total MySQL columns: {len(mysql_schema)}")
        print(f"Mapped columns: {len(mapping)}")
        print(f"Unmapped CSV columns: {len(unmapped)}")
        
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

def main():
    comparison = SchemaComparison()
    
    try:
        if comparison.connect():
            comparison.analyze_mismatches()
    finally:
        comparison.close()

if __name__ == "__main__":
    main()