# Deployment Guide

Complete instructions for deploying SHL Assessment Recommender to production.

## Pre-Deployment Checklist

- [ ] All tests passing (`pytest test_recommender.py -v`)
- [ ] Environment variables configured
- [ ] Catalog built (`python build_catalog.py`)
- [ ] Embeddings built (`python build_embeddings.py`)
- [ ] No hardcoded API keys in code
- [ ] README.md reviewed and updated
- [ ] Error handling and logging verified

## Local Testing Before Deployment

```bash
# 1. Start server locally
python -m uvicorn main:app --reload

# 2. Test health endpoint
curl http://localhost:8000/health

# 3. Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# 4. Monitor logs for errors
# Logs appear in console

# 5. Run tests
pytest test_recommender.py -v --tb=short
```

## Platform-Specific Deployment

### Option 1: Render.com (Recommended)

**Advantages**: Zero-config, auto-scaling, persistent disk, free tier available

**Steps**:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Account**:
   - Go to https://render.com
   - Sign up with GitHub
   - Authorize repository access

3. **Create New Service**:
   - Dashboard → New Service → Web Service
   - Connect GitHub repo
   - Select branch (main)

4. **Configure Service**:
   - **Name**: shl-recommender
   - **Environment**: Python 3.11
   - **Build Command**: 
     ```
     pip install -r requirements.txt && \
     python build_catalog.py && \
     python build_embeddings.py
     ```
   - **Start Command**:
     ```
     python -m uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

5. **Add Environment Variables**:
   - Click Environment
   - Add:
     - Key: `ANTHROPIC_API_KEY`
     - Value: `sk-...` (your API key)
   - Add:
     - Key: `LOG_LEVEL`
     - Value: `info`

6. **Add Persistent Disk** (for embeddings):
   - Click "Create Disk"
   - Name: `data`
   - Mount Path: `/app/data`
   - Size: 5 GB

7. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Copy service URL

8. **Test**:
   ```bash
   curl https://your-service.onrender.com/health
   ```

**Cost**: 
- Free tier: 0.5 GB RAM, auto-pauses after 15 min inactivity
- Starter: $7/month, 0.5 GB RAM, no auto-pause
- Standard: $12/month, 1 GB RAM, better performance

### Option 2: Railway

**Advantages**: Simple configuration, GitHub integration, affordable

**Steps**:

1. **Create Railway Account**:
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**:
   - Dashboard → Create Project → Deploy from GitHub Repo
   - Select your repository

3. **Configure Build & Deploy**:
   - Railway auto-detects Python
   - Add build command in `package.json` or settings:
     ```
     python build_catalog.py && python build_embeddings.py
     ```

4. **Add Environment Variables**:
   - Go to Variables
   - Add `ANTHROPIC_API_KEY`
   - Add `PORT` (Railway sets this automatically)

5. **Configure Start Command**:
   - Settings → Start Command
   - Set: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

6. **Deploy**:
   - Push to GitHub (Railway auto-deploys)
   - Check logs in Railway dashboard

7. **Test**:
   ```bash
   curl https://your-app-production.up.railway.app/health
   ```

**Cost**: Pay-as-you-go (~$5/month for modest usage)

### Option 3: AWS Lambda + API Gateway

**Advantages**: Serverless, pay-per-request, auto-scaling

**Prerequisites**:
- AWS Account
- AWS CLI installed
- `sam` CLI for local testing

**Steps**:

1. **Create deployment package**:
   ```bash
   # Create function directory
   mkdir lambda_package
   cd lambda_package
   
   # Install dependencies
   pip install -r ../requirements.txt -t ./
   
   # Copy application code
   cp -r ../app .
   cp -r ../data .
   cp ../*.py .
   
   # Create Lambda handler
   cat > lambda_handler.py << 'EOF'
   import os
   import json
   from main import app
   from fastapi_aws_lambda.middleware import AWSLambdaMiddleware
   
   app.add_middleware(AWSLambdaMiddleware)
   
   def handler(event, context):
       return AWSLambdaMiddleware.handler(app, event, context)
   EOF
   
   # Create deployment zip
   zip -r ../lambda.zip .
   cd ..
   ```

2. **Deploy to Lambda**:
   ```bash
   aws lambda create-function \
     --function-name shl-recommender \
     --runtime python3.11 \
     --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
     --handler lambda_handler.handler \
     --zip-file fileb://lambda.zip \
     --timeout 30 \
     --memory-size 512 \
     --environment Variables={ANTHROPIC_API_KEY=sk-...}
   ```

3. **Create API Gateway**:
   ```bash
   aws apigateway create-rest-api \
     --name shl-recommender-api
   ```

4. **Connect Lambda to API Gateway**:
   - AWS Console → API Gateway
   - Create resource and methods
   - Point to Lambda function

**Cost**: 
- Free tier: 1M requests/month
- After: $0.0000002 per request + compute time

### Option 4: Docker + Private Server

**Advantages**: Full control, custom configuration

**Steps**:

1. **Build image**:
   ```bash
   docker build -t shl-recommender:latest .
   ```

2. **Push to registry** (Docker Hub):
   ```bash
   docker login
   docker tag shl-recommender:latest myusername/shl-recommender:latest
   docker push myusername/shl-recommender:latest
   ```

3. **On production server**:
   ```bash
   # Pull image
   docker pull myusername/shl-recommender:latest
   
   # Create .env file
   cat > .env << 'EOF'
   ANTHROPIC_API_KEY=sk-...
   PORT=8000
   LOG_LEVEL=info
   EOF
   
   # Run container
   docker run -d \
     --name shl-recommender \
     -p 8000:8000 \
     --env-file .env \
     --restart unless-stopped \
     myusername/shl-recommender:latest
   
   # Verify
   curl http://localhost:8000/health
   ```

4. **Set up reverse proxy** (nginx):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Enable HTTPS** (Let's Encrypt):
   ```bash
   certbot --nginx -d your-domain.com
   ```

## Monitoring & Logging

### Render.com Logs
```bash
# View logs in dashboard or CLI
render logs shl-recommender --tail
```

### Railway Logs
```bash
# View in Railway dashboard
# Or use Railway CLI
railway logs
```

### Local Logging
```python
# Logs configured in main.py
# Check stdout/stderr for issues
```

### Application Metrics
Monitor:
- Response times (target <2s)
- Error rates (target <1%)
- Number of recommendations returned
- Refusal rate (should be <5% of valid requests)

## Scaling Considerations

### Horizontal Scaling
- **Render**: Auto-scales with multiple instances (paid tier)
- **Railway**: Scales based on load
- **Lambda**: Automatically scales
- **Docker**: Use orchestration (Kubernetes, Docker Swarm)

### Vertical Scaling
- Increase instance memory if embeddings load is slow
- Increase CPU for faster LLM calls
- More disk space if expanding catalog

### Caching Strategy
- Cache common queries' embeddings
- Cache frequent comparisons
- Use Redis for multi-instance setups

## Rollback Plan

### If deployment fails:

1. **Render.com**:
   ```bash
   # Go to Dashboard → Deployments
   # Click previous successful deployment
   # Click "Redeploy"
   ```

2. **Railway**:
   ```bash
   # Go to Deployments
   # Select previous version
   # Redeploy
   ```

3. **Lambda**:
   ```bash
   # Revert to previous function version
   aws lambda update-alias \
     --function-name shl-recommender \
     --name LIVE \
     --function-version 1
   ```

4. **Docker**:
   ```bash
   docker run -d \
     --name shl-recommender \
     -p 8000:8000 \
     --env-file .env \
     myusername/shl-recommender:previous-tag
   ```

## Performance Tuning

### Pre-built Indexes
- Embeddings are pre-computed at build time
- Reduces startup time from 60s to <10s
- Recommended for production

### FAISS Optimization
```python
# In faiss_index.py, can add:
# - GPU support (if available)
# - Index compression
# - Approximate search (faster but less accurate)
```

### LLM Optimization
- Use `temperature=0.3-0.5` for structured outputs (faster, more consistent)
- Shorter prompts = faster responses
- Batch requests if processing multiple queries

## Security in Production

1. **API Key Management**:
   - Never commit `.env` to git
   - Use platform's secret management
   - Rotate keys regularly

2. **CORS Configuration**:
   - Restrict to known domains
   - Disable in main.py if not needed

3. **Rate Limiting**:
   - Implement via API Gateway
   - Limit: 100 requests/minute per IP

4. **Input Validation**:
   - Pydantic enforces limits (1-10,000 chars)
   - Refusal mechanism catches prompt injection

5. **HTTPS/TLS**:
   - Enable on all platforms
   - Render/Railway handle automatically
   - Docker: Use reverse proxy

## Troubleshooting Deployment

### Issue: "ModuleNotFoundError"
```bash
# Ensure all imports are in requirements.txt
pip freeze > requirements.txt
```

### Issue: "ANTHROPIC_API_KEY not found"
```bash
# Check environment variables in platform dashboard
# Restart service after adding variables
```

### Issue: "Out of memory"
```bash
# Increase instance size
# Or optimize embeddings model
# Or use smaller batch sizes
```

### Issue: Embeddings not found at startup
```bash
# Ensure build command runs:
# python build_catalog.py && python build_embeddings.py
# Check disk space (need 2GB+)
```

### Issue: Slow responses
```bash
# Check LLM API latency (should be <1s)
# Check FAISS search time (should be <20ms)
# Monitor network connectivity
```

## Post-Deployment Validation

1. **Health check**:
   ```bash
   curl https://your-service.com/health
   ```

2. **Basic functionality**:
   ```bash
   curl -X POST https://your-service.com/chat \
     -H "Content-Type: application/json" \
     -d '{"messages": [{"role": "user", "content": "Test"}]}'
   ```

3. **Error handling**:
   ```bash
   # Test invalid request
   curl -X POST https://your-service.com/chat \
     -H "Content-Type: application/json" \
     -d '{"messages": []}'  # Should return 400
   ```

4. **Performance monitoring**:
   - Record baseline response times
   - Set up alerts for errors
   - Monitor API quota usage

## Continuous Integration / Continuous Deployment (CI/CD)

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest test_recommender.py -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl -X POST https://api.render.com/deploy/service/$RENDER_SERVICE_ID \
            -H "Authorization: Bearer $RENDER_API_KEY"
        env:
          RENDER_SERVICE_ID: ${{ secrets.RENDER_SERVICE_ID }}
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
```

## Support & Troubleshooting

1. **Check platform logs**
2. **Verify environment variables**
3. **Ensure catalog is built**
4. **Check API key validity**
5. **Review error messages in logs**

---

**Next Steps**: After successful deployment, set up monitoring and alerting for production reliability.
