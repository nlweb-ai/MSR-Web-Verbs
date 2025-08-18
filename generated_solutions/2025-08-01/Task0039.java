import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0039 {
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
            // Step 1: Get NASA Astronomy Picture of the Day for August 12, 2025
            Nasa nasa = new Nasa();
            JsonObject nasaResult = new JsonObject();
            
            try {
                // Get APOD for the astronomy night date
                Nasa.ApodResult apod = nasa.getApod("2025-08-12", true);
                
                if (apod != null) {
                    JsonObject apodObj = new JsonObject();
                    apodObj.addProperty("title", apod.title);
                    apodObj.addProperty("explanation", apod.explanation);
                    apodObj.addProperty("image_url", apod.url);
                    apodObj.addProperty("date", apod.date.toString());
                    apodObj.addProperty("event_relevance", "Perfect visual centerpiece for virtual astronomy night");
                    apodObj.addProperty("hd_quality", "High definition image suitable for screen sharing");
                    
                    nasaResult.add("astronomy_picture", apodObj);
                }
                
                nasaResult.addProperty("astronomy_night_date", "August 12, 2025");
                nasaResult.addProperty("content_source", "NASA Astronomy Picture of the Day");
                
            } catch (Exception e) {
                nasaResult.addProperty("error", "Failed to fetch NASA APOD: " + e.getMessage());
            }
            
            output.add("nasa_content", nasaResult);
            
            // Step 2: Get astronomical information from Wikimedia
            Wikimedia wikimedia = new Wikimedia();
            JsonObject astronomyInfo = new JsonObject();
            
            try {
                // Search for various astronomy topics
                Wikimedia.SearchResult constellationInfo = wikimedia.search("constellation August night sky", "en", 5);
                Wikimedia.SearchResult astronomyBasics = wikimedia.search("astronomy for beginners", "en", 4);
                Wikimedia.SearchResult stellarObjects = wikimedia.search("stars galaxies nebulae", "en", 4);
                Wikimedia.SearchResult telescopeInfo = wikimedia.search("telescope observing guide", "en", 3);
                
                JsonArray astronomyTopics = new JsonArray();
                
                // Process constellation information
                if (constellationInfo != null && constellationInfo.titles != null) {
                    for (String title : constellationInfo.titles) {
                        JsonObject topicObj = new JsonObject();
                        topicObj.addProperty("topic_title", title);
                        topicObj.addProperty("category", "Constellations & Night Sky");
                        topicObj.addProperty("relevance", "August sky viewing");
                        topicObj.addProperty("discussion_value", "High - perfect for stargazing event");
                        astronomyTopics.add(topicObj);
                    }
                }
                
                // Process astronomy basics
                if (astronomyBasics != null && astronomyBasics.titles != null) {
                    for (String title : astronomyBasics.titles) {
                        JsonObject topicObj = new JsonObject();
                        topicObj.addProperty("topic_title", title);
                        topicObj.addProperty("category", "Astronomy Fundamentals");
                        topicObj.addProperty("relevance", "Educational content");
                        topicObj.addProperty("discussion_value", "High - great for all skill levels");
                        astronomyTopics.add(topicObj);
                    }
                }
                
                // Process stellar objects
                if (stellarObjects != null && stellarObjects.titles != null) {
                    for (String title : stellarObjects.titles) {
                        JsonObject topicObj = new JsonObject();
                        topicObj.addProperty("topic_title", title);
                        topicObj.addProperty("category", "Stellar Objects");
                        topicObj.addProperty("relevance", "Deep space exploration");
                        topicObj.addProperty("discussion_value", "Medium - fascinating facts");
                        astronomyTopics.add(topicObj);
                    }
                }
                
                // Process telescope information
                if (telescopeInfo != null && telescopeInfo.titles != null) {
                    for (String title : telescopeInfo.titles) {
                        JsonObject topicObj = new JsonObject();
                        topicObj.addProperty("topic_title", title);
                        topicObj.addProperty("category", "Observing Equipment");
                        topicObj.addProperty("relevance", "Practical stargazing");
                        topicObj.addProperty("discussion_value", "High - equipment sharing tips");
                        astronomyTopics.add(topicObj);
                    }
                }
                
                astronomyInfo.add("astronomy_topics", astronomyTopics);
                astronomyInfo.addProperty("total_topics", astronomyTopics.size());
                astronomyInfo.addProperty("educational_focus", "Comprehensive astronomy knowledge for virtual stargazing");
                
            } catch (Exception e) {
                astronomyInfo.addProperty("error", "Failed to fetch astronomy information: " + e.getMessage());
            }
            
            output.add("astronomy_education", astronomyInfo);
            
            // Step 3: Create space-themed music atmosphere using Spotify
            Spotify spotify = new Spotify();
            JsonObject musicSection = new JsonObject();
            
            try {
                // Search for space-themed playlists
                java.util.List<Spotify.SpotifyPlaylist> spaceMusic = spotify.searchPlaylists("space music cosmic ambient", null, 5);
                java.util.List<Spotify.SpotifyPlaylist> chillMusic = spotify.searchPlaylists("chill ambient stargazing", null, 5);
                java.util.List<Spotify.SpotifyPlaylist> astronomyMusic = spotify.searchPlaylists("astronomy theme space exploration", null, 4);
                
                JsonArray playlistsArray = new JsonArray();
                
                // Process space music playlists
                if (spaceMusic != null) {
                    for (Spotify.SpotifyPlaylist playlist : spaceMusic) {
                        JsonObject playlistObj = new JsonObject();
                        playlistObj.addProperty("name", playlist.name);
                        playlistObj.addProperty("description", playlist.description);
                        playlistObj.addProperty("category", "Space & Cosmic Music");
                        playlistObj.addProperty("event_fit", "Perfect background for virtual stargazing");
                        playlistObj.addProperty("atmosphere", "Cosmic and contemplative");
                        playlistsArray.add(playlistObj);
                    }
                }
                
                // Process chill ambient music
                if (chillMusic != null) {
                    for (Spotify.SpotifyPlaylist playlist : chillMusic) {
                        JsonObject playlistObj = new JsonObject();
                        playlistObj.addProperty("name", playlist.name);
                        playlistObj.addProperty("description", playlist.description);
                        playlistObj.addProperty("category", "Ambient & Chill");
                        playlistObj.addProperty("event_fit", "Relaxing atmosphere for discussions");
                        playlistObj.addProperty("atmosphere", "Calm and focusing");
                        playlistsArray.add(playlistObj);
                    }
                }
                
                // Process astronomy-themed music
                if (astronomyMusic != null) {
                    for (Spotify.SpotifyPlaylist playlist : astronomyMusic) {
                        JsonObject playlistObj = new JsonObject();
                        playlistObj.addProperty("name", playlist.name);
                        playlistObj.addProperty("description", playlist.description);
                        playlistObj.addProperty("category", "Astronomy Themed");
                        playlistObj.addProperty("event_fit", "Thematically perfect for astronomy night");
                        playlistObj.addProperty("atmosphere", "Educational and inspiring");
                        playlistsArray.add(playlistObj);
                    }
                }
                
                musicSection.add("space_themed_playlists", playlistsArray);
                musicSection.addProperty("total_playlists", playlistsArray.size());
                musicSection.addProperty("music_purpose", "Creating perfect atmosphere for virtual astronomy night");
                
            } catch (Exception e) {
                musicSection.addProperty("error", "Failed to fetch space music: " + e.getMessage());
            }
            
            output.add("event_music", musicSection);
            
            // Step 4: Create virtual meeting invitation using Microsoft Teams
            teams_microsoft_com teams = new teams_microsoft_com(context);
            JsonObject teamsResult = new JsonObject();
            
            try {
                // Create comprehensive meeting message for the astronomy night
                String meetingMessage = "🌟 Virtual Astronomy Night - August 12, 2025 🌟\n\n" +
                    "Join us for an amazing virtual stargazing experience!\n\n" +
                    "📅 Date: Monday, August 12, 2025  \n" +
                    "🕖 Time: 8:00 PM - 10:00 PM  \n" +
                    "🌌 Theme: Exploring the Cosmos Together\n\n" +
                    "What we'll explore:\n" +
                    "• NASA's Astronomy Picture of the Day with detailed discussion\n" +
                    "• Learn about constellations visible in August night sky\n" +
                    "• Share telescope observations and astronomy photos\n" +
                    "• Discover fascinating facts about stars, galaxies, and nebulae\n" +
                    "• Listen to space-themed ambient music for relaxation\n" +
                    "• Discuss meteor showers and upcoming celestial events\n\n" +
                    "What to bring:\n" +
                    "• Your curiosity about the universe ✨\n" +
                    "• Telescope or binoculars (if you have them) 🔭\n" +
                    "• Any astronomy photos you'd like to share 📸\n" +
                    "• Questions about space and astronomy 🚀\n" +
                    "• A comfortable spot with good internet connection 💻\n\n" +
                    "This will be a relaxing and educational evening perfect for astronomy enthusiasts of all levels!\n\n" +
                    "RSVP by replying to this message. Can't wait to explore the cosmos with you! 🌠🪐";
                
                // Send invitation to Friends Group
                teams_microsoft_com.MessageStatus messageSent = teams.sendToGroupChat("Friends Group", meetingMessage);
                
                if (messageSent != null && "SUCCESS".equals(messageSent.status)) {
                    teamsResult.addProperty("invitation_sent", true);
                    teamsResult.addProperty("group_chat", "Friends Group");
                    teamsResult.addProperty("message_type", "Astronomy night invitation with comprehensive details");
                } else {
                    teamsResult.addProperty("invitation_sent", false);
                    teamsResult.addProperty("error", "Failed to send meeting invitation");
                }
                
            } catch (Exception e) {
                teamsResult.addProperty("error", "Failed to send Teams invitation: " + e.getMessage());
            }
            
            output.add("virtual_meeting_setup", teamsResult);
            
            // Step 5: Create comprehensive virtual astronomy night plan
            JsonObject astronomyNightPlan = new JsonObject();
            astronomyNightPlan.addProperty("event_title", "Virtual Astronomy Night with Friends");
            astronomyNightPlan.addProperty("date", "Monday, August 12, 2025");
            astronomyNightPlan.addProperty("time", "8:00 PM - 10:00 PM EST");
            astronomyNightPlan.addProperty("format", "Virtual Meeting via Video Call");
            astronomyNightPlan.addProperty("theme", "Exploring the Cosmos Together");
            
            // Event agenda
            JsonArray agenda = new JsonArray();
            
            JsonObject opening = new JsonObject();
            opening.addProperty("time", "8:00 PM - 8:15 PM");
            opening.addProperty("activity", "Welcome & Introductions");
            opening.addProperty("description", "Greet participants, share tonight's agenda, get everyone settled");
            agenda.add(opening);
            
            JsonObject apodSegment = new JsonObject();
            apodSegment.addProperty("time", "8:15 PM - 8:35 PM");
            apodSegment.addProperty("activity", "NASA Astronomy Picture of the Day");
            apodSegment.addProperty("description", "View and discuss August 12th featured space image in detail");
            agenda.add(apodSegment);
            
            JsonObject constellations = new JsonObject();
            constellations.addProperty("time", "8:35 PM - 8:55 PM");
            constellations.addProperty("activity", "August Night Sky Tour");
            constellations.addProperty("description", "Explore constellations visible this month, sharing tips");
            agenda.add(constellations);
            
            JsonObject sharing = new JsonObject();
            sharing.addProperty("time", "8:55 PM - 9:25 PM");
            sharing.addProperty("activity", "Participant Sharing Session");
            sharing.addProperty("description", "Share telescope photos, observations, and astronomy experiences");
            agenda.add(sharing);
            
            JsonObject discussion = new JsonObject();
            discussion.addProperty("time", "9:25 PM - 9:50 PM");
            discussion.addProperty("activity", "Astronomy Q&A and Fun Facts");
            discussion.addProperty("description", "Answer questions, share fascinating space facts and discoveries");
            agenda.add(discussion);
            
            JsonObject closing = new JsonObject();
            closing.addProperty("time", "9:50 PM - 10:00 PM");
            closing.addProperty("activity", "Closing & Next Event Planning");
            closing.addProperty("description", "Wrap up discussion, plan future astronomy meetups");
            agenda.add(closing);
            
            astronomyNightPlan.add("event_agenda", agenda);
            
            // Event resources and preparation
            JsonObject resources = new JsonObject();
            
            JsonArray visualResources = new JsonArray();
            if (nasaResult.has("astronomy_picture")) {
                JsonObject nasaImage = nasaResult.get("astronomy_picture").getAsJsonObject();
                visualResources.add("NASA APOD: " + nasaImage.get("title").getAsString());
                visualResources.add("High-definition space imagery for screen sharing");
            }
            visualResources.add("Constellation charts for August night sky");
            visualResources.add("Star maps and celestial event calendars");
            
            resources.add("visual_materials", visualResources);
            
            JsonArray educationalResources = new JsonArray();
            if (astronomyInfo.has("astronomy_topics")) {
                JsonArray topics = astronomyInfo.get("astronomy_topics").getAsJsonArray();
                for (int i = 0; i < Math.min(5, topics.size()); i++) {
                    JsonObject topic = topics.get(i).getAsJsonObject();
                    educationalResources.add(topic.get("category").getAsString() + " resources");
                }
            }
            
            resources.add("educational_content", educationalResources);
            
            JsonArray musicResources = new JsonArray();
            if (musicSection.has("space_themed_playlists")) {
                JsonArray playlists = musicSection.get("space_themed_playlists").getAsJsonArray();
                for (int i = 0; i < Math.min(3, playlists.size()); i++) {
                    JsonObject playlist = playlists.get(i).getAsJsonObject();
                    musicResources.add(playlist.get("name").getAsString() + " - " + playlist.get("event_fit").getAsString());
                }
            }
            
            resources.add("background_music_options", musicResources);
            
            astronomyNightPlan.add("event_resources", resources);
            
            // Participant preparation suggestions
            JsonArray participantPrep = new JsonArray();
            participantPrep.add("Check local weather for potential real sky observation opportunities");
            participantPrep.add("Gather any telescopes, binoculars, or astronomy equipment to show");
            participantPrep.add("Prepare any astronomy photos or observations to share");
            participantPrep.add("Think of space and astronomy questions you'd like to discuss");
            participantPrep.add("Find a comfortable spot with good internet connection");
            participantPrep.add("Consider dimming lights to create a stargazing atmosphere");
            
            astronomyNightPlan.add("participant_preparation", participantPrep);
            
            // Event success metrics
            JsonObject successMetrics = new JsonObject();
            successMetrics.addProperty("expected_participants", "5-10 astronomy enthusiasts");
            successMetrics.addProperty("educational_goals", "Learn about current astronomical events and general space knowledge");
            successMetrics.addProperty("social_goals", "Connect friends through shared interest in astronomy");
            successMetrics.addProperty("follow_up_plans", "Plan regular monthly virtual astronomy nights");
            
            astronomyNightPlan.add("success_planning", successMetrics);
            
            output.add("complete_astronomy_night_plan", astronomyNightPlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while organizing virtual astronomy night: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
