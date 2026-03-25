## CoQ10 Product Search Summary
### Overall Goal
The program searches for CoQ10 supplements on Amazon to compare different products, their prices, and customer ratings. This helps gather information to compare shopping options for this health supplement.
### Main Steps (In Order)
1. **Search Amazon** — Uses the `amazon_com__amazon/amazon_search` verb to find 15 CoQ10 products on Amazon using the exact search term the user asked for: "coq10"
2. **Organize the Results** — Takes the product information (name, price, and customer rating) from Amazon and puts it into a neat organized list
3. **Save the Information** — Appends the results to a file called `known_facts.md` so you can refer back to this information later
### Data Being Collected
- **Product Names** — What each product is called
- **Prices** — How much each product costs
- **Customer Ratings** — What rating customers gave each product (on the Amazon platform)
- **Search Date** — When the search was performed (March 25, 2026)
### Web Verb Used
- `amazon_com__amazon/amazon_search` — Searches Amazon for products matching a keyword