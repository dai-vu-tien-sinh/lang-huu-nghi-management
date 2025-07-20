# Quick Git Push Commands - Standard Template

## Standard Push Commands (Use Every Time)

```bash
# Clear any Git locks
rm -f .git/index.lock .git/config.lock .git/objects/*/tmp_obj_*
killall git 2>/dev/null || true

# Add all changed files
git add .

# Commit with descriptive message
git commit -m "Your commit message here"

# Push to GitHub
git push origin main
```

## For Vietnamese Navigation Fix

```bash
# Clear Git locks
rm -f .git/index.lock .git/config.lock .git/objects/*/tmp_obj_*
killall git 2>/dev/null || true

# Add specific files for navigation fix
git add streamlit_app.py
git add "🏠_Trang_chủ.py" 
git add STREAMLIT_CLOUD_ENTRY_FIX.md
git add QUICK_PUSH_FIX.md
git add gdrive_backup.py
git add GOOGLE_OAUTH_SETUP.md

# Commit navigation and backup fixes
git commit -m "Fix Vietnamese navigation and Google Drive backup

- Navigation now shows '🏠 Trang chữ' instead of 'streamlit app'
- Created Vietnamese homepage file with proper naming
- Fixed Google Drive backup create_backup method error  
- Added comprehensive OAuth setup guide
- Streamlit Cloud ready for deployment"

# Push to GitHub
git push origin main
```

## Quick Template for Future Updates

```bash
# Standard 3-step process:
rm -f .git/index.lock .git/config.lock .git/objects/*/tmp_obj_*; killall git 2>/dev/null || true
git add .; git commit -m "Your update description"  
git push origin main
```

## Common Commit Messages

```bash
# Feature additions
git commit -m "Add new feature: [description]"

# Bug fixes  
git commit -m "Fix: [issue description]"

# UI/UX improvements
git commit -m "Improve: [interface element]"

# Database changes
git commit -m "Update database: [changes made]"

# Documentation
git commit -m "Update documentation: [what was added]"
```

Save these commands and use them whenever you need to push changes to GitHub!