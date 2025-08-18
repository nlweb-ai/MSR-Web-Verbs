import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;

/**
 * NewsAPI wrapper for searching news articles.
 * Extends BaseApiClient for HTTP functionality.
 * Returns explicit result types for news data.
 */
public class News extends BaseApiClient {
    private static final String BASE_URL = "https://newsapi.org";
    private static final String DEFAULT_LANGUAGE = "en";
    private static final String DEFAULT_SORT_BY = "publishedAt";
    private static final int DEFAULT_PAGE_SIZE = 10;
    private static final int DEFAULT_PAGE = 1;

    /**
     * Represents a news article from NewsAPI.
     */
    public static class NewsArticle {
        /** Title of the article. */
        public String title;
        /** Description or summary of the article. */
        public String description;
        /** URL to the full article. */
        public String url;
        /** Date the article was published. */
        public LocalDate publishedAt;
        /** Source name of the article. */
        public String source;
    }

    /**
     * Represents the response from NewsAPI, including metadata and articles.
     */
    public static class NewsResponse {
        /** API status (e.g., "ok"). */
        public String status;
        /** Total number of results available. */
        public int totalResults;
        /** List of news articles. */
        public List<NewsArticle> articles = new ArrayList<>();
    }

    public News() {
        super(ApiUtil.buildNewsUserAgent(), null); // NewsAPI uses API key, not Bearer token
    }

    /**
     * Get the current user agent string for debugging/verification
     * @return The user agent string being used
     */
    public static String getUserAgent() {
        return ApiUtil.buildNewsUserAgent();
    }

    /**
     * Search for everything - articles from news sources and blogs.
     * @param q Keywords or phrases to search for
     * @return NewsResponse containing articles and metadata
     */
    public NewsResponse searchEverything(String q) throws IOException, InterruptedException {
        return searchEverything(q, null, null, null, null, null, null, DEFAULT_LANGUAGE, DEFAULT_SORT_BY, DEFAULT_PAGE_SIZE, DEFAULT_PAGE);
    }

    /**
     * Search for everything with basic parameters.
     * @param q Keywords or phrases to search for
     * @param language The 2-letter ISO-639-1 code of the language
     * @param pageSize The number of results to return per page
     * @return NewsResponse containing articles and metadata
     */
    public NewsResponse searchEverything(String q, String language, int pageSize) throws IOException, InterruptedException {
        return searchEverything(q, null, null, null, null, null, null, language, DEFAULT_SORT_BY, pageSize, DEFAULT_PAGE);
    }

    /**
     * Search for everything with full customization.
     * @param q Keywords or phrases to search for
     * @param searchIn The fields to restrict search to (title, description, content)
     * @param sources Comma-separated string of source identifiers
     * @param domains Comma-separated string of domains to include
     * @param excludeDomains Comma-separated string of domains to exclude
     * @param fromDate Date for oldest article (as LocalDate, ISO 8601 format)
     * @param toDate Date for newest article (as LocalDate, ISO 8601 format)
     * @param language The 2-letter ISO-639-1 code of the language
     * @param sortBy Sort order (relevancy, popularity, publishedAt)
     * @param pageSize Number of results per page (max 100)
     * @param page Page number to retrieve
     * @return NewsResponse containing articles and metadata
     */
    public NewsResponse searchEverything(String q, String searchIn, String sources, String domains,
                                        String excludeDomains, LocalDate fromDate, LocalDate toDate, String language,
                                        String sortBy, int pageSize, int page) throws IOException, InterruptedException {
        StringBuilder url = new StringBuilder();
        url.append(BASE_URL).append("/v2/everything");

        // Build query parameters
        List<String> params = new ArrayList<>();

        if (q != null && !q.trim().isEmpty()) {
            params.add("q=" + URLEncoder.encode(q, StandardCharsets.UTF_8));
        }

        if (searchIn != null && !searchIn.trim().isEmpty()) {
            params.add("searchIn=" + URLEncoder.encode(searchIn, StandardCharsets.UTF_8));
        }

        if (sources != null && !sources.trim().isEmpty()) {
            params.add("sources=" + URLEncoder.encode(sources, StandardCharsets.UTF_8));
        }

        if (domains != null && !domains.trim().isEmpty()) {
            params.add("domains=" + URLEncoder.encode(domains, StandardCharsets.UTF_8));
        }

        if (excludeDomains != null && !excludeDomains.trim().isEmpty()) {
            params.add("excludeDomains=" + URLEncoder.encode(excludeDomains, StandardCharsets.UTF_8));
        }

        if (fromDate != null) {
            params.add("from=" + URLEncoder.encode(fromDate.toString(), StandardCharsets.UTF_8));
        }
        if (toDate != null) {
            params.add("to=" + URLEncoder.encode(toDate.toString(), StandardCharsets.UTF_8));
        }

        if (language != null && !language.trim().isEmpty()) {
            params.add("language=" + language);
        }

        if (sortBy != null && !sortBy.trim().isEmpty()) {
            params.add("sortBy=" + sortBy);
        }

        if (pageSize > 0 && pageSize <= 100) {
            params.add("pageSize=" + pageSize);
        }

        if (page > 0) {
            params.add("page=" + page);
        }

        // Add API key
        String apiKey = ApiUtil.loadEnvValue("NEWSAPI_API_KEY");
        if (apiKey != null && !apiKey.trim().isEmpty()) {
            params.add("apiKey=" + apiKey);
        }

        if (!params.isEmpty()) {
            url.append("?").append(String.join("&", params));
        }

        String responseBody = performGet(url.toString());
        return parseNewsResponse(responseBody);
    }

    /**
     * Get top headlines for the US.
     * @return NewsResponse containing top headlines and metadata
     */
    public NewsResponse getTopHeadlines() throws IOException, InterruptedException {
        return getTopHeadlines("us", null, null, null, DEFAULT_PAGE_SIZE, DEFAULT_PAGE);
    }

    /**
     * Get top headlines for a specific country and category.
     * @param country The 2-letter ISO 3166-1 country code (e.g., "us", "gb", "de")
     * @param category The category (business, entertainment, general, health, science, sports, technology)
     * @return NewsResponse containing top headlines and metadata
     */
    public NewsResponse getTopHeadlines(String country, String category) throws IOException, InterruptedException {
        return getTopHeadlines(country, category, null, null, DEFAULT_PAGE_SIZE, DEFAULT_PAGE);
    }

    /**
     * Get top headlines with full customization.
     * @param country The 2-letter ISO 3166-1 country code (cannot mix with sources)
     * @param category The category (cannot mix with sources)
     * @param sources Comma-separated string of source identifiers (cannot mix with country/category)
     * @param q Keywords or phrases to search for
     * @param pageSize Number of results per page (max 100)
     * @param page Page number to retrieve
     * @return NewsResponse containing top headlines and metadata
     */
    public NewsResponse getTopHeadlines(String country, String category, String sources,
                                       String q, int pageSize, int page) throws IOException, InterruptedException {

        StringBuilder url = new StringBuilder();
        url.append(BASE_URL).append("/v2/top-headlines");

        // Build query parameters
        List<String> params = new ArrayList<>();

        if (country != null && !country.trim().isEmpty()) {
            params.add("country=" + country);
        }

        if (category != null && !category.trim().isEmpty()) {
            params.add("category=" + category);
        }

        if (sources != null && !sources.trim().isEmpty()) {
            params.add("sources=" + URLEncoder.encode(sources, StandardCharsets.UTF_8));
        }

        if (q != null && !q.trim().isEmpty()) {
            params.add("q=" + URLEncoder.encode(q, StandardCharsets.UTF_8));
        }

        if (pageSize > 0 && pageSize <= 100) {
            params.add("pageSize=" + pageSize);
        }

        if (page > 0) {
            params.add("page=" + page);
        }

        // Add API key
        String apiKey = ApiUtil.loadEnvValue("NEWSAPI_API_KEY");
        if (apiKey != null && !apiKey.trim().isEmpty()) {
            params.add("apiKey=" + apiKey);
        }

        if (!params.isEmpty()) {
            url.append("?").append(String.join("&", params));
        }

        String responseBody = performGet(url.toString());
        return parseNewsResponse(responseBody);
    }

    /**
     * Parse the JSON response from NewsAPI into a NewsResponse object.
     * @param jsonResponse The JSON response string
     * @return NewsResponse object
     */
    private NewsResponse parseNewsResponse(String jsonResponse) {
        NewsResponse result = new NewsResponse();
        // Extract total results
        java.util.regex.Pattern totalResultsPattern = java.util.regex.Pattern.compile("\"totalResults\"\\s*:\\s*(\\d+)");
        java.util.regex.Matcher totalResultsMatcher = totalResultsPattern.matcher(jsonResponse);
        if (totalResultsMatcher.find()) {
            result.totalResults = Integer.parseInt(totalResultsMatcher.group(1));
        }
        // Extract status
        java.util.regex.Pattern statusPattern = java.util.regex.Pattern.compile("\"status\"\\s*:\\s*\"([^\"]+)\"");
        java.util.regex.Matcher statusMatcher = statusPattern.matcher(jsonResponse);
        if (statusMatcher.find()) {
            result.status = statusMatcher.group(1);
        }
        // Extract articles from the articles array
        java.util.regex.Pattern articlesPattern = java.util.regex.Pattern.compile("\"articles\"\\s*:\\s*\\[([^\\]]+)\\]");
        java.util.regex.Matcher articlesMatcher = articlesPattern.matcher(jsonResponse);
        if (articlesMatcher.find()) {
            String articlesSection = articlesMatcher.group(1);
            // Extract individual article fields
            java.util.regex.Pattern titlePattern = java.util.regex.Pattern.compile("\"title\"\\s*:\\s*\"([^\"]+)\"");
            java.util.regex.Pattern descriptionPattern = java.util.regex.Pattern.compile("\"description\"\\s*:\\s*\"([^\"]+)\"");
            java.util.regex.Pattern urlPattern = java.util.regex.Pattern.compile("\"url\"\\s*:\\s*\"([^\"]+)\"");
            java.util.regex.Pattern publishedAtPattern = java.util.regex.Pattern.compile("\"publishedAt\"\\s*:\\s*\"([^\"]+)\"");
            java.util.regex.Pattern sourceNamePattern = java.util.regex.Pattern.compile("\"source\"\\s*:\\s*\\{[^}]*\"name\"\\s*:\\s*\"([^\"]+)\"");
            java.util.regex.Matcher titleMatcher = titlePattern.matcher(articlesSection);
            java.util.regex.Matcher descriptionMatcher = descriptionPattern.matcher(articlesSection);
            java.util.regex.Matcher urlMatcher = urlPattern.matcher(articlesSection);
            java.util.regex.Matcher publishedAtMatcher = publishedAtPattern.matcher(articlesSection);
            java.util.regex.Matcher sourceNameMatcher = sourceNamePattern.matcher(articlesSection);
            while (titleMatcher.find()) {
                NewsArticle article = new NewsArticle();
                article.title = titleMatcher.group(1);
                if (descriptionMatcher.find()) {
                    article.description = descriptionMatcher.group(1);
                }
                if (urlMatcher.find()) {
                    article.url = urlMatcher.group(1);
                }
                if (publishedAtMatcher.find()) {
                    String publishedAtStr = publishedAtMatcher.group(1);
                    try {
                        article.publishedAt = LocalDate.parse(publishedAtStr.substring(0, 10));
                    } catch (DateTimeParseException | StringIndexOutOfBoundsException e) {
                        article.publishedAt = null;
                    }
                }
                if (sourceNameMatcher.find()) {
                    article.source = sourceNameMatcher.group(1);
                }
                result.articles.add(article);
            }
        }
        return result;
    }
}
// End of News.java