import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0071 {
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
        
        // Step 1: Check current weather in Austin, TX for August 10, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get Austin, TX location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Austin, TX");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData austinLocation = locations.get(0);
                double lat = austinLocation.getLatitude();
                double lon = austinLocation.getLongitude();
                
                // Get current weather for Austin, TX
                OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(lat, lon);
                
                weatherInfo.addProperty("city", currentWeather.getCityName());
                weatherInfo.addProperty("country", currentWeather.getCountry());
                weatherInfo.addProperty("date", currentWeather.getDate().toString());
                weatherInfo.addProperty("condition", currentWeather.getCondition());
                weatherInfo.addProperty("description", currentWeather.getDescription());
                weatherInfo.addProperty("temperature", currentWeather.getTemperature());
                weatherInfo.addProperty("feels_like", currentWeather.getFeelsLike());
                weatherInfo.addProperty("humidity", currentWeather.getHumidity());
                weatherInfo.addProperty("wind_speed", currentWeather.getWindSpeed());
                weatherInfo.addProperty("cloudiness", currentWeather.getCloudiness());
                weatherInfo.addProperty("target_date", "August 10, 2025");
                
                // Check if weather is sunny (using condition and cloudiness)
                String condition = currentWeather.getCondition().toLowerCase();
                int cloudiness = currentWeather.getCloudiness();
                boolean isSunny = (condition.contains("clear") || condition.contains("sun")) && cloudiness < 30;
                weatherInfo.addProperty("is_sunny", isSunny);
                
                // Step 2: If sunny, search for outdoor grills at Costco
                JsonObject costcoInfo = new JsonObject();
                if (isSunny) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult grillResults = costco.searchProducts("outdoor grill");
                    
                    if (grillResults.products != null && !grillResults.products.isEmpty()) {
                        // Find the cheapest grill
                        costco_com.ProductInfo cheapestGrill = null;
                        double cheapestPrice = Double.MAX_VALUE;
                        
                        JsonArray grillsArray = new JsonArray();
                        for (costco_com.ProductInfo product : grillResults.products) {
                            JsonObject grillObj = new JsonObject();
                            grillObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                grillObj.addProperty("price", product.productPrice.amount);
                                grillObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount < cheapestPrice) {
                                    cheapestPrice = product.productPrice.amount;
                                    cheapestGrill = product;
                                }
                            }
                            grillsArray.add(grillObj);
                        }
                        
                        costcoInfo.add("available_grills", grillsArray);
                        costcoInfo.addProperty("grills_found", grillResults.products.size());
                        
                        if (cheapestGrill != null) {
                            JsonObject selectedGrill = new JsonObject();
                            selectedGrill.addProperty("product_name", cheapestGrill.productName);
                            selectedGrill.addProperty("price", cheapestGrill.productPrice.amount);
                            selectedGrill.addProperty("currency", cheapestGrill.productPrice.currency);
                            selectedGrill.addProperty("selection_reason", "Cheapest outdoor grill found");
                            costcoInfo.add("selected_grill", selectedGrill);
                        }
                    } else {
                        costcoInfo.addProperty("grills_found", 0);
                        costcoInfo.addProperty("message", "No outdoor grills found at Costco");
                        if (grillResults.error != null) {
                            costcoInfo.addProperty("error", grillResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "Weather is not sunny, skipping grill search");
                }
                
                result.add("costco_search", costcoInfo);
                
                // Step 3: Find books about barbecue in OpenLibrary and select the one with shortest title
                OpenLibrary openLibrary = new OpenLibrary();
                JsonObject booksInfo = new JsonObject();
                
                try {
                    List<OpenLibrary.BookInfo> barbecueBooks = openLibrary.search("barbecue", "title,author_name,first_publish_year", "new", "en", 20, 1);
                    
                    if (barbecueBooks != null && !barbecueBooks.isEmpty()) {
                        JsonArray booksArray = new JsonArray();
                        OpenLibrary.BookInfo shortestTitleBook = null;
                        int shortestLength = Integer.MAX_VALUE;
                        
                        for (OpenLibrary.BookInfo book : barbecueBooks) {
                            JsonObject bookObj = new JsonObject();
                            bookObj.addProperty("title", book.title);
                            bookObj.addProperty("title_length", book.title.length());
                            booksArray.add(bookObj);
                            
                            if (book.title.length() < shortestLength) {
                                shortestLength = book.title.length();
                                shortestTitleBook = book;
                            }
                        }
                        
                        booksInfo.add("available_books", booksArray);
                        booksInfo.addProperty("books_found", barbecueBooks.size());
                        
                        if (shortestTitleBook != null) {
                            JsonObject selectedBook = new JsonObject();
                            selectedBook.addProperty("title", shortestTitleBook.title);
                            selectedBook.addProperty("title_length", shortestTitleBook.title.length());
                            selectedBook.addProperty("selection_reason", "Book with shortest title about barbecue");
                            booksInfo.add("selected_book", selectedBook);
                        }
                    } else {
                        booksInfo.addProperty("books_found", 0);
                        booksInfo.addProperty("message", "No books about barbecue found in OpenLibrary");
                    }
                } catch (java.io.IOException | InterruptedException e) {
                    booksInfo.addProperty("error", "Failed to search books: " + e.getMessage());
                }
                
                result.add("openlibrary_search", booksInfo);
                
                // Step 4: Search for apartments in Austin, TX under $1800 within 3 miles of Costco
                redfin_com redfin = new redfin_com(context);
                JsonObject apartmentInfo = new JsonObject();
                
                try {
                    redfin_com.ApartmentSearchResult apartmentResults = redfin.searchApartments("Austin, TX", 0, 1800);
                    
                    if (apartmentResults.apartments != null && !apartmentResults.apartments.isEmpty()) {
                        // Find Costco locations in Austin using Google Maps
                        maps_google_com maps = new maps_google_com(context);
                        maps_google_com.NearestBusinessesResult costcoLocations = maps.get_nearestBusinesses("Austin, TX", "Costco", 10);
                        
                        JsonArray apartmentsArray = new JsonArray();
                        JsonArray costcoLocationsArray = new JsonArray();
                        
                        // Document Costco locations found
                        if (costcoLocations.businesses != null) {
                            for (maps_google_com.BusinessInfo costco : costcoLocations.businesses) {
                                JsonObject costcoObj = new JsonObject();
                                costcoObj.addProperty("name", costco.name);
                                costcoObj.addProperty("address", costco.address);
                                costcoLocationsArray.add(costcoObj);
                            }
                        }
                        
                        // Process apartments and calculate distances to Costco locations
                        for (redfin_com.ApartmentInfo apartment : apartmentResults.apartments) {
                            JsonObject aptObj = new JsonObject();
                            aptObj.addProperty("address", apartment.address);
                            if (apartment.price != null) {
                                aptObj.addProperty("rent", apartment.price.amount);
                                aptObj.addProperty("currency", apartment.price.currency);
                            }
                            aptObj.addProperty("url", apartment.url);
                            
                            // Calculate distance to each Costco location
                            JsonArray distancesToCostco = new JsonArray();
                            double shortestDistanceMiles = Double.MAX_VALUE;
                            String closestCostcoName = "";
                            boolean withinThreeMiles = false;
                            
                            if (costcoLocations.businesses != null && !costcoLocations.businesses.isEmpty()) {
                                for (maps_google_com.BusinessInfo costco : costcoLocations.businesses) {
                                    try {
                                        maps_google_com.DirectionResult direction = maps.get_direction(apartment.address, costco.address);
                                        
                                        JsonObject distanceObj = new JsonObject();
                                        distanceObj.addProperty("costco_name", costco.name);
                                        distanceObj.addProperty("costco_address", costco.address);
                                        distanceObj.addProperty("distance", direction.distance);
                                        distanceObj.addProperty("travel_time", direction.travelTime);
                                        
                                        // Parse distance to extract miles (assuming format like "2.5 mi" or "2.5 miles")
                                        double distanceInMiles = parseDistanceToMiles(direction.distance);
                                        distanceObj.addProperty("distance_miles", distanceInMiles);
                                        
                                        if (distanceInMiles < shortestDistanceMiles) {
                                            shortestDistanceMiles = distanceInMiles;
                                            closestCostcoName = costco.name;
                                        }
                                        
                                        if (distanceInMiles <= 3.0) {
                                            withinThreeMiles = true;
                                        }
                                        
                                        distancesToCostco.add(distanceObj);
                                        
                                    } catch (Exception e) {
                                        JsonObject errorObj = new JsonObject();
                                        errorObj.addProperty("costco_name", costco.name);
                                        errorObj.addProperty("error", "Failed to calculate distance: " + e.getMessage());
                                        distancesToCostco.add(errorObj);
                                    }
                                }
                            }
                            
                            aptObj.add("distances_to_costco", distancesToCostco);
                            aptObj.addProperty("closest_costco_distance_miles", shortestDistanceMiles != Double.MAX_VALUE ? shortestDistanceMiles : -1);
                            aptObj.addProperty("closest_costco_name", closestCostcoName);
                            aptObj.addProperty("within_3_miles_of_costco", withinThreeMiles);
                            
                            apartmentsArray.add(aptObj);
                        }
                        
                        apartmentInfo.add("apartments_under_1800", apartmentsArray);
                        apartmentInfo.add("costco_locations", costcoLocationsArray);
                        apartmentInfo.addProperty("apartments_found", apartmentResults.apartments.size());
                        apartmentInfo.addProperty("costco_locations_found", costcoLocations.businesses != null ? costcoLocations.businesses.size() : 0);
                        
                        // Count apartments within 3 miles of Costco
                        int apartmentsNearCostco = 0;
                        for (int i = 0; i < apartmentsArray.size(); i++) {
                            JsonObject apt = apartmentsArray.get(i).getAsJsonObject();
                            if (apt.has("within_3_miles_of_costco") && apt.get("within_3_miles_of_costco").getAsBoolean()) {
                                apartmentsNearCostco++;
                            }
                        }
                        
                        apartmentInfo.addProperty("apartments_within_3_miles_of_costco", apartmentsNearCostco);
                        apartmentInfo.addProperty("note", "Distances calculated using Google Maps directions API between apartment addresses and Costco locations");
                    } else {
                        apartmentInfo.addProperty("apartments_found", 0);
                        apartmentInfo.addProperty("message", "No apartments found under $1800 in Austin, TX");
                        if (apartmentResults.error != null) {
                            apartmentInfo.addProperty("error", apartmentResults.error);
                        }
                    }
                } catch (RuntimeException e) {
                    apartmentInfo.addProperty("error", "Failed to search apartments: " + e.getMessage());
                }
                
                result.add("apartment_search", apartmentInfo);
                
            } else {
                weatherInfo.addProperty("error", "Could not find location data for Austin, TX");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
        }
        
        result.add("weather_info", weatherInfo);
        result.addProperty("task_summary", "Check Austin weather for Aug 10, 2025. If sunny, find cheapest Costco outdoor grill and shortest barbecue book title. Search apartments under $1800 near Costco.");
        result.addProperty("target_date", "August 10, 2025");
        result.addProperty("location", "Austin, TX");
        
        return result;
    }
    
    /**
     * Helper method to parse distance string and convert to miles
     * Handles formats like "2.5 mi", "2.5 miles", "3.2 km", etc.
     */
    private static double parseDistanceToMiles(String distanceStr) {
        if (distanceStr == null || distanceStr.trim().isEmpty()) {
            return -1.0;
        }
        
        try {
            // Remove common distance units and extract numeric value
            String cleaned = distanceStr.toLowerCase().trim();
            double value = 0.0;
            
            // Extract the numeric part
            String numericPart = cleaned.replaceAll("[^0-9.]", "");
            if (!numericPart.isEmpty()) {
                value = Double.parseDouble(numericPart);
            }
            
            // Convert based on unit
            if (cleaned.contains("km") || cleaned.contains("kilometer")) {
                // Convert kilometers to miles (1 km = 0.621371 miles)
                return value * 0.621371;
            } else if (cleaned.contains("ft") || cleaned.contains("feet")) {
                // Convert feet to miles (1 mile = 5280 feet)
                return value / 5280.0;
            } else if (cleaned.contains("mi") || cleaned.contains("mile")) {
                // Already in miles
                return value;
            } else {
                // Assume miles if no unit specified
                return value;
            }
        } catch (NumberFormatException e) {
            // If parsing fails, return -1 to indicate error
            return -1.0;
        }
    }
}
