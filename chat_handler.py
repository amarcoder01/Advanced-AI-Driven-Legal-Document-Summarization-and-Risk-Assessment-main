import streamlit as st
import google.generativeai as genai
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import os

class ChatHandler:
    """Enhanced chat handler for both document-specific and general conversations."""
    
    def __init__(self):
        """Initialize chat handler with necessary configurations."""
        self.setup_logging()
        self.initialize_model()
        self.initialize_session_state()
        
    def setup_logging(self):
        """Set up logging configuration."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
    def initialize_model(self):
        """Initialize the Gemini model."""
        try:
            # Try getting API key from environment variable first
            api_key = os.getenv('GOOGLE_API_KEY')
            
            # If not in environment, try Streamlit secrets
            if not api_key:
                try:
                    # Try the new location first
                    api_key = st.secrets["api"]["GEMINI_API_KEY"]
                except:
                    try:
                        # Try the old location as fallback
                        api_key = st.secrets["google"]["api_key"]
                    except:
                        pass
            
            # If still no API key, show error
            if not api_key:
                st.error("Google API key not found. Please set it in your environment variables as 'GOOGLE_API_KEY' or in Streamlit secrets.")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.chat = self.model.start_chat(history=[])
        except Exception as e:
            self.logger.error(f"Error initializing Gemini model: {str(e)}")
            st.error(f"Error initializing chat: {str(e)}")
            
    def initialize_session_state(self):
        """Initialize or reset session state for chat."""
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
    def clear_chat_history(self):
        """Clear the chat history."""
        st.session_state.chat_history = []
        self.chat = self.model.start_chat(history=[])
        
    def format_system_prompt(self) -> str:
        """Format the system prompt."""
        base_prompt = """You are an advanced AI assistant with the following capabilities:
        1. Problem-solving: Help users solve complex problems step by step
        2. Code assistance: Write, explain, and debug code in various programming languages
        3. Writing assistance: Help with writing, editing, and improving text
        4. Math and analysis: Handle mathematical calculations and data analysis
        5. Research and information: Provide detailed information on various topics
        6. Creative tasks: Help with creative writing, brainstorming, and ideation
        7. Learning assistance: Explain concepts and help with learning
        8. Task planning: Help break down and plan complex tasks
        9. General conversation: Engage in natural, helpful dialogue

        Guidelines:
        - Provide detailed, accurate responses
        - Break down complex problems into manageable steps
        - Use examples and analogies when helpful
        - Acknowledge limitations and uncertainties
        - Maintain a professional yet friendly tone
        - Ask clarifying questions when needed"""

        # Add document context if available
        if st.session_state.get("extracted_text"):
            return f"""{base_prompt}

            You have access to the following document content:
            {st.session_state.extracted_text[:2000]}...

            When asked about the document, analyze and respond based on this content.
            If the document content is too long, focus on the most relevant parts for the user's question.
            Always acknowledge that you're working with the document provided in the upload section."""

        return base_prompt
        
    def generate_response(self, user_input: str) -> str:
        """Generate a response to user input."""
        try:
            # Get current hour for time-aware greetings
            current_hour = datetime.now().hour
            
            # Enhanced greetings with variations
            greetings = {
                "hi", "hello", "hey", "greetings", "hi there", "hello there", "howdy",
                "good morning", "morning", "good afternoon", "afternoon", 
                "good evening", "evening", "good day", "hola", "sup"
            }
            farewells = {
                "bye", "goodbye", "see you", "see ya", "farewell", "cya",
                "good night", "have a good day", "take care"
            }
            thanks = {
                "thanks", "thank you", "thx", "thanks a lot", "thank you very much",
                "appreciate it", "thanks for your help"
            }
            
            user_input_lower = user_input.lower().strip()
            
            # Handle basic interactions with enhanced responses
            if user_input_lower in greetings:
                if current_hour < 12:
                    greeting = "Good morning"
                elif current_hour < 17:
                    greeting = "Good afternoon"
                else:
                    greeting = "Good evening"
                    
                if st.session_state.get("extracted_text"):
                    response_text = f"{greeting}! I see you've uploaded a document. I can help you analyze it, answer questions about it, or assist with any other tasks. What would you like to explore?"
                else:
                    response_text = f"{greeting}! I'm here to help you with any questions, problems, or tasks you have. I can assist with analysis, writing, coding, math, planning, or any other topics you'd like to discuss. What would you like to explore?"
                
                self._save_to_history(user_input, response_text)
                return response_text
            
            # Handle farewells with context
            if user_input_lower in farewells:
                if st.session_state.chat_history:
                    response_text = "Goodbye! I enjoyed our conversation and hope I was helpful. If you need any more assistance with your tasks or have other questions, feel free to come back. Have a great day!"
                else:
                    response_text = "Goodbye! If you need any help in the future with problem-solving or any other tasks, feel free to return. Have a great day!"
                self._save_to_history(user_input, response_text)
                return response_text
            
            # Handle thanks with context awareness
            if user_input_lower in thanks:
                if st.session_state.chat_history:
                    response_text = "You're welcome! I'm glad I could help. Is there anything else you'd like to explore or any other aspects you'd like me to explain further?"
                else:
                    response_text = "You're welcome! I'm here to help with any questions or tasks you have. Would you like to explore any specific topics?"
                self._save_to_history(user_input, response_text)
                return response_text
            
            # Handle empty or very short inputs
            if len(user_input.strip()) < 2:
                response_text = "I didn't catch that. Could you please provide more details about what you'd like to know or what problem you're trying to solve? I'm here to help with any questions or tasks you have."
                self._save_to_history(user_input, response_text)
                return response_text
            
            # Check if the query is about the document
            document_related_keywords = {"document", "text", "content", "file", "upload", "summary", "analyze", "key points", "main points"}
            is_document_query = any(keyword in user_input_lower for keyword in document_related_keywords)
            
            if is_document_query and not st.session_state.get("extracted_text"):
                response_text = "I notice you're asking about a document, but I don't see any document uploaded yet. Please upload a document in the Upload tab first, and then I'll be happy to help you analyze it."
                self._save_to_history(user_input, response_text)
                return response_text
            
            # Prepare the prompt with enhanced context
            system_prompt = self.format_system_prompt()
            recent_context = self._get_recent_chat_context()
            
            # Create a more engaging and context-aware prompt
            prompt = f"""{system_prompt}

Recent conversation context:
{recent_context}

Current request: {user_input}

Please provide a helpful, detailed response that:
1. Addresses the user's specific question or need
2. Provides relevant examples or explanations
3. Suggests next steps or follow-up questions if appropriate
4. Maintains a natural, engaging conversation flow

User: {user_input}"""
            
            # Generate response
            response = self.chat.send_message(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response received from the model")
            
            self._save_to_history(user_input, response.text)
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            error_message = "I apologize, but I encountered an error processing your request. Could you try rephrasing your question or breaking it down into smaller parts? I'm here to help and want to ensure I understand your needs correctly."
            self._save_to_history(user_input, error_message)
            return error_message
    
    def _save_to_history(self, user_input: str, response_text: str):
        """Helper method to save interactions to chat history."""
        # Save user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        # Save assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })
    
    def _get_recent_chat_context(self, max_messages: int = 4) -> str:
        """Get recent chat context for better conversation coherence."""
        if not st.session_state.chat_history:
            return ""
            
        # Get last few messages for context
        recent_messages = st.session_state.chat_history[-max_messages:] if len(st.session_state.chat_history) > max_messages else st.session_state.chat_history
        
        context = ""
        for message in recent_messages:
            context += f"{message['role'].title()}: {message['content']}\n"
        
        return context.strip()
            
    def chat_ui(self):
        """Display the chat interface."""
        st.markdown("### 💬 Interactive Chat Assistant")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Chat input
        if user_input := st.chat_input("Ask me anything..."):
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
                
            # Generate and display response
            with st.chat_message("assistant"):
                response = self.generate_response(user_input)
                st.markdown(response)
                
        # Clear chat button
        if st.button("Clear Chat History"):
            self.clear_chat_history()
            st.rerun()
            
    def save_chat_history(self, filepath: str):
        """Save chat history to a file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(st.session_state.chat_history, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving chat history: {str(e)}")
            return False
            
    def load_chat_history(self, filepath: str):
        """Load chat history from a file."""
        try:
            with open(filepath, 'r') as f:
                st.session_state.chat_history = json.load(f)
            return True
        except Exception as e:
            self.logger.error(f"Error loading chat history: {str(e)}")
            return False
            
    def get_chat_summary(self) -> str:
        """Generate a summary of the chat conversation."""
        if not st.session_state.chat_history:
            return "No chat history available."
            
        try:
            summary_prompt = "Summarize the key points of this conversation:\n"
            for message in st.session_state.chat_history:
                summary_prompt += f"\n{message['role'].title()}: {message['content']}"
                
            response = self.model.generate_content(summary_prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Error generating chat summary: {str(e)}")
            return "Unable to generate chat summary."
            
    def export_chat_history(self, format: str = "text") -> Optional[str]:
        """Export chat history in specified format."""
        try:
            if format == "text":
                output = "Chat History:\n\n"
                for message in st.session_state.chat_history:
                    output += f"{message['role'].title()}: {message['content']}\n\n"
                return output
            elif format == "json":
                return json.dumps(st.session_state.chat_history, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
        except Exception as e:
            self.logger.error(f"Error exporting chat history: {str(e)}")
            return None 
