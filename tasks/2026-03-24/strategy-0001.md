## What This Does (In Plain English)
This is a **shopping helper** that automatically looks up a popular heart-health supplement called **CoQ10** (Coenzyme Q10) across five major stores — all at once — so you don't have to visit each site yourself.
---
## Overall Goal
Find and compare CoQ10 products from multiple online stores, then save all the results in one place for easy review.
---
## Steps It Takes (In Order)
1. **Searches Amazon** — looks up up to 5 CoQ10 products, collecting name, price, and customer rating
2. **Searches Walmart** — same thing, good for budget-friendly options
3. **Searches Costco** — looks for bulk/value packs (name and price only, no ratings)
4. **Searches Target** — checks mainstream retail, collecting name, price, and rating
5. **Searches eBay** — checks the resale market, collecting listing title, price, and shipping cost
6. **Saves everything** to a file called `known_facts.md` with today's date, neatly organized by store
7. **Returns all results** in a tidy, organized package
---
## What Information Is Collected
| Store   | Product Name | Price | Star Rating | Shipping Cost |
|---------|-------------|-------|-------------|---------------|
| Amazon  | ✅ | ✅ | ✅ | ❌ |
| Walmart | ✅ | ✅ | ✅ | ❌ |
| Costco  | ✅ | ✅ | ❌ | ❌ |
| Target  | ✅ | ✅ | ✅ | ❌ |
| eBay    | ✅ | ✅ | ❌ | ✅ |