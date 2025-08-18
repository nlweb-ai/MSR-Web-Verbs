import java.time.LocalDate;

import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;

//Functions of Booking.com
public class booking_com extends com_base {
    //write a constructor that takes BrowserContext context as an argument
    public booking_com(BrowserContext _context) {
        super(_context);
    }

    
    /**
     * Searches for hotels in a destination for given dates.
     * @param destination The destination city/location
     * @param checkinDate Check-in date (LocalDate)
     * @param checkoutDate Check-out date (LocalDate)
     * @return HotelSearchResult containing a list of hotels and the search parameters
     */
    public HotelSearchResult search_hotel(String destination, LocalDate checkinDate, LocalDate checkoutDate) {
        page.navigate("https://www.booking.com/");
        //System.out.print("press any key:"); scanner.nextLine();
        
        Locator b=page.locator("input[id=':rh:']");
        b.fill(destination);
        //b.focus();
        // Press Enter to submit the input
        //page.keyboard().press("Enter");
        
        b=page.locator("button[data-testid=\"searchbox-dates-container\"]");
        b.click();

        b=page.locator(String.format("span[data-date=\"%s\"]", checkinDate.toString()));
        b.click();
        b=page.locator(String.format("span[data-date=\"%s\"]", checkoutDate.toString()));
        b.click();
        page.waitForTimeout(1500);
        //System.out.print("press any key:"); scanner.nextLine();

        // Click the 'Search' button
        for (int i=0;i<2;i++)
        {
            try {
                b = page.locator("button[type='submit']").nth(0);
                //b = page.locator("span[class=\"ca2ca5203b\"]");
                b.click();
                page.waitForURL("https://www.booking.com/searchresults.html?*", new Page.WaitForURLOptions().setTimeout(2000));  
            } catch (Exception e) {
            }
            if (page.url().contains("searchresults")) {
                break; // Exit the loop if the URL indicates a successful search
            }
        }

        // Use try-with-resources to ensure the Scanner is properly closed
        /*System.out.println("Press any key to continue...");
        try (java.util.Scanner scanner = new java.util.Scanner(System.in)) {
            scanner.nextLine();
        }*/
         page.waitForTimeout(1500);
        b=page.locator(".f6e3a11b0d.ae5dbab14d.e95943ce9b.d32e843a31");
        //loop through all hotels in b
        int hotelCount = Math.min(b.count(), 5);
        java.util.List<HotelInfo> hotels = new java.util.ArrayList<>();
        for (int i = 0; i < hotelCount; i++) {
            Locator titleLocator = b.nth(i).locator("div[data-testid='title']");
            String hotelName = titleLocator.innerText();
            Locator priceLocator = b.nth(i).locator(".b87c397a13.ab607752a2");
            CurrencyAmount price = null;
            if (priceLocator.count() > 0) {
                String priceText = priceLocator.innerText();
                String numericPrice = priceText.replaceAll("[^0-9.]", "");
                try {
                    double priceValue = Double.parseDouble(numericPrice);
                    price = new CurrencyAmount(priceValue);
                } catch (Exception e) {
                    price = null;
                }
            }
            hotels.add(new HotelInfo(hotelName, price));
        }
        HotelSearchResult result = new HotelSearchResult(destination, checkinDate, checkoutDate, hotels);
        System.out.println("Destination: " + result.destination);
        System.out.println("Check-in: " + result.checkinDate);
        System.out.println("Check-out: " + result.checkoutDate);
        System.out.println("Hotels found: " + result.hotels.size());
        for (int i = 0; i < result.hotels.size(); i++) {
            booking_com.HotelInfo hotel = result.hotels.get(i);
            System.out.print("Hotel " + (i + 1) + ": " + hotel.hotelName);
            if (hotel.price != null) {
                System.out.println(" | Price: " + hotel.price.amount + " " + hotel.price.currency);
            } else {
                System.out.println(" | Price: N/A");
            }
        }
        return result;
    }

    /**
     * Represents a hotel search result, including search parameters and a list of hotels.
     */
    public static class HotelSearchResult {
        /** Destination city/location. */
        public final String destination;
        /** Check-in date. */
        public final LocalDate checkinDate;
        /** Check-out date. */
        public final LocalDate checkoutDate;
        /** List of hotels found. */
        public final java.util.List<HotelInfo> hotels;
        public HotelSearchResult(String destination, LocalDate checkinDate, LocalDate checkoutDate, java.util.List<HotelInfo> hotels) {
            this.destination = destination;
            this.checkinDate = checkinDate;
            this.checkoutDate = checkoutDate;
            this.hotels = hotels;
        }
    }

    /**
     * Represents information about a single hotel, including name and price.
     */
    public static class HotelInfo {
        /** Hotel name. */
        public final String hotelName;
        /** Price as CurrencyAmount, or null if not found. */
        public final CurrencyAmount price;
        public HotelInfo(String hotelName, CurrencyAmount price) {
            this.hotelName = hotelName;
            this.price = price;
        }
    }
}