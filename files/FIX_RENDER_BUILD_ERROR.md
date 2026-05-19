# 🔧 FIX: Render Build Failure - Status 1 Error

## Problem
Render shows: "Exited with status 1 while building your code"

This means the Docker build failed during one of the build steps.

---

## Most Likely Causes (in order)

### 1. Missing Dependencies in requirements.txt
The most common cause is a missing or incompatible package.

### 2. Python Version Issue
Something incompatible with Python 3.11

### 3. build_catalog.py or build_embeddings.py Error
These scripts run during Docker build and might be failing

### 4. Missing System Dependencies
Some packages need system libraries

---

## Solution 1: Check Render Logs (IMPORTANT)

1. Go to Render dashboard
2. Click your service: shl-recommender
3. Click "Logs" tab
4. Scroll down to see the actual error message
5. Look for lines like:
   - "ERROR: Could not find a version..."
   - "ModuleNotFoundError"
   - "FileNotFoundError"
   - "SyntaxError"

**Share the actual error message here** and I can fix it!

---

## Solution 2: Simplified Dockerfile (Try This First)

The current Dockerfile builds embeddings which takes time and memory.

Replace your Dockerfile with this simpler version:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Build catalog only (not embeddings - they're too heavy)
RUN python build_catalog.py

# Don't build embeddings in Docker - do it separately

# Expose port
EXPOSE 8000

# Start app
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Solution 3: Build Embeddings Locally First

Instead of building in Docker, build locally:

```bash
# 1. On your computer
python build_catalog.py
python build_embeddings.py

# 2. This creates:
#    - data/catalog.json
#    - data/faiss.index
#    - data/metadata.json

# 3. Add data folder to git (optional)
git add data/
git commit -m "Add pre-built embeddings"

# 4. Push to GitHub
git push origin main

# 5. Render uses pre-built files (much faster!)
```

---

## Solution 4: Check requirements.txt

Make sure you have this exact requirements.txt:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sentence-transformers==2.2.2
faiss-cpu==1.7.4
numpy==1.24.3
google-generativeai==0.3.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
beautifulsoup4==4.12.2
requests==2.31.0
```

If different, update it and push:
```bash
git add requirements.txt
git commit -m "Fix requirements"
git push origin main
```

---

## Solution 5: Skip Embeddings in Docker Build

Edit your Dockerfile and remove the embedding build step:

Change this:
```dockerfile
RUN python build_catalog.py && \
    python build_embeddings.py
```

To this:
```dockerfile
RUN python build_catalog.py
```

The app will build embeddings on first startup, or you can pre-build them.

---

## Recommended Fix (Fastest)

### Step 1: Update Dockerfile
Use the simplified version from Solution 2 above

### Step 2: Build Embeddings Locally
```bash
cd /mnt/user-data/outputs
python build_catalog.py
python build_embeddings.py
```

This creates these files:
- `data/catalog.json`
- `data/faiss.index`
- `data/metadata.json`

### Step 3: Add Data to GitHub
```bash
git add data/
git commit -m "Add pre-built embeddings"
git push origin main
```

### Step 4: Create .gitignore (if needed)
Make sure you have proper .gitignore to avoid large files:

```
# Keep data folder but ignore temporary files
data/temp/
data/*.tmp
__pycache__/
venv/
.env
```

### Step 5: Redeploy on Render
1. Go to Render dashboard
2. Click service
3. Click "Manual Deploy" or wait for auto-deploy
4. Should succeed now!

---

## Troubleshooting Steps

```bash
# 1. Verify all files exist
ls -la /mnt/user-data/outputs/
ls -la /mnt/user-data/outputs/data/

# 2. Check requirements syntax
cat /mnt/user-data/outputs/requirements.txt

# 3. Check Dockerfile syntax
cat /mnt/user-data/outputs/Dockerfile

# 4. Verify git has everything
cd /mnt/user-data/outputs
git status

# 5. Make sure Dockerfile is tracked
git ls-files | grep Dockerfile
# Should show: Dockerfile
```

---

## Quick Actions to Try (in order)

1. **First:** Check Render logs for actual error
2. **Second:** Use simplified Dockerfile from Solution 2
3. **Third:** Build embeddings locally (Solution 3)
4. **Fourth:** Update requirements.txt exactly
5. **Fifth:** Redeploy on Render

---

## Check Render Logs

Most important step! The actual error message will be in Render logs.

Look for these patterns:
- "ERROR:" - shows what failed
- "not found" - missing file
- "No module" - missing package
- "version" - package conflict
- "exit code" - what failed

Once you see the error, tell me and I can give you the exact fix!

---

## What NOT to Do

❌ Don't keep the heavy embedding build in Docker
❌ Don't forget the .gitignore
❌ Don't leave requirements.txt incomplete
❌ Don't use old requirements format

---

## Success Path

1. Fix Dockerfile ✓
2. Build embeddings locally ✓
3. Push to GitHub ✓
4. Render auto-deploys ✓
5. API goes live ✓

---

## Get Exact Error

Please share:
1. The exact error from Render logs
2. Screenshot of the error message
3. Or copy the error text

Then I can give you the exact fix! 🎯

---

**For now:** Try Solution 2 (simplified Dockerfile) and redeploy! 🚀
