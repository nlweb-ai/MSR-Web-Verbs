import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0067 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Search for top 3 most popular kitchen gadgets at Costco
            costco_com costco = new costco_com(context);
            costco_com.ProductListResult gadgets = costco.searchProducts("kitchen gadgets");
            JsonArray gadgetsArr = new JsonArray();
            List<costco_com.ProductInfo> topGadgets = new ArrayList<>();
            
            if (gadgets.products != null && !gadgets.products.isEmpty()) {
                int gadgetCount = Math.min(3, gadgets.products.size());
                for (int i = 0; i < gadgetCount; i++) {
                    costco_com.ProductInfo gadget = gadgets.products.get(i);
                    topGadgets.add(gadget);
                    JsonObject gadgetObj = new JsonObject();
                    gadgetObj.addProperty("name", gadget.productName);
                    gadgetObj.addProperty("price", gadget.productPrice != null ? gadget.productPrice.amount : null);
                    gadgetsArr.add(gadgetObj);
                }
            }
            result.add("top_3_kitchen_gadgets", gadgetsArr);

            // 2. Search for books about kitchen gadgets in OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            List<OpenLibrary.BookInfo> books = openLibrary.search("kitchen gadgets", "title,first_publish_year", "new", "en", 20, 1);
            JsonArray kitchenGadgetBooksArr = new JsonArray();
            
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                kitchenGadgetBooksArr.add(bookObj);
            }
            result.add("kitchen_gadget_books", kitchenGadgetBooksArr);

            // 3. For each book, check for apartments in Chicago, IL under $1800, within 2 miles of Costco warehouses
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentsResult = redfin.searchApartments("Chicago, IL", 0, 1800);
            List<redfin_com.ApartmentInfo> apartments = apartmentsResult.apartments != null ? apartmentsResult.apartments : new ArrayList<>();
            
            // Find nearby Costco warehouses in Chicago
            maps_google_com maps = new maps_google_com(context);
            maps_google_com.NearestBusinessesResult warehousesResult = maps.get_nearestBusinesses("Chicago, IL", "Costco Warehouse", 10);
            List<maps_google_com.BusinessInfo> warehouses = warehousesResult.businesses != null ? warehousesResult.businesses : new ArrayList<>();
            
            JsonArray matchingApartmentsArr = new JsonArray();
            List<redfin_com.ApartmentInfo> closeApartments = new ArrayList<>();
            
            if (!books.isEmpty()) {
                for (redfin_com.ApartmentInfo apt : apartments) {
                    String aptAddr = apt.address;
                    boolean isNearCostco = false;
                    
                    for (maps_google_com.BusinessInfo warehouse : warehouses) {
                        String warehouseAddr = warehouse.address;
                        maps_google_com.DirectionResult dir = maps.get_direction(aptAddr, warehouseAddr);
                        double miles = parseMiles(dir.distance);
                        if (miles > 0 && miles <= 2.0) {
                            isNearCostco = true;
                            break;
                        }
                    }
                    
                    if (isNearCostco) {
                        closeApartments.add(apt);
                        JsonObject aptObj = new JsonObject();
                        aptObj.addProperty("address", apt.address);
                        aptObj.addProperty("price", apt.price != null ? apt.price.amount : null);
                        aptObj.addProperty("url", apt.url);
                        aptObj.addProperty("near_costco_warehouse", true);
                        matchingApartmentsArr.add(aptObj);
                    }
                }
            }
            result.add("apartments_near_costco", matchingApartmentsArr);

            // 4. Get weather forecast for Chicago, IL for August 12, 2025
            LocalDate targetDate = LocalDate.of(2025, 8, 12);
            LocalDate today = LocalDate.now();
            JsonArray weatherForecastsArr = new JsonArray();
            
            if (!closeApartments.isEmpty()) {
                if (!targetDate.isBefore(today) && targetDate.isBefore(today.plusDays(5))) {
                    // Chicago, IL coordinates: 41.8781, -87.6298
                    OpenWeather openWeather = new OpenWeather();
                    OpenWeather.WeatherForecastData forecast = openWeather.getForecast5Day(41.8781, -87.6298);
                    
                    for (redfin_com.ApartmentInfo apt : closeApartments) {
                        JsonObject weatherObj = new JsonObject();
                        weatherObj.addProperty("apartment_address", apt.address);
                        weatherObj.addProperty("target_date", targetDate.toString());
                        weatherObj.addProperty("city", forecast.getCityName());
                        weatherObj.addProperty("country", forecast.getCountry());
                        
                        JsonArray forecastEntriesArr = new JsonArray();
                        for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                            JsonObject entryObj = new JsonObject();
                            entryObj.addProperty("date_time", entry.getDateTime().toString());
                            entryObj.addProperty("condition", entry.getCondition());
                            entryObj.addProperty("description", entry.getDescription());
                            entryObj.addProperty("temperature", entry.getTemperature());
                            entryObj.addProperty("humidity", entry.getHumidity());
                            entryObj.addProperty("wind_speed", entry.getWindSpeed());
                            forecastEntriesArr.add(entryObj);
                        }
                        weatherObj.add("forecast_entries", forecastEntriesArr);
                        weatherForecastsArr.add(weatherObj);
                        break; // Only get forecast for first matching apartment
                    }
                } else {
                    JsonObject weatherObj = new JsonObject();
                    weatherObj.addProperty("target_date", targetDate.toString());
                    weatherObj.addProperty("message", "Target date is outside 5-day forecast range");
                    weatherForecastsArr.add(weatherObj);
                }
            }
            result.add("weather_forecasts_chicago", weatherForecastsArr);

            // Summary information
            JsonObject summaryObj = new JsonObject();
            summaryObj.addProperty("kitchen_gadgets_found", gadgetsArr.size());
            summaryObj.addProperty("kitchen_gadget_books_found", kitchenGadgetBooksArr.size());
            summaryObj.addProperty("matching_apartments_found", matchingApartmentsArr.size());
            summaryObj.addProperty("weather_forecasts_generated", weatherForecastsArr.size());
            result.add("search_summary", summaryObj);
            
        } catch (Exception e) {
            result.addProperty("error", e.toString());
        }
        return result;
    }
    
    // Helper method to parse miles from distance string
    private static double parseMiles(String distanceStr) {
        if (distanceStr == null) return -1;
        distanceStr = distanceStr.toLowerCase().trim();
        try {
            if (distanceStr.contains("mile")) {
                String num = distanceStr.split("mile")[0].replaceAll("[^0-9.]+", "");
                return Double.parseDouble(num);
            } else if (distanceStr.contains("ft")) {
                String num = distanceStr.split("ft")[0].replaceAll("[^0-9.]+", "");
                double feet = Double.parseDouble(num);
                return feet / 5280.0;
            }
        } catch (Exception e) {
            return -1;
        }
        return -1;
    }
}
