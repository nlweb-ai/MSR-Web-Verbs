import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0063 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Search for kitchen appliances at Costco and get top 3 products
            costco_com costco = new costco_com(context);
            costco_com.ProductListResult appliances = costco.searchProducts("kitchen appliances");
            JsonArray appliancesArr = new JsonArray();
            List<costco_com.ProductInfo> top3Products = new ArrayList<>();
            
            if (appliances.products != null && !appliances.products.isEmpty()) {
                int productCount = Math.min(3, appliances.products.size());
                for (int i = 0; i < productCount; i++) {
                    costco_com.ProductInfo product = appliances.products.get(i);
                    top3Products.add(product);
                    JsonObject productObj = new JsonObject();
                    productObj.addProperty("name", product.productName);
                    productObj.addProperty("price", product.productPrice != null ? product.productPrice.amount : null);
                    appliancesArr.add(productObj);
                }
            }
            result.add("top_3_kitchen_appliances", appliancesArr);

            // 2. Find apartments for rent in San Jose, CA, under $3000 within 5 miles of Costco warehouse
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentsResult = redfin.searchApartments("San Jose, CA", 0, 3000);
            List<redfin_com.ApartmentInfo> apartments = apartmentsResult.apartments != null ? apartmentsResult.apartments : new ArrayList<>();
            
            // Find nearby Costco warehouses in San Jose
            maps_google_com maps = new maps_google_com(context);
            maps_google_com.NearestBusinessesResult warehousesResult = maps.get_nearestBusinesses("San Jose, CA", "Costco Warehouse", 5);
            List<maps_google_com.BusinessInfo> warehouses = warehousesResult.businesses != null ? warehousesResult.businesses : new ArrayList<>();
            
            JsonArray matchingApartmentsArr = new JsonArray();
            List<redfin_com.ApartmentInfo> closeApartments = new ArrayList<>();
            
            for (redfin_com.ApartmentInfo apt : apartments) {
                String aptAddr = apt.address;
                boolean isNearCostco = false;
                
                for (maps_google_com.BusinessInfo warehouse : warehouses) {
                    String warehouseAddr = warehouse.address;
                    maps_google_com.DirectionResult dir = maps.get_direction(aptAddr, warehouseAddr);
                    double miles = parseMiles(dir.distance);
                    if (miles > 0 && miles <= 5.0) {
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
                    matchingApartmentsArr.add(aptObj);
                }
            }
            result.add("apartments_near_costco", matchingApartmentsArr);

            // 3. For each matching apartment, check for kitchen design books published after 2020
            OpenLibrary openLibrary = new OpenLibrary();
            JsonArray kitchenBooksArr = new JsonArray();
            boolean foundKitchenBooks = false;
            
            if (!closeApartments.isEmpty()) {
                List<OpenLibrary.BookInfo> books = openLibrary.search("kitchen design", "title,first_publish_year", "new", "en", 20, 1);
                
                for (OpenLibrary.BookInfo book : books) {
                    Integer bookYear = extractYearFromTitle(book.title);
                    if (bookYear != null && bookYear > 2020) {
                        foundKitchenBooks = true;
                        JsonObject bookObj = new JsonObject();
                        bookObj.addProperty("title", book.title);
                        bookObj.addProperty("estimated_year", bookYear);
                        kitchenBooksArr.add(bookObj);
                    }
                }
            }
            result.add("kitchen_design_books_after_2020", kitchenBooksArr);
            result.addProperty("found_recent_kitchen_books", foundKitchenBooks);

            // 4. Get weather forecast for San Jose, CA for August 10, 2025
            LocalDate targetDate = LocalDate.of(2025, 8, 10);
            LocalDate today = LocalDate.now();
            JsonObject weatherObj = new JsonObject();
            
            if (!targetDate.isBefore(today) && targetDate.isBefore(today.plusDays(5))) {
                // San Jose, CA coordinates: 37.3382, -121.8863
                OpenWeather openWeather = new OpenWeather();
                OpenWeather.WeatherForecastData forecast = openWeather.getForecast5Day(37.3382, -121.8863);
                
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
            } else {
                weatherObj.addProperty("target_date", targetDate.toString());
                weatherObj.addProperty("message", "Target date is outside 5-day forecast range");
            }
            result.add("weather_forecast_san_jose", weatherObj);
            
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
    
    // Helper method to extract year from book title
    private static Integer extractYearFromTitle(String title) {
        if (title == null) return null;
        
        // Look for 4-digit years in the title (between 2020-2030 for recent books)
        for (int year = 2020; year <= 2030; year++) {
            if (title.contains(String.valueOf(year))) {
                return year;
            }
        }
        
        return null;
    }
}
