# 🔒 Security Checklist - Before Pushing to Git

## ✅ **Protected Files (Should NOT be in git)**
- [ ] `credentials.json` - Google OAuth credentials
- [ ] `token.json` - Google OAuth tokens  
- [ ] `config.json` - May contain sensitive configuration
- [ ] `auth_log.json` - Authentication logs
- [ ] `Job Tracker.xlsx` - Your personal job applications
- [ ] `job_applications_fallback.csv` - Job data export
- [ ] `venv/` - Virtual environment
- [ ] `__pycache__/` - Python cache files
- [ ] `.zshrc` - Shell config (may contain API keys)

## ✅ **Safe Files (Can be committed)**
- [ ] All `.py` files - Your code
- [ ] All `.md` files - Documentation
- [ ] `requirements.txt` - Dependencies
- [ ] `.gitignore` - Git ignore rules

## 🔍 **Final Check Commands**

### Check what git will commit:
```bash
git status
```

### Check for any sensitive files that might be tracked:
```bash
git ls-files | grep -E "(json|key|token|credential|excel|csv)"
```

### Check for API keys in your code:
```bash
grep -r "AIza" . --exclude-dir=venv --exclude-dir=.git
```

## 🚨 **If You Find Sensitive Data**

### Remove from git tracking:
```bash
git rm --cached <filename>
```

### Add to .gitignore:
```bash
echo "<filename>" >> .gitignore
```

### Check git history for sensitive data:
```bash
git log --all --full-history -- <filename>
```

## 📋 **Pre-Push Checklist**
- [ ] Run `git status` - verify no sensitive files
- [ ] Run `git diff` - review all changes
- [ ] Check for hardcoded API keys in code
- [ ] Verify `.gitignore` is comprehensive
- [ ] Test that sensitive files are ignored

## 🔐 **Best Practices**
1. **Never commit API keys** - Use environment variables
2. **Never commit personal data** - Keep job files local
3. **Use .env files** for local configuration
4. **Regular security audits** of your repository
5. **Rotate API keys** if accidentally exposed

## 🆘 **If You Accidentally Commit Sensitive Data**
1. **Immediately revoke** any exposed API keys
2. **Remove from git history** using `git filter-branch` or BFG
3. **Force push** to overwrite remote history
4. **Notify collaborators** to update their local repos
5. **Generate new credentials** and update local configs 