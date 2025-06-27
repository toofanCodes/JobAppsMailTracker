#!/usr/bin/env python3
"""
Create sample Excel file for job application import testing
"""

import pandas as pd
import datetime

def create_sample_excel():
    """Create a sample Excel file with job applications"""
    
    # Sample job applications data
    sample_data = [
        {
            'company': 'Google',
            'position': 'Senior Backend Software Engineer',
            'application_date': '2024-01-15',
            'status': 'Applied',
            'location': 'Mountain View, CA',
            'job_type': 'Full-time',
            'experience_level': 'Senior',
            'department': 'Infrastructure',
            'salary_range': '$150,000 - $200,000',
            'notes': 'Applied through company website'
        },
        {
            'company': 'Microsoft',
            'position': 'Frontend Developer',
            'application_date': '2024-01-16',
            'status': 'Interview',
            'location': 'Remote',
            'job_type': 'Full-time',
            'experience_level': 'Mid-level',
            'department': 'Azure',
            'salary_range': '$120,000 - $160,000',
            'notes': 'Interview scheduled for next week'
        },
        {
            'company': 'Apple',
            'position': 'Machine Learning Engineer',
            'application_date': '2024-01-17',
            'status': 'Applied',
            'location': 'Cupertino, CA',
            'job_type': 'Full-time',
            'experience_level': 'Senior',
            'department': 'AI/ML',
            'salary_range': '$140,000 - $180,000',
            'notes': 'Applied through LinkedIn'
        },
        {
            'company': 'Netflix',
            'position': 'Data Scientist',
            'application_date': '2024-01-18',
            'status': 'Rejected',
            'location': 'Los Gatos, CA',
            'job_type': 'Full-time',
            'experience_level': 'Mid-level',
            'department': 'Analytics',
            'salary_range': '$130,000 - $170,000',
            'notes': 'Not selected after technical interview'
        },
        {
            'company': 'Amazon',
            'position': 'Software Development Engineer',
            'application_date': '2024-01-19',
            'status': 'Applied',
            'location': 'Seattle, WA',
            'job_type': 'Full-time',
            'experience_level': 'Entry-level',
            'department': 'AWS',
            'salary_range': '$100,000 - $130,000',
            'notes': 'Applied through Amazon careers portal'
        },
        {
            'company': 'Meta',
            'position': 'Product Manager',
            'application_date': '2024-01-20',
            'status': 'Interview',
            'location': 'Menlo Park, CA',
            'job_type': 'Full-time',
            'experience_level': 'Senior',
            'department': 'Product',
            'salary_range': '$160,000 - $220,000',
            'notes': 'Phone interview completed, waiting for onsite'
        },
        {
            'company': 'LinkedIn',
            'position': 'Data Analyst',
            'application_date': '2024-01-21',
            'status': 'Applied',
            'location': 'Sunnyvale, CA',
            'job_type': 'Full-time',
            'experience_level': 'Mid-level',
            'department': 'Data Science',
            'salary_range': '$110,000 - $140,000',
            'notes': 'Applied through LinkedIn Easy Apply'
        },
        {
            'company': 'Uber',
            'position': 'Backend Engineer',
            'application_date': '2024-01-22',
            'status': 'Applied',
            'location': 'San Francisco, CA',
            'job_type': 'Full-time',
            'experience_level': 'Senior',
            'department': 'Engineering',
            'salary_range': '$140,000 - $180,000',
            'notes': 'Applied through company website'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save to Excel
    excel_file = 'sample_jobs.xlsx'
    df.to_excel(excel_file, index=False, sheet_name='Job Applications')
    
    print(f"✅ Created sample Excel file: {excel_file}")
    print(f"📊 Contains {len(sample_data)} job applications")
    
    # Also create CSV version
    csv_file = 'sample_jobs.csv'
    df.to_csv(csv_file, index=False)
    print(f"✅ Created sample CSV file: {csv_file}")
    
    # Print sample data
    print("\n📋 Sample data preview:")
    print(df.head(3).to_string(index=False))
    
    print(f"\n🎯 You can now run: python import_and_track.py")
    print("   This will import these jobs and search for status updates in your emails!")

if __name__ == "__main__":
    create_sample_excel() 