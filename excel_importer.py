#!/usr/bin/env python3
"""
Excel/CSV Job Application Importer
Imports job applications from Excel/CSV files and integrates with email tracking
"""

import pandas as pd
import os
import json
import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from job_tracker import JobTracker, JobApplication
from gemini_parser import GeminiEmailParser

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
    email_id: str = ""
    email_date: str = ""

class ExcelJobImporter:
    """Imports job applications from Excel/CSV files and integrates with email tracking"""
    
    def __init__(self, job_tracker: JobTracker):
        self.job_tracker = job_tracker
        self.gemini_parser = None
        try:
            self.gemini_parser = GeminiEmailParser()
        except:
            pass  # Use basic parsing if Gemini not available
    
    def import_from_excel(self, file_path: str, sheet_name: str = None) -> List[ImportedJob]:
        """Import job applications from Excel file"""
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            print(f"📊 Loaded {len(df)} rows from {file_path}")
            
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
            
            # Map columns to expected format
            mapped_jobs = self._map_columns(df)
            
            print(f"✅ Successfully imported {len(mapped_jobs)} job applications")
            return mapped_jobs
            
        except Exception as e:
            print(f"❌ Error importing from CSV: {e}")
            return []
    
    def _map_columns(self, df: pd.DataFrame) -> List[ImportedJob]:
        """Map DataFrame columns to ImportedJob objects"""
        jobs = []
        
        # Common column name mappings
        column_mappings = {
            'company': ['company', 'company_name', 'employer', 'organization'],
            'position': ['position', 'job_title', 'role', 'title', 'job_position'],
            'application_date': ['application_date', 'applied_date', 'date_applied', 'date'],
            'status': ['status', 'application_status', 'current_status'],
            'location': ['location', 'job_location', 'city', 'state'],
            'job_type': ['job_type', 'employment_type', 'type', 'full_time'],
            'experience_level': ['experience_level', 'level', 'seniority', 'seniority_level'],
            'department': ['department', 'team', 'division'],
            'salary_range': ['salary_range', 'salary', 'compensation'],
            'notes': ['notes', 'comments', 'description', 'details']
        }
        
        # Find actual column names in the DataFrame
        actual_columns = {}
        for field, possible_names in column_mappings.items():
            for col_name in possible_names:
                if col_name.lower() in [col.lower() for col in df.columns]:
                    actual_columns[field] = col_name
                    break
        
        print(f"🔍 Detected columns: {actual_columns}")
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Extract values with fallbacks
                company = self._get_value(row, actual_columns.get('company'), 'Unknown Company')
                position = self._get_value(row, actual_columns.get('position'), 'Unknown Position')
                application_date = self._get_value(row, actual_columns.get('application_date'), '')
                status = self._get_value(row, actual_columns.get('status'), 'Applied')
                location = self._get_value(row, actual_columns.get('location'), '')
                job_type = self._get_value(row, actual_columns.get('job_type'), '')
                experience_level = self._get_value(row, actual_columns.get('experience_level'), '')
                department = self._get_value(row, actual_columns.get('department'), '')
                salary_range = self._get_value(row, actual_columns.get('salary_range'), '')
                notes = self._get_value(row, actual_columns.get('notes'), '')
                
                # Convert empty strings to None for optional fields
                location = location if location != '' else None
                job_type = job_type if job_type != '' else None
                experience_level = experience_level if experience_level != '' else None
                department = department if department != '' else None
                salary_range = salary_range if salary_range != '' else None
                
                # Normalize application date
                if application_date:
                    application_date = self._normalize_date(application_date)
                else:
                    application_date = datetime.datetime.now().isoformat()
                
                # Create ImportedJob object
                job = ImportedJob(
                    company=company,
                    position=position,
                    application_date=application_date,
                    status=status,
                    location=location,
                    job_type=job_type,
                    experience_level=experience_level,
                    department=department,
                    salary_range=salary_range,
                    notes=notes
                )
                
                jobs.append(job)
                
            except Exception as e:
                print(f"⚠️ Error processing row {index}: {e}")
                continue
        
        return jobs
    
    def _get_value(self, row: pd.Series, column_name: Optional[str], default: str) -> str:
        """Safely get value from DataFrame row"""
        if column_name and column_name in row:
            value = row[column_name]
            if pd.isna(value):
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
                parsed_date = pd.to_datetime(date_value)
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
                email_id=imported_job.email_id,
                email_date=imported_job.email_date,
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
        
        # Get all job application emails
        try:
            emails = self.job_tracker.search_job_emails()
            print(f"📧 Found {len(emails)} job-related emails to search")
            
            for imported_job in imported_jobs:
                # Search for emails related to this job
                matching_emails = self._find_matching_emails(imported_job, emails)
                
                if matching_emails:
                    print(f"📬 Found {len(matching_emails)} emails for {imported_job.company} - {imported_job.position}")
                    
                    for email_data in matching_emails:
                        # Parse email to get status update
                        if self.gemini_parser:
                            parsed_details = self.gemini_parser.parse_email(email_data)
                            status_update = {
                                'new_status': parsed_details.status,
                                'email_subject': email_data.get('subject', ''),
                                'email_date': email_data.get('date', ''),
                                'confidence': parsed_details.confidence_score,
                                'ai_notes': parsed_details.extraction_notes
                            }
                        else:
                            # Use basic parsing
                            status_update = self._basic_status_extraction(email_data)
                        
                        updates.append((imported_job, status_update))
                        
        except Exception as e:
            print(f"❌ Error searching for status updates: {e}")
        
        return updates
    
    def _find_matching_emails(self, imported_job: ImportedJob, emails: List[Dict]) -> List[Dict]:
        """Find emails that match the imported job"""
        matching_emails = []
        
        # Create search terms
        company_terms = [imported_job.company.lower()]
        position_terms = [imported_job.position.lower()]
        
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
            
            # If both company and position match, it's likely related
            if company_match and position_match:
                matching_emails.append(email_data)
        
        return matching_emails
    
    def _basic_status_extraction(self, email_data: Dict) -> Dict:
        """Basic status extraction when Gemini is not available"""
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
            'ai_notes': 'Basic keyword parsing used'
        }

def main():
    """Main function to demonstrate Excel import functionality"""
    print("=== Excel Job Application Importer ===")
    
    # Initialize job tracker
    tracker = JobTracker()
    
    # Initialize importer
    importer = ExcelJobImporter(tracker)
    
    # Example usage
    print("\n📋 Example usage:")
    print("1. Import from Excel: importer.import_from_excel('my_jobs.xlsx')")
    print("2. Import from CSV: importer.import_from_csv('my_jobs.csv')")
    print("3. Search for updates: importer.search_for_status_updates(imported_jobs)")
    
    # Check for sample files
    sample_files = ['sample_jobs.xlsx', 'sample_jobs.csv', 'jobs.xlsx', 'jobs.csv']
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            print(f"\n📁 Found sample file: {file_path}")
            print("Run the importer to process this file!")

if __name__ == "__main__":
    main() 