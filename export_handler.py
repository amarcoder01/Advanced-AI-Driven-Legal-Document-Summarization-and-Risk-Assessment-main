import streamlit as st
import io
import logging
from datetime import datetime
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Optional, BinaryIO

class ExportHandler:
    def __init__(self):
        """Initialize export handler."""
        pass

    def generate_txt(self, content: str) -> str:
        """Generate a well-formatted text document."""
        lines = content.split("\n")
        formatted_lines = []
        
        # Add header
        formatted_lines.append("=" * 80)
        formatted_lines.append("LEGAL DOCUMENT ANALYSIS REPORT")
        formatted_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        formatted_lines.append("=" * 80)
        formatted_lines.append("")
        
        # Process content with proper spacing
        in_section = False
        for line in lines:
            if "DOCUMENT SUMMARY" in line or "RISK ANALYSIS" in line or "RISK SCORE" in line:
                if in_section:
                    formatted_lines.append("")
                
                in_section = True
                section_title = line.strip()
                
                formatted_lines.append("")
                formatted_lines.append(section_title)
                formatted_lines.append("-" * len(section_title))
            elif line.strip() == "=" * 50:
                continue
            else:
                if line.strip():
                    formatted_lines.append(line)
        
        # Add footer
        formatted_lines.append("")
        formatted_lines.append("-" * 80)
        formatted_lines.append("End of Report")
        
        return "\n".join(formatted_lines)

    def generate_docx(self, content: str) -> BinaryIO:
        """Generate a professionally formatted Word document."""
        doc = Document()
        
        # Set document properties
        doc.core_properties.title = "Legal Document Analysis"
        doc.core_properties.author = "AI Legal Document Assistant"
        
        # Add header with title
        header = doc.add_heading("Legal Document Analysis Report", level=1)
        header.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add date
        date_paragraph = doc.add_paragraph()
        date_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        date_run = date_paragraph.add_run(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        date_run.italic = True
        
        # Add horizontal line
        doc.add_paragraph("_" * 60)
        
        # Process content by sections
        lines = content.split("\n")
        current_section = None
        
        for line in lines:
            if "DOCUMENT SUMMARY" in line:
                doc.add_paragraph()
                heading = doc.add_heading("Document Summary", level=2)
                current_section = "summary"
            elif "RISK SCORE" in line:
                doc.add_paragraph()
                heading = doc.add_heading("Risk Assessment Score", level=2)
                current_section = "risk_score"
            elif "RISK ANALYSIS" in line:
                doc.add_paragraph()
                heading = doc.add_heading("Detailed Risk Analysis", level=2)
                current_section = "risk_analysis"
            elif line.strip() and not line.startswith("="):
                p = doc.add_paragraph()
                
                if current_section == "risk_analysis":
                    if line.lower().startswith(("high", "medium", "low")) and ":" in line:
                        priority, description = line.split(":", 1)
                        priority = priority.strip()
                        
                        priority_run = p.add_run(f"{priority}: ")
                        priority_run.bold = True
                        
                        if "high" in priority.lower():
                            priority_run.font.color.rgb = RGBColor(255, 0, 0)
                        elif "medium" in priority.lower():
                            priority_run.font.color.rgb = RGBColor(255, 165, 0)
                        
                        p.add_run(description.strip())
                    else:
                        p.add_run(line)
                else:
                    p.add_run(line)
        
        # Add footer
        doc.add_paragraph()
        footer = doc.add_paragraph("End of Report")
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Save to buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    def generate_pdf(self, content: str) -> BinaryIO:
        """Generate a professionally formatted PDF document."""
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'Legal Document Analysis Report', 0, 1, 'C')
                self.set_font('Arial', 'I', 10)
                self.cell(0, 5, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
                self.ln(5)
                self.line(10, 25, 200, 25)
                self.ln(10)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        content_parts = content.split("\n\n")
        current_section = None
        
        for part in content_parts:
            if "DOCUMENT SUMMARY" in part:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Document Summary", 0, 1, "L")
                pdf.set_font("Arial", "", 11)
                
                summary_content = part.split("-" * 30)[1].strip() if "-" * 30 in part else part.replace("DOCUMENT SUMMARY", "").strip()
                pdf.multi_cell(0, 7, self._sanitize_text_for_pdf(summary_content))
                pdf.ln(5)
                
            elif "RISK SCORE" in part:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Risk Assessment Score", 0, 1, "L")
                pdf.set_font("Arial", "", 11)
                
                score_content = part.split("-" * 30)[1].strip() if "-" * 30 in part else part.replace("RISK SCORE", "").strip()
                
                for line in score_content.split("\n"):
                    if "Score:" in line or "Risk Level:" in line:
                        pdf.set_font("Arial", "B", 11)
                        pdf.cell(0, 7, line, 0, 1)
                        pdf.set_font("Arial", "", 11)
                    else:
                        pdf.cell(0, 7, line, 0, 1)
                        
                pdf.ln(5)
                
            elif "RISK ANALYSIS" in part:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Detailed Risk Analysis", 0, 1, "L")
                pdf.set_font("Arial", "", 11)
                
                analysis_content = part.split("-" * 30)[1].strip() if "-" * 30 in part else part.replace("RISK ANALYSIS", "").strip()
                
                if "HIGH PRIORITY RISKS" in analysis_content:
                    sections = analysis_content.split("\n\n")
                    for section in sections:
                        if "HIGH PRIORITY RISKS" in section:
                            pdf.set_font("Arial", "B", 12)
                            pdf.set_text_color(255, 0, 0)
                            pdf.cell(0, 10, "High Priority Risks", 0, 1)
                            pdf.set_text_color(0, 0, 0)
                            pdf.set_font("Arial", "", 11)
                            
                            for line in section.split("\n"):
                                if not line.strip() or "HIGH PRIORITY RISKS" in line:
                                    continue
                                pdf.multi_cell(0, 7, self._sanitize_text_for_pdf(line))
                                
                        elif "MEDIUM PRIORITY RISKS" in section:
                            pdf.set_font("Arial", "B", 12)
                            pdf.set_text_color(255, 165, 0)
                            pdf.cell(0, 10, "Medium Priority Risks", 0, 1)
                            pdf.set_text_color(0, 0, 0)
                            pdf.set_font("Arial", "", 11)
                            
                            for line in section.split("\n"):
                                if not line.strip() or "MEDIUM PRIORITY RISKS" in line:
                                    continue
                                pdf.multi_cell(0, 7, self._sanitize_text_for_pdf(line))
                                
                        elif "LOW PRIORITY RISKS" in section:
                            pdf.set_font("Arial", "B", 12)
                            pdf.set_text_color(0, 128, 0)
                            pdf.cell(0, 10, "Low Priority Risks", 0, 1)
                            pdf.set_text_color(0, 0, 0)
                            pdf.set_font("Arial", "", 11)
                            
                            for line in section.split("\n"):
                                if not line.strip() or "LOW PRIORITY RISKS" in line:
                                    continue
                                pdf.multi_cell(0, 7, self._sanitize_text_for_pdf(line))
                else:
                    pdf.multi_cell(0, 7, self._sanitize_text_for_pdf(analysis_content))
                    
                pdf.ln(5)
                
            else:
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 7, self._sanitize_text_for_pdf(part))
                pdf.ln(3)
        
        # Get PDF as bytes
        pdf_str = pdf.output(dest="S")
        if isinstance(pdf_str, str):
            pdf_bytes = pdf_str.encode("latin1")
        else:
            pdf_bytes = pdf_str
            
        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        return buffer

    def _sanitize_text_for_pdf(self, text: str) -> str:
        """Clean and sanitize text for PDF output."""
        if not text:
            return ""
        
        replacements = {
            '\u2013': '-',    # en dash
            '\u2014': '--',   # em dash
            '\u2018': "'",    # left single quote
            '\u2019': "'",    # right single quote
            '\u201c': '"',    # left double quote
            '\u201d': '"',    # right double quote
            '\u2022': '*',    # bullet
            '\u2026': '...', # ellipsis
            '\u00a0': ' ',   # non-breaking space
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        clean_text = ""
        for char in text:
            if ord(char) < 256:
                clean_text += char
            else:
                clean_text += '?'
                
        return clean_text

    def export_ui(self) -> None:
        """Handle export UI and functionality."""
        st.title("📤 Export Options")
        
        if not (st.session_state.get("summary") or st.session_state.get("risks")):
            st.info("Upload a document and analyze it to enable download options.")
            return
            
        st.subheader("📥 Download Results")
        
        # Initialize download options
        download_options = []
        if st.session_state.get("summary"):
            download_options.append("Summary")
        if st.session_state.get("risks"):
            download_options.append("Risk Analysis")
        
        selected_content = st.multiselect(
            "Select content to export:",
            options=download_options,
            default=download_options
        )
        
        if not selected_content:
            return
            
        # Generate content for export
        export_content = ""
        
        if "Summary" in selected_content and st.session_state.get("summary"):
            export_content += "DOCUMENT SUMMARY\n"
            export_content += "=" * 50 + "\n"
            export_content += st.session_state.summary + "\n\n"
            
        if "Risk Analysis" in selected_content and st.session_state.get("risks"):
            export_content += "RISK ANALYSIS\n"
            export_content += "=" * 50 + "\n"
            export_content += st.session_state.risks + "\n\n"
            
        # Export format selection
        export_format = st.selectbox(
            "Choose export format:",
            ["PDF", "DOCX", "TXT"]
        )
        
        # Add download button
        if export_format == "PDF":
            pdf_buffer = self.generate_pdf(export_content)
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="legal_analysis.pdf",
                mime="application/pdf"
            )
        elif export_format == "DOCX":
            docx_buffer = self.generate_docx(export_content)
            st.download_button(
                label="Download DOCX",
                data=docx_buffer,
                file_name="legal_analysis.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:  # TXT format
            txt_content = self.generate_txt(export_content)
            st.download_button(
                label="Download TXT",
                data=txt_content,
                file_name="legal_analysis.txt",
                mime="text/plain"
            ) 