# Gemini AI Integration Setup Guide

## 🚀 Overview

The JobAppsMailTracker now includes **Gemini AI integration** for intelligent email parsing! This replaces the basic keyword-based parsing with AI-powered understanding that can extract much more detailed and accurate information from job application emails.

## 🎯 Benefits of Gemini Integration

### **Before (Basic Parsing):**
- Simple keyword matching
- Limited context understanding
- Basic company/position extraction
- No confidence scoring
- Misses nuanced information

### **After (Gemini AI):**
- **Intelligent context understanding**
- **Accurate company extraction** from email domains and content
- **Detailed position information** with seniority levels
- **Location detection** (remote, onsite, hybrid)
- **Job type classification** (full-time, part-time, contract, intern)
- **Department identification** (engineering, marketing, sales, etc.)
- **Experience level detection** (entry, junior, mid, senior, lead)
- **Confidence scoring** for extraction quality
- **Graceful fallback** to basic parsing if AI fails

## 🔧 Setup Instructions

### **Step 1: Get Gemini API Key**

1. **Visit Google AI Studio:**
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Sign in with your Google account

2. **Create API Key:**
   - Click on "Get API key" in the top right
   - Choose "Create API key in new project" or use existing project
   - Copy the generated API key

3. **API Key Format:**
   ```
   AIzaSyC... (long string of characters)
   ```

### **Step 2: Set Environment Variable**

#### **On macOS/Linux:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

#### **On Windows:**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

#### **Permanent Setup (Recommended):**

**macOS/Linux:**
```bash
# Add to your shell profile (~/.zshrc, ~/.bashrc, etc.)
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
- Add to System Environment Variables
- Or create a `.env` file in the project directory

### **Step 3: Test the Integration**

Run the test script to verify Gemini is working:

```bash
python test_gemini_integration.py
```

You should see output like:
```
✅ Gemini AI available - testing intelligent parsing...
🤖 Using Gemini AI for intelligent email parsing...
```

## 📊 Example Comparison

### **Sample Email:**
```
From: recruiter@google.com
Subject: Application Confirmation - Senior Backend Software Engineer, Infrastructure Team
Body: Thank you for your application to Google for the Senior Backend Software Engineer 
position on our Infrastructure team. This is a full-time position based in Mountain View, 
CA with a competitive salary range of $150,000 - $200,000.
```

### **Basic Parsing Results:**
```
Company: Google
Position: Software Engineer
Status: Applied
Notes: Subject: Application Confirmation - Senior Backend Software Engineer, Infrastructure Team | Basic parsing used
```

### **Gemini AI Results:**
```
Company: Google
Position: Senior Backend Software Engineer
Status: Applied
Location: Mountain View, CA
Job Type: full-time
Experience Level: senior
Department: Infrastructure
Confidence: 0.95
AI Notes: Successfully extracted detailed position information including seniority level, location, and department
```

## 🔄 How It Works

### **1. Automatic Detection:**
The job tracker automatically detects if Gemini is available:
- If `GEMINI_API_KEY` is set → Uses Gemini AI parsing
- If not set or fails → Falls back to basic parsing

### **2. Intelligent Parsing:**
Gemini analyzes the email content and extracts:
- **Company name** (from domain, subject, or body)
- **Job position** (with full title and context)
- **Application status** (based on email content)
- **Location** (city, state, remote, etc.)
- **Job type** (full-time, part-time, contract, intern)
- **Experience level** (entry, junior, mid, senior, lead)
- **Department** (engineering, marketing, sales, etc.)
- **Confidence score** (how certain the AI is)

### **3. Enhanced Notes:**
The system creates rich notes with all extracted information:
```
Subject: Application Confirmation - Senior Backend Software Engineer, Infrastructure Team | 
Location: Mountain View, CA | Type: full-time | Level: senior | Dept: Infrastructure | 
AI Confidence: 0.95 | AI Notes: Successfully extracted detailed position information
```

## 🛠️ Configuration

### **Environment Variables:**
```bash
GEMINI_API_KEY=your_api_key_here
```

### **Optional Settings:**
You can customize the Gemini model in `gemini_parser.py`:
```python
# Change model if needed
self.model = genai.GenerativeModel('gemini-1.5-flash')  # or 'gemini-1.5-pro'
```

## 🧪 Testing

### **Test Basic vs AI Parsing:**
```bash
python test_gemini_integration.py
```

### **Test with Real Emails:**
```bash
python job_tracker.py
```

Look for these indicators in the output:
- `🤖 Using Gemini AI for intelligent email parsing...` = AI active
- `⚠️ Gemini not available, using basic parsing` = Fallback mode
- `Source: Gmail (Gemini AI)` = AI was used
- `Source: Gmail (Basic)` = Basic parsing was used

## 💰 Cost Considerations

### **Gemini API Pricing:**
- **Free Tier:** 15 requests per minute, 1,500 requests per day
- **Paid Tier:** $0.00025 per 1K characters input, $0.0005 per 1K characters output

### **Typical Usage:**
- **Job application email:** ~500-1000 characters
- **Cost per email:** ~$0.0001-0.0002
- **100 emails per month:** ~$0.01-0.02

### **Cost Optimization:**
- The system only uses Gemini for new emails
- Processed emails are skipped
- Fallback to basic parsing if API limits are reached

## 🚨 Troubleshooting

### **Common Issues:**

1. **"Gemini API key required"**
   - Set the `GEMINI_API_KEY` environment variable
   - Restart your terminal after setting

2. **"API quota exceeded"**
   - Wait for quota reset (usually daily)
   - System will automatically fall back to basic parsing

3. **"Invalid API key"**
   - Check your API key format
   - Ensure it starts with "AIzaSy"

4. **"Network error"**
   - Check your internet connection
   - System will fall back to basic parsing

### **Fallback Behavior:**
The system is designed to be robust:
- **Gemini fails** → Uses basic parsing
- **API quota exceeded** → Uses basic parsing
- **Network issues** → Uses basic parsing
- **Invalid key** → Uses basic parsing

## 🎉 Success Indicators

When Gemini is working correctly, you'll see:
- `🤖 Using Gemini AI for intelligent email parsing...`
- Rich notes with location, job type, experience level
- High confidence scores (0.8-1.0)
- `Source: Gmail (Gemini AI)` in the output

## 📈 Performance Comparison

| Feature | Basic Parsing | Gemini AI |
|---------|---------------|-----------|
| **Company Extraction** | Domain only | Domain + context |
| **Position Details** | Basic keywords | Full title + context |
| **Location Detection** | ❌ No | ✅ Yes |
| **Job Type** | ❌ No | ✅ Yes |
| **Experience Level** | ❌ No | ✅ Yes |
| **Department** | ❌ No | ✅ Yes |
| **Confidence Scoring** | ❌ No | ✅ Yes |
| **Context Understanding** | ❌ Limited | ✅ Advanced |

The Gemini integration transforms your job tracker from a basic email processor into an intelligent job application analyzer! 🚀 