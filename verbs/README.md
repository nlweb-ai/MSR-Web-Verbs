## Web verbs 

This document describes (1) how to run the existing solutions that are composed by the existing verbs, (2) how to generate new tasks and their solutions that are composed by the existing verbs, (3) how to generate new verbs.

### How to run the existing solutions

1. Install Visual Studio Code (VS Code) from [here](https://code.visualstudio.com/download).
2. Install Oracle JDK from [here](https://www.oracle.com/java/technologies/downloads/#jdk24-windows)
3. In VS Code, go to the Extensions view (Ctrl+Shift+X). Search for and install "Extension Pack for Java (by Microsoft)"


This repository contains prototypes to show a potential path for developers to build an agent-operable World Wide Web.

Today, a user performs an operation on the web by making a web-API call or interacting with a sequence of HTML elements using a browser. Imagine that developers can wrap these web APIs and browser interactions into functions (which we call "web verbs") and ingest these functions in NLWeb's vector database. This will pave a promising path toward a realistic agentic web because every user task becomes a coding task, which LLMs are very good at.

## A video demo
To show this vision, we have implemented 50 web verbs across various websites as Java functions. Using the agent mode in VS Code, we let the agent generate a solution according to the following description. The video shows the execution result.

<small>

```
Search for hotels in Paris on booking.com for the dates 2025-09-10 to 2025-09-15.  
Find a list of top-rated hotels.

Select the third cheapest hotel from the list, output its price and its hotel information. 

Find the distance to the Eiffel Tower: calculate the distance from the hotel's address to the Eiffel Tower.

Then, go to amazon.com and search for a travel adapter suitable for the country of the hotel’s address.  
Add the top-rated travel adapter to the Amazon shopping cart.  

Print the hotel name, distance to the Eiffel Tower, and the price of the travel adapter.

Also, send a Microsoft Teams message to john@foo.com that contains the printed information.
```
</small>

<a href="https://www.youtube.com/watch?v=ofbcKK8sMaA">
<img src="resources/img/videoThumbnail.jpg" alt="Demo of an NL task" width="400">
</a>

## The vision
We want to inspire developers to wrap the whole web as a gigantic set of web verbs. A similar industry-wide effort happened before -- the web used to be accessed by browsers only, but in the mobile computing revolution, the web was purposefully "wrapped" for mobile apps. Today, we wish the web to be operable by agents. Let's purposefully wrap it as web verbs.  

## About this repository
Currently we have three early prototypes:

1. Our extension to NLWeb's db_load functionality. It ingests web verbs into the vector database. Please see [this instruction](verb_ingress/README.md). 
2. A set of 50 implemented verbs and a set of 100 tasks, each similar to the one shown above in the video. The agent successfully composes the verbs to fulfill all the tasks. The solutions are also contained in this repo. (To be added to this repo soon.)
3. A tool for developers to wrap a browser-interaction sequence into a verb. (To be added to this repo later.)  



