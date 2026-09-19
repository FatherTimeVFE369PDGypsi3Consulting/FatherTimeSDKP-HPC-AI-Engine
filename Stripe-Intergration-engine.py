from pathlib import Path
import zipfile

root = Path("/mnt/data/stripe_code_engine_integration")
(root / "app").mkdir(parents=True, exist_ok=True)

content = {
"app/app.py": '''import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/create-payment-intent")
def create_payment_intent():
    data = request.get_json(silent=True) or {}
    intent = stripe.PaymentIntent.create(
        amount=int(data["amount"]),
        currency=data.get("currency", "usd"),
        automatic_payment_methods={"enabled": True},
    )
    return jsonify({"client_secret": intent.client_secret})

@app.post("/webhook/stripe")
def stripe_webhook():
    payload = request.get_data()
    signature = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return jsonify({"error": "invalid webhook"}), 400

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        # TODO: persist/update application state using payment_intent["id"].
        pass
    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        # TODO: persist/update application state using invoice["id"].
        pass

    return jsonify({"received": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
''',
"requirements.txt": "Flask>=3.0,<4\\nstripe>=12,<14\\ngunicorn>=23,<24\\n",
"Dockerfile": '''FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app.app:app"]
''',
".dockerignore": "__pycache__\\n*.pyc\\n.env\\n.git\\n.venv\\n",
".env.example": "STRIPE_SECRET_KEY=sk_test_REPLACE_ME\\nSTRIPE_WEBHOOK_SECRET=whsec_REPLACE_ME\\nPORT=8080\\n",
"CODE_ENGINE_DEPLOYMENT.md": '''# Stripe + IBM Code Engine

Architecture: Stripe -> HTTPS webhook -> IBM Code Engine -> Stripe SDK -> application/database.

Required Code Engine secrets:
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET

Do not commit real Stripe credentials.

Expose the application over HTTPS and configure Stripe to call:
`https://<code-engine-host>/webhook/stripe`

Recommended events:
- payment_intent.succeeded
- invoice.payment_succeeded

The webhook verifies Stripe-Signature against the signing secret using the raw request body.

Before production, persist processed Stripe event IDs and make event handling idempotent so retries cannot duplicate business actions.
''',
"README.md": '''# Stripe / IBM Code Engine Integration

Minimal server-side Stripe service for IBM Code Engine.

Endpoints:
- GET /health
- POST /create-payment-intent
- POST /webhook/stripe

Supply STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET through deployment secrets, never source control.
'''
}

for rel, text in content.items():
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

zip_path = Path("/mnt/data/stripe_code_engine_integration.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(root.parent))

print(f"Created: {zip_path}")
