import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Page;

public class com_base {
    protected BrowserContext context;
    protected Page page;
    java.util.Scanner scanner= new java.util.Scanner(System.in);
    public com_base(BrowserContext _context) {
        context = _context;
        if (context.pages().isEmpty()) {
            page = context.newPage(); // Create a new page if none exist
        } else {
            page = context.pages().get(0); // Use the first existing page
        }
    }
}
