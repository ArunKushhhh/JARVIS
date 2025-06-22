from livekit.agents import RunContext, function_tool
import requests
import logging
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

@function_tool()
async def get_weather(
    context: RunContext,
    city: str) -> str:
    """
    Get current weather for a city
    """
    try: 
        response = requests.get(
            f"https://wttr.in/{city}?format=3"
        )
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}"
    except Exception as e:
        logging.error(f"Error retreiving weather for {city}: {e}")
        return f"An error occured while retrieving weather for {city}"

@function_tool()
async def search_web(
    context: RunContext,
    query: str) -> str:
    """
    Search the web using DuckDuckGo
    """
    try: 
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}" )
        return results
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occured while searching the web for '{query}'"

@function_tool()
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None ) -> str:
    """
    Send an email through gmail SMTP

    Args:
        to_email: Recipients email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional cc email address
    """
    try:
        # Gmail smtp configuration
        smtp_server = "stmp.google.com"
        smtp_port = 573

        # getting gmail creds from dotenv
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_PASSWORD") #using google app password

        if not gmail_user or not gmail_password:
            logging.error(f"Error sending smtp request as creds not found in env var")
            return "Error sending email: Creds not found in env var/ maybe not configured"

        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        recipients = [to_email]

        # adding cc mails to recipients if present
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)

        # email content
        msg.attach(MIMEText(message, 'plain'))

        # connecting to gmail smtp server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.startts()
        server.login(gmail_user, gmail_password)

        # send email
        text = msg.as_string()
        server.sendmail(gmail_user, recipients, text)
        server.quit()

        logging.info(f"Email send successfully to {to_email}")
        return f"Email sent successfully to {to_email}"

    except smtplib.SMTPAuthenticationError:
        logging.error(f"gmail authentication failed")
        return f"Error sending email: Gmail authentication failed. Please check your gmail creds"
    
    except smtplib.SMTPException as e:
        logging.error(f"SMTP Exception occured: {e}")
        return f"Error sending email: SMTP Error - {str(e)}"

    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An unknown error occured while sending email: {e}"
    