# Agentic AI Hub website (Django)

A complete Django site: landing page, courses, events, about, portfolio, media and blog, all managed from the Django admin.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser                      # your admin login
python manage.py seed_demo                            # optional: demo content (add --with-admin for admin/admin12345)
python manage.py runserver
```

Site: http://127.0.0.1:8000/  Admin: http://127.0.0.1:8000/admin/

To use PostgreSQL instead of the local SQLite database, set `POSTGRES_URL` in
your environment to the PostgreSQL connection URL before running Django
commands. Keep the URL (including its password) out of source control. On
Windows PowerShell, set it for the current session with:

```powershell
$env:POSTGRES_URL = "your-rotated-postgres-connection-url"
```

Then run `python manage.py migrate` to create the site's tables in PostgreSQL.
The `supa` query parameter, if present in the URL, is removed before connecting;
the other connection parameters such as `sslmode` are preserved.

## What to edit in the admin

| Section | What you add |
|---|---|
| **Site settings** | Banner headline and image, organisation story, mission, vision, contact details, social links |
| **Courses** | Name, summary, price in KES, duration, prerequisites, topics, and course outcomes. Add the payment page URL for each course; applicants are redirected there after submitting the Apply now form. |
| **Course applications** | Review applicant details and Python proficiency from the admin. Applications are recorded before redirecting to the course payment page. |
| **Events** | Title, description, tags (comma separated), date, location, highlights (bullet points), banner and small photo |
| **Blog posts** | Title, date, author, description, content (blank line = new paragraph, `## ` = sub-heading), banner |
| **Media items** | Name, description, portrait or landscape, platform, video link, cover image. Tick Featured to show on the home page. YouTube and Vimeo links play on the page |
| **Projects** | Portfolio entries |
| **Team members, Core values, Other about-page sections** | The About page |
| **Subscribers** | Newsletter and membership sign-ups, with a CSV export action |

Events are listed earliest first, with upcoming events above past events.

## Deploying
Set `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, run `collectstatic`, and serve `/media/` (uploads) from your web server or storage.
