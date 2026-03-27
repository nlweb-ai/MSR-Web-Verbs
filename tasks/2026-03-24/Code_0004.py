import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
# The maps_google_com__createList folder contains maps_createList.py
from maps_google_com__createList.maps_createList import create_saved_list, CreateListRequest
def automate(page):
    # task-0004.md specifies creating a Google Maps saved list "CVS Stores Bellevue"
    # with the 5 CVS store addresses already identified in prior rounds
    # (documented in known_facts.md and task-0004.md "Already Known" section).
    # Place strings match exactly what was specified in the
    # "Step: Add CVS Stores to Google Maps List" block of task-0004.md.
    request = CreateListRequest(
        list_name="CVS Stores Bellevue",
        places=[
            "CVS 10116 NE 8th St, Bellevue, WA 98004",
            "CVS 107 Bellevue Way SE, Bellevue, WA 98004",
            "CVS 653 156th Ave NE, Bellevue, WA 98007",
            "CVS 3023 78th Ave SE, Mercer Island, WA 98040",
            "CVS 10625 NE 68th St, Kirkland, WA 98033",
        ]
    )
    result = create_saved_list(page, request)
    output = {
        "action": "create_google_maps_list",
        "date": "2026-03-27",
        "list_name": result.list_name,
        "places_added": result.places_added,
        "success": result.success,
    }
    # Append the result to known_facts.md so future rounds can reference it
    known_facts_path = os.path.join(os.path.dirname(__file__), "known_facts.md")
    with open(known_facts_path, "a", encoding="utf-8") as f:
        f.write("\n## Google Maps List: CVS Stores Bellevue (created 2026-03-27)\n\n")
        f.write(f"- List name: {result.list_name}\n")
        f.write(f"- Success: {result.success}\n")
        f.write("- Places added:\n")
        for place in result.places_added:
            f.write(f"  - {place}\n")
        f.write("\n```json\n")
        f.write(json.dumps(output, indent=2, ensure_ascii=False))
        f.write("\n```\n")
    return output