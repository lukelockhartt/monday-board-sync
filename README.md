# Monday.com Board Sync Script

Automatically syncs data from your Main Board to a duplicate board daily using GitHub Actions (100% free).

## Overview

This script:
1. Pulls all items from the **Main Board** (ID: 18269603341)
2. Extracts the `column_id` (client ID) from each item
3. Checks the **Duplicate Board** (ID: 18399599376) for matching `source_item_id`
4. Updates existing items or creates new ones
5. Handles all column types (status, people, dates, etc.)

## Setup Instructions

### Step 1: Get Your Monday.com API Token

1. Go to your Monday.com workspace
2. Click your profile picture → **Admin** → **API**
3. Generate a new API token (or use existing one)
4. Copy the token - you'll need it in Step 3

### Step 2: Create GitHub Repository

1. Initialize git in this directory:
   ```bash
   cd /Users/squarecowmoovers/Documents/tbs
   git init
   git add .
   git commit -m "Initial commit: Monday.com sync script"
   ```

2. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Name it (e.g., `monday-board-sync`)
   - Choose **Private** (recommended for security)
   - Don't initialize with README (we already have one)
   - Click **Create repository**

3. Push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/monday-board-sync.git
   git branch -M main
   git push -u origin main
   ```

### Step 3: Configure GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these secrets:

   | Name | Value |
   |------|-------|
   | `MONDAY_API_TOKEN` | Your Monday.com API token from Step 1 |
   | `SOURCE_BOARD_ID` | `18269603341` |
   | `DEST_BOARD_ID` | `18399599376` |
   | `CLIENT_ID_COLUMN` | `pulse_id_mkxvh6ca` |

### Step 4: Enable GitHub Actions

1. Go to your repository's **Actions** tab
2. If prompted, click **I understand my workflows, go ahead and enable them**
3. You should see the workflow "Daily Monday.com Board Sync"

### Step 5: Test the Sync

Before waiting for the scheduled run, test it manually:

1. Go to **Actions** tab
2. Click **Daily Monday.com Board Sync**
3. Click **Run workflow** → **Run workflow**
4. Wait for it to complete (usually 30-60 seconds)
5. Check the logs to verify success
6. Verify your duplicate board has been updated

## Schedule

The sync runs automatically at **2:00 AM UTC** every day. To change the schedule:

1. Edit `.github/workflows/daily_sync.yml`
2. Modify the cron expression:
   ```yaml
   schedule:
     - cron: '0 2 * * *'  # Minute Hour Day Month DayOfWeek
   ```

**Examples:**
- `'0 2 * * *'` - 2:00 AM UTC daily
- `'0 14 * * *'` - 2:00 PM UTC daily (9 AM EST)
- `'0 6 * * 1-5'` - 6:00 AM UTC, Monday-Friday only

## Local Testing (Optional)

If you want to test locally before pushing to GitHub:

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your API token:
   ```
   MONDAY_API_TOKEN=your_actual_token_here
   ```

4. Run the script:
   ```bash
   python monday_sync.py
   ```

5. Check `monday_sync.log` for results

## Monitoring

### View Sync Logs

1. Go to **Actions** tab in GitHub
2. Click on any workflow run
3. Click **sync** job to see detailed logs
4. Download logs artifact for detailed analysis

### What Gets Logged

- Number of items retrieved from each board
- Items created, updated, or skipped
- Any errors encountered
- Total sync statistics

## Troubleshooting

### "MONDAY_API_TOKEN environment variable not set"
- Make sure you added the secret in GitHub Settings → Secrets
- Secret names are case-sensitive

### "API errors" or "403 Forbidden"
- Check your API token is valid
- Ensure the token has access to both boards
- Regenerate token if needed

### Items not syncing
- Verify the `column_id` exists in your Main Board
- Check that items have a value in the `column_id` column
- Review logs for specific error messages

### Workflow not running
- Check that GitHub Actions is enabled for your repository
- Verify the workflow file is in `.github/workflows/` directory
- Check the Actions tab for any error messages

## Cost

**100% FREE** ✅

- GitHub Actions provides 2,000 free minutes/month for private repos
- This script uses ~1 minute per run
- Running daily = 30 minutes/month (well within free tier)
- Public repos get unlimited free minutes

## Column Types Supported

The script handles all Monday.com column types:
- ✅ Text
- ✅ Status
- ✅ Date
- ✅ People
- ✅ Numbers
- ✅ Email
- ✅ Phone
- ✅ Link
- ✅ Dropdown
- ✅ Checkbox
- ✅ Timeline
- ✅ Long Text

## Security Notes

- Never commit your `.env` file (it's in `.gitignore`)
- Never commit your API token to git
- Use GitHub Secrets for all sensitive data
- Consider using a private repository

## Support

If you encounter issues:
1. Check the logs in GitHub Actions
2. Review the `monday_sync.log` file
3. Verify your API token and board IDs
4. Ensure both boards have the same column structure

## License

MIT License - feel free to modify and use as needed.
