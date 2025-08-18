import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.Comparator;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class TaskParisTravel {
    static BrowserContext context = null;
    static java.util.Scanner scanner= new java.util.Scanner(System.in);
    public static void main(String[] args) {
        
        try (Playwright playwright = Playwright.create()) {
            String userDataDir = System.getProperty("user.home") +"\\AppData\\Local\\Google\\Chrome\\User Data\\Default";

            BrowserType.LaunchPersistentContextOptions options = new BrowserType.LaunchPersistentContextOptions().setChannel("chrome").setHeadless(false).setArgs(java.util.Arrays.asList("--start-maximized"));

            //please add the following option to the options:
            //new Browser.NewContextOptions().setViewportSize(null)
            options.setViewportSize(null);
            
            context = playwright.chromium().launchPersistentContext(Paths.get(userDataDir), options);


            //browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(false).setArgs(java.util.Arrays.asList("--start-maximized")));
            //Browser browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel("msedge").setHeadless(false).setArgs(java.util.Arrays.asList("--start-maximized")));

            JsonObject result = automate(context);
            Gson gson = new GsonBuilder()
                .disableHtmlEscaping()
                .setPrettyPrinting()
                .create();
            String prettyResult = gson.toJson(result);
            System.out.println("Final output: " + prettyResult);
            System.out.print("Press Enter to exit...");
            scanner.nextLine(); 
            
            context.close();
        }
    }

    /* Do not modify anything above this line. 
       The following "automate(...)" function is the one you should modify. 
       The current function body is just an example specifically about youtube.
    */
    static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        
        try {
            // Step 1: Search for hotels in Paris on booking.com for dates 2025-09-10 to 2025-09-15
            booking_com booking = new booking_com(context);
            LocalDate checkinDate = LocalDate.of(2025, 9, 10);
            LocalDate checkoutDate = LocalDate.of(2025, 9, 15);
            
            booking_com.HotelSearchResult hotelSearchResult = booking.search_hotel("Paris", checkinDate, checkoutDate);
            List<booking_com.HotelInfo> hotels = hotelSearchResult.hotels;
            
            // Step 2: Find the third cheapest hotel from the list
            // Sort hotels by price (ascending) and filter out hotels without prices
            List<booking_com.HotelInfo> hotelsWithPrices = hotels.stream()
                .filter(hotel -> hotel.price != null)
                .sorted(Comparator.comparing(hotel -> hotel.price.amount))
                .toList();
            
            if (hotelsWithPrices.size() < 3) {
                result.addProperty("error", "Not enough hotels with prices found");
                return result;
            }
            
            booking_com.HotelInfo selectedHotel = hotelsWithPrices.get(2); // Third cheapest (0-indexed)
            String hotelName = selectedHotel.hotelName;
            CurrencyAmount hotelPrice = selectedHotel.price;
            
            // Step 3: Find the distance to the Eiffel Tower
            maps_google_com maps = new maps_google_com(context);
            String hotelAddress = hotelName + ", Paris, France"; // Use hotel name as address reference
            String eiffelTowerAddress = "Eiffel Tower, Paris, France";
            
            maps_google_com.DirectionResult direction = maps.get_direction(hotelAddress, eiffelTowerAddress);
            String distanceToEiffelTower = direction.distance;
            
            // Step 4: Go to amazon.com and search for "travel adapter" suitable for the country
            amazon_com amazon = new amazon_com(context);
            amazon.clearCart(); // Clear cart first
            amazon_com.CartResult cartResult = amazon.addItemToCart("travel adapter");
            
            CurrencyAmount adapterPrice = null;
            if (!cartResult.items.isEmpty()) {
                adapterPrice = cartResult.items.get(0).price; // Get the price of the first (top-rated) adapter
            }
            
            // Step 5: Prepare the message content
            String messageContent = String.format(
                "Paris Travel Information:\n" +
                "Hotel: %s\n" +
                "Hotel Price: %s %.2f\n" +
                "Distance to Eiffel Tower: %s\n" +
                "Travel Adapter Price: %s %.2f",
                hotelName,
                hotelPrice.currency, hotelPrice.amount,
                distanceToEiffelTower,
                adapterPrice != null ? adapterPrice.currency : "N/A", 
                adapterPrice != null ? adapterPrice.amount : 0.0
            );
            
            // Step 6: Send Microsoft Teams message to JohnDoe@contoso.com
            teams_microsoft_com teams = new teams_microsoft_com(context);
            teams_microsoft_com.MessageStatus messageStatus = teams.sendMessage("JohnDoe@contoso.com", messageContent);
            
            // Step 7: Print the required information and prepare final output
            System.out.println("Hotel Name: " + hotelName);
            System.out.println("Distance to Eiffel Tower: " + distanceToEiffelTower);
            System.out.println("Travel Adapter Price: " + (adapterPrice != null ? adapterPrice.currency + " " + adapterPrice.amount : "N/A"));
            
            // Prepare JSON result
            result.addProperty("hotelName", hotelName);
            result.addProperty("hotelPriceCurrency", hotelPrice.currency);
            result.addProperty("hotelPriceAmount", hotelPrice.amount);
            result.addProperty("distanceToEiffelTower", distanceToEiffelTower);
            
            if (adapterPrice != null) {
                result.addProperty("adapterPriceCurrency", adapterPrice.currency);
                result.addProperty("adapterPriceAmount", adapterPrice.amount);
            } else {
                result.addProperty("adapterPriceCurrency", "N/A");
                result.addProperty("adapterPriceAmount", 0.0);
            }
            
            result.addProperty("teamsMessageStatus", messageStatus.status);
            result.addProperty("teamsRecipient", messageStatus.recipientEmail);
            result.addProperty("messageContent", messageContent);
            
        } catch (Exception e) {
            result.addProperty("error", "An error occurred: " + e.getMessage());
            e.printStackTrace();
        }
        
        return result;
    }
}
