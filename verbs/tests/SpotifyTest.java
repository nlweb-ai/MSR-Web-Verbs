import java.util.List;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the Spotify API wrapper
 */
public class SpotifyTest {
    private Spotify spotify;

    @BeforeEach
    void setUp() {
        spotify = new Spotify(); // Uses client credentials from .env file
    }

    @Test
    @DisplayName("Test searching for tracks and artists")
    void testSearchTracksAndArtists() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("The Beatles", "track,artist", null, 5, 0, null);
        
        assertNotNull(results, "Results should not be null");
        assertNull(results.errorMessage, "Should not have error message");
        
        // Check that results contain tracks and/or artists
        boolean hasTracks = !results.tracks.isEmpty();
        boolean hasArtists = !results.artists.isEmpty();
        
        assertTrue(hasTracks || hasArtists, "Should contain tracks or artists");
        
        System.out.println("Found Beatles search results:");
        System.out.println("Tracks: " + results.tracks.size());
        for (Spotify.SpotifyTrack track : results.tracks) {
            System.out.println("- " + track.name + " by " + String.join(", ", track.artistNames));
        }
        System.out.println("Artists: " + results.artists.size());
        for (Spotify.SpotifyArtist artist : results.artists) {
            System.out.println("- " + artist.name + " (popularity: " + artist.popularity + ")");
        }
    }    @Test
    @DisplayName("Test search tracks convenience method")
    void testSearchTracks() throws Exception {
        List<Spotify.SpotifyTrack> results = spotify.searchTracks("Hotel California", null, 3);
        
        assertNotNull(results, "Results list should not be null");
        assertFalse(results.isEmpty(), "Should find at least one track");
        
        System.out.println("Found Hotel California tracks:");
        for (Spotify.SpotifyTrack track : results) {
            System.out.println("- " + track.name + " by " + String.join(", ", track.artistNames) 
                + " (Duration: " + track.duration.toMinutes() + ":" + 
                String.format("%02d", track.duration.toSecondsPart()) + ")");
        }
    }

    @Test
    @DisplayName("Test search artists convenience method")
    void testSearchArtists() throws Exception {
        List<Spotify.SpotifyArtist> results = spotify.searchArtists("Queen", null, 3);
        
        assertNotNull(results, "Results list should not be null");
        assertFalse(results.isEmpty(), "Should find at least one artist");
        
        System.out.println("Found Queen artists:");
        for (Spotify.SpotifyArtist artist : results) {
            System.out.println("- " + artist.name + " (Popularity: " + artist.popularity + 
                ", Followers: " + artist.followers + ")");
            if (!artist.genres.isEmpty()) {
                System.out.println("  Genres: " + String.join(", ", artist.genres));
            }
        }
    }

    @Test
    @DisplayName("Test search albums convenience method")
    void testSearchAlbums() throws Exception {
        List<Spotify.SpotifyAlbum> results = spotify.searchAlbums("Abbey Road", null, 3);
        
        assertNotNull(results, "Results list should not be null");
        assertFalse(results.isEmpty(), "Should find at least one album");
        
        System.out.println("Found Abbey Road albums:");
        for (Spotify.SpotifyAlbum album : results) {
            System.out.println("- " + album.name + " by " + String.join(", ", album.artistNames) +
                " (" + album.totalTracks + " tracks)");
            if (album.releaseDate != null) {
                System.out.println("  Released: " + album.releaseDate);
            }
        }
    }

    @Test
    @DisplayName("Test search playlists convenience method")
    void testSearchPlaylists() throws Exception {
        List<Spotify.SpotifyPlaylist> results = spotify.searchPlaylists("Top Hits", null, 3);
        
        assertNotNull(results, "Results list should not be null");
        assertFalse(results.isEmpty(), "Should find at least one playlist");
        
        System.out.println("Found Top Hits playlists:");
        for (Spotify.SpotifyPlaylist playlist : results) {
            System.out.println("- " + playlist.name + " by " + playlist.ownerName +
                " (" + playlist.totalTracks + " tracks)");
            if (playlist.description != null && !playlist.description.isEmpty()) {
                System.out.println("  Description: " + playlist.description);
            }
        }
    }

    @Test
    @DisplayName("Test simple search convenience method")
    void testSimpleSearch() throws Exception {
        Spotify.SpotifySearchResult results = spotify.search("Taylor Swift", "track,artist");
        
        assertNotNull(results, "Results should not be null");
        assertNull(results.errorMessage, "Should not have error message");
        
        boolean hasTracks = !results.tracks.isEmpty();
        boolean hasArtists = !results.artists.isEmpty();
        assertTrue(hasTracks || hasArtists, "Should find tracks or artists for Taylor Swift");
        
        System.out.println("Found Taylor Swift search results:");
        System.out.println("Tracks: " + results.tracks.size());
        System.out.println("Artists: " + results.artists.size());
    }

    @Test
    @DisplayName("Test search with market parameter")
    void testSearchWithMarket() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("Coldplay", "track", "US", 5, 0, null);
        
        assertNotNull(results, "Results should not be null");
        assertNull(results.errorMessage, "Should not have error message");
        assertFalse(results.tracks.isEmpty(), "Should find at least one result for Coldplay");
        
        System.out.println("Found Coldplay tracks in US market:");
        for (Spotify.SpotifyTrack track : results.tracks) {
            System.out.println("- " + track.name + " by " + String.join(", ", track.artistNames));
        }
    }

    @Test
    @DisplayName("Test search with offset parameter")
    void testSearchWithOffset() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("Rock", "track", null, 3, 5, null);
        
        assertNotNull(results, "Results should not be null");
        assertNull(results.errorMessage, "Should not have error message");
        // Note: Results might be empty if offset is beyond available results
        
        System.out.println("Found Rock tracks with offset 5:");
        System.out.println("Track count: " + results.tracks.size());
        for (Spotify.SpotifyTrack track : results.tracks) {
            System.out.println("- " + track.name);
        }
    }

    @Test
    @DisplayName("Test search with external content inclusion")
    void testSearchWithExternalContent() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("Led Zeppelin", "track", null, 5, 0, "audio");
        
        assertNotNull(results, "Results should not be null");
        assertNull(results.errorMessage, "Should not have error message");
        assertFalse(results.tracks.isEmpty(), "Should find at least one result for Led Zeppelin");
        
        System.out.println("Found Led Zeppelin tracks with external audio:");
        for (Spotify.SpotifyTrack track : results.tracks) {
            System.out.println("- " + track.name + " (Explicit: " + track.explicit + ")");
        }
    }    @Test
    @DisplayName("Test search with empty query returns error")
    void testSearchWithEmptyQuery() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("", "track", null, 5, 0, null);
        
        assertNotNull(results, "Results should not be null");
        assertNotNull(results.errorMessage, "Should have error message");
        assertTrue(results.errorMessage.contains("Query parameter is required"), 
                   "Should return error about missing query parameter");
    }

    @Test
    @DisplayName("Test search with null query returns error")
    void testSearchWithNullQuery() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems(null, "track", null, 5, 0, null);
        
        assertNotNull(results, "Results should not be null");
        assertNotNull(results.errorMessage, "Should have error message");
        assertTrue(results.errorMessage.contains("Query parameter is required"), 
                   "Should return error about missing query parameter");
    }

    @Test
    @DisplayName("Test search with empty type returns error")
    void testSearchWithEmptyType() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("Beatles", "", null, 5, 0, null);
        
        assertNotNull(results, "Results should not be null");
        assertNotNull(results.errorMessage, "Should have error message");
        assertTrue(results.errorMessage.contains("Type parameter is required"), 
                   "Should return error about missing type parameter");
    }

    @Test
    @DisplayName("Test search with null type returns error")
    void testSearchWithNullType() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("Beatles", null, null, 5, 0, null);
        
        assertNotNull(results, "Results should not be null");
        assertNotNull(results.errorMessage, "Should have error message");
        assertTrue(results.errorMessage.contains("Type parameter is required"), 
                   "Should return error about missing type parameter");
    }

    @Test
    @DisplayName("Test search with negative limit")
    void testSearchWithNegativeLimit() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("Test", "track", null, -1, 0, null);
        
        assertNotNull(results, "Results should not be null");
        // The API should handle negative limits gracefully or use default
    }

    @Test
    @DisplayName("Test search with negative offset")
    void testSearchWithNegativeOffset() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("Test", "track", null, 5, -1, null);
        
        assertNotNull(results, "Results should not be null");
        // The API should handle negative offsets gracefully or use default
    }

    @Test
    @DisplayName("Test search with all types")
    void testSearchWithAllTypes() throws Exception {
        Spotify.SpotifySearchResult results = spotify.searchItems("Beatles", "album,artist,playlist,track", null, 2, 0, null);
        
        assertNotNull(results, "Results should not be null");
        assertNull(results.errorMessage, "Should not have error message");
        
        // Should contain multiple types of results
        int totalResults = results.tracks.size() + results.artists.size() + 
                          results.albums.size() + results.playlists.size();
        assertTrue(totalResults > 0, "Should find at least one result for Beatles");
        
        System.out.println("Found Beatles results for all types:");
        System.out.println("- Tracks: " + results.tracks.size());
        System.out.println("- Artists: " + results.artists.size());
        System.out.println("- Albums: " + results.albums.size());
        System.out.println("- Playlists: " + results.playlists.size());
        
        // Show some sample results
        if (!results.tracks.isEmpty()) {
            System.out.println("Sample track: " + results.tracks.get(0).name);
        }
        if (!results.artists.isEmpty()) {
            System.out.println("Sample artist: " + results.artists.get(0).name);
        }
        if (!results.albums.isEmpty()) {
            System.out.println("Sample album: " + results.albums.get(0).name);
        }
    }
}
