import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Saaya Credit Officer Dashboard",
    page_icon="🏦",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "assets" / "saaya-logo.png"

DEFAULT_APPLICATIONS = [
    {
        "Application ID": "SA-2026-1042",
        "Applicant": "Ayesha Khan",
        "Loan Amount": 45000,
        "Business Years": 2,
        "Guarantor": "Yes",
        "Bureau Record": "Yes",
        "Repayment History": "Good",
        "Documents": "Complete",
        "Status": "Ready for review",
        "Recommendation": "Fast-track to credit officer",
        "Risk Level": "Low",
        "Branch": "Lahore Main",
    },
    {
        "Application ID": "SA-2026-1043",
        "Applicant": "Bilal Ahmed",
        "Loan Amount": 70000,
        "Business Years": 3,
        "Guarantor": "Yes",
        "Bureau Record": "Yes",
        "Repayment History": "No previous Saaya loan",
        "Documents": "Missing",
        "Status": "Documents missing",
        "Recommendation": "Application incomplete",
        "Risk Level": "Pending",
        "Branch": "Lahore Main",
    },
    {
        "Application ID": "SA-2026-1044",
        "Applicant": "Sana Bibi",
        "Loan Amount": 60000,
        "Business Years": 2,
        "Guarantor": "Yes",
        "Bureau Record": "No",
        "Repayment History": "No previous Saaya loan",
        "Documents": "Complete",
        "Status": "Manual review",
        "Recommendation": "Manual review required",
        "Risk Level": "Needs review",
        "Branch": "Lahore Main",
    },
]

if "applications" not in st.session_state:
    st.session_state.applications = DEFAULT_APPLICATIONS.copy()


def determine_outcome(documents, business_years, guarantor, repayment_history):
    if documents == "Missing":
        return "Documents missing", "Application incomplete", "Pending"

    if business_years < 1 or guarantor == "No":
        return "Manual review", "Manual review required", "Needs review"

    if repayment_history == "Good":
        return "Ready for review", "Fast-track to credit officer", "Low"

    return "Manual review", "Manual review required", "Medium"


def officer_action_note(application):
    recommendation = application["Recommendation"]

    if recommendation == "Application incomplete":
        return (
            "Action required: request the missing documents before progressing "
            "the application to credit assessment."
        )

    if recommendation == "Manual review required":
        return (
            "Action required: review the application, verify relevant evidence, "
            "and complete the required field assessment before recording a decision."
        )

    return (
        "Action required: prioritise the application for credit review and "
        "complete the field visit before recording the final decision."
    )


def show_gate_checks(documents, business_years, guarantor, bureau_record, repayment_history):
    documents_complete = str(documents).strip().lower() == "complete"

    checks = [
        ("PASS" if documents_complete else "REVIEW", "Documents complete"),
        (
            "PASS" if business_years >= 1 else "REVIEW",
            "Business operating for at least one year"
        ),
        (
            "PASS" if guarantor == "Yes" else "REVIEW",
            "Guarantor available"
        ),
        (
            "PASS" if bureau_record == "Yes" else "INFO",
            "Credit bureau record available"
        ),
        (
            "PASS" if repayment_history == "Good" else "INFO",
            "Previous repayment history with Saaya"
        ),
    ]

    for result, check_name in checks:
        if result == "PASS":
            st.success(f"PASS — {check_name}")

        elif result == "INFO":
            st.info(
                f"INFO — {check_name}: additional officer assessment is required."
            )

        else:
            st.warning(f"REVIEW — {check_name}")


st.markdown("""
<style>
.stApp { background:#f4f7fa; color:#172b3a; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:1.2rem; max-width:1450px; }

h1, h2, h3 { color:#16477c !important; }
p, label { color:#172b3a !important; }

[data-testid="stSidebar"] { background:#16477c; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span { color:white !important; }

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background:white !important;
    color:#172b3a !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color:#172b3a !important;
}

.top-banner {
    background:linear-gradient(110deg,#123d69,#216aa4);
    border-radius:16px;
    padding:24px 28px;
    margin-bottom:18px;
}

.top-banner h1 { color:white !important; margin:0; }
.top-banner p { color:#e7f1fb !important; margin:8px 0 0; }

.governance-note {
    background:#fff4d9;
    border-left:5px solid #d79214;
    border-radius:9px;
    padding:14px 18px;
    margin:4px 0 22px;
    color:#5d4300 !important;
}

.metric-box {
    background:white;
    border-top:4px solid #d79214;
    border-radius:12px;
    padding:16px 18px;
    min-height:125px;
    box-shadow:0 4px 12px rgba(20,71,124,.09);
}

.metric-label {
    color:#5f7180 !important;
    font-size:12px;
    font-weight:700;
}

.metric-value {
    color:#16477c !important;
    font-size:30px;
    font-weight:800;
    margin:8px 0 3px;
}

.metric-note { color:#287a70 !important; font-size:12px; }

.recommendation {
    background:#16477c;
    border-radius:10px;
    padding:16px;
    margin:14px 0;
}

.recommendation p, .recommendation h3 {
    color:white !important;
    margin:0;
}

[data-testid="stFormSubmitButton"] button,
button[kind="primary"] {
    background:#d79214 !important;
    color:white !important;
    border:none !important;
    font-weight:700 !important;
}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown("## Credit Officer Workspace")
    st.caption("Lahore Main Branch")

    page = st.radio(
        "Navigation",
        ["Dashboard", "Application Review", "Add Application"]
    )

    st.divider()
    st.markdown("**Officer**")
    st.write("Hira Fatima")
    st.markdown("**Today**")
    st.write(datetime.now().strftime("%d %B %Y"))


st.markdown("""
<div class="top-banner">
<h1>Saaya Credit Officer Dashboard</h1>
<p>Faster document checks, explainable recommendations, and human decision control</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="governance-note">
<b>Governance:</b> All records and performance indicators displayed are fictional.
The dashboard provides decision support only; authorised Saaya credit officers retain responsibility for final lending decisions.
</div>
""", unsafe_allow_html=True)

applications_df = pd.DataFrame(st.session_state.applications)


if page == "Dashboard":

    ready_count = len(applications_df[applications_df["Status"] == "Ready for review"])
    incomplete_count = len(applications_df[applications_df["Status"] == "Documents missing"])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="metric-box">
        <div class="metric-label">APPLICATIONS TODAY</div>
        <div class="metric-value">42</div>
        <div class="metric-note">Current branch workload</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-label">READY FOR REVIEW</div>
        <div class="metric-value">{ready_count + 17}</div>
        <div class="metric-note">Initial checks complete</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-box">
        <div class="metric-label">INCOMPLETE FILES</div>
        <div class="metric-value">{incomplete_count + 8}</div>
        <div class="metric-note">Customer follow-up needed</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="metric-box">
        <div class="metric-label">AVERAGE DECISION TIME</div>
        <div class="metric-value">1.7</div>
        <div class="metric-note">Working days · Target: 2 days</div>
        </div>
        """, unsafe_allow_html=True)

    chart1, chart2 = st.columns(2)

    with chart1:
        st.subheader("Application volume this week")

        volume_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            "Applications": [31, 35, 29, 38, 42, 24]
        })

        figure = px.area(
            volume_data,
            x="Day",
            y="Applications",
            markers=True,
            color_discrete_sequence=["#16477c"]
        )

        figure.update_layout(
            height=330,
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#172b3a")
        )

        st.plotly_chart(figure, use_container_width=True)

    with chart2:
        st.subheader("Application status")

        status_data = applications_df["Status"].value_counts().reset_index()
        status_data.columns = ["Status", "Count"]

        figure = px.pie(
            status_data,
            names="Status",
            values="Count",
            hole=0.58,
            color="Status",
            color_discrete_map={
                "Ready for review": "#2c8c70",
                "Documents missing": "#d79214",
                "Manual review": "#16477c"
            }
        )

        figure.update_layout(
            height=330,
            paper_bgcolor="white",
            font=dict(color="#172b3a")
        )

        st.plotly_chart(figure, use_container_width=True)

    st.subheader("Priority application queue")

    queue_table = applications_df[
        ["Application ID", "Applicant", "Loan Amount", "Status", "Recommendation"]
    ].copy()

    queue_table["Loan Amount"] = queue_table["Loan Amount"].apply(
        lambda amount: f"PKR {amount:,}"
    )

    st.dataframe(queue_table, use_container_width=True, hide_index=True)


elif page == "Application Review":

    st.subheader("Application review")

    selected_name = st.selectbox(
        "Select an application from the queue",
        applications_df["Applicant"].tolist()
    )

    selected = applications_df[
        applications_df["Applicant"] == selected_name
    ].iloc[0].to_dict()

    left, right = st.columns([1, 1.05])

    with left:
        st.subheader(selected["Applicant"])
        st.caption(f'{selected["Application ID"]} · {selected["Branch"]}')

        a, b, c = st.columns(3)

        with a:
            st.metric("Loan requested", f'PKR {selected["Loan Amount"]:,}')

        with b:
            st.metric("Business age", f'{selected["Business Years"]} years')

        with c:
            st.metric("Risk level", selected["Risk Level"])

        details = pd.DataFrame({
            "Field": [
                "Guarantor available",
                "Credit bureau record",
                "Repayment history",
                "Documents"
            ],
            "Value": [
                selected["Guarantor"],
                selected["Bureau Record"],
                selected["Repayment History"],
                selected["Documents"]
            ]
        })

        st.dataframe(details, use_container_width=True, hide_index=True)

    with right:
        st.markdown("## Gate-check results")

        show_gate_checks(
            selected["Documents"],
            selected["Business Years"],
            selected["Guarantor"],
            selected["Bureau Record"],
            selected["Repayment History"]
        )

        st.markdown("## Recommendation")

        if selected["Recommendation"] == "Fast-track to credit officer":
            st.success(selected["Recommendation"])

        elif selected["Recommendation"] == "Application incomplete":
            st.warning(selected["Recommendation"])

        else:
            st.info(selected["Recommendation"])

        st.markdown("## Officer action note")
        st.write(officer_action_note(selected))


elif page == "Add Application":

    st.subheader("Add new customer application")

    st.write(
        "Credit officers enter or verify borrower information after receiving "
        "the application and required documents at the branch."
    )

    with st.form("add_application_form"):

        col1, col2 = st.columns(2)

        with col1:
            applicant_name = st.text_input("Applicant full name")

            loan_amount = st.number_input(
                "Loan amount requested (PKR)",
                min_value=10000,
                max_value=500000,
                value=50000,
                step=1000
            )

            business_years = st.number_input(
                "Business operating for years",
                min_value=0.0,
                max_value=30.0,
                value=1.0,
                step=0.5
            )

            guarantor = st.selectbox("Guarantor available?", ["Yes", "No"])

        with col2:
            bureau_record = st.selectbox("Credit bureau record?", ["Yes", "No"])

            repayment_history = st.selectbox(
                "Previous repayment history with Saaya?",
                ["Good", "No previous Saaya loan", "Late payments"]
            )

            documents = st.selectbox(
                "Documents complete?",
                ["Complete", "Missing"]
            )

            branch = st.selectbox(
                "Branch",
                ["Lahore Main", "Karachi Central", "Multan", "Faisalabad"]
            )

        submitted = st.form_submit_button(
            "Add application and run checks",
            type="primary"
        )

    if submitted:

        if applicant_name.strip() == "":
            st.error("Please enter the applicant's full name.")

        else:
            status, recommendation, risk_level = determine_outcome(
                documents,
                business_years,
                guarantor,
                repayment_history
            )

            new_application = {
                "Application ID": f"SA-2026-{1046 + len(st.session_state.applications)}",
                "Applicant": applicant_name,
                "Loan Amount": int(loan_amount),
                "Business Years": business_years,
                "Guarantor": guarantor,
                "Bureau Record": bureau_record,
                "Repayment History": repayment_history,
                "Documents": documents,
                "Status": status,
                "Recommendation": recommendation,
                "Risk Level": risk_level,
                "Branch": branch,
            }

            st.session_state.applications.append(new_application)

            st.success("Application added to the credit officer queue.")

            st.markdown("## Gate-check results")

            show_gate_checks(
                documents,
                business_years,
                guarantor,
                bureau_record,
                repayment_history
            )

            st.markdown("## Recommendation")

            if recommendation == "Fast-track to credit officer":
                st.success(recommendation)

            elif recommendation == "Application incomplete":
                st.warning(recommendation)

            else:
                st.info(recommendation)

            st.markdown("## Officer action note")
            st.write(officer_action_note(new_application))