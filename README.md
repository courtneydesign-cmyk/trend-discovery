# Trend Discovery System

A self-learning trend intelligence tool for menswear graphics and activewear. This system learns your taste through interaction and generates actionable design intelligence.

## Features

- **Daily Feed**: AI-curated trend items that learn from your votes
- **Keep/Skip Learning**: System adapts to your preferences over time
- **Weekly Intelligence**: Automated pattern analysis every Sunday
- **Tee Concepts**: Range-ready design concepts from your kept items
- **"Why You're Seeing This"**: Transparent AI explanations for each item

## Quick Start

### 1. Set Up Supabase

1. Go to [https://supabase.com](https://supabase.com) and create a free account
2. Create a new project (choose a region close to you)
3. Wait for the database to provision (~2 minutes)
4. In your project, go to **SQL Editor**
5. Copy and paste the entire contents of `supabase_schema.sql`
6. Click **Run** to create all tables and functions
7. Go to **Settings** → **API** and copy:
   - Project URL (looks like: `https://xxxxx.supabase.co`)
   - `anon public` key (long string starting with `eyJ...`)

### 2. Configure GitHub Repository

1. Your repository is already created at: `https://github.com/courtneydesign-cmyk/trend-discovery`
2. Upload all the files from this folder to your repository
3. Go to **Settings** → **Secrets and variables** → **Actions**
4. Click **New repository secret** and add:
   - Name: `SUPABASE_URL`
   - Value: Your Supabase project URL
5. Click **New repository secret** again:
   - Name: `SUPABASE_ANON_KEY`
   - Value: Your Supabase anon key

### 3. Configure Frontend

Edit `site/app.js` and replace the first two lines:

```javascript
const SUPABASE_URL = 'YOUR_SUPABASE_URL'; // Replace with your actual URL
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY'; // Replace with your actual key
```

### 4. Enable GitHub Pages

1. Go to your repository **Settings** → **Pages**
2. Under **Source**, select **Deploy from a branch**
3. Under **Branch**, select **main** and **/site** folder
4. Click **Save**
5. Your site will be live at: `https://courtneydesign-cmyk.github.io/trend-discovery/`

### 5. Run First Data Collection

1. Go to **Actions** tab in your repository
2. Click **Daily Trend Update** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait 2-3 minutes for it to complete
5. Visit your GitHub Pages URL to see your feed!

## How to Use

### Daily Feed
- Browse trend items curated to your aesthetic preferences
- Click **✓ Keep** to save items and teach the system your taste
- Click **✕ Skip** to remove items and refine preferences
- Click "Why you're seeing this" to understand the AI's reasoning

### Saved Items
- View all items you've kept
- Reference saved trends for design inspiration
- Track your taste evolution over time

### Weekly Intelligence
- **Emerging Patterns**: Updated every Sunday with trend analysis
- **10 Tee Concepts**: Range-ready designs generated from your keeps
- Each concept includes: placement, motifs, slogans, print style, colorways

## Customization

### Add More RSS Feeds
Edit `sources.yml`:
```yaml
feeds:
  - url: "https://example.com/feed"
    name: "Your Source Name"
```

### Adjust Cluster Tags
Edit `trend_bot.py` → `CLUSTER_TAGS` dictionary to add/modify aesthetic clusters.

### Change Quality Filters
Edit `trend_bot.py` → `QUALITY_SIGNALS` to adjust what content passes the filter.

## Automation Schedule

- **Daily**: Runs at 8 AM UTC (collects new items, updates feed)
- **Weekly**: Runs at 10 AM UTC on Sundays (generates intelligence)
- **Manual**: Run workflows anytime from the Actions tab

## Troubleshooting

**No items in feed?**
- Check that workflows have run successfully in Actions tab
- Verify Supabase secrets are set correctly
- Check RSS feeds in `sources.yml` are accessible

**Voting not working?**
- Verify `site/app.js` has correct Supabase credentials
- Check browser console for errors (F12)
- Ensure Supabase functions were created properly

**Weekly intelligence empty?**
- Need at least 3 keep votes in the past 7 days
- Run the weekly workflow manually from Actions tab

## Architecture

```
trend-discovery/
├── trend_bot.py          # Daily RSS parsing & feed generation
├── weekly_bot.py         # Weekly pattern analysis & concept generation
├── sources.yml           # RSS feed configuration
├── requirements.txt      # Python dependencies
├── supabase_schema.sql   # Database schema & functions
├── .github/workflows/    # GitHub Actions automation
│   ├── daily.yml
│   └── weekly.yml
└── site/                 # GitHub Pages frontend
    ├── index.html        # Daily feed
    ├── saved.html        # Kept items
    ├── week.html         # Weekly intelligence
    ├── app.js            # Frontend logic
    └── styles.css        # Styling
```

## Technical Details

**Backend**: Python + Supabase (PostgreSQL)
**Frontend**: Vanilla HTML/CSS/JS
**Automation**: GitHub Actions
**Hosting**: GitHub Pages (static)

**Learning Algorithm**:
- Tag weights increase with keeps (+0.2), decrease with skips (-0.1)
- Tag pair weights track co-occurring preferences (+0.3)
- Personalized scoring combines cluster relevance + learned weights

## Privacy & Data

- All data stored in your Supabase project
- No external tracking or analytics
- Your votes and preferences are private to your database

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review GitHub Actions logs for error details
3. Check Supabase logs in your project dashboard

## License

MIT License - Free to use and modify for personal or commercial projects.
