## Summary: Uber Ride Price Lookup
### Overall Goal
This function gets pricing information for Uber rides from a Microsoft office building in Redmond, Washington to the Seattle airport, then saves the results to a file.
### Main Steps (in order)
1. **Set up the search** - The function creates a request to find Uber rides from Microsoft Building 99 (a specific office building in Redmond) to the Seattle-Tacoma International Airport's departures terminal, asking for up to 10 ride options.
2. **Search for rides** - The function uses the `uber_rides/search_uber_rides` verb to find available rides and get their prices.
3. **Organize the prices** - The function takes the ride results (different ride types like UberX or UberXL) and pulls out the key information: the type of ride and the price range.
4. **Save to a file** - The function writes all the results to a file called `known_facts.md`, including:
   - Where the pickup location is (Microsoft Building 99)
   - Where the dropoff is (Seattle airport)
   - A list of each ride type and its price
   - A detailed data summary in structured format
### Data Being Collected
- **Pickup location:** Microsoft Building 99, Redmond, WA
- **Dropoff location:** Seattle-Tacoma International Airport Departures terminal
- **Ride information:** For each available ride option, the system records:
  - The ride type (e.g., basic car, premium, larger vehicle, etc.)
  - The estimated price range (e.g., "$25-35")
### Verbs Used
- `uber_rides/search_uber_rides`