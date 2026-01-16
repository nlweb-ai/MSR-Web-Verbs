// import com.google.gson.Gson;
// import com.google.gson.GsonBuilder;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Locator;


public class maps_google_com extends com_base {
    //write a constructor that takes BrowserContext context as an argument
    public maps_google_com(BrowserContext _context) {
        super(_context);
    }

    /**
     * Gets travel information between two locations.
     * @param source The starting location
     * @param destination The destination location
     * @return DirectionResult containing travel time, distance, and route
     */
    public DirectionResult get_direction(String source, String destination) {
        page.navigate("https://www.google.com/maps/dir//");
        
        /*the <input> element is as follows:
         * <input autocomplete="off" class="tactile-searchbox-input" aria-autocomplete="list" aria-controls="sbsg50" dir="ltr" spellcheck="false" style="border: none; padding: 0px; margin: 0px; height: auto; width: 100%; outline: none;" aria-label="Choose starting point, or click on the map..." placeholder="Choose starting point, or click on the map..." tooltip="Choose starting point, or click on the map...">
         */
        Locator sourceInput = page.locator("input[placeholder='Choose starting point, or click on the map...']");
        sourceInput.fill(source);
        //press Enter to submit the input
        sourceInput.press("Enter");
        //wait for the page to update
        page.waitForTimeout(1000);
        // Fill in the destination location
        Locator destinationInput = page.locator("input[placeholder='Choose destination, or click on the map...']");
        destinationInput.fill(destination);
        //press Enter to submit the input
        page.waitForTimeout(1000);
        destinationInput.press("Enter");
        // Wait for the directions to load
        page.waitForLoadState();
        Locator drivingButton= page.locator("div[aria-label='Driving']");
        // Click the "Driving" button to get driving directions
        drivingButton.click();
        // Wait for the directions to load
        page.waitForLoadState();
        String travelTime = "N/A";
        String distance = "N/A";
        String route = "N/A";
        
        /*
         * <div tabindex="0" class="UgZKXd clearfix selected yYG3jf" data-trip-index="0" id="section-directions-trip-0" role="link" jslog="14905; track:click;metadata:WyIwYWhVS0V3aU80WU9idmJXTkF4VWRJVFFJSFQtM0FyZ1EtQ1FJQmlnQyJd" jsaction="pane.wfvdle17.selectTrip; keydown:pane.wfvdle17.selectTrip"><span id="section-directions-trip-travel-mode-0"><span class="Os0QJc google-symbols" aria-label="Driving" role="img" style="font-size: 24px;"></span></span><div class="MespJc"><div><div class="XdKEzd"><div class="Fk3sm fontHeadlineSmall delay-heavy ">11 min</div><div class="ivN21e tUEI8e fontBodyMedium"><div>4.9 miles</div></div></div><div><h1 class="VuCHmb fontHeadlineSmall " id="section-directions-trip-title-0">via WA-520 W</h1></div><div class="ue5qRc tUEI8e fontBodyMedium"> <span class="mTOalf" style=""><span><span class="Bzv5Cd cGU3ub OEQ85d aAGpje ltr" style="display: none; background-color: rgb(255, 255, 255);"><span class="cukLmd">Fastest route, despite the usual traffic</span></span><span class="JxBYrc pk9Qwb " dir="ltr">Fastest route, despite the usual traffic</span></span></span></div><div><button class="TIQqpf fontTitleSmall Hk4XGb" aria-labelledby="section-directions-trip-details-msg-0"><div class="J7Hggc XbJon"><div class="OyjIsf "></div> <span id="section-directions-trip-details-msg-0">Details</span></div></button></div></div></div><div class="ieZ08"></div></div>
         */
        //use id="section-directions-trip-0" to locate the first trip
        Locator directions = page.locator("#section-directions-trip-0");
        page.waitForTimeout(2000);
        if (directions.count() == 0) {
            directions = page.locator("#section-directions-trip-0");
            page.waitForTimeout(2000);
        }
        //extract the travel time and distance
        if (directions.count() > 0) {
            travelTime = directions.locator(".Fk3sm").innerText();
            distance = directions.locator(".ivN21e").innerText();
            route = directions.locator("#section-directions-trip-title-0").innerText();
        }
        DirectionResult result = new DirectionResult(travelTime, distance, route);
        System.out.println(result);
        return result;
    }

    /**
     * Represents the result of a direction query, including travel time, distance, and route.
     */
    public static class DirectionResult {
        /** Estimated travel time. */
        public final String travelTime;
        /** Distance of the route. */
        public final String distance;
        /** Route description. */
        public final String route;
        public DirectionResult(String travelTime, String distance, String route) {
            this.travelTime = travelTime;
            this.distance = distance;
            this.route = route;
        }
        @Override
        public String toString() {
            return String.format("Travel Time: %s\nDistance: %s\nRoute: %s", travelTime, distance, route);
        }
    }

    //generate javadoc for the method
    /**
     * This method retrieves a list of nearby businesses based on a reference point and business description.
     * 
     * @param referencePoint The location from which to find nearby businesses (e.g., "Seattle, WA").
     * @param businessDescription A description of the type of business to search for (e.g., "coffee shop").
     * @param maxCount The maximum number of businesses to return.
     * @return A list of of the nearest businesses. Each business info contains a "name" property and an "address" property.
     */
    /**
     * This method retrieves a list of nearby businesses based on a reference point and business description.
     *
     * @param referencePoint The location from which to find nearby businesses (e.g., "Seattle, WA").
     * @param businessDescription A description of the type of business to search for (e.g., "coffee shop").
     * @param maxCount The maximum number of businesses to return.
     * @return NearestBusinessesResult containing a list of the nearest businesses.
     */
    public NearestBusinessesResult get_nearestBusinesses(String referencePoint, String businessDescription, int maxCount) {
        page.navigate("https://www.google.com/maps/place/");
        Locator inputboxes = page.locator("input[aria-controls=\"ucc-0\"]");
        Locator sourceInput = inputboxes.nth(0);
        sourceInput.fill(referencePoint);
        sourceInput.press("Enter");
        page.waitForTimeout(2000);
        Locator listOfReferences = page.locator(".Nv2PK.Q2HXcd.THOPZb");
        if (listOfReferences.count() > 0) {
            Locator refP = listOfReferences.first();
            refP.click();      
            page.waitForLoadState();      
        }

        Locator nearbyButton = page.locator("button[aria-label='Nearby']");
        nearbyButton.click();
        page.waitForLoadState();
        Locator searchbox = page.locator("input[aria-controls=\"ucc-0\"]");
        searchbox.fill(businessDescription);
        searchbox.press("Enter");
        page.waitForTimeout(2000);
        Locator resultsFor = page.locator("div[aria-label^='Results for']");
        Locator listOfBusinesses = resultsFor.locator(".bfdHYd.Ppzolf.OFBs3e");
        int businessCount = Math.min(listOfBusinesses.count(), maxCount);
        java.util.List<BusinessInfo> businesses = new java.util.ArrayList<>();
        for (int i = 0; i < businessCount; i++) {
            Locator titleLocator = listOfBusinesses.nth(i).locator(".fontHeadlineSmall");
            String businessName = titleLocator.first().innerText();
            String address; 
            try {
                Locator addressLocator = listOfBusinesses.nth(i).locator(".W4Efsd > .W4Efsd");
                String[] threeStrings = addressLocator.first().innerText().split("·");
                address = threeStrings[threeStrings.length-1].trim();
            } catch (Exception e) {
                address = "Address not found"; // Default value if address parsing fails
            }
            businesses.add(new BusinessInfo(businessName, address));
        }
        NearestBusinessesResult result = new NearestBusinessesResult(referencePoint, businessDescription, businesses);
        System.out.println(result);
        return result;
    }

    /**
     * Represents a business with a name and address.
     */
    public static class BusinessInfo {
        /** Name of the business. */
        public final String name;
        /** Address of the business. */
        public final String address;
        public BusinessInfo(String name, String address) {
            this.name = name;
            this.address = address;
        }
        @Override
        public String toString() {
            return String.format("%s (%s)", name, address);
        }
    }

    /**
     * Represents the result of a nearest businesses query.
     */
    public static class NearestBusinessesResult {
        /** The reference point for the search. */
        public final String referencePoint;
        /** The business description searched for. */
        public final String businessDescription;
        /** List of found businesses. */
        public final java.util.List<BusinessInfo> businesses;
        public NearestBusinessesResult(String referencePoint, String businessDescription, java.util.List<BusinessInfo> businesses) {
            this.referencePoint = referencePoint;
            this.businessDescription = businessDescription;
            this.businesses = businesses;
        }
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append(String.format("Reference Point: %s\nBusiness Description: %s\nFound %d businesses:\n", referencePoint, businessDescription, businesses.size()));
            for (int i = 0; i < businesses.size(); i++) {
                sb.append(String.format("  %d. %s\n", i + 1, businesses.get(i)));
            }
            return sb.toString();
        }
    }

    /**
     * Creates a new list on Google Maps and adds the specified places to it.
     * 
     * @param listName The name of the list to create (e.g., "Anchorage 2025").
     * @param places A list of place names to add to the list (e.g., ["Anchorage Museum at Rasmuson Center", "Alaska Native Heritage Center"]).
     * @return true if the list was created successfully and all places were added, false otherwise.
     */
    public boolean createList(String listName, java.util.List<String> places) {
        try {
            // Navigate to Google Maps
            page.navigate("https://www.google.com/maps/");
            page.waitForLoadState();
            
            // Click on the "Saved" button
            Locator savedButton = page.locator("text=Saved");
            if (savedButton.count() == 0) {
                System.out.println("Saved button not found");
                return false;
            }
            savedButton.click();
            page.waitForTimeout(2000);
            
            // Click on "New list"
            Locator newListButton = page.locator("text=\"New list\"");
            if (newListButton.count() == 0) {
                System.out.println("New list button not found");
                return false;
            }
            newListButton.click();
            page.waitForTimeout(2000);
            
            // Fill in the list name
            Locator listNameInput = page.locator(".fontTitleLarge");
            if (listNameInput.count() == 0) {
                System.out.println("List name input not found");
                return false;
            }
            listNameInput.fill(listName);
            page.waitForTimeout(2000);
            
            // Add each place to the list
            for (String place : places) {
                // Fill in the search box for adding a place
                Locator searchInput = page.locator("[aria-label=\"Search for a place to add\"]");
                if (searchInput.count() == 0) {
                    System.out.println("Search input for place not found");
                    return false;
                }
                searchInput.fill(place);
                page.waitForTimeout(2000);
                
                // Click on the first search result
                Locator firstResult = page.locator("#cell-1x0").first();
                if (firstResult.count() == 0) {
                    System.out.println("First search result not found for place: " + place);
                    return false;
                }
                firstResult.click();
                page.waitForTimeout(2000);
            }
            
            System.out.println("Successfully created list '" + listName + "' with " + places.size() + " places");
            return true;
            
        } catch (Exception e) {
            System.out.println("Error creating list: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Deletes saved lists from Google Maps.
     * 
     * @param listName All lists whose names contain listName will be deleted.
     * @return true if no matching list was not or all such lists were deleted successfully, false if there was an exception.
     */
    public boolean deleteList(String listName) {
        try {
            // Navigate to Google Maps
            page.navigate("https://www.google.com/maps/");
            page.waitForLoadState();
            
            // Click on the "Saved" button
            Locator savedButton = page.locator("text=Saved");
            if (savedButton.count() == 0) {
                System.out.println("Saved button not found");
                return false;
            }
            savedButton.click();
            page.waitForTimeout(2000);

            Locator panel = page.locator("role=tabpanel").first();
            if (panel.count() == 0) {
                System.out.println("Panel not found");
                return false;
            }

            while (true) {
                // Loop through all direct children of panel
                Locator children = panel.locator("> *");
                int childCount = children.count();
                int i;
                for (i = 0; i < childCount; i++) {
                    Locator child = children.nth(i);
                    if (child.innerText().contains(listName)) {
                        Locator MoreOptionsButton = child.locator("button[aria-label='More options']").first();
                        MoreOptionsButton.click();
                        page.waitForTimeout(1000);
                        Locator deleteButton = page.locator(".fxNQSd:nth-child(5)").first();
                        if (deleteButton.count() == 0) {
                            System.out.println("Delete button not found");
                            return false;
                        }
                        deleteButton.click();
                        page.waitForTimeout(1000);
                        Locator confirmButton = page.locator(".peSXAf .DVeyrd").first();
                        if (confirmButton.count() == 0) {
                            System.out.println("Confirm button not found");
                            return false;
                        }
                        confirmButton.click();
                        page.waitForTimeout(1000);
                        System.out.println("Successfully deleted list: " + listName);
                        break;
                    }
                }
                if (i==childCount) {
                    break;
                }
            }
            return true;
        } catch (Exception e) {
            System.out.println("Error deleting list: " + e.getMessage());
            return false;
        }
    }
}