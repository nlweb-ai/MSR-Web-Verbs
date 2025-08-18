import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Wikimedia API wrapper for searching Wikipedia articles
 * Extends BaseApiClient for HTTP functionality
 */
public class Wikimedia extends BaseApiClient {

    /**
     * Represents Wikipedia search results containing a list of article titles
     */
    public static class SearchResult {
        /** List of article titles found in the search */
        public List<String> titles;

        public SearchResult() {
            this.titles = new ArrayList<>();
        }

        public SearchResult(List<String> titles) {
            this.titles = titles != null ? new ArrayList<>(titles) : new ArrayList<>();
        }
    }

    /**
     * Represents detailed information about a Wikipedia page
     */
    public static class PageInfo {
        /** Unique identifier of the page */
        public long id;
        /** Title of the page */
        public String title;
        /** Page key/path identifier */
        public String key;
        /** Content model (e.g., "wikitext", "javascript", "css") */
        public String contentModel;
        /** License URL for the page content */
        public String licenseUrl;
        /** License title/name */
        public String licenseTitle;
        /** HTML URL to view the page */
        public String htmlUrl;
        /** Last modification date of the page */
        public LocalDateTime lastModified;

        public PageInfo() {
            this.title = "";
            this.key = "";
            this.contentModel = "";
            this.licenseUrl = "";
            this.licenseTitle = "";
            this.htmlUrl = "";
        }
    }

    /**
     * Represents HTML content analysis and statistics of a Wikipedia page
     */
    public static class HtmlContentInfo {
        /** Title extracted from HTML */
        public String htmlTitle;
        /** Number of H1 headings */
        public int h1Count;
        /** Number of H2 headings */
        public int h2Count;
        /** Number of H3 headings */
        public int h3Count;
        /** Number of links in the page */
        public int linkCount;
        /** Number of images in the page */
        public int imageCount;
        /** Number of paragraphs */
        public int paragraphCount;
        /** Total character count of the HTML content */
        public int contentLength;
        /** Sample H1 headings (up to 3) */
        public List<String> sampleH1Headings;
        /** Sample H2 headings (up to 5) */
        public List<String> sampleH2Headings;

        public HtmlContentInfo() {
            this.htmlTitle = "";
            this.sampleH1Headings = new ArrayList<>();
            this.sampleH2Headings = new ArrayList<>();
        }
    }

    /**
     * Represents a simulated page creation or edit request with all the details
     */
    public static class PageOperationRequest {
        /** Type of operation: "CREATE" or "EDIT" */
        public String operationType;
        /** Target URL for the request */
        public String url;
        /** HTTP method (POST for create, PUT for edit) */
        public String method;
        /** Page title */
        public String title;
        /** Page content/source */
        public String source;
        /** Edit comment explaining the operation */
        public String comment;
        /** Content model (e.g., "wikitext") */
        public String contentModel;
        /** Language code (e.g., "en") */
        public String languageCode;
        /** Latest revision ID (for edit operations only) */
        public Long latestRevisionId;
        /** Whether this is a simulation (always true for safety) */
        public boolean isSimulation;

        public PageOperationRequest() {
            this.operationType = "";
            this.url = "";
            this.method = "";
            this.title = "";
            this.source = "";
            this.comment = "";
            this.contentModel = "";
            this.languageCode = "";
            this.isSimulation = true;
        }
    }

    /**
     * Helper method to parse page data from API response into PageInfo object
     * @param jsonResponse The JSON response from the API
     * @return PageInfo object with parsed data
     */
    private PageInfo parsePageInfo(String jsonResponse) {
        PageInfo pageInfo = new PageInfo();
        List<String> rawData = parsePageData(jsonResponse);
        
        for (String item : rawData) {
            if (item.startsWith("ID: ")) {
                try {
                    pageInfo.id = Long.parseLong(item.substring(4));
                } catch (NumberFormatException e) {
                    pageInfo.id = 0;
                }
            } else if (item.startsWith("Title: ")) {
                pageInfo.title = item.substring(7);
            } else if (item.startsWith("Key: ")) {
                pageInfo.key = item.substring(5);
            } else if (item.startsWith("Content Model: ")) {
                pageInfo.contentModel = item.substring(15);
            } else if (item.startsWith("License URL: ")) {
                pageInfo.licenseUrl = item.substring(13);
            } else if (item.startsWith("License: ")) {
                pageInfo.licenseTitle = item.substring(9);
            } else if (item.startsWith("HTML URL: ")) {
                pageInfo.htmlUrl = item.substring(10);
            } else if (item.startsWith("Last Modified: ")) {
                try {
                    String dateStr = item.substring(15);
                    // Try to parse ISO 8601 datetime format typically used by Wikipedia API
                    pageInfo.lastModified = LocalDateTime.parse(dateStr.replace("Z", ""), 
                        DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss"));
                } catch (DateTimeParseException e) {
                    // If parsing fails, leave as null
                    pageInfo.lastModified = null;
                }
            }
        }
        
        return pageInfo;
    }

    /**
     * Helper method to parse HTML content into HtmlContentInfo object
     * @param htmlContent The HTML content response
     * @return HtmlContentInfo object with parsed statistics and sample content
     */
    private HtmlContentInfo parseHtmlContentInfo(String htmlContent) {
        HtmlContentInfo htmlInfo = new HtmlContentInfo();
        List<String> rawData = parseHtmlContent(htmlContent);
        
        for (String item : rawData) {
            if (item.startsWith("HTML Title: ")) {
                htmlInfo.htmlTitle = item.substring(12);
            } else if (item.contains("H1 Headings: ")) {
                try {
                    htmlInfo.h1Count = Integer.parseInt(item.substring(item.indexOf(": ") + 2));
                } catch (NumberFormatException e) {
                    htmlInfo.h1Count = 0;
                }
            } else if (item.contains("H2 Headings: ")) {
                try {
                    htmlInfo.h2Count = Integer.parseInt(item.substring(item.indexOf(": ") + 2));
                } catch (NumberFormatException e) {
                    htmlInfo.h2Count = 0;
                }
            } else if (item.contains("H3 Headings: ")) {
                try {
                    htmlInfo.h3Count = Integer.parseInt(item.substring(item.indexOf(": ") + 2));
                } catch (NumberFormatException e) {
                    htmlInfo.h3Count = 0;
                }
            } else if (item.contains("Links: ")) {
                try {
                    htmlInfo.linkCount = Integer.parseInt(item.substring(item.indexOf(": ") + 2));
                } catch (NumberFormatException e) {
                    htmlInfo.linkCount = 0;
                }
            } else if (item.contains("Images: ")) {
                try {
                    htmlInfo.imageCount = Integer.parseInt(item.substring(item.indexOf(": ") + 2));
                } catch (NumberFormatException e) {
                    htmlInfo.imageCount = 0;
                }
            } else if (item.contains("Paragraphs: ")) {
                try {
                    htmlInfo.paragraphCount = Integer.parseInt(item.substring(item.indexOf(": ") + 2));
                } catch (NumberFormatException e) {
                    htmlInfo.paragraphCount = 0;
                }
            } else if (item.startsWith("Content Length: ")) {
                try {
                    String lengthStr = item.substring(16);
                    if (lengthStr.contains(" characters")) {
                        lengthStr = lengthStr.substring(0, lengthStr.indexOf(" characters"));
                    }
                    htmlInfo.contentLength = Integer.parseInt(lengthStr);
                } catch (NumberFormatException e) {
                    htmlInfo.contentLength = 0;
                }
            } else if (item.startsWith("H1: ")) {
                htmlInfo.sampleH1Headings.add(item.substring(4));
            } else if (item.startsWith("H2: ")) {
                htmlInfo.sampleH2Headings.add(item.substring(4));
            }
        }
        
        return htmlInfo;
    }

    /**
     * Helper method to parse page operation request data
     * @param rawRequestInfo List of strings from ApiUtil formatting
     * @param operationType "CREATE" or "EDIT"
     * @return PageOperationRequest object with parsed data
     */
    private PageOperationRequest parsePageOperationRequest(List<String> rawRequestInfo, String operationType) {
        PageOperationRequest request = new PageOperationRequest();
        request.operationType = operationType;
        
        for (String line : rawRequestInfo) {
            if (line.startsWith("URL: ")) {
                request.url = line.substring(5);
            } else if (line.startsWith("Method: ")) {
                request.method = line.substring(8);
            } else if (line.contains("\"title\": \"")) {
                int start = line.indexOf("\"title\": \"") + 10;
                int end = line.indexOf("\"", start);
                if (end > start) {
                    request.title = line.substring(start, end);
                }
            } else if (line.contains("\"comment\": \"")) {
                int start = line.indexOf("\"comment\": \"") + 12;
                int end = line.indexOf("\"", start);
                if (end > start) {
                    request.comment = line.substring(start, end);
                }
            } else if (line.contains("\"content_model\": \"")) {
                int start = line.indexOf("\"content_model\": \"") + 18;
                int end = line.indexOf("\"", start);
                if (end > start) {
                    request.contentModel = line.substring(start, end);
                }
            } else if (line.contains("\"source\": \"")) {
                int start = line.indexOf("\"source\": \"") + 11;
                int end = line.lastIndexOf("\"");
                if (end > start) {
                    String source = line.substring(start, end);
                    // Remove "..." if content was truncated
                    if (source.endsWith("...")) {
                        source = source.substring(0, source.length() - 3);
                    }
                    request.source = source;
                }
            } else if (line.contains("\"id\": ")) {
                try {
                    int start = line.indexOf("\"id\": ") + 6;
                    String idStr = line.substring(start).trim();
                    if (idStr.endsWith(",")) {
                        idStr = idStr.substring(0, idStr.length() - 1);
                    }
                    request.latestRevisionId = Long.parseLong(idStr);
                } catch (NumberFormatException e) {
                    request.latestRevisionId = null;
                }
            }
        }
        
        // Extract language code from URL
        if (request.url.contains("/wikipedia/")) {
            int start = request.url.indexOf("/wikipedia/") + 11;
            int end = request.url.indexOf("/", start);
            if (end > start) {
                request.languageCode = request.url.substring(start, end);
            }
        }
        
        return request;
    }
    private static final String BASE_URL = "https://api.wikimedia.org/core/v1/wikipedia/";
    private static final String DEFAULT_LANGUAGE = "en";
    private static final int DEFAULT_LIMIT = 5;

    public Wikimedia() {
        super(ApiUtil.buildWikimediaUserAgent(), loadAccessToken());
    }
    
    /**
     * Search for Wikipedia articles using the REST API search endpoint.
     * This method performs a full-text search across Wikipedia articles and returns
     * matching article titles. The search is performed on article content, not just titles.
     * 
     * @param query The search query string to look for in Wikipedia articles
     * @param languageCode Language code (e.g., "en" for English) to specify which Wikipedia to search
     * @param limit Maximum number of results to return (typically 1-50)
     * @return SearchResult object containing a list of matching article titles
     * @throws IOException if there's a network or I/O error during the request
     * @throws InterruptedException if the request is interrupted
     */
    public SearchResult search(String query, String languageCode, int limit) throws IOException, InterruptedException {
        String encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8);
        String url = String.format("%s%s/search/page?q=%s&limit=%d", 
                BASE_URL, languageCode, encodedQuery, limit);
        
        String responseBody = performGet(url);
        List<String> titles = parseArticleTitles(responseBody);
        return new SearchResult(titles);
    }

    /**
     * Search for Wikipedia article titles that begin with the provided search terms (autocomplete).
     * Uses the search/title endpoint for title-based autocomplete functionality.
     * This is useful for implementing search suggestions or autocomplete features.
     * 
     * @param query The search query - returns titles that begin with this text
     * @param languageCode Language code (e.g., "en" for English), defaults to "en" if null or empty
     * @param limit Number of results to return (1-100), defaults to 5 if 0 or negative
     * @return SearchResult object containing article titles that begin with the search terms
     * @throws IOException if there's a network or I/O error during the request
     * @throws InterruptedException if the request is interrupted
     */
    public SearchResult searchTitles(String query, String languageCode, int limit) throws IOException, InterruptedException {
        // Use defaults if not provided
        if (languageCode == null || languageCode.trim().isEmpty()) {
            languageCode = DEFAULT_LANGUAGE;
        }
        if (limit <= 0) {
            limit = DEFAULT_LIMIT;
        }
        
        String encodedQuery = URLEncoder.encode(query, StandardCharsets.UTF_8);
        String url = String.format("%s%s/search/title?q=%s&limit=%d", 
                BASE_URL, languageCode, encodedQuery, limit);
        
        String responseBody = performGet(url);
        List<String> titles = parseArticleTitles(responseBody);
        return new SearchResult(titles);
    }

    /**
     * Search for Wikipedia article titles that begin with the provided search terms using default settings.
     * This is a convenience method that uses the default language (English) and limit (5 results).
     * 
     * @param query The search query - returns titles that begin with this text
     * @return SearchResult object containing article titles that begin with the search terms
     * @throws IOException if there's a network or I/O error during the request
     * @throws InterruptedException if the request is interrupted
     */
    public SearchResult searchTitles(String query) throws IOException, InterruptedException {
        return searchTitles(query, DEFAULT_LANGUAGE, DEFAULT_LIMIT);
    }

    /**
     * Get comprehensive information about a specific Wikipedia page using the page/{title}/bare endpoint.
     * This method retrieves detailed metadata about a Wikipedia page including its ID, title, content model,
     * license information, and last modification timestamp.
     * 
     * @param title The page title to get information for (will be URL encoded automatically)
     * @param languageCode Language code (e.g., "en" for English), defaults to "en" if null or empty
     * @return PageInfo object containing comprehensive page metadata
     * @throws IOException if there's a network or I/O error during the request
     * @throws InterruptedException if the request is interrupted
     */
    public PageInfo getPage(String title, String languageCode) throws IOException, InterruptedException {
        // Use default if not provided
        if (languageCode == null || languageCode.trim().isEmpty()) {
            languageCode = DEFAULT_LANGUAGE;
        }
        
        String encodedTitle = URLEncoder.encode(title, StandardCharsets.UTF_8);
        String url = String.format("%s%s/page/%s/bare", 
                BASE_URL, languageCode, encodedTitle);
        
        String responseBody = performGet(url);
        return parsePageInfo(responseBody);
    }

    /**
     * Get information about a specific Wikipedia page using the default language (English).
     * This is a convenience method that retrieves page metadata using English Wikipedia.
     * 
     * @param title The page title to get information for
     * @return PageInfo object containing comprehensive page metadata
     * @throws IOException if there's a network or I/O error during the request
     * @throws InterruptedException if the request is interrupted
     */
    public PageInfo getPage(String title) throws IOException, InterruptedException {
        return getPage(title, DEFAULT_LANGUAGE);
    }

    /**
     * Get comprehensive HTML content analysis of a specific Wikipedia page using the page/{title}/html endpoint.
     * This method retrieves and analyzes the HTML content of a Wikipedia page, providing statistics about
     * headings, links, images, and other structural elements, along with sample content.
     * 
     * @param title The page title to get HTML content analysis for (will be URL encoded automatically)
     * @param languageCode Language code (e.g., "en" for English), defaults to "en" if null or empty
     * @return HtmlContentInfo object containing content analysis and statistics
     * @throws IOException if there's a network or I/O error during the request
     * @throws InterruptedException if the request is interrupted
     */
    public HtmlContentInfo getHtml(String title, String languageCode) throws IOException, InterruptedException {
        // Use default if not provided
        if (languageCode == null || languageCode.trim().isEmpty()) {
            languageCode = DEFAULT_LANGUAGE;
        }
        
        String encodedTitle = URLEncoder.encode(title, StandardCharsets.UTF_8);
        String url = String.format("%s%s/page/%s/html", 
                BASE_URL, languageCode, encodedTitle);
        
        String responseBody = performGet(url);
        return parseHtmlContentInfo(responseBody);
    }
    
    /**
     * Get HTML content analysis of a specific Wikipedia page using the default language (English).
     * This is a convenience method that analyzes page HTML content using English Wikipedia.
     * 
     * @param title The page title to get HTML content analysis for
     * @return HtmlContentInfo object containing content analysis and statistics
     * @throws IOException if there's a network or I/O error during the request
     * @throws InterruptedException if the request is interrupted
     */
    public HtmlContentInfo getHtml(String title) throws IOException, InterruptedException {
        return getHtml(title, DEFAULT_LANGUAGE);
    }

    /**
     * Simulate creating a new Wikipedia page without actually performing the operation.
     * This method formats and returns the details of what would be sent to the Wikipedia API
     * for page creation, including the URL, HTTP method, and request body structure.
     * No actual page creation occurs to avoid unintended modifications to Wikipedia.
     * 
     * @param title The page title to create (e.g., "User:Username/Sandbox")
     * @param source The page content/source in wikitext format
     * @param comment The edit comment explaining the page creation purpose
     * @param contentModel The content model (e.g., "wikitext", "javascript", "css"), defaults to "wikitext" if null
     * @param languageCode Language code (e.g., "en" for English), defaults to "en" if null or empty
     * @return PageOperationRequest object containing details of the simulated create operation
     */
    public PageOperationRequest createPage(String title, String source, String comment, String contentModel, String languageCode) {
        // Use defaults if not provided
        if (languageCode == null || languageCode.trim().isEmpty()) {
            languageCode = DEFAULT_LANGUAGE;
        }
        if (contentModel == null || contentModel.trim().isEmpty()) {
            contentModel = "wikitext";
        }
        
        // Get formatted request information from ApiUtil
        List<String> rawRequestInfo = formatCreatePageRequest(title, source, comment, contentModel, languageCode);
        return parsePageOperationRequest(rawRequestInfo, "CREATE");
    }
    
    /**
     * Simulate creating a new Wikipedia page using default content model and language.
     * This convenience method uses "wikitext" as the content model and English as the language.
     * No actual page creation occurs to avoid unintended modifications to Wikipedia.
     * 
     * @param title The page title to create
     * @param source The page content/source in wikitext format
     * @param comment The edit comment explaining the page creation purpose
     * @return PageOperationRequest object containing details of the simulated create operation
     */
    public PageOperationRequest createPage(String title, String source, String comment) {
        return createPage(title, source, comment, "wikitext", DEFAULT_LANGUAGE);
    }

    /**
     * Simulate editing an existing Wikipedia page without actually performing the operation.
     * This method formats and returns the details of what would be sent to the Wikipedia API
     * for page editing, including the URL, HTTP method, request body, and revision conflict detection.
     * No actual page editing occurs to avoid unintended modifications to Wikipedia.
     * 
     * @param title The page title to edit
     * @param source The new page content/source in wikitext format
     * @param comment The edit comment explaining the changes made
     * @param contentModel The content model (e.g., "wikitext", "javascript", "css"), defaults to "wikitext" if null
     * @param latestRevisionId The latest revision ID for conflict detection (prevents edit conflicts)
     * @param languageCode Language code (e.g., "en" for English), defaults to "en" if null or empty
     * @return PageOperationRequest object containing details of the simulated edit operation
     */
    public PageOperationRequest editPage(String title, String source, String comment, String contentModel, long latestRevisionId, String languageCode) {
        // Use defaults if not provided
        if (languageCode == null || languageCode.trim().isEmpty()) {
            languageCode = DEFAULT_LANGUAGE;
        }
        if (contentModel == null || contentModel.trim().isEmpty()) {
            contentModel = "wikitext";
        }
        
        // Get formatted request information from ApiUtil
        List<String> rawRequestInfo = formatEditPageRequest(title, source, comment, contentModel, latestRevisionId, languageCode);
        return parsePageOperationRequest(rawRequestInfo, "EDIT");
    }

    /**
     * Simulate editing an existing Wikipedia page using default content model and language.
     * This convenience method uses "wikitext" as the content model and English as the language.
     * No actual page editing occurs to avoid unintended modifications to Wikipedia.
     * 
     * @param title The page title to edit
     * @param source The new page content/source in wikitext format
     * @param comment The edit comment explaining the changes made
     * @param latestRevisionId The latest revision ID for conflict detection
     * @return PageOperationRequest object containing details of the simulated edit operation
     */
    public PageOperationRequest editPage(String title, String source, String comment, long latestRevisionId) {
        return editPage(title, source, comment, "wikitext", latestRevisionId, DEFAULT_LANGUAGE);
    }

    /**
     * Load the Wikimedia access token from the .env file
     * @return The access token, or null if not found
     */
    private static String loadAccessToken() {
        return ApiUtil.loadEnvValue("WIKIMEDIA_ACCESS_TOKEN");
    }
    
    /**
     * Get the current user agent string for debugging/verification
     * @return The user agent string being used
     */
    public static String getUserAgent() {
        return ApiUtil.buildWikimediaUserAgent();
    }

    

    /**
     * Simple JSON parsing to extract page information using regex
     * In a real application, you'd use a proper JSON library like Jackson or Gson
     * @param jsonResponse The JSON response string
     * @return List of page information (id, title, content_model, license info, html_url, timestamp)
     */    
    private static List<String> parsePageData(String jsonResponse) {
        // Return empty list if jsonResponse is null
        if (jsonResponse == null) {
            return new ArrayList<>();
        }
        
        List<String> pageData = new ArrayList<>();
        
        // Extract key page fields
        Pattern idPattern = Pattern.compile("\"id\"\\s*:\\s*(\\d+)");
        Pattern titlePattern = Pattern.compile("\"title\"\\s*:\\s*\"([^\"]+)\"");
        Pattern keyPattern = Pattern.compile("\"key\"\\s*:\\s*\"([^\"]+)\"");
        Pattern contentModelPattern = Pattern.compile("\"content_model\"\\s*:\\s*\"([^\"]+)\"");
        Pattern licenseUrlPattern = Pattern.compile("\"license\"\\s*:\\s*\\{[^}]*\"url\"\\s*:\\s*\"([^\"]+)\"");
        Pattern licenseTitlePattern = Pattern.compile("\"license\"\\s*:\\s*\\{[^}]*\"title\"\\s*:\\s*\"([^\"]+)\"");
        Pattern htmlUrlPattern = Pattern.compile("\"html_url\"\\s*:\\s*\"([^\"]+)\"");
        Pattern timestampPattern = Pattern.compile("\"timestamp\"\\s*:\\s*\"([^\"]+)\"");
        
        Matcher idMatcher = idPattern.matcher(jsonResponse);
        Matcher titleMatcher = titlePattern.matcher(jsonResponse);
        Matcher keyMatcher = keyPattern.matcher(jsonResponse);
        Matcher contentModelMatcher = contentModelPattern.matcher(jsonResponse);
        Matcher licenseUrlMatcher = licenseUrlPattern.matcher(jsonResponse);
        Matcher licenseTitleMatcher = licenseTitlePattern.matcher(jsonResponse);
        Matcher htmlUrlMatcher = htmlUrlPattern.matcher(jsonResponse);
        Matcher timestampMatcher = timestampPattern.matcher(jsonResponse);
        
        if (idMatcher.find()) {
            pageData.add("ID: " + idMatcher.group(1));
        }
        if (titleMatcher.find()) {
            pageData.add("Title: " + titleMatcher.group(1));
        }
        if (keyMatcher.find()) {
            pageData.add("Key: " + keyMatcher.group(1));
        }
        if (contentModelMatcher.find()) {
            pageData.add("Content Model: " + contentModelMatcher.group(1));
        }
        if (licenseUrlMatcher.find()) {
            pageData.add("License URL: " + licenseUrlMatcher.group(1));
        }
        if (licenseTitleMatcher.find()) {
            pageData.add("License: " + licenseTitleMatcher.group(1));
        }
        if (htmlUrlMatcher.find()) {
            pageData.add("HTML URL: " + htmlUrlMatcher.group(1));
        }
        if (timestampMatcher.find()) {
            pageData.add("Last Modified: " + timestampMatcher.group(1));
        }
        
        return pageData;
    }
   
    /**
     * Simple HTML parsing to extract basic page information
     * In a real application, you'd use a proper HTML parser like Jsoup
     * @param htmlContent The HTML content string
     * @return List of basic HTML information (title, headings count, links count, etc.)
     */
    private static List<String> parseHtmlContent(String htmlContent) {
        List<String> htmlData = new ArrayList<>();
        
        // Extract title from HTML
        Pattern titlePattern = Pattern.compile("<title>([^<]+)</title>", Pattern.CASE_INSENSITIVE);
        Matcher titleMatcher = titlePattern.matcher(htmlContent);
        if (titleMatcher.find()) {
            htmlData.add("HTML Title: " + titleMatcher.group(1).trim());
        }
        
        // Count various HTML elements
        int h1Count = ApiUtil.countMatches(htmlContent, "<h1[^>]*>", Pattern.CASE_INSENSITIVE);
        int h2Count = ApiUtil.countMatches(htmlContent, "<h2[^>]*>", Pattern.CASE_INSENSITIVE);
        int h3Count = ApiUtil.countMatches(htmlContent, "<h3[^>]*>", Pattern.CASE_INSENSITIVE);
        int linkCount = ApiUtil.countMatches(htmlContent, "<a[^>]*href", Pattern.CASE_INSENSITIVE);
        int imageCount = ApiUtil.countMatches(htmlContent, "<img[^>]*src", Pattern.CASE_INSENSITIVE);
        int paragraphCount = ApiUtil.countMatches(htmlContent, "<p[^>]*>", Pattern.CASE_INSENSITIVE);
        
        htmlData.add("Content Statistics:");
        htmlData.add("  H1 Headings: " + h1Count);
        htmlData.add("  H2 Headings: " + h2Count);
        htmlData.add("  H3 Headings: " + h3Count);
        htmlData.add("  Links: " + linkCount);
        htmlData.add("  Images: " + imageCount);
        htmlData.add("  Paragraphs: " + paragraphCount);
        
        // Extract first few headings for preview
        Pattern h1Pattern = Pattern.compile("<h1[^>]*>([^<]+)</h1>", Pattern.CASE_INSENSITIVE);
        Pattern h2Pattern = Pattern.compile("<h2[^>]*>([^<]+)</h2>", Pattern.CASE_INSENSITIVE);
        
        Matcher h1Matcher = h1Pattern.matcher(htmlContent);
        int h1Found = 0;
        while (h1Matcher.find() && h1Found < 3) {
            htmlData.add("H1: " + h1Matcher.group(1).trim());
            h1Found++;
        }
        
        Matcher h2Matcher = h2Pattern.matcher(htmlContent);
        int h2Found = 0;
        while (h2Matcher.find() && h2Found < 5) {
            htmlData.add("H2: " + h2Matcher.group(1).trim());
            h2Found++;
        }
        
        // Add content length information
        htmlData.add("Content Length: " + htmlContent.length() + " characters");
        
        return htmlData;
    }
      /**
     * Format a create page request for display (without actually sending it)
     * @param title The page title
     * @param source The page content/source
     * @param comment The edit comment
     * @param contentModel The content model (e.g., "wikitext", "javascript", "css")
     * @param languageCode The language code
     * @return List of formatted request information
     */
    private static List<String> formatCreatePageRequest(String title, String source, String comment, String contentModel, String languageCode) {
        List<String> requestInfo = new ArrayList<>();
        
        requestInfo.add("=== CREATE PAGE REQUEST (SIMULATION) ===");
        requestInfo.add("URL: https://api.wikimedia.org/core/v1/wikipedia/" + languageCode + "/page");
        requestInfo.add("Method: POST");
        requestInfo.add("Content-Type: application/json");
        requestInfo.add("");
        requestInfo.add("Request Body:");
        requestInfo.add("{");
        requestInfo.add("  \"title\": \"" + title + "\",");
        requestInfo.add("  \"source\": \"" + (source.length() > 100 ? source.substring(0, 100) + "..." : source) + "\",");
        requestInfo.add("  \"comment\": \"" + comment + "\",");
        requestInfo.add("  \"content_model\": \"" + contentModel + "\"");
        requestInfo.add("}");
        requestInfo.add("");
        requestInfo.add("NOTE: This is a simulation - no actual page creation request was sent to avoid real-world impact.");
        
        return requestInfo;
    }
    
    /**
     * Format an edit page request for display (without actually sending it)
     * @param title The page title to edit
     * @param source The new page content/source
     * @param comment The edit comment
     * @param contentModel The content model (e.g., "wikitext", "javascript", "css")
     * @param latestRevisionId The latest revision ID for conflict detection
     * @param languageCode The language code
     * @return List of formatted request information
     */
    private static List<String> formatEditPageRequest(String title, String source, String comment, String contentModel, long latestRevisionId, String languageCode) {
        List<String> requestInfo = new ArrayList<>();
        
        requestInfo.add("=== EDIT PAGE REQUEST (SIMULATION) ===");
        requestInfo.add("URL: https://api.wikimedia.org/core/v1/wikipedia/" + languageCode + "/page/" + title);
        requestInfo.add("Method: PUT");
        requestInfo.add("Content-Type: application/json");
        requestInfo.add("");
        requestInfo.add("Request Body:");
        requestInfo.add("{");
        requestInfo.add("  \"title\": \"" + title + "\",");
        requestInfo.add("  \"source\": \"" + (source.length() > 100 ? source.substring(0, 100) + "..." : source) + "\",");
        requestInfo.add("  \"comment\": \"" + comment + "\",");
        requestInfo.add("  \"content_model\": \"" + contentModel + "\",");
        requestInfo.add("  \"latest\": {");
        requestInfo.add("    \"id\": " + latestRevisionId);
        requestInfo.add("  }");
        requestInfo.add("}");
        requestInfo.add("");
        requestInfo.add("NOTE: This is a simulation - no actual page edit request was sent to avoid real-world impact.");
        
        return requestInfo;
    } 

    /**
     * Simple JSON parsing to extract article titles using regex
     * In a real application, you'd use a proper JSON library like Jackson or Gson
     * @param jsonResponse The JSON response string
     * @return List of article titles found in the response
     */
    private static List<String> parseArticleTitles(String jsonResponse) {
        List<String> titles = new ArrayList<>();
        
        // Simple regex to find titles in the JSON response
        Pattern titlePattern = Pattern.compile("\"title\"\\s*:\\s*\"([^\"]+)\"");
        Matcher matcher = titlePattern.matcher(jsonResponse);
        
        while (matcher.find()) {
            titles.add(matcher.group(1));
        }
        
        return titles;
    }
}
