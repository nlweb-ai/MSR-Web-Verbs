import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Spotify Web API client
 * Provides methods to interact with Spotify's Web API for search operations
 */
public class Spotify extends BaseApiClient {
    
    /**
     * Represents a Spotify track with detailed information
     */
    public static class SpotifyTrack {
        public String id;
        public String name;
        public String uri;
        public List<String> artistNames;
        public String albumName;
        public LocalDate releaseDate;
        public Duration duration;
        public int popularity;
        public boolean explicit;
        public String previewUrl;
        
        public SpotifyTrack() {
            this.artistNames = new ArrayList<>();
        }
    }

    /**
     * Represents a Spotify artist with detailed information
     */
    public static class SpotifyArtist {
        public String id;
        public String name;
        public String uri;
        public List<String> genres;
        public int popularity;
        public int followers;
        public String imageUrl;
        
        public SpotifyArtist() {
            this.genres = new ArrayList<>();
        }
    }

    /**
     * Represents a Spotify album with detailed information
     */
    public static class SpotifyAlbum {
        public String id;
        public String name;
        public String uri;
        public List<String> artistNames;
        public LocalDate releaseDate;
        public int totalTracks;
        public String albumType;
        public String imageUrl;
        
        public SpotifyAlbum() {
            this.artistNames = new ArrayList<>();
        }
    }

    /**
     * Represents a Spotify playlist with detailed information
     */
    public static class SpotifyPlaylist {
        public String id;
        public String name;
        public String uri;
        public String description;
        public String ownerName;
        public int totalTracks;
        public boolean isPublic;
        public boolean collaborative;
        public String imageUrl;
        
        public SpotifyPlaylist() {
        }
    }

    /**
     * Represents the complete search results from Spotify API
     */
    public static class SpotifySearchResult {
        public List<SpotifyTrack> tracks;
        public List<SpotifyArtist> artists;
        public List<SpotifyAlbum> albums;
        public List<SpotifyPlaylist> playlists;
        public String errorMessage;
        
        public SpotifySearchResult() {
            this.tracks = new ArrayList<>();
            this.artists = new ArrayList<>();
            this.albums = new ArrayList<>();
            this.playlists = new ArrayList<>();
        }
    }
    
    private static final String BASE_URL = "https://api.spotify.com/v1";
    private static final String TOKEN_URL = "https://accounts.spotify.com/api/token";
    
    /**
     * Default constructor - automatically requests access token using client credentials
     */
    public Spotify() {
        super(ApiUtil.buildSpotifyUserAgent(), requestAccessToken());
    }
    
    /**
     * Constructor with explicit token (for testing or when you already have a token)
     * @param token Spotify access token
     */
    public Spotify(String token) {
        super(ApiUtil.buildSpotifyUserAgent(), token);
    }
    
    /**
     * Request an access token using the Client Credentials flow
     * @return Access token string, or null if request failed
     */
    private static String requestAccessToken() {
        try {
            String clientId = ApiUtil.loadEnvValue("SPOTIFY_CLIENT_ID");
            String clientSecret = ApiUtil.loadEnvValue("SPOTIFY_CLIENT_SECRET");
            
            if (clientId == null || clientSecret == null) {
                System.err.println("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env file");
                return null;
            }
            
            // Prepare the request body
            String requestBody = String.format("grant_type=client_credentials&client_id=%s&client_secret=%s",
                    ApiUtil.urlEncode(clientId), ApiUtil.urlEncode(clientSecret));
            
            // Create HTTP client and request
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(TOKEN_URL))
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                    .build();
            
            // Send request and get response
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                // Parse the access token from JSON response
                String responseBody = response.body();
                Pattern tokenPattern = Pattern.compile("\"access_token\"\\s*:\\s*\"([^\"]+)\"");
                Matcher matcher = tokenPattern.matcher(responseBody);
                
                if (matcher.find()) {
                    return matcher.group(1);
                } else {
                    System.err.println("Error: Could not parse access token from response");
                    return null;
                }
            } else {
                System.err.println("Error requesting Spotify access token: HTTP " + response.statusCode());
                System.err.println("Response: " + response.body());
                return null;
            }
            
        } catch (Exception e) {
            System.err.println("Error requesting Spotify access token: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Search for Spotify catalog items (albums, artists, playlists, tracks, shows, episodes, audiobooks)
     * @param query Search query string - the search terms to look for
     * @param type Comma-separated list of item types to search across (album, artist, playlist, track, show, episode, audiobook)
     * @param market ISO 3166-1 alpha-2 country code for regional content filtering (optional)
     * @param limit Maximum number of results to return in each item type (0-50, default: 20)
     * @param offset Index of first result to return for pagination (0-1000, default: 0)
     * @param includeExternal Whether to include externally hosted audio content like podcasts (optional)
     * @return SpotifySearchResult containing parsed search results with tracks, artists, albums, and playlists
     */    
    public SpotifySearchResult searchItems(String query, String type, String market, Integer limit, 
                                          Integer offset, String includeExternal) {
        SpotifySearchResult result = new SpotifySearchResult();
        
        // Check for valid access token first
        if (accessToken == null || accessToken.isEmpty()) {
            result.errorMessage = "Error: Spotify access token is required for API access";
            return result;
        }
        
        try {
            // Build URL with query parameters
            StringBuilder urlBuilder = new StringBuilder(BASE_URL + "/search");
            List<String> queryParams = new ArrayList<>();
            
            // Required parameters
            if (query == null || query.isEmpty()) {
                result.errorMessage = "Error: Query parameter is required";
                return result;
            }
            queryParams.add("q=" + ApiUtil.urlEncode(query));
            
            if (type == null || type.isEmpty()) {
                result.errorMessage = "Error: Type parameter is required";
                return result;
            }
            queryParams.add("type=" + type);
            
            // Optional parameters
            if (market != null && !market.isEmpty()) {
                queryParams.add("market=" + market);
            }
            if (limit != null) {
                queryParams.add("limit=" + limit);
            }
            if (offset != null) {
                queryParams.add("offset=" + offset);
            }
            if (includeExternal != null && !includeExternal.isEmpty()) {
                queryParams.add("include_external=" + includeExternal);
            }
            
            if (!queryParams.isEmpty()) {
                urlBuilder.append("?").append(String.join("&", queryParams));
            }
            
            // Use base client's performSpotifyGet method
            String responseBody = performSpotifyGet(urlBuilder.toString());
            return parseSpotifySearchResponse(responseBody);
            
        } catch (IOException | InterruptedException e) {
            result.errorMessage = "Error occurred while searching Spotify: " + e.getMessage();
            return result;
        }
    }
    
    /**
     * Parse Spotify search response JSON into structured objects
     * @param jsonResponse The JSON response from Spotify API
     * @return SpotifySearchResult containing parsed data
     */
    private SpotifySearchResult parseSpotifySearchResponse(String jsonResponse) {
        SpotifySearchResult result = new SpotifySearchResult();
        
        if (jsonResponse == null || jsonResponse.isEmpty()) {
            result.errorMessage = "Empty response from Spotify API";
            return result;
        }
        
        try {
            // Parse tracks
            Pattern tracksPattern = Pattern.compile("\"tracks\"\\s*:\\s*\\{[^}]*\"items\"\\s*:\\s*\\[([^\\]]+)\\]");
            Matcher tracksMatcher = tracksPattern.matcher(jsonResponse);
            
            if (tracksMatcher.find()) {
                String tracksSection = tracksMatcher.group(1);
                result.tracks = parseSpotifyTracks(tracksSection);
            }
            
            // Parse artists
            Pattern artistsPattern = Pattern.compile("\"artists\"\\s*:\\s*\\{[^}]*\"items\"\\s*:\\s*\\[([^\\]]+)\\]");
            Matcher artistsMatcher = artistsPattern.matcher(jsonResponse);
            
            if (artistsMatcher.find()) {
                String artistsSection = artistsMatcher.group(1);
                result.artists = parseSpotifyArtists(artistsSection);
            }
            
            // Parse albums
            Pattern albumsPattern = Pattern.compile("\"albums\"\\s*:\\s*\\{[^}]*\"items\"\\s*:\\s*\\[([^\\]]+)\\]");
            Matcher albumsMatcher = albumsPattern.matcher(jsonResponse);
            
            if (albumsMatcher.find()) {
                String albumsSection = albumsMatcher.group(1);
                result.albums = parseSpotifyAlbums(albumsSection);
            }
            
            // Parse playlists
            Pattern playlistsPattern = Pattern.compile("\"playlists\"\\s*:\\s*\\{[^}]*\"items\"\\s*:\\s*\\[([^\\]]+)\\]");
            Matcher playlistsMatcher = playlistsPattern.matcher(jsonResponse);
            
            if (playlistsMatcher.find()) {
                String playlistsSection = playlistsMatcher.group(1);
                result.playlists = parseSpotifyPlaylists(playlistsSection);
            }
            
        } catch (Exception e) {
            result.errorMessage = "Error parsing Spotify response: " + e.getMessage();
        }
        
        return result;
    }
    
    /**
     * Parse individual Spotify tracks from JSON items section
     * @param itemsSection JSON section containing track items
     * @return List of SpotifyTrack objects
     */
    private List<SpotifyTrack> parseSpotifyTracks(String itemsSection) {
        List<SpotifyTrack> tracks = new ArrayList<>();
        String[] items = itemsSection.split("\\},\\s*\\{");
        
        for (int i = 0; i < Math.min(items.length, 10); i++) {
            String item = items[i];
            SpotifyTrack track = new SpotifyTrack();
            
            track.id = extractJsonValue(item, "id");
            track.name = extractJsonValue(item, "name");
            track.uri = extractJsonValue(item, "uri");
            track.previewUrl = extractJsonValue(item, "preview_url");
            
            String popularityStr = extractJsonValue(item, "popularity");
            if (popularityStr != null && !popularityStr.isEmpty()) {
                try {
                    track.popularity = Integer.parseInt(popularityStr);
                } catch (NumberFormatException e) {
                    track.popularity = 0;
                }
            }
            
            String explicitStr = extractJsonValue(item, "explicit");
            track.explicit = "true".equals(explicitStr);
            
            // Parse duration (in milliseconds)
            String durationStr = extractJsonValue(item, "duration_ms");
            if (durationStr != null && !durationStr.isEmpty()) {
                try {
                    long durationMs = Long.parseLong(durationStr);
                    track.duration = Duration.ofMillis(durationMs);
                } catch (NumberFormatException e) {
                    track.duration = Duration.ZERO;
                }
            } else {
                track.duration = Duration.ZERO;
            }
            
            // Parse artist names
            Pattern artistPattern = Pattern.compile("\"artists\"[^\\]]*\"name\"\\s*:\\s*\"([^\"]+)\"");
            Matcher artistMatcher = artistPattern.matcher(item);
            while (artistMatcher.find()) {
                track.artistNames.add(artistMatcher.group(1));
            }
            
            // Parse album info
            Pattern albumPattern = Pattern.compile("\"album\"[^}]*\"name\"\\s*:\\s*\"([^\"]+)\"");
            Matcher albumMatcher = albumPattern.matcher(item);
            if (albumMatcher.find()) {
                track.albumName = albumMatcher.group(1);
            }
            
            // Parse release date
            String releaseDateStr = extractJsonValue(item, "release_date");
            if (releaseDateStr != null && releaseDateStr.length() >= 4) {
                try {
                    if (releaseDateStr.length() == 4) {
                        // Year only
                        track.releaseDate = LocalDate.of(Integer.parseInt(releaseDateStr), 1, 1);
                    } else if (releaseDateStr.length() == 10) {
                        // Full date YYYY-MM-DD
                        track.releaseDate = LocalDate.parse(releaseDateStr);
                    }
                } catch (Exception e) {
                    // If parsing fails, leave as null
                }
            }
            
            tracks.add(track);
        }
        
        return tracks;
    }
    
    /**
     * Parse individual Spotify artists from JSON items section
     * @param itemsSection JSON section containing artist items
     * @return List of SpotifyArtist objects
     */
    private List<SpotifyArtist> parseSpotifyArtists(String itemsSection) {
        List<SpotifyArtist> artists = new ArrayList<>();
        String[] items = itemsSection.split("\\},\\s*\\{");
        
        for (int i = 0; i < Math.min(items.length, 10); i++) {
            String item = items[i];
            SpotifyArtist artist = new SpotifyArtist();
            
            artist.id = extractJsonValue(item, "id");
            artist.name = extractJsonValue(item, "name");
            artist.uri = extractJsonValue(item, "uri");
            
            String popularityStr = extractJsonValue(item, "popularity");
            if (popularityStr != null && !popularityStr.isEmpty()) {
                try {
                    artist.popularity = Integer.parseInt(popularityStr);
                } catch (NumberFormatException e) {
                    artist.popularity = 0;
                }
            }
            
            // Parse follower count
            Pattern followersPattern = Pattern.compile("\"followers\"[^}]*\"total\"\\s*:\\s*(\\d+)");
            Matcher followersMatcher = followersPattern.matcher(item);
            if (followersMatcher.find()) {
                try {
                    artist.followers = Integer.parseInt(followersMatcher.group(1));
                } catch (NumberFormatException e) {
                    artist.followers = 0;
                }
            }
            
            // Parse genres
            Pattern genrePattern = Pattern.compile("\"genres\"\\s*:\\s*\\[([^\\]]+)\\]");
            Matcher genreMatcher = genrePattern.matcher(item);
            if (genreMatcher.find()) {
                String genresStr = genreMatcher.group(1);
                Pattern genreItemPattern = Pattern.compile("\"([^\"]+)\"");
                Matcher genreItemMatcher = genreItemPattern.matcher(genresStr);
                while (genreItemMatcher.find()) {
                    artist.genres.add(genreItemMatcher.group(1));
                }
            }
            
            // Parse image URL (get first/largest image)
            Pattern imagePattern = Pattern.compile("\"images\"[^\\]]*\"url\"\\s*:\\s*\"([^\"]+)\"");
            Matcher imageMatcher = imagePattern.matcher(item);
            if (imageMatcher.find()) {
                artist.imageUrl = imageMatcher.group(1);
            }
            
            artists.add(artist);
        }
        
        return artists;
    }
    
    /**
     * Parse individual Spotify albums from JSON items section
     * @param itemsSection JSON section containing album items
     * @return List of SpotifyAlbum objects
     */
    private List<SpotifyAlbum> parseSpotifyAlbums(String itemsSection) {
        List<SpotifyAlbum> albums = new ArrayList<>();
        String[] items = itemsSection.split("\\},\\s*\\{");
        
        for (int i = 0; i < Math.min(items.length, 10); i++) {
            String item = items[i];
            SpotifyAlbum album = new SpotifyAlbum();
            
            album.id = extractJsonValue(item, "id");
            album.name = extractJsonValue(item, "name");
            album.uri = extractJsonValue(item, "uri");
            album.albumType = extractJsonValue(item, "album_type");
            
            String totalTracksStr = extractJsonValue(item, "total_tracks");
            if (totalTracksStr != null && !totalTracksStr.isEmpty()) {
                try {
                    album.totalTracks = Integer.parseInt(totalTracksStr);
                } catch (NumberFormatException e) {
                    album.totalTracks = 0;
                }
            }
            
            // Parse artist names
            Pattern artistPattern = Pattern.compile("\"artists\"[^\\]]*\"name\"\\s*:\\s*\"([^\"]+)\"");
            Matcher artistMatcher = artistPattern.matcher(item);
            while (artistMatcher.find()) {
                album.artistNames.add(artistMatcher.group(1));
            }
            
            // Parse release date
            String releaseDateStr = extractJsonValue(item, "release_date");
            if (releaseDateStr != null && releaseDateStr.length() >= 4) {
                try {
                    if (releaseDateStr.length() == 4) {
                        // Year only
                        album.releaseDate = LocalDate.of(Integer.parseInt(releaseDateStr), 1, 1);
                    } else if (releaseDateStr.length() == 10) {
                        // Full date YYYY-MM-DD
                        album.releaseDate = LocalDate.parse(releaseDateStr);
                    }
                } catch (Exception e) {
                    // If parsing fails, leave as null
                }
            }
            
            // Parse image URL (get first/largest image)
            Pattern imagePattern = Pattern.compile("\"images\"[^\\]]*\"url\"\\s*:\\s*\"([^\"]+)\"");
            Matcher imageMatcher = imagePattern.matcher(item);
            if (imageMatcher.find()) {
                album.imageUrl = imageMatcher.group(1);
            }
            
            albums.add(album);
        }
        
        return albums;
    }
    
    /**
     * Parse individual Spotify playlists from JSON items section
     * @param itemsSection JSON section containing playlist items
     * @return List of SpotifyPlaylist objects
     */
    private List<SpotifyPlaylist> parseSpotifyPlaylists(String itemsSection) {
        List<SpotifyPlaylist> playlists = new ArrayList<>();
        String[] items = itemsSection.split("\\},\\s*\\{");
        
        for (int i = 0; i < Math.min(items.length, 10); i++) {
            String item = items[i];
            SpotifyPlaylist playlist = new SpotifyPlaylist();
            
            playlist.id = extractJsonValue(item, "id");
            playlist.name = extractJsonValue(item, "name");
            playlist.uri = extractJsonValue(item, "uri");
            playlist.description = extractJsonValue(item, "description");
            
            // Parse owner info
            Pattern ownerPattern = Pattern.compile("\"owner\"[^}]*\"display_name\"\\s*:\\s*\"([^\"]+)\"");
            Matcher ownerMatcher = ownerPattern.matcher(item);
            if (ownerMatcher.find()) {
                playlist.ownerName = ownerMatcher.group(1);
            }
            
            // Parse track count
            Pattern tracksPattern = Pattern.compile("\"tracks\"[^}]*\"total\"\\s*:\\s*(\\d+)");
            Matcher tracksMatcher = tracksPattern.matcher(item);
            if (tracksMatcher.find()) {
                try {
                    playlist.totalTracks = Integer.parseInt(tracksMatcher.group(1));
                } catch (NumberFormatException e) {
                    playlist.totalTracks = 0;
                }
            }
            
            String publicStr = extractJsonValue(item, "public");
            playlist.isPublic = "true".equals(publicStr);
            
            String collaborativeStr = extractJsonValue(item, "collaborative");
            playlist.collaborative = "true".equals(collaborativeStr);
            
            // Parse image URL (get first/largest image)
            Pattern imagePattern = Pattern.compile("\"images\"[^\\]]*\"url\"\\s*:\\s*\"([^\"]+)\"");
            Matcher imageMatcher = imagePattern.matcher(item);
            if (imageMatcher.find()) {
                playlist.imageUrl = imageMatcher.group(1);
            }
            
            playlists.add(playlist);
        }
        
        return playlists;
    }
    
    /**
     * Helper method to extract a JSON field value using regex
     * @param json JSON string
     * @param key Field key to extract
     * @return Field value or null if not found
     */
    private String extractJsonValue(String json, String key) {
        Pattern pattern = Pattern.compile("\"" + key + "\"\\s*:\\s*\"([^\"]+)\"");
        Matcher matcher = pattern.matcher(json);
        if (matcher.find()) {
            return matcher.group(1);
        }
        
        // Also try without quotes for numeric/boolean values
        Pattern numPattern = Pattern.compile("\"" + key + "\"\\s*:\\s*([^,}\\]]+)");
        Matcher numMatcher = numPattern.matcher(json);
        if (numMatcher.find()) {
            return numMatcher.group(1).trim();
        }
        
        return null;
    }
    
    /**
     * Search for tracks only with detailed filtering options
     * @param query Search query string - the search terms to look for
     * @param market ISO 3166-1 alpha-2 country code for regional content filtering (optional)
     * @param limit Maximum number of track results to return (0-50, default: 20)
     * @return List of SpotifyTrack objects containing track details
     */
    public List<SpotifyTrack> searchTracks(String query, String market, Integer limit) {
        SpotifySearchResult result = searchItems(query, "track", market, limit, null, null);
        return result.tracks;
    }
    
    /**
     * Search for artists only with detailed filtering options
     * @param query Search query string - the search terms to look for
     * @param market ISO 3166-1 alpha-2 country code for regional content filtering (optional)
     * @param limit Maximum number of artist results to return (0-50, default: 20)
     * @return List of SpotifyArtist objects containing artist details
     */
    public List<SpotifyArtist> searchArtists(String query, String market, Integer limit) {
        SpotifySearchResult result = searchItems(query, "artist", market, limit, null, null);
        return result.artists;
    }
    
    /**
     * Search for albums only with detailed filtering options
     * @param query Search query string - the search terms to look for
     * @param market ISO 3166-1 alpha-2 country code for regional content filtering (optional)
     * @param limit Maximum number of album results to return (0-50, default: 20)
     * @return List of SpotifyAlbum objects containing album details
     */
    public List<SpotifyAlbum> searchAlbums(String query, String market, Integer limit) {
        SpotifySearchResult result = searchItems(query, "album", market, limit, null, null);
        return result.albums;
    }
    
    /**
     * Search for playlists only with detailed filtering options
     * @param query Search query string - the search terms to look for
     * @param market ISO 3166-1 alpha-2 country code for regional content filtering (optional)
     * @param limit Maximum number of playlist results to return (0-50, default: 20)
     * @return List of SpotifyPlaylist objects containing playlist details
     */
    public List<SpotifyPlaylist> searchPlaylists(String query, String market, Integer limit) {
        SpotifySearchResult result = searchItems(query, "playlist", market, limit, null, null);
        return result.playlists;
    }
    
    /**
     * Search with simple query and type combination
     * @param query Search query string - the search terms to look for
     * @param type Item type to search for (track, artist, album, playlist, or combinations)
     * @return SpotifySearchResult containing all matching content types
     */
    public SpotifySearchResult search(String query, String type) {
        return searchItems(query, type, null, null, null, null);
    }
    
    /**
     * Convenience method for basic track search - searches for tracks with default settings
     * @param query Search query string - the search terms to look for
     * @return List of SpotifyTrack objects containing track details
     */
    public List<SpotifyTrack> searchTracks(String query) {
        return searchTracks(query, null, null);
    }
    
    /**
     * Convenience method for basic artist search - searches for artists with default settings
     * @param query Search query string - the search terms to look for
     * @return List of SpotifyArtist objects containing artist details
     */
    public List<SpotifyArtist> searchArtists(String query) {
        return searchArtists(query, null, null);
    }
    
    /**
     * Convenience method for basic album search - searches for albums with default settings
     * @param query Search query string - the search terms to look for
     * @return List of SpotifyAlbum objects containing album details
     */
    public List<SpotifyAlbum> searchAlbums(String query) {
        return searchAlbums(query, null, null);
    }
}
