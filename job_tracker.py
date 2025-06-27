#!/usr/bin/env python3
"""
JobAppsMailTracker - Automated Job Application Tracking System

This script:
1. Connects to Gmail API to search for job application emails
2. Extracts key details from job-related emails
3. Updates a Google Sheets document with job application tracking data
4. Manages email labels to track processed emails

Author: Saran Pavuluri (ToofanCoder)
"""

import os
import json
import datetime
import base64
import email
import re
import csv
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Google API Client Libraries
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import gspread
from google.auth.transport.requests import Request
from google.auth import default
import google.generativeai as genai

# Import Gemini parser
from gemini_parser import GeminiEmailParser, ParsedJobDetails

# Configuration
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets"
]

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
STATE_FILE = 'auth_state.json'
LOG_FILE = 'auth_log.jsonl'
CONFIG_FILE = 'config.json'

@dataclass
class JobApplication:
    """Data class for job application information"""
    company: str
    position: str
    application_date: str
    status: str
    email_id: str
    email_date: str
    source: str
    job_id: str = ""  # Unique identifier for the job
    notes: str = ""
    last_updated: str = ""

class JobTracker:
    def __init__(self):
        self.gmail_service = None
        self.sheets_service = None
        self.gspread_client = None
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from config.json or create default"""
        default_config = {
            "gmail_label": "Job Applications",
            "processed_label": "Job Applications/Processed",
            "spreadsheet_id": None,
            "spreadsheet_name": "Job Applications Tracker",
            "email_search_query": "label:Job Applications -label:Job Applications/Processed",
            "status_mapping": {
                "applied": "Applied",
                "interview": "Interview",
                "rejected": "Rejected",
                "accepted": "Accepted",
                "withdrawn": "Withdrawn"
            }
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config file
            try:
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(default_config, f, indent=4)
                print(f"Created default config file: {CONFIG_FILE}")
            except Exception as e:
                print(f"Error creating config file: {e}")
            return default_config

    def authenticate_and_get_status(self) -> Tuple[bool, Dict]:
        """Authenticate with Google APIs and return status"""
        creds = None
        trigger_reason = None
        status = 'FAILURE'

        if os.path.exists(TOKEN_FILE):
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        try:
                            creds.refresh(Request())
                            status = 'TOKEN_REFRESHED'
                        except Exception as e:
                            trigger_reason = 'TOKEN_REFRESH_FAILED'
                            creds = None
                    else:
                        trigger_reason = 'TOKEN_INVALID'
                        creds = None
                else:
                    status = 'TOKEN_SUCCESS'
            except Exception as e:
                trigger_reason = 'TOKEN_LOAD_ERROR'
                creds = None
        else:
            trigger_reason = 'NO_TOKEN_FILE'
            creds = None

        if status not in ['TOKEN_SUCCESS', 'TOKEN_REFRESHED']:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                status = 'BROWSER_AUTH_SUCCESS'
                if trigger_reason is None:
                    trigger_reason = 'INITIATED_BROWSER_FLOW'
                if creds:
                    try:
                        with open(TOKEN_FILE, 'w') as token:
                            token.write(creds.to_json())
                    except Exception as e:
                        pass
            except FileNotFoundError:
                trigger_reason = 'MISSING_CREDENTIALS_FILE'
                status = 'FAILURE'
                creds = None
            except Exception as e:
                trigger_reason = 'BROWSER_FLOW_ERROR'
                status = 'FAILURE'
                creds = None

        # Build services if authentication successful
        if status in ['TOKEN_SUCCESS', 'BROWSER_REFRESHED', 'BROWSER_AUTH_SUCCESS'] and creds and creds.valid:
            try:
                self.gmail_service = build('gmail', 'v1', credentials=creds)
                self.sheets_service = build('sheets', 'v4', credentials=creds)
                self.gspread_client = gspread.authorize(creds)
                return True, {'status': status, 'trigger_reason': trigger_reason}
            except Exception as e:
                return False, {'status': 'FAILURE', 'trigger_reason': 'SERVICE_BUILD_ERROR'}
        
        return False, {'status': status, 'trigger_reason': trigger_reason}

    def log_event(self, event_data: Dict):
        """Log events to JSON Lines file"""
        try:
            with open(LOG_FILE, 'a') as f:
                json.dump(event_data, f)
                f.write('\n')
        except IOError as e:
            print(f"Error writing log event to {LOG_FILE}: {e}")

    def create_or_get_spreadsheet(self) -> Optional[str]:
        """Create or get existing Google Sheets spreadsheet"""
        try:
            if self.config['spreadsheet_id']:
                # Try to access existing spreadsheet
                try:
                    if self.gspread_client is None:
                        print("Gspread client is not initialized")
                        return None
                    spreadsheet = self.gspread_client.open_by_key(self.config['spreadsheet_id'])
                    print(f"Using existing spreadsheet: {spreadsheet.title}")
                    return self.config['spreadsheet_id']
                except Exception as e:
                    print(f"Could not access existing spreadsheet: {e}")
                    # Continue to create new one
            
            # Create new spreadsheet
            if self.gspread_client is None:
                print("Gspread client is not initialized")
                return None
            spreadsheet = self.gspread_client.create(self.config['spreadsheet_name'])
            spreadsheet_id = spreadsheet.id
            
            # Update config with new spreadsheet ID
            self.config['spreadsheet_id'] = spreadsheet_id
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            # Set up headers
            headers = [
                'Job ID', 'Company', 'Position', 'Application Date', 'Status', 
                'Email ID', 'Email Date', 'Source', 'Notes', 'Last Updated'
            ]
            worksheet = spreadsheet.get_worksheet(0)
            worksheet.update('A1:J1', headers)
            worksheet.format('A1:J1', {'textFormat': {'bold': True}})
            
            print(f"Created new spreadsheet: {spreadsheet.title} (ID: {spreadsheet_id})")
            return spreadsheet_id
            
        except Exception as e:
            print(f"Error creating/getting spreadsheet: {e}")
            return None

    def search_job_emails(self) -> List[Dict]:
        """Search for job application emails in Gmail"""
        try:
            # Search for emails with the job applications label
            query = self.config['email_search_query']
            if self.gmail_service is None:
                print("Gmail service is not initialized")
                return []
                
            results = self.gmail_service.users().messages().list(
                userId='me', q=query, maxResults=100
            ).execute()
            
            messages = results.get('messages', [])
            print(f"Found {len(messages)} job application emails")
            
            return messages
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []

    def extract_email_content(self, message_id: str) -> Dict:
        """Extract content from Gmail message"""
        try:
            if self.gmail_service is None:
                print("Gmail service is not initialized")
                return {}
                
            message = self.gmail_service.users().messages().get(
                userId='me', id=message_id, format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date_header = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Parse email body
            body = self.get_email_body(message['payload'])
            
            return {
                'subject': subject,
                'from': from_header,
                'date': date_header,
                'body': body,
                'message_id': message_id
            }
        except Exception as e:
            print(f"Error extracting email content: {e}")
            return {}

    def get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        
        return ""

    def generate_job_id(self, company: str, position: str, email_subject: str = "", application_date: str = "") -> str:
        """Generate a unique job identifier based on company, position, email subject, and optionally application date"""
        import hashlib
        
        # Extract key terms from email subject that might differentiate positions
        subject_keywords = self.extract_position_keywords(email_subject)
        
        # Create a normalized string for consistent hashing
        base_normalized = f"{company.lower().strip()}|{position.lower().strip()}"
        
        # Add subject keywords if they exist
        if subject_keywords:
            normalized = f"{base_normalized}|{subject_keywords}"
        else:
            normalized = base_normalized
            
        # Add application date if provided (for multiple applications to same role)
        if application_date:
            # Use just the date part (YYYY-MM-DD) to avoid time-based variations
            try:
                date_part = application_date.split('T')[0]  # Extract date from ISO format
                normalized = f"{normalized}|{date_part}"
            except:
                pass
        
        # Generate a hash for uniqueness
        job_hash = hashlib.md5(normalized.encode()).hexdigest()[:8]
        
        # Create a readable job ID
        clean_company = re.sub(r'[^a-zA-Z0-9]', '', company)[:10]
        clean_position = re.sub(r'[^a-zA-Z0-9]', '', position)[:15]
        
        # Include subject keywords in the ID if available
        if subject_keywords:
            clean_keywords = re.sub(r'[^a-zA-Z0-9]', '', subject_keywords)[:10]
            return f"{clean_company}_{clean_position}_{clean_keywords}_{job_hash}"
        else:
            return f"{clean_company}_{clean_position}_{job_hash}"

    def extract_position_keywords(self, email_subject: str) -> str:
        """Extract keywords from email subject that might differentiate positions"""
        if not email_subject:
            return ""
            
        subject_lower = email_subject.lower()
        
        # Keywords that might indicate different roles
        role_keywords = [
            'backend', 'frontend', 'fullstack', 'full-stack', 'full stack',
            'machine learning', 'ml', 'ai', 'data', 'infrastructure',
            'mobile', 'ios', 'android', 'web', 'cloud', 'devops',
            'security', 'embedded', 'systems', 'platform', 'api',
            'senior', 'junior', 'lead', 'principal', 'staff',
            'remote', 'onsite', 'hybrid', 'contract', 'intern'
        ]
        
        found_keywords = []
        for keyword in role_keywords:
            if keyword in subject_lower:
                found_keywords.append(keyword)
        
        # Return up to 2 most relevant keywords
        return '_'.join(found_keywords[:2]) if found_keywords else ""

    def parse_job_application(self, email_data: Dict) -> Optional[JobApplication]:
        """Parse email content to extract job application details using Gemini AI"""
        try:
            # Initialize Gemini parser (with fallback to basic parsing)
            gemini_parser = None
            try:
                gemini_parser = GeminiEmailParser()
                print("🤖 Using Gemini AI for intelligent email parsing...")
            except Exception as e:
                print(f"⚠️ Gemini not available, using basic parsing: {e}")
                gemini_parser = None
            
            # Use Gemini if available, otherwise fallback to basic parsing
            if gemini_parser:
                # Parse with Gemini
                parsed_details = gemini_parser.parse_email(email_data)
                
                # Parse email date
                email_date = self.parse_email_date(email_data.get('date', ''))
                application_date = parsed_details.application_date or email_date
                
                # Generate unique job identifier
                job_id = self.generate_job_id(
                    parsed_details.company or 'Unknown Company', 
                    parsed_details.position or 'Unknown Position', 
                    email_data.get('subject', ''), 
                    application_date
                )
                
                # Create enhanced notes with Gemini insights
                notes_parts = [f"Subject: {email_data.get('subject', '')}"]
                if parsed_details.location:
                    notes_parts.append(f"Location: {parsed_details.location}")
                if parsed_details.job_type:
                    notes_parts.append(f"Type: {parsed_details.job_type}")
                if parsed_details.experience_level:
                    notes_parts.append(f"Level: {parsed_details.experience_level}")
                if parsed_details.department:
                    notes_parts.append(f"Dept: {parsed_details.department}")
                if parsed_details.confidence_score > 0:
                    notes_parts.append(f"AI Confidence: {parsed_details.confidence_score:.2f}")
                if parsed_details.extraction_notes:
                    notes_parts.append(f"AI Notes: {parsed_details.extraction_notes}")
                
                notes = " | ".join(notes_parts)
                
                return JobApplication(
                    company=parsed_details.company or 'Unknown Company',
                    position=parsed_details.position or 'Unknown Position',
                    application_date=application_date,
                    status=parsed_details.status or 'Applied',
                    email_id=email_data.get('message_id', ''),
                    email_date=email_date,
                    source='Gmail (Gemini AI)',
                    job_id=job_id,
                    notes=notes,
                    last_updated=datetime.datetime.now().isoformat()
                )
            else:
                # Fallback to basic parsing
                return self._parse_job_application_basic(email_data)
                
        except Exception as e:
            print(f"Error parsing job application: {e}")
            # Final fallback to basic parsing
            return self._parse_job_application_basic(email_data)
    
    def _parse_job_application_basic(self, email_data: Dict) -> Optional[JobApplication]:
        """Basic parsing fallback when Gemini is not available"""
        try:
            subject = email_data.get('subject', '') or ''
            body = email_data.get('body', '') or ''
            from_email = email_data.get('from', '') or ''
            
            subject_lower = subject.lower()
            body_lower = body.lower()
            
            # Extract company name from email domain or subject
            company = self.extract_company(from_email, subject)
            
            # Extract position title
            position = self.extract_position(subject, body)
            
            # Parse email date first
            email_date = self.parse_email_date(email_data.get('date', ''))
            
            # Estimate application date (usually email date for new applications)
            application_date = email_date
            
            # Generate unique job identifier (now includes application date for better uniqueness)
            job_id = self.generate_job_id(company, position, subject, application_date)
            
            # Determine application status
            status = self.determine_status(subject, body)
            
            return JobApplication(
                company=company,
                position=position,
                application_date=application_date,
                status=status,
                email_id=email_data.get('message_id', ''),
                email_date=email_date,
                source='Gmail (Basic)',
                job_id=job_id,
                notes=f"Subject: {subject} | Basic parsing used",
                last_updated=datetime.datetime.now().isoformat()
            )
        except Exception as e:
            print(f"Error in basic parsing: {e}")
            return None

    def extract_company(self, from_email: str, subject: str) -> str:
        """Extract company name from email or subject"""
        # Try to extract from email domain
        if '@' in from_email:
            domain = from_email.split('@')[1].split('.')[0]
            if domain not in ['gmail', 'yahoo', 'hotmail', 'outlook']:
                return domain.title()
        
        # Try to extract from subject line
        if subject:
            subject_upper = subject.upper()
            common_indicators = ['AT ', 'FOR ', 'WITH ', 'VIA ']
            for indicator in common_indicators:
                if indicator in subject_upper:
                    parts = subject_upper.split(indicator)
                    if len(parts) > 1:
                        company_part = parts[1].split()[0]
                        return company_part.title()
        
        return "Unknown Company"

    def extract_position(self, subject: str, body: str) -> str:
        """Extract job position from subject or body"""
        # Look for common position indicators
        position_indicators = [
            'software engineer', 'developer', 'programmer', 'data scientist',
            'analyst', 'manager', 'director', 'lead', 'architect', 'consultant'
        ]
        
        text = f"{subject or ''} {body or ''}"
        for indicator in position_indicators:
            if indicator in text.lower():
                # Try to get the full position title
                words = text.split()
                for i, word in enumerate(words):
                    if indicator in word.lower():
                        # Get surrounding words for context
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        position = ' '.join(words[start:end])
                        return position.title()
        
        return "Unknown Position"

    def determine_status(self, subject: str, body: str) -> str:
        """Determine application status from email content"""
        text = f"{subject or ''} {body or ''}".lower()
        
        status_keywords = {
            'rejected': ['rejected', 'not selected', 'unfortunately', 'regret'],
            'interview': ['interview', 'schedule', 'meeting', 'call'],
            'accepted': ['accepted', 'congratulations', 'welcome', 'offer'],
            'withdrawn': ['withdrawn', 'cancelled', 'no longer interested']
        }
        
        for status, keywords in status_keywords.items():
            if any(keyword in text for keyword in keywords):
                return self.config['status_mapping'].get(status, status.title())
        
        return 'Applied'  # Default status

    def parse_email_date(self, date_str: str) -> str:
        """Parse email date string to ISO format"""
        try:
            # Try to parse various date formats
            import email.utils
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            return parsed_date.isoformat()
        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")
            return datetime.datetime.now().isoformat()

    def write_to_csv(self, job_applications: List[JobApplication], csv_file: str = 'job_applications_fallback.csv') -> bool:
        """Write job applications to a CSV file as a fallback"""
        try:
            file_exists = os.path.isfile(csv_file)
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow([
                        'Job ID', 'Company', 'Position', 'Application Date', 'Status',
                        'Email ID', 'Email Date', 'Source', 'Notes', 'Last Updated'
                    ])
                for job in job_applications:
                    writer.writerow([
                        job.job_id, job.company, job.position, job.application_date,
                        job.status, job.email_id, job.email_date,
                        job.source, job.notes, job.last_updated
                    ])
            print(f"✅ Wrote {len(job_applications)} job applications to CSV fallback: {csv_file}")
            return True
        except Exception as e:
            print(f"❌ Error writing to CSV fallback: {e}")
            return False

    def update_spreadsheet(self, job_applications: List[JobApplication]) -> bool:
        """Update Google Sheets with job application data, fallback to CSV if Sheets fails"""
        try:
            spreadsheet_id = self.create_or_get_spreadsheet()
            if not spreadsheet_id:
                raise Exception("No spreadsheet ID available")
            
            if not self.gspread_client:
                raise Exception("Gspread client not initialized")
                
            spreadsheet = self.gspread_client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.get_worksheet(0)
            
            # Convert job applications to rows
            rows = []
            for job in job_applications:
                rows.append([
                    job.job_id, job.company, job.position, job.application_date,
                    job.status, job.email_id, job.email_date,
                    job.source, job.notes, job.last_updated
                ])
            
            if rows:
                # Append new rows
                worksheet.append_rows(rows)
                print(f"Added {len(rows)} job applications to spreadsheet")
            
            return True
            
        except Exception as e:
            print(f"Error updating spreadsheet: {e}")
            print("Falling back to CSV export...")
            return self.write_to_csv(job_applications)

    def mark_email_processed(self, message_id: str) -> bool:
        """Mark email as processed by adding label"""
        try:
            # Get or create processed label
            label_name = self.config['processed_label']
            if not self.gmail_service:
                raise Exception("Gmail service not initialized")
            labels = self.gmail_service.users().labels().list(userId='me').execute()
            
            label_id = None
            for label in labels.get('labels', []):
                if label['name'] == label_name:
                    label_id = label['id']
                    break
            
            if not label_id:
                # Create new label
                label_object = {'name': label_name}
                created_label = self.gmail_service.users().labels().create(
                    userId='me', body=label_object
                ).execute()
                label_id = created_label['id']
            
            # Add label to message
            self.gmail_service.users().messages().modify(
                userId='me', id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error marking email as processed: {e}")
            return False

    def find_existing_job(self, job_id: str) -> Optional[Dict]:
        """Find existing job application by job_id in spreadsheet"""
        try:
            if not self.config.get('spreadsheet_id'):
                return None
            
            if not self.gspread_client:
                raise Exception("Gspread client not initialized")
                
            spreadsheet = self.gspread_client.open_by_key(self.config['spreadsheet_id'])
            worksheet = spreadsheet.get_worksheet(0)
            
            # Get all data
            all_data = worksheet.get_all_records()
            
            # Find job with matching job_id
            for row_num, row in enumerate(all_data, start=2):  # Start from row 2 (after headers)
                if row.get('Job ID') == job_id:
                    return {
                        'row_number': row_num,
                        'data': row
                    }
            
            return None
            
        except Exception as e:
            print(f"Error finding existing job: {e}")
            return None

    def update_existing_job_status(self, job_id: str, new_status: str, new_email_id: str, new_email_date: str) -> bool:
        """Update status of existing job application"""
        try:
            existing_job = self.find_existing_job(job_id)
            if not existing_job:
                return False
            
            if not self.gspread_client:
                raise Exception("Gspread client not initialized")
                
            spreadsheet = self.gspread_client.open_by_key(self.config['spreadsheet_id'])
            worksheet = spreadsheet.get_worksheet(0)
            
            row_num = existing_job['row_number']
            
            # Update status and last updated timestamp
            worksheet.update(f'D{row_num}', new_status)  # Status column
            worksheet.update(f'J{row_num}', datetime.datetime.now().isoformat())  # Last Updated column
            
            # Update notes to include the new email info
            current_notes = existing_job['data'].get('Notes', '')
            new_note = f"Status updated to {new_status} via email {new_email_id}"
            updated_notes = f"{current_notes}; {new_note}" if current_notes else new_note
            worksheet.update(f'I{row_num}', updated_notes)  # Notes column
            
            print(f"✅ Updated existing job {job_id} status to: {new_status}")
            return True
            
        except Exception as e:
            print(f"Error updating existing job status: {e}")
            return False

    def process_job_applications_with_updates(self, job_applications: List[JobApplication]) -> Tuple[List[JobApplication], List[JobApplication]]:
        """Process job applications, separating new jobs from status updates"""
        new_jobs = []
        status_updates = []
        
        for job_app in job_applications:
            # Check if this job already exists
            existing_job = self.find_existing_job(job_app.job_id)
            
            if existing_job:
                # This is a status update for an existing job
                current_status = existing_job['data'].get('Status', '')
                
                if current_status != job_app.status:
                    # Status has changed, update it
                    if self.update_existing_job_status(job_app.job_id, job_app.status, job_app.email_id, job_app.email_date):
                        status_updates.append(job_app)
                        print(f"🔄 Status update: {job_app.company} - {job_app.position}: {current_status} → {job_app.status}")
                    else:
                        # If update failed, treat as new entry
                        new_jobs.append(job_app)
                else:
                    # Same status, just mark email as processed
                    print(f"ℹ️  No status change: {job_app.company} - {job_app.position} (still {job_app.status})")
            else:
                # This is a new job application
                new_jobs.append(job_app)
                print(f"🆕 New job: {job_app.company} - {job_app.position} ({job_app.status})")
        
        return new_jobs, status_updates

    def run(self):
        """Main execution function"""
        print("=== Job Applications Mail Tracker ===")
        
        # Authenticate
        success, auth_result = self.authenticate_and_get_status()
        if not success:
            print(f"Authentication failed: {auth_result}")
            return
        
        print(f"Authentication successful: {auth_result['status']}")
        
        # Search for job emails
        messages = self.search_job_emails()
        if not messages:
            print("No job application emails found")
            return
        
        # Process each email
        job_applications = []
        for message in messages:
            email_data = self.extract_email_content(message['id'])
            if email_data:
                job_app = self.parse_job_application(email_data)
                if job_app:
                    job_applications.append(job_app)
                    print(f"Parsed: {job_app.company} - {job_app.position} ({job_app.status})")
        
        # Process job applications with updates
        new_jobs, status_updates = self.process_job_applications_with_updates(job_applications)
        
        # Update spreadsheet with only new jobs (status updates are handled separately)
        if new_jobs:
            if self.update_spreadsheet(new_jobs):
                print(f"✅ Added {len(new_jobs)} new job applications to spreadsheet")
            else:
                print("Failed to update Google Sheets")
        
        # Summary
        if new_jobs or status_updates:
            print(f"\n📊 Processing Summary:")
            print(f"   🆕 New jobs: {len(new_jobs)}")
            print(f"   🔄 Status updates: {len(status_updates)}")
            
            # Mark all emails as processed
            for job_app in new_jobs + status_updates:
                self.mark_email_processed(job_app.email_id)
            print("✅ Marked all emails as processed")
        else:
            print("No job applications to process")
        
        print("=== Job tracking complete ===")

if __name__ == '__main__':
    tracker = JobTracker()
    tracker.run() 