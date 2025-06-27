#!/usr/bin/env python3
"""
Gemini-powered email parser for job application tracking
Uses Google's Gemini AI to intelligently extract job details from emails
"""

import json
import re
import os
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
import google.generativeai as genai
from datetime import datetime

@dataclass
class ParsedJobDetails:
    """Structured data extracted from email using Gemini"""
    company: str
    position: str
    status: str
    application_date: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, contract, intern
    experience_level: Optional[str] = None  # entry, mid, senior, lead
    department: Optional[str] = None
    confidence_score: float = 0.0
    extraction_notes: str = ""

class GeminiEmailParser:
    """Uses Gemini AI to intelligently parse job application emails"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini parser with API key"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Define the parsing prompt
        self.parsing_prompt = """
You are an expert at extracting job application information from emails. Analyze the email content and extract structured information.

EMAIL CONTENT:
From: {from_email}
Subject: {subject}
Date: {email_date}
Body: {body}

Please extract the following information in JSON format:

{{
    "company": "Company name (extract from email domain, subject, or body)",
    "position": "Job title/position (be specific)",
    "status": "Application status (Applied, Interview, Rejected, Accepted, Withdrawn, Offer)",
    "application_date": "Date when application was submitted (YYYY-MM-DD format, null if not found)",
    "location": "Job location (city, state, country, or remote)",
    "salary_range": "Salary range if mentioned (null if not found)",
    "job_type": "Job type (full-time, part-time, contract, intern, freelance)",
    "experience_level": "Experience level (entry, junior, mid, senior, lead, principal)",
    "department": "Department or team (engineering, marketing, sales, etc.)",
    "confidence_score": 0.95,
    "extraction_notes": "Brief notes about what was extracted and any uncertainties"
}}

IMPORTANT GUIDELINES:
1. Be precise with company names - extract from email domain when possible
2. Job titles should be specific (e.g., "Senior Backend Software Engineer" not just "Software Engineer")
3. Status should reflect the email content (e.g., "Interview" if scheduling interview, "Rejected" if rejection)
4. If information is not found, use null for that field
5. Confidence score should reflect how certain you are (0.0 to 1.0)
6. For multiple positions mentioned, focus on the primary one
7. Consider email context - is this a confirmation, invitation, rejection, etc.?

Return ONLY the JSON object, no additional text.
"""
    
    def parse_email(self, email_data: Dict) -> ParsedJobDetails:
        """Parse email using Gemini AI"""
        try:
            # Extract email components
            from_email = email_data.get('from', '')
            subject = email_data.get('subject', '')
            email_date = email_data.get('date', '')
            body = email_data.get('body', '')
            
            # Clean and prepare content
            cleaned_body = self._clean_email_body(body)
            
            # Create prompt with email content
            prompt = self.parsing_prompt.format(
                from_email=from_email,
                subject=subject,
                email_date=email_date,
                body=cleaned_body[:4000]  # Limit body length for API
            )
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            parsed_data = self._parse_gemini_response(response.text)
            
            # Convert to ParsedJobDetails with robust null handling
            company = self._safe_extract(parsed_data, 'company', 'Unknown Company')
            position = self._safe_extract(parsed_data, 'position', 'Unknown Position')
            status = self._safe_extract(parsed_data, 'status', 'Applied')
            
            # Handle optional fields with defaults
            application_date = parsed_data.get('application_date')
            location = parsed_data.get('location')
            salary_range = parsed_data.get('salary_range')
            job_type = parsed_data.get('job_type')
            experience_level = parsed_data.get('experience_level')
            department = parsed_data.get('department')
            confidence_score = parsed_data.get('confidence_score', 0.0)
            extraction_notes = parsed_data.get('extraction_notes', '')
            
            # If critical fields are missing, try fallback extraction
            if company == 'Unknown Company':
                company = self._extract_company_fallback(from_email, subject, body)
                if extraction_notes:
                    extraction_notes += " | Company extracted via fallback"
                else:
                    extraction_notes = "Company extracted via fallback"
            
            if position == 'Unknown Position':
                position = self._extract_position_fallback(subject, body)
                if extraction_notes:
                    extraction_notes += " | Position extracted via fallback"
                else:
                    extraction_notes = "Position extracted via fallback"
            
            return ParsedJobDetails(
                company=company,
                position=position,
                status=status,
                application_date=application_date,
                location=location,
                salary_range=salary_range,
                job_type=job_type,
                experience_level=experience_level,
                department=department,
                confidence_score=confidence_score,
                extraction_notes=extraction_notes
            )
            
        except Exception as e:
            print(f"Error parsing email with Gemini: {e}")
            # Fallback to basic parsing
            return self._fallback_parsing(email_data)
    
    def _clean_email_body(self, body: str) -> str:
        """Clean email body for better parsing"""
        # Remove HTML tags
        body = re.sub(r'<[^>]+>', '', body)
        
        # Remove excessive whitespace
        body = re.sub(r'\s+', ' ', body)
        
        # Remove common email signatures
        body = re.sub(r'--\s*\n.*', '', body, flags=re.DOTALL)
        
        # Remove quoted text
        body = re.sub(r'>.*', '', body)
        
        return body.strip()
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini's JSON response"""
        try:
            # Extract JSON from response (handle cases where Gemini adds extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                
                # Debug: Log if critical fields are missing
                missing_fields = []
                if not parsed_data.get('company') or parsed_data.get('company') == 'null':
                    missing_fields.append('company')
                if not parsed_data.get('position') or parsed_data.get('position') == 'null':
                    missing_fields.append('position')
                
                if missing_fields:
                    print(f"⚠️ Gemini parsing warning: Missing fields: {missing_fields}")
                    print(f"   Raw response: {response_text[:200]}...")
                
                return parsed_data
            else:
                print(f"❌ No JSON found in Gemini response")
                print(f"   Raw response: {response_text}")
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"❌ Error parsing Gemini response: {e}")
            print(f"   Raw response: {response_text}")
            return {}
    
    def _safe_extract(self, data: Dict, key: str, default: str) -> str:
        """Safely extract a value from parsed data, handling None and empty strings"""
        value = data.get(key)
        if value is None or value == '' or value == 'null':
            return default
        return str(value).strip()
    
    def _extract_company_fallback(self, from_email: str, subject: str, body: str) -> str:
        """Fallback company extraction when Gemini fails"""
        # Try email domain first
        if '@' in from_email:
            domain = from_email.split('@')[1].split('.')[0]
            if domain not in ['gmail', 'yahoo', 'hotmail', 'outlook', 'aol']:
                return domain.title()
        
        # Try subject line for company names
        subject_upper = subject.upper()
        common_indicators = ['AT ', 'FOR ', 'WITH ', 'VIA ', 'FROM ']
        for indicator in common_indicators:
            if indicator in subject_upper:
                parts = subject_upper.split(indicator)
                if len(parts) > 1:
                    company_part = parts[1].split()[0]
                    return company_part.title()
        
        return "Unknown Company"
    
    def _extract_position_fallback(self, subject: str, body: str) -> str:
        """Fallback position extraction when Gemini fails"""
        # Look for common job title patterns in subject
        subject_lower = subject.lower()
        
        # Common job title keywords
        job_keywords = [
            'analyst', 'engineer', 'developer', 'manager', 'specialist',
            'coordinator', 'associate', 'assistant', 'director', 'lead',
            'architect', 'consultant', 'advisor', 'supervisor', 'coordinator'
        ]
        
        for keyword in job_keywords:
            if keyword in subject_lower:
                # Extract the phrase containing the keyword
                words = subject.split()
                for i, word in enumerate(words):
                    if keyword.lower() in word.lower():
                        # Get surrounding words for context
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        position = ' '.join(words[start:end])
                        return position
        
        # If no keyword found, try to extract from subject
        if 'position' in subject_lower or 'role' in subject_lower or 'job' in subject_lower:
            # Extract text after these keywords
            for keyword in ['position', 'role', 'job']:
                if keyword in subject_lower:
                    parts = subject_lower.split(keyword)
                    if len(parts) > 1:
                        position_part = parts[1].strip()
                        if position_part:
                            return position_part.title()
        
        return "Unknown Position"
    
    def _fallback_parsing(self, email_data: Dict) -> ParsedJobDetails:
        """Fallback parsing when Gemini fails"""
        from_email = email_data.get('from', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        
        # Basic company extraction
        company = self._extract_company_basic(from_email, subject)
        
        # Basic position extraction
        position = self._extract_position_basic(subject, body)
        
        # Basic status extraction
        status = self._determine_status_basic(subject, body)
        
        return ParsedJobDetails(
            company=company,
            position=position,
            status=status,
            confidence_score=0.3,
            extraction_notes="Fallback parsing used due to Gemini error"
        )
    
    def _extract_company_basic(self, from_email: str, subject: str) -> str:
        """Basic company extraction as fallback"""
        # Try email domain first
        if '@' in from_email:
            domain = from_email.split('@')[1].split('.')[0]
            if domain not in ['gmail', 'yahoo', 'hotmail', 'outlook']:
                return domain.title()
        
        # Try subject line
        subject_upper = subject.upper()
        common_indicators = ['AT ', 'FOR ', 'WITH ', 'VIA ']
        for indicator in common_indicators:
            if indicator in subject_upper:
                parts = subject_upper.split(indicator)
                if len(parts) > 1:
                    company_part = parts[1].split()[0]
                    return company_part.title()
        
        return "Unknown Company"
    
    def _extract_position_basic(self, subject: str, body: str) -> str:
        """Basic position extraction as fallback"""
        position_indicators = [
            'software engineer', 'developer', 'programmer', 'data scientist',
            'analyst', 'manager', 'director', 'lead', 'architect', 'consultant'
        ]
        
        text = f"{subject} {body}".lower()
        for indicator in position_indicators:
            if indicator in text:
                words = text.split()
                for i, word in enumerate(words):
                    if indicator in word.lower():
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        position = ' '.join(words[start:end])
                        return position.title()
        
        return "Unknown Position"
    
    def _determine_status_basic(self, subject: str, body: str) -> str:
        """Basic status determination as fallback"""
        text = f"{subject} {body}".lower()
        
        status_keywords = {
            'rejected': ['rejected', 'not selected', 'unfortunately', 'regret'],
            'interview': ['interview', 'schedule', 'meeting', 'call'],
            'accepted': ['accepted', 'congratulations', 'welcome', 'offer'],
            'withdrawn': ['withdrawn', 'cancelled', 'no longer interested']
        }
        
        for status, keywords in status_keywords.items():
            if any(keyword in text for keyword in keywords):
                return status.title()
        
        return 'Applied'
    
    def batch_parse_emails(self, email_list: List[Dict]) -> List[ParsedJobDetails]:
        """Parse multiple emails in batch"""
        results = []
        for i, email_data in enumerate(email_list):
            print(f"Parsing email {i+1}/{len(email_list)}...")
            parsed = self.parse_email(email_data)
            results.append(parsed)
        return results

def test_gemini_parser():
    """Test the Gemini parser with sample emails"""
    # You'll need to set GEMINI_API_KEY environment variable
    try:
        parser = GeminiEmailParser()
        
        # Sample email data
        test_emails = [
            {
                'from': 'recruiter@google.com',
                'subject': 'Application Confirmation - Senior Backend Software Engineer',
                'date': '2024-01-15T10:00:00',
                'body': 'Thank you for your application to Google for the Senior Backend Software Engineer position. We have received your application and will review it within the next week.'
            },
            {
                'from': 'careers@microsoft.com',
                'subject': 'Interview Invitation - Frontend Developer Role',
                'date': '2024-01-16T14:30:00',
                'body': 'Congratulations! We would like to invite you for an interview for the Frontend Developer position at Microsoft. Please schedule a time that works for you.'
            },
            {
                'from': 'noreply@linkedin.com',
                'subject': 'Your application was sent to Apple Inc.',
                'date': '2024-01-17T09:15:00',
                'body': 'Your application for the Machine Learning Engineer position at Apple has been successfully submitted. The hiring team will review your application.'
            }
        ]
        
        print("Testing Gemini Email Parser...")
        for i, email in enumerate(test_emails):
            print(f"\n--- Email {i+1} ---")
            parsed = parser.parse_email(email)
            print(f"Company: {parsed.company}")
            print(f"Position: {parsed.position}")
            print(f"Status: {parsed.status}")
            print(f"Confidence: {parsed.confidence_score}")
            print(f"Notes: {parsed.extraction_notes}")
            
    except Exception as e:
        print(f"Error testing Gemini parser: {e}")
        print("Make sure GEMINI_API_KEY environment variable is set")

if __name__ == "__main__":
    test_gemini_parser() 