import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0035 {
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
            // Step 1: Search for popular children's books using OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            JsonArray childrensBooksArray = new JsonArray();
            
            try {
                // Search for popular children's books
                List<OpenLibrary.BookInfo> popularBooks = openLibrary.search("children picture books", null, null, "en", 15, 1);
                List<OpenLibrary.BookInfo> classicBooks = openLibrary.search("classic children literature", null, null, "en", 10, 1);
                List<OpenLibrary.BookInfo> summerBooks = openLibrary.search("summer reading kids", null, null, "en", 8, 1);
                
                // Add popular children's books
                if (popularBooks != null) {
                    for (OpenLibrary.BookInfo book : popularBooks) {
                        JsonObject bookObj = new JsonObject();
                        bookObj.addProperty("title", book.title);
                        bookObj.addProperty("category", "Popular Children's Books");
                        bookObj.addProperty("reading_level", "Elementary/Middle School");
                        childrensBooksArray.add(bookObj);
                    }
                }
                
                // Add classic children's books
                if (classicBooks != null) {
                    for (OpenLibrary.BookInfo book : classicBooks) {
                        JsonObject bookObj = new JsonObject();
                        bookObj.addProperty("title", book.title);
                        bookObj.addProperty("category", "Classic Children's Literature");
                        bookObj.addProperty("reading_level", "All Ages");
                        childrensBooksArray.add(bookObj);
                    }
                }
                
                // Add summer reading books
                if (summerBooks != null) {
                    for (OpenLibrary.BookInfo book : summerBooks) {
                        JsonObject bookObj = new JsonObject();
                        bookObj.addProperty("title", book.title);
                        bookObj.addProperty("category", "Summer Reading");
                        bookObj.addProperty("reading_level", "Various");
                        childrensBooksArray.add(bookObj);
                    }
                }
                
            } catch (Exception e) {
                JsonObject booksError = new JsonObject();
                booksError.addProperty("error", "Failed to get children's books: " + e.getMessage());
                childrensBooksArray.add(booksError);
            }
            
            output.add("childrens_books", childrensBooksArray);
            
            // Step 2: Find articles about benefits of summer reading for kids
            News news = new News();
            LocalDate fromDate = LocalDate.of(2025, 6, 1); // Recent articles from June 2025
            LocalDate toDate = LocalDate.of(2025, 8, 3);
            
            JsonArray readingNewsArray = new JsonArray();
            try {
                // Search for summer reading benefits articles
                News.NewsResponse readingNews = news.searchEverything("summer reading children benefits kids education literacy", 
                                                                    null, null, null, null, 
                                                                    fromDate, toDate, "en", 
                                                                    "publishedAt", 15, 1);
                
                if (readingNews != null && readingNews.articles != null) {
                    for (News.NewsArticle article : readingNews.articles) {
                        // Filter for relevant reading articles
                        if (article.title != null && 
                            (article.title.toLowerCase().contains("reading") ||
                             article.title.toLowerCase().contains("literacy") ||
                             article.title.toLowerCase().contains("children") ||
                             article.title.toLowerCase().contains("education") ||
                             article.title.toLowerCase().contains("summer") ||
                             article.title.toLowerCase().contains("books"))) {
                            
                            JsonObject articleObj = new JsonObject();
                            articleObj.addProperty("title", article.title);
                            articleObj.addProperty("description", article.description);
                            articleObj.addProperty("url", article.url);
                            articleObj.addProperty("source", article.source);
                            articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                            articleObj.addProperty("relevance", "High");
                            readingNewsArray.add(articleObj);
                        }
                    }
                }
                
                // Search for library program articles if needed
                if (readingNewsArray.size() < 8) {
                    News.NewsResponse libraryNews = news.searchEverything("library programs children reading challenge", 
                                                                        null, null, null, null, 
                                                                        fromDate, toDate, "en", 
                                                                        "publishedAt", 10, 1);
                    
                    if (libraryNews != null && libraryNews.articles != null) {
                        for (News.NewsArticle article : libraryNews.articles) {
                            if (readingNewsArray.size() >= 12) break;
                            
                            JsonObject articleObj = new JsonObject();
                            articleObj.addProperty("title", article.title);
                            articleObj.addProperty("description", article.description);
                            articleObj.addProperty("url", article.url);
                            articleObj.addProperty("source", article.source);
                            articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                            articleObj.addProperty("relevance", "Medium");
                            readingNewsArray.add(articleObj);
                        }
                    }
                }
                
            } catch (Exception e) {
                JsonObject newsError = new JsonObject();
                newsError.addProperty("error", "Failed to get reading news: " + e.getMessage());
                readingNewsArray.add(newsError);
            }
            
            output.add("reading_news", readingNewsArray);
            
            // Step 3: Gather fun facts about famous children's authors using Wikimedia
            Wikimedia wikimedia = new Wikimedia();
            JsonArray authorFacts = new JsonArray();
            
            try {
                // Search for famous children's authors
                String[] childrenAuthors = {
                    "Dr. Seuss", "Roald Dahl", "Maurice Sendak", "Eric Carle", "Beverly Cleary", 
                    "Judy Blume", "Shel Silverstein", "Laura Ingalls Wilder", "E.B. White", "C.S. Lewis"
                };
                
                for (String author : childrenAuthors) {
                    try {
                        Wikimedia.SearchResult searchResult = wikimedia.search(author, "en", 2);
                        if (searchResult != null && searchResult.titles != null && !searchResult.titles.isEmpty()) {
                            for (String title : searchResult.titles) {
                                Wikimedia.PageInfo pageInfo = wikimedia.getPage(title);
                                if (pageInfo != null) {
                                    JsonObject authorObj = new JsonObject();
                                    authorObj.addProperty("author_name", author);
                                    authorObj.addProperty("wikipedia_title", pageInfo.title);
                                    authorObj.addProperty("url", pageInfo.htmlUrl);
                                    authorObj.addProperty("lastModified", pageInfo.lastModified != null ? pageInfo.lastModified.toString() : null);
                                    authorObj.addProperty("fun_fact_source", true);
                                    authorFacts.add(authorObj);
                                    break; // Only take first result for each author
                                }
                            }
                        }
                    } catch (Exception e) {
                        System.err.println("Failed to get info for author: " + author + " - " + e.getMessage());
                    }
                }
                
            } catch (Exception e) {
                JsonObject factsError = new JsonObject();
                factsError.addProperty("error", "Failed to get author facts: " + e.getMessage());
                authorFacts.add(factsError);
            }
            
            output.add("author_facts", authorFacts);
            
            // Step 4: Send announcement to library staff group chat
            teams_microsoft_com teams = new teams_microsoft_com(context);
            
            // Prepare staff announcement content
            StringBuilder announcementContent = new StringBuilder();
            announcementContent.append("📚 SUMMER READING CHALLENGE 2025 - STAFF ANNOUNCEMENT\\n\\n");
            announcementContent.append("🌟 Program Launch: August 3, 2025\\n");
            announcementContent.append("📍 Location: Boston Public Library\\n\\n");
            
            // Add reading list highlights
            announcementContent.append("📖 FEATURED READING LIST HIGHLIGHTS:\\n");
            int bookCount = Math.min(5, childrensBooksArray.size());
            for (int i = 0; i < bookCount; i++) {
                JsonObject book = childrensBooksArray.get(i).getAsJsonObject();
                if (book.has("title")) {
                    announcementContent.append("• ").append(book.get("title").getAsString()).append("\\n");
                }
            }
            
            // Add news highlights
            announcementContent.append("\\n📰 RESEARCH HIGHLIGHTS:\\n");
            announcementContent.append("• ").append(readingNewsArray.size()).append(" recent articles found on benefits of summer reading\\n");
            announcementContent.append("• Research shows increased literacy and engagement through summer programs\\n");
            
            // Add author facts
            announcementContent.append("\\n✨ FUN AUTHOR FACTS PREPARED:\\n");
            announcementContent.append("• Background info on ").append(authorFacts.size()).append(" famous children's authors\\n");
            announcementContent.append("• Perfect for story time and program activities\\n");
            
            announcementContent.append("\\n🎯 NEXT STEPS:\\n");
            announcementContent.append("• Review complete reading list and author materials\\n");
            announcementContent.append("• Prepare display materials and program schedules\\n");
            announcementContent.append("• Coordinate with children's department for activities\\n");
            announcementContent.append("\\nLet's make this the best summer reading challenge yet! 📚🌞");
            
            String staffEmail = "library-staff@bostonlibrary.org"; // Placeholder staff email
            teams_microsoft_com.MessageStatus messageStatus = teams.sendToGroupChat(staffEmail, announcementContent.toString());
            
            JsonObject teamsResult = new JsonObject();
            teamsResult.addProperty("recipient", messageStatus.recipientEmail);
            teamsResult.addProperty("message_preview", announcementContent.toString().substring(0, Math.min(150, announcementContent.length())) + "...");
            teamsResult.addProperty("status", messageStatus.status);
            teamsResult.addProperty("announcement_type", "Summer Reading Challenge Launch");
            
            output.add("staff_announcement", teamsResult);
            
            // Step 5: Create comprehensive reading challenge summary
            JsonObject challengeSummary = new JsonObject();
            challengeSummary.addProperty("challenge_name", "Summer Reading Challenge 2025");
            challengeSummary.addProperty("start_date", "August 3, 2025");
            challengeSummary.addProperty("location", "Boston Public Library");
            challengeSummary.addProperty("target_audience", "Children and Families");
            challengeSummary.addProperty("books_researched", childrensBooksArray.size());
            challengeSummary.addProperty("news_articles_found", readingNewsArray.size());
            challengeSummary.addProperty("author_profiles_prepared", authorFacts.size());
            challengeSummary.addProperty("staff_notified", messageStatus.status.equals("success"));
            
            JsonObject programDetails = new JsonObject();
            
            // Create age-appropriate reading lists
            JsonArray readingLists = new JsonArray();
            
            JsonObject earlyReaders = new JsonObject();
            earlyReaders.addProperty("age_group", "Early Readers (Ages 4-7)");
            earlyReaders.addProperty("focus", "Picture books and beginner chapter books");
            earlyReaders.addProperty("book_count", 8);
            readingLists.add(earlyReaders);
            
            JsonObject middleGrade = new JsonObject();
            middleGrade.addProperty("age_group", "Middle Grade (Ages 8-12)");
            middleGrade.addProperty("focus", "Chapter books and middle grade novels");
            middleGrade.addProperty("book_count", 10);
            readingLists.add(middleGrade);
            
            JsonObject teens = new JsonObject();
            teens.addProperty("age_group", "Teen Readers (Ages 13+)");
            teens.addProperty("focus", "Young adult fiction and classics");
            teens.addProperty("book_count", 6);
            readingLists.add(teens);
            
            programDetails.add("reading_lists", readingLists);
            
            // Program activities
            JsonArray activities = new JsonArray();
            activities.add("Author spotlight presentations");
            activities.add("Reading comprehension games");
            activities.add("Book-themed craft activities");
            activities.add("Reading progress tracking");
            activities.add("End-of-summer celebration event");
            
            programDetails.add("planned_activities", activities);
            
            // Benefits highlighted from research
            JsonArray benefits = new JsonArray();
            benefits.add("Prevents summer learning loss");
            benefits.add("Improves reading comprehension skills");
            benefits.add("Builds vocabulary and language skills");
            benefits.add("Encourages lifelong reading habits");
            benefits.add("Strengthens family reading time");
            
            programDetails.add("program_benefits", benefits);
            
            challengeSummary.add("program_details", programDetails);
            output.add("challenge_summary", challengeSummary);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while organizing the summer reading challenge: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
