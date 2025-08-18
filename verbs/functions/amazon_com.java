import java.util.ArrayList;
import java.util.List;

import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Locator;
//import com_base;


public class amazon_com extends com_base {

    public amazon_com(BrowserContext _context) {
        super(_context);
    }

    /**
     * Clears all items from the Amazon shopping cart.
     */
    public void clearCart() {
        page.navigate("https://www.amazon.com/gp/cart/view.html?ref_=nav_cart");
        page.waitForTimeout(1000);
        Locator cartItems = page.locator("Input[data-feature-id='item-delete-button']");
        int itemCount = cartItems.count();
        for (int i = 0; i < itemCount; i++) {
            cartItems.first().click();
            page.waitForTimeout(1000);
            cartItems = page.locator("Input[data-feature-id='item-delete-button']");
        }
    }

    /**
     * Adds an item to the cart and returns cart information.
     * @param item The item to search for and add to cart
     * @return CartResult containing cart items and their prices
     */
    public CartResult addItemToCart(String item) {
        page.navigate("https://www.amazon.com");
        page.waitForTimeout(1000);
        Locator searchBox = page.locator("input#twotabsearchtextbox");
        if (!searchBox.isVisible()) {
            searchBox = page.locator("input#nav-bb-search");
        }
        searchBox.fill(item);
        searchBox.press("Enter");
        page.waitForSelector("div.s-main-slot");
        Locator sortDropdown = page.locator("select#s-result-sort-select");
        sortDropdown.selectOption("exact-aware-popularity-rank");
        page.waitForSelector("button[name='submit.addToCart']");
        Locator firstAddToCartButton = page.locator("button[name='submit.addToCart']").first();
        firstAddToCartButton.scrollIntoViewIfNeeded();
        page.waitForTimeout(4000);
        firstAddToCartButton.click();
        page.waitForTimeout(1000);
        Locator cartIcon = page.locator("#nav-cart");
        cartIcon.click();
        page.waitForTimeout(2000);
        Locator items = page.locator("#activeCartViewForm .sc-list-item-content");
        int itemCount = items.count();
        List<CartItem> cartItems = new ArrayList<>();
        for (int i = 0; i < itemCount; i++) {
            String priceText = items.nth(i).locator(".a-price").first().textContent().trim();
            String itemName = items.nth(i).locator(".a-truncate-full.a-offscreen").first().textContent().trim();
            String numericPrice = priceText.substring(1, priceText.indexOf("$", 1)).trim().replaceAll(",", "");
            CurrencyAmount price = null;
            try {
                double priceValue = Double.parseDouble(numericPrice);
                price = new CurrencyAmount(priceValue);
            } catch (Exception e) {
                price = null;
            }
            cartItems.add(new CartItem(itemName, price));
        }
        return new CartResult(cartItems);
    }

    /**
     * Represents a single item in the Amazon cart.
     */
    public static class CartItem {
        /** Name of the item. */
        public final String itemName;
        /** Price of the item as CurrencyAmount. */
        public final CurrencyAmount price;
        public CartItem(String itemName, CurrencyAmount price) {
            this.itemName = itemName;
            this.price = price;
        }
    }

    /**
     * Represents the result of adding an item to the cart.
     */
    public static class CartResult {
        /** List of items in the cart. */
        public final List<CartItem> items;
        public CartResult(List<CartItem> items) {
            this.items = items;
        }
    }
}