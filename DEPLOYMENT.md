# Auto EDA Deployment Guide (Render + Vercel)

This is a fresh deployment path for:
- Backend: Render Web Service (FastAPI)
- Frontend: Vercel Project (Vite + React)

Use this checklist in order and do not skip steps.

## 1. Pre-Deployment Checklist

1. Push current code to your GitHub repository branch (usually `main`).
2. Confirm these files exist:
   - `render.yaml`
   - `client/vercel.json`
   - `client/src/api/apiService.js` uses `VITE_API_BASE_URL`
3. Keep required secrets ready:
   - `GROQ_API_KEY`
   - `JWT_SECRET` (long random string)

## 2. Deploy Backend on Render

1. Open Render dashboard.
2. Click `New` -> `Blueprint`.
3. Connect your GitHub repo and select this repository.
4. Render will detect `render.yaml` and propose service `auto-eda-backend`.
5. Click `Apply`.

### 2.1 Set Render Environment Variables

In Render service settings, set or verify:

1. `GROQ_API_KEY` = your key
2. `JWT_SECRET` = long random secret
3. `CORS_ORIGINS` = your Vercel domain(s), comma-separated
   - Example: `https://auto-eda.vercel.app,https://auto-eda-git-main-yourname.vercel.app`
4. `FASTAPI_ENV` = `production`
5. `DEBUG` = `False`

### 2.2 Verify Backend Health

1. Wait for deploy to finish.
2. Open `https://<your-render-service>.onrender.com/health`.
3. Expected response contains `"status": "healthy"`.

If health fails:
1. Check Render logs for startup errors.
2. Fix env vars first (`GROQ_API_KEY`, `CORS_ORIGINS`).
3. Redeploy.

## 3. Deploy Frontend on Vercel

1. Open Vercel dashboard.
2. Click `Add New` -> `Project`.
3. Import same GitHub repository.
4. Set `Root Directory` to `client`.
5. Framework preset: `Vite`.
6. Build settings should match `client/vercel.json`:
   - Install: `npm ci`
   - Build: `npm run build`
   - Output: `dist`
7. Add env var:
   - `VITE_API_BASE_URL` = `https://<your-render-service>.onrender.com`
8. Click `Deploy`.

## 4. Connect Frontend and Backend (Critical)

After frontend deploy:

1. Copy Vercel production URL.
2. Go back to Render service env vars.
3. Update `CORS_ORIGINS` to include Vercel URL(s).
4. Redeploy Render service.

Why this step matters:
- Frontend calls backend from browser.
- Backend must allow your exact Vercel origins via CORS.

## 5. Full Smoke Test

Run these in order:

1. Open Vercel app URL.
2. Upload sample CSV.
3. Trigger one processing action.
4. Generate charts.
5. Trigger AI insights (requires `GROQ_API_KEY`).

If frontend shows network error:
1. Check browser devtools -> failing request URL.
2. Confirm `VITE_API_BASE_URL` points to Render.
3. Confirm Render `CORS_ORIGINS` includes active Vercel domain.

## 6. Post-Deploy Hardening (Recommended)

1. In Render, keep only required env vars.
2. Rotate `JWT_SECRET` if it was shared.
3. Add custom domains later after base deployment is stable.
4. Keep `autoDeploy` enabled for both platforms.

## 7. Fast Re-Deploy Flow (Daily Use)

1. Push code to GitHub.
2. Render auto-deploys backend.
3. Vercel auto-deploys frontend.
4. Test on Vercel preview URL first.
5. Promote/merge to `main` when good.

## 8. Common Pitfalls to Avoid

1. Using `http://localhost:8000` in production frontend.
2. Missing `CORS_ORIGINS` for current Vercel URL.
3. Forgetting to set `Root Directory` = `client` in Vercel.
4. Setting wrong backend URL in `VITE_API_BASE_URL` (must be Render HTTPS URL).

## 9. Rollback Plan (If Deployment Breaks)

1. In Vercel, promote last successful deployment.
2. In Render, manual deploy previous commit.
3. Re-check env vars (most failures are config-related).

---

If you want, the next step can be a live guided execution where you share each URL/value and I validate every step before you click deploy.
