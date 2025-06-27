# 🎯 JobAppsMailTracker - Gmail Job Application Tracking Script

<div align="center">

# 🚨 **VIBE CODE DISCLAIMER** 🚨

### *"Because why track job applications manually when you can automate it while learning cool new tools?"* 🤖

**This is a vibe project built for fun, learning, and productivity experimentation!** 

- 🎓 **Learning Goal:** Master Cursor AI, explore new productivity tools, and build something actually useful
- ⚡ **Productivity Hack:** Turn boring job tracking into an automated workflow
- 🧪 **Tech Playground:** OAuth 2.0, Google APIs, Gemini AI, and whatever else catches our fancy
- 🎯 **Real Problem:** Job hunting is chaotic - let's make it less so!

*Built with ❤️ during free time because apparently, we can't just watch Netflix all day*

---

</div>

## Project Goal

The ultimate goal of this project is to create a Python script that automates the tracking of job applications by:

1. Connecting securely to a user's Gmail account.
2. Identifying emails related to job applications (using a specific Gmail label).
3. Extracting key details from these emails (e.g., Role Title, Company, Application Status/Decision, Links).
4. Logging this information in a structured way for easy review or analysis.
5. **NEW**: Automatically updating a Google Sheets document with job application data.
6. **NEW**: Removing the specific label from processed emails to avoid duplicates.

## Current Status (Complete Implementation)

This project is now **fully functional** and includes:

**Core Features:**
* **Secure Authentication:** Implements the OAuth 2.0 Authorization Code Flow for Desktop Applications to securely connect to both Gmail and Google Sheets APIs.
* **Token Persistence:** Successfully saves (`token.json`) and loads user authorization tokens to avoid requiring browser login on every run.
* **Automatic Token Refresh:** Handles expired tokens automatically without user intervention.
* **Gmail Email Processing:** Searches for job application emails using configurable labels and extracts key information.
* **Intelligent Parsing:** Automatically extracts company names, job positions, and application status from email content.
* **Google Sheets Integration:** Creates and updates a Google Sheets document with job application tracking data.
* **Email Label Management:** Automatically marks processed emails to prevent duplicate processing.
* **Configuration Management:** Flexible configuration system for customizing labels, spreadsheet settings, and status mappings.

**Data Extracted:**
* Company name (from email domain or subject line)
* Job position/title
* Application date
* Application status (Applied, Interview, Rejected, Accepted, Withdrawn)
* Email metadata (ID, date, source)
* Notes and last updated timestamp

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
    * You need to set up a project in the Google Cloud Console and enable both the **Gmail API** and **Google Sheets API**.
    * Create **OAuth 2.0 Credentials** for a **Desktop Application**.
    * **Detailed Steps:** For comprehensive instructions, please refer to the official Google documentation:
        * [Google Cloud Console](https://console.cloud.google.com/)
        * [Python Quickstart for Gmail API](https://developers.google.com/gmail/api/quickstart/python)
        * [Google Sheets API Setup](https://developers.google.com/sheets/api/quickstart/python)
        * [Using OAuth 2.0 for Desktop Apps Guide](https://developers.google.com/identity/protocols/oauth2/native-app)
    * **Download Credentials:** Download the credentials JSON file and save it as `credentials.json` in the root directory of this project. **Do not commit this file to Git.**
    * **Permissions (Scopes):** This script requests two scopes:
        * `https://www.googleapis.com/auth/gmail.modify` - For reading and modifying Gmail messages and labels
        * `https://www.googleapis.com/auth/spreadsheets` - For creating and updating Google Sheets
    * **Test Users:** While your application is in the "Testing" publishing status in the Google Cloud Console, you *must* add the Google account(s) you intend to authenticate with to the "Test users" list under the OAuth consent screen settings.

5.  **Configuration Files:**
    * Place the downloaded `credentials.json` in the project root.
    * The script will automatically create the following files upon first successful run:
        * `token.json`: Stores your authorization token (add to `.gitignore`).
        * `config.json`: Configuration settings (can be customized).
        * `auth_state.json`: Stores run state (add to `.gitignore`).
        * `auth_log.jsonl`: Stores detailed logs (add to `.gitignore`).

6.  **Gmail Setup:**
    * Create a Gmail label called "Job Applications" (or customize in `config.json`)
    * Apply this label to emails related to job applications
    * The script will automatically create a "Job Applications/Processed" sub-label for tracking

## Usage

1.  **Prepare Your Gmail:**
    * Create a label called "Job Applications" in Gmail
    * Apply this label to emails you want to track (job applications, interview invitations, rejections, etc.)

2.  **Run the Script:**
    ```bash
    python job_tracker.py
    ```

3.  **First Run:** Your web browser will open, asking you to log in to your Google account and grant the requested permissions (make sure you are logged in as a registered "Test user").

4.  **Subsequent Runs:** If `token.json` is valid, the script should authenticate without opening the browser.

5.  **Results:** The script will:
    * Search for emails with the "Job Applications" label
    * Extract job application details from each email
    * Create or update a Google Sheets document with the data
    * Mark processed emails with a "Processed" label to avoid duplicates
    * Display progress and results in the console

## Configuration

The `config.json` file allows you to customize:

```json
{
    "gmail_label": "Job Applications",           // Gmail label to search for
    "processed_label": "Job Applications/Processed", // Label for processed emails
    "spreadsheet_id": null,                      // Auto-populated after first run
    "spreadsheet_name": "Job Applications Tracker", // Name for new spreadsheets
    "email_search_query": "label:Job Applications -label:Job Applications/Processed",
    "status_mapping": {                          // Keywords for status detection
        "applied": "Applied",
        "interview": "Interview", 
        "rejected": "Rejected",
        "accepted": "Accepted",
        "withdrawn": "Withdrawn"
    }
}
```

## How It Works

1. **Authentication:** Uses OAuth 2.0 to securely connect to Gmail and Google Sheets APIs
2. **Email Search:** Searches Gmail for emails with the specified label that haven't been processed
3. **Content Extraction:** Parses email headers and body to extract:
   - Company name (from email domain or subject)
   - Job position (using keyword matching)
   - Application status (based on email content keywords)
   - Dates and metadata
4. **Data Processing:** Organizes extracted data into structured job application records
5. **Spreadsheet Update:** Creates or updates a Google Sheets document with the job application data
6. **Email Management:** Marks processed emails to prevent duplicate processing

## Output Format

The Google Sheets document will contain the following columns:
- **Company:** Extracted company name
- **Position:** Job title/position
- **Application Date:** When the application was made
- **Status:** Current application status
- **Email ID:** Gmail message ID for reference
- **Email Date:** When the email was received
- **Source:** Source of the data (Gmail)
- **Notes:** Additional information from email subject
- **Last Updated:** Timestamp of when the record was processed

## Troubleshooting

**Common Issues:**
- **"Access blocked" error:** Make sure your Google account is added as a test user in the Google Cloud Console
- **"Credentials file not found":** Ensure `credentials.json` is in the project root directory
- **"No job application emails found":** Make sure you have emails labeled with "Job Applications" in Gmail
- **Permission errors:** Ensure both Gmail API and Google Sheets API are enabled in your Google Cloud project

**Logs:** Check `auth_log.jsonl` for detailed authentication and processing logs.

## Educational Journey & Skill Demonstration

This project demonstrates:
1. **API Integration:** Secure OAuth 2.0 authentication with multiple Google APIs
2. **Data Processing:** Email parsing and content extraction
3. **State Management:** Persistent configuration and token management
4. **Error Handling:** Robust error handling and logging
5. **Data Storage:** Google Sheets integration for structured data storage
6. **Automation:** End-to-end automation of job application tracking

-- Saran Pavuluri a.k.a ToofanCoder
