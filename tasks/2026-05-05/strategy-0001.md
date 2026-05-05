## Summary
- Simple, jargon-free explanation of what the function does.
## Overall goal / task
- Find a nearby event in Seattle, get basic details, suggest a nearby hotel, and save findings to the repo.
## Main steps (in order)
- Search Ticketmaster for Seattle events; open the first event page if found and extract title, date, venue, price, and URL.
- If Ticketmaster fails, try Songkick the same way.
- If an event and venue are found, search Booking.com for a nearby hotel and capture name, price, distance, and link.
- Append the gathered summary (with timestamps) to tasks/2026-05-05/known_facts.md.
## Data collected or processed
- Event info: source, title, date text, venue, ticket price text, URL.
- Hotel recommendation: source, name, price estimate text, distance, search URL, hotel URL.
- Metadata: generation timestamps and any notes about failures.
## Web verbs used
- None (no functions from a `verbs/` folder are called).