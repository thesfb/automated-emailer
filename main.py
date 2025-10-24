import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = '<key>'  # Required for flash messages

def send_email_message(
    sender_email: str,
    app_password: str,
    to_email: str,
    cc_email: str,
    subject: str,
    body: str,
    attachment_file=None
) -> tuple[bool, str]:
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Cc'] = cc_email
    msg['Subject'] = subject

    recipients = [to_email]
    if cc_email:
        recipients.append(cc_email)

    msg.attach(MIMEText(body, 'plain'))

    if attachment_file and attachment_file.filename:
        try:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_file.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={attachment_file.filename}")
            msg.attach(part)
        except Exception as e:
            print(f"Attachment Error: {e}")
            return False, f"ERROR: Could not process attachment {attachment_file.filename}. Details: {e}"

    server = None
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        return True, f"Email sent to {to_email} with CC: {cc_email or 'None'}."
    except smtplib.SMTPAuthenticationError:
        return False, "ERROR: Authentication failed. Check email and App Password."
    except Exception as e:
        return False, f"ERROR: Unexpected error during sending. Details: {e}"
    finally:
        if server:
            server.quit()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/send', methods=['POST'])
def send_email():
    sender_email = request.form['sender_email']
    app_password = request.form['app_password']
    to_email = request.form['to_email']
    cc_email = request.form.get('cc_email', '')
    subject = request.form['subject']
    body = request.form['body']
    attachment = request.files.get('attachment')

    success, message = send_email_message(
        sender_email,
        app_password,
        to_email,
        cc_email,
        subject,
        body,
        attachment_file=attachment
    )

    flash(message, 'success' if success else 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
