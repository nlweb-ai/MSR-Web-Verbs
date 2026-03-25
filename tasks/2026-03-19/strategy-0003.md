## What This Does
This is a little helper that figures out which car dealerships are closest to a hotel, so someone can plan their visit efficiently.
## Overall Goal
Find the **3 nearest car dealerships** (by driving distance) from the Red Roof Inn in Champaign, IL, and save that information for later use.
## Main Steps (in order)
1. **Looks up driving directions** from the hotel to each dealership on the list, one by one, using Google Maps.
2. **Records the details** for each dealership — its name, address, how long the drive takes, and how far away it is.
3. **Sorts all dealerships** from closest to farthest.
4. **Picks the top 3 closest** and sets aside the rest.
5. **Saves everything** to a notes file (`known_facts.md`), including which dealerships were picked and which were skipped (and why).
## Data Collected
- **For each dealership:** name, address, estimated drive time, and distance in miles
- **Final output:** the 3 closest dealerships (kept for a Sunday–Tuesday visit) and the rest (marked as "farther than top 3")