
from flask import Flask, render_template, request
import re
import dns.resolver
import dns.exception

app = Flask(__name__)

def check_email(email):
    email = email.strip()

    pattern = r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"

    if not re.fullmatch(pattern, email):
        return "Likely Bounce", "Invalid email format"

    domain = email.rsplit("@", 1)[1]

    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        records = list(answers)

        # Null MX means the domain does not accept email.
        if len(records) == 1:
            record = records[0]
            if record.preference == 0 and str(record.exchange) == ".":
                return "Likely Bounce", "Domain does not accept email"

        return "Unknown", "Mail server found; mailbox not verified"

    except dns.resolver.NXDOMAIN:
        return "Likely Bounce", "Domain does not exist"

    except dns.resolver.NoAnswer:
        # Some domains receive mail via A/AAAA records.
        try:
            for record_type in ("A", "AAAA"):
                try:
                    dns.resolver.resolve(domain, record_type, lifetime=5)
                    return "Unknown", "Domain has a possible mail destination"
                except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                    continue
        except (dns.exception.Timeout, dns.resolver.NoNameservers):
            return "Unknown", "DNS lookup inconclusive"

        return "Likely Bounce", "No mail destination found"

    except (dns.exception.Timeout, dns.resolver.NoNameservers):
        return "Unknown", "DNS lookup failed or timed out"

    except Exception:
        return "Unknown", "Unable to complete verification"


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    emails_text = ""

    if request.method == "POST":
        emails_text = request.form.get("emails", "")
        emails = re.split(r"[\s,;]+", emails_text.strip())

        for email in emails[:100]:
            if email:
                status, reason = check_email(email)
                results.append({
                    "email": email,
                    "status": status,
                    "reason": reason
                })

    return render_template(
        "index.html",
        results=results,
        emails_text=emails_text
    )


if __name__ == "__main__":
    app.run(debug=True)
