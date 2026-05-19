# 🚀 START HERE - Deploy & Get URL in 10 Minutes

## What You Have
A complete, production-ready SHL Assessment Recommender system with:
- ✅ 7 Python modules (2,000+ lines)
- ✅ RAG-based conversational AI
- ✅ Semantic search with embeddings
- ✅ All files ready to deploy
- ✅ 8 documentation guides

## What You'll Get
A **live URL** you can use immediately:
```
https://shl-recommender-XXXXX.onrender.com/chat
```

---

## 🎯 The 5-Step Process

### Step 1: Get API Key (1 min)
Go to: https://console.anthropic.com/keys
- Click "Create Key"
- Copy the key (looks like: `sk-ant-v0-xxxxx`)
- Save it somewhere safe

### Step 2: Push Code to GitHub (2 min)
```bash
cd /mnt/user-data/outputs

git init
git add .
git commit -m "SHL Assessment Recommender"
git remote add origin https://github.com/YOUR_USERNAME/shl-recommender.git
git branch -M main
git push -u origin main
```

**What to include:**
- All `.py` files ✓
- `requirements.txt` ✓
- `Dockerfile` ✓
- `render.yaml` ✓

**What to exclude:**
- `data/` folder (created at startup)
- `venv/` folder
- `__pycache__/`

### Step 3: Create Render Account (1 min)
1. Go to https://render.com
2. Click "Sign Up"
3. Sign up with GitHub
4. Click "Authorize"

### Step 4: Deploy Service (1 min)
1. On Render dashboard, click **"New Web Service"**
2. Select your `shl-recommender` repository
3. Fill in:
   - **Name:** `shl-recommender`
   - **Environment:** `Docker`
4. Click **"Advanced"**
5. Add **Environment Variables:**
   - Key: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-v0-xxxxx` (your key from Step 1)
   - Key: `PORT`
   - Value: `8000`
6. Click **"Create Disk":**
   - Name: `data`
   - Mount Path: `/app/data`
   - Size: `5 GB`
7. Click **"Create Web Service"**

### Step 5: Wait & Copy URL (5-10 min)
Watch the logs. After 5-10 minutes, you'll see:
```
✓ Service is live at: https://shl-recommender-XXXXX.onrender.com
```

**Copy this URL! That's your live API endpoint.**

---

## ✅ Test Your URL Works

Once you have the URL, test it:

### Health Check
```bash
curl https://shl-recommender-XXXXX.onrender.com/health

# Should return: {"status":"ok"}
```

### Chat Endpoint
```bash
curl -X POST https://shl-recommender-XXXXX.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need to hire a Java developer"}
    ]
  }'
```

---

## 🎁 What You Can Do Now

### Share the URL
- Send to colleagues: `https://shl-recommender-XXXXX.onrender.com/chat`
- Works 24/7
- No setup needed for them

### Integrate with Your App
```python
import requests

response = requests.post(
    "https://shl-recommender-XXXXX.onrender.com/chat",
    json={
        "messages": [
            {"role": "user", "content": "Hiring a Python developer"}
        ]
    }
)

result = response.json()
print(result['reply'])
for rec in result['recommendations']:
    print(f"- {rec['name']}: {rec['url']}")
```

### Use in Your Frontend
```javascript
fetch('https://shl-recommender-XXXXX.onrender.com/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        messages: [{
            role: 'user',
            content: 'Hiring a Java developer'
        }]
    })
})
.then(r => r.json())
.then(data => console.log(data.reply))
```

---

## 💰 Costs

**Free Tier:** $0/month
- Works great for getting started
- Auto-pauses after 15 min inactivity
- Perfect for development

**Upgrade to Always-On (optional):**
- Starter: $7/month (recommended for production)
- Standard: $12/month (better performance)

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Check GitHub repo has all files |
| Service won't start | Verify ANTHROPIC_API_KEY is set |
| Timeout error | First request loads model (~30s) |
| No recommendations | Wait for embeddings to build |
| 404 error | Check URL format: `https://...onrender.com/chat` |

---

## 📖 If You Need Help

- **DEPLOY_5_STEPS.md** - Quick 5-step reference
- **DEPLOYMENT_VISUAL_GUIDE.txt** - Visual step-by-step
- **DEPLOY_WITH_URL.md** - Detailed instructions
- **README.md** - Complete documentation
- **API_EXAMPLES.md** - Request/response examples

---

## Your Final URL Format

```
https://shl-recommender-XXXXX.onrender.com
```

Endpoints available:
- GET `/health` - Check if service is running
- POST `/chat` - Main conversational endpoint

---

## Next: Customize (Optional)

Once deployed, you can:

1. **Add more assessments:**
   - Edit `build_catalog.py`
   - Push to GitHub
   - Render auto-redeploys

2. **Modify prompts:**
   - Edit `prompt_templates.py`
   - Push changes
   - Auto-redeploy

3. **Scale up:**
   - Upgrade Render plan
   - Add more resources
   - Increase RAM

---

## Quick Timeline

| Step | Time | Action |
|------|------|--------|
| 1 | 1 min | Get API key |
| 2 | 2 min | Push to GitHub |
| 3 | 1 min | Create Render account |
| 4 | 1 min | Configure service |
| 5 | 5 min | Wait for deployment |
| **Total** | **10 min** | **Live URL!** |

---

## 🎉 You're Ready!

Just follow the 5 steps above, and you'll have a production API running 24/7.

**Ready to deploy?**

1. ✅ Have API key from Step 1
2. ✅ Push code to GitHub (Step 2)
3. ✅ Create Render account (Step 3)
4. ✅ Configure and deploy (Step 4)
5. ✅ Copy your live URL (Step 5)

**Let's go!** 🚀

---

## Questions?

- See **DEPLOY_WITH_URL.md** for detailed instructions
- See **API_EXAMPLES.md** for request/response examples
- See **ARCHITECTURE.md** for how the system works

Good luck! Your API will be live in 10 minutes! 🎊
