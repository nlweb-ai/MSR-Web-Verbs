import java.util.List;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the OpenLibrary API wrapper
 */
public class OpenLibraryTest {
    
    private OpenLibrary openLibrary;
    
    @BeforeEach
    void setUp() {
        openLibrary = new OpenLibrary();
    }
      @Test
    void testSearchWithQuery() throws Exception {
        // Test searching for Java programming books
        List<OpenLibrary.BookInfo> books = openLibrary.search("java programming", "*", "new", "en", 5, 1);

        assertNotNull(books, "Search should return a non-null list");
        assertFalse(books.isEmpty(), "Search should return at least one book");
        assertTrue(books.size() <= 5, "Search should return at most 5 books by default");

        // Print results for verification
        System.out.println("Found Java programming books:");
        for (int i = 0; i < books.size(); i++) {
            System.out.println((i + 1) + ". " + books.get(i).title);
        }
    }
      @Test
    void testSearchWithQueryAndLimit() throws Exception {
        // Test searching with custom parameters matching openlibrary.txt structure
        List<OpenLibrary.BookInfo> books = openLibrary.search("python", "title,author_name", "new", "en", 3, 1);

        assertNotNull(books, "Search should return a non-null list");
        assertFalse(books.isEmpty(), "Search should return at least one book");
        assertTrue(books.size() <= 3, "Search should return at most 3 books when limit is 3");
    }
      @Test
    void testSearchWithEmptyQuery() throws Exception {
        // Test searching with empty query
        List<OpenLibrary.BookInfo> books = openLibrary.search("", "*", "new", "en", 5, 1);

        assertNotNull(books, "Search should return a non-null list even for empty query");
        // Empty query might still return results, so we just check it doesn't crash
    }
    
    @Test
    void testSearchAuthorsWithQuery() throws Exception {
        // Test searching for a well-known author
        List<OpenLibrary.AuthorInfo> authors = openLibrary.searchAuthors("j k rowling");

        assertNotNull(authors, "Search should return a non-null list");
        assertFalse(authors.isEmpty(), "Search should return at least one author");
        assertTrue(authors.size() <= 5, "Search should return at most 5 authors by default");

        // Print results for verification
        System.out.println("Found authors for 'j k rowling':");
        for (int i = 0; i < authors.size(); i++) {
            System.out.println((i + 1) + ". " + authors.get(i).name);
        }
    }
    
    @Test
    void testSearchAuthorsWithCustomLimit() throws Exception {
        // Test searching for authors with custom limit
        List<OpenLibrary.AuthorInfo> authors = openLibrary.searchAuthors("stephen king", 3);

        assertNotNull(authors, "Search should return a non-null list");
        assertTrue(authors.size() <= 3, "Search should return at most 3 authors when limit is 3");

        // Print results for verification
        System.out.println("Found authors for 'stephen king' (limit 3):");
        for (int i = 0; i < authors.size(); i++) {
            System.out.println((i + 1) + ". " + authors.get(i).name);
        }
    }
    
    @Test
    void testSearchAuthorsWithEmptyQuery() throws Exception {
        // Test searching with empty query
        List<OpenLibrary.AuthorInfo> authors = openLibrary.searchAuthors("");

        assertNotNull(authors, "Search should return a non-null list even for empty query");
        // Empty query might still return results, so we just check it doesn't crash
    }
    
    @Test
    void testGetSubjectBasic() throws Exception {
        // Test getting subject information for a common subject
        List<OpenLibrary.SubjectInfo> subjectInfo = openLibrary.getSubject("love");

        assertNotNull(subjectInfo, "Subject search should return a non-null list");
        assertFalse(subjectInfo.isEmpty(), "Subject search should return at least some information");

        // Print results for verification
        System.out.println("Subject information for 'love':");
        for (OpenLibrary.SubjectInfo info : subjectInfo) {
            System.out.println("  " + info.info);
        }
    }
    
    @Test
    void testGetSubjectWithDetails() throws Exception {
        // Test getting detailed subject information
        List<OpenLibrary.SubjectInfo> subjectInfo = openLibrary.getSubject("science", true);

        assertNotNull(subjectInfo, "Subject search with details should return a non-null list");
        assertFalse(subjectInfo.isEmpty(), "Subject search with details should return at least some information");

        // Print results for verification
        System.out.println("Detailed subject information for 'science':");
        for (OpenLibrary.SubjectInfo info : subjectInfo) {
            System.out.println("  " + info.info);
        }
    }
    
    @Test
    void testGetSubjectWithCustomParameters() throws Exception {
        // Test getting subject information with custom limit and offset
        List<OpenLibrary.SubjectInfo> subjectInfo = openLibrary.getSubject("history", false, 3, 0);

        assertNotNull(subjectInfo, "Subject search with custom parameters should return a non-null list");

        // Print results for verification
        System.out.println("Subject information for 'history' (limit 3):");
        for (OpenLibrary.SubjectInfo info : subjectInfo) {
            System.out.println("  " + info.info);
        }
    }
}
