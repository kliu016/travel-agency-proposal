# Travel Agency Database Migration Proposal

This repository contains the proposal documents for The Travel Agency's migration from Airtable to MySQL.

## View Proposal
Visit: https://[your-username].github.io/travel-agency-proposal/

## Documents Included
- Executive Migration Plan
- Database Structure Overview  
- Current Airtable Analysis
- Phase 1 Detailed Plan
- About Value Software Solutions

---
Prepared for: Kyle MacKinnon  
By: Value Software Solutions

## Database Info
| Environment | Database Name          | Hostname                          | Username           | Password
| ----------- | --------------------   | -------------------------------   | --------------     | --------------
| Dev         | `travel_agency_dev`    | `mysql-dev.thetravelagency.us`    | `kylemac_dev`      | `TravelAgencyDev`  
| Staging     | `travel_agency_staging`| `mysql-stage.thetravelagency.us`  | `kylemac_staging`  | `TravelAgencyStage`  
| Prod        | `travel_agency_prod`   | `mysql-prod.thetravelagency.us`   | `kylemac_prod`     | `TravelAgencyProd`  

# Connect to your new database from the command line with:
- mysql -u kylemac_dev -p -h mysql-dev.globe.thetravelagency.us travel_agency_dev
- mysql -u kylemac_staging -p -h mysql-stage.kcment.com travel_agency_staging
- 
