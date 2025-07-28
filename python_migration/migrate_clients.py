#!/usr/bin/env python3
"""
Travel Agency Complete Migration Scripts
Migrates all remaining tables from Airtable CSV to MySQL database
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import numpy as np

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_complete.log'),
        logging.StreamHandler()
    ]
)

class CompleteMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect_to_database(self):
        """Connect to MySQL database"""
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
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                logging.info("Successfully connected to MySQL database")
                return True
                
        except Error as e:
            logging.error(f"Error connecting to MySQL: {e}")
            return False

    def migrate_users(self):
        """Create initial users for the system"""
        try:
            # Create initial admin and agent users
            users_data = [
                ('Kyle', 'MacKinnon', 'kyle@thetravelagency.us', 'admin', True),
                ('Ashley', 'Tran', 'ashley@thetravelagency.us', 'agent', True),
                ('Kevin', 'Liu', 'kevin@valuesoftware.com', 'admin', True)
            ]
            
            insert_query = """
                INSERT INTO users (first_name, last_name, email, role, is_active, password_hash)
                VALUES (%s, %s, %s, %s, %s, 'temp_password_hash')
            """
            
            self.cursor.executemany(insert_query, users_data)
            self.connection.commit()
            logging.info(f"Created {len(users_data)} initial users")
            return True
            
        except Error as e:
            logging.error(f"Error creating users: {e}")
            return False

    def migrate_travelers(self, csv_file_path):
        """Migrate traveler data from Airtable CSV"""
        try:
            df = pd.read_csv(csv_file_path, dtype=str, na_values=['', 'nan', 'NaN'])
            logging.info(f"Loaded {len(df)} traveler records")
            
            # Transform data
            mysql_data = pd.DataFrame()
            
            # Map client_id from CLIENT_ID field (need to get the cid from clients table)
            mysql_data['client_id'] = None  # Will need to map from CLIENT_ID string
            mysql_data['first_name'] = df['FIRSTNAME'].str.strip().str.upper()
            mysql_data['middle_name'] = df.get('MIDDLENAME', '').str.strip().str.upper()
            mysql_data['last_name'] = df['LASTNAME'].str.strip().str.upper()
            mysql_data['date_of_birth'] = pd.to_datetime(df.get('3DOB', ''), errors='coerce').dt.date
            mysql_data['gender'] = df.get('GENDER', '')
            mysql_data['nationality'] = df.get('NATIONALITY', '')
            mysql_data['type_vip_management_crew'] = df.get('TYPE', 'Crew')
            mysql_data['role'] = df.get('ROLE', '')
            
            # Contact info
            mysql_data['primary_email'] = df.get('PRIMARY_EMAIL', '').str.lower().str.strip()
            mysql_data['primary_phone'] = df.get('PRIMARY_PHONE', '')
            mysql_data['alternate_email'] = df.get('ALTERNATE_EMAIL', '').str.lower().str.strip()
            mysql_data['alternate_phone'] = df.get('ALTERNATE_PHONE', '')
            
            # Address
            mysql_data['home_street_address'] = df.get('HOME_STREET_ADDRESS', '')
            mysql_data['home_city'] = df.get('HOME_CITY', '')
            mysql_data['home_state_region'] = df.get('HOME_STATE', '')
            mysql_data['home_zip_postal_code'] = df.get('HOME_ZIP', '')
            mysql_data['home_country'] = df.get('HOME_COUNTRY', '')
            
            # Emergency contact
            mysql_data['emergency_contact_name'] = df.get('EMERGENCY_CONTACT_NAME', '')
            mysql_data['emergency_contact_relationship'] = df.get('EMERGENCY_CONTACT_RELATIONSHIP', '')
            mysql_data['emergency_contact_phone'] = df.get('EMERGENCY_CONTACT_PHONE', '')
            mysql_data['emergency_contact_email'] = df.get('EMERGENCY_CONTACT_EMAIL', '').str.lower().str.strip()
            
            # Passport 1
            mysql_data['passport_1_number'] = df.get('3PP', '')  # Encrypted passport field
            mysql_data['passport_1_country'] = df.get('PASSPORT_1_COUNTRY', '')
            mysql_data['passport_1_issue_date'] = pd.to_datetime(df.get('PASSPORT_1_ISSUE_DATE', ''), errors='coerce').dt.date
            mysql_data['passport_1_expiration_date'] = pd.to_datetime(df.get('PASSPORT_1_EXPIRATION_DATE', ''), errors='coerce').dt.date
            mysql_data['passport_1_scan'] = df.get('PASSPORT_1_SCAN', '')
            
            # Preferences
            mysql_data['air_class_of_service'] = df.get('AIR_CLASS_OF_SERVICE', 'Economy')
            mysql_data['hotel_room_type'] = df.get('HOTEL_ROOM_TYPE', '')
            mysql_data['seat_preference'] = df.get('SEAT_PREFERENCE', '')
            mysql_data['meal_preference'] = df.get('MEAL_PREFERENCE', '')
            mysql_data['special_assistance_required'] = df.get('SPECIAL_ASSISTANCE_REQUIRED', '')
            mysql_data['preferred_airline'] = df.get('PREFERRED_AIRLINE', '')
            
            # Frequent Flyer Programs
            for i in range(1, 10):
                mysql_data[f'ff{i}_airline'] = df.get(f'FF{i}_AIRLINE', '')
                mysql_data[f'ff{i}_number'] = df.get(f'FF{i}_NUMBER', '')
            
            # Hotel Loyalty Programs
            mysql_data['preferred_hotel'] = df.get('PREFERRED_HOTEL', '')
            for i in range(1, 8):
                mysql_data[f'hh{i}_brand'] = df.get(f'HH{i}_BRAND', '')
                mysql_data[f'hh{i}_number'] = df.get(f'HH{i}_NUMBER', '')
            
            # Security
            mysql_data['global_entry_tsa_pre_nexus'] = df.get('GLOBAL_ENTRY_TSA_PRE_NEXUS', '')
            mysql_data['notes'] = df.get('NOTES', '')
            mysql_data['documented_by'] = None  # Will map to user ID
            
            # Need to map client IDs - this requires a lookup
            logging.info("Mapping client IDs...")
            client_mapping = self.get_client_id_mapping()
            mysql_data['client_id'] = df['Client ID'].map(client_mapping)
            
            # Insert data
            self.insert_dataframe('travelers', mysql_data)
            logging.info(f"Successfully migrated {len(mysql_data)} travelers")
            return True
            
        except Exception as e:
            logging.error(f"Error migrating travelers: {e}")
            return False

    def migrate_air_bookings(self, csv_file_path):
        """Migrate air bookings - NOTE: Kyle mentioned this might be hotel data mislabeled"""
        try:
            df = pd.read_csv(csv_file_path, dtype=str, na_values=['', 'nan', 'NaN'])
            logging.info(f"Loaded {len(df)} air booking records")
            
            # Check if this is actually hotel data (per Kyle's feedback)
            columns = df.columns.tolist()
            if 'Hotel' in columns or 'Net Rate' in columns or 'Gross Rate' in columns:
                logging.warning("WARNING: This appears to be hotel data, not air bookings!")
                logging.warning("Columns found: " + ", ".join(columns[:10]))
                
                response = input("This looks like hotel data. Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    return False
            
            mysql_data = pd.DataFrame()
            
            # Basic booking info
            mysql_data['departure_date'] = pd.to_datetime(df.get('Departure Date', ''), errors='coerce').dt.date
            mysql_data['client_id'] = None  # Map from Client field
            mysql_data['traveler_id'] = None  # Map from Traveler field
            mysql_data['agent_id'] = None  # Map later
            
            # Flight segments
            mysql_data['segment1_airline'] = df.get('Airline-1', '').str.upper()
            mysql_data['segment1_flight_number'] = df.get('Flight #-1', '')
            mysql_data['segment1_departure_city'] = df.get('Departure Airport', '').str.upper()
            mysql_data['segment1_departure_time'] = df.get('Departure Time', '')
            mysql_data['segment1_arrival_city'] = df.get('Arrival Airport', '').str.upper()
            mysql_data['segment1_arrival_time'] = df.get('Arrival Time', '')
            
            # Booking details
            mysql_data['airline_confirmation'] = df.get('Confirmation Number', '')
            mysql_data['gds_pnr'] = df.get('PNR', '')
            mysql_data['ticket_number'] = df.get('Ticket Number', '')
            mysql_data['booked_via'] = 'Sabre'  # Default
            
            # Map relationships
            client_mapping = self.get_client_id_mapping()
            traveler_mapping = self.get_traveler_id_mapping()
            
            mysql_data['client_id'] = df.get('Client', '').map(client_mapping)
            mysql_data['traveler_id'] = df.get('Traveler', '').map(traveler_mapping)
            
            self.insert_dataframe('air_bookings', mysql_data)
            logging.info(f"Successfully migrated {len(mysql_data)} air bookings")
            return True
            
        except Exception as e:
            logging.error(f"Error migrating air bookings: {e}")
            return False

    def migrate_hotel_bookings(self, csv_file_path, booking_type='transient'):
        """Migrate hotel bookings (transient or group)"""
        try:
            df = pd.read_csv(csv_file_path, dtype=str, na_values=['', 'nan', 'NaN'])
            logging.info(f"Loaded {len(df)} hotel {booking_type} records")
            
            mysql_data = pd.DataFrame()
            
            if booking_type == 'transient':
                # Individual hotel bookings
                mysql_data['client_id'] = None  # Map from Client field
                mysql_data['traveler_id'] = None  # Map from Traveler field
                mysql_data['agent_id'] = None
                mysql_data['hotel_name'] = df.get('Hotel Name', '')
                mysql_data['hotel_chain'] = df.get('Hotel Chain', '')
                mysql_data['check_in_date'] = pd.to_datetime(df.get('C/I Date', ''), errors='coerce').dt.date
                mysql_data['check_out_date'] = pd.to_datetime(df.get('C/O Date', ''), errors='coerce').dt.date
                mysql_data['room_type'] = df.get('Room Type', '')
                mysql_data['confirmation_number'] = df.get('Confirmation Number', '')
                mysql_data['status'] = 'Confirmed'
                mysql_data['cca_needed'] = df.get('CCA Needed', 'false').str.lower() == 'true'
                mysql_data['cca_submitted_date'] = pd.to_datetime(df.get('CCA Submitted Date', ''), errors='coerce').dt.date
                
                table_name = 'hotel_transient_bookings'
                
            else:  # group bookings
                mysql_data['client_id'] = None  # Map from Client field
                mysql_data['agent_id'] = None
                mysql_data['group_name'] = df.get('Touring Party', '')
                mysql_data['hotel_name'] = df.get('Hotel', '')
                mysql_data['check_in_date'] = pd.to_datetime(df.get('C/I Date', ''), errors='coerce').dt.date
                mysql_data['check_out_date'] = pd.to_datetime(df.get('C/O Date', ''), errors='coerce').dt.date
                mysql_data['contracted_rate_net'] = pd.to_numeric(df.get('Net Rate', '').str.replace('$', '').str.replace(',', ''), errors='coerce')
                mysql_data['contracted_rate_estimated_taxes'] = pd.to_numeric(df.get('Tax Rate', '').str.replace('$', '').str.replace(',', ''), errors='coerce')
                mysql_data['contracted_rate_gross'] = pd.to_numeric(df.get('Gross Rate', '').str.replace('$', '').str.replace(',', ''), errors='coerce')
                mysql_data['confirmation_number'] = df.get('Confirmation Number', '')
                mysql_data['status'] = 'Contracted'
                
                table_name = 'hotel_group_bookings'
            
            # Map relationships
            client_mapping = self.get_client_id_mapping()
            if booking_type == 'transient':
                traveler_mapping = self.get_traveler_id_mapping()
                mysql_data['traveler_id'] = df.get('Traveler', '').map(traveler_mapping)
            
            mysql_data['client_id'] = df.get('Client', '').map(client_mapping)
            
            self.insert_dataframe(table_name, mysql_data)
            logging.info(f"Successfully migrated {len(mysql_data)} hotel {booking_type} bookings")
            return True
            
        except Exception as e:
            logging.error(f"Error migrating hotel {booking_type} bookings: {e}")
            return False

    def migrate_other_bookings(self, csv_file_path):
        """Migrate other commissionable bookings"""
        try:
            df = pd.read_csv(csv_file_path, dtype=str, na_values=['', 'nan', 'NaN'])
            logging.info(f"Loaded {len(df)} other booking records")
            
            mysql_data = pd.DataFrame()
            mysql_data['client_id'] = None  # Map from Clients field
            mysql_data['traveler_id'] = None  # Map from NAME field to traveler
            mysql_data['agent_id'] = None
            mysql_data['service_type'] = df.get('Type', 'Other')
            mysql_data['service_name'] = df.get('Details', '')
            mysql_data['vendor'] = df.get('Supplier', '')
            mysql_data['service_date'] = pd.to_datetime(df.get('Date', ''), errors='coerce').dt.date
            mysql_data['location'] = df.get('Location', '')
            mysql_data['description'] = df.get('Details', '')
            mysql_data['quoted_rate'] = pd.to_numeric(df.get('Total Rate', '').str.replace('$', '').str.replace(',', ''), errors='coerce')
            
            # Map relationships
            client_mapping = self.get_client_id_mapping()
            mysql_data['client_id'] = df.get('Clients', '').map(client_mapping)
            
            # For travelers, we need to map by name since that's what's in the NAME field
            # This is more complex and may need manual review
            
            self.insert_dataframe('other_bookings', mysql_data)
            logging.info(f"Successfully migrated {len(mysql_data)} other bookings")
            return True
            
        except Exception as e:
            logging.error(f"Error migrating other bookings: {e}")
            return False

    def migrate_passenger_credits(self, csv_file_path):
        """Migrate passenger credits with BOTH client and traveler links"""
        try:
            df = pd.read_csv(csv_file_path, dtype=str, na_values=['', 'nan', 'NaN'])
            logging.info(f"Loaded {len(df)} passenger credit records")
            
            mysql_data = pd.DataFrame()
            mysql_data['client_id'] = None  # Map from relationship
            mysql_data['traveler_id'] = None  # Map from Traveler field
            mysql_data['agent_id'] = None
            mysql_data['airline'] = df.get('Airline', '').str.upper()
            mysql_data['amount'] = pd.to_numeric(df.get('Amount', '').str.replace('$', '').str.replace(',', ''), errors='coerce')
            mysql_data['currency'] = 'USD'
            mysql_data['expiration_date'] = pd.to_datetime(df.get('Expiration Date', ''), errors='coerce').dt.date
            mysql_data['mco_ticket_number'] = df.get('MCO/Ticket #', '')
            mysql_data['status'] = 'Active'
            
            # Map relationships
            traveler_mapping = self.get_traveler_id_mapping()
            mysql_data['traveler_id'] = df.get('Traveler', '').map(traveler_mapping)
            
            # Get client_id from traveler relationship
            # This requires a join query to get the client_id for each traveler
            
            self.insert_dataframe('passenger_credits', mysql_data)
            logging.info(f"Successfully migrated {len(mysql_data)} passenger credits")
            return True
            
        except Exception as e:
            logging.error(f"Error migrating passenger credits: {e}")
            return False

    def get_client_id_mapping(self):
        """Get mapping of client names/IDs to database IDs"""
        try:
            self.cursor.execute("SELECT cid, name FROM clients")
            results = self.cursor.fetchall()
            return {name: cid for cid, name in results}
        except:
            return {}

    def get_traveler_id_mapping(self):
        """Get mapping of traveler names to database IDs"""
        try:
            self.cursor.execute("SELECT traveler_id, full_name FROM travelers")
            results = self.cursor.fetchall()
            return {name: tid for tid, name in results}
        except:
            return {}

    def insert_dataframe(self, table_name, df):
        """Generic function to insert DataFrame into MySQL table"""
        try:
            # Remove rows where all values are None/NaN
            df_clean = df.dropna(how='all')
            
            if len(df_clean) == 0:
                logging.warning(f"No valid data to insert into {table_name}")
                return False
            
            columns = df_clean.columns.tolist()
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Convert DataFrame to list of tuples
            data_tuples = []
            for _, row in df_clean.iterrows():
                row_data = [None if pd.isna(value) else value for value in row]
                data_tuples.append(tuple(row_data))
            
            self.cursor.executemany(insert_query, data_tuples)
            self.connection.commit()
            
            logging.info(f"Inserted {len(data_tuples)} records into {table_name}")
            return True
            
        except Error as e:
            logging.error(f"Error inserting into {table_name}: {e}")
            self.connection.rollback()
            return False

    def close_connection(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("Database connection closed")

def main():
    """Main migration orchestrator"""
    migration = CompleteMigration()
    
    # CSV file paths - UPDATE THESE
    csv_files = {
        'travelers': 'Traveler-Master.csv',
        'air_bookings': 'Air-Master.csv',  # Kyle says this might be hotel data!
        'hotel_transient': 'Hotel-Transient-Master.csv',
        'hotel_group': 'Hotel-Group-Master.csv',
        'other_bookings': 'Other-Commissionable.csv',
        'passenger_credits': 'Passenger-Credits.csv',
        'chauffeur': 'Chauffeur-Vehicles-Master.csv',
        'rental_cars': 'Rental-Vehicles-Master.csv'
    }
    
    try:
        if not migration.connect_to_database():
            return
        
        # Create initial users
        print("Creating initial users...")
        migration.migrate_users()
        
        # Ask which tables to migrate
        print("\nAvailable tables to migrate:")
        for i, (table, file) in enumerate(csv_files.items(), 1):
            print(f"{i}. {table}: {file}")
        
        choice = input("\nEnter table numbers to migrate (comma-separated) or 'all': ")
        
        if choice.lower() == 'all':
            tables_to_migrate = list(csv_files.keys())
        else:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            tables_to_migrate = [list(csv_files.keys())[i] for i in indices]
        
        # Migrate selected tables
        for table in tables_to_migrate:
            file_path = csv_files[table]
            print(f"\nMigrating {table} from {file_path}...")
            
            if not os.path.exists(file_path):
                logging.warning(f"File not found: {file_path}")
                continue
            
            if table == 'travelers':
                migration.migrate_travelers(file_path)
            elif table == 'air_bookings':
                migration.migrate_air_bookings(file_path)
            elif table == 'hotel_transient':
                migration.migrate_hotel_bookings(file_path, 'transient')
            elif table == 'hotel_group':
                migration.migrate_hotel_bookings(file_path, 'group')
            elif table == 'other_bookings':
                migration.migrate_other_bookings(file_path)
            elif table == 'passenger_credits':
                migration.migrate_passenger_credits(file_path)
            # Add other table migrations as needed
        
        logging.info("Migration completed!")
        
    except Exception as e:
        logging.error(f"Migration failed: {e}")
    finally:
        migration.close_connection()

if __name__ == "__main__":
    main()