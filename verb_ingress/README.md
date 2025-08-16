## Web verbs (as Java functions) => Vector Database

This folder implements two functionalities: (1) ingesting web verbs into the vector DB; (2) retrieving a list of ranked web verbs according to a natural language task description. It calls the code in the NLWeb repo.

### Setting up the NLWeb repo
1. Follow [the steps](https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-hello-world.md?plain=1) described in the NLWeb repo.
2. Once all steps succeed, delete the ingested contents.
   ```sh
   python -m data_loading.db_load Behind-the-Tech --only-delete
   python -m data_loading.db_load Decoder --only-delete
   ```

### Cloning the MSR-Web-Verbs repo
```sh
git clone https://github.com/nlweb-ai/MSR-Web-Verbs.git
cd MSR-Web-Verbs
pip install -r verb_ingress/requirements.txt
```

If the root dir of the NLWeb repo is d:\repos\NLWeb, set the dir in the **`.env`** file:

```env
NLWEB_ROOT=d:\repos\NLWeb
```
### Ingesting the interface files (*.itfc) 

Run the following commands. 
```sh
python -m verb_ingress.db_load verbs/interfaces/alaskaair_com.itfc alaskaair_com-api
python -m verb_ingress.db_load verbs/interfaces/amazon_com.itfc amazon_com-api
python -m verb_ingress.db_load verbs/interfaces/booking_com.itfc booking_com-api
python -m verb_ingress.db_load verbs/interfaces/costco_com.itfc costco_com-api
python -m verb_ingress.db_load verbs/interfaces/Wikimedia.itfc wikimedia-api
python -m verb_ingress.db_load verbs/interfaces/maps_google_com.itfc maps_google_com-api
python -m verb_ingress.db_load verbs/interfaces/Nasa.itfc Nasa-api
python -m verb_ingress.db_load verbs/interfaces/News.itfc News-api
python -m verb_ingress.db_load verbs/interfaces/OpenLibrary.itfc OpenLibrary-api
python -m verb_ingress.db_load verbs/interfaces/OpenWeather.itfc OpenWeather-api
python -m verb_ingress.db_load verbs/interfaces/redfin_com.itfc redfin_com-api
python -m verb_ingress.db_load verbs/interfaces/Spotify.itfc Spotify-api
python -m verb_ingress.db_load verbs/interfaces/teams_microsoft_com.itfc teams_microsoft_com-api
python -m verb_ingress.db_load verbs/interfaces/youtube_com.itfc youtube_com-api
```

### Retrieving the ranked list of verbs  
The following command retrieves a maximal number of 20 verbs from the vector database based on an NL description. 
```sh
python -m verb_ingress.cli_app -q "1. Search for hotels in Paris for the dates 2025-07-10 to 2025-07-15.  Find a list of top-rated hotels. 2. Find the direction to the Eiffel Tower. 3. On Amazon, buy a travel adaptor for France. 4. Send a Microsoft Teams message to foo@bar.com that contains the hotel and the purchase information."  --num-results 20
```
(Note: The current code is a proof-of-concept about the ingestion functionality. We haven't tuned the algorithm to optimize the ranking result.)


