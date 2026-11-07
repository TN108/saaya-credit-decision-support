import streamlit as st
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    Groq = None


# Page settings
st.set_page_config(
    page_title="Saaya Credit Decision Support",
    page_icon="🏦",
    layout="wide"
)

# File paths
BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "assets" / "saaya-logo.png"


def make_recommendation(documents, years, guarantor, history):
    """
    Transparent prototype rules.
    This is not a real AI credit-scoring model.
    """

    checks = [
        ("Documents complete", documents == "Yes"),
        ("Business operating for at least one year", years >= 1),
        ("Guarantor available", guarantor == "Yes"),
    ]

    if documents == "No":
        return (
            "Application incomplete",
            "warning",
            checks,
            "Some required documents are missing. Please provide the missing documents so Saaya can continue reviewing your application."
        )

    if years < 1 or guarantor == "No":
        return (
            "Manual review required",
            "info",
            checks,
            "Your application needs review by a credit officer because some eligibility information requires verification."
        )

    if history == "Good":
        return (
            "Fast-track to credit officer",
            "success",
            checks,
            "Your application passed the initial checks and has a good repayment record. A credit officer will complete the final review."
        )

    return (
        "Manual review required",
        "info",
        checks,
        "A credit officer will review your application because more information is needed to understand repayment ability. No automatic decline is made."
    )


def create_ai_explanation(outcome, normal_explanation):
    """
    Groq only improves the customer explanation.
    It does not make the lending decision.
    """

    api_key = st.secrets.get("GROQ_API_KEY", "")

    if not api_key or Groq is None:
        return normal_explanation

    prompt = f"""
Write exactly two short, respectful sentences in simple English for a
microfinance-bank customer.

Preliminary outcome: {outcome}
Reason: {normal_explanation}

Rules:
- Do not say AI made the decision.
- Do not promise loan approval or rejection.
- State that a credit officer makes the final decision.
"""

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=100,
        )

        return response.choices[0].message.content

    except Exception:
        return normal_explanation


# Light Saaya theme
st.markdown("""
<style>
    .stApp {
        background-color: #f7f8f7;
        color: #172b3a;
    }

    h1, h2, h3 {
        color: #16477c !important;
    }

    p, label, span {
        color: #172b3a !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: #172b3a !important;
        font-weight: 600;
    }

    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input,
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #172b3a !important;
        border-color: #b7c4d0 !important;
    }

    [data-testid="stNumberInput"] input {
        color: #172b3a !important;
    }

    .note {
        border-left: 5px solid #d79214;
        background-color: #fff9ed;
        padding: 14px 18px;
        border-radius: 7px;
        color: #172b3a !important;
        margin-bottom: 24px;
    }

    .note b {
        color: #16477c !important;
    }

    div.stButton > button {
        background-color: #16477c !important;
        color: white !important;
        border: none !important;
        font-weight: bold;
    }

    div.stButton > button:hover {
        background-color: #10365e !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# Header
logo_col, title_col = st.columns([1, 3])

with logo_col:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.warning("Logo file not found. Add saaya-logo.png to the assets folder.")

with title_col:
    st.title("Credit Decision Support")
    st.caption(
        "Explainable workflow prototype — Final lending decisions remain with credit officers"
    )

st.markdown("""
<div class="note">
<b>Prototype demonstration:</b> This is not a real credit-scoring model.
It uses transparent checks to help staff process applications faster.
A trained credit officer makes every final lending decision.
</div>
""", unsafe_allow_html=True)


# Main application layout
form_col, output_col = st.columns([1.1, 0.9], gap="large")

with form_col:
    st.subheader("Applicant details")

    with st.form("loan_form"):

        name = st.text_input("Applicant name")

        amount = st.number_input(
            "Loan amount (PKR)",
            min_value=10000,
            max_value=500000,
            value=50000,
            step=1000
        )

        years = st.number_input(
            "Business operating for years",
            min_value=0.0,
            max_value=30.0,
            value=1.0,
            step=0.5
        )

        guarantor = st.selectbox(
            "Guarantor available?",
            ["Yes", "No"]
        )

        bureau = st.selectbox(
            "Credit bureau record?",
            ["Yes", "No"]
        )

        history = st.selectbox(
            "Previous repayment history with Saaya?",
            ["Good", "No previous Saaya loan", "Late payments"]
        )

        documents = st.selectbox(
            "Documents complete?",
            ["Yes", "No"]
        )

        submitted = st.form_submit_button(
            "Run checks",
            type="primary"
        )


with output_col:
    st.subheader("Decision-support output")

    if submitted:

        outcome, message_type, checks, explanation = make_recommendation(
            documents,
            years,
            guarantor,
            history
        )

        st.markdown("#### Gate-check results")

        for check_name, passed in checks:
            if passed:
                st.success(f"PASS — {check_name}")
            else:
                st.warning(f"REVIEW — {check_name}")

        st.markdown("#### Recommendation")

        if message_type == "success":
            st.success(outcome)

        elif message_type == "warning":
            st.warning(outcome)

        else:
            st.info(outcome)

        st.markdown("#### Customer explanation")

        customer_explanation = create_ai_explanation(
            outcome,
            explanation
        )

        st.write(customer_explanation)

        st.caption(
            "Governance safeguard: Fairness and repayment outcomes should be monitored "
            "by gender, rural/urban location, branch, and bureau-record availability."
        )

    else:
        st.info("Enter applicant information and select Run checks.")