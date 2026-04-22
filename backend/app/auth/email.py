import resend

from app.config import settings

resend.api_key = settings.resend_api_key

SENDER = "Martin <noreply@martinlaw.co.za>"


async def send_verification_email(email: str, token: str) -> None:
    verify_url = f"{settings.frontend_url}/auth/verify?token={token}"
    resend.Emails.send({
        "from": SENDER,
        "to": [email],
        "subject": "Verify your Martin account",
        "html": (
            f"<p>Click the link below to verify your email address:</p>"
            f'<p><a href="{verify_url}">{verify_url}</a></p>'
            f"<p>This link expires in 24 hours.</p>"
        ),
    })


async def send_reset_password_email(email: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/auth/reset-password?token={token}"
    resend.Emails.send({
        "from": SENDER,
        "to": [email],
        "subject": "Reset your Martin password",
        "html": (
            f"<p>Click the link below to reset your password:</p>"
            f'<p><a href="{reset_url}">{reset_url}</a></p>'
            f"<p>This link expires in 1 hour. If you didn't request this, ignore this email.</p>"
        ),
    })
