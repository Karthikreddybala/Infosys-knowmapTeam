import streamlit as st
import base64
import os

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def add_background():
    """
    Injects custom CSS tuned for the dark navy/purple AI-cybersecurity background (img2.jpg).
    Falls back to a matching dark-navy gradient if the file is missing.
    Call this immediately after st.set_page_config() on every page.
    """
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img2.jpg")

    if os.path.exists(img_path):
        bg_bin = get_base64_of_bin_file(img_path)
        bg_css = f"background-image: url('data:image/jpg;base64,{bg_bin}');"
    else:
        bg_css = "background: linear-gradient(135deg, #050918 0%, #0d0825 60%, #1a0535 100%);"

    st.markdown(f"""
    <style>
        /* ── App background ──────────────────────────────────────────── */
        .stApp {{
            {bg_css}
            background-size: cover;
            background-position: center top;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}

        /* ── Main content card — white glass ─────────────────────────── */
        .main .block-container {{
            background: rgba(255, 255, 255, 0.30);
            border-radius: 14px;
            padding: 2rem 2.5rem;
            margin-top: 1rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 2px solid rgba(255, 255, 255, 0.85);
        }}

        /* ── All inner containers — st.container, st.form, columns ──── */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stForm"],
        div[data-testid="stContainer"] {{
            background: rgba(255, 255, 255, 0.18) !important;
            border-radius: 12px !important;
            border: 2px solid rgba(255, 255, 255, 0.75) !important;
            padding: 1rem 1.2rem !important;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }}

        /* ── Form container specifically ─────────────────────────────── */
        [data-testid="stForm"] {{
            background: rgba(255, 255, 255, 0.22) !important;
            border: 2px solid rgba(255, 255, 255, 0.80) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }}

        /* ── Column wrappers ─────────────────────────────────────────── */
        [data-testid="column"] {{
            background: rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.55) !important;
            padding: 0.8rem !important;
            backdrop-filter: blur(6px);
        }}

        /* ── Sidebar ─────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {{
            background: rgba(255, 255, 255, 0.20) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-right: 2px solid rgba(255, 255, 255, 0.8);
        }}
        [data-testid="stSidebar"] * {{
            color: #ffffff !important;
        }}

        /* ── Typography ──────────────────────────────────────────────── */
        h1 {{
            color: #ffffff;
            font-weight: 700;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }}
        h2, h3 {{ color: #e8f0ff; text-shadow: 0 1px 6px rgba(0,0,0,0.4); }}
        h4, h5, h6 {{ color: #d0dcf5; }}
        p, li, span, label {{ color: #e8edf8; }}

        /* ── Tabs ────────────────────────────────────────────────────── */
        [data-testid="stTabs"] [role="tablist"] {{
            background: rgba(255, 255, 255, 0.22);
            border-radius: 10px;
            padding: 3px;
            border: 2px solid rgba(255, 255, 255, 0.8);
        }}
        [data-testid="stTabs"] [role="tab"] {{
            border-radius: 8px;
            font-weight: 600;
            color: #ffffff;
            transition: all 0.2s ease;
        }}
        [data-testid="stTabs"] [aria-selected="true"] {{
            background: rgba(255, 255, 255, 0.40) !important;
            color: #000000 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }}

        /* ── Buttons ─────────────────────────────────────────────────── */
        .stButton > button {{
            background: rgba(255, 255, 255, 0.25) !important;
            border: 2px solid rgba(255, 255, 255, 0.85) !important;
            color: #ffffff !important;
            border-radius: 9px !important;
            font-weight: 600 !important;
            backdrop-filter: blur(4px);
            transition: all 0.25s ease !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.5);
        }}
        .stButton > button:hover {{
            background: rgba(255, 255, 255, 0.40) !important;
            border-color: #ffffff !important;
            box-shadow: 0 4px 18px rgba(255, 255, 255, 0.3),
                        0 4px 12px rgba(0,0,0,0.3) !important;
            transform: translateY(-1px);
        }}

        /* ── Text inputs & selects ───────────────────────────────────── */
        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stTextArea"] textarea {{
            background: rgba(255, 255, 255, 0.25) !important;
            border: 2px solid rgba(255, 255, 255, 0.85) !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            box-shadow: inset 0 1px 4px rgba(0,0,0,0.15);
            transition: border 0.2s ease, box-shadow 0.2s ease;
        }}
        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus {{
            border-color: #ffffff !important;
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.25) !important;
        }}
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {{
            color: rgba(255, 255, 255, 0.6) !important;
        }}

        /* ── Metric cards ────────────────────────────────────────────── */
        [data-testid="metric-container"] {{
            background: rgba(255, 255, 255, 0.85);
            border-radius: 12px;
            padding: 1rem 1.3rem;
            border: 2px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255,255,255,0.4);
            backdrop-filter: blur(8px);
        }}
        [data-testid="stMetricValue"] {{
            color: #ffffff !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            text-shadow: 0 2px 8px rgba(0,0,0,0.5);
        }}
        [data-testid="stMetricLabel"] {{ color: rgba(255,255,255,0.9) !important; }}

        /* ── Expanders ───────────────────────────────────────────────── */
        .streamlit-expanderHeader {{
            background: rgba(255, 255, 255, 0.85) !important;
            border-radius: 8px !important;
            border: 2px solid rgba(255, 255, 255, 0.8) !important;
            font-weight: 600;
            color: #ffffff !important;
        }}
        .streamlit-expanderContent {{
            background: rgba(255, 255, 255, 0.15) !important;
            border-radius: 0 0 8px 8px !important;
            border: 2px solid rgba(255, 255, 255, 0.6) !important;
            border-top: none !important;
        }}

        /* ── Alerts ──────────────────────────────────────────────────── */
        [data-testid="stAlert"] {{
            border-radius: 10px !important;
            backdrop-filter: blur(6px);
            background: rgba(255, 255, 255, 0.22) !important;
            border: 2px solid rgba(255, 255, 255, 0.75) !important;
        }}

        /* ── Dividers ────────────────────────────────────────────────── */
        hr {{ border-color: rgba(255, 255, 255, 0.7) !important; }}

        /* ── Slider ──────────────────────────────────────────────────── */
        [data-testid="stSlider"] [role="slider"] {{
            background: #ffffff !important;
            box-shadow: 0 0 8px rgba(255,255,255,0.5);
        }}

        /* ── Progress bar ────────────────────────────────────────────── */
        [data-testid="stProgressBar"] > div > div {{
            background: linear-gradient(90deg, rgba(255,255,255,0.5), #ffffff) !important;
        }}

        /* ── Scrollbar ───────────────────────────────────────────────── */
        ::-webkit-scrollbar {{ width: 5px; }}
        ::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.05); }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.25);
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.45);
        }}
    </style>
    """, unsafe_allow_html=True)


def feedback_form(user_id, target_type, reference_id=None, container=None):
    """
    Renders a reusable feedback form for the website or a specific graph.
    """
    target = container if container else st
    
    with target.form(key=f"feedback_form_{target_type}_{reference_id}"):
        st.markdown(f"#### Leave {target_type.capitalize()} Feedback")
        rating = st.slider("Rating (1-5 Stars)", min_value=1, max_value=5, value=5)
        comments = st.text_area("Additional Comments")
        submit_btn = st.form_submit_button("Submit Feedback")
        
        if submit_btn:
            from db.connection import run_insert
            sql = "INSERT INTO feedback (user_id, feedback_type, reference_id, rating, comments) VALUES (%s, %s, %s, %s, %s)"
            try:
                run_insert(sql, (user_id, target_type, reference_id, rating, comments))
                st.success("Thank you for your feedback!")
            except Exception as e:
                st.error(f"Failed to submit feedback: {e}")
