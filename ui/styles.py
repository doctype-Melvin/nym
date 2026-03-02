import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        mark { border-radius: 4px; padding: 2px 4px; cursor: pointer; transition: all 0.2s; }
        .pii-default { background-color: #ffd700; color: black; }
        .pii-excluded { background-color: #e0e0e0; color: #9e9e9e; text-decoration: line-through; }
        .gen-flagged { background-color: #ffcccb; border: 1px solid red; }
        .gen-resolved { background-color: #90ee90; }
        small { font-size: 0.7em; opacity: 0.8; margin-left: 4px; }
        </style>
    """, unsafe_allow_value=True)