import streamlit as st
import logging
from typing import Dict, Any, Optional
from utils_file_processor import extract_text_from_uploaded_file

class DocumentComparer:
    def __init__(self):
        """Initialize document comparer."""
        pass

    def compare_documents(self, doc_texts: Dict[str, str], doc_names: Dict[str, str], comparison_type: str) -> Dict[str, Any]:
        """Compare two documents and return analysis results."""
        try:
            # Basic validation
            if not all(doc_texts.values()) or len(doc_texts) != 2:
                return {"error": "Invalid document texts provided for comparison"}

            # Prepare documents for comparison
            doc1_text = doc_texts['main_doc']
            doc2_text = doc_texts['second_doc']
            doc1_name = doc_names['main_doc']
            doc2_name = doc_names['second_doc']

            # Calculate basic similarity
            similarity = self._calculate_similarity(doc1_text, doc2_text)

            # Analyze based on comparison type
            analysis = self._analyze_documents(doc1_text, doc2_text, comparison_type)
            key_differences = self._find_key_differences(doc1_text, doc2_text, comparison_type)
            common_elements = self._find_common_elements(doc1_text, doc2_text, comparison_type)

            return {
                "similarity": similarity,
                "analysis": analysis,
                "key_differences": key_differences,
                "common_elements": common_elements
            }

        except Exception as e:
            logging.error(f"Error in document comparison: {str(e)}")
            return {"error": f"Error comparing documents: {str(e)}"}

    def _calculate_similarity(self, text1: str, text2: str) -> int:
        """Calculate a simple similarity score between two texts."""
        # Simple implementation - can be enhanced with more sophisticated algorithms
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return int((len(intersection) / len(union)) * 100)

    def _analyze_documents(self, text1: str, text2: str, comparison_type: str) -> str:
        """Generate analysis based on comparison type."""
        if comparison_type == "Legal Clauses":
            return self._analyze_legal_clauses(text1, text2)
        elif comparison_type == "Compliance Elements":
            return self._analyze_compliance(text1, text2)
        elif comparison_type == "Risk Factors":
            return self._analyze_risks(text1, text2)
        else:
            return self._analyze_general(text1, text2)

    def _find_key_differences(self, text1: str, text2: str, comparison_type: str) -> Dict[str, list]:
        """Find key differences between documents based on comparison type."""
        differences = {}
        
        if comparison_type == "Legal Clauses":
            differences["Legal Terms"] = self._compare_legal_terms(text1, text2)
        elif comparison_type == "Compliance Elements":
            differences["Compliance Requirements"] = self._compare_compliance(text1, text2)
        elif comparison_type == "Risk Factors":
            differences["Risk Elements"] = self._compare_risks(text1, text2)
        else:
            differences["General Differences"] = self._compare_general(text1, text2)
            
        return differences

    def _find_common_elements(self, text1: str, text2: str, comparison_type: str) -> Dict[str, list]:
        """Find common elements between documents based on comparison type."""
        common = {}
        
        if comparison_type == "Legal Clauses":
            common["Shared Legal Terms"] = self._find_shared_legal_terms(text1, text2)
        elif comparison_type == "Compliance Elements":
            common["Shared Compliance Elements"] = self._find_shared_compliance(text1, text2)
        elif comparison_type == "Risk Factors":
            common["Shared Risk Factors"] = self._find_shared_risks(text1, text2)
        else:
            common["Shared Elements"] = self._find_shared_general(text1, text2)
            
        return common

    def _analyze_legal_clauses(self, text1: str, text2: str) -> str:
        """Analyze legal clauses in both documents."""
        # Implement legal clause analysis logic
        return "Legal clause analysis would go here"

    def _analyze_compliance(self, text1: str, text2: str) -> str:
        """Analyze compliance elements in both documents."""
        # Implement compliance analysis logic
        return "Compliance analysis would go here"

    def _analyze_risks(self, text1: str, text2: str) -> str:
        """Analyze risk factors in both documents."""
        # Implement risk analysis logic
        return "Risk analysis would go here"

    def _analyze_general(self, text1: str, text2: str) -> str:
        """Perform general analysis of both documents."""
        # Implement general analysis logic
        return "General analysis would go here"

    def compare_documents_ui(self) -> None:
        """Handle document comparison UI and functionality."""
        st.subheader("Compare Documents")
        
        if 'uploaded_docs' not in st.session_state or not st.session_state.uploaded_docs:
            st.warning("Please upload at least one document in the Upload tab first.")
            return
        
        # Get the main document
        if 'main_doc_id' in st.session_state and st.session_state.main_doc_id in st.session_state.uploaded_docs:
            main_doc_id = st.session_state.main_doc_id
        else:
            main_doc_id = list(st.session_state.uploaded_docs.keys())[0]
        
        st.info(f"**First Document:** {st.session_state.uploaded_docs[main_doc_id]['name']} (from Upload tab)")
        
        # Option for selecting second document
        st.subheader("Select Second Document")
        compare_option = st.radio(
            "Choose second document source:",
            ["Upload a new document", "Use an existing uploaded document"]
        )
        
        doc2 = None
        doc2_text = None
        doc2_name = None
        
        if compare_option == "Upload a new document":
            uploaded_comparison_file = st.file_uploader(
                "Upload a document to compare with the main document", 
                type=["pdf", "txt"],
                key="comparison_uploader"
            )
            
            if uploaded_comparison_file:
                doc2_text = extract_text_from_uploaded_file(uploaded_comparison_file)
                doc2_name = uploaded_comparison_file.name
                st.success(f"Uploaded: {doc2_name}")
                
        else:  # Use existing document
            remaining_docs = [doc for doc in st.session_state.uploaded_docs.keys() if doc != main_doc_id]
            
            if remaining_docs:
                doc2 = st.selectbox(
                    "Select document to compare", 
                    options=remaining_docs,
                    format_func=lambda x: st.session_state.uploaded_docs[x]['name']
                )
                
                if doc2:
                    doc2_text = st.session_state.uploaded_docs[doc2]['text']
                    doc2_name = st.session_state.uploaded_docs[doc2]['name']
            else:
                st.warning("No other documents available. Please upload another document or use the direct upload option.")
        
        comparison_type = st.selectbox(
            "Comparison Focus",
            options=["General Comparison", "Legal Clauses", "Compliance Elements", "Risk Factors"],
            help="Select what aspect of the documents you want to focus on comparing"
        )
        
        st.info("The comparison will automatically include the document summary to highlight key differences.")
        
        compare_button_enabled = bool(doc2_text or doc2)
        
        if st.button("Compare Documents", disabled=not compare_button_enabled):
            if not doc2_text and not doc2:
                st.error("Please select or upload a second document to compare.")
                return
                
            with st.spinner("Comparing documents..."):
                main_doc_text = st.session_state.uploaded_docs[main_doc_id]['text']
                main_doc_summary = st.session_state.summaries.get(main_doc_id, "")
                enhanced_main_doc_text = f"DOCUMENT SUMMARY:\n{main_doc_summary}\n\nFULL TEXT:\n{main_doc_text}"
                
                doc_texts = {
                    'main_doc': enhanced_main_doc_text,
                    'second_doc': doc2_text
                }
                
                doc_names = {
                    'main_doc': st.session_state.uploaded_docs[main_doc_id]['name'],
                    'second_doc': doc2_name
                }
                
                results = self.compare_documents(doc_texts, doc_names, comparison_type)
                
                if "error" in results:
                    st.error(results["error"])
                else:
                    st.subheader("Comparison Results")
                    
                    if "similarity" in results:
                        st.metric("Document Similarity", f"{results['similarity']}%")
                    
                    st.markdown("### Analysis")
                    st.write(results["analysis"])
                    
                    with st.expander("Key Differences", expanded=True):
                        if results["key_differences"]:
                            for category, differences in results["key_differences"].items():
                                st.markdown(f"#### {category}")
                                
                                for diff in differences:
                                    if isinstance(diff, dict) and "doc1" in diff and "doc2" in diff:
                                        cols = st.columns(2)
                                        cols[0].markdown(f"**{doc_names['main_doc']}**")
                                        cols[0].write(diff["doc1"])
                                        
                                        cols[1].markdown(f"**{doc_names['second_doc']}**")
                                        cols[1].write(diff["doc2"])
                                        
                                        st.markdown("---")
                                    else:
                                        st.write(diff.get("content", ""))
                        else:
                            st.write("No significant differences identified.")
                    
                    with st.expander("Common Elements", expanded=True):
                        if results["common_elements"]:
                            for category, elements in results["common_elements"].items():
                                st.markdown(f"#### {category}")
                                
                                for element in elements:
                                    st.markdown(f"**{element.get('title', 'Element')}**")
                                    st.write(element.get("content", ""))
                                    st.markdown("---")
                        else:
                            st.write("No common elements identified.") 