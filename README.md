# JobAppsMailTracker - Gmail Job Application Tracking Script

## Project Goal

The ultimate goal of this project is to create a Python script that automates the tracking of job applications by:

1. Connecting securely to a user's Gmail account.
2. Identifying emails related to job applications (using a specific Gmail label).
3. Extracting key details from these emails (e.g., Role Title, Company, Application Status/Decision, Links).
4. Logging this information in a structured way for easy review or analysis.
5. Removing the specific label from processed emails.

## Current Status (As of Step 3.2+)

This project is currently **in development** and focuses heavily on establishing a robust and well-logged authentication foundation.

**Implemented Features:**

* **Secure Authentication:** Implements the OAuth 2.0 Authorization Code Flow for Desktop Applications to securely connect to the Gmail API.
* **Token Persistence:** Successfully saves (`token.json`) and loads user authorization tokens to avoid requiring browser login on every run (refresh logic for expired tokens is the next step).
* **State Management:** Uses a state file (`auth_state.json`) to track persistent information across runs, such as the last browser authentication session ID and the number of consecutive successful token uses.
* **Detailed Logging:** Logs authentication events (token success, browser auth trigger, failures) with timestamps, reasons, and state information to a structured JSON Lines file (`auth_log.jsonl`) for debugging and analysis.
* **Modular Authentication:** The authentication logic returns a detailed status, separating it from the main state/logging logic.

**Work in Progress / Next Steps:**

* Implementing token refresh logic (Step 3.3) to handle expired tokens automatically.
* Adding core Gmail API interaction (searching/fetching emails based on a label).
* Developing email parsing logic to extract relevant job application details.
* Implementing the final data storage/output mechanism.
* Adding the label removal step for processed emails.

## Setup

1.  **Prerequisites:**
    * Python 3.x installed.
    * `pip` (Python package installer).

2.  **Clone Repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

3.  **Install Dependencies:**
    * It's highly recommended to use a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows use `venv\Scripts\activate`
        ```
    * Install required packages:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Google Cloud Platform & API Setup:**
    * You need to set up a project in the Google Cloud Console, enable the **Gmail API**, and create **OAuth 2.0 Credentials** for a **Desktop Application**.
    * **Detailed Steps:** For comprehensive instructions, please refer to the official Google documentation:
        * [Google Cloud Console](https://console.cloud.google.com/)
        * [Python Quickstart for Gmail API (includes setup)](https://developers.google.com/gmail/api/quickstart/python)
        * [Using OAuth 2.0 for Desktop Apps Guide](https://developers.google.com/identity/protocols/oauth2/native-app)
    * **Download Credentials:** Download the credentials JSON file and save it as `credentials.json` in the root directory of this project. **Do not commit this file to Git.**
    * **Permissions (Scopes):** This script currently requests the `https://www.googleapis.com/auth/gmail.modify` scope. This is a powerful scope allowing reading, sending, deleting, and managing mail/labels. Ensure you are comfortable granting this permission.
    * **Test Users:** While your application is in the "Testing" publishing status in the Google Cloud Console, you *must* add the Google account(s) you intend to authenticate with to the "Test users" list under the OAuth consent screen settings. Otherwise, you will encounter an "Access blocked" error.

5.  **Configuration Files:**
    * Place the downloaded `credentials.json` in the project root.
    * The script will automatically create the following files upon first successful run:
        * `token.json`: Stores your authorization token (add to `.gitignore`).
        * `auth_state.json`: Stores run state (add to `.gitignore`).
        * `auth_log.jsonl`: Stores detailed logs (add to `.gitignore`).

## Usage

1.  Ensure your virtual environment is activated (if using one).
2.  Run the main script:
    ```bash
    python <your_main_script_name>.py
    ```
3.  **First Run:** Your web browser will open, asking you to log in to your Google account and grant the requested permissions (make sure you are logged in as a registered "Test user").
4.  **Subsequent Runs:** If `token.json` is valid, the script should authenticate without opening the browser. It will log events to `auth_log.jsonl` and update `auth_state.json`.

*(Note: Actual email processing functionality is not yet implemented.)*

## Educational Journey & Skill Demonstration

This project serves a dual purpose:

1.  **Skill Demonstration:** It showcases the implementation of secure authentication (OAuth 2.0), interaction with external APIs (Google Gmail), state management, logging, and potentially data parsing and manipulation in Python.
2.  **Educational Work:** The development process itself is a learning exercise, progressing step-by-step from basic concepts to more robust implementations. The detailed logging and state management added during the authentication phase are part of this incremental learning process, exploring how to build more observable and resilient applications. The commit history may reflect this step-by-step approach.

-- Saran Pavuluri a.k.a ToofanCoder
