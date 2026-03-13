import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* ── Hide Streamlit deploy button and menu ────────────────────────── */
        #MainMenu { visibility: hidden; }
        [data-testid="stToolbar"] { display: none; }
        [data-testid="stDecoration"] { display: none; }
        [data-testid="stStatusWidget"] { display: none; }
        footer { visibility: hidden; }
        
        /* ── Force dark theme base ────────────────────────────────────────── */
        [data-testid="stAppViewContainer"] {
            background-color: #0e1117;
            color: #fafafa;
        }
        [data-testid="stSidebar"] {
            background-color: #1a1d23;
        }
                
        /* ── Primary button color override ───────────────────────────────── */
        button[kind="primary"] {
            background-color: #1a4a2e !important;
            color: #56d364 !important;
            border: 1px solid #2ea043 !important;
        }
        button[kind="primary"]:hover {
            background-color: #1f5c38 !important;
            box-shadow: 0 0 10px rgba(46, 160, 67, 0.4) !important;
            transition: all 0.3s ease !important;
        }
                
        /* ── Warning/orange button — use key prefix "warn_" ──────────────── */
        [data-testid="stButton"] button[kind="secondary"].warn,
        div:has(> [data-testid="stButton"] > button[key*="warn_"]) button {
            background-color: rgba(251, 146, 60, 0.12) !important;
            color: #fb923c !important;
            border: 1px solid #ea580c !important;
        }
        div:has(> [data-testid="stButton"] > button[key*="warn_"]) button:hover {
            background-color: rgba(251, 146, 60, 0.25) !important;
            box-shadow: 0 0 10px rgba(251, 146, 60, 0.4) !important;
            transition: all 0.3s ease !important;
        }

        /* ── Dropdown cursor fix ──────────────────────────────────────────── */
        [data-testid="stSelectbox"] div[data-baseweb="select"] {
            cursor: pointer !important;
        }
        [data-testid="stSelectbox"] div[data-baseweb="select"] * {
            cursor: pointer !important;
        }
                
        /* ── Sidebar navigation buttons ──────────────────────────────────── */
        [data-testid="stSidebar"] .stButton button {
            background-color: transparent;
            color: #a0a0a0;
            border: none;
            text-align: left;
            font-size: 0.85rem;
            padding: 6px 12px;
            border-radius: 6px;
            width: 100%;
        }    
                
        [data-testid="stSidebar"] .stButton button:hover {
            background-color: #2a2d35;
            color: #ffffff;
        }

        /* ── Active sidebar button — set via data attribute ──────────────── */
        [data-testid="stSidebar"] .stButton button[data-active="true"] {
            background-color: #2a2d35;
            color: #ffffff;
            border-left: 3px solid #4a9eff;
        }

        /* ── PII highlight classes ────────────────────────────────────────── */
       small { font-size: 0.7em; opacity: 0.7; margin-left: 4px; }

        /* ── Reduce header sizes ──────────────────────────────────────────── */
        h1 { font-size: 1.4rem !important; font-weight: 600 !important; }
        h2 { font-size: 1.2rem !important; font-weight: 500 !important; }
        h3 { font-size: 1.0rem !important; font-weight: 500 !important; }

        /* ── Metric labels ────────────────────────────────────────────────── */
        [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
        [data-testid="stMetricValue"] { font-size: 1.1rem !important; }

        /* ── Reduce expander padding ──────────────────────────────────────── */
        [data-testid="stExpander"] { border: 1px solid #2a2d35 !important; }

        /* ── Caption text ─────────────────────────────────────────────────── */
        .stCaption { font-size: 0.75rem !important; color: #888 !important; }

        /* ── Version tag ──────────────────────────────────────────────────── */
        .version-tag {
            font-size: 0.7rem;
            color: #555;
            text-align: center;
            padding-top: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

def inject_active_nav(app_mode):
    nav_map = {"Dashboard": 4, "Review": 5, "Archive": 6}
    idx = nav_map.get(app_mode, 4)
    st.markdown(f"""
        <style>
        /* ── Sidebar layout ───────────────────────────────────────────────── */
        section[data-testid="stSidebar"] {{
            min-width: 200px !important;
            max-width: 240px !important;
        }}
        section[data-testid="stSidebar"] > div:first-child {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding-bottom: 0;
        }}
        /* ── Active nav button ────────────────────────────────────────────── */
        section[data-testid="stSidebar"] > div > div > div > div > div:nth-child({idx}) button {{
            background-color: #2a2d35 !important;
            color: #ffffff !important;
            border-left: 3px solid #4a9eff !important;
        }}
       
        </style>
    """, unsafe_allow_html=True)

def orange_button(label, key, use_container_width=False, disabled=False):
    st.markdown(f"""
        <style>
        div[data-testid="stButton"]:has(button#btn_{key}) button {{
            background-color: rgba(251, 146, 60, 0.12) !important;
            color: #fb923c !important;
            border: 1px solid #ea580c !important;
            transition: all 0.3s ease !important;
        }}
        div[data-testid="stButton"]:has(button#btn_{key}) button:hover {{
            background-color: rgba(251, 146, 60, 0.25) !important;
            box-shadow: 0 0 10px rgba(251, 146, 60, 0.4) !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    return st.button(label, key=key, use_container_width=use_container_width, disabled=disabled)