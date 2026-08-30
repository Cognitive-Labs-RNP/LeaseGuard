"""
CSS loader utility for LeaseGuard AI Streamlit interface.
Safely loads and injects custom styles into the Streamlit application.
"""
import os
import streamlit as st


def load_css(css_file_path: str = "assets/styles.css") -> bool:
    """
    Read and inject a CSS file into the current Streamlit app.
    
    Args:
        css_file_path: Relative or absolute path to the CSS file.
        
    Returns:
        bool: True if CSS was successfully loaded, False otherwise.
    """
    # Handle paths relative to project root or calling directory
    if not os.path.isabs(css_file_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        css_file_path = os.path.join(base_dir, css_file_path)

    try:
        if os.path.exists(css_file_path):
            with open(css_file_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
            return True
        else:
            # Fallback if CSS file is missing
            st.markdown(
                """
                <style>
                .block-container { padding-top: 2rem; }
                </style>
                """,
                unsafe_allow_html=True
            )
            return False
    except Exception as e:
        # Graceful fallback: never crash app on CSS load failure
        print(f"[Warning] Failed to load CSS: {e}")
        return False
