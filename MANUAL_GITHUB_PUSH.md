# Manual GitHub Push Instructions

Since Replit is restricting automated Git operations, please run these commands manually in the Shell:

## Step 1: Clear any lock files
```bash
rm -f .git/index.lock .git/config.lock
killall git 2>/dev/null || true
```

## Step 2: Pull remote changes first
```bash
# Pull changes from remote to resolve conflicts
git pull https://ghp_YOUR_TOKEN@github.com/dai-vu-tien-sinh/lang-huu-nghi-management.git main --allow-unrelated-histories

# If you get merge conflicts, accept them by:
git add .
git commit -m "Merge remote changes"
```

## Step 3: Force push if needed
Since the repositories have different histories, you may need to force push:

```bash
# Option A: Force push with lease (safer)
git push --force-with-lease https://ghp_YOUR_TOKEN@github.com/dai-vu-tien-sinh/lang-huu-nghi-management.git main

# Option B: If that fails, use force push (overwrites remote)
git push --force https://ghp_YOUR_TOKEN@github.com/dai-vu-tien-sinh/lang-huu-nghi-management.git main
```

## Alternative: Create new repository
If the above doesn't work, create a fresh repository:

```bash
# Remove existing Git tracking
rm -rf .git

# Initialize new repository
git init
git add .
git commit -m "Initial commit: Complete Làng Hữu Nghị management system"

# Add remote and push
git remote add origin https://ghp_YOUR_TOKEN@github.com/dai-vu-tien-sinh/lang-huu-nghi-management.git
git branch -M main
git push -u origin main --force
```

## What will be pushed:
- Complete project source code (Python, Streamlit)
- Database: lang_huu_nghi.db (485KB with 107 students)
- 4 document attachments for Nguyễn Văn Học
- Vietnamese documentation and README
- All configuration files

## Verify success:
After successful push, check:
1. Go to https://github.com/dai-vu-tien-sinh/lang-huu-nghi-management
2. Confirm files are there including `lang_huu_nghi.db`
3. Check README.md displays correctly

Replace `YOUR_TOKEN` with your actual GitHub personal access token.