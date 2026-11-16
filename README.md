# GIGMATE AI — Cloud MVP

Browser-deployable Streamlit app using Gemini for AI drafting and Supabase for cloud authentication and CRM storage.

## 1. Create accounts
- Google AI Studio: https://aistudio.google.com/apikey
- GitHub: https://github.com/
- Supabase: https://supabase.com/dashboard
- Streamlit Community Cloud: https://share.streamlit.io/

## 2. Configure Supabase
1. Create a Supabase project.
2. Open SQL Editor.
3. Paste and run `supabase_schema.sql`.
4. Open Project Settings > API (or Connect/API settings).
5. Copy the Project URL and publishable/anon key. Do not use the `service_role` key.

## 3. Create Gemini API key
1. Open Google AI Studio API Keys.
2. Create an API key.
3. Keep it private. Never paste it into source code or a public GitHub file.
4. Free tier has model-specific quotas and data-use terms. Avoid sensitive personal data.

## 4. Upload to GitHub
Create a new repository named `gigmate-ai-cloud`.
Upload:
- `app.py`
- `requirements.txt`
- `supabase_schema.sql`
- `README.md`

A public repository is easiest for the free Streamlit deployment. Do not put API keys, passwords, real student data or business contact exports in the repository.

## 5. Deploy
1. Sign in at https://share.streamlit.io/ using GitHub.
2. Click Create app.
3. Select the `gigmate-ai-cloud` repository, branch `main`, and file `app.py`.
4. Before or after deployment, open App settings > Secrets.
5. Add this TOML, replacing values with your own:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_MODEL = "gemini-3.8-flash"
```

6. Save and reboot/redeploy the app.

## Current functionality
- Email/password sign-up and sign-in via Supabase Auth.
- Cloud lead CRM with per-user row-level security.
- Lead pipeline status and follow-up dates.
- Gemini-powered outreach drafts.
- Gemini sales coach.

## Important limitations
- This is an early MVP, not a production-ready marketplace.
- The app does not scrape business directories or send messages automatically.
- AI output must be checked before use.
- Do not store sensitive student identity documents, bank details or private data in this MVP.
- Google AI Studio free-tier quotas and data terms can change. Do not send confidential customer information through free-tier AI.
- Streamlit Community Cloud and Supabase free plans have quotas, inactivity and availability limitations. Review current terms before relying on them for business-critical operations.
- This app uses a Supabase publishable/anon key plus RLS. Never put the Supabase service-role key in Streamlit secrets for this client-side user-scoped pattern.
