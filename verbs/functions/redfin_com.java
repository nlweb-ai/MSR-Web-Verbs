// import com.google.gson.JsonArray;
// import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Locator;

public class redfin_com extends com_base {
    public redfin_com(BrowserContext _context) {
        super(_context);
    }

    /**
     * Search Redfin for apartments for rent in a location and price range.
     * @param location The city or area to search (e.g., "bellevue, WA").
     * @param minRent The minimum rent (e.g., 2000).
     * @param maxRent The maximum rent (e.g., 3000).
     * @return ApartmentSearchResult containing a list of apartments and any error message.
     */
    public ApartmentSearchResult searchApartments(String location, int minRent, int maxRent) {
        java.util.List<ApartmentInfo> apartments = new java.util.ArrayList<>();
        String error = null;
        try {
            page.navigate("https://www.redfin.com/");
            page.setViewportSize(1759, 1023);
            page.waitForTimeout(3000);

            // Click on <span> "Rent"
            String selector_string = "[data-text=\"Rent\"]|";
            String[] selectors = selector_string.split("\\|");
            for (String selector : selectors) {
                if (!selector.isEmpty() && page.locator(selector).count() > 0) {
                    page.locator(selector).first().click();
                    break;
                }
            }
            page.waitForTimeout(1000);

            // Fill location
            selector_string = "#search-box-input|[name=\"searchInputBox\"]|[title=\"City, Address, School, Building, ZIP\"]|#search-box-input|#search-box-input|";
            selectors = selector_string.split("\\|");
            for (String selector : selectors) {
                if (!selector.isEmpty() && page.locator(selector).count() > 0) {
                    page.locator(selector).first().fill(location);
                    page.locator(selector).first().press("Enter");
                    break;
                }
            }
            page.waitForTimeout(3000);

            // Click on <div> "Price"
            selector_string = ".ExposedPriceFilter .RichSelect__label|[class=\"RichSelect RichSelect__size--compact ExposedSearchFilter ExposedPriceFilter ExposedPriceFilter--desktop ExposedSearchFilter--desktop\"] [class=\"RichSelect__label flex align-center\"]|";
            selectors = selector_string.split("\\|");
            for (String selector : selectors) {
                if (!selector.isEmpty() && page.locator(selector).count() > 0) {
                    page.locator(selector).first().click();
                    break;
                }
            }
            page.waitForTimeout(1000);

            // Fill min price
            selector_string = "[placeholder=\"Enter min\"]|";
            selectors = selector_string.split("\\|");
            for (String selector : selectors) {
                if (!selector.isEmpty() && page.locator(selector).count() > 0) {
                    page.locator(selector).first().fill("$" + minRent);
                    break;
                }
            }
            page.waitForTimeout(2000);

            // Fill max price and press Enter
            selector_string = "[placeholder=\"Enter max\"]|";
            selectors = selector_string.split("\\|");
            for (String selector : selectors) {
                if (!selector.isEmpty() && page.locator(selector).count() > 0) {
                    page.locator(selector).first().fill("$" + maxRent);
                    page.locator(selector).first().press("Enter");
                    break;
                }
            }
            page.waitForTimeout(1000);

            // Click on <div> "Home type"
            selector_string = ".ExposedPropertyTypeFilter .RichSelect__label|[class=\"RichSelect RichSelect__size--compact ExposedSearchFilter ExposedPropertyTypeFilter ExposedSearchFilter--desktop\"] [class=\"RichSelect__label flex align-center\"]|";
            selectors = selector_string.split("\\|");
            for (String selector : selectors) {
                if (!selector.isEmpty() && page.locator(selector).count() > 0) {
                    page.locator(selector).first().click();
                    break;
                }
            }
            page.waitForTimeout(1000);

            // Click on <span> "Apartment"
            selector_string = "[for=\"Apartment\"] > [class=\"Label--text\"]|";
            selectors = selector_string.split("\\|");
            for (String selector : selectors) {
                if (!selector.isEmpty() && page.locator(selector).count() > 0) {
                    page.locator(selector).first().click();
                    break;
                }
            }
            page.waitForTimeout(500);

            // Click on <span> "Done"
            selector_string = "text=Done|.ExposedSearchFilter__doneBtn > .ButtonLabel|[class=\"bp-Button ExposedSearchFilter__doneBtn bp-Button__type--primary\"] > [class=\"ButtonLabel\"]|";
            selectors = selector_string.split("\\|");
            for (String selector : selectors) {
                if (!selector.isEmpty() && page.locator(selector).count() > 0) {
                    page.locator(selector).first().click();
                    break;
                }
            }
            page.waitForTimeout(1000);

            int count=0;
            for (int i = 0; i < 10; i++) {
                String cardSelector = "#MapHomeCard_" + i + " .bp-Homecard__Price--value";
                Locator cardLocator = page.locator(cardSelector);
                if (cardLocator.count() > 0) {
                    String priceInfo = cardLocator.first().innerText();
                    CurrencyAmount price = null;
                    try {
                        String numericPrice = priceInfo.replaceAll("[^0-9.]", "");
                        double priceValue = Double.parseDouble(numericPrice);
                        price = new CurrencyAmount(priceValue);
                    } catch (Exception e) {
                        price = null;
                    }
                    Locator parentLocator = cardLocator.first().locator("..").locator("..").locator("..").locator("..").first();
                    Locator addressLocator = parentLocator.locator(".bp-Homecard__Address--address");
                    if (addressLocator.count() == 0) {
                        continue;
                    }
                    String address = addressLocator.innerText();
                    String url = parentLocator.first().getAttribute("href");
                    if (url != null) {
                        url = "https://redfin.com" + url;
                    }
                    apartments.add(new ApartmentInfo(address, price, url));
                    count++;
                    if (count >= 5) {
                        break;
                    }
                }
            }
        } catch (Exception e) {
            error = e.getMessage();
        }
        ApartmentSearchResult result = new ApartmentSearchResult(apartments, error);
        System.out.println(result);
        return result;
    }

    /**
     * Represents an apartment listing with address, price, and URL.
     */
    public static class ApartmentInfo {
        /** Address of the apartment. */
        public final String address;
        /** Price of the apartment. */
        public final CurrencyAmount price;
        /** URL of the listing. */
        public final String url;
        public ApartmentInfo(String address, CurrencyAmount price, String url) {
            this.address = address;
            this.price = price;
            this.url = url;
        }
        @Override
        public String toString() {
            return String.format("%s | %s | %s", address, price != null ? price : "N/A", url);
        }
    }

    /**
     * Represents the result of an apartment search, including a list of apartments and any error message.
     */
    public static class ApartmentSearchResult {
        /** List of found apartments. */
        public final java.util.List<ApartmentInfo> apartments;
        /** Error message, if any. */
        public final String error;
        public ApartmentSearchResult(java.util.List<ApartmentInfo> apartments, String error) {
            this.apartments = apartments;
            this.error = error;
        }
        @Override
        public String toString() {
            if (error != null) {
                return String.format("Error: %s", error);
            }
            StringBuilder sb = new StringBuilder();
            sb.append(String.format("Found %d apartments:\n", apartments.size()));
            for (int i = 0; i < apartments.size(); i++) {
                sb.append(String.format("  %d. %s\n", i + 1, apartments.get(i)));
            }
            return sb.toString();
        }
    }
}
