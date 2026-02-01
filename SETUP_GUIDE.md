# Quick Setup Guide

## Step-by-Step Setup (15 minutes)

### Step 1: Set Up Supabase (5 min)

1. Go to https://supabase.com
2. Sign up / Log in
3. Click "New Project"
4. Fill in:
   - Name: `trend-discovery`
   - Database Password: (choose a strong password)
   - Region: (choose closest to you)
5. Click "Create new project" and wait ~2 minutes

**Run SQL Schema:**
1. In Supabase dashboard, click "SQL Editor" (left sidebar)
2. Click "New query"
3. Open `supabase_schema.sql` from this folder
4. Copy ALL contents and paste into Supabase SQL Editor
5. Click "Run" (or press Cmd/Ctrl + Enter)
6. You should see "Success. No rows returned"

**Get Your Credentials:**
1. Click "Settings" (gear icon, bottom left)
2. Click "API" in settings menu
3. Copy these two values:
   - **Project URL** (e.g., `https://abcdefgh.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)
4. Keep these handy for next steps!

### Step 2: Upload Files to GitHub (3 min)

Your repository already exists at:
https://github.com/courtneydesign-cmyk/trend-discovery

**Upload all files:**
1. Go to your repository on GitHub
2. Click "Add file" → "Upload files"
3. Drag ALL files from this `trend-discovery` folder
4. Commit message: "Initial setup"
5. Click "Commit changes"

### Step 3: Add Secrets to GitHub (2 min)

1. In your GitHub repository, click "Settings"
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add first secret:
   - Name: `SUPABASE_URL`
   - Secret: [paste your Supabase Project URL]
   - Click "Add secret"
5. Click "New repository secret" again
6. Add second secret:
   - Name: `SUPABASE_ANON_KEY`
   - Secret: [paste your Supabase anon key]
   - Click "Add secret"

### Step 4: Configure Frontend (2 min)

1. In GitHub, click on `site/app.js`
2. Click the pencil icon (Edit)
3. Find lines 2-3:
   ```javascript
   const SUPABASE_URL = 'YOUR_SUPABASE_URL';
   const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';
   ```
4. Replace with your actual values:
   ```javascript
   const SUPABASE_URL = 'https://abcdefgh.supabase.co';
   const SUPABASE_KEY = 'eyJ...your actual key...';
   ```
5. Scroll down, commit message: "Add Supabase credentials"
6. Click "Commit changes"

### Step 5: Enable GitHub Pages (1 min)

1. Go to "Settings" → "Pages"
2. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/site**
3. Click "Save"
4. Wait 1-2 minutes for deployment

### Step 6: Run First Collection (2 min)

1. Go to "Actions" tab
2. Click "Daily Trend Update" on the left
3. Click "Run workflow" button (top right)
4. Click the green "Run workflow" button
5. Wait 2-3 minutes for workflow to complete
6. Green checkmark = success!

### Step 7: Visit Your Site! 🎉

Your site is now live at:
https://courtneydesign-cmyk.github.io/trend-discovery/

You should see:
- Trend items in a grid
- Keep/Skip buttons
- Tag clusters on each item

## What's Next?

1. **Start Voting**: Keep items you like, skip items you don't
2. **Wait for Sunday**: Weekly intelligence generates automatically
3. **Check Saved**: View all your kept items in the Saved tab
4. **Review Intel**: Check Weekly Intel tab after Sunday for patterns

## Customization

### Add Your Own RSS Feeds

Edit `sources.yml`:
```yaml
feeds:
  - url: "https://your-feed-url.com/rss"
    name: "Your Source Name"
```

### Change Aesthetics

Edit `trend_bot.py` line 13-20:
```python
CLUSTER_TAGS = {
    'your_tag': ['keyword1', 'keyword2', 'keyword3'],
    # Add more clusters...
}
```

## Need Help?

**No items showing?**
- Check Actions tab → Daily Trend Update → View logs
- Verify secrets are set correctly

**Voting doesn't work?**
- Check browser console (F12)
- Verify app.js has correct Supabase credentials

**Weekly intel empty?**
- Need at least 3 votes in past 7 days
- Run weekly workflow manually from Actions

## System is Now Running!

✅ Daily collection at 8 AM UTC
✅ Weekly intelligence at 10 AM UTC Sundays
✅ Learning from your votes automatically
✅ Generating design concepts based on your taste
