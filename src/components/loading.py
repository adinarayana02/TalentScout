import streamlit as st

def loading_spinner():
    return st.markdown("""
        <div class="loading-spinner">
            <div class="spinner"></div>
            <style>
                .loading-spinner {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 50px;
                }
                .spinner {
                    width: 30px;
                    height: 30px;
                    border: 3px solid #f3f3f3;
                    border-top: 3px solid #1976d2;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </div>
    """, unsafe_allow_html=True) 