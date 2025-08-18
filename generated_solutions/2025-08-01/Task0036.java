import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0036 {
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
        JsonObject output = new JsonObject();
        
        try {
            // Step 1: Search for organic produce and healthy snacks at Costco
            costco_com costco = new costco_com(context);
            JsonArray costcoProductsArray = new JsonArray();
            
            try {
                // Search for organic produce
                costco_com.ProductListResult organicProduce = costco.searchProducts("organic vegetables fruits");
                if (organicProduce != null && organicProduce.products != null) {
                    for (costco_com.ProductInfo product : organicProduce.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("name", product.productName);
                        productObj.addProperty("price", product.productPrice != null ? product.productPrice.amount : 0.0);
                        productObj.addProperty("currency", product.productPrice != null ? product.productPrice.currency : "USD");
                        productObj.addProperty("category", "Organic Produce");
                        productObj.addProperty("store", "Costco");
                        if (product.error != null) {
                            productObj.addProperty("error", product.error);
                        }
                        costcoProductsArray.add(productObj);
                    }
                }
                
                // Search for healthy snacks
                costco_com.ProductListResult healthySnacks = costco.searchProducts("healthy snacks nuts organic");
                if (healthySnacks != null && healthySnacks.products != null) {
                    for (costco_com.ProductInfo product : healthySnacks.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("name", product.productName);
                        productObj.addProperty("price", product.productPrice != null ? product.productPrice.amount : 0.0);
                        productObj.addProperty("currency", product.productPrice != null ? product.productPrice.currency : "USD");
                        productObj.addProperty("category", "Healthy Snacks");
                        productObj.addProperty("store", "Costco");
                        if (product.error != null) {
                            productObj.addProperty("error", product.error);
                        }
                        costcoProductsArray.add(productObj);
                    }
                }
                
            } catch (Exception e) {
                JsonObject costcoError = new JsonObject();
                costcoError.addProperty("error", "Failed to search Costco products: " + e.getMessage());
                costcoProductsArray.add(costcoError);
            }
            
            output.add("costco_products", costcoProductsArray);
            
            // Step 2: Add water filter pitcher to Amazon cart
            amazon_com amazon = new amazon_com(context);
            JsonObject amazonResult = new JsonObject();
            
            try {
                // Clear cart first for clean comparison
                amazon.clearCart();
                
                // Add water filter pitcher to cart
                amazon_com.CartResult cartResult = amazon.addItemToCart("water filter pitcher");
                
                if (cartResult != null && cartResult.items != null) {
                    JsonArray cartItems = new JsonArray();
                    double totalCost = 0.0;
                    
                    for (amazon_com.CartItem item : cartResult.items) {
                        JsonObject itemObj = new JsonObject();
                        itemObj.addProperty("name", item.itemName);
                        itemObj.addProperty("price", item.price != null ? item.price.amount : 0.0);
                        itemObj.addProperty("currency", item.price != null ? item.price.currency : "USD");
                        itemObj.addProperty("store", "Amazon");
                        cartItems.add(itemObj);
                        
                        if (item.price != null) {
                            totalCost += item.price.amount;
                        }
                    }
                    
                    amazonResult.add("cart_items", cartItems);
                    amazonResult.addProperty("total_cost", totalCost);
                    amazonResult.addProperty("cart_status", "Items added successfully");
                } else {
                    amazonResult.addProperty("error", "Failed to add water filter pitcher to cart");
                }
                
            } catch (Exception e) {
                amazonResult.addProperty("error", "Failed to add items to Amazon cart: " + e.getMessage());
            }
            
            output.add("amazon_cart", amazonResult);
            
            // Step 3: Check weather forecast for Los Angeles on August 6, 2025
            OpenWeather weather = new OpenWeather();
            JsonObject weatherInfo = new JsonObject();
            
            try {
                List<OpenWeather.LocationData> locations = weather.getLocationsByName("Los Angeles, CA");
                if (!locations.isEmpty()) {
                    OpenWeather.LocationData laLocation = locations.get(0);
                    double lat = laLocation.getLatitude();
                    double lon = laLocation.getLongitude();
                    
                    OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(lat, lon);
                    
                    JsonObject currentWeatherObj = new JsonObject();
                    currentWeatherObj.addProperty("city", currentWeather.getCityName());
                    currentWeatherObj.addProperty("condition", currentWeather.getCondition());
                    currentWeatherObj.addProperty("description", currentWeather.getDescription());
                    currentWeatherObj.addProperty("temperature", currentWeather.getTemperature());
                    currentWeatherObj.addProperty("humidity", currentWeather.getHumidity());
                    currentWeatherObj.addProperty("windSpeed", currentWeather.getWindSpeed());
                    
                    OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                    
                    JsonArray forecastArray = new JsonArray();
                    if (forecast != null && forecast.getForecasts() != null) {
                        for (int i = 0; i < Math.min(8, forecast.getForecasts().size()); i++) {
                            OpenWeather.ForecastEntry entry = forecast.getForecasts().get(i);
                            JsonObject forecastEntry = new JsonObject();
                            forecastEntry.addProperty("dateTime", entry.getDateTime().toString());
                            forecastEntry.addProperty("condition", entry.getCondition());
                            forecastEntry.addProperty("temperature", entry.getTemperature());
                            forecastEntry.addProperty("description", entry.getDescription());
                            forecastArray.add(forecastEntry);
                        }
                    }
                    
                    weatherInfo.add("current_weather", currentWeatherObj);
                    weatherInfo.add("forecast", forecastArray);
                    
                    // Shopping time recommendations based on weather
                    String shoppingRecommendation;
                    double temp = currentWeather.getTemperature();
                    
                    if (temp > 30) {
                        shoppingRecommendation = "Very hot weather - shop early morning (7-9 AM) or late evening (7-9 PM) to avoid peak heat.";
                    } else if (temp > 25) {
                        shoppingRecommendation = "Warm weather - ideal for morning shopping (8-11 AM) or early evening (5-7 PM).";
                    } else if (temp > 20) {
                        shoppingRecommendation = "Pleasant weather - any time is good for shopping, prefer midday for warmth.";
                    } else {
                        shoppingRecommendation = "Cool weather - midday shopping (11 AM - 3 PM) recommended for comfortable temperatures.";
                    }
                    
                    weatherInfo.addProperty("shopping_time_recommendation", shoppingRecommendation);
                    
                } else {
                    weatherInfo.addProperty("error", "Could not find location data for Los Angeles, CA");
                }
            } catch (Exception e) {
                weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
            }
            
            output.add("weather_forecast", weatherInfo);
            
            // Step 4: Find nearest Costco warehouse using Google Maps
            maps_google_com maps = new maps_google_com(context);
            JsonObject storeLocationResult = new JsonObject();
            
            try {
                maps_google_com.NearestBusinessesResult costcoStores = maps.get_nearestBusinesses("Los Angeles, CA", "Costco warehouse", 5);
                
                if (costcoStores != null && costcoStores.businesses != null) {
                    JsonArray storesArray = new JsonArray();
                    
                    for (maps_google_com.BusinessInfo store : costcoStores.businesses) {
                        JsonObject storeObj = new JsonObject();
                        storeObj.addProperty("name", store.name);
                        storeObj.addProperty("address", store.address);
                        storeObj.addProperty("type", "Costco Warehouse");
                        storesArray.add(storeObj);
                    }
                    
                    storeLocationResult.add("nearby_stores", storesArray);
                    storeLocationResult.addProperty("stores_found", costcoStores.businesses.size());
                    
                    // Get directions to the nearest store
                    if (!costcoStores.businesses.isEmpty()) {
                        maps_google_com.BusinessInfo nearestStore = costcoStores.businesses.get(0);
                        maps_google_com.DirectionResult directions = maps.get_direction("Los Angeles, CA", nearestStore.address);
                        
                        if (directions != null) {
                            JsonObject directionsObj = new JsonObject();
                            directionsObj.addProperty("destination", nearestStore.name);
                            directionsObj.addProperty("address", nearestStore.address);
                            directionsObj.addProperty("travel_time", directions.travelTime);
                            directionsObj.addProperty("distance", directions.distance);
                            directionsObj.addProperty("route", directions.route);
                            
                            storeLocationResult.add("directions_to_nearest", directionsObj);
                        }
                    }
                } else {
                    storeLocationResult.addProperty("error", "No Costco warehouses found near Los Angeles, CA");
                }
                
            } catch (Exception e) {
                storeLocationResult.addProperty("error", "Failed to find Costco locations: " + e.getMessage());
            }
            
            output.add("store_locations", storeLocationResult);
            
            // Step 5: Create comprehensive grocery shopping plan
            JsonObject shoppingPlan = new JsonObject();
            shoppingPlan.addProperty("shopping_date", "August 6, 2025");
            shoppingPlan.addProperty("location", "Los Angeles, California");
            shoppingPlan.addProperty("family_focus", "Healthy Grocery Shopping");
            
            // Price comparison and budget analysis
            JsonObject budgetAnalysis = new JsonObject();
            
            double costcoTotal = 0.0;
            int costcoItemCount = 0;
            for (int i = 0; i < costcoProductsArray.size(); i++) {
                JsonObject item = costcoProductsArray.get(i).getAsJsonObject();
                if (item.has("price") && item.has("name")) {
                    costcoTotal += item.get("price").getAsDouble();
                    costcoItemCount++;
                }
            }
            
            double amazonTotal = amazonResult.has("total_cost") ? amazonResult.get("total_cost").getAsDouble() : 0.0;
            
            budgetAnalysis.addProperty("costco_items", costcoItemCount);
            budgetAnalysis.addProperty("costco_estimated_total", costcoTotal);
            budgetAnalysis.addProperty("amazon_total", amazonTotal);
            budgetAnalysis.addProperty("combined_estimated_cost", costcoTotal + amazonTotal);
            budgetAnalysis.addProperty("cost_savings_note", "Bulk buying at Costco provides better unit prices for family groceries");
            
            shoppingPlan.add("budget_analysis", budgetAnalysis);
            
            // Shopping recommendations
            JsonObject recommendations = new JsonObject();
            
            JsonArray shoppingTips = new JsonArray();
            shoppingTips.add("Focus on organic produce for better nutrition");
            shoppingTips.add("Buy healthy snacks in bulk to save money");
            shoppingTips.add("Use water filter to reduce plastic bottle waste");
            shoppingTips.add("Shop during recommended weather-friendly hours");
            shoppingTips.add("Bring reusable bags and cooler for fresh items");
            
            recommendations.add("shopping_tips", shoppingTips);
            
            // Shopping route optimization
            if (storeLocationResult.has("directions_to_nearest")) {
                JsonObject route = new JsonObject();
                JsonObject directions = storeLocationResult.get("directions_to_nearest").getAsJsonObject();
                route.addProperty("primary_destination", directions.get("destination").getAsString());
                route.addProperty("travel_time", directions.get("travel_time").getAsString());
                route.addProperty("distance", directions.get("distance").getAsString());
                route.addProperty("route_plan", "Start at Costco for bulk items, then coordinate Amazon delivery to home");
                
                recommendations.add("optimized_route", route);
            }
            
            // Weather-based timing
            if (weatherInfo.has("shopping_time_recommendation")) {
                recommendations.addProperty("best_shopping_time", weatherInfo.get("shopping_time_recommendation").getAsString());
            }
            
            shoppingPlan.add("recommendations", recommendations);
            
            // Shopping list summary
            JsonObject shoppingList = new JsonObject();
            shoppingList.addProperty("costco_focus", "Organic produce, healthy snacks in bulk");
            shoppingList.addProperty("amazon_focus", "Water filter pitcher for home delivery");
            shoppingList.addProperty("total_categories", "Fresh produce, healthy snacks, water filtration");
            shoppingList.addProperty("family_health_benefits", "Organic nutrition, reduced processed foods, clean drinking water");
            
            shoppingPlan.add("shopping_list_summary", shoppingList);
            
            output.add("shopping_plan", shoppingPlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning the grocery shopping trip: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
