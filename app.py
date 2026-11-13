import os
import re
import secrets
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, session, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

secret_key = os.getenv("SECRET_KEY")
if os.getenv("VERCEL") and (
    not secret_key or secret_key == "replace-with-a-long-random-secret"
):
    raise RuntimeError("Set a unique SECRET_KEY in the Vercel project environment variables.")

app = Flask(__name__, static_folder=None)
app.config["SECRET_KEY"] = secret_key or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = bool(os.getenv("VERCEL"))
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
STUDIO_EMAIL = os.getenv("STUDIO_EMAIL", "avinashthammaiahgari@gmail.com")
ENQUIRY_TO = os.getenv("ENQUIRY_TO", STUDIO_EMAIL)
STUDIO_PHONE = "+91 87905 64558"

TEAM = [
    {
        "name": "Avinash Thammaiahgari",
        "role": "Data Consultant · Fusion Consulting",
        "initials": "AT",
        "accent": "cyan",
        "location": "Bengaluru, India",
        "bio": "Builds cloud ETL and data-migration workflows for healthcare and life-sciences clients. Focused on intelligent systems, scalable data infrastructure, and AI-driven solutions.",
        "focus": ["Python", "PySpark", "AWS Glue", "Spark SQL", "Data Quality"],
        "linkedin": "https://www.linkedin.com/in/thammaiahgari-avinash-3236aa222",
        "github": "https://github.com/avinasht213",
    },
    {
        "name": "Sudarshan Raghavaraju",
        "role": "Software Developer · Adobe",
        "initials": "SR",
        "accent": "purple",
        "location": "Bengaluru, India",
        "bio": "Builds enterprise learning platforms with a focus on responsive, accessible interfaces. Previously delivered full-stack features using React, Node.js, MongoDB, and AWS at Exafluence.",
        "focus": ["React", "JavaScript", "Node.js", "AWS", "Accessibility"],
        "linkedin": "https://www.linkedin.com/in/sudarshan02/",
        "github": "https://github.com/sud02",
    },
    {
        "name": "Tejeswar Reddy",
        "role": "Software Engineer · Pine Labs",
        "initials": "TR",
        "accent": "pink",
        "location": "Bengaluru, India",
        "bio": "Engineers payment systems and event-driven services using C++, Java, and Kafka. Led scheme-automation improvements that increased bulk-processing throughput by 70%.",
        "focus": ["Java", "C++", "Spring Boot", "Apache Kafka", "MySQL"],
        "linkedin": "https://www.linkedin.com/in/tejeswar-reddy-300989216/",
        "github": "https://github.com/Tejeswar28",
    },
]
PROJECTS = [
    {"id": "01", "title": "LSJ Collections", "category": "Commerce", "status": "Live website", "description": "A jewellery storefront for browsing BIS-hallmarked collections, new arrivals, and certified gold pieces.", "url": "https://lsjcollections.com/", "stack": ["Jewellery", "Hallmarked gold", "Online store"], "visual": "visual-commerce"},
    {"id": "02", "title": "A.C.S.R. Government Medical College", "category": "Education", "status": "Live website", "description": "The official digital presence of A.C.S.R. Government Medical College in Nellore, Andhra Pradesh.", "url": "https://acsrgmcnlr.com/", "stack": ["Medical college", "Institutional website", "Nellore"], "visual": "visual-medical"},
    {"id": "03", "title": "Taablr", "category": "Hospitality", "status": "Live product", "description": "A QR-based ordering platform helping hotels offer digital menus, shared table orders, and live order updates.", "url": "https://www.taablr.in/", "stack": ["QR ordering", "Digital menus", "Hotel operations"], "visual": "visual-hospitality"}
]
SERVICES = [
("01","DATA ENGINEERING","MIGRATION & QUALITY","Build dependable ETL workflows and migration pipelines for large, complex datasets.",["Python, SQL & PySpark","AWS Glue & Amazon S3","Spark SQL transformations","Data quality automation","Reconciliation & migration"],"cyan","▤"),
("02","PRODUCT ENGINEERING","WEB & ENTERPRISE SOFTWARE","Develop responsive product interfaces, backend services, and integrations for real business workflows.",["React interfaces","Java & Spring Boot services","Python & FastAPI","C# and C++ applications","APIs & microservices"],"purple","⌘"),
("03","AI & WORKFLOW AUTOMATION","LLM-ASSISTED OPERATIONS","Apply language models and deterministic data processing to reduce repetitive information work.",["Multimodal document processing","Google Gemini & AWS Bedrock","Structured data extraction","Human-reviewed quality checks","Workflow automation"],"pink","◈")
]
TECHNOLOGIES = [
("LANGUAGES","Python · Java · C++ · C# · SQL · JavaScript · TypeScript"),
("DATA ENGINEERING","Apache Spark · PySpark · Spark SQL · AWS Glue · Amazon S3 · Oracle"),
("PRODUCT DEVELOPMENT","React · Node.js · Express.js · Spring Boot · FastAPI · REST APIs"),
("DATA & MESSAGING","MySQL · MongoDB · Redis · Apache Kafka"),
("AI & DELIVERY","Google Gemini · AWS Bedrock · Claude · Docker · Git · GitHub")
]
PROCESS = [
("01","DISCOVER","Understand the business problem, requirements, users, and expected outcomes."),
("02","DESIGN","Shape the architecture, choose the right tools, and define a practical roadmap."),
("03","ENGINEER","Build, integrate, test, and refine the solution in close collaboration."),
("04","DEPLOY & EVOLVE","Ship the solution, observe how it performs, and improve it over time.")
]

def send_notification(enquiry):
    """Email an enquiry without persisting its personal data on the application filesystem."""
    host = os.getenv("SMTP_HOST", "").strip()
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    if not all((host, username, password)):
        return False

    message = EmailMessage()
    message["Subject"] = f"New studio enquiry: {enquiry['project_type']}"
    message["From"] = os.getenv("SMTP_FROM", username)
    message["To"] = ENQUIRY_TO
    message["Reply-To"] = enquiry["email"]
    message.set_content(
        f"Name: {enquiry['name']}\nOrganization: {enquiry['organization']}\n"
        f"Phone: {enquiry['phone'] or 'Not provided'}\n"
        f"Email: {enquiry['email']}\nProject: {enquiry['project_type']}\n"
        f"Budget: {enquiry['budget']}\n\nDescription:\n{enquiry['description']}"
    )
    port = int(os.getenv("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=15) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(username, password)
        smtp.send_message(message)
    return True

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

@app.get("/styles.css")
def styles_css():
    return send_from_directory(os.path.join(BASE_DIR, "public"), "styles.css")

@app.get("/app.js")
def app_js():
    return send_from_directory(os.path.join(BASE_DIR, "public"), "app.js")

@app.get("/")
def home():
    token = session.setdefault("csrf_token", secrets.token_urlsafe(32))
    return render_template(
        "index.html", team=TEAM, projects=PROJECTS, services=SERVICES,
        technologies=TECHNOLOGIES, process=PROCESS, studio_email=STUDIO_EMAIL,
        studio_phone=STUDIO_PHONE,
        year=datetime.now(timezone.utc).year, csrf_token=token
    )

@app.post("/contact")
def contact():
    if not secrets.compare_digest(request.form.get("csrf_token", ""), session.get("csrf_token", "")):
        abort(400)
    name = request.form.get("name", "").strip()
    organization = request.form.get("organization", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    project_type = request.form.get("projectType", "").strip()
    description = request.form.get("description", "").strip()
    budget = request.form.get("budget", "").strip()
    allowed_types = {"Data Engineering", "Product Development", "AI & Workflow Automation", "Other"}
    if not name or not email or not description or project_type not in allowed_types:
        flash("Please complete the required fields and select a valid project type.", "error")
        return redirect(url_for("home") + "#contact")
    if len(name) > 120 or len(organization) > 160 or len(phone) > 40 or len(email) > 254 or len(description) > 10000:
        abort(413)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("home") + "#contact")
    enquiry = {"name":name,"organization":organization,"phone":phone,"email":email,"project_type":project_type,"description":description,"budget":budget}
    try:
        notification_sent = send_notification(enquiry)
    except (OSError, smtplib.SMTPException, ValueError) as error:
        app.logger.error("Project enquiry email delivery failed (%s).", type(error).__name__)
        notification_sent = False
    if notification_sent:
        flash("Your enquiry was emailed to Avinash. Thank you for getting in touch.", "success")
    else:
        flash(
            f"We couldn't send your enquiry. Please email Avinash directly at {STUDIO_EMAIL}.",
            "warning",
        )
    session.pop("csrf_token", None)
    return redirect(url_for("home") + "#contact")

@app.get("/health")
def health():
    return {"status":"ok"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
