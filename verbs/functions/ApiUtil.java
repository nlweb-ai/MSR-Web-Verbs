import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Utility class for common API operations
 * Contains shared parsing and configuration loading functions
 */
public class ApiUtil {
    /**
     * Extracts a field value from a JSON string using regex. For demo only.
     * @param json The JSON string
     * @param key The key to extract
     * @return The value as a string, or null if not found
     */
    public static String extractJsonField(String json, String key) {
        if (json == null || key == null) return null;
        String pattern = "\"" + key + "\"\\s*:\\s*\"([^\"]+)\"";
        java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern);
        java.util.regex.Matcher m = p.matcher(json);
        if (m.find()) {
            return m.group(1);
        }
        return null;
    }
    
    /**
     * Load a specific environment variable value from the .env_api_keys file
     * @param key The environment variable key to load
     * @return The value, or null if not found
     */
    public static String loadEnvValue(String key) {
        try {
            List<String> lines = Files.readAllLines(Paths.get(".env_api_keys"));
            for (String line : lines) {
                line = line.trim();
                // Handle both "KEY=value" and "KEY = value" formats
                if (line.startsWith(key)) {
                    int equalsIndex = line.indexOf('=');
                    if (equalsIndex > 0) {
                        String foundKey = line.substring(0, equalsIndex).trim();
                        if (foundKey.equals(key)) {
                            String value = line.substring(equalsIndex + 1).trim();
                            return value.isEmpty() ? null : value;
                        }
                    }
                }
            }
        } catch (IOException e) {
            System.err.println("Warning: Could not read .env_api_keys file: " + e.getMessage());
        }
        return null;
    }
    
    /**
     * Build the user agent string from environment variables
     * Format: 'APP_NAME (EMAIL)' as required by API guidelines
     * @param fallbackAppName The fallback app name if env var not found
     * @param fallbackEmail The fallback email if env var not found
     * @return Formatted user agent string
     */
    public static String buildUserAgent(String fallbackAppName, String fallbackEmail) {
        String appName = loadEnvValue("WIKIMEDIA_APP_NAME");
        String email = loadEnvValue("WIKIMEDIA_EMAIL");
        
        if (appName != null && email != null) {
            return appName + " (" + email + ")";
        } else {
            // Fallback to provided defaults if env vars not found
            return fallbackAppName + " (" + fallbackEmail + ")";
        }
    }
    
    /**
     * Build the Wikimedia user agent string from environment variables
     * @return Formatted user agent string for Wikimedia API
     */
    public static String buildWikimediaUserAgent() {
        String appName = loadEnvValue("WIKIMEDIA_APP_NAME");
        String email = loadEnvValue("WIKIMEDIA_EMAIL");
        return buildUserAgent(appName + "/1.0", email);
    }
    
    /**
     * Build the OpenLibrary user agent string from environment variables
     * @return Formatted user agent string for OpenLibrary API
     */
    public static String buildOpenLibraryUserAgent() {
        return buildUserAgent("JavaOpenLibraryClient/1.0", "example@email.com");
    }
    
    /**
     * Build the NASA user agent string from environment variables
     * @return Formatted user agent string for NASA API
     */
    public static String buildNasaUserAgent() {
        return buildUserAgent("JavaNasaClient/1.0", "example@email.com");
    }
      /**
     * Build the News user agent string from environment variables
     * @return Formatted user agent string for News API
     */
    public static String buildNewsUserAgent() {
        return buildUserAgent("JavaNewsClient/1.0", "example@email.com");
    }
      /**
     * Build the OpenWeather user agent string
     * @return Formatted user agent string for OpenWeather API
     */
    public static String buildOpenWeatherUserAgent() {
        return buildUserAgent("JavaOpenWeatherClient/1.0", "example@email.com");
    }
    
    /**
     * Build the GitHub user agent string
     * @return Formatted user agent string for GitHub API
     */
    public static String buildGitHubUserAgent() {
        return buildUserAgent("JavaGitHubClient/1.0", "example@email.com");
    }
   
    /**
     * Helper method to count regex matches in a string
     * @param text The text to search in
     * @param regex The regex pattern to match
     * @param flags Pattern flags
     * @return Number of matches found
     */
    public static int countMatches(String text, String regex, int flags) {
        Pattern pattern = Pattern.compile(regex, flags);
        Matcher matcher = pattern.matcher(text);
        int count = 0;
        while (matcher.find()) {
            count++;
        }
        return count;
    }
   
    /**
     * Simple JSON parsing to extract GitHub repository data using regex
     * In a real application, you'd use a proper JSON library like Jackson or Gson
     * @param jsonResponse The JSON response string from GitHub API
     * @return List of repository information (name, description, stars, etc.)
     */
    public static List<String> parseGitHubRepositoryData(String jsonResponse) {
        List<String> repositoryData = new ArrayList<>();
        
        // Check if it's an array response (list repos) or single object (get repo)
        boolean isArrayResponse = jsonResponse.trim().startsWith("[");
        
        if (isArrayResponse) {
            // Handle array response for listing repositories
            repositoryData.add("=== REPOSITORIES ===");
            repositoryData.add("");
            
            // Remove array brackets and split entries
            String content = jsonResponse.trim();
            if (content.startsWith("[") && content.endsWith("]")) {
                content = content.substring(1, content.length() - 1);
            }
            
            // Simple splitting by repository objects
            String[] repoEntries = content.split("\\}\\s*,\\s*\\{");
            
            int count = 0;
            for (String entry : repoEntries) {
                if (count >= 10) break; // Limit to first 10 results
                
                // Clean up the entry
                if (!entry.startsWith("{")) entry = "{" + entry;
                if (!entry.endsWith("}")) entry = entry + "}";
                
                // Extract repository data
                Pattern namePattern = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]+)\"");
                Pattern fullNamePattern = Pattern.compile("\"full_name\"\\s*:\\s*\"([^\"]+)\"");
                Pattern descriptionPattern = Pattern.compile("\"description\"\\s*:\\s*\"([^\"]+)\"");
                Pattern starsPattern = Pattern.compile("\"stargazers_count\"\\s*:\\s*(\\d+)");
                Pattern forksPattern = Pattern.compile("\"forks_count\"\\s*:\\s*(\\d+)");
                Pattern languagePattern = Pattern.compile("\"language\"\\s*:\\s*\"([^\"]+)\"");
                Pattern privatePattern = Pattern.compile("\"private\"\\s*:\\s*(true|false)");
                Pattern urlPattern = Pattern.compile("\"html_url\"\\s*:\\s*\"([^\"]+)\"");
                
                Matcher nameMatcher = namePattern.matcher(entry);
                Matcher fullNameMatcher = fullNamePattern.matcher(entry);
                Matcher descriptionMatcher = descriptionPattern.matcher(entry);
                Matcher starsMatcher = starsPattern.matcher(entry);
                Matcher forksMatcher = forksPattern.matcher(entry);
                Matcher languageMatcher = languagePattern.matcher(entry);
                Matcher privateMatcher = privatePattern.matcher(entry);
                Matcher urlMatcher = urlPattern.matcher(entry);
                
                repositoryData.add("--- Repository " + (count + 1) + " ---");
                
                if (nameMatcher.find()) {
                    repositoryData.add("Name: " + nameMatcher.group(1));
                }
                if (fullNameMatcher.find()) {
                    repositoryData.add("Full Name: " + fullNameMatcher.group(1));
                }
                if (descriptionMatcher.find()) {
                    String desc = descriptionMatcher.group(1);
                    if (!desc.equals("null") && !desc.isEmpty()) {
                        repositoryData.add("Description: " + desc);
                    }
                }
                if (languageMatcher.find()) {
                    String lang = languageMatcher.group(1);
                    if (!lang.equals("null") && !lang.isEmpty()) {
                        repositoryData.add("Language: " + lang);
                    }
                }
                if (starsMatcher.find()) {
                    repositoryData.add("Stars: " + starsMatcher.group(1));
                }
                if (forksMatcher.find()) {
                    repositoryData.add("Forks: " + forksMatcher.group(1));
                }
                if (privateMatcher.find()) {
                    repositoryData.add("Private: " + privateMatcher.group(1));
                }
                if (urlMatcher.find()) {
                    repositoryData.add("URL: " + urlMatcher.group(1));
                }
                
                repositoryData.add("");
                count++;
            }
        } else {
            // Handle single repository object
            repositoryData.add("=== REPOSITORY DETAILS ===");
            repositoryData.add("");
            
            // Extract repository data
            Pattern namePattern = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]+)\"");
            Pattern fullNamePattern = Pattern.compile("\"full_name\"\\s*:\\s*\"([^\"]+)\"");
            Pattern descriptionPattern = Pattern.compile("\"description\"\\s*:\\s*\"([^\"]+)\"");
            Pattern starsPattern = Pattern.compile("\"stargazers_count\"\\s*:\\s*(\\d+)");
            Pattern forksPattern = Pattern.compile("\"forks_count\"\\s*:\\s*(\\d+)");
            Pattern watchersPattern = Pattern.compile("\"watchers_count\"\\s*:\\s*(\\d+)");
            Pattern languagePattern = Pattern.compile("\"language\"\\s*:\\s*\"([^\"]+)\"");
            Pattern privatePattern = Pattern.compile("\"private\"\\s*:\\s*(true|false)");
            Pattern urlPattern = Pattern.compile("\"html_url\"\\s*:\\s*\"([^\"]+)\"");
            Pattern cloneUrlPattern = Pattern.compile("\"clone_url\"\\s*:\\s*\"([^\"]+)\"");
            Pattern createdPattern = Pattern.compile("\"created_at\"\\s*:\\s*\"([^\"]+)\"");
            Pattern updatedPattern = Pattern.compile("\"updated_at\"\\s*:\\s*\"([^\"]+)\"");
            Pattern sizePattern = Pattern.compile("\"size\"\\s*:\\s*(\\d+)");
            Pattern defaultBranchPattern = Pattern.compile("\"default_branch\"\\s*:\\s*\"([^\"]+)\"");
            
            Matcher nameMatcher = namePattern.matcher(jsonResponse);
            Matcher fullNameMatcher = fullNamePattern.matcher(jsonResponse);
            Matcher descriptionMatcher = descriptionPattern.matcher(jsonResponse);
            Matcher starsMatcher = starsPattern.matcher(jsonResponse);
            Matcher forksMatcher = forksPattern.matcher(jsonResponse);
            Matcher watchersMatcher = watchersPattern.matcher(jsonResponse);
            Matcher languageMatcher = languagePattern.matcher(jsonResponse);
            Matcher privateMatcher = privatePattern.matcher(jsonResponse);
            Matcher urlMatcher = urlPattern.matcher(jsonResponse);
            Matcher cloneUrlMatcher = cloneUrlPattern.matcher(jsonResponse);
            Matcher createdMatcher = createdPattern.matcher(jsonResponse);
            Matcher updatedMatcher = updatedPattern.matcher(jsonResponse);
            Matcher sizeMatcher = sizePattern.matcher(jsonResponse);
            Matcher defaultBranchMatcher = defaultBranchPattern.matcher(jsonResponse);
            
            if (nameMatcher.find()) {
                repositoryData.add("Name: " + nameMatcher.group(1));
            }
            if (fullNameMatcher.find()) {
                repositoryData.add("Full Name: " + fullNameMatcher.group(1));
            }
            if (descriptionMatcher.find()) {
                String desc = descriptionMatcher.group(1);
                if (!desc.equals("null") && !desc.isEmpty()) {
                    repositoryData.add("Description: " + desc);
                }
            }
            if (languageMatcher.find()) {
                String lang = languageMatcher.group(1);
                if (!lang.equals("null") && !lang.isEmpty()) {
                    repositoryData.add("Primary Language: " + lang);
                }
            }
            if (starsMatcher.find()) {
                repositoryData.add("Stars: " + starsMatcher.group(1));
            }
            if (forksMatcher.find()) {
                repositoryData.add("Forks: " + forksMatcher.group(1));
            }
            if (watchersMatcher.find()) {
                repositoryData.add("Watchers: " + watchersMatcher.group(1));
            }
            if (privateMatcher.find()) {
                repositoryData.add("Private: " + privateMatcher.group(1));
            }
            if (sizeMatcher.find()) {
                repositoryData.add("Size: " + sizeMatcher.group(1) + " KB");
            }
            if (defaultBranchMatcher.find()) {
                repositoryData.add("Default Branch: " + defaultBranchMatcher.group(1));
            }
            if (createdMatcher.find()) {
                repositoryData.add("Created: " + createdMatcher.group(1));
            }
            if (updatedMatcher.find()) {
                repositoryData.add("Last Updated: " + updatedMatcher.group(1));
            }
            if (urlMatcher.find()) {
                repositoryData.add("URL: " + urlMatcher.group(1));
            }
            if (cloneUrlMatcher.find()) {
                repositoryData.add("Clone URL: " + cloneUrlMatcher.group(1));
            }
        }
          return repositoryData;
    }
      /**
     * Extract GitHub issue JSON strings from response without parsing
     * @param jsonResponse The JSON response string
     * @return List of raw JSON strings, one for each issue
     */
    public static List<String> parseGitHubIssueData(String jsonResponse) {
        List<String> issueJsonList = new ArrayList<>();
        
        // Check if it's an array response (multiple issues)
        if (jsonResponse.trim().startsWith("[")) {
            // Use the findMatchingBrace helper to extract complete issue objects
            String content = jsonResponse.trim();
            int i = 1; // Skip opening bracket
            while (i < content.length()) {
                // Skip whitespace and commas
                while (i < content.length() && (Character.isWhitespace(content.charAt(i)) || content.charAt(i) == ',')) {
                    i++;
                }
                
                // Find opening brace of issue object
                if (i < content.length() && content.charAt(i) == '{') {
                    int endIndex = findMatchingBrace(content, i);
                    if (endIndex != -1) {
                        String issueJson = content.substring(i, endIndex + 1);
                        issueJsonList.add(issueJson);
                        i = endIndex + 1;
                    } else {
                        break;
                    }
                } else if (content.charAt(i) == ']') {
                    break; // End of array
                } else {
                    i++;
                }
            }
        } else {
            // Single issue object - return as is
            issueJsonList.add(jsonResponse.trim());
        }
          return issueJsonList;
    }
    
    /**
     * Helper method to find the matching closing brace for an opening brace
     * @param content The string content to search in
     * @param startIndex The index of the opening brace
     * @return The index of the matching closing brace, or -1 if not found
     */
    private static int findMatchingBrace(String content, int startIndex) {
        if (startIndex >= content.length() || content.charAt(startIndex) != '{') {
            return -1;
        }
        
        int braceCount = 1;
        int i = startIndex + 1;
        boolean inString = false;
        boolean escaped = false;
        
        while (i < content.length() && braceCount > 0) {
            char c = content.charAt(i);
            
            if (escaped) {
                escaped = false;
            } else if (c == '\\') {
                escaped = true;
            } else if (c == '"' && !escaped) {
                inString = !inString;
            } else if (!inString) {
                if (c == '{') {
                    braceCount++;
                } else if (c == '}') {
                    braceCount--;
                }
            }
            
            i++;
        }
          return braceCount == 0 ? i - 1 : -1;
    }
    
    /**
     * Build the Spotify user agent string from environment variables
     * @return Formatted user agent string for Spotify API
     */
    public static String buildSpotifyUserAgent() {
        return buildUserAgent("JavaSpotifyClient/1.0", "example@email.com");
    }
   
    /**
     * URL encode a string for use in query parameters
     * @param value The string to encode
     * @return URL-encoded string
     */
    public static String urlEncode(String value) {
        if (value == null) {
            return "";
        }
        
        try {
            return java.net.URLEncoder.encode(value, "UTF-8");
        } catch (java.io.UnsupportedEncodingException e) {
            // UTF-8 should always be supported
            return value.replace(" ", "%20")
                       .replace("&", "%26")
                       .replace("=", "%3D")
                       .replace("?", "%3F")
                       .replace("#", "%23");
        }
    }
}
