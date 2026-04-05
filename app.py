import os
import smtplib
import pandas as pd
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables (EMAIL_PASSWORD, SENDER_EMAIL, etc.)
load_dotenv()

class EmailSender:
    def __init__(self, server, port, sender_email, sender_password):
        self.server = server
        self.port = port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_status_email(self, recipient_email: str) -> bool:
        """Sends a notification email to the recipient."""
        try:
            with smtplib.SMTP(self.server, self.port) as smtp_server:
                smtp_server.starttls()
                smtp_server.login(self.sender_email, self.sender_password)
                
                message = MIMEMultipart()
                message["From"] = self.sender_email
                message["To"] = recipient_email
                message["Subject"] = "Assessment Status Update: Completed"
                
                body = "Hello,\n\nYour assessment status has been marked as completed. Thank you!"
                message.attach(MIMEText(body, "plain"))
                
                smtp_server.send_message(message)
                print(f"✅ Successfully sent email to {recipient_email}") # Console log preserved
                return True
                
        except Exception as e:
            print(f"❌ Failed to send email to {recipient_email}: {e}") # Console log preserved
            return False

def main():
    # --- Streamlit UI Setup ---
    st.title("✉️ Raters Email Notification System")
    st.write("Upload your candidate CSV to automatically send completion emails.")

    # Email Configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL") 
    SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")
    
    if not SENDER_PASSWORD or not SENDER_EMAIL:
        st.error("Error: Missing SENDER_EMAIL or EMAIL_PASSWORD in environment variables. Please check your .env file.")
        return

    email_sender = EmailSender(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD)

    # --- Streamlit File Uploader ---
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

    if uploaded_file is not None:
        # Process the CSV
        try:
            # Load the data from the uploaded file
            df = pd.read_csv(uploaded_file)
            
            st.write("**Data Preview:**")
            st.dataframe(df) # Display the CSV to the user
            
            if st.button("Process & Send Emails", type="primary"):
                with st.spinner("Processing data and sending emails..."):
                    
                    # Clean column names (removes spaces like "name " -> "name")
                    df.columns = df.columns.str.strip()
                    
                    # Clean string values in the status column and filter for 'completed'
                    completed_records = df[df['status'].str.strip().str.lower() == 'completed']
                    
                    # Extract unique emails to prevent sending multiple emails to the same person
                    emails_to_notify = completed_records['email'].dropna().unique()
                    
                    st.info(f"Found {len(emails_to_notify)} unique candidate(s) with 'completed' status.")
                    
                    # Send emails
                    for email in emails_to_notify:
                        email = email.strip()
                        success = email_sender.send_status_email(email)
                        
                        # Show result in the Streamlit UI
                        if success:
                            st.success(f"✅ Successfully sent email to {email}")
                        else:
                            st.error(f"❌ Failed to send email to {email}")
                
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()