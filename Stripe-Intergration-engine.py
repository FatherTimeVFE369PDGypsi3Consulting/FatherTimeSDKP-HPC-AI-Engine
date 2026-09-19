import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Track processed webhook event IDs to ensure idempotency
processed_events = set()

@app.get("/health")
def health():
    return jsonify({"status": "ok", "engine": "FatherTimeSDKP-HPC-AI-Engine"})

@app.post("/create-payment-intent")
def create_payment_intent():
    data = request.get_json(silent=True) or {}
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(data.get("amount", 1000)), # Default minimum tier amount in cents
            currency=data.get("currency", "usd"),
            automatic_payment_methods={"enabled": True},
            metadata={
                "tier": data.get("tier", "standard_research"),
                "engine_version": "FatherTimeSDKP-v1.0"
            }
        )
        return jsonify({"client_secret": intent.client_secret, "id": intent.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.post("/webhook/stripe")
def stripe_webhook():
    payload = request.get_data()
    signature = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return jsonify({"error": "invalid signature"}), 400

    event_id = event["id"]
    if event_id in processed_events:
        return jsonify({"status": "already_processed"}), 200
    
    processed_events.add(event_id)

    event_type = event["type"]
    if event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        # TODO: Hook into your user credit database using payment_intent["id"] and metadata
        print(f"Payment successful for intent: {payment_intent['id']}")
        
    elif event_type == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        # TODO: Renew subscription API compute credits
        print(f"Invoice paid successfully: {invoice['id']}")

    return jsonify({"received": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
