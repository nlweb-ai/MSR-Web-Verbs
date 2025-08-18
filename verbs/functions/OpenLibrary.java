import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Open Library API wrapper for searching books
 * Extends BaseApiClient for HTTP functionality
 */
public class OpenLibrary extends BaseApiClient {
    private static final String BASE_URL = "https://openlibrary.org";
    private static final String DEFAULT_FIELDS = "*";
    private static final String DEFAULT_SORT = "new";
    private static final String DEFAULT_LANG = "en";
    private static final int DEFAULT_LIMIT = 5;
    private static final int DEFAULT_PAGE = 1;
      public OpenLibrary() {
        super(ApiUtil.buildOpenLibraryUserAgent(), null); // Open Library doesn't require authentication
    }
    
    /**
     * Get the current user agent string for debugging/verification
     * @return The user agent string being used
     */
    public static String getUserAgent() {
        return ApiUtil.buildOpenLibraryUserAgent();
    }
      /**
     * Search for books (matches the REST API endpoint name)
     * Parameters match the JSON fields defined in openlibrary.txt
     * @param q The search query
     * @param fields The fields to get back from solr
     * @param sort Sort results by facets like new, old, random, or key
     * @param lang User's language as a two-letter (ISO 639-1) code
     * @param limit Number of results to return
     * @param page Page number for pagination
     * @return List of book titles
     */
    /**
     * Search for books using the OpenLibrary Search API.
     * @param q The search query
     * @param fields The fields to get back from solr
     * @param sort Sort results by facets like new, old, random, or key
     * @param lang User's language as a two-letter (ISO 639-1) code
     * @param limit Number of results to return
     * @param page Page number for pagination
     * @return List of BookInfo objects
     */
    public List<BookInfo> search(String q, String fields, String sort, String lang, int limit, int page) throws IOException, InterruptedException {
        if (fields==null || fields.isEmpty()) {
            fields = ""; 
        }
        if (sort==null || sort.isEmpty()) {
            sort = ""; 
        }
        if (lang==null || fields.isEmpty()) {
            lang = "en"; 
        }

        String encodedQuery = URLEncoder.encode(q, StandardCharsets.UTF_8);
        String encodedFields = URLEncoder.encode(fields, StandardCharsets.UTF_8);
        String encodedSort = URLEncoder.encode(sort, StandardCharsets.UTF_8);
        String encodedLang = URLEncoder.encode(lang, StandardCharsets.UTF_8);

        String url = String.format("%s/search.json?q=%s&fields=%s&sort=%s&lang=%s&limit=%d&page=%d",
                BASE_URL, encodedQuery, encodedFields, encodedSort, encodedLang, limit, page);

        String responseBody = performGet(url);
        // Parse book titles and wrap in BookInfo
        List<String> titles = parseBookTitles(responseBody);
        List<BookInfo> books = new ArrayList<>();
        for (String title : titles) {
            books.add(new BookInfo(title));
        }
        return books;
    }
      /**
     * Search for authors using OpenLibrary Authors API
     * @param q The search query (author name)
     * @return List of author names
     */
    /**
     * Search for authors using OpenLibrary Authors API.
     * @param q The search query (author name)
     * @return List of AuthorInfo objects
     */
    public List<AuthorInfo> searchAuthors(String q) throws IOException, InterruptedException {
        return searchAuthors(q, DEFAULT_LIMIT);
    }
    
    /**
     * Search for authors using OpenLibrary Authors API with custom limit
     * @param q The search query (author name)
     * @param limit Number of results to return
     * @return List of author names
     */
    /**
     * Search for authors using OpenLibrary Authors API with custom limit.
     * @param q The search query (author name)
     * @param limit Number of results to return
     * @return List of AuthorInfo objects
     */
    public List<AuthorInfo> searchAuthors(String q, int limit) throws IOException, InterruptedException {
        String encodedQuery = URLEncoder.encode(q, StandardCharsets.UTF_8);

        String url = String.format("%s/search/authors.json?q=%s&limit=%d", BASE_URL, encodedQuery, limit);

        String responseBody = performGet(url);
        List<String> names = parseAuthorNames(responseBody);
        List<AuthorInfo> authors = new ArrayList<>();
        for (String name : names) {
            authors.add(new AuthorInfo(name));
        }
        return authors;
    }
    
    /**
     * Get works and information for a subject using OpenLibrary Subjects API
     * @param subject The subject name (e.g., "love", "science", "history")
     * @return List of subject information and sample works
     */
    /**
     * Get works and information for a subject using OpenLibrary Subjects API.
     * @param subject The subject name (e.g., "love", "science", "history")
     * @return List of SubjectInfo objects
     */
    public List<SubjectInfo> getSubject(String subject) throws IOException, InterruptedException {
        return getSubject(subject, false, DEFAULT_LIMIT, 0);
    }
    
    /**
     * Get works and information for a subject with details
     * @param subject The subject name (e.g., "love", "science", "history")
     * @param details Whether to include detailed information (authors, publishers, etc.)
     * @return List of subject information and sample works
     */
    /**
     * Get works and information for a subject with details.
     * @param subject The subject name (e.g., "love", "science", "history")
     * @param details Whether to include detailed information (authors, publishers, etc.)
     * @return List of SubjectInfo objects
     */
    public List<SubjectInfo> getSubject(String subject, boolean details) throws IOException, InterruptedException {
        return getSubject(subject, details, DEFAULT_LIMIT, 0);
    }
    
    /**
     * Get works and information for a subject with full customization
     * @param subject The subject name (e.g., "love", "science", "history")
     * @param details Whether to include detailed information (authors, publishers, etc.)
     * @param limit Number of works to include in the response
     * @param offset Starting offset for pagination
     * @return List of subject information and sample works
     */
    /**
     * Get works and information for a subject with full customization.
     * @param subject The subject name (e.g., "love", "science", "history")
     * @param details Whether to include detailed information (authors, publishers, etc.)
     * @param limit Number of works to include in the response
     * @param offset Starting offset for pagination
     * @return List of SubjectInfo objects
     */
    public List<SubjectInfo> getSubject(String subject, boolean details, int limit, int offset) throws IOException, InterruptedException {
        String encodedSubject = URLEncoder.encode(subject, StandardCharsets.UTF_8);

        StringBuilder url = new StringBuilder();
        url.append(String.format("%s/subjects/%s.json", BASE_URL, encodedSubject));

        // Add query parameters
        List<String> params = new ArrayList<>();
        if (details) {
            params.add("details=true");
        }
        if (limit != DEFAULT_LIMIT) {
            params.add("limit=" + limit);
        }
        if (offset > 0) {
            params.add("offset=" + offset);
        }

        if (!params.isEmpty()) {
            url.append("?").append(String.join("&", params));
        }

        String responseBody = performGet(url.toString());
        List<String> subjectData = parseSubjectData(responseBody);
        List<SubjectInfo> infoList = new ArrayList<>();
        for (String info : subjectData) {
            infoList.add(new SubjectInfo(info));
        }
        return infoList;
    }

    
    /**
     * Simple JSON parsing to extract book titles using regex
     * In a real application, you'd use a proper JSON library like Jackson or Gson
     * @param jsonResponse The JSON response string
     * @return List of book titles found in the response
     */
    private static List<String> parseBookTitles(String jsonResponse) {
        List<String> titles = new ArrayList<>();
        
        // Simple regex to find titles in the JSON response
        Pattern titlePattern = Pattern.compile("\"title\"\\s*:\\s*\"([^\"]+)\"");
        Matcher matcher = titlePattern.matcher(jsonResponse);
        
        while (matcher.find()) {
            titles.add(matcher.group(1));
        }
        
        return titles;
    }
    
    /**
     * Simple JSON parsing to extract author names using regex
     * In a real application, you'd use a proper JSON library like Jackson or Gson
     * @param jsonResponse The JSON response string
     * @return List of author names found in the response
     */
    private static List<String> parseAuthorNames(String jsonResponse) {
        List<String> authorNames = new ArrayList<>();
        
        // Simple regex to find author names in the JSON response
        Pattern namePattern = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]+)\"");
        Matcher matcher = namePattern.matcher(jsonResponse);
        
        while (matcher.find()) {
            authorNames.add(matcher.group(1));
        }
        
        return authorNames;
    }
    
    /**
     * Simple JSON parsing to extract subject data using regex
     * In a real application, you'd use a proper JSON library like Jackson or Gson
     * @param jsonResponse The JSON response string
     * @return List of subject information (name, work count, works titles, etc.)
     */
    private static List<String> parseSubjectData(String jsonResponse) {
        List<String> subjectData = new ArrayList<>();
        
        // Extract key subject fields
        Pattern namePattern = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]+)\"");
        Pattern workCountPattern = Pattern.compile("\"work_count\"\\s*:\\s*(\\d+)");
        Pattern ebookCountPattern = Pattern.compile("\"ebook_count\"\\s*:\\s*(\\d+)");
        Pattern keyPattern = Pattern.compile("\"key\"\\s*:\\s*\"([^\"]+)\"");
        
        Matcher nameMatcher = namePattern.matcher(jsonResponse);
        Matcher workCountMatcher = workCountPattern.matcher(jsonResponse);
        Matcher ebookCountMatcher = ebookCountPattern.matcher(jsonResponse);
        Matcher keyMatcher = keyPattern.matcher(jsonResponse);
        
        if (nameMatcher.find()) {
            subjectData.add("Subject: " + nameMatcher.group(1));
        }
        if (keyMatcher.find()) {
            subjectData.add("Key: " + keyMatcher.group(1));
        }
        if (workCountMatcher.find()) {
            subjectData.add("Total Works: " + workCountMatcher.group(1));
        }
        if (ebookCountMatcher.find()) {
            subjectData.add("E-books Available: " + ebookCountMatcher.group(1));
        }
        
        // Extract first few work titles from the works array
        Pattern worksPattern = Pattern.compile("\"works\"\\s*:\\s*\\[([^\\]]+)\\]");
        Matcher worksMatcher = worksPattern.matcher(jsonResponse);
        
        if (worksMatcher.find()) {
            String worksSection = worksMatcher.group(1);
            Pattern titlePattern = Pattern.compile("\"title\"\\s*:\\s*\"([^\"]+)\"");
            Matcher titleMatcher = titlePattern.matcher(worksSection);
            
            subjectData.add("Sample Works:");
            int workCount = 0;
            while (titleMatcher.find() && workCount < 5) {
                subjectData.add("  " + (workCount + 1) + ". " + titleMatcher.group(1));
                workCount++;
            }
        }
        
        return subjectData;
    }
    
// --- Explicit return type classes ---

    /**
     * Represents a book result from OpenLibrary search.
     */
    public static class BookInfo {
        /** Title of the book. */
        public final String title;
        public BookInfo(String title) {
            this.title = title;
        }
        @Override
        public String toString() { return title; }
    }

    /**
     * Represents an author result from OpenLibrary search.
     */
    public static class AuthorInfo {
        /** Name of the author. */
        public final String name;
        public AuthorInfo(String name) {
            this.name = name;
        }
        @Override
        public String toString() { return name; }
    }

    /**
     * Represents a subject result from OpenLibrary subject API.
     */
    public static class SubjectInfo {
        /** Info string for the subject (could be name, key, work, etc.). */
        public final String info;
        public SubjectInfo(String info) {
            this.info = info;
        }
        @Override
        public String toString() { return info; }
    }
}
