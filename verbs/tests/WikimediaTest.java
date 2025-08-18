import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the Wikimedia API wrapper
 * Tests all methods with their new explicit return types
 */
public class WikimediaTest {
    private Wikimedia wikimedia;

    @BeforeEach
    void setUp() {
        wikimedia = new Wikimedia();
    }

    @Test
    @DisplayName("Test searching for Seattle articles with explicit SearchResult return type")
    void testSearchSeattleArticles() throws Exception {
        Wikimedia.SearchResult result = wikimedia.search("Seattle", "en", 5);
        
        assertNotNull(result, "SearchResult should not be null");
        assertNotNull(result.titles, "Titles list should not be null");
        assertFalse(result.titles.isEmpty(), "Should find at least one article about Seattle");
        assertTrue(result.titles.size() <= 5, "Should not return more than 5 articles");
        
        // Check that at least one article title contains "Seattle"
        boolean foundSeattleArticle = result.titles.stream()
            .anyMatch(title -> title.toLowerCase().contains("seattle"));
        assertTrue(foundSeattleArticle, "At least one article should contain 'Seattle' in the title");
        
        System.out.println("Found Seattle articles:");
        for (int i = 0; i < result.titles.size(); i++) {
            System.out.println((i + 1) + ". " + result.titles.get(i));
        }
    }

    @Test
    @DisplayName("Test search with custom parameters")
    void testSearchWithCustomParameters() throws Exception {
        Wikimedia.SearchResult result = wikimedia.search("Seattle", "en", 3);
        
        assertNotNull(result, "SearchResult should not be null");
        assertNotNull(result.titles, "Titles list should not be null");
        assertTrue(result.titles.size() <= 3, "Should not return more than 3 articles");
    }

    @Test
    @DisplayName("Test search with empty query")
    void testSearchWithEmptyQuery() {
        assertThrows(Exception.class, () -> {
            wikimedia.search("", "en", 5);
        }, "Empty query should throw an exception");
    }

    @Test
    @DisplayName("Test searching titles that begin with 'earth' using SearchResult")
    void testSearchTitles() throws Exception {
        Wikimedia.SearchResult result = wikimedia.searchTitles("earth", "en", 5);
        
        assertNotNull(result, "SearchResult should not be null");
        assertNotNull(result.titles, "Titles list should not be null");
        assertFalse(result.titles.isEmpty(), "Should find at least one title starting with 'earth'");
        assertTrue(result.titles.size() <= 5, "Should not return more than 5 titles");
        
        // Check that all titles begin with "earth" (case-insensitive)
        for (String title : result.titles) {
            assertTrue(title.toLowerCase().startsWith("earth"), 
                "Title '" + title + "' should start with 'earth'");
        }
        
        System.out.println("Found titles starting with 'earth':");
        for (int i = 0; i < result.titles.size(); i++) {
            System.out.println((i + 1) + ". " + result.titles.get(i));
        }
    }

    @Test
    @DisplayName("Test searchTitles with default parameters using SearchResult")
    void testSearchTitlesDefault() throws Exception {
        Wikimedia.SearchResult result = wikimedia.searchTitles("cat");
        
        assertNotNull(result, "SearchResult should not be null");
        assertNotNull(result.titles, "Titles list should not be null");
        assertTrue(result.titles.size() <= 5, "Should not return more than default limit of 5");
        
        System.out.println("Found titles starting with 'cat' (using defaults):");
        for (int i = 0; i < result.titles.size(); i++) {
            System.out.println((i + 1) + ". " + result.titles.get(i));
        }
    }

    @Test
    @DisplayName("Test searchTitles with custom limit using SearchResult")
    void testSearchTitlesCustomLimit() throws Exception {
        Wikimedia.SearchResult result = wikimedia.searchTitles("java", "en", 3);
        
        assertNotNull(result, "SearchResult should not be null");
        assertNotNull(result.titles, "Titles list should not be null");
        assertTrue(result.titles.size() <= 3, "Should not return more than 3 titles");
        
        // Check that all titles begin with "java" (case-insensitive)
        for (String title : result.titles) {
            assertTrue(title.toLowerCase().startsWith("java"), 
                "Title '" + title + "' should start with 'java'");
        }
        
        System.out.println("Found titles starting with 'java' (limit 3):");
        for (int i = 0; i < result.titles.size(); i++) {
            System.out.println((i + 1) + ". " + result.titles.get(i));
        }
    }

    @Test
    @DisplayName("Test getUserAgent method")
    void testGetUserAgent() {
        String userAgent = Wikimedia.getUserAgent();
        
        assertNotNull(userAgent, "User agent should not be null");
        assertTrue(userAgent.contains("javify"), "User agent should contain app name");
        assertTrue(userAgent.contains("sirius0see+api@gmail.com"), "User agent should contain email");
        
        System.out.println("Wikimedia User Agent: " + userAgent);
    }

    @Test
    @DisplayName("Test getting page information for Earth article using PageInfo")
    void testGetPage() throws Exception {
        Wikimedia.PageInfo pageInfo = wikimedia.getPage("Earth", "en");
        
        assertNotNull(pageInfo, "PageInfo should not be null");
        assertNotNull(pageInfo.title, "Page title should not be null");
        assertTrue(pageInfo.id > 0 || !pageInfo.title.isEmpty(), "Should have either ID or title information");
        
        System.out.println("Page information for 'Earth':");
        System.out.println("  ID: " + pageInfo.id);
        System.out.println("  Title: " + pageInfo.title);
        System.out.println("  Key: " + pageInfo.key);
        System.out.println("  Content Model: " + pageInfo.contentModel);
        System.out.println("  License URL: " + pageInfo.licenseUrl);
        System.out.println("  License Title: " + pageInfo.licenseTitle);
        System.out.println("  HTML URL: " + pageInfo.htmlUrl);
        System.out.println("  Last Modified: " + pageInfo.lastModified);
    }

    @Test
    @DisplayName("Test getPage with default language using PageInfo")
    void testGetPageDefault() throws Exception {
        Wikimedia.PageInfo pageInfo = wikimedia.getPage("Java");
        
        assertNotNull(pageInfo, "PageInfo should not be null");
        
        System.out.println("Page information for 'Java' (using default language):");
        System.out.println("  ID: " + pageInfo.id);
        System.out.println("  Title: " + pageInfo.title);
        System.out.println("  Content Model: " + pageInfo.contentModel);
    }

    @Test
    @DisplayName("Test getPage with non-existent page")
    void testGetPageNotFound() {
        assertDoesNotThrow(() -> {
            wikimedia.getPage("ThisPageDoesNotExistForSure123456", "en");
        }, "Should not throw exception for non-existent page");
    }

    @Test
    @DisplayName("Test getHtml functionality using HtmlContentInfo")
    void testGetHtml() throws Exception {
        Wikimedia.HtmlContentInfo htmlInfo = wikimedia.getHtml("Earth", "en");
        
        assertNotNull(htmlInfo, "HtmlContentInfo should not be null");
        assertNotNull(htmlInfo.htmlTitle, "HTML title should not be null");
        assertTrue(htmlInfo.contentLength >= 0, "Content length should be non-negative");
        
        System.out.println("HTML information for 'Earth' article:");
        System.out.println("  HTML Title: " + htmlInfo.htmlTitle);
        System.out.println("  H1 Count: " + htmlInfo.h1Count);
        System.out.println("  H2 Count: " + htmlInfo.h2Count);
        System.out.println("  H3 Count: " + htmlInfo.h3Count);
        System.out.println("  Link Count: " + htmlInfo.linkCount);
        System.out.println("  Image Count: " + htmlInfo.imageCount);
        System.out.println("  Paragraph Count: " + htmlInfo.paragraphCount);
        System.out.println("  Content Length: " + htmlInfo.contentLength);
        System.out.println("  Sample H1 Headings: " + htmlInfo.sampleH1Headings);
        System.out.println("  Sample H2 Headings: " + htmlInfo.sampleH2Headings);
    }

    @Test
    @DisplayName("Test getHtml with default language using HtmlContentInfo")
    void testGetHtmlDefault() throws Exception {
        Wikimedia.HtmlContentInfo htmlInfo = wikimedia.getHtml("Java");
        
        assertNotNull(htmlInfo, "HtmlContentInfo should not be null");
        
        System.out.println("HTML information for 'Java' (using default language):");
        System.out.println("  HTML Title: " + htmlInfo.htmlTitle);
        System.out.println("  Content Length: " + htmlInfo.contentLength);
    }

    @Test
    @DisplayName("Test getHtml with non-existent page")
    void testGetHtmlNotFound() {
        assertThrows(Exception.class, () -> {
            wikimedia.getHtml("ThisPageDoesNotExistForSure123456", "en");
        }, "Should throw exception for non-existent page");
    }

    @Test
    @DisplayName("Test createPage simulation with full parameters using PageOperationRequest")
    void testCreatePage() {
        String title = "User:TestUser/Sandbox";
        String source = "== Welcome ==\nThis is a test page created via the Wikimedia API.\n\n* Item 1\n* Item 2\n* Item 3";
        String comment = "Creating a test page for API demonstration";
        String contentModel = "wikitext";
        String languageCode = "en";
        
        Wikimedia.PageOperationRequest request = wikimedia.createPage(title, source, comment, contentModel, languageCode);
        
        assertNotNull(request, "PageOperationRequest should not be null");
        assertEquals("CREATE", request.operationType, "Operation type should be CREATE");
        assertEquals("POST", request.method, "HTTP method should be POST");
        assertEquals(title, request.title, "Title should match");
        assertEquals(comment, request.comment, "Comment should match");
        assertEquals(contentModel, request.contentModel, "Content model should match");
        assertEquals(languageCode, request.languageCode, "Language code should match");
        assertTrue(request.isSimulation, "Should be marked as simulation");
        assertTrue(request.url.contains("wikipedia/en/page"), "URL should contain correct endpoint");
        
        System.out.println("Create page simulation output:");
        System.out.println("  Operation: " + request.operationType);
        System.out.println("  URL: " + request.url);
        System.out.println("  Method: " + request.method);
        System.out.println("  Title: " + request.title);
        System.out.println("  Comment: " + request.comment);
        System.out.println("  Content Model: " + request.contentModel);
        System.out.println("  Language: " + request.languageCode);
        System.out.println("  Is Simulation: " + request.isSimulation);
    }

    @Test
    @DisplayName("Test createPage simulation with default parameters using PageOperationRequest")
    void testCreatePageDefault() {
        String title = "User:TestUser/AnotherSandbox";
        String source = "This is a simple test page.";
        String comment = "Simple test page creation";
        
        Wikimedia.PageOperationRequest request = wikimedia.createPage(title, source, comment);
        
        assertNotNull(request, "PageOperationRequest should not be null");
        assertEquals("CREATE", request.operationType, "Operation type should be CREATE");
        assertEquals("wikitext", request.contentModel, "Should use default content model 'wikitext'");
        assertEquals("en", request.languageCode, "Should use default English language");
        assertTrue(request.isSimulation, "Should be marked as simulation");
        
        System.out.println("Create page simulation with defaults:");
        System.out.println("  Content Model: " + request.contentModel);
        System.out.println("  Language: " + request.languageCode);
    }

    @Test
    @DisplayName("Test createPage simulation with long content using PageOperationRequest")
    void testCreatePageLongContent() {
        String title = "User:TestUser/LongContentPage";
        StringBuilder longSource = new StringBuilder();
        for (int i = 0; i < 50; i++) {
            longSource.append("This is line ").append(i + 1).append(" of a very long content that exceeds 100 characters. ");
        }
        String comment = "Testing page creation with long content";
        
        Wikimedia.PageOperationRequest request = wikimedia.createPage(title, longSource.toString(), comment);
        
        assertNotNull(request, "PageOperationRequest should not be null");
        assertEquals("CREATE", request.operationType, "Operation type should be CREATE");
        assertTrue(request.isSimulation, "Should be marked as simulation");
        
        System.out.println("Create page simulation with long content (may be truncated in display):");
        System.out.println("  Source length: " + request.source.length());
    }

    @Test
    @DisplayName("Test editPage simulation with full parameters using PageOperationRequest")
    void testEditPage() {
        String title = "Wikipedia:Sandbox";
        String source = "== Updated Content ==\n\nThis page has been updated via the Wikimedia API.\n\n=== New Section ===\n* Updated item 1\n* Updated item 2\n* Updated item 3\n\n[[Category:API Test Pages]]";
        String comment = "Updating page content via API demonstration";
        String contentModel = "wikitext";
        long latestRevisionId = 1234567890L;
        String languageCode = "en";
        
        Wikimedia.PageOperationRequest request = wikimedia.editPage(title, source, comment, contentModel, latestRevisionId, languageCode);
        
        assertNotNull(request, "PageOperationRequest should not be null");
        assertEquals("EDIT", request.operationType, "Operation type should be EDIT");
        assertEquals("PUT", request.method, "HTTP method should be PUT");
        assertEquals(title, request.title, "Title should match");
        assertEquals(comment, request.comment, "Comment should match");
        assertEquals(contentModel, request.contentModel, "Content model should match");
        assertEquals(languageCode, request.languageCode, "Language code should match");
        assertEquals(Long.valueOf(latestRevisionId), request.latestRevisionId, "Revision ID should match");
        assertTrue(request.isSimulation, "Should be marked as simulation");
        assertTrue(request.url.contains("wikipedia/en/page/" + title), "URL should contain correct endpoint");
        
        System.out.println("Edit page simulation output:");
        System.out.println("  Operation: " + request.operationType);
        System.out.println("  URL: " + request.url);
        System.out.println("  Method: " + request.method);
        System.out.println("  Title: " + request.title);
        System.out.println("  Comment: " + request.comment);
        System.out.println("  Content Model: " + request.contentModel);
        System.out.println("  Language: " + request.languageCode);
        System.out.println("  Revision ID: " + request.latestRevisionId);
        System.out.println("  Is Simulation: " + request.isSimulation);
    }

    @Test
    @DisplayName("Test editPage simulation with default parameters using PageOperationRequest")
    void testEditPageDefault() {
        String title = "Wikipedia:Sandbox";
        String source = "Updated content with default parameters.";
        String comment = "Simple update via API";
        long latestRevisionId = 9876543210L;
        
        Wikimedia.PageOperationRequest request = wikimedia.editPage(title, source, comment, latestRevisionId);
        
        assertNotNull(request, "PageOperationRequest should not be null");
        assertEquals("EDIT", request.operationType, "Operation type should be EDIT");
        assertEquals("wikitext", request.contentModel, "Should use default content model 'wikitext'");
        assertEquals("en", request.languageCode, "Should use default English language");
        assertEquals(Long.valueOf(latestRevisionId), request.latestRevisionId, "Revision ID should match");
        assertTrue(request.isSimulation, "Should be marked as simulation");
        
        System.out.println("Edit page simulation with defaults:");
        System.out.println("  Content Model: " + request.contentModel);
        System.out.println("  Language: " + request.languageCode);
        System.out.println("  Revision ID: " + request.latestRevisionId);
    }

    @Test
    @DisplayName("Test editPage simulation with long content using PageOperationRequest")
    void testEditPageLongContent() {
        String title = "User:TestUser/LongContentEdit";
        StringBuilder longSource = new StringBuilder();
        for (int i = 0; i < 30; i++) {
            longSource.append("This is updated line ").append(i + 1).append(" with much longer content than before. ");
        }
        String comment = "Testing page edit with long content";
        long latestRevisionId = 5555555555L;
        
        Wikimedia.PageOperationRequest request = wikimedia.editPage(title, longSource.toString(), comment, latestRevisionId);
        
        assertNotNull(request, "PageOperationRequest should not be null");
        assertEquals("EDIT", request.operationType, "Operation type should be EDIT");
        assertEquals(Long.valueOf(latestRevisionId), request.latestRevisionId, "Revision ID should match");
        assertTrue(request.isSimulation, "Should be marked as simulation");
        
        System.out.println("Edit page simulation with long content:");
        System.out.println("  Source length: " + request.source.length());
        System.out.println("  Revision ID: " + request.latestRevisionId);
    }
}
