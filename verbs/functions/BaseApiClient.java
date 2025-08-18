import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

/**
 * Base HTTP client for REST API wrappers
 * Provides common HTTP functionality for making API requests
 */
public abstract class BaseApiClient {
    protected final HttpClient httpClient;
    protected final String userAgent;
    protected final String accessToken;
    
    public BaseApiClient(String userAgent) {
        this(userAgent, null);
    }
    
    public BaseApiClient(String userAgent, String accessToken) {
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(30))
                .build();
        this.userAgent = userAgent;
        this.accessToken = accessToken;
    }
      /**
     * Perform a GET request to the specified URL with automatic authentication
     * @param url The URL to request
     * @return The response body as a string
     * @throws IOException If the request fails
     * @throws InterruptedException If the request is interrupted
     */
    protected String performGet(String url) throws IOException, InterruptedException {
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("User-Agent", userAgent)
                .GET();
        
        // Add Authorization header if access token is available
        if (accessToken != null && !accessToken.isEmpty()) {
            requestBuilder.header("Authorization", "Bearer " + accessToken);
        }
        
        // Log the requested URL
        System.out.println("Performing GET request to: " + url);
        HttpRequest request = requestBuilder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
          if (response.statusCode() == 200) {
            return response.body();
        } else {
            // Handle 404 errors with warning instead of exception
            if (response.statusCode() == 404) {
                System.err.println("Warning: Resource not found (404) for URL: " + url);
                return null;
            }
            // If authentication fails, try unauthenticated request
            if (response.statusCode() == 403 && accessToken != null) {
                System.err.println("Warning: Authentication failed, falling back to unauthenticated request");
                return performGetUnauthenticated(url);
            }
            throw new IOException("HTTP " + response.statusCode() + ": " + response.body());
        }
    }
    
    /**
     * Perform an unauthenticated GET request
     * @param url The URL to request
     * @return The response body as a string
     * @throws IOException If the request fails
     * @throws InterruptedException If the request is interrupted
     */    private String performGetUnauthenticated(String url) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("User-Agent", userAgent)
                .GET()
                .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() == 200) {
            return response.body();
        } else {
            // Handle 404 errors with warning instead of exception
            if (response.statusCode() == 404) {
                System.err.println("Warning: Resource not found (404) for URL: " + url);
                return null;
            }
            throw new IOException("HTTP " + response.statusCode() + ": " + response.body());
        }
    }
    
    /**
     * Perform a GET request with GitHub-specific headers
     * @param url The URL to request
     * @return The response body as a string
     * @throws IOException If the request fails
     * @throws InterruptedException If the request is interrupted
     */
    protected String performGitHubGet(String url) throws IOException, InterruptedException {
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("User-Agent", userAgent)
                .header("Accept", "application/vnd.github+json")
                .header("X-GitHub-Api-Version", "2022-11-28")
                .GET();
          // Add Authorization header if access token is available
        if (accessToken != null && !accessToken.isEmpty()) {
            requestBuilder.header("Authorization", "Bearer " + accessToken);
        }
        
        HttpRequest request = requestBuilder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
          if (response.statusCode() == 200) {
            return response.body();
        } else {
            // Handle 404 errors with warning instead of exception
            if (response.statusCode() == 404) {
                System.err.println("Warning: Resource not found (404) for URL: " + url);
                return null;
            }
            throw new IOException("HTTP " + response.statusCode() + ": " + response.body());
        }
    }
    
    /**
     * Perform a GET request with Spotify-specific headers
     * @param url The URL to request
     * @return The response body as a string
     * @throws IOException If the request fails
     * @throws InterruptedException If the request is interrupted
     */
    protected String performSpotifyGet(String url) throws IOException, InterruptedException {
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("User-Agent", userAgent)
                .header("Accept", "application/json")
                .header("Content-Type", "application/json")
                .GET();
        
        // Add Authorization header if access token is available
        if (accessToken != null && !accessToken.isEmpty()) {
            requestBuilder.header("Authorization", "Bearer " + accessToken);
        }
        
        HttpRequest request = requestBuilder.build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
          if (response.statusCode() == 200) {
            return response.body();
        } else {
            // Handle 404 errors with warning instead of exception
            if (response.statusCode() == 404) {
                System.err.println("Warning: Resource not found (404) for URL: " + url);
                return null;
            }
            throw new IOException("HTTP " + response.statusCode() + ": " + response.body());
        }
    }
}
