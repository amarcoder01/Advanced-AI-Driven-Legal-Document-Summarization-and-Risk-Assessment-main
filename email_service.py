import smtplib
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import io
import logging
from fpdf import FPDF
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

class EmailService:
    """Service class for handling email functionality."""
    
    def __init__(self):
        """Initialize the email service."""
        self.smtp_server = None
        self.smtp_port = None
        self.sender_email = None
        self.sender_password = None
        self._load_email_config()

    def _load_email_config(self):
        """Load email configuration from Streamlit secrets."""
        try:
            self.smtp_server = st.secrets["email"]["SMTP_SERVER"]
            self.smtp_port = int(st.secrets["email"]["SMTP_PORT"])
            self.sender_email = st.secrets["email"]["SENDER_EMAIL"]
            self.sender_password = st.secrets["email"]["SENDER_PASSWORD"]
        except Exception as e:
            logging.error(f"Error loading email configuration: {str(e)}")

    def generate_email_pdf(self, content):
        """Generate a professionally formatted PDF for email attachment"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Add a header with logo placeholder
            pdf.set_font("Arial", "B", 16)
            pdf.cell(190, 10, "Legal Document Analysis", 0, 1, "C")
            pdf.set_font("Arial", "I", 10)
            pdf.cell(190, 5, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
            pdf.line(10, 25, 200, 25)
            pdf.ln(5)
            
            # Process the content by sections
            content_parts = content.split("\n\n")
            
            for part in content_parts:
                if "DOCUMENT SUMMARY" in part:
                    # Summary section
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(190, 10, "Document Summary", 0, 1, "L")
                    pdf.set_font("Arial", "", 11)
                    summary_content = part.split("-" * 30)[1].strip() if "-" * 30 in part else part
                    pdf.multi_cell(190, 7, summary_content)
                    pdf.ln(5)
                    
                elif "RISK SCORE" in part:
                    # Risk score section
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(190, 10, "Risk Assessment Score", 0, 1, "L")
                    pdf.set_font("Arial", "", 11)
                    score_content = part.split("-" * 30)[1].strip() if "-" * 30 in part else part
                    pdf.multi_cell(190, 7, score_content)
                    pdf.ln(5)
                    
                elif "RISK ANALYSIS" in part:
                    # Risk analysis section
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(190, 10, "Detailed Risk Analysis", 0, 1, "L")
                    pdf.set_font("Arial", "", 11)
                    analysis_content = part.split("-" * 30)[1].strip() if "-" * 30 in part else part
                    pdf.multi_cell(190, 7, analysis_content)
                    pdf.ln(5)
                
                else:
                    # Other content
                    pdf.set_font("Arial", "", 11)
                    pdf.multi_cell(190, 7, part)
                    pdf.ln(3)
            
            # Add footer
            pdf.set_y(-15)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(0, 10, f"Page {pdf.page_no()}/{{nb}}", 0, 0, "C")
            
            pdf_bytes = pdf.output(dest="S").encode("latin1")
            buf = io.BytesIO(pdf_bytes)
            buf.seek(0)
            return buf
            
        except Exception as e:
            logging.error(f"Error generating PDF: {str(e)}")
            return None

    def send_email(self, recipient_email, subject, body, attachment=None, attachment_name=None, attachment_type=None):
        """Send an email with optional attachment."""
        try:
            if not all([self.smtp_server, self.smtp_port, self.sender_email, self.sender_password]):
                return False, "Email configuration is incomplete. Please check your Streamlit secrets."
                
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment if provided
            if attachment and attachment_name and attachment_type:
                attachment_data = attachment
                
                if attachment_type == "pdf":
                    part = MIMEApplication(attachment_data.read() if hasattr(attachment_data, 'read') else attachment_data, Name=attachment_name)
                    part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
                    msg.attach(part)
                elif attachment_type == "docx":
                    part = MIMEApplication(attachment_data.getvalue(), Name=attachment_name)
                    part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
                    msg.attach(part)
                elif attachment_type == "txt":
                    part = MIMEText(attachment_data)
                    part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
                    msg.attach(part)
                    
            # Connect to server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            return True, "Email sent successfully!"
            
        except Exception as e:
            logging.error(f"Error sending email: {str(e)}")
            return False, f"Error sending email: {str(e)}"

    @staticmethod
    def validate_email(email):
        """Simple email validation"""
        if not email:
            return False
        if "@" not in email or "." not in email:
            return False
        return True

    def prepare_email_content(self) -> str:
        """Prepare comprehensive email content including all analysis components."""
        content_parts = []
        
        # Add header
        content_parts.extend([
            "LEGAL DOCUMENT ANALYSIS REPORT",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 80,
            "\n"
        ])
        
        # Document Summary
        if st.session_state.get("summary"):
            content_parts.extend([
                "DOCUMENT SUMMARY",
                "-" * 50,
                st.session_state.summary,
                "\n"
            ])
        
        # Risk Score Analysis
        if st.session_state.get("risk_score"):
            content_parts.extend([
                "RISK SCORE ANALYSIS",
                "-" * 50,
                f"Overall Risk Score: {st.session_state.risk_score}/100",
                f"Risk Level: {st.session_state.risk_level}",
                "\n"
            ])
        
        # Detailed Risk Analysis
        if st.session_state.get("risks"):
            content_parts.extend([
                "DETAILED RISK ANALYSIS",
                "-" * 50,
                st.session_state.risks,
                "\n"
            ])
        
        # Compliance Analysis
        if st.session_state.get("compliance_results"):
            content_parts.extend([
                "COMPLIANCE ANALYSIS",
                "-" * 50,
                st.session_state.compliance_results,
                "\n"
            ])
        
        # Key Findings
        if st.session_state.get("key_findings"):
            content_parts.extend([
                "KEY FINDINGS",
                "-" * 50,
                st.session_state.key_findings,
                "\n"
            ])
        
        # Recommendations
        if st.session_state.get("recommendations"):
            content_parts.extend([
                "RECOMMENDATIONS",
                "-" * 50,
                st.session_state.recommendations,
                "\n"
            ])
        
        # Add footer
        content_parts.extend([
            "-" * 80,
            "End of Report",
            "\n"
        ])
        
        return "\n".join(content_parts)

def email_ui_section():
    """Display email UI section with comprehensive options."""
    st.markdown("### 📧 Email Analysis")
    
    if not st.session_state.get("extracted_text"):
        st.info("Upload and analyze a document to enable email options.")
        return
        
    # Email input
    recipient_email = st.text_input("Recipient Email Address")
    
    if recipient_email:
        email_service = EmailService()
        
        if not email_service.validate_email(recipient_email):
            st.error("Please enter a valid email address.")
            return
            
        # Email customization
        st.markdown("#### Email Options")
        
        subject = st.text_input(
            "Email Subject",
            value="Legal Document Analysis Report",
            help="Customize the email subject line"
        )
        
        # Prepare email content
        email_content = email_service.prepare_email_content()
        
        if email_content:
            # Format selection
            attachment_format = st.selectbox(
                "Attachment Format",
                ["PDF", "DOCX", "TXT"],
                help="Choose the format for the analysis attachment"
            )
            
            if st.button("Send Email"):
                try:
                    with st.spinner("Sending email..."):
                        # Generate attachment
                        if attachment_format == "PDF":
                            attachment = email_service.generate_email_pdf(email_content)
                            attachment_name = f"legal_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                            mime_type = "application/pdf"
                        elif attachment_format == "DOCX":
                            attachment = email_service.generate_email_docx(email_content)
                            attachment_name = f"legal_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
                            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        else:  # TXT
                            attachment = email_content.encode('utf-8')
                            attachment_name = f"legal_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                            mime_type = "text/plain"
                        
                        # Send email
                        email_service.send_email(
                            recipient_email=recipient_email,
                            subject=subject,
                            body="Please find attached the legal document analysis report.",
                            attachment=attachment,
                            attachment_name=attachment_name,
                            attachment_type=mime_type
                        )
                        
                        st.success("Email sent successfully! 📨")
                except Exception as e:
                    st.error(f"Error sending email: {str(e)}")
                    logging.error(f"Email error: {str(e)}", exc_info=True)
        else:
            st.info("Analyze the document first to enable email options.") 