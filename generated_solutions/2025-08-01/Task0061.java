import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0061 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Compare prices of air purifiers at Costco
            costco_com costco = new costco_com(context);
            costco_com.ProductListResult airPurifiers = costco.searchProducts("air purifier");
            JsonArray airPurifierArr = new JsonArray();
            if (airPurifiers.products != null) {
                for (costco_com.ProductInfo p : airPurifiers.products) {
                    JsonObject obj = new JsonObject();
                    obj.addProperty("name", p.productName);
                    obj.addProperty("price", p.productPrice != null ? p.productPrice.amount : null);
                    airPurifierArr.add(obj);
                }
            }
            result.add("costco_air_purifiers", airPurifierArr);

            // 2. Find apartments for rent in Seattle, WA, under $2500 (today)
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentsResult = redfin.searchApartments("Seattle, WA", 0, 2500);
            List<redfin_com.ApartmentInfo> apartments = apartmentsResult.apartments != null ? apartmentsResult.apartments : new ArrayList<>();
            JsonArray apartmentsArr = new JsonArray();
            for (redfin_com.ApartmentInfo apt : apartments) {
                JsonObject obj = new JsonObject();
                obj.addProperty("address", apt.address);
                obj.addProperty("price", apt.price != null ? apt.price.amount : null);
                obj.addProperty("url", apt.url);
                apartmentsArr.add(obj);
            }
            result.add("apartments", apartmentsArr);

            // 3. For top 3 apartments, check if any address is within 2 miles of a Costco warehouse
            // Use Google Maps to find nearby Costcos
            maps_google_com maps = new maps_google_com(context);
            // Get up to 5 costco warehouses in Seattle
            maps_google_com.NearestBusinessesResult warehousesResult = maps.get_nearestBusinesses("Seattle, WA", "Costco Warehouse", 5);
            List<maps_google_com.BusinessInfo> warehouses = warehousesResult.businesses != null ? warehousesResult.businesses : new ArrayList<>();
            List<redfin_com.ApartmentInfo> closeApts = new ArrayList<>();
            int maxApts = Math.min(3, apartments.size());
            for (int i = 0; i < maxApts; i++) {
                redfin_com.ApartmentInfo apt = apartments.get(i);
                String aptAddr = apt.address;
                for (maps_google_com.BusinessInfo warehouse : warehouses) {
                    String warehouseAddr = warehouse.address;
                    maps_google_com.DirectionResult dir = maps.get_direction(aptAddr, warehouseAddr);
                    // Distance is a string like "1.8 miles" or "950 ft"
                    double miles = parseMiles(dir.distance);
                    if (miles > 0 && miles <= 2.0) {
                        closeApts.add(apt);
                        break;
                    }
                }
            }
            JsonArray closeAptsArr = new JsonArray();
            for (redfin_com.ApartmentInfo apt : closeApts) {
                JsonObject obj = new JsonObject();
                obj.addProperty("address", apt.address);
                obj.addProperty("price", apt.price != null ? apt.price.amount : null);
                obj.addProperty("url", apt.url);
                closeAptsArr.add(obj);
            }
            result.add("close_apartments", closeAptsArr);

            // 4. If any close apartment, get most recent news headline about air quality in Seattle
            if (!closeApts.isEmpty()) {
                News newsApi = new News();
                News.NewsResponse newsResp = newsApi.searchEverything("air quality Seattle");
                JsonArray newsArr = new JsonArray();
                if (newsResp.articles != null && !newsResp.articles.isEmpty()) {
                    News.NewsArticle article = newsResp.articles.get(0);
                    JsonObject newsObj = new JsonObject();
                    newsObj.addProperty("title", article.title);
                    newsObj.addProperty("description", article.description);
                    newsObj.addProperty("url", article.url);
                    newsObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                    newsObj.addProperty("source", article.source);
                    newsArr.add(newsObj);
                }
                result.add("air_quality_news", newsArr);
            }
        } catch (Exception e) {
            result.addProperty("error", e.toString());
        }
        return result;
    }

    // Helper to parse miles from a string like "1.8 miles" or "950 ft"
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
