// import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Locator;
public class teams_microsoft_com extends com_base{
    //write a constructor that takes BrowserContext context as an argument
    public teams_microsoft_com(BrowserContext _context) {
        super(_context);
    }

    /**
     * Sends a message to a specified recipient in Microsoft Teams.
     *
     * @param recipientEmail The email address of the recipient.
     * @param messageText The text of the message to send.
     * @return MessageStatus containing the recipient email, message text, and status.
     */
    public MessageStatus sendMessage(String recipientEmail, String messageText) {
        page.navigate("https://teams.microsoft.com/v2/");
        page.waitForLoadState();
        
        Locator inputboxes = page.locator("#ms-searchux-input");
        // Fill in the recipient email
        inputboxes.fill(recipientEmail);
        //press Enter to submit the input
        inputboxes.press("Enter");

        //locate this element using data-tid
        Locator peopleTab = page.locator("button[data-tid='people-tab']");
        // Click the "People" tab
        peopleTab.click();
        page.waitForLoadState();
         //locate this element using data-tid
        Locator peopleList = page.locator("div[data-tid='search-people-card']").first();
        
        /*Locator selectedPerson;
        try {
            selectedPerson = peopleList.count() > 1 ? peopleList.first() : peopleList;
        } catch (Exception e) {
            selectedPerson = peopleList;
        }
        //click the first person in the list
        selectedPerson.click();*/
        //click the first person in the list
        peopleList.click();
        //wait for the page to load
        page.waitForLoadState();
        //locate this element
        /*<p data-placeholder="Type a message"> */
        Locator messageBox = page.locator("p[data-placeholder='Type a message']");
        // get the current text in the box, append message text
        String currentText = messageBox.innerText();
        messageBox.fill(currentText+ messageText);


        Locator sendButton = page.locator("button[data-tid='newMessageCommands-send']");
        // Click the "Send" button  
        sendButton.click();
        page.waitForLoadState(); page.waitForTimeout(1000);
        return new MessageStatus(recipientEmail, messageText, "SUCCESS");
    }

    /**
     * Sends a message to a specified group chat in Microsoft Teams.
     *
     * @param recipientEmail The email address or group chat name.
     * @param messageText The text of the message to send.
     * @return MessageStatus containing the recipient email, message text, and status.
     */
    public MessageStatus sendToGroupChat(String recipientEmail, String messageText) {
        page.navigate("https://teams.microsoft.com/v2/");
        page.waitForLoadState();
        
        Locator inputboxes = page.locator("#ms-searchux-input");
        // Fill in the recipient email
        inputboxes.fill("dummy chat for testing"); // NOTE: This is a placeholder, replace with recipientEmail if needed
        //press Enter to submit the input
        inputboxes.press("Enter");

        //locate this element using data-tid
        Locator peopleTab = page.locator("button[data-tid='groupchats-tab']");
        // Click the "groupchats" tab
        peopleTab.click();
        page.waitForLoadState();
         //locate this element using data-tid
        Locator peopleList = page.locator("div[data-tid='search-card']").first();
        
        /*Locator selectedPerson;
        try {
            selectedPerson = peopleList.count() > 1 ? peopleList.first() : peopleList;
        } catch (Exception e) {
            selectedPerson = peopleList;
        }
        //click the first person in the list
        selectedPerson.click();*/
        //click the first person in the list
        peopleList.click();
        //wait for the page to load
        page.waitForLoadState();
        //locate this element
        /*<p data-placeholder="Type a message"> */
        Locator messageBox = page.locator("p[data-placeholder='Type a message']");
        // get the current text in the box, append message text
        String currentText = messageBox.innerText();
        messageBox.fill(currentText+ messageText);


        Locator sendButton = page.locator("button[data-tid='newMessageCommands-send']");
        // Click the "Send" button  
        sendButton.click();
        page.waitForLoadState(); page.waitForTimeout(1000);
        return new MessageStatus(recipientEmail, messageText, "SUCCESS");
    }

    /**
     * Represents the result of sending a message, including recipient, message, and status.
     */
    public static class MessageStatus {
        /** The recipient email or group chat name. */
        public final String recipientEmail;
        /** The message text sent. */
        public final String messageText;
        /** The status of the send operation. */
        public final String status;
        public MessageStatus(String recipientEmail, String messageText, String status) {
            this.recipientEmail = recipientEmail;
            this.messageText = messageText;
            this.status = status;
        }
        @Override
        public String toString() {
            return String.format("Recipient: %s, Message: %s, Status: %s", recipientEmail, messageText, status);
        }
    }
}