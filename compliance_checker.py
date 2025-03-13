import streamlit as st
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class ComplianceChecker:
    def __init__(self):
        """Initialize compliance checker with framework definitions."""
        self.framework_data = {
            "GDPR": {
                "keywords": {
                    "personal data": {
                        "suggestion": "Include explicit statements about how personal data is collected, processed, and stored."
                    },
                    "consent": {
                        "suggestion": "Add clear language about how user consent is obtained and how it can be withdrawn."
                    },
                    "data subject rights": {
                        "suggestion": "Detail the rights of data subjects including access, rectification, erasure, and portability."
                    },
                    "processing": {
                        "suggestion": "Specify the lawful basis for processing personal data."
                    },
                    "data protection": {
                        "suggestion": "Describe data protection measures implemented to safeguard personal information."
                    }
                }
            },
            "HIPAA": {
                "keywords": {
                    "health information": {
                        "suggestion": "Include specific protections for health information as required by HIPAA."
                    },
                    "phi": {
                        "suggestion": "Add provisions for protecting Personal Health Information (PHI)."
                    },
                    "patient privacy": {
                        "suggestion": "Detail measures to ensure patient privacy is maintained."
                    },
                    "security measures": {
                        "suggestion": "Describe technical safeguards implemented to protect health data."
                    },
                    "authorization": {
                        "suggestion": "Include procedures for obtaining proper authorization for disclosure of health information."
                    }
                }
            },
            "ISO 27001": {
                "keywords": {
                    "information security": {
                        "suggestion": "Include a comprehensive information security management policy."
                    },
                    "risk assessment": {
                        "suggestion": "Add details about your risk assessment and management procedures."
                    },
                    "security controls": {
                        "suggestion": "Specify the security controls implemented to protect information assets."
                    },
                    "asset management": {
                        "suggestion": "Include provisions for inventorying and managing information assets."
                    },
                    "incident response": {
                        "suggestion": "Detail your security incident response procedures."
                    }
                }
            }
        }

    def check_compliance(self, text: str, frameworks: List[str]) -> Dict[str, Any]:
        """Check document compliance against specified frameworks."""
        if not text or len(text) < 10:
            return self._generate_empty_result(frameworks)

        # Limit text length to prevent performance issues
        max_text_length = 20000
        text = text[:max_text_length]
        paragraphs = text.split('\n\n')
        
        results = {}
        for framework in frameworks:
            if framework not in self.framework_data:
                continue
                
            results[framework] = self._analyze_framework(framework, text, paragraphs)
            
        return results

    def _analyze_framework(self, framework: str, text: str, paragraphs: List[str]) -> Dict[str, Any]:
        """Analyze text against a specific compliance framework."""
        keywords = self.framework_data[framework]["keywords"]
        found_items = []
        missing_items = []
        
        for keyword, data in keywords.items():
            if keyword.lower() in text.lower():
                locations = []
                for i, para in enumerate(paragraphs):
                    if keyword.lower() in para.lower():
                        locations.append(f"Paragraph {i+1}")
                        if len(locations) >= 3:  # Limit to 3 locations
                            break
                
                found_items.append({
                    "keyword": keyword,
                    "locations": locations
                })
            else:
                missing_items.append({
                    "keyword": keyword,
                    "suggestion": data["suggestion"]
                })
        
        total = len(keywords)
        score = len(found_items)
        percentage = int((score / total) * 100) if total > 0 else 0
        
        status = "COMPLIANT" if percentage >= 80 else "PARTIALLY COMPLIANT" if percentage >= 50 else "NON-COMPLIANT"
        color = "green" if percentage >= 80 else "orange" if percentage >= 50 else "red"
        
        return {
            "found": found_items,
            "missing": missing_items,
            "score": percentage,
            "status": status,
            "color": color
        }

    def _generate_empty_result(self, frameworks: List[str]) -> Dict[str, Any]:
        """Generate an empty result when no text is provided."""
        return {
            "timestamp": datetime.now().isoformat(),
            "analyzed_frameworks": frameworks,
            "total_issues": 0,
            "issues": [],
            "risk_assessment": {
                "level": "LOW",
                "breakdown": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "explanation": "Document too short for meaningful analysis."
            },
            "summary": "Document is too short to perform compliance analysis."
        }

    def compliance_check_ui(self) -> None:
        """Handle compliance checking UI and functionality."""
        st.title("Compliance Analysis")
        st.write("### Regulatory Compliance Check")
        
        if not st.session_state.get("extracted_text"):
            st.info("Please upload a document in the Document Upload tab first.")
            if st.button("Go to Upload Tab"):
                st.experimental_set_query_params(tab="upload")
                st.rerun()
            return
        
        frameworks = st.multiselect(
            "Select compliance frameworks to check against:",
            ["GDPR", "HIPAA", "ISO 27001"],
            default=["GDPR"]
        )
        
        if st.button("Run Compliance Scan"):
            try:
                with st.spinner("Checking document compliance..."):
                    results = self.check_compliance(st.session_state.extracted_text, frameworks)
                
                st.success("Compliance check complete!")
                
                for framework, data in results.items():
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; padding:15px; border-radius:5px; margin-bottom:20px">
                        <h3 style="margin-top:0">{framework} Framework</h3>
                        <div style="background-color:{data['color']}; color:white; padding:8px; border-radius:4px; display:inline-block">
                            {data['status']} - {data['score']}% Compliant
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("View Compliance Details", expanded=True):
                        if data["found"]:
                            st.subheader("✅ Compliance Requirements Met")
                            for item in data["found"]:
                                st.markdown(f"**{item['keyword']}**")
                                st.markdown(f"*Found in: {', '.join(item['locations'])}*")
                                st.markdown("---")
                        else:
                            st.warning("No compliance requirements were met.")
                        
                        if data["missing"]:
                            st.subheader("❌ Compliance Gaps Identified")
                            for item in data["missing"]:
                                st.markdown(f"**Missing: {item['keyword']}**")
                                st.markdown(f"*Suggestion: {item['suggestion']}*")
                                st.markdown("---")
                
                # Generate downloadable report
                report = {
                    "timestamp": datetime.now().isoformat(),
                    "frameworks_analyzed": frameworks,
                    "results": {k: {
                        "status": v["status"],
                        "score": v["score"],
                        "compliant_items": [i["keyword"] for i in v["found"]],
                        "non_compliant_items": [{
                            "keyword": i["keyword"],
                            "suggestion": i["suggestion"]
                        } for i in v["missing"]]
                    } for k, v in results.items()}
                }
                
                st.download_button(
                    "📥 Download Compliance Report",
                    data=json.dumps(report, indent=2),
                    file_name="compliance_report.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("If you're experiencing issues, try with a smaller document.") 