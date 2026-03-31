from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from ..schemas.auth import CurrentUser
from ..dependencies import require_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create-portal-session")
async def create_portal_session(
    user: CurrentUser = Depends(require_user),
) -> dict:
    from archon.config.settings import settings

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Billing not configured")

    try:
        import stripe
        stripe.api_key = settings.stripe_secret_key

        # Look up Stripe customer by Clerk user ID metadata
        # In production, store stripe_customer_id in UserRow
        customers = stripe.Customer.list(
            email=user.email, limit=1
        )
        if not customers.data:
            raise HTTPException(status_code=404, detail="No billing account found. Contact support.")

        customer_id = customers.data[0].id
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url="http://localhost:3000/billing",
        )
        return {"url": session.url}

    except ImportError:
        raise HTTPException(status_code=503, detail="Stripe SDK not installed")
    except stripe.StripeError as exc:
        logger.error("Stripe error: %s", exc)
        raise HTTPException(status_code=500, detail="Billing service error")


@router.post("/webhook")
async def stripe_webhook(request: Request) -> JSONResponse:
    from archon.config.settings import settings

    if not settings.stripe_secret_key:
        return JSONResponse(status_code=503, content={"detail": "Billing not configured"})

    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        import stripe
        stripe.api_key = settings.stripe_secret_key

        # TODO: verify webhook signature with endpoint secret
        event = stripe.Event.construct_from(
            stripe.util.json.loads(payload), stripe.api_key
        )

        if event.type == "customer.subscription.updated":
            subscription = event.data.object
            logger.info("Subscription updated: %s -> %s", subscription.id, subscription.status)
            # TODO: update UserRow.plan based on subscription price ID

        elif event.type == "customer.subscription.deleted":
            subscription = event.data.object
            logger.info("Subscription cancelled: %s", subscription.id)
            # TODO: downgrade UserRow.plan to "starter"

        elif event.type == "invoice.payment_failed":
            invoice = event.data.object
            logger.warning("Payment failed for customer: %s", invoice.customer)

        return JSONResponse(status_code=200, content={"received": True})

    except Exception as exc:
        logger.error("Webhook error: %s", exc)
        return JSONResponse(status_code=400, content={"error": str(exc)})
