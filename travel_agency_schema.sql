-- ========================================
-- THE TRAVEL AGENCY - COMPLETE DATABASE SCHEMA
-- Generated from Kyle's CSV templates
-- Total: 10 tables, 441 fields optimized for MySQL
-- ========================================

-- Create database
CREATE DATABASE IF NOT EXISTS travel_agency_dev;
USE travel_agency_dev;

-- ========================================
-- CORE BUSINESS TABLES
-- ========================================

-- Users table (17 fields)
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(255) GENERATED ALWAYS AS (CONCAT(first_name, ' ', IFNULL(middle_name, ''), ' ', last_name)) STORED,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    primary_phone VARCHAR(20),
    secondary_phone VARCHAR(20),
    role ENUM('admin', 'agent', 'client', 'traveler') NOT NULL DEFAULT 'agent',
    clients_access_to TEXT, -- JSON array of client IDs
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    reset_token VARCHAR(255),
    
    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_active (is_active)
);

-- Clients table (137 fields) - Kyle's comprehensive client profile
CREATE TABLE clients (
    cid BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type ENUM('Band', 'Artist', 'Company', 'Management', 'Individual') DEFAULT 'Band',
    status ENUM('Active', 'Inactive', 'Prospect', 'Former') DEFAULT 'Active',
    client_enroll_date DATE,
    client_enrolled_by BIGINT,
    
    -- Company Information
    company_country VARCHAR(100),
    company_street_address TEXT,
    company_city VARCHAR(100),
    company_state VARCHAR(100),
    company_zip_postal VARCHAR(20),
    tax_id_ein VARCHAR(50),
    w9 VARCHAR(500), -- File path
    internal_notes TEXT,
    
    -- Primary Contacts
    primary_contact VARCHAR(255),
    primary_email VARCHAR(255),
    primary_phone VARCHAR(20),
    business_manager_contact VARCHAR(255),
    business_manager_email VARCHAR(255),
    business_manager_phone VARCHAR(20),
    additional_email_1 VARCHAR(255),
    additional_email_2 VARCHAR(255),
    additional_email_3 VARCHAR(255),
    
    -- Documents
    service_agreement VARCHAR(500), -- File path
    cca_agreement VARCHAR(500), -- File path
    
    -- Credit Card 1
    credit_card_1_nickname VARCHAR(100),
    credit_card_1_type ENUM('Visa', 'MasterCard', 'Amex', 'Discover'),
    credit_card_1_number VARCHAR(255), -- Encrypted
    credit_card_1_expiration VARCHAR(10),
    credit_card_1_security_code VARCHAR(10), -- Encrypted
    credit_card_1_name VARCHAR(255),
    credit_card_1_country VARCHAR(100),
    credit_card_1_street_address TEXT,
    credit_card_1_city VARCHAR(100),
    credit_card_1_state VARCHAR(100),
    credit_card_1_zip_postal VARCHAR(20),
    credit_card_1_scan_front VARCHAR(500),
    credit_card_1_scan_back VARCHAR(500),
    credit_card_1_id VARCHAR(100),
    
    -- Credit Card 2
    credit_card_2_nickname VARCHAR(100),
    credit_card_2_type ENUM('Visa', 'MasterCard', 'Amex', 'Discover'),
    credit_card_2_number VARCHAR(255), -- Encrypted
    credit_card_2_expiration VARCHAR(10),
    credit_card_2_security_code VARCHAR(10), -- Encrypted
    credit_card_2_name VARCHAR(255),
    credit_card_2_country VARCHAR(100),
    credit_card_2_street_address TEXT,
    credit_card_2_city VARCHAR(100),
    credit_card_2_state VARCHAR(100),
    credit_card_2_zip_postal VARCHAR(20),
    credit_card_2_scan_front VARCHAR(500),
    credit_card_2_scan_back VARCHAR(500),
    credit_card_2_id VARCHAR(100),
    
    -- Credit Card 3
    credit_card_3_nickname VARCHAR(100),
    credit_card_3_type ENUM('Visa', 'MasterCard', 'Amex', 'Discover'),
    credit_card_3_number VARCHAR(255), -- Encrypted
    credit_card_3_expiration VARCHAR(10),
    credit_card_3_security_code VARCHAR(10), -- Encrypted
    credit_card_3_name VARCHAR(255),
    credit_card_3_country VARCHAR(100),
    credit_card_3_street_address TEXT,
    credit_card_3_city VARCHAR(100),
    credit_card_3_state VARCHAR(100),
    credit_card_3_zip_postal VARCHAR(20),
    credit_card_3_scan_front VARCHAR(500),
    credit_card_3_scan_back VARCHAR(500),
    credit_card_3_id VARCHAR(100),
    
    -- Corporate Airline Programs
    air_canada_for_business VARCHAR(100),
    air_france_klm_bluebiz VARCHAR(100),
    alaska_airlines_easybiz VARCHAR(100),
    american_airlines_business_extra VARCHAR(100),
    ana_biz_all_nippon_airways VARCHAR(100),
    asiana_corporate_rewards VARCHAR(100),
    british_airways_on_business VARCHAR(100),
    cathay_pacific_business_plus VARCHAR(100),
    delta_skybonus VARCHAR(100),
    emirates_business_rewards VARCHAR(100),
    ethiopian_airlines_corporate_bonus_program VARCHAR(100),
    etihad_businessconnect VARCHAR(100),
    finnair_corporate_program VARCHAR(100),
    japan_airlines_jal_business_on_web VARCHAR(100),
    jetblue_business_via_bluebiz_air_france_klm VARCHAR(100),
    kenya_airways_corporate_loyalty_program VARCHAR(100),
    korean_air_kalbiz VARCHAR(100),
    lot_polish_airlines_corporate_program VARCHAR(100),
    lufthansa_partnerplusbenefit VARCHAR(100),
    qantas_business_rewards VARCHAR(100),
    qatar_airways_beyond_business VARCHAR(100),
    saudia_alfursan_business VARCHAR(100),
    sas_credits_scandinavian_airlines VARCHAR(100),
    singapore_airlines_highflyer VARCHAR(100),
    south_african_airways_voyager_for_corporates VARCHAR(100),
    southwest_business_swabiz VARCHAR(100),
    united_perksplus VARCHAR(100),
    
    -- Car Rental Programs
    enterprise_national_contract VARCHAR(100),
    enterprise_national_billing_number VARCHAR(100),
    avis_budget_awd VARCHAR(100),
    avis_budget_billing_number VARCHAR(100),
    hertz_dollar_thrifty_contract VARCHAR(100),
    hertz_dollar_thrifty_contract_billing_number VARCHAR(100),
    sixt_contract VARCHAR(100),
    sixt_billing_number VARCHAR(100),
    
    -- Ground Transportation Preferences
    preferred_ground_vendor_us VARCHAR(255),
    preferred_ground_vendor_eu VARCHAR(255),
    preferred_ground_asia VARCHAR(255),
    preferred_ground_australia VARCHAR(255),
    alpha_priority_account VARCHAR(100),
    beat_the_street_account VARCHAR(100),
    empire_cls_account VARCHAR(100),
    star_transportation_account VARCHAR(100),
    
    -- Team Assignments
    lead_agent_1 BIGINT,
    lead_agent_2 BIGINT,
    assigned_agent_1 BIGINT,
    assigned_agent_2 BIGINT,
    coordinator_1 BIGINT,
    coordinator_2 BIGINT,
    coordinator_3 BIGINT,
    finance_1 BIGINT,
    finance_2 BIGINT,
    
    -- Billing & Rates
    rates_as_of_date DATE,
    rates_expiration_date DATE,
    air_domestic_tf DECIMAL(10,2),
    air_international_tf DECIMAL(10,2),
    air_domestic_change_tf DECIMAL(10,2),
    air_international_change_tf DECIMAL(10,2),
    air_domestic_refund DECIMAL(10,2),
    air_international_refund DECIMAL(10,2),
    air_charters DECIMAL(10,2),
    air_miles_award_bookings DECIMAL(10,2),
    hotel_bookings DECIMAL(10,2),
    cca_charge DECIMAL(10,2),
    car_rental_booking DECIMAL(10,2),
    chauffer_booking DECIMAL(10,2),
    rail_ticket DECIMAL(10,2),
    after_hours_emergency_line DECIMAL(10,2),
    net_terms INT DEFAULT 30,
    cc_payment_fee DECIMAL(5,2),
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_clients_name (name),
    INDEX idx_clients_status (status),
    INDEX idx_clients_type (type),
    INDEX idx_clients_primary_email (primary_email),
    INDEX idx_clients_lead_agent_1 (lead_agent_1),
    INDEX idx_clients_assigned_agent_1 (assigned_agent_1),
    
    -- Foreign Keys
    FOREIGN KEY (client_enrolled_by) REFERENCES users(id),
    FOREIGN KEY (lead_agent_1) REFERENCES users(id),
    FOREIGN KEY (lead_agent_2) REFERENCES users(id),
    FOREIGN KEY (assigned_agent_1) REFERENCES users(id),
    FOREIGN KEY (assigned_agent_2) REFERENCES users(id),
    FOREIGN KEY (coordinator_1) REFERENCES users(id),
    FOREIGN KEY (coordinator_2) REFERENCES users(id),
    FOREIGN KEY (coordinator_3) REFERENCES users(id),
    FOREIGN KEY (finance_1) REFERENCES users(id),
    FOREIGN KEY (finance_2) REFERENCES users(id)
);

-- Travelers table (91 fields) - Kyle's comprehensive traveler profile
CREATE TABLE travelers (
    traveler_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id BIGINT NOT NULL,
    
    -- Personal Information
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(255) GENERATED ALWAYS AS (CONCAT(UPPER(last_name), '/', UPPER(first_name), IFNULL(CONCAT(' ', UPPER(middle_name)), ''))) STORED,
    date_of_birth DATE,
    gender ENUM('M', 'F', 'Other'),
    nationality VARCHAR(100),
    type_vip_management_crew ENUM('VIP', 'Management', 'Crew', 'Talent') DEFAULT 'Crew',
    role VARCHAR(100),
    
    -- Contact Information
    primary_email VARCHAR(255),
    primary_phone VARCHAR(20),
    alternate_email VARCHAR(255),
    alternate_phone VARCHAR(20),
    
    -- Home Address
    home_street_address TEXT,
    home_city VARCHAR(100),
    home_state_region VARCHAR(100),
    home_zip_postal_code VARCHAR(20),
    home_country VARCHAR(100),
    
    -- Emergency Contact
    emergency_contact_name VARCHAR(255),
    emergency_contact_relationship VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_email VARCHAR(255),
    
    -- Passport 1
    passport_1_number VARCHAR(50),
    passport_1_country VARCHAR(100),
    passport_1_issue_date DATE,
    passport_1_expiration_date DATE,
    passport_1_scan VARCHAR(500),
    
    -- Passport 2
    passport_2_number VARCHAR(50),
    passport_2_country VARCHAR(100),
    passport_2_issue_date DATE,
    passport_2_expiration_date DATE,
    passport_2_scan VARCHAR(500),
    
    -- Travel Preferences
    air_class_of_service ENUM('Economy', 'Premium Economy', 'Business', 'First') DEFAULT 'Economy',
    hotel_room_type VARCHAR(100),
    seat_preference VARCHAR(100),
    meal_preference VARCHAR(100),
    special_assistance_required TEXT,
    preferred_airline VARCHAR(100),
    
    -- Frequent Flyer Programs (9 airlines)
    ff1_airline VARCHAR(50),
    ff1_number VARCHAR(50),
    ff2_airline VARCHAR(50),
    ff2_number VARCHAR(50),
    ff3_airline VARCHAR(50),
    ff3_number VARCHAR(50),
    ff4_airline VARCHAR(50),
    ff4_number VARCHAR(50),
    ff5_airline VARCHAR(50),
    ff5_number VARCHAR(50),
    ff6_airline VARCHAR(50),
    ff6_number VARCHAR(50),
    ff7_airline VARCHAR(50),
    ff7_number VARCHAR(50),
    ff8_airline VARCHAR(50),
    ff8_number VARCHAR(50),
    ff9_airline VARCHAR(50),
    ff9_number VARCHAR(50),
    
    -- Hotel Loyalty Programs (7 chains)
    preferred_hotel VARCHAR(100),
    hh1_brand VARCHAR(50),
    hh1_number VARCHAR(50),
    hh2_brand VARCHAR(50),
    hh2_number VARCHAR(50),
    hh3_brand VARCHAR(50),
    hh3_number VARCHAR(50),
    hh4_brand VARCHAR(50),
    hh4_number VARCHAR(50),
    hh5_brand VARCHAR(50),
    hh5_number VARCHAR(50),
    hh6_brand VARCHAR(50),
    hh6_number VARCHAR(50),
    hh7_brand VARCHAR(50),
    hh7_number VARCHAR(50),
    
    -- Rail Programs
    preferred_rail VARCHAR(100),
    rail1_brand VARCHAR(50),
    rail1_number VARCHAR(50),
    
    -- Car Rental Programs (5 companies)
    preferred_car VARCHAR(100),
    car1_brand VARCHAR(50),
    car1_number VARCHAR(50),
    car2_brand VARCHAR(50),
    car2_number VARCHAR(50),
    car3_brand VARCHAR(50),
    car3_number VARCHAR(50),
    car4_brand VARCHAR(50),
    car4_number VARCHAR(50),
    car5_brand VARCHAR(50),
    car5_number VARCHAR(50),
    
    -- Security Programs
    global_entry_tsa_pre_nexus VARCHAR(100),
    
    -- Admin
    notes TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    documented_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_travelers_client_id (client_id),
    INDEX idx_travelers_last_name (last_name),
    INDEX idx_travelers_full_name (full_name),
    INDEX idx_travelers_type (type_vip_management_crew),
    INDEX idx_travelers_passport_1_exp (passport_1_expiration_date),
    INDEX idx_travelers_passport_2_exp (passport_2_expiration_date),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid) ON DELETE RESTRICT,
    FOREIGN KEY (documented_by) REFERENCES users(id)
);

-- ========================================
-- BOOKING TABLES - Enhanced with Agent tracking
-- ========================================

-- Air Bookings table (46 fields) - Multi-segment flight support
CREATE TABLE air_bookings (
    air_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    departure_date DATE NOT NULL,
    client_id BIGINT NOT NULL,
    traveler_id BIGINT NOT NULL,
    agent_id BIGINT, -- Who booked this
    
    -- Segment 1 (Required)
    segment1_airline VARCHAR(10),
    segment1_flight_number VARCHAR(10),
    segment1_departure_city VARCHAR(10), -- Airport code (LAX, JFK)
    segment1_departure_time TIME,
    segment1_arrival_city VARCHAR(10),
    segment1_arrival_time TIME,
    
    -- Segment 2 (Optional)
    segment2_airline VARCHAR(10),
    segment2_flight_number VARCHAR(10),
    segment2_departure_city VARCHAR(10),
    segment2_departure_time TIME,
    segment2_arrival_city VARCHAR(10),
    segment2_arrival_time TIME,
    
    -- Segment 3 (Optional)
    segment3_airline VARCHAR(10),
    segment3_flight_number VARCHAR(10),
    segment3_departure_city VARCHAR(10),
    segment3_departure_time TIME,
    segment3_arrival_city VARCHAR(10),
    segment3_arrival_time TIME,
    
    -- Segment 4 (Optional)
    segment4_airline VARCHAR(10),
    segment4_flight_number VARCHAR(10),
    segment4_departure_city VARCHAR(10),
    segment4_departure_time TIME,
    segment4_arrival_city VARCHAR(10),
    segment4_arrival_time TIME,
    
    -- Booking Details
    airline_confirmation VARCHAR(50),
    booked_via ENUM('Sabre', 'Online', 'Phone', 'Other') DEFAULT 'Sabre',
    gds_pnr VARCHAR(20),
    ticket_number VARCHAR(50),
    class_of_service ENUM('Y', 'M', 'B', 'F') DEFAULT 'Y', -- Economy, Premium, Business, First
    baggage_allowance VARCHAR(100),
    ticketing_date DATE,
    ticket_status ENUM('Issued', 'Voided', 'Refunded', 'Exchanged') DEFAULT 'Issued',
    ticket_price DECIMAL(10,2),
    tta_ticket_fee DECIMAL(10,2),
    tta_commission DECIMAL(10,2),
    
    -- Admin
    booked_by BIGINT,
    inputted_by BIGINT,
    invoice_id BIGINT,
    service_order_id BIGINT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for date range queries (KEY REQUIREMENT)
    INDEX idx_air_departure_date (departure_date),
    INDEX idx_air_client_date (client_id, departure_date),
    INDEX idx_air_traveler_date (traveler_id, departure_date),
    INDEX idx_air_agent_date (agent_id, departure_date),
    INDEX idx_air_airline_conf (airline_confirmation),
    INDEX idx_air_ticket_number (ticket_number),
    INDEX idx_air_pnr (gds_pnr),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid),
    FOREIGN KEY (traveler_id) REFERENCES travelers(traveler_id),
    FOREIGN KEY (agent_id) REFERENCES users(id),
    FOREIGN KEY (booked_by) REFERENCES users(id),
    FOREIGN KEY (inputted_by) REFERENCES users(id)
);

-- Hotel Transient Bookings table (29 fields) - Individual reservations
CREATE TABLE hotel_transient_bookings (
    hotel_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id BIGINT NOT NULL,
    traveler_id BIGINT NOT NULL,
    agent_id BIGINT,
    
    -- Hotel Information
    hotel_name VARCHAR(255) NOT NULL,
    hotel_chain VARCHAR(100),
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_nights INT GENERATED ALWAYS AS (DATEDIFF(check_out_date, check_in_date)) STORED,
    room_type VARCHAR(100),
    
    -- Rates
    net_rate_per_night DECIMAL(10,2),
    gross_rate_per_night DECIMAL(10,2),
    gross_total DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'USD',
    
    -- Booking Details
    confirmation_number VARCHAR(50),
    status ENUM('Confirmed', 'Cancelled', 'No-Show', 'Completed') DEFAULT 'Confirmed',
    loyalty_program VARCHAR(100),
    booking_source ENUM('Direct', 'GDS', 'Online', 'Phone') DEFAULT 'Direct',
    gds_pnr VARCHAR(20),
    
    -- CCA (Credit Card Authorization)
    cca_needed BOOLEAN DEFAULT FALSE,
    cca_submitted_date DATE,
    cca_submitted_by BIGINT,
    cca_pdf VARCHAR(500),
    
    -- Admin
    final_invoice VARCHAR(500),
    invoice_id BIGINT,
    booked_by BIGINT,
    inputted_by BIGINT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for date range queries
    INDEX idx_hotel_trans_checkin (check_in_date),
    INDEX idx_hotel_trans_checkout (check_out_date),
    INDEX idx_hotel_trans_client_date (client_id, check_in_date),
    INDEX idx_hotel_trans_traveler_date (traveler_id, check_in_date),
    INDEX idx_hotel_trans_confirmation (confirmation_number),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid),
    FOREIGN KEY (traveler_id) REFERENCES travelers(traveler_id),
    FOREIGN KEY (agent_id) REFERENCES users(id),
    FOREIGN KEY (cca_submitted_by) REFERENCES users(id),
    FOREIGN KEY (booked_by) REFERENCES users(id),
    FOREIGN KEY (inputted_by) REFERENCES users(id)
);

-- Hotel Group Bookings table (36 fields) - Group room blocks
CREATE TABLE hotel_group_bookings (
    group_hotel_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id BIGINT NOT NULL,
    agent_id BIGINT,
    
    -- Group Information
    group_name VARCHAR(255),
    hotel_name VARCHAR(255) NOT NULL,
    hotel_chain VARCHAR(100),
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_nights INT GENERATED ALWAYS AS (DATEDIFF(check_out_date, check_in_date)) STORED,
    room_block_details TEXT,
    rooming_list_link VARCHAR(500),
    
    -- Rates
    contracted_rate_net DECIMAL(10,2),
    contracted_rate_estimated_taxes DECIMAL(10,2),
    contracted_rate_gross DECIMAL(10,2),
    contracted_rate_total DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'USD',
    commissionable_rate DECIMAL(10,2),
    commission_amount DECIMAL(10,2),
    rate_type ENUM('Net', 'Commissionable', 'Contract') DEFAULT 'Net',
    
    -- Booking Details
    confirmation_number VARCHAR(50),
    status ENUM('Contracted', 'Confirmed', 'Cancelled', 'Completed') DEFAULT 'Contracted',
    
    -- Hotel Contacts
    hotel_sales_contact_name VARCHAR(255),
    hotel_sales_contact_email VARCHAR(255),
    hotel_sales_contact_phone VARCHAR(20),
    hotel_coordinator_contact_name VARCHAR(255),
    hotel_coordinator_contact_email VARCHAR(255),
    hotel_coordinator_contact_phone VARCHAR(20),
    
    -- Documents
    cca_pdf VARCHAR(500),
    contract_pdf VARCHAR(500),
    hotel_roominglist_pdf VARCHAR(500),
    final_invoice VARCHAR(500),
    
    -- Admin
    invoice_id BIGINT,
    booked_by BIGINT,
    inputted_by BIGINT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for date range queries
    INDEX idx_hotel_group_checkin (check_in_date),
    INDEX idx_hotel_group_checkout (check_out_date),
    INDEX idx_hotel_group_client_date (client_id, check_in_date),
    INDEX idx_hotel_group_confirmation (confirmation_number),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid),
    FOREIGN KEY (agent_id) REFERENCES users(id),
    FOREIGN KEY (booked_by) REFERENCES users(id),
    FOREIGN KEY (inputted_by) REFERENCES users(id)
);

-- Chauffeur Bookings table (25 fields) - Ground transportation
CREATE TABLE chauffeur_bookings (
    chauffeur_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    client_id BIGINT NOT NULL,
    primary_traveler_id BIGINT NOT NULL,
    agent_id BIGINT,
    
    -- Additional travelers (JSON array of traveler_ids)
    additional_travelers JSON,
    
    -- Service Details
    vendor VARCHAR(255),
    movement_type ENUM('Airport Transfer', 'Rider Directed', 'Point to Point', 'Hourly') DEFAULT 'Airport Transfer',
    vehicle_type ENUM('Sedan', 'SUV', 'Van', 'Sprinter', 'Bus', 'Limo') DEFAULT 'Sedan',
    pickup_time TIME,
    pickup_location TEXT,
    dropoff_location TEXT,
    passenger_count INT DEFAULT 1,
    luggage_count INT DEFAULT 0,
    
    -- Vendor Information
    chauffeur_company VARCHAR(255),
    confirmation_number VARCHAR(50),
    passenger_contact VARCHAR(255),
    passenger_contact_number VARCHAR(20),
    
    -- Booking Details
    status ENUM('Confirmed', 'Cancelled', 'Completed', 'No-Show') DEFAULT 'Confirmed',
    quoted_rate DECIMAL(10,2),
    
    -- Admin
    invoice_id BIGINT,
    booked_by BIGINT,
    inputted_by BIGINT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for date range queries
    INDEX idx_chauffeur_date (date),
    INDEX idx_chauffeur_client_date (client_id, date),
    INDEX idx_chauffeur_traveler_date (primary_traveler_id, date),
    INDEX idx_chauffeur_confirmation (confirmation_number),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid),
    FOREIGN KEY (primary_traveler_id) REFERENCES travelers(traveler_id),
    FOREIGN KEY (agent_id) REFERENCES users(id),
    FOREIGN KEY (booked_by) REFERENCES users(id),
    FOREIGN KEY (inputted_by) REFERENCES users(id)
);

-- Rental Car Bookings table (24 fields)
CREATE TABLE rental_car_bookings (
    rental_car_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id BIGINT NOT NULL,
    traveler_id BIGINT NOT NULL,
    agent_id BIGINT,
    
    -- Rental Details
    rental_company ENUM('Enterprise', 'Hertz', 'Avis', 'Budget', 'National', 'Alamo', 'Thrifty', 'Dollar', 'Sixt') NOT NULL,
    vehicle_type VARCHAR(100),
    pickup_date DATE NOT NULL,
    pickup_time TIME,
    pickup_location VARCHAR(255),
    dropoff_date DATE NOT NULL,
    dropoff_time TIME,
    dropoff_location VARCHAR(255),
    
    -- Booking Information
    confirmation_number VARCHAR(50),
    loyalty_program VARCHAR(100),
    
    -- Rates
    base_rate DECIMAL(10,2),
    gross_rate DECIMAL(10,2),
    quoted_rate DECIMAL(10,2),
    commission DECIMAL(10,2),
    
    -- Admin
    final_invoice VARCHAR(500),
    invoice_id BIGINT,
    booked_by BIGINT,
    inputted_by BIGINT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for date range queries
    INDEX idx_rental_pickup_date (pickup_date),
    INDEX idx_rental_client_date (client_id, pickup_date),
    INDEX idx_rental_traveler_date (traveler_id, pickup_date),
    INDEX idx_rental_confirmation (confirmation_number),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid),
    FOREIGN KEY (traveler_id) REFERENCES travelers(traveler_id),
    FOREIGN KEY (agent_id) REFERENCES users(id),
    FOREIGN KEY (booked_by) REFERENCES users(id),
    FOREIGN KEY (inputted_by) REFERENCES users(id)
);

-- Airport Greeter table (18 fields) - NEW TABLE per Kyle's request
CREATE TABLE airport_greeter_bookings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    client_id BIGINT NOT NULL,
    primary_traveler_id BIGINT NOT NULL,
    agent_id BIGINT,
    
    -- Additional travelers (JSON array)
    additional_travelers JSON,
    
    -- Service Details
    greeter_type ENUM('Meet & Greet', 'Fast Track', 'Lounge Access', 'VIP Service', 'Customs Assistance') DEFAULT 'Meet & Greet',
    airport_code VARCHAR(10) NOT NULL, -- LAX, JFK, etc.
    flight_info VARCHAR(255), -- Flight numbers, arrival times
    greeter_details TEXT,
    
    -- Booking Details
    quoted_rate DECIMAL(10,2),
    invoice_total DECIMAL(10,2),
    invoice_reference VARCHAR(100),
    
    -- Admin
    booked_by VARCHAR(255),
    inputted_by VARCHAR(255),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for date range queries
    INDEX idx_greeter_date (date),
    INDEX idx_greeter_client_date (client_id, date),
    INDEX idx_greeter_airport (airport_code),
    INDEX idx_greeter_traveler_date (primary_traveler_id, date),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid),
    FOREIGN KEY (primary_traveler_id) REFERENCES travelers(traveler_id),
    FOREIGN KEY (agent_id) REFERENCES users(id)
);

-- Other Bookings table (18 fields) - Miscellaneous services
CREATE TABLE other_bookings (
    other_booking_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id BIGINT NOT NULL,
    traveler_id BIGINT,
    agent_id BIGINT,
    
    -- Service Details
    service_type ENUM('Disney', 'Cruise', 'Tours', 'Entertainment', 'Transportation', 'Other') DEFAULT 'Other',
    service_name VARCHAR(255),
    vendor VARCHAR(255),
    service_date DATE,
    end_date DATE,
    location VARCHAR(255),
    description TEXT,
    
    -- Financial
    quoted_rate DECIMAL(10,2),
    final_invoice VARCHAR(500),
    invoice_id BIGINT,
    
    -- Admin
    booked_by BIGINT,
    inputted_by BIGINT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for date range queries
    INDEX idx_other_service_date (service_date),
    INDEX idx_other_client_date (client_id, service_date),
    INDEX idx_other_traveler_date (traveler_id, service_date),
    INDEX idx_other_service_type (service_type),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid),
    FOREIGN KEY (traveler_id) REFERENCES travelers(traveler_id),
    FOREIGN KEY (agent_id) REFERENCES users(id),
    FOREIGN KEY (booked_by) REFERENCES users(id),
    FOREIGN KEY (inputted_by) REFERENCES users(id)
);

-- ========================================
-- SUPPORTING TABLES
-- ========================================

-- Passenger Credits table - Links to BOTH client and traveler
CREATE TABLE passenger_credits (
    credit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id BIGINT NOT NULL,
    traveler_id BIGINT NOT NULL,
    agent_id BIGINT,
    
    -- Credit Details
    airline VARCHAR(50) NOT NULL, -- AA, DL, UA
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    expiration_date DATE,
    mco_ticket_number VARCHAR(50),
    
    -- Status
    status ENUM('Active', 'Used', 'Expired', 'Cancelled') DEFAULT 'Active',
    used_date DATE,
    used_for_booking_id BIGINT, -- Reference to booking where used
    
    -- Admin
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_credits_client (client_id),
    INDEX idx_credits_traveler (traveler_id),
    INDEX idx_credits_expiration (expiration_date),
    INDEX idx_credits_airline (airline),
    INDEX idx_credits_status (status),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid),
    FOREIGN KEY (traveler_id) REFERENCES travelers(traveler_id),
    FOREIGN KEY (agent_id) REFERENCES users(id)
);

-- Vendor Websites table - Secure credential management
CREATE TABLE vendor_websites (
    vendor_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    vendor_type ENUM('Airline', 'Hotel', 'Car Rental', 'Vacation Package', 'Ground Transportation', 'Other') NOT NULL,
    website_url VARCHAR(500),
    login_username VARCHAR(255),
    login_password VARCHAR(255), -- Encrypted
    account_number VARCHAR(100),
    notes TEXT,
    
    -- Security
    is_active BOOLEAN DEFAULT TRUE,
    last_login_attempt TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_vendors_name (name),
    INDEX idx_vendors_type (vendor_type),
    INDEX idx_vendors_active (is_active)
);

-- Email Templates table
CREATE TABLE email_templates (
    template_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    body TEXT,
    template_type ENUM('Commission', 'Rooming List', 'Confirmation', 'Reminder', 'Invoice', 'Other') DEFAULT 'Other',
    cc_recipients TEXT, -- JSON array of email addresses
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Admin
    created_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_templates_name (name),
    INDEX idx_templates_type (template_type),
    INDEX idx_templates_active (is_active),
    
    -- Foreign Keys
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Invoices table - Financial tracking
CREATE TABLE invoices (
    invoice_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id BIGINT NOT NULL,
    agent_id BIGINT,
    
    -- Invoice Details
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    status ENUM('Draft', 'Sent', 'Paid', 'Overdue', 'Cancelled') DEFAULT 'Draft',
    
    -- Amounts
    subtotal DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    balance_due DECIMAL(10,2) GENERATED ALWAYS AS (total_amount - paid_amount) STORED,
    currency VARCHAR(10) DEFAULT 'USD',
    
    -- Payment
    payment_terms INT DEFAULT 30, -- Days
    payment_method ENUM('Credit Card', 'Check', 'Wire Transfer', 'ACH', 'Other'),
    payment_date DATE,
    
    -- Admin
    notes TEXT,
    pdf_file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_invoices_client (client_id),
    INDEX idx_invoices_number (invoice_number),
    INDEX idx_invoices_date (invoice_date),
    INDEX idx_invoices_status (status),
    INDEX idx_invoices_due_date (due_date),
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(cid),
    FOREIGN KEY (agent_id) REFERENCES users(id)
);

-- Audit Log table - Track all changes
CREATE TABLE audit_log (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id BIGINT NOT NULL,
    action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    user_id BIGINT,
    changed_fields JSON, -- What fields were changed
    old_values JSON, -- Previous values
    new_values JSON, -- New values
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_audit_table_record (table_name, record_id),
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_timestamp (timestamp),
    INDEX idx_audit_action (action),
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ========================================
-- CREATE VIEWS FOR COMMON QUERIES
-- ========================================

-- Client summary view
CREATE VIEW client_summary AS
SELECT 
    c.cid,
    c.name,
    c.type,
    c.status,
    c.primary_email,
    CONCAT(u1.first_name, ' ', u1.last_name) AS lead_agent_name,
    CONCAT(u2.first_name, ' ', u2.last_name) AS assigned_agent_name,
    COUNT(DISTINCT t.traveler_id) AS total_travelers,
    COUNT(DISTINCT ab.air_id) AS total_air_bookings,
    COUNT(DISTINCT htb.hotel_id) AS total_hotel_bookings
FROM clients c
LEFT JOIN users u1 ON c.lead_agent_1 = u1.id
LEFT JOIN users u2 ON c.assigned_agent_1 = u2.id
LEFT JOIN travelers t ON c.cid = t.client_id
LEFT JOIN air_bookings ab ON c.cid = ab.client_id
LEFT JOIN hotel_transient_bookings htb ON c.cid = htb.client_id
GROUP BY c.cid;

-- Upcoming bookings view (next 30 days) - Critical for daily operations
CREATE VIEW upcoming_bookings AS
SELECT 
    'Air' AS booking_type,
    ab.air_id AS booking_id,
    ab.departure_date AS service_date,
    c.name AS client_name,
    t.full_name AS traveler_name,
    CONCAT(ab.segment1_departure_city, ' → ', ab.segment1_arrival_city) AS details,
    ab.airline_confirmation AS confirmation
FROM air_bookings ab
JOIN clients c ON ab.client_id = c.cid
JOIN travelers t ON ab.traveler_id = t.traveler_id
WHERE ab.departure_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)

UNION ALL

SELECT 
    'Hotel' AS booking_type,
    htb.hotel_id AS booking_id,
    htb.check_in_date AS service_date,
    c.name AS client_name,
    t.full_name AS traveler_name,
    htb.hotel_name AS details,
    htb.confirmation_number AS confirmation
FROM hotel_transient_bookings htb
JOIN clients c ON htb.client_id = c.cid
JOIN travelers t ON htb.traveler_id = t.traveler_id
WHERE htb.check_in_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)

UNION ALL

SELECT 
    'Chauffeur' AS booking_type,
    cb.chauffeur_id AS booking_id,
    cb.date AS service_date,
    c.name AS client_name,
    t.full_name AS traveler_name,
    CONCAT(cb.movement_type, ' - ', cb.vehicle_type) AS details,
    cb.confirmation_number AS confirmation
FROM chauffeur_bookings cb
JOIN clients c ON cb.client_id = c.cid
JOIN travelers t ON cb.primary_traveler_id = t.traveler_id
WHERE cb.date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)

ORDER BY service_date, client_name;

-- ========================================
-- SAMPLE QUERIES FOR DATE RANGE SEARCHES
-- ========================================

/*
-- Find all bookings for a client within date range
DELIMITER //
CREATE PROCEDURE GetClientBookingsByDateRange(
    IN p_client_id BIGINT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    -- Air bookings
    SELECT 'Air' AS type, air_id AS id, departure_date AS date, 
           CONCAT(segment1_departure_city, ' → ', segment1_arrival_city) AS details
    FROM air_bookings 
    WHERE client_id = p_client_id 
      AND departure_date BETWEEN p_start_date AND p_end_date
    
    UNION ALL
    
    -- Hotel bookings
    SELECT 'Hotel' AS type, hotel_id AS id, check_in_date AS date, hotel_name AS details
    FROM hotel_transient_bookings 
    WHERE client_id = p_client_id 
      AND check_in_date BETWEEN p_start_date AND p_end_date
    
    UNION ALL
    
    -- Chauffeur bookings
    SELECT 'Chauffeur' AS type, chauffeur_id AS id, date, 
           CONCAT(movement_type, ' - ', vehicle_type) AS details
    FROM chauffeur_bookings 
    WHERE client_id = p_client_id 
      AND date BETWEEN p_start_date AND p_end_date
      
    ORDER BY date;
END //
DELIMITER ;
*/