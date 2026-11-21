import smtplib
import imaplib
import email
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

# def fetch_inbox_summary() -> str:
#     """Connects to Gmail via IMAP and returns a summary of up to 5 unread emails."""
#     if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
#         return "[MOCK INBOX] ID: 1 | From: client@techcorp.com | Subject: Friday Budget Review"
        
#     try:
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#         mail.select("inbox")
        
#         status, messages = mail.search(None, "UNSEEN")
#         mail_ids = messages[0].split()[-5:] # Get last 5 unread
        
#         if not mail_ids:
#             return "No unread emails found."
            
#         summary = []
#         for e_id in mail_ids:
#             status, msg_data = mail.fetch(e_id, "(BODY[HEADER.FIELDS (FROM SUBJECT)])")
#             for response_part in msg_data:
#                 if isinstance(response_part, tuple):
#                     msg = email.message_from_bytes(response_part[1])
#                     summary.append(f"ID: {e_id.decode()} | From: {msg.get('From')} | Subject: {msg.get('Subject')}")
                    
#         return "\n".join(summary)
#     except Exception as e:
#         return f"IMAP Error: {e}"


def fetch_email_summaries(sender: str = None, keyword: str = None, unread_only: bool = False) -> str:
    """Connects to Gmail via IMAP and returns emails based on dynamic search criteria."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return f"[MOCK INBOX] ID: 1 | From: {sender or 'manager@techcorp.com'} | Subject: Important Project Update"
        
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")
        
        # Build IMAP search criteria dynamically
        criteria = []
        if unread_only:
            criteria.append("UNSEEN")
        if sender:
            criteria.append(f'FROM "{sender}"')
        if keyword:
            criteria.append(f'SUBJECT "{keyword}"')
            
        # If no criteria provided, fetch all emails (IMAP uses 'ALL')
        if not criteria:
            criteria.append("ALL")
            
        search_string = " ".join(criteria)
        
        status, messages = mail.search(None, search_string)
        
        if not messages[0]:
            return "No emails found matching your criteria."
            
        # Get the 5 most recent matching emails
        mail_ids = messages[0].split()[-5:]
        
        summary = []
        for e_id in mail_ids:
            status, msg_data = mail.fetch(e_id, "(BODY[HEADER.FIELDS (FROM SUBJECT)])")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    summary.append(f"ID: {e_id.decode()} | From: {msg.get('From')} | Subject: {msg.get('Subject')}")
                    
        return "\n".join(summary)
    except Exception as e:
        return f"IMAP Search Error: {e}"

def fetch_full_email(email_id: str) -> str:
    """Fetches the full body of a specific email ID."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return "From: client@techcorp.com\nSubject: Friday Budget Review\nBody: Can we meet Friday to discuss the Q3 budget?"
        
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")
        
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                    
                return f"From: {msg.get('From')}\nSubject: {msg.get('Subject')}\nBody: {body}"
    except Exception as e:
        return f"IMAP Fetch Error: {e}"

def send_email_smtp(to_address: str, subject: str, body: str) -> str:
    """Executes the final SMTP send action."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return f"✅ [MOCK SUCCESS] Email sent to {to_address}"
        
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_address

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return f"✅ Email successfully sent to {to_address}!"
    except Exception as e:
        return f"❌ SMTP Error: {e}"