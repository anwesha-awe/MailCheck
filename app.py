
from flask import Flask, render_template, request
import re
import socket
import smtplib
import dns.resolver
import dns.exception

app = Flask(__name__)

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)


def smtp_verify(email, mx_host):
    """Attempt recipient verification without sending a message."""

    try:
        with smtplib.SMTP(timeout=5) as server:
            server.connect(mx_host, 25)
            server.ehlo_or_helo_if_needed()

            # Some servers require TLS; do not downgrade
            # or assume a plaintext check is reliable.
            if server.has_extn("starttls"):
                server.starttls()
                server.ehlo()

            code, response = server.mail("")

            if code != 250:
                return "Unknown", "SMTP sender verification unavailable"

            code, response = server.rcpt(email)

            if code in (250, 251):
                return (
                    "Likely Delivered",
                    "Recipient accepted by mail server; delivery not guaranteed"
                )

            if code in (550, 551, 553):
                return (
                    "Unknown",
                    "Recipient rejected; mailbox existence not confirmed"
                )

            return "Unknown", "Mail server did not confirm recipient"

    except (
        OSError,
        smtplib.SMTPException,
        TimeoutError
    ):
        return "Unknown", "SMTP verification unavailable"


def check_email(email):
    email = email.strip()

    if not EMAIL_PATTERN.fullmatch(email):
        return "Likely Bounce", "Invalid email format"

    domain = email.rsplit("@", 1)[1]

    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        records = sorted(answers, key=lambda mx: mx.preference)

        if len(records) == 1:
            if records[0].preference == 0 and str(records[0].exchange) == ".":
                return "Likely Bounce", "Domain does not accept email"

        if records:
            mx_host = str(records[0].exchange).rstrip(".")
            return smtp_verify(email, mx_host)

        return "Unknown", "No MX records returned"

    except dns.resolver.NXDOMAIN:
        return "Likely Bounce", "Domain does not exist"

    except dns.resolver.NoAnswer:
        try:
            for record_type in ("A", "AAAA"):
                try:
                    dns.resolver.resolve(domain, record_type, lifetime=5)
                    return "Unknown", "Domain may accept email via A/AAAA"
                except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                    continue
        except (dns.exception.Timeout, dns.resolver.NoNameservers):
            return "Unknown", "DNS verification inconclusive"

        return "Likely Bounce", "No mail destination found"

    except (dns.exception.Timeout, dns.resolver.NoNameservers):
        return "Unknown", "DNS lookup unavailable"

    except Exception:
        return "Unknown", "Verification could not be completed"



@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    emails_text = ""
    demo_mode = False

    if request.method == "POST":
        emails_text = request.form.get("emails", "")
        demo_mode = request.form.get("demo_mode") == "on"

        emails = re.split(r"[\s,;]+", emails_text.strip())

        for email in emails[:100]:
            if not email:
                continue

            if demo_mode:
                demo_results = {
                    "delivered@demo.example": (
                        "Likely Delivered",
                        "SIMULATED: Test server accepted recipient"
                    ),
                    "bounce@demo.example": (
                        "Likely Bounce",
                        "SIMULATED: Test server rejected recipient"
                    ),
                    "unknown@demo.example": (
                        "Unknown",
                        "SIMULATED: Test server could not verify recipient"
                    )
                }

                status, reason = demo_results.get(
                    email.lower(),
                    (
                        "Unknown",
                        "SIMULATED: No predefined result for this address"
                    )
                )
            else:
                status, reason = check_email(email)

            results.append({
                "email": email,
                "status": status,
                "reason": reason
            })

    return render_template(
        "index.html",
        results=results,
        emails_text=emails_text,
        demo_mode=demo_mode
    )


if __name__ == "__main__":
    app.run(debug=True)
