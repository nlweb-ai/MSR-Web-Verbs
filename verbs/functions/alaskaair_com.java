
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Locator;

//Functions of Alaska Airlines
public class alaskaair_com extends com_base{
    //write a constructor that takes BrowserContext context as an argument
    public alaskaair_com(BrowserContext _context) {
        super(_context);
    }
    /**
     * Extracts flight information from the current page.
     * @return FlightInfoResult containing a list of flights and the price.
     */
    FlightInfoResult getFlightInfo() {
        List<String> flights = new ArrayList<>();
        Locator flightCards = page.locator(".flight-card-extended");
        int flightCardCount = flightCards.count();
        for (int i = 0; i < flightCardCount; i++) {
            String flightCardText = flightCards.nth(i).innerText();
            flights.add(flightCardText);
        }
        Locator priceLocator = page.locator(".svelte-2v9ttl");
        CurrencyAmount price = null;
        if (priceLocator.count() > 0) {
            String priceText = priceLocator.first().innerText();
            String numericPrice = priceText.replaceAll("[^0-9.]", "");
            try {
                double priceValue = Double.parseDouble(numericPrice);
                price = new CurrencyAmount(priceValue);
            } catch (Exception e) {
                price = null;
            }
        }
        return new FlightInfoResult(flights, price);
    }
    /**
     * Searches for flights between the given origin and destination on specified dates.
     * @param origin Origin AIRPORT CODE
     * @param destination Destination AIRPORT CODE
     * @param outboundDate Outbound flight date
     * @param returnDate Return flight date
     * @return SearchFlightsResult containing flight info or a message if no flights found
     */
    public SearchFlightsResult searchFlights(String origin, String destination, LocalDate outboundDate, LocalDate returnDate) {
        String baseUrl = "https://www.alaskaair.com/search/results";
        String queryParams = "?A=1&C=0&L=0&O=%s&D=%s&OD=%s&DD=%s&RT=true";
        String searchUrl = String.format(baseUrl + queryParams, origin, destination, outboundDate.toString(), returnDate.toString());
        page.navigate(searchUrl);
        page.waitForLoadState();
        page.waitForTimeout(1000);
        Locator noFlights = page.locator(".no-flights");
        if (noFlights.count() > 0) {
            return new SearchFlightsResult("No flights found for the given criteria.", null);
        }
        page.waitForURL("https://www.alaskaair.com/search/cart?*");
        FlightInfoResult info = getFlightInfo();
        return new SearchFlightsResult(null, info);
    }
    /**
     * Result class for flight information extraction.
     */
    public static class FlightInfoResult {
        /** List of flight card texts. */
        public final List<String> flights;
        /** Price as a CurrencyAmount, or null if not found. */
        public final CurrencyAmount price;
        public FlightInfoResult(List<String> flights, CurrencyAmount price) {
            this.flights = flights;
            this.price = price;
        }
    }

    /**
     * Result class for searching flights.
     */
    public static class SearchFlightsResult {
        /** Message if no flights found, otherwise null. */
        public final String message;
        /** Flight info if flights found, otherwise null. */
        public final FlightInfoResult flightInfo;
        public SearchFlightsResult(String message, FlightInfoResult flightInfo) {
            this.message = message;
            this.flightInfo = flightInfo;
        }
    }
}