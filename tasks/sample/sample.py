"""
Sample task – Python equivalent of generated_solutions/Task0000.java
Sends a Teams message using the verbs Teams verb with a persistent Chrome profile.
"""

import os
import sys
import json

# Add verbs to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))

from playwright.sync_api import sync_playwright
from teams_microsoft_com.teams_send_message import send_teams_message, TeamsMessageRequest


def automate(page):
    request = TeamsMessageRequest(
        recipient="johndoe@contoso.com",
        message="hello"
    )
    result = send_teams_message(page, request)
    return {
        "recipient": result.recipient,
        "message": result.message,
        "success": result.success,
    }


def main():
    user_data_dir = os.path.join(
        os.environ["LOCALAPPDATA"],
        "Google", "Chrome", "User Data", "Default"
    )

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = automate(page)
            print("Final output:", json.dumps(result, indent=2, ensure_ascii=False))
        finally:
            context.close()


if __name__ == "__main__":
    main()
