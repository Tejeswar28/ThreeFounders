# Three Founders — Flask Landing Page

A Flask landing page for the Three Founders engineering team. It presents the founders, capabilities, live project links, and a project enquiry form.

## Stack

- **Backend:** Python 3.12 and Flask
- **Templates:** Jinja2
- **Frontend:** HTML, CSS, and vanilla JavaScript
- **Enquiries:** server-side validation, CSRF token, and SMTP email
- **Hosting:** Vercel Python Functions or another Python WSGI host

## Run locally (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set a unique `SECRET_KEY`. For Gmail, use an App Password—not your normal account password—for `SMTP_PASSWORD`. The enquiry recipient defaults to Avinash's email; set `ENQUIRY_TO` if it should go elsewhere. The app loads `.env` automatically.

```powershell
python app.py
```

Open http://127.0.0.1:5000.

## Contact form and privacy

- Valid enquiries are sent directly by SMTP to `ENQUIRY_TO`; the sender's email is set as Reply-To.
- The application does not write submissions or personal details to a database or local file.
- If SMTP settings are missing or email delivery fails, the page says the message could not be sent and provides a direct email link.
- The app does not log enquiry contents.
- Never commit `.env` or live credentials.

## Deploy to Vercel

Vercel detects the Flask application exported as `app` by the root `app.py`. It installs Python packages from `requirements.txt`. Static assets live in `public/` and are served by Vercel's CDN. No database or `vercel.json` is needed for this app.

1. Import the project repository into Vercel.
2. In the Vercel project's **Settings → Environment Variables**, set:
   - `SECRET_KEY`: a long, unique random value.
   - `STUDIO_EMAIL` and `ENQUIRY_TO`: the contact and recipient addresses.
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM`: working credentials from your email provider. For Gmail, use an App Password.
3. Add variables for the Production environment (and Preview/Development if needed), then deploy.
4. Verify `/health`, the page styling and JavaScript, and a test enquiry. Confirm that the email arrives.

Vercel sets `VERCEL=1`. The app refuses to start there unless `SECRET_KEY` is configured and is not the sample value. SMTP connectivity depends on the provider and platform's network policy; use an email provider/API that supports your Vercel deployment if SMTP delivery fails.

## Project structure

```text
three-founders-studio-python/
├── app.py
├── requirements.txt
├── .python-version
├── .env.example
├── public/
│   ├── app.js
│   └── styles.css
└── templates/
    └── index.html
```

## Production server (non-Vercel)

```powershell
gunicorn --workers 2 --bind 0.0.0.0:8000 app:app
```

Set the environment variables through the hosting platform's secret/environment-variable settings.

## Health check

`GET /health` returns `{"status":"ok"}`.
