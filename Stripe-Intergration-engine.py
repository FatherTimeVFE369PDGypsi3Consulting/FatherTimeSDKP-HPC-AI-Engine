"""
Module: Stripe-Intergration-engine.py
Repository: FatherTimeSDKP-HPC-AI-Engine
Description: Secure Flask-based Stripe payment intent and webhook processing 
             server optimized for IBM Code Engine containerized deployment.
"""

import os
import sys
import logging
import stripe
from flask import Flask, request, jsonify

# Configure logging for containerized stdout tracking
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("FatherTimeSDKP-StripeEngine")

app = Flask(__name__)

# Load and validate environment configuration on startup
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

if not STRIPE_SECRET_KEY:
    logger.error("CRITICAL: STRIPE_SECRET_KEY environment variable is missing.")
if not WEBHOOK_SECRET:
    logger.error("CRITICAL: STRIPE_WEBHOOK_SECRET environment variable is missing.")

stripe.api_key = STRIPE_SECRET_KEY

# In-memory or state tracker for idempotent event processing
PROCESSED_EVENTS = set()

@app.get("/health")
def health_check():
    """Health check endpoint for IBM Code Engine load balancer probes."""
    return jsonify({
        "status": "healthy",
        "service": "FatherTimeSDKP-HPC-AI-Engine",
        "stripe_configured": bool(STRIPE_SECRET_KEY)
    }), 200

@app.post("/create-payment-intent")
def create_payment_intent():
    """Creates a Stripe Payment Intent linked to engine API credit allocation."""
    data = request.get_json(silent=True) or {}
    
    try:
        amount = int(data.get("amount", 1000)) # Default amount in cents
        currency = data.get("currency", "usd")
        tier = data.get("tier", "standard_research")
        
        logger.info(f"Generating payment intent for tier: {tier}, amount: {amount} {currency}")
        
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={"enabled": True},
            metadata={
                "tier": tier,
                "engine_framework": "FatherTimeSDKP"
            }
        )
        
        return jsonify({
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "status": "created"
        }), 200

    except KeyError as ke:
        logger.error(f"Missing required parameter: {ke}")
        return jsonify({"error": f"Missing key: {str(ke)}"}), 400
    except Exception as e:
        logger.error(f"Failed to create payment intent: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.post("/webhook/stripe")
def stripe_webhook():
    """Cryptographically verifies and handles incoming Stripe webhook events."""
    payload = request.get_data()
    signature_header = request.headers.get("Stripe-Signature")

    if not signature_header:
        logger.warning("Webhook request received without Stripe-Signature header.")
        return jsonify({"error": "Missing signature header"}), 400

    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload structure in webhook: {e}")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        return jsonify({"error": "Invalid signature"}), 400

    event_id = event.get("id")
    event_type = event.get("type")

    # Ensure idempotency to protect against duplicate webhook deliveries
    if event_id in PROCESSED_EVENTS:
        logger.info(f"Event {event_id} already processed. Skipping.")
        return jsonify({"status": "already_processed"}), 200

    PROCESSED_EVENTS.add(event_id)
    logger.info(f"Successfully verified incoming Stripe event: {event_type} [{event_id}]")

    # Handle specific event triggers
    if event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        intent_id = payment_intent.get("id")
        metadata = payment_intent.get("metadata", {})
        logger.info(f"Payment Intent Succeeded: {intent_id} | Tier: {metadata.get('tier')}")
        # TODO: Implement persistence logic to provision API access credits

    elif event_type == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        invoice_id = invoice.get("id")
        logger.info(f"Invoice Payment Succeeded: {invoice_id}")
        # TODO: Implement subscription renewal logic

    return jsonify({"received": True}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting FatherTimeSDKP Stripe Engine server on port {port}...")
    app.run(host="0.0.0.0", port=port)
