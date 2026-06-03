import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import httpx
from datetime import date, datetime, timedelta
from report_generator import generate_pdf_report
import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="PCOS Tracker - Empowering Hormonal Health",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_URL = BACKEND_URL

# Custom Styling (Pastel medical theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background-color: #FAFAFC;
    }
    
   h1, h2, h3 {
    color: #4A4E69;
}

.card p, .card div, .card span, .card label {
    color: #4A4E69 !important;
}
    
    .stButton>button {
        background: linear-gradient(135deg, #F3C6D1 0%, #E29578 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #E29578 0%, #F3C6D1 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        color: white;
    }
    
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem;
        border: 1px solid #ECEEF6;
        color: #4A4E69 !important;  
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #8C92AC !important;
        margin: 0.2rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #8C92AC;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    .phase-badge {
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        color: white;
        display: inline-block;
    }
    
    .phase-Menstrual { background-color: #E29578; }
    .phase-Follicular { background-color: #83C5BE; }
    .phase-Ovulatory { background-color: #FFB5A7; }
    .phase-Luteal { background-color: #9C89B8; }
</style>
""", unsafe_allow_html=True)

# Helper functions for API calls
def api_headers():
    headers = {}
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"
    return headers

def safe_api_request(method, endpoint, json_data=None, params=None):
    try:
        with httpx.Client(timeout=10.0) as client:
            url = f"{API_URL}{endpoint}"
            if method == "GET":
                response = client.get(url, headers=api_headers(), params=params)
            elif method == "POST":
                response = client.post(url, headers=api_headers(), json=json_data, params=params)
            elif method == "PUT":
                response = client.put(url, headers=api_headers(), json=json_data, params=params)
            elif method == "DELETE":
                response = client.delete(url, headers=api_headers())
            
            if response.status_code in [200, 201, 204]:
                return response.json() if response.status_code != 204 else True
            else:
                try:
                    err_msg = response.json().get("detail", "Request failed.")
                except:
                    err_msg = response.text
                return {"error": err_msg, "status_code": response.status_code}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

# Session state initialization
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

# Sidebar Auth status
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>PCOS Tracker</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8C92AC;'>Empowering and tracking hormonal health</p>", unsafe_allow_html=True)
    st.write("---")
    
    if st.session_state["token"]:
        st.markdown(f"**Logged in as:**\n{st.session_state['user_name'] or st.session_state['user_email']}")
        if st.button("Logout"):
            st.session_state["token"] = None
            st.session_state["user_email"] = None
            st.session_state["user_name"] = None
            st.rerun()
    else:
        st.info("Please log in or sign up to begin tracking.")

# Main routing logic
if not st.session_state["token"]:
    # Display Login / Signup
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        
        with tab_login:
            st.subheader("Login to your Account")
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Log In"):
                res = safe_api_request("POST", "/auth/login", {"email": login_email, "password": login_password})
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.session_state["token"] = res["access_token"]
                    st.session_state["user_email"] = login_email
                    # Fetch profile info
                    prof = safe_api_request("GET", "/auth/me")
                    if "error" not in prof:
                        st.session_state["user_name"] = prof.get("full_name")
                    st.success("Successfully logged in.")
                    st.rerun()
                    
        with tab_signup:
            st.subheader("Create a New Account")
            signup_name = st.text_input("Full Name", key="signup_name")
            signup_email = st.text_input("Email Address", key="signup_email")
            signup_password = st.text_input("Password (min 6 characters)", type="password", key="signup_password")
            if st.button("Sign Up"):
                if len(signup_password) < 6:
                    st.warning("Password must be at least 6 characters.")
                else:
                    res = safe_api_request("POST", "/auth/signup", {
                        "email": signup_email, 
                        "password": signup_password,
                        "full_name": signup_name
                    })
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success("Account created successfully. Please login.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='card' style='text-align: center;'>", unsafe_allow_html=True)
        st.subheader("Easy Access Demo Account")
        st.write("For testing without creating an account, use the following credentials:")
        st.code("Email: demo@pcostracker.org\nPassword: demopassword123", language="text")
        
        st.write("---")
        
        st.subheader("Google OAuth Authentication Mockup")
        st.write("Secure healthcare apps support fast OAuth registration.")
        if st.button("Simulated Google OAuth Single-Sign-On"):
            # Call /auth/google with a mock validated JWT payload
            mock_payload = {
                "email": "google_test_user@gmail.com",
                "sub": "google-oauth-sub-123456789",
                "name": "Sarah Parker"
            }
            res = safe_api_request("POST", "/auth/google", mock_payload)
            if "error" in res:
                st.error(res["error"])
            else:
                st.session_state["token"] = res["access_token"]
                st.session_state["user_email"] = mock_payload["email"]
                st.session_state["user_name"] = mock_payload["name"]
                st.success("Authenticated successfully via Google OAuth!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Logged In App Interface
    menu = ["Dashboard", "Log Daily Symptoms", "Menstrual Cycle Logs", "AI Lifestyle Prediction", "Reminders & Alerts"]
    choice = st.sidebar.radio("Navigation Menu", menu)
    
    if choice == "Dashboard":
        st.title("Hormonal Health & Cycle Dashboard")
        
        # Load Prediction and Phase details
        pred_res = safe_api_request("GET", "/cycles/prediction")
        symptom_res = safe_api_request("GET", "/symptoms")
        cycle_res = safe_api_request("GET", "/cycles")
        
        # Grid metrics
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='metric-label'>Current Phase</div>", unsafe_allow_html=True)
            phase = pred_res.get("current_phase", "Menstrual") if "error" not in pred_res else "Menstrual"
            st.markdown(f"<span class='phase-badge phase-{phase}'>{phase}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='metric-label'>Next Period Prediction</div>", unsafe_allow_html=True)
            pred_date = pred_res.get("predicted_start_date", "N/A") if "error" not in pred_res else "N/A"
            st.markdown(f"<div class='metric-value'>{pred_date}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='metric-label'>Days Until Next Period</div>", unsafe_allow_html=True)
            days = pred_res.get("days_until_next_period", 28) if "error" not in pred_res else 28
            days_str = f"{days} days" if days >= 0 else f"Delayed by {abs(days)} days"
            st.markdown(f"<div class='metric-value'>{days_str}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c4:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='metric-label'>Logged Days</div>", unsafe_allow_html=True)
            log_count = len(symptom_res) if isinstance(symptom_res, list) else 0
            st.markdown(f"<div class='metric-value'>{log_count} Entries</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Personalized Phase Recommendations Section
        if "error" not in pred_res:
            recs = pred_res["phase_recommendations"]
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader(f"Custom Phase Recommendations: {recs.get('phase_name')}")
            st.write(f"**Hormone Profile:** {recs.get('hormones')}")
            st.write(f"**PCOS Focus:** {recs.get('pcos_focus')}")
            
            col_diet, col_ex = st.columns(2)
            with col_diet:
                st.markdown("**Nutrients & Diet Suggestions:**")
                for item in recs.get("diet", []):
                    st.write(f"- {item}")
            with col_ex:
                st.markdown("**Tailored Exercise Program:**")
                for item in recs.get("exercise", []):
                    st.write(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Analytics charts
        if isinstance(symptom_res, list) and len(symptom_res) > 0:
            df_sym = pd.DataFrame(symptom_res)
            # Re-convert dates
            df_sym["date"] = pd.to_datetime(df_sym["date"])
            
            # Chart grid
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader("Cycle Tracking Over Time")
                if isinstance(cycle_res, list) and len(cycle_res) > 0:
                    df_cyc = pd.DataFrame(cycle_res)
                    df_cyc = df_cyc.dropna(subset=["cycle_length"])
                    if not df_cyc.empty:
                        fig = px.line(
                            df_cyc, x="start_date", y="cycle_length",
                            title="Menstrual Cycle Length (Days)",
                            markers=True, color_discrete_sequence=["#E29578"]
                        )
                        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Log at least two menstrual cycles to visualize cycle length variation over time.")
                else:
                    st.info("No cycle data logs recorded.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col_chart2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader("Symptom Correlation Heatmap")
                corr_cols = ["pain_level", "stress_level", "sleep_hours", "exercise_minutes", "bloating", "hair_growth", "acne"]
                # Filter down to present columns
                corr_cols = [c for c in corr_cols if c in df_sym.columns]
                
                if len(df_sym) >= 3:
                    corr_df = df_sym[corr_cols].corr()
                    fig = px.imshow(
                        corr_df,
                        text_auto=".2f",
                        color_continuous_scale="Purples",
                        labels=dict(color="Correlation"),
                        x=corr_df.columns,
                        y=corr_df.index
                    )
                    fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Please log at least 3 daily symptom logs to compute correlations.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            # Export data row
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Export Medical Health Reports")
            col_csv, col_pdf = st.columns(2)
            
            with col_csv:
                st.write("Download your entire symptoms record in CSV format for personal archiving or spreadsheet analysis.")
                csv_bytes = df_sym.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Symptoms Data CSV",
                    data=csv_bytes,
                    file_name="pcos_tracker_symptoms.csv",
                    mime="text/csv"
                )
                
            with col_pdf:
                st.write("Generate a beautifully structured, styled, print-friendly PDF medical log to share with your gynecologist or endocrinologist.")
                cycles_list = cycle_res if isinstance(cycle_res, list) else []
                try:
                    pdf_bytes = generate_pdf_report(
                        user_name=st.session_state["user_name"],
                        symptoms=symptom_res,
                        cycles=cycles_list
                    )
                    st.download_button(
                        label="Download PDF Health Report",
                        data=pdf_bytes,
                        file_name="PCOS_Health_Report.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Failed to compile PDF Report: {str(e)}")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Welcome to PCOS Tracker! Please log your symptoms in the next section to begin accumulating statistics and generating correlation charts.")

    elif choice == "Log Daily Symptoms":
        st.title("Daily Symptom & Lifestyle Tracker")
        st.write("Consistency is key to understanding PCOS triggers and cycle fluctuations. Log today's symptoms:")
        
        # Log Form
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        log_date = st.date_input("Date", date.today())
        
        c1, c2 = st.columns(2)
        with c1:
            pain = st.slider("Pelvic Pain / Cramps Level (0 - 10)", 0, 10, 0)
            bloating = st.select_slider("Bloating Intensity", options=[0, 1, 2, 3], format_func=lambda x: ["None", "Mild", "Moderate", "Severe"][x])
            acne = st.select_slider("Acne Breakout Intensity", options=[0, 1, 2, 3], format_func=lambda x: ["None", "Mild", "Moderate", "Severe"][x])
            hair = st.select_slider("Hirsutism / Hair Growth", options=[0, 1, 2, 3], format_func=lambda x: ["None", "Mild", "Moderate", "Severe"][x])
            
        with c2:
            mood = st.selectbox("Dominant Emotional State / Mood", ["Calm", "Happy", "Irritable", "Sad", "Anxious", "Fatigued"])
            sleep = st.number_input("Sleep Duration (Hours)", min_value=0.0, max_value=24.0, value=8.0, step=0.5)
            exercise = st.number_input("Exercise Duration (Minutes)", min_value=0, max_value=480, value=0, step=5)
            stress = st.slider("Daily Stress Level (1 - 10)", 1, 10, 5)
            diet = st.selectbox("Primary Diet Intake Profile", ["Balanced", "Low Carb", "Mediterranean", "Keto", "High Sugar"])
            
        if st.button("Save Daily Log"):
            payload = {
                "date": str(log_date),
                "pain_level": pain,
                "mood": mood,
                "bloating": bloating,
                "hair_growth": hair,
                "acne": acne,
                "sleep_hours": sleep,
                "diet_type": diet,
                "exercise_minutes": exercise,
                "stress_level": stress
            }
            res = safe_api_request("POST", "/symptoms", payload)
            if "error" in res:
                st.error(res["error"])
            else:
                st.success(f"Successfully recorded daily symptoms for {log_date}!")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display history
        st.subheader("Previous Daily Logs")
        hist_res = safe_api_request("GET", "/symptoms")
        if isinstance(hist_res, list) and hist_res:
            df_hist = pd.DataFrame(hist_res)
            st.dataframe(df_hist[["date", "pain_level", "mood", "bloating", "sleep_hours", "exercise_minutes", "diet_type"]].head(10))
        else:
            st.info("No symptoms logged yet.")

    elif choice == "Menstrual Cycle Logs":
        st.title("Period Cycle & Bleeding Tracker")
        
        col_log, col_hist = st.columns([1, 1])
        
        with col_log:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Record Period Start Date")
            st.write("Log the first day of your bleeding to mark the beginning of a new cycle:")
            start_date = st.date_input("Start Date", date.today())
            if st.button("Log Period Start"):
                res = safe_api_request("POST", "/cycles", {"start_date": str(start_date)})
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success(f"New cycle logged successfully starting on {start_date}!")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Record Bleeding End Date")
            st.write("Update the end date of your latest logged period once active bleeding completes:")
            end_date = st.date_input("End Date", date.today())
            if st.button("Update Period End"):
                res = safe_api_request("PUT", "/cycles/latest", {"end_date": str(end_date)})
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success(f"Latest cycle bleeding end date updated to {end_date}!")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_hist:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Cycle Logging Records")
            c_hist = safe_api_request("GET", "/cycles")
            if isinstance(c_hist, list) and c_hist:
                df_c = pd.DataFrame(c_hist)
                st.dataframe(df_c[["start_date", "end_date", "cycle_length", "period_length"]])
            else:
                st.info("No menstrual cycle records logged yet.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "AI Lifestyle Prediction":
        st.title("AI Menstrual Irregularity Prediction")
        st.write("Using our trained scikit-learn Random Forest model, we predict the likelihood of cycle irregularity based on lifestyle and symptom loads.")
        
        tab_auto, tab_manual = st.tabs(["Automated 30-Day Analysis", "Manual Inference Simulator"])
        
        with tab_auto:
            st.subheader("Automated Trend Prediction")
            st.write("This tool aggregates your daily symptom entries over the past 30 days, calculates baseline averages, and feeds them directly into the ML model.")
            
            if st.button("Analyze My Lifestyle Trends"):
                with st.spinner("Retrieving log data and running Random Forest inference..."):
                    res = safe_api_request("GET", "/predictions/analyze-my-lifestyle")
                    if "error" in res:
                        st.error(res["error"])
                    elif not res.get("has_enough_data"):
                        st.warning(res.get("message"))
                    else:
                        st.success("Analysis complete!")
                        
                        # Display results
                        c_prob, c_status = st.columns(2)
                        with c_prob:
                            prob_val = res["prediction"]["probability"]
                            st.metric("Irregularity Probability", f"{prob_val * 100:.1f}%")
                            st.progress(prob_val)
                        with c_status:
                            status_val = "Irregular Cycle Pattern Predicted" if res["prediction"]["is_irregular"] else "Regular Cycle Pattern Predicted"
                            st.subheader(status_val)
                            st.write(f"**Method:** {res['prediction']['method']}")
                            
                        # Display averages
                        st.markdown("---")
                        st.subheader("📊 Your 30-Day Lifestyle Baselines")
                        averages = res["averages"]
                        
                        col_avg1, col_avg2 = st.columns(2)
                        with col_avg1:
                            st.write(f"- **Average Sleep:** {averages['sleep_hours']} hours/day")
                            st.write(f"- **Average Exercise:** {averages['exercise_minutes']} minutes/day")
                            st.write(f"- **Average Stress Level:** {averages['stress_level']} (1-10)")
                            st.write(f"- **Average Pelvic Pain:** {averages['pain_level']} (0-10)")
                        with col_avg2:
                            st.write(f"- **Average Bloating:** {averages['bloating']} (0-3)")
                            st.write(f"- **Average Hirsutism:** {averages['hair_growth']} (0-3)")
                            st.write(f"- **Average Acne Breakout:** {averages['acne']} (0-3)")
                            st.write(f"- **Primary Diet Intake:** {averages['diet_type']}")

        with tab_manual:
            st.subheader("Manual Inference Simulator")
            st.write("Simulate custom lifestyle scenarios to observe how changes in sleep, stress, and exercise parameters affect cycle stability projections.")
            
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                m_sleep = st.slider("Sleep Hours", 4.0, 10.0, 7.5, 0.5)
                m_exec = st.slider("Exercise Minutes", 0, 120, 30, 5)
                m_stress = st.slider("Stress Level", 1.0, 10.0, 5.0, 0.5)
                m_pain = st.slider("Pelvic Pain Level", 0.0, 10.0, 2.0, 0.5)
            with c_m2:
                m_bloat = st.slider("Bloating Level", 0, 3, 1)
                m_hair = st.slider("Hirsutism Level", 0, 3, 1)
                m_acne = st.slider("Acne Level", 0, 3, 1)
                m_diet = st.selectbox("Diet Profile Type", ["Balanced", "Low Carb", "Mediterranean", "Keto", "High Sugar"])
                
            if st.button("Run Simulation"):
                params = {
                    "sleep_hours": m_sleep,
                    "exercise_minutes": m_exec,
                    "stress_level": m_stress,
                    "pain_level": m_pain,
                    "bloating": m_bloat,
                    "hair_growth": m_hair,
                    "acne": m_acne,
                    "diet_type": m_diet
                }
                res = safe_api_request("POST", "/predictions/predict", params=params)
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.markdown("---")
                    col_res1, col_res2 = st.columns(2)
                    with col_res1:
                        prob_val = res["probability"]
                        st.metric("Simulated Irregularity Risk", f"{prob_val * 100:.1f}%")
                        st.progress(prob_val)
                    with col_res2:
                        status_val = "Irregular Cycle Pattern Projected" if res["is_irregular"] else "Regular Cycle Pattern Projected"
                        st.subheader(status_val)
                        st.write(f"Method: {res['method']}")

    elif choice == "Reminders & Alerts":
        st.title("Reminders & Healthcare Notifications")
        st.write("Ensure medication adherence and keep track of essential medical checkups by triggering Discord or Email alarms.")
        
        tab_med, tab_app, tab_test = st.tabs(["Medication Reminders", "Doctor Appointments", "Test Configurations"])
        
        with tab_med:
            st.subheader("Configure Medication Reminder")
            m_name = st.text_input("Medication Name (e.g. Metformin, Spironolactone, Myo-Inositol)", key="m_name")
            m_dose = st.text_input("Dosage (e.g. 500mg, 1 Capsule)", key="m_dose")
            m_time = st.text_input("Scheduled Time (e.g. 08:00 AM, With Dinner)", key="m_time")
            m_notes = st.text_area("Additional Notes", key="m_notes")
            m_email = st.text_input("Email Destination (defaults to profile)", key="m_email")
            
            if st.button("Dispatch Medication Reminder"):
                payload = {
                    "medication_name": m_name,
                    "dosage": m_dose,
                    "time": m_time,
                    "notes": m_notes,
                    "email_recipient": m_email if m_email else None
                }
                res = safe_api_request("POST", "/alerts/medication", payload)
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success("Reminder request dispatched.")
                    st.write(res)
                    
        with tab_app:
            st.subheader("Configure Appointment Reminder")
            a_doc = st.text_input("Doctor Name / Specialization (e.g. Dr. Davis - Gynecologist)", key="a_doc")
            a_clinic = st.text_input("Clinic / Hospital Name", key="a_clinic")
            a_time = st.text_input("Appointment Date & Time (e.g. Tomorrow at 10:30 AM)", key="a_time")
            a_notes = st.text_area("Special Instructions (e.g. Fasting required)", key="a_notes")
            a_email = st.text_input("Email Destination", key="a_email")
            
            if st.button("Dispatch Appointment Reminder"):
                payload = {
                    "doctor_name": a_doc,
                    "clinic_name": a_clinic,
                    "appointment_time": a_time,
                    "notes": a_notes,
                    "email_recipient": a_email if a_email else None
                }
                res = safe_api_request("POST", "/alerts/appointment", payload)
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success("Reminder request dispatched.")
                    st.write(res)
                    
        with tab_test:
            st.subheader("Integration Diagnostics")
            st.write("Ensure your API environment variables are wired correctly by firing off instant test messages.")
            
            if st.button("Send Test Discord Webhook Alert"):
                res = safe_api_request("POST", "/alerts/test-discord")
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.success("Discord alert fired successfully. Check your Discord channel!")
