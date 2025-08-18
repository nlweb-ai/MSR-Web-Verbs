
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the News API wrapper
 */
public class NewsTest {
    
    private News news;
    
    @BeforeEach
    void setUp() {
        news = new News();
    }
    
    @Test
    void testSearchEverythingBasic() throws Exception {
        // Test basic search for bitcoin news
        News.NewsResponse response = news.searchEverything("bitcoin");
        assertNotNull(response, "Search should return a non-null response");
        assertNotNull(response.articles, "Articles list should not be null");
        assertFalse(response.articles.isEmpty(), "Search should return at least some articles");
        // Print results for verification
        System.out.println("Basic search for 'bitcoin':");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
            System.out.println("  Source: " + article.source);
            System.out.println("  Published: " + article.publishedAt);
            System.out.println("  URL: " + article.url);
            System.out.println("  Description: " + article.description);
        }
    }
    
    @Test
    void testSearchEverythingWithLanguageAndPageSize() throws Exception {
        // Test search with language and page size parameters
        News.NewsResponse response = news.searchEverything("technology", "en", 5);
        assertNotNull(response, "Search should return a non-null response");
        // Print results for verification
        System.out.println("Search for 'technology' (en, pageSize 5):");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
        }
    }
    
    @Test
    void testSearchEverythingWithFullParameters() throws Exception {
        // Test search with comprehensive parameters
        News.NewsResponse response = news.searchEverything(
            "artificial intelligence",
            "title,content",
            null, // sources
            null, // domains
            null, // excludeDomains
            java.time.LocalDate.parse("2025-08-15"), // from
            java.time.LocalDate.parse("2025-08-16"), // to
            "en", // language
            "relevancy", // sortBy
            3, // pageSize
            1 // page
        );
        assertNotNull(response, "Search should return a non-null response");
        // Print results for verification
        System.out.println("Advanced search for 'artificial intelligence':");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
        }
    }
    
    @Test
    void testSearchEverythingWithDomains() throws Exception {
        // Test search restricted to specific domains
        News.NewsResponse response = news.searchEverything(
            "apple",
            null, // searchIn
            null, // sources
            "techcrunch.com,engadget.com", // domains
            null, // excludeDomains
            null, // from
            null, // to
            "en", // language
            "popularity", // sortBy
            5, // pageSize
            1 // page
        );
        assertNotNull(response, "Search should return a non-null response");
        // Print results for verification
        System.out.println("Search for 'apple' from tech domains:");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
        }
    }
    
    @Test
    void testSearchEverythingWithEmptyQuery() throws Exception {
        // Test search with empty query (should still work with other parameters)
        News.NewsResponse response = news.searchEverything(
            "", // empty query
            null, // searchIn
            null, // sources
            "bbc.co.uk", // domains - get news from BBC
            null, // excludeDomains
            null, // from
            null, // to
            "en", // language
            "publishedAt", // sortBy
            3, // pageSize
            1 // page
        );
        assertNotNull(response, "Search should return a non-null response even for empty query");
        // Print results for verification
        System.out.println("Search with empty query from BBC:");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
        }
    }
    
    @Test
    void testGetTopHeadlinesBasic() throws Exception {
        // Test basic top headlines for US
        News.NewsResponse response = news.getTopHeadlines();
        assertNotNull(response, "Top headlines should return a non-null response");
        assertNotNull(response.articles, "Articles list should not be null");
        assertFalse(response.articles.isEmpty(), "Top headlines should return at least some articles");
        // Print results for verification
        System.out.println("Basic top headlines for US:");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
        }
    }
    
    @Test
    void testGetTopHeadlinesWithCountryAndCategory() throws Exception {
        // Test top headlines for specific country and category
        News.NewsResponse response = news.getTopHeadlines("us", "technology");
        assertNotNull(response, "Top headlines should return a non-null response");
        // Print results for verification
        System.out.println("Top technology headlines for US:");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
        }
    }
    
    @Test
    void testGetTopHeadlinesWithSources() throws Exception {
        // Test top headlines from specific sources
        News.NewsResponse response = news.getTopHeadlines(
            null, // country
            null, // category
            "bbc-news,cnn", // sources
            null, // q
            5, // pageSize
            1 // page
        );
        assertNotNull(response, "Top headlines should return a non-null response");
        // Print results for verification
        System.out.println("Top headlines from BBC News and CNN:");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
        }
    }
    
    @Test
    void testGetTopHeadlinesWithSearchQuery() throws Exception {
        // Test top headlines with search query
        News.NewsResponse response = news.getTopHeadlines(
            "us", // country
            null, // category
            null, // sources
            "climate", // q
            3, // pageSize
            1 // page
        );
        assertNotNull(response, "Top headlines should return a non-null response");
        // Print results for verification
        System.out.println("Top headlines about 'climate' in US:");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
        }
    }
    
    @Test
    void testGetTopHeadlinesBusinessCategory() throws Exception {
        // Test top headlines for business category
        News.NewsResponse response = news.getTopHeadlines("us", "business");
        assertNotNull(response, "Top headlines should return a non-null response");
        // Print results for verification
        System.out.println("Top business headlines for US:");
        for (News.NewsArticle article : response.articles) {
            System.out.println("  Title: " + article.title);
        }
    }
}
