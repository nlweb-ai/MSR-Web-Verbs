## This demo 

There are four types of files in this folder

### task-xxxx.md

* task-0001.md is the initial vague task description.
* task-0002.md is the result of the first round refinement. The user adds *"Since the museums are already selected, I want to select the hotel which has the smallest total distance to all the museums."* into the task. 
* task-0003.md is the result of the second round refinement. The user adds *"One more thing: we want to see kids winter jackets in the Anchorage costco. Please get a list of the jackets."* into the task. 
* task-0004.md is the result of the third round refinement. The user adds *"Finally, please create a google maps list named "Anchorage 2025" (if there is an existing list with the same name, please delete it first). Please add the anchorage airport, the selected hotel and the museums into this list. When it is done, compose a nicely-formatted itinerary and send it to johndoe@contoso.com using Microsoft Teams."* into the task. 

### known_facts.md
* Each Java program execution (each refinement) adds new facts into this file.

### prompt_refine_*.md
* prompt_refine_code.md is the prompt to generate Java code.
* prompt_refine_description.md is the prompt to generate the next round task description.

### strategy-xxxx.md
* These files are generated with the Java files. They help understand the code, but not essential to the workflow.

