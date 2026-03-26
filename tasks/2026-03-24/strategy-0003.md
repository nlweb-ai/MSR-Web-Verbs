## Function Summary: CVS Store Finder for Bellevue, WA
### Overall Goal
Find all CVS pharmacy locations in Bellevue, Washington and collect their information like addresses, phone numbers, and services available.
### Main Steps (In Order)
1. **Set the search location** — Uses ZIP code 98004, which is the central downtown area of Bellevue, WA
2. **Search for CVS stores** — Uses the `cvs_retailer/cvs_search` web verb to look up CVS locations, requesting up to 10 results
3. **Organize the store information** — Takes each store found and collects key details (address, phone number, hours, pharmacy availability, MinuteClinic availability)
4. **Save the results** — Writes all the collected store information to a file called `known_facts.md` for future reference, including:
   - The search date (March 26, 2026)
   - The ZIP code used
   - Formatted store details with addresses and phone numbers
   - A complete JSON record of all data collected
### Data Being Collected
For each CVS store found, the function gathers:
- **Address** — Store location
- **Phone number** — Contact information
- **Hours** — When the store is open
- **Pharmacy availability** — Whether it has a pharmacy
- **MinuteClinic availability** — Whether it has an urgent care clinic