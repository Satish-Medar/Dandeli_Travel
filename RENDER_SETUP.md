# Render Deployment - Environment Variables Setup

## Quick Fix for Current Deployment Error

The deployment is failing because **API keys are not set as environment variables** in Render.

### ✅ Steps to Fix

#### 1. Go to Render Dashboard

- Visit: https://dashboard.render.com/
- Select your `Dandeli_Travel` service

#### 2. Navigate to Environment Variables

- Click on the service → **Settings** tab
- Scroll to **Environment** section
- Click **Add Environment Variable**

#### 3. Add These Environment Variables

Copy and paste your actual API keys (replace with your real keys):

| Variable           | Value                          |
| ------------------ | ------------------------------ |
| `GROQ_API_KEY_1`   | Your Groq API key #1           |
| `GROQ_API_KEY_2`   | Your Groq API key #2           |
| `GROQ_API_KEY_3`   | Your Groq API key #3           |
| `GOOGLE_API_KEY_1` | Your Google API key #1         |
| `GOOGLE_API_KEY_2` | Your Google API key #2         |
| `GOOGLE_API_KEY_3` | Your Google API key #3         |
| `GOOGLE_API_KEY`   | Your primary Google API key    |
| `GROQ_API_KEY`     | Your primary Groq API key      |
| `MONGODB_URI`      | Your MongoDB connection string |

#### 4. Redeploy

- Click **Manual Deploy** or **Deploy** button
- Wait for the new deployment to complete

---

## Recommended: Use Environment-Based Configuration

Instead of copy-pasting, use this safer approach:

### Option A: Create `.env` Template File

Create a `render.example.env` file:

```env
# Copy this to .env and fill in your actual values
# DO NOT commit .env file to git
GROQ_API_KEY_1=your_groq_api_key_1
GROQ_API_KEY_2=your_groq_api_key_2
GROQ_API_KEY_3=your_groq_api_key_3
GOOGLE_API_KEY_1=your_google_api_key_1
GOOGLE_API_KEY_2=your_google_api_key_2
GOOGLE_API_KEY_3=your_google_api_key_3
GOOGLE_API_KEY=your_primary_google_key
GROQ_API_KEY=your_primary_groq_key
MONGODB_URI=your_mongodb_connection_string
```

### Option B: Set via Render CLI

```bash
# Install Render CLI
npm install -g @render-com/cli

# Login to Render
render login

# Set environment variables
render env set GROQ_API_KEY_1 "your_key_here" -s dandeli-travel-api
```

---

## Error Explanation

**Current Error:**

```
ValidationError: Value error, API key required for Gemini!
```

**Why it happens:**

- Code tries to load API keys from environment variables
- Render deployment doesn't have these variables set
- Application crashes during startup

**Solution:**

- Set the environment variables in Render dashboard (this step)
- Application will load keys from environment variables
- Deployment will succeed

---

## Troubleshooting

**Still getting API key errors?**

1. Verify all environment variable keys are spelled **exactly** as shown
2. Check that values are **not** wrapped in quotes in Render dashboard
3. Click **Manual Deploy** again after setting variables
4. Check deployment logs in Render dashboard

**Check logs:**

- Go to **Logs** tab in Render dashboard
- Look for any "API key" or "environment variable" errors
