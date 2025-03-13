import streamlit as st
import logging
from google.generativeai import GenerativeModel
from typing import Optional, Tuple, Dict, List

class RiskAnalyzer:
    def __init__(self):
        """Initialize the risk analyzer with Gemini model."""
        try:
            self.model = GenerativeModel("gemini-1.5-flash-latest")
        except Exception as e:
            logging.error(f"Error initializing Gemini model: {str(e)}")
            self.model = None

    def identify_risks(self, text: str) -> Optional[str]:
        """Identify risks in the document using Gemini API."""
        if not text or not self.model:
            return None

        try:
            prompt = (
                "Analyze the following legal document and identify potential risks. "
                "Categorize risks by severity (High, Medium, Low) and provide clear explanations. "
                "Focus on legal, compliance, and business risks.\n\n"
                f"Document text:\n{text}"
            )
            response = self.model.generate_content(prompt)
            return response.text.strip() if response and hasattr(response, "text") else None
        except Exception as e:
            logging.error(f"Risk analysis error: {str(e)}")
            return None

    def calculate_risk_score(self, risks_text: str) -> Tuple[int, int, int, int]:
        """Calculate a risk score based on identified risks."""
        if not risks_text or not isinstance(risks_text, str):
            return 0, 0, 0, 0
        
        text_lower = risks_text.lower()
        max_text_length = min(len(text_lower), 10000)
        text_sample = text_lower[:max_text_length]
        
        high_count = sum(text_sample.count(word) for word in ['critical', 'severe', 'high risk', 'significant', 'major', 'serious'])
        medium_count = sum(text_sample.count(word) for word in ['moderate', 'medium', 'potential', 'possible', 'concerning'])
        low_count = len(text_sample.split('.')) - high_count - medium_count
        low_count = max(0, low_count)
        
        total = high_count + medium_count + low_count
        if total == 0:
            return 0, 0, 0, 0
        
        score = min(100, round((high_count * 3 + medium_count * 2 + low_count) / max(total, 1) * 20))
        return score, high_count, medium_count, low_count

    def display_risk_score(self, risks_text: str) -> None:
        """Display risk score analysis in the UI."""
        if not risks_text:
            st.info("No risk data available for scoring.")
            return
        
        try:
            score, high_count, medium_count, low_count = self.calculate_risk_score(risks_text)
            
            st.subheader("Risk Score Analysis")
            st.write(f"Overall Risk Score: {score}/100")
            
            if score >= 70:
                st.error("🔴 High Risk Level")
            elif score >= 40:
                st.warning("🟠 Medium Risk Level")
            else:
                st.success("🟢 Low Risk Level")
            
            st.write("Risk Breakdown:")
            st.write(f"- High Priority Risks: {high_count}")
            st.write(f"- Medium Priority Risks: {medium_count}")
            st.write(f"- Low Priority Risks: {low_count}")
        
        except Exception as e:
            st.error(f"Error calculating risk score: {str(e)}")
            st.info("Please try again with a different document.")

    def display_risks_with_filters(self, risks_text: str) -> None:
        """Display filtered risks in the UI."""
        if not risks_text:
            st.warning("No risks identified.")
            return
        
        sentences = [s.strip() for s in risks_text.split('.') if s.strip()]
        if not sentences:
            st.warning("No clear risk statements identified.")
            return
            
        st.write(f"Total Potential Risks Found: {len(sentences)}")
        
        priority_filter = st.multiselect(
            "Filter by Priority",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )
        
        high_risk_keywords = ['critical', 'severe', 'high risk', 'significant', 'major', 'serious']
        medium_risk_keywords = ['moderate', 'medium', 'potential', 'possible', 'concerning']
        
        risks_by_priority = {
            "High": [],
            "Medium": [],
            "Low": []
        }
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in high_risk_keywords):
                risks_by_priority["High"].append(sentence)
            elif any(keyword in sentence_lower for keyword in medium_risk_keywords):
                risks_by_priority["Medium"].append(sentence)
            elif len(sentence.split()) > 5:
                risks_by_priority["Low"].append(sentence)
        
        for priority in priority_filter:
            if priority == "High" and risks_by_priority["High"]:
                st.markdown("#### 🔴 High Priority Risks")
                for idx, risk in enumerate(risks_by_priority["High"], 1):
                    st.error(f"{idx}. {risk}")
            
            if priority == "Medium" and risks_by_priority["Medium"]:
                st.markdown("#### 🟠 Medium Priority Risks")
                for idx, risk in enumerate(risks_by_priority["Medium"], 1):
                    st.warning(f"{idx}. {risk}")
            
            if priority == "Low" and risks_by_priority["Low"]:
                st.markdown("#### 🟢 Low Priority Risks")
                for idx, risk in enumerate(risks_by_priority["Low"], 1):
                    st.info(f"{idx}. {risk}")

    def display_risk_visualizer(self, risks_text: str) -> None:
        """Display a visualization of the risks."""
        if not risks_text:
            st.info("No risk data available to visualize.")
            return
        
        try:
            # Calculate risk scores
            score, high_count, medium_count, low_count = self.calculate_risk_score(risks_text)
            
            st.subheader("Risk Visualization")
            
            # Overall risk level
            st.write("Overall Risk Level:")
            if score >= 70:
                color = "red"
                level = "High Risk 🔴"
            elif score >= 40:
                color = "orange"
                level = "Medium Risk 🟠"
            else:
                color = "green"
                level = "Low Risk 🟢"
                
            st.markdown(f"### {level}")
            st.progress(min(score/100, 1.0))
            
            # Risk distribution
            st.write("Risk Distribution:")
            
            total = high_count + medium_count + low_count
            if total > 0:
                # Calculate percentages
                high_pct = int((high_count / total) * 100)
                medium_pct = int((medium_count / total) * 100)
                low_pct = 100 - high_pct - medium_pct
                
                # Display risk distribution bars
                st.markdown("**High Priority** 🔴")
                st.progress(high_count / max(total, 1))
                st.markdown(f"{high_count} issues ({high_pct}%)")
                
                st.markdown("**Medium Priority** 🟠")
                st.progress(medium_count / max(total, 1))
                st.markdown(f"{medium_count} issues ({medium_pct}%)")
                
                st.markdown("**Low Priority** 🟢")
                st.progress(low_count / max(total, 1))
                st.markdown(f"{low_count} issues ({low_pct}%)")
                
                # Key risk indicators
                st.subheader("Key Risk Indicators")
                
                # Find most common risk keywords
                risk_keywords = [
                    ("non-compliance", "regulatory requirements"),
                    ("liability", "legal exposure"),
                    ("breach", "contract terms"),
                    ("confidentiality", "disclosure"),
                    ("warranty", "guarantees"),
                    ("termination", "cancellation"),
                    ("intellectual property", "IP rights"),
                    ("dispute", "resolution"),
                    ("payment", "financial terms")
                ]
                
                # Count keyword occurrences
                keyword_counts = []
                for kw_pair in risk_keywords:
                    count = sum(risks_text.lower().count(kw) for kw in kw_pair)
                    if count > 0:
                        keyword_counts.append((f"{kw_pair[0]}/{kw_pair[1]}", count))
                
                # Display top 5 risk areas
                if keyword_counts:
                    keyword_counts.sort(key=lambda x: x[1], reverse=True)
                    for kw, count in keyword_counts[:5]:
                        st.write(f"• {kw}: {count} mentions")
                else:
                    st.info("No specific risk areas identified.")
                    
        except Exception as e:
            st.error(f"Error generating visualization: {str(e)}")
            st.info("Please try again with a different document.")

    def risk_assessment_ui(self) -> None:
        """Handle risk assessment UI and functionality."""
        st.subheader("Risk Assessment")
        
        if not st.session_state.get("extracted_text"):
            st.info("Please upload a document in the Upload tab first.")
            return
            
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Analyze Risks", key="analyze_risks_button", use_container_width=True):
                try:
                    with st.spinner("Analyzing document for potential risks..."):
                        risks = self.identify_risks(st.session_state.extracted_text)
                        st.session_state.risks = risks
                        st.success("✅ Analysis complete")
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
        
        with col2:
            if st.button("📊 View Score", key="view_score_button", use_container_width=True):
                if st.session_state.get("risks"):
                    self.display_risk_score(st.session_state.risks)
                else:
                    st.info("Please analyze the document first.")
        
        with col3:
            if st.button("📈 Visualize", key="visualize_risks_button", use_container_width=True):
                if st.session_state.get("risks"):
                    self.display_risk_visualizer(st.session_state.risks)
                else:
                    st.info("Please analyze the document first.")
        
        with col4:
            if st.button("📝 Summary", key="risk_summary_button", use_container_width=True):
                if st.session_state.get("risks"):
                    st.subheader("Risk Summary")
                    st.write(st.session_state.risks[:500] + "...")
                    st.info("View the Detailed Analysis tab for complete information")
                else:
                    st.info("Please analyze the document first.")
        
        if st.session_state.get("risks"):
            st.markdown("---")
            risk_tab1, risk_tab2 = st.tabs(["📋 Detailed Analysis", "📄 Full Risk Text"])
            
            with risk_tab1:
                self.display_risks_with_filters(st.session_state.risks)
            
            with risk_tab2:
                st.markdown("### Complete Risk Analysis")
                st.write(st.session_state.risks) 