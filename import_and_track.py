#!/usr/bin/env python3
"""
Import and Track Job Applications
Imports job applications from Excel/CSV files and tracks status updates from emails
"""

import pandas as pd
import os
import json
import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from job_tracker import JobTracker, JobApplication

@dataclass
class ImportedJob:
    """Data structure for imported job applications"""
    company: str
    position: str
    application_date: str
    status: str
    source: str = "Excel Import"
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    department: Optional[str] = None
    salary_range: Optional[str] = None
    notes: str = ""

class JobImportTracker:
    """Imports job applications and tracks status updates"""
    
    def __init__(self):
        self.job_tracker = JobTracker()
        
    def import_from_excel(self, file_path: str, sheet_name: str = None) -> List[ImportedJob]:
        """Import job applications from Excel file"""
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            print(f"📊 Loaded {len(df)} rows from {file_path}")
            print(f"📋 Columns found: {list(df.columns)}")
            
            # Map columns to expected format
            mapped_jobs = self._map_columns(df)
            
            print(f"✅ Successfully imported {len(mapped_jobs)} job applications")
            return mapped_jobs
            
        except Exception as e:
            print(f"❌ Error importing from Excel: {e}")
            return []
    
    def import_from_csv(self, file_path: str) -> List[ImportedJob]:
        """Import job applications from CSV file"""
        try:
            df = pd.read_csv(file_path)
            print(f"📊 Loaded {len(df)} rows from {file_path}")
            print(f"📋 Columns found: {list(df.columns)}")
            
            # Map columns to expected format
            mapped_jobs = self._map_columns(df)
            
            print(f"✅ Successfully imported {len(mapped_jobs)} job applications")
            return mapped_jobs
            
        except Exception as e:
            print(f"❌ Error importing from CSV: {e}")
            return []
    
    def _map_columns(self, df: pd.DataFrame) -> List[ImportedJob]:
        """Map DataFrame columns to ImportedJob objects (only title, company, link, applied date)"""
        jobs = []
        
        # Lowercase column names for robust matching
        lower_columns = {col.lower(): col for col in df.columns}
        
        # Only map these fields
        column_mappings = {
            'company': ['company'],
            'position': ['title'],
            'link': ['link'],
            'application_date': ['applied date', 'application_date', 'applied_date', 'date_applied', 'date']
        }
        
        # Find actual column names in the DataFrame (case-insensitive)
        actual_columns = {}
        for field, possible_names in column_mappings.items():
            for col_name in possible_names:
                if col_name in lower_columns:
                    actual_columns[field] = lower_columns[col_name]
                    break
        print(f"🔍 Detected column mappings: {actual_columns}")
        
        # Process each row
        for index, row in df.iterrows():
            try:
                company = self._get_value(row, actual_columns.get('company'), 'Unknown Company')
                position = self._get_value(row, actual_columns.get('position'), 'Unknown Position')
                link = self._get_value(row, actual_columns.get('link'), '')
                application_date = self._get_value(row, actual_columns.get('application_date'), '')
                # Normalize application date
                if application_date:
                    application_date = self._normalize_date(application_date)
                else:
                    application_date = datetime.datetime.now().isoformat()
                # Create ImportedJob object (only these fields)
                job = ImportedJob(
                    company=company,
                    position=position,
                    application_date=application_date,
                    status='Applied',
                    notes=f"Link: {link}" if link else ""
                )
                jobs.append(job)
            except Exception as e:
                print(f"⚠️ Error processing row {index}: {e}")
                continue
        return jobs
    
    def _get_value(self, row: pd.Series, column_name: Optional[str], default: str) -> str:
        """Safely get value from DataFrame row"""
        if column_name is not None and column_name in row:
            value = row[column_name]
            # If value is a Series or ndarray, treat as missing
            try:
                if hasattr(value, 'shape') and hasattr(value.shape, '__len__') and len(value.shape) > 0:
                    return default
            except (TypeError, AttributeError):
                pass
            if value is None or pd.isna(value):
                return default
            return str(value).strip()
        return default
    
    def _normalize_date(self, date_value: str) -> str:
        """Normalize date to ISO format"""
        try:
            # Try to parse various date formats
            if isinstance(date_value, str):
                # Handle common Excel date formats
                if '/' in date_value:
                    # MM/DD/YYYY or DD/MM/YYYY
                    parts = date_value.split('/')
                    if len(parts) == 3:
                        if int(parts[0]) > 12:  # DD/MM/YYYY
                            date_value = f"{parts[2]}-{parts[1]}-{parts[0]}"
                        else:  # MM/DD/YYYY
                            date_value = f"{parts[2]}-{parts[0]}-{parts[1]}"
                # Try pandas to_datetime
                parsed_date = pd.to_datetime(date_value, errors='coerce')
                if pd.isna(parsed_date):
                    return datetime.datetime.now().isoformat()
                return parsed_date.isoformat()
        except Exception as e:
            print(f"⚠️ Could not parse date '{date_value}': {e}")
        return datetime.datetime.now().isoformat()
    
    def convert_to_job_applications(self, imported_jobs: List[ImportedJob]) -> List[JobApplication]:
        """Convert ImportedJob objects to JobApplication objects"""
        job_applications = []
        
        for imported_job in imported_jobs:
            # Generate unique job ID
            job_id = self.job_tracker.generate_job_id(
                imported_job.company,
                imported_job.position,
                "",  # No email subject for imported jobs
                imported_job.application_date
            )
            
            # Create enhanced notes
            notes_parts = [f"Imported from Excel/CSV"]
            if imported_job.location:
                notes_parts.append(f"Location: {imported_job.location}")
            if imported_job.job_type:
                notes_parts.append(f"Type: {imported_job.job_type}")
            if imported_job.experience_level:
                notes_parts.append(f"Level: {imported_job.experience_level}")
            if imported_job.department:
                notes_parts.append(f"Dept: {imported_job.department}")
            if imported_job.salary_range:
                notes_parts.append(f"Salary: {imported_job.salary_range}")
            if imported_job.notes:
                notes_parts.append(f"Original Notes: {imported_job.notes}")
            
            notes = " | ".join(notes_parts)
            
            # Create JobApplication
            job_app = JobApplication(
                company=imported_job.company,
                position=imported_job.position,
                application_date=imported_job.application_date,
                status=imported_job.status,
                email_id="",  # No email ID for imported jobs
                email_date="",  # No email date for imported jobs
                source=imported_job.source,
                job_id=job_id,
                notes=notes,
                last_updated=datetime.datetime.now().isoformat()
            )
            
            job_applications.append(job_app)
        
        return job_applications
    
    def search_for_status_updates(self, imported_jobs: List[ImportedJob]) -> List[Tuple[ImportedJob, Dict]]:
        """Search emails for status updates for imported jobs"""
        print("🔍 Searching emails for status updates...")
        
        updates = []
        
        # Check if Gmail service is available
        if not self.job_tracker.gmail_service:
            print("❌ Gmail service not available. Please authenticate first.")
            print("   Run: python job_tracker.py to set up authentication")
            return updates
        
        # Get all emails from inbox (not just labeled ones)
        try:
            print("📧 Searching entire inbox for job-related emails...")
            
            # Search for emails that might be job-related
            # Use a broader search to find job application emails
            search_queries = [
                "application", "apply", "job", "position", "role", "recruiter",
                "interview", "schedule", "meeting", "rejection", "offer",
                "thank you for applying", "application received", "application status"
            ]
            
            all_emails = []
            for query in search_queries:
                try:
                    results = self.job_tracker.gmail_service.users().messages().list(
                        userId='me', q=query, maxResults=50
                    ).execute()
                    
                    messages = results.get('messages', [])
                    if messages:
                        print(f"   Found {len(messages)} emails with query: '{query}'")
                        all_emails.extend(messages)
                except Exception as e:
                    print(f"   Error searching for '{query}': {e}")
                    continue
            
            # Remove duplicates based on message ID
            unique_emails = {}
            for email in all_emails:
                unique_emails[email['id']] = email
            
            print(f"📧 Found {len(unique_emails)} unique job-related emails to search")
            
            # Extract content for each email
            email_contents = []
            for email_id in list(unique_emails.keys())[:100]:  # Limit to first 100 for performance
                try:
                    email_content = self.job_tracker.extract_email_content(email_id)
                    if email_content:
                        email_contents.append(email_content)
                except Exception as e:
                    print(f"   Error extracting email {email_id}: {e}")
                    continue
            
            print(f"📬 Successfully extracted {len(email_contents)} email contents")
            
            # Search for matches with imported jobs
            for imported_job in imported_jobs:
                # Search for emails related to this job
                matching_emails = self._find_matching_emails(imported_job, email_contents)
                
                if matching_emails:
                    print(f"📬 Found {len(matching_emails)} emails for {imported_job.company} - {imported_job.position}")
                    
                    for email_data in matching_emails:
                        # Parse email to get status update
                        status_update = self._extract_status_from_email(email_data)
                        updates.append((imported_job, status_update))
                        
        except Exception as e:
            print(f"❌ Error searching for status updates: {e}")
        
        return updates
    
    def _find_matching_emails(self, imported_job: ImportedJob, emails: List[Dict]) -> List[Dict]:
        """Find emails that match the imported job (using only company, position, link)"""
        matching_emails = []
        # Create search terms
        company_terms = [imported_job.company.lower()]
        position_terms = [imported_job.position.lower()]
        link_terms = []
        if imported_job.notes and 'Link:' in imported_job.notes:
            link_val = imported_job.notes.split('Link:')[1].strip()
            if link_val:
                link_terms.append(link_val.lower())
        # Add variations
        if ' ' in imported_job.company:
            company_terms.extend(imported_job.company.lower().split())
        if ' ' in imported_job.position:
            position_terms.extend(imported_job.position.lower().split())
        for email_data in emails:
            subject = email_data.get('subject', '').lower()
            body = email_data.get('body', '').lower()
            from_email = email_data.get('from', '').lower()
            # Check if email matches this job
            company_match = any(term in subject or term in body or term in from_email for term in company_terms)
            position_match = any(term in subject or term in body for term in position_terms)
            link_match = any(term in subject or term in body for term in link_terms) if link_terms else True
            # If company, position, and (if present) link match, it's likely related
            if company_match and position_match and link_match:
                matching_emails.append(email_data)
        return matching_emails
    
    def _extract_status_from_email(self, email_data: Dict) -> Dict:
        """Extract status from email content"""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        
        # Determine status from content
        text = f"{subject} {body}"
        
        status_keywords = {
            'rejected': ['rejected', 'not selected', 'unfortunately', 'regret'],
            'interview': ['interview', 'schedule', 'meeting', 'call'],
            'accepted': ['accepted', 'congratulations', 'welcome', 'offer'],
            'withdrawn': ['withdrawn', 'cancelled', 'no longer interested']
        }
        
        detected_status = 'Applied'  # Default
        for status, keywords in status_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_status = status.title()
                break
        
        return {
            'new_status': detected_status,
            'email_subject': email_data.get('subject', ''),
            'email_date': email_data.get('date', ''),
            'confidence': 0.5,  # Lower confidence for basic parsing
            'notes': 'Basic keyword parsing used'
        }
    
    def save_to_spreadsheet(self, job_applications: List[JobApplication]) -> bool:
        """Save imported job applications to spreadsheet"""
        try:
            return self.job_tracker.update_spreadsheet(job_applications)
        except Exception as e:
            print(f"❌ Error saving to spreadsheet: {e}")
            return False
    
    def print_import_summary(self, imported_jobs: List[ImportedJob]):
        """Print a summary of imported jobs (showing actual company/position values)"""
        print("\n📊 IMPORT SUMMARY")
        print("=" * 50)
        
        companies = {}
        statuses = {}
        
        for job in imported_jobs:
            # Count by company
            companies[job.company] = companies.get(job.company, 0) + 1
            # Count by status
            statuses[job.status] = statuses.get(job.status, 0) + 1
        
        print(f"Total Applications: {len(imported_jobs)}")
        print(f"Unique Companies: {len(companies)}")
        print(f"Status Distribution: {statuses}")
        
        print("\n📋 Sample Applications:")
        for i, job in enumerate(imported_jobs[:5], 1):
            print(f"{i}. {job.company} - {job.position} ({job.status})")
        
        if len(imported_jobs) > 5:
            print(f"... and {len(imported_jobs) - 5} more")

def main():
    """Main function to demonstrate the import and tracking functionality"""
    print("=== Job Application Import and Tracking ===")
    
    # Initialize tracker
    tracker = JobImportTracker()
    
    # Check for sample files
    sample_files = ['Job Tracker.xlsx', 'sample_jobs.xlsx', 'sample_jobs.csv', 'jobs.xlsx', 'jobs.csv']
    found_files = []
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            found_files.append(file_path)
    
    if found_files:
        print(f"\n📁 Found files: {found_files}")
        
        # Process first found file
        file_path = found_files[0]
        print(f"\n🔄 Processing: {file_path}")
        
        # Import jobs
        if file_path.endswith('.xlsx'):
            imported_jobs = tracker.import_from_excel(file_path)
        else:
            imported_jobs = tracker.import_from_csv(file_path)
        
        if imported_jobs:
            # Print summary
            tracker.print_import_summary(imported_jobs)
            
            # Convert to JobApplication objects
            job_applications = tracker.convert_to_job_applications(imported_jobs)
            
            # Save to spreadsheet
            print(f"\n💾 Saving to spreadsheet...")
            success = tracker.save_to_spreadsheet(job_applications)
            
            if success:
                print("✅ Successfully saved to spreadsheet!")
            else:
                print("❌ Failed to save to spreadsheet")
            
            # Search for status updates
            print(f"\n🔍 Searching for status updates...")
            updates = tracker.search_for_status_updates(imported_jobs)
            
            if updates:
                print(f"\n📬 Found {len(updates)} status updates:")
                for job, update in updates:
                    print(f"   {job.company} - {job.position}: {job.status} → {update['new_status']}")
            else:
                print("   No status updates found")
    
    else:
        print("\n📋 No job files found. To use this script:")
        print("1. Create an Excel/CSV file with your job applications")
        print("2. Include columns like: company, position, application_date, status")
        print("3. Run this script to import and track them")
        
        print("\n📝 Example Excel format:")
        print("| Company | Position | Application Date | Status | Location |")
        print("|---------|----------|------------------|--------|----------|")
        print("| Google  | SWE      | 2024-01-15      | Applied| Mountain View |")
        print("| Microsoft | Developer | 2024-01-16   | Interview | Remote |")

if __name__ == "__main__":
    main() 