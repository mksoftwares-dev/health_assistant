
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import sqlite3
import base64
import os
from datetime import datetime
from auth import (
    init_users_db, register_user, login_user,
    update_profile, is_logged_in, logout, delete_user
)

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="🏥",
    layout="wide"
)

# ── HIDE STREAMLIT DEFAULT LOADING / RUNNING SPINNER ─────
st.markdown("""
    <style>
        [data-testid="stStatusWidget"] { display: none !important; }
        .stSpinner { display: none !important; }
        .element-container [data-testid="stSkeleton"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

import time
import streamlit.components.v1 as components

# ── Helper Function for Video Loading ────────────────────
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# ── Full Screen Intro Video Loading (OVERLAY METHOD) ─────
if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    video_base64 = get_base64_of_bin_file("video/intro.mp4")
    video_html = f'<source src="data:video/mp4;base64,{video_base64}" type="video/mp4">' if video_base64 else '<source src="https://cdn.pixabay.com/video/2020/05/21/40003-424696001_large.mp4" type="video/mp4">'

    components.html(
        f"""
        <script>
            const doc = window.parent.document;
            
            if (!doc.getElementById("custom-intro-screen")) {{
                const splash = doc.createElement("div");
                splash.id = "custom-intro-screen";
                splash.innerHTML = `
                    <style>
                        #custom-intro-screen {{
                            position: fixed; top: 0; left: 0;
                            width: 100vw; height: 100vh; z-index: 9999999;
                            background-color: #000; font-family: 'Segoe UI', Tahoma, sans-serif;
                            display: flex; flex-direction: column; justify-content: center; align-items: center;
                        }}
                        
                        /* DESKTOP DEFAULT SETTINGS */
                        #introVideo {{ 
                            position: absolute; top: 0; left: 0;
                            width: 100%; height: 100%; 
                            object-fit: contain; 
                            background-color: #000;
                            z-index: 1;
                        }}
                        .overlay {{
                            position: absolute; top: 0; left: 0;
                            width: 100%; height: 100%; 
                            background: rgba(0, 0, 0, 0.4); 
                            display: flex; justify-content: center; /* Exactly in the MIDDLE */
                            align-items: center; flex-direction: column; color: white;
                            z-index: 2;
                        }}
                        
                        .loading-box {{ text-align: center; width: 80%; max-width: 400px; }}
                        .loading-box h2 {{ font-weight: 300; letter-spacing: 2px; margin-bottom: 20px; text-transform: uppercase; }}
                        .progress-container {{ width: 100%; height: 6px; background: rgba(255, 255, 255, 0.2); border-radius: 10px; margin-bottom: 10px; overflow: hidden; }}
                        .progress-bar {{ width: 0%; height: 100%; background: linear-gradient(90deg, #00dbde, #fc00ff); box-shadow: 0 0 15px #00dbde; transition: width 0.05s linear; }}
                        #percentText {{ font-size: 1.2rem; font-weight: bold; }}
                        
                        /* MOBILE RESPONSIVE FIXES */
                        @media (max-width: 768px) {{
                            #introVideo {{
                                position: relative; /* Stacks normally */
                                height: auto;
                                max-height: 45vh; /* Gives room for the loading bar below */
                            }}
                            .overlay {{
                                position: relative; /* Stacks below the video */
                                height: auto;
                                background: transparent; /* No dim shading */
                                margin-top: 30px; /* Exact space below the video */
                            }}
                        }}
                    </style>
                    
                    <video autoplay muted playsinline loop id="introVideo">
                        {video_html}
                    </video>

                    <div class="overlay">
                        <div class="loading-box">
                            <h2>Launching</h2>
                            <div class="progress-container">
                                <div class="progress-bar" id="progressBar"></div>
                            </div>
                            <div id="percentText">0%</div>
                        </div>
                    </div>
                `;
                doc.body.appendChild(splash);

                let progressBar = doc.getElementById("progressBar");
                let percentText = doc.getElementById("percentText");
                let width = 0;
                let speed = 40; 

                let interval = setInterval(() => {{
                    if (width >= 100) {{
                        clearInterval(interval);
                        splash.style.transition = "opacity 0.5s ease";
                        splash.style.opacity = "0";
                        setTimeout(() => splash.remove(), 500);
                    }} else {{
                        width++;
                        progressBar.style.width = width + "%";
                        percentText.innerHTML = width + "%";
                    }}
                }}, speed);
            }}
        </script>
        """,
        height=0
    )
    
    st.session_state.splash_shown = True



# ── Mouse Cursor Sparkle Effect (Mobile Touch Added!) ────
components.html(
    """
    <script>
        const parentWin = window.parent;
        const parentDoc = parentWin.document;

        if (parentWin.__sparkleListener) {
            parentDoc.removeEventListener("mousemove", parentWin.__sparkleListener);
            parentDoc.removeEventListener("touchmove", parentWin.__sparkleListener);
        }
        
        let oldContainer = parentDoc.getElementById("cursor-sparkles");
        if (oldContainer) { oldContainer.remove(); }

        let oldStyle = parentDoc.getElementById("cursor-sparkles-style");
        if (oldStyle) { oldStyle.remove(); }

        const style = parentDoc.createElement('style');
        style.id = "cursor-sparkles-style";
        style.innerHTML = `
            #cursor-sparkles { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 999999; }
            .sparkle { position: absolute; width: 6px; height: 6px; border-radius: 50%; pointer-events: none; transform: translate(-50%, -50%); animation: fadeOut 1s ease-out forwards; }
            @keyframes fadeOut { 0% { opacity: 1; transform: translate(-50%, -50%) scale(1); } 100% { opacity: 0; transform: translate(-50%, -50%) scale(0); } }
        `;
        parentDoc.head.appendChild(style);

        const sparkleContainer = parentDoc.createElement("div");
        sparkleContainer.id = "cursor-sparkles";
        parentDoc.body.appendChild(sparkleContainer);

        parentWin.__sparkleListener = function(e) {
            const sparkle = parentDoc.createElement("div");
            sparkle.className = "sparkle";
            const colors = ["#ffffff", "#008080", "#ff4ecd", "#ffd700", "#00ff9c"];
            const color = colors[Math.floor(Math.random() * colors.length)];
            sparkle.style.background = `radial-gradient(circle, ${color}, transparent)`;
            sparkle.style.boxShadow = `0 0 10px ${color}`;
            
            let clientX = e.clientX || (e.touches && e.touches[0].clientX);
            let clientY = e.clientY || (e.touches && e.touches[0].clientY);
            
            if(clientX && clientY) {
                sparkle.style.left = clientX + "px";
                sparkle.style.top = clientY + "px";
                sparkleContainer.appendChild(sparkle);
                setTimeout(() => { if(sparkle.parentNode === sparkleContainer) { sparkle.remove(); } }, 1000); 
            }
        };

        parentDoc.addEventListener("mousemove", parentWin.__sparkleListener);
        parentDoc.addEventListener("touchmove", parentWin.__sparkleListener, {passive: true});
    </script>
    """,
    height=0
)

# # ── General CSS (Mobile Responsive Added) ────────────────
# st.markdown("""
# <style>
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}

#     [data-testid="stSidebar"] {
#         background-color: rgba(255, 255, 255, 0.7) !important;
#         backdrop-filter: blur(10px);
#         border-right: 1px solid rgba(0,0,0,0.05);
#     }
    
#     header[data-testid="stHeader"] {
#         background: transparent !important;
#     }

#     .stButton>button {
#         border-radius: 8px;
#         transition: all 0.3s ease;
#         border: 1px solid transparent;
#         box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
#         font-weight: 600;
#         width: 100%; 
#     }
#     .stButton>button:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
#         border: 1px solid #008080;
#         color: #008080;
#     }
    
#     .stButton>button[kind="primary"] {
#         background-color: #008080;
#         color: white;
#     }
#     .stButton>button[kind="primary"]:hover {
#         background-color: #006666;
#         color: white;
#     }

#     div[data-testid="metric-container"] {
#         background-color: #FFFFFF;
#         border: 1px solid #E2E8F0;
#         padding: 15px 20px;
#         border-radius: 12px;
#         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
#         transition: transform 0.2s ease-in-out;
#     }
#     div[data-testid="metric-container"]:hover {
#         transform: scale(1.02);
#         border-color: #008080;
#     }

#     div[data-testid="stVerticalBlockBorderWrapper"] {
#         background-color: #FFFFFF;
#         border-radius: 12px;
#         border: 1px solid rgba(0,0,0,0.05);
#         box-shadow: 0 4px 6px rgba(0,0,0,0.02);
#     }

#     .stTabs [data-baseweb="tab-list"] {
#         gap: 15px;
#         background-color: transparent;
#     }
#     .stTabs [data-baseweb="tab"] {
#         border-radius: 6px 6px 0px 0px;
#         padding: 10px 20px;
#         font-weight: 600;
#         background-color: rgba(255, 255, 255, 0.9);
#     }
    
#     .streamlit-expanderHeader {
#         background-color: #FFFFFF;
#         border-radius: 8px;
#         border: 1px solid #E2E8F0;
#     }

#     @media (max-width: 768px) {
#         div[data-testid="stVerticalBlockBorderWrapper"] { padding: 10px !important; }
#         .stTabs [data-baseweb="tab"] { padding: 8px 12px; font-size: 14px; }
#         [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
#         .chat-bubble { max-width: 85% !important; font-size: 14px !important; }
#         h1 { font-size: 1.8rem !important; }
#         h2 { font-size: 1.5rem !important; }
#         h3 { font-size: 1.2rem !important; }
#     }
# </style>
# """, unsafe_allow_html=True)

# # ── General CSS (Mobile Responsive Added) ────────────────
# st.markdown("""
# <style>
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     [data-testid="stToolbar"] { display: none !important; }

#     [data-testid="stSidebar"] {
#         background-color: rgba(255, 255, 255, 0.7) !important;
#         backdrop-filter: blur(10px);
#         border-right: 1px solid rgba(0,0,0,0.05);
#     }
    
#     header[data-testid="stHeader"] {
#         background: transparent !important;
#     }

#     /* 📱 MOBILE: Hamburger menu-va perusa Teal color box-la theliva kaatta */
#     header[data-testid="stHeader"] button {
#         background-color: #008080 !important;
#         border-radius: 8px !important;
#         padding: 4px !important;
#         margin: 10px !important;
#         box-shadow: 0px 4px 6px rgba(0,0,0,0.3) !important;
#     }
#     header[data-testid="stHeader"] button svg {
#         fill: #ffffff !important;
#         color: #ffffff !important;
#         width: 28px !important;
#         height: 28px !important;
#     }

#     /* 💻 DESKTOP: Pazhaya '>' symbol-a thookitu puthusa '☰' symbol poda */
#     [data-testid="collapsedControl"] {
#         background-color: #008080 !important;
#         border-radius: 8px !important;
#         margin: 15px !important;
#         box-shadow: 0px 4px 6px rgba(0,0,0,0.3) !important;
#         transition: all 0.3s ease;
#     }
#     [data-testid="collapsedControl"]:hover {
#         transform: scale(1.05);
#         background-color: #006666 !important;
#     }
#     [data-testid="collapsedControl"] svg {
#         display: none !important; /* Pazhaya symbol-a maraikirathu */
#     }
#     [data-testid="collapsedControl"]::after {
#         content: '☰' !important; /* Puthu 3-dash symbol */
#         font-size: 24px !important;
#         color: #ffffff !important;
#         font-weight: bold !important;
#         line-height: 1 !important;
#         display: flex !important;
#         justify-content: center !important;
#         align-items: center !important;
#         padding: 6px 10px !important;
#     }

#     .stButton>button {
#         border-radius: 8px;
#         transition: all 0.3s ease;
#         border: 1px solid transparent;
#         box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
#         font-weight: 600;
#         width: 100%; 
#     }
#     .stButton>button:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
#         border: 1px solid #008080;
#         color: #008080;
#     }
    
#     .stButton>button[kind="primary"] {
#         background-color: #008080;
#         color: white;
#     }
#     .stButton>button[kind="primary"]:hover {
#         background-color: #006666;
#         color: white;
#     }

#     div[data-testid="metric-container"] {
#         background-color: #FFFFFF;
#         border: 1px solid #E2E8F0;
#         padding: 15px 20px;
#         border-radius: 12px;
#         box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
#         transition: transform 0.2s ease-in-out;
#     }
#     div[data-testid="metric-container"]:hover {
#         transform: scale(1.02);
#         border-color: #008080;
#     }

#     div[data-testid="stVerticalBlockBorderWrapper"] {
#         background-color: #FFFFFF;
#         border-radius: 12px;
#         border: 1px solid rgba(0,0,0,0.05);
#         box-shadow: 0 4px 6px rgba(0,0,0,0.02);
#     }

#     .stTabs [data-baseweb="tab-list"] {
#         gap: 15px;
#         background-color: transparent;
#     }
#     .stTabs [data-baseweb="tab"] {
#         border-radius: 6px 6px 0px 0px;
#         padding: 10px 20px;
#         font-weight: 600;
#         background-color: rgba(255, 255, 255, 0.9);
#     }
    
#     .streamlit-expanderHeader {
#         background-color: #FFFFFF;
#         border-radius: 8px;
#         border: 1px solid #E2E8F0;
#     }

#     @media (max-width: 768px) {
#         div[data-testid="stVerticalBlockBorderWrapper"] { padding: 10px !important; }
#         .stTabs [data-baseweb="tab"] { padding: 8px 12px; font-size: 14px; }
#         [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
#         .chat-bubble { max-width: 85% !important; font-size: 14px !important; }
#         h1 { font-size: 1.8rem !important; }
#         h2 { font-size: 1.5rem !important; }
#         h3 { font-size: 1.2rem !important; }
#     }
# </style>
# """, unsafe_allow_html=True)

# ── General CSS (Mobile Responsive Added) ────────────────
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 1. Right side la irukka thevayillatha icons-a (Share, Star, GitHub) maraikkum */
    [data-testid="stToolbar"] { display: none !important; }

    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0,0,0,0.05);
    }
    
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 2. Left side Menu (Hamburger) Button-a theliva Teal color box-la kaatta */
    [data-testid="collapsedControl"] {
        display: inline-flex !important;
        background-color: #008080 !important;
        border-radius: 8px !important;
        margin: 15px !important;
        padding: 5px !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3) !important;
        z-index: 99999 !important;
    }
    
    /* Hover effect for Menu button */
    [data-testid="collapsedControl"]:hover {
        background-color: #006666 !important;
    }

    /* Native SVG Icon-a White color-ku maathurathu */
    [data-testid="collapsedControl"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
        width: 28px !important;
        height: 28px !important;
    }

    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
        border: 1px solid transparent;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        font-weight: 600;
        width: 100%; 
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        border: 1px solid #008080;
        color: #008080;
    }
    
    .stButton>button[kind="primary"] {
        background-color: #008080;
        color: white;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #006666;
        color: white;
    }

    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="metric-container"]:hover {
        transform: scale(1.02);
        border-color: #008080;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        font-weight: 600;
        background-color: rgba(255, 255, 255, 0.9);
    }
    
    .streamlit-expanderHeader {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
    }

    @media (max-width: 768px) {
        div[data-testid="stVerticalBlockBorderWrapper"] { padding: 10px !important; }
        .stTabs [data-baseweb="tab"] { padding: 8px 12px; font-size: 14px; }
        [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
        .chat-bubble { max-width: 85% !important; font-size: 14px !important; }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ── Load model & symptoms ─────────────────────────────────
@st.cache_resource
def load_model():
    model = joblib.load("model/rf_model.pkl")
    symptoms = joblib.load("model/symptom_list.pkl")
    return model, symptoms

@st.cache_data
def load_extra_data():
    desc_df = pd.read_csv("data/symptom_Description.csv")
    desc_df.columns = desc_df.columns.str.strip()
    prec_df = pd.read_csv("data/symptom_precaution.csv")
    prec_df.columns = prec_df.columns.str.strip()
    return desc_df, prec_df

model, symptom_list = load_model()
desc_df, prec_df = load_extra_data()

# ── Init DB ───────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            method TEXT,
            symptoms TEXT,
            prediction TEXT,
            confidence REAL,
            user_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()
init_users_db()

# ── Session state init ────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

# Setup session states for registration to persist during mobile tab changes/keyboard popups
if "reg_user_val" not in st.session_state: st.session_state.reg_user_val = ""
if "reg_email_val" not in st.session_state: st.session_state.reg_email_val = ""
if "reg_pass_val" not in st.session_state: st.session_state.reg_pass_val = ""
if "reg_confirm_val" not in st.session_state: st.session_state.reg_confirm_val = ""


# ── Top 15 symptoms for chatbot ───────────────────────────
CHATBOT_SYMPTOMS = [
    "itching", "skin_rash", "fever", "headache",
    "fatigue", "cough", "chest_pain", "vomiting",
    "breathlessness", "sweating", "back_pain",
    "weight_loss", "nausea", "joint_pain", "chills"
]

# ── History functions ─────────────────────────────────────
def save_to_history(method, symptoms, prediction, confidence, user_id):
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO history (timestamp, method, symptoms, prediction, confidence, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        method,
        ", ".join(symptoms),
        prediction,
        round(confidence, 2),
        user_id
    ))
    conn.commit()
    conn.close()

def load_history(user_id):
    conn = sqlite3.connect("history.db")
    df = pd.read_sql_query(
        "SELECT * FROM history WHERE user_id=? ORDER BY id DESC",
        conn, params=(user_id,)
    )
    conn.close()
    return df

# ── Prediction function ───────────────────────────────────
def predict_disease(selected_symptoms):
    input_vector = [1 if s in selected_symptoms else 0 for s in symptom_list]
    input_df = pd.DataFrame([input_vector], columns=symptom_list)
    prediction = model.predict(input_df)[0]
    probabilities = model.predict_proba(input_df)[0]
    classes = model.classes_
    prob_df = pd.DataFrame({
        "Disease": classes,
        "Probability": probabilities
    }).sort_values("Probability", ascending=False)
    return prediction, prob_df

# ── Disease info helper ───────────────────────────────────
def show_disease_info(prediction, user_name=""):
    with st.container(border=True):
        if user_name:
            st.success(f"### 👋 Hello {user_name}! Predicted Disease: **{prediction}**")
        else:
            st.success(f"### 🏥 Predicted Disease: **{prediction}**")

        desc_row = desc_df[desc_df["Disease"].str.strip() == prediction]
        if not desc_row.empty:
            st.markdown("---")
            st.subheader("📖 About this Disease")
            st.info(desc_row.iloc[0]["Description"])

        prec_row = prec_df[prec_df["Disease"].str.strip() == prediction]
        if not prec_row.empty:
            st.markdown("---")
            st.subheader("🛡️ Precautions to Follow")
            prec_cols = [c for c in prec_df.columns if "Precaution" in c]
            for i, col in enumerate(prec_cols, 1):
                val = prec_row.iloc[0][col]
                if pd.notna(val) and str(val).strip() != "":
                    st.write(f"**{i}.** {str(val).strip().capitalize()}")

# ── Charts helper ─────────────────────────────────────────
def show_charts(prob_df):
    top10 = prob_df.head(10)
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("📊 Top 10 Diseases — Bar Chart")
            fig_bar = px.bar(
                top10, x="Probability", y="Disease", orientation="h",
                color="Probability", color_continuous_scale="teal",
                text=top10["Probability"].apply(lambda x: f"{x*100:.1f}%")
            )
            fig_bar.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
    with col2:
        with st.container(border=True):
            st.subheader("🥧 Top 5 Diseases — Pie Chart")
            top5 = prob_df[prob_df["Probability"] > 0].head(5)
            fig_pie = px.pie(
                top5, names="Disease", values="Probability",
                color_discrete_sequence=px.colors.sequential.Teal
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

# ══════════════════════════════════════════════════════════
# AUTH PAGES — LOGIN / REGISTER
# ══════════════════════════════════════════════════════════
if not is_logged_in():
    st.markdown("""
        <style>
            .stApp { background-color: #F1F5F9 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#1E293B;'>🏥 AI Health Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748B; font-size:18px;'>Your personal disease prediction & health monitoring app</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1]) 
    with col_m:
        with st.container(border=True):
            tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

            with tab1:
                st.markdown("### Welcome back!")
                
                with st.form("login_form"):
                    login_username = st.text_input("Username")
                    login_password = st.text_input("Password", type="password")
                    st.markdown("<br>", unsafe_allow_html=True)
                    login_submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

                    if login_submitted:
                        if not login_username or not login_password:
                            st.warning("⚠️ Please fill all fields!")
                        else:
                            success, user, msg = login_user(login_username, login_password)
                            if success:
                                st.session_state.user = user
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

            with tab2:
                st.markdown("### Create your account")
                if "reg_success_msg" in st.session_state:
                    st.success(st.session_state["reg_success_msg"])
                    del st.session_state["reg_success_msg"]
                
                with st.form("register_form"):
                    reg_username = st.text_input("Username", value=st.session_state.reg_user_val)
                    reg_email    = st.text_input("Email", value=st.session_state.reg_email_val)
                    reg_password = st.text_input("Password", type="password", value=st.session_state.reg_pass_val)
                    reg_confirm  = st.text_input("Confirm Password", type="password", value=st.session_state.reg_confirm_val)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        reg_age = st.number_input("Age", min_value=1, max_value=120, value=25)
                    with col_b:
                        reg_gender = st.selectbox("Gender", ["Male", "Female", "Other"])

                    st.markdown("<br>", unsafe_allow_html=True)
                    reg_submitted = st.form_submit_button("Register", type="primary", use_container_width=True)

                    if reg_submitted:
                        st.session_state.reg_user_val = reg_username
                        st.session_state.reg_email_val = reg_email
                        st.session_state.reg_pass_val = reg_password
                        st.session_state.reg_confirm_val = reg_confirm

                        if not reg_username or not reg_email or not reg_password:
                            st.warning("⚠️ Please fill all fields!")
                        elif reg_password != reg_confirm:
                            st.error("❌ Passwords do not match!")
                        elif len(reg_password) < 6:
                            st.error("❌ Password must be at least 6 characters!")
                        else:
                            success, msg = register_user(
                                reg_username, reg_email, reg_password, reg_age, reg_gender
                            )
                            if success:
                                st.session_state["reg_success_msg"] = msg + " Please login now."
                                st.session_state.reg_user_val = ""
                                st.session_state.reg_email_val = ""
                                st.session_state.reg_pass_val = ""
                                st.session_state.reg_confirm_val = ""
                                st.rerun()
                            else:
                                st.error(msg)

# ══════════════════════════════════════════════════════════
# MAIN APP — after login
# ══════════════════════════════════════════════════════════
else:
    user = st.session_state.user

    st.sidebar.markdown(f"<h2 style='text-align: center; color: #008080;'>🏥 Health Assistant</h2>", unsafe_allow_html=True)
    
    with st.sidebar.container(border=True):
        st.markdown(f"👤 **{user['username']}**")
        st.markdown(f"📧 <small>{user['email']}</small>", unsafe_allow_html=True)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "🗂️ Manual Form", "🤖 Chatbot", "📋 History", "👤 Profile", "ℹ️ About"],
        label_visibility="hidden"
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

    # 🌟 DYNAMIC PAGE BACKGROUND COLORS 🌟
    page_colors = {
         "📊 Dashboard": "#F0F4F8",      
        "🗂️ Manual Form": "#EFFFF6",    
        "🤖 Chatbot": "#EFFFF6",        
        "📋 History": "#F0F4F8",        
        "👤 Profile": "#EFFFF6",        
        "ℹ️ About": "#EFFFF6"           
    }
    
    current_bg_color = page_colors.get(page, "#F8FAFC")

    st.markdown(f"""
        <style>
            .stApp {{
                background-color: {current_bg_color} !important;
                transition: background-color 0.4s ease-in-out;
            }}
        </style>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    # DASHBOARD
    # ══════════════════════════════════════════════════════
    if page == "📊 Dashboard":
        st.title(f"📊 Welcome, {user['username']}!")
        st.markdown("<p style='color:#64748B; font-size:16px;'>Here's your personal health summary & insights.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        df_history = load_history(user["id"])

        if df_history.empty:
            st.info("📭 No assessments yet. Use Manual Form or Chatbot to get started!")
        else:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔬 Total Assessments", len(df_history))
            col2.metric("🗂️ Via Manual Form", len(df_history[df_history["method"] == "Manual Form"]))
            col3.metric("🤖 Via Chatbot", len(df_history[df_history["method"] == "Chatbot"]))
            col4.metric("🏥 Unique Diseases", df_history["prediction"].nunique())

            st.markdown("<br>", unsafe_allow_html=True)

            col_left, col_right = st.columns(2)

            with col_left:
                with st.container(border=True):
                    st.subheader("🏆 Most Predicted Diseases")
                    top_diseases = df_history["prediction"].value_counts().head(8).reset_index()
                    top_diseases.columns = ["Disease", "Count"]
                    fig = px.bar(
                        top_diseases, x="Count", y="Disease",
                        orientation="h", color="Count",
                        color_continuous_scale="teal"
                    )
                    fig.update_layout(yaxis=dict(autorange="reversed"), showlegend=False, height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

            with col_right:
                with st.container(border=True):
                    st.subheader("📱 Assessment Method Usage")
                    method_counts = df_history["method"].value_counts().reset_index()
                    method_counts.columns = ["Method", "Count"]
                    fig2 = px.pie(
                        method_counts, names="Method", values="Count",
                        color_discrete_sequence=px.colors.sequential.Teal
                    )
                    fig2.update_traces(textposition="inside", textinfo="percent+label")
                    fig2.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig2, use_container_width=True)

            st.markdown("---")

            st.subheader("🕐 Recent Assessments")
            with st.container(border=True):
                st.dataframe(
                    df_history[["timestamp", "method", "prediction", "confidence"]].head(5),
                    use_container_width=True,
                    hide_index=True
                )

    # ══════════════════════════════════════════════════════
    # MANUAL FORM
    # ══════════════════════════════════════════════════════
    elif page == "🗂️ Manual Form":
        st.title("🗂️ Manual Symptom Checker")
        st.markdown("<p style='color:#64748B;'>Select or type your symptoms accurately for the best prediction.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        tab_cb, tab_txt = st.tabs(["☑️ Checkbox Mode", "⌨️ Text Input Mode"])

        with tab_cb:
            with st.container(border=True):
                st.markdown("#### Select your symptoms below and click Predict.")
                st.markdown("---")

                cols = st.columns(4) 
                selected = []

                for i, symptom in enumerate(symptom_list):
                    col = cols[i % 4]
                    display_name = symptom.replace("_", " ").title()
                    if col.checkbox(display_name, key=f"cb_{symptom}"):
                        selected.append(symptom)

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("🔍 Predict Disease", type="primary", key="cb_predict"):
                    if len(selected) == 0:
                        st.warning("⚠️ Please select at least one symptom!")
                    else:
                        prediction, prob_df = predict_disease(selected)
                        top_conf = prob_df.iloc[0]["Probability"] * 100
                        save_to_history("Manual Form", selected, prediction, top_conf, user["id"])

                        show_disease_info(prediction, user["username"])
                        st.markdown("<br>", unsafe_allow_html=True)
                        show_charts(prob_df)

                        st.markdown("---")
                        st.subheader("✅ Symptoms You Selected")
                        symptom_display = [s.replace("_", " ").title() for s in selected]
                        st.info(", ".join(symptom_display))

        with tab_txt:
            with st.container(border=True):
                st.markdown("#### Type your symptoms separated by commas.")
                st.markdown("Example: **fever, headache, cough**")
                st.markdown("---")

                from thefuzz import process

                with st.expander("💡 View all available symptoms"):
                    all_display = [s.replace("_", " ").title() for s in symptom_list]
                    cols_ref = st.columns(3)
                    for i, sym in enumerate(all_display):
                        cols_ref[i % 3].write(f"• {sym}")

                st.markdown("<br>", unsafe_allow_html=True)

                user_text = st.text_area(
                    "Enter your symptoms here:",
                    placeholder="fever, headache, cough, nausea...",
                    height=120,
                    key="txt_symptoms"
                )

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("🔍 Predict Disease", type="primary", key="txt_predict"):
                    if not user_text.strip():
                        st.warning("⚠️ Please enter at least one symptom!")
                    else:
                        raw_inputs = [s.strip().lower() for s in user_text.split(",") if s.strip()]
                        matched = []
                        unmatched = []
                        match_details = []

                        for raw in raw_inputs:
                            raw_underscore = raw.replace(" ", "_")
                            result = process.extractOne(
                                raw_underscore,
                                symptom_list,
                                score_cutoff=60
                            )

                            if result:
                                matched_symptom, score = result[0], result[1]
                                matched.append(matched_symptom)
                                match_details.append({
                                    "You typed": raw,
                                    "Matched to": matched_symptom.replace("_", " ").title(),
                                    "Confidence": f"{score}%"
                                })
                            else:
                                unmatched.append(raw)

                        if match_details:
                            st.subheader("🔗 Symptom Matching Results")
                            st.dataframe(
                                pd.DataFrame(match_details),
                                use_container_width=True,
                                hide_index=True
                            )

                        if unmatched:
                            st.warning(f"⚠️ Could not match: **{', '.join(unmatched)}** — please check spelling or use checkbox mode.")

                        if len(matched) == 0:
                            st.error("❌ No symptoms matched! Please try again.")
                        else:
                            prediction, prob_df = predict_disease(matched)
                            top_conf = prob_df.iloc[0]["Probability"] * 100
                            save_to_history("Text Input", matched, prediction, top_conf, user["id"])

                            st.markdown("---")
                            show_disease_info(prediction, user["username"])
                            st.markdown("<br>", unsafe_allow_html=True)
                            show_charts(prob_df)

                            st.markdown("---")
                            st.subheader("✅ Symptoms Matched")
                            symptom_display = [s.replace("_", " ").title() for s in matched]
                            st.info(", ".join(symptom_display))

    # ══════════════════════════════════════════════════════
    # CHATBOT
    # ══════════════════════════════════════════════════════
    elif page == "🤖 Chatbot":
        import streamlit.components.v1 as components

        col_title, col_btn = st.columns([3, 1])
        with col_title:
            st.title("🤖 Health Assistant Chatbot")
            st.markdown("<p style='color:#64748B;'>Answer a few quick questions to get your diagnosis.</p>", unsafe_allow_html=True)
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Start New Chat", type="primary", use_container_width=True):
                for key in ["chat_step", "chat_answers", "chat_messages", "chat_done"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if "chat_step" not in st.session_state:
            st.session_state.chat_step = 0
        if "chat_answers" not in st.session_state:
            st.session_state.chat_answers = {}
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [
                {"role": "assistant", "content": f"👋 Hi {user['username']}! I'm your Health Assistant. I'll ask you about your symptoms one by one. Let's begin!"}
            ]
        if "chat_done" not in st.session_state:
            st.session_state.chat_done = False

        with st.container(height=400, border=True):
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:flex-end; margin:10px 0;">
                            <div class="chat-bubble" style="background: linear-gradient(135deg, #008080, #006666); color:#fff; padding:12px 18px;
                                        border-radius:18px 18px 4px 18px; max-width:70%; word-wrap:break-word; overflow-wrap:break-word;
                                        font-size:15px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                                {msg["content"].replace("**", "<b>", 1).replace("**", "</b>", 1)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:flex-start; margin:10px 0;">
                            <div class="chat-bubble" style="background:#ffffff; color:#1e293b; padding:12px 18px;
                                        border-radius:18px 18px 18px 4px; max-width:70%; word-wrap:break-word; overflow-wrap:break-word;
                                        font-size:15px; box-shadow:0 2px 5px rgba(0,0,0,0.05);
                                        border: 1px solid #e2e8f0;">
                                {msg["content"].replace("**", "<b>", 1).replace("**", "</b>", 1)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            st.markdown('<div id="end-of-chat"></div>', unsafe_allow_html=True)
            
            components.html(
                """
                <script>
                    const doc = window.parent.document;
                    const targets = doc.querySelectorAll('[id="end-of-chat"]');
                    if (targets.length > 0) {
                        const target = targets[targets.length - 1];
                        
                        let scrollContainer = target.parentElement;
                        while (scrollContainer) {
                            const style = window.getComputedStyle(scrollContainer);
                            if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
                                scrollContainer.scrollTo({
                                    top: scrollContainer.scrollHeight,
                                    behavior: 'smooth'
                                });
                                break;
                            }
                            scrollContainer = scrollContainer.parentElement;
                        }
                    }
                </script>
                """,
                height=0
            )

        if not st.session_state.chat_done:
            step = st.session_state.chat_step

            if step < len(CHATBOT_SYMPTOMS):
                user_input = st.chat_input("Type yes or no...")

                if user_input:
                    st.session_state.chat_messages.append(
                        {"role": "user", "content": user_input}
                    )

                    symptom = CHATBOT_SYMPTOMS[step]
                    display = symptom.replace("_", " ").title()
                    answer = user_input.strip().lower()

                    if answer in ["yes", "y"]:
                        st.session_state.chat_answers[symptom] = 1
                        bot_reply = f"✅ Noted! You have **{display}**."
                    elif answer in ["no", "n"]:
                        st.session_state.chat_answers[symptom] = 0
                        bot_reply = f"👍 Ok, no **{display}**."
                    else:
                        bot_reply = "⚠️ Please type **yes** or **no** only."
                        st.session_state.chat_messages.append(
                            {"role": "assistant", "content": bot_reply}
                        )
                        st.rerun()

                    st.session_state.chat_step += 1
                    st.session_state.chat_messages.append(
                        {"role": "assistant", "content": bot_reply}
                    )

                    next_step = st.session_state.chat_step
                    if next_step < len(CHATBOT_SYMPTOMS):
                        next_symptom = CHATBOT_SYMPTOMS[next_step]
                        next_display = next_symptom.replace("_", " ").title()
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": f"Do you have **{next_display}**? (yes / no)"
                        })
                    else:
                        st.session_state.chat_done = True
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": "🔍 Thanks! Analyzing your symptoms now..."
                        })
                    st.rerun()

            if step == 0 and len(st.session_state.chat_messages) == 1:
                first_symptom = CHATBOT_SYMPTOMS[0].replace("_", " ").title()
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": f"Do you have **{first_symptom}**? (yes / no)"
                })
                st.rerun()

        else:
            st.markdown("---")
            selected_symptoms = [
                s for s, v in st.session_state.chat_answers.items() if v == 1
            ]

            if len(selected_symptoms) == 0:
                st.warning("⚠️ You said No to all symptoms. Please click 'Start New Chat' above and try again.")
            else:
                prediction, prob_df = predict_disease(selected_symptoms)
                top_conf = prob_df.iloc[0]["Probability"] * 100
                save_to_history("Chatbot", selected_symptoms, prediction, top_conf, user["id"])

                show_disease_info(prediction, user["username"])
                st.markdown("<br>", unsafe_allow_html=True)
                show_charts(prob_df)

    # ══════════════════════════════════════════════════════
    # HISTORY
    # ══════════════════════════════════════════════════════
    elif page == "📋 History":
        st.title("📋 My Health Assessment History")
        st.markdown("<br>", unsafe_allow_html=True)

        df_history = load_history(user["id"])

        if df_history.empty:
            st.info("📭 No history yet. Use Manual Form or Chatbot to get predictions!")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Assessments", len(df_history))
            col2.metric("Via Manual Form", len(df_history[df_history["method"] == "Manual Form"]))
            col3.metric("Via Chatbot", len(df_history[df_history["method"] == "Chatbot"]))

            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.subheader("All Records")
                st.dataframe(
                    df_history[["timestamp", "method", "prediction", "confidence", "symptoms"]],
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Clear My History"):
                conn = sqlite3.connect("history.db")
                conn.execute("DELETE FROM history WHERE user_id=?", (user["id"],))
                conn.commit()
                conn.close()
                st.success("Your history cleared!")
                st.rerun()

    # ══════════════════════════════════════════════════════
    # PROFILE
    # ══════════════════════════════════════════════════════
    elif page == "👤 Profile":
        st.title("👤 My Profile")
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.subheader("Account Details")
                st.markdown("---")
                st.write(f"**Username:** {user['username']}")
                st.write(f"**Email:** {user['email']}")
                st.write(f"**Member since:** {user['created_at']}")

        with col2:
            with st.container(border=True):
                st.subheader("Update Profile")
                st.markdown("---")
                new_age = st.number_input(
                    "Age", min_value=1, max_value=120,
                    value=int(user["age"]) if user["age"] else 25
                )
                new_gender = st.selectbox(
                    "Gender", ["Male", "Female", "Other"],
                    index=["Male", "Female", "Other"].index(user["gender"])
                    if user["gender"] in ["Male", "Female", "Other"] else 0
                )
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Save Changes", type="primary"):
                    update_profile(user["id"], new_age, new_gender)
                    st.session_state.user["age"] = new_age
                    st.session_state.user["gender"] = new_gender
                    st.success("✅ Profile updated!")

        st.markdown("<br>", unsafe_allow_html=True)

        df_history = load_history(user["id"])
        if not df_history.empty:
            with st.container(border=True):
                st.subheader("📊 My Health Stats")
                col3, col4 = st.columns(2)
                col3.metric("Total Assessments", len(df_history))
                col4.metric("Most Predicted",
                    df_history["prediction"].value_counts().index[0]
                    if not df_history.empty else "N/A"
                )
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ── Danger Zone (Delete Account) ──────────────────────
        st.markdown("---")
        st.subheader("⚠️ Danger Zone")
        with st.container(border=True):
            st.markdown("<p style='color:#DC2626; font-weight:600;'>Deleting your account is permanent. All your data and assessment history will be lost.</p>", unsafe_allow_html=True)
            
            confirm_delete = st.checkbox("I understand that this action cannot be undone.")
            
            st.markdown("""
                <style>
                div[data-testid="stButton"] button[key="btn_delete_account"] {
                    color: #DC2626; border-color: #DC2626; background-color: transparent;
                }
                div[data-testid="stButton"] button[key="btn_delete_account"]:hover {
                    background-color: #DC2626; color: white;
                }
                </style>
            """, unsafe_allow_html=True)
            
            if st.button("🗑️ Delete My Account", key="btn_delete_account"):
                if confirm_delete:
                    conn = sqlite3.connect("history.db")
                    conn.execute("DELETE FROM history WHERE user_id=?", (user["id"],))
                    conn.commit()
                    conn.close()
                    
                    delete_user(user["id"])
                    
                    logout()
                    st.rerun()
                else:
                    st.warning("⚠️ Please check the confirmation box to delete your account.")

    # ══════════════════════════════════════════════════════
    # ABOUT
    # ══════════════════════════════════════════════════════
    elif page == "ℹ️ About":
        st.title("ℹ️ About This Project")

        with st.container(border=True):
            st.markdown("""
            ## 🏥 AI-Powered Multi-Disease Prediction & Health Assistant

            This application uses **Machine Learning** to predict possible diseases
            based on symptoms provided by the user.
            """)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.subheader("🎯 Features")
                st.markdown("""
                - ✅ Predicts **41 different diseases**
                - ✅ **131 symptoms** supported
                - ✅ Manual symptom selection form
                - ✅ Conversational chatbot interface
                - ✅ Disease description & precautions
                - ✅ Health assessment history tracking
                - ✅ Interactive charts & visualizations
                - ✅ Personal login & user accounts
                - ✅ Personal dashboard & profile
                """)

        with col2:
            with st.container(border=True):
                st.subheader("🛠️ Tech Stack")
                st.markdown("""
                | Technology | Purpose |
                |-----------|---------|
                | Python | Core language |
                | Streamlit | Web UI framework |
                | Scikit-learn | ML model (Random Forest) |
                | Pandas & NumPy | Data processing |
                | Plotly | Charts & visualizations |
                | SQLite | History & user storage |
                | Bcrypt | Password security |
                """)

        st.markdown("<br>", unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            with st.container(border=True):
                st.subheader("🤖 ML Model Info")
                st.markdown("""
                - **Algorithm:** Random Forest Classifier
                - **Training samples:** 4,920
                - **Diseases covered:** 41
                - **Symptoms used:** 131
                - **Model accuracy:** 100%
                """)

        with col4:
            with st.container(border=True):
                st.subheader("⚠️ Disclaimer")
                st.warning("""
                This tool is for **educational purposes only**.
                It is NOT a substitute for professional medical advice.
                Always consult a qualified doctor for medical diagnosis.
                """)

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Developed as part of Final Year Project | Python & Machine Learning")
