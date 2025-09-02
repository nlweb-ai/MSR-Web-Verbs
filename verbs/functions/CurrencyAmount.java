/**
 * Represents a currency amount with a currency code and a two-decimal fixed-point value.
 */
public class CurrencyAmount {
    /** Currency code, default is "USD". */
    public String currency = "USD";
    /** Amount as a two-decimal fixed-point number. */
    public double amount;

    /**
     * Constructs a CurrencyAmount with default currency (USD) and amount 0.00.
     */
    public CurrencyAmount() {
        this.amount = 0.00;
    }

    /**
     * Constructs a CurrencyAmount with specified amount and default currency (USD).
     * @param amount The amount value (will be rounded to two decimals)
     */
    public CurrencyAmount(double amount) {
        this.amount = Math.round(amount * 100.0) / 100.0;
    }

    /**
     * Constructs a CurrencyAmount with specified currency and amount.
     * @param currency The currency code
     * @param amount The amount value (will be rounded to two decimals)
     */
    public CurrencyAmount(String currency, double amount) {
        this.currency = currency;
        this.amount = Math.round(amount * 100.0) / 100.0;
    }

    /**
     * Returns a string representation of the currency amount in the format "amount currency".
     * For example: "1234.00 USD" or "99.99 EUR"
     * @return String representation of the currency amount
     */
    @Override
    public String toString() {
        return String.format("%.2f %s", amount, currency);
    }
}
