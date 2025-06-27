# Quick Start Guide - JobAppsMailTracker

Get your job application tracking system up and running in 5 minutes!

## Prerequisites

- Python 3.7 or higher
- A Google account
- Job application emails in Gmail

## Step 1: Setup Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Gmail API
   - Google Sheets API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the JSON file and rename it to `credentials.json`
5. Add your email as a test user in OAuth consent screen

## Step 2: Install and Setup

```bash
# Clone or download the project
cd JobAppsMailTracker

# Run the setup script
python setup.py

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Place your credentials.json in the project root
```

## Step 3: Prepare Gmail

1. Open Gmail
2. Create a label called "Job Applications"
3. Apply this label to emails related to:
   - Job applications you've submitted
   - Interview invitations
   - Rejection emails
   - Offer letters
   - Any job-related correspondence

## Step 4: Run the Tracker

```bash
# Test the setup first
python test_tracker.py

# Run the main tracker
python job_tracker.py
```

## Step 5: View Results

1. Check your Google Drive for a new spreadsheet called "Job Applications Tracker"
2. The spreadsheet will contain columns for:
   - Company name
   - Job position
   - Application date
   - Status (Applied, Interview, Rejected, etc.)
   - Email metadata

## What Happens

1. **Authentication**: First run opens browser for Google authorization
2. **Email Search**: Finds emails with "Job Applications" label
3. **Data Extraction**: Parses company, position, and status from emails
4. **Spreadsheet Update**: Adds new job applications to Google Sheets
5. **Email Management**: Marks processed emails to avoid duplicates

## Customization

Edit `config.json` to customize:
- Gmail label names
- Spreadsheet name
- Status keywords
- Email search queries

## Troubleshooting

**"Access blocked" error:**
- Add your email as a test user in Google Cloud Console

**"No emails found":**
- Make sure you have emails labeled with "Job Applications"

**"Credentials not found":**
- Ensure `credentials.json` is in the project root

## Next Steps

- Run the tracker regularly to keep your job applications updated
- Customize the configuration for your specific needs
- Check the logs in `auth_log.jsonl` for detailed information

## Support

- Check the main README.md for detailed documentation
- Review the code comments for implementation details
- Use `test_tracker.py` to verify your setup

---

**Happy job hunting! 🚀** 