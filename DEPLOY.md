# 🚀 Quick Deployment Guide

## Option 1: Railway (Recommended - Fastest & Most Reliable)

### Step 1: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `FinSolvers` repository
5. Railway will auto-detect Python and deploy using our `railway.json` config

### Step 2: Set Environment Variables (Optional)
```bash
OPENAI_API_KEY=your-openai-api-key-here
FLASK_ENV=production
```

### Step 3: Get Your URL
Railway will provide a URL like: `https://finsolvers-production.up.railway.app`

**Your submission URL will be:**
```
https://finsolvers-production.up.railway.app/api/v1/hackrx/run
```

---

## Option 2: Vercel (Good for Serverless)

### Deploy Command:
```bash
npm i -g vercel
vercel --prod
```

**Your submission URL will be:**
```
https://finsolvers.vercel.app/api/v1/hackrx/run
```

---

## Option 3: AWS (Enterprise Scale)

### Using AWS App Runner:
1. Push code to GitHub
2. Go to AWS App Runner console
3. Create service from GitHub repository
4. Select Python runtime
5. Use build command: `pip install -r requirements.txt`
6. Use start command: `gunicorn flask_app:app --bind 0.0.0.0:8080`

---

## 🎯 Recommended Deployment: Railway

**Why Railway?**
- ✅ **Fastest**: Auto-deploy in 30 seconds
- ✅ **Python Optimized**: Built for Python apps
- ✅ **Free Tier**: 500 hours/month free
- ✅ **Auto SSL**: HTTPS enabled by default
- ✅ **Git Integration**: Auto-deploy on push
- ✅ **Health Monitoring**: Built-in health checks

## 🔗 Final Submission URLs

After Railway deployment, your URLs will be:

```bash
# Main API Endpoint (for hackathon submission)
https://your-app.up.railway.app/api/v1/hackrx/run

# Health Check
https://your-app.up.railway.app/health

# Web Interface
https://your-app.up.railway.app/
```

## ⚡ Quick Deploy Commands

```bash
# Commit latest changes
git add .
git commit -m "Ready for production deployment"
git push

# Then deploy to Railway via web interface
# Or use Railway CLI:
npm install -g @railway/cli
railway login
railway link
railway up
```

Your RAG system will be live in under 2 minutes! 🚀
