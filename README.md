
# MailCheck – Email Deliverability Checker

MailCheck is a web application built using Python and Flask
that checks multiple email addresses and estimates whether
they are likely to bounce or have an unknown delivery status.

## Features

- Check up to 100 email addresses at once
- Validate email address format
- Check DNS and MX records
- Detect nonexistent domains
- Display results in a user-friendly table
- Explain each verification result
- Responsive dark-themed interface

## Technologies Used

- Python
- Flask
- HTML
- CSS
- dnspython

## How It Works

1. Users paste a list of email addresses.
2. The application checks email syntax.
3. It looks up the domain's DNS and MX records.
4. It classifies each email address.

### Possible Results

- Likely Bounce: Invalid syntax or a domain that cannot receive email.
- Unknown: The domain may receive email, but the mailbox
  cannot be verified.
- Likely Delivered: Reserved for positive mailbox-level
  verification. Not produced by this DNS-only version.

## How to Run Locally

1. Clone or download the repository.
2. Open the project folder.
3. Create a virtual environment:

   python -m venv venv

4. Install the dependencies:

   pip install -r requirements.txt

5. Start the application:

   python app.py

6. Open http://127.0.0.1:5000 in your browser.

## Deployment

The application can be deployed on Render.

Build command:
pip install -r requirements.txt

Start command:
gunicorn app:app

## Limitations

- The application cannot guarantee email delivery.
- A valid MX record does not prove a mailbox exists.
- The current version does not perform SMTP mailbox verification.
- Some hosting providers block outgoing SMTP connections.
  This version uses DNS checks and does not require SMTP.
- DNS timeouts and inconclusive results are classified as Unknown.
- No emails are sent to the addresses being checked.

## Disclaimer

Results are estimates and should not be treated as
guaranteed delivery outcomes.
