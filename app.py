import streamlit as st
import pandas as pd
import json
import io
import re
from gemini_parser import extract_pdf_text, gemini_extract_statement_details
from dotenv import load_dotenv

load_dotenv()

def robust_load_json(text):
    # Try to fix common Gemini formatting errors manually
    try:
        return json.loads(text)
    except Exception:
        # Attempt to extract a JSON-like block
        match = re.search(r'({.*})', text, re.DOTALL)
        if match:
            block = match.group(1)
            try:
                return json.loads(block)
            except Exception:
                pass
        # Replace invalid trailing commas and re-try
        try:
            fixed = re.sub(",[ \t\r\n]*}", "}", text)
            fixed = re.sub(",[ \t\r\n]*]", "]", fixed)
            return json.loads(fixed)
        except Exception:
            return None

# CSS for background and headers (remains unchanged)
st.markdown("""
    <style>
        body {
            background: linear-gradient(120deg, #232526 0%, #005c97 100%) !important;
        }
        .stApp {
            background: linear-gradient(120deg, #232526 0%, #005c97 100%) !important;
        }
        .stButton > button, .css-nho97x {
            background-color: #ff9800 !important;
            color: #fff !important;
            font-weight: bold !important;
            border-radius: 6px !important;
        }
        h1, h2, h3, h4 {
            color: #ffd700 !important;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Credit Card Statement Data Extractor", page_icon="💳", layout="wide")
st.title("💳 Credit Card Statement Data Extractor")
st.subheader("Next-generation statement analysis with AI")

uploaded_pdf = st.file_uploader("Upload your Credit Card Statement (PDF)", type=["pdf"])

if uploaded_pdf:
    with st.spinner("Extracting content..."):
        pdf_text = extract_pdf_text(uploaded_pdf)
    with st.spinner("Getting the insights..."):
        gemini_result = gemini_extract_statement_details(pdf_text)
    data = robust_load_json(gemini_result)
    show_raw = False

    # Fallback to showing Gemini output if JSON could not be parsed at all
    if data is None:
        st.error("Failed to parse AI result as JSON. Here's the raw AI output for reference:")
        st.code(gemini_result)
        show_raw = True

    if not show_raw:
        # 1. Human-literate summary
        summary_text = data.get("summary_text", "").strip()
        if summary_text:
            st.success(summary_text)
        else:
            st.warning("No summary text generated.")

        # 2. Main fields display
        st.markdown("### Statement Fields")
        display_fields = [
            ("Card Ending", data.get("card_last4", "N/A")),
            ("Statement Date", data.get("statement_date", "N/A")),
            ("Total Amount Due", data.get("total_due", "N/A")),
            ("Payment Due Date", data.get("payment_due", "N/A")),
            ("Minimum Due", data.get("min_due", "N/A")),
            ("Credit Limit", data.get("credit_limit", "N/A")),
            ("Available Credit", data.get("available_credit", "N/A")),
            ("Reward Points", data.get("reward_points", "N/A")),
            ("Billing Address", data.get("billing_address", "N/A")),
            ("Late Fees/Penalties", data.get("late_fees", "N/A")),
        ]
        df_fields = pd.DataFrame(display_fields, columns=["Field", "Value"])
        st.table(df_fields)

        # 3. Transactions Display
        if "transactions" in data and isinstance(data["transactions"], list) and len(data["transactions"]):
            st.markdown("### Transactions")
            tx_df = pd.DataFrame(data["transactions"])
            st.dataframe(tx_df)
        else:
            tx_df = pd.DataFrame()
            st.info("No transaction data found.")

        # 4. Merchant Summary Table
        if "merchant_summary" in data and isinstance(data["merchant_summary"], list) and len(data["merchant_summary"]):
            st.markdown("### Top Merchant Summary")
            merch_df = pd.DataFrame(data["merchant_summary"])
            st.dataframe(merch_df)
        else:
            st.info("No merchant summary found.")

        # 5. Monthly Spending Table
        if "monthly_spending" in data and isinstance(data["monthly_spending"], list) and len(data["monthly_spending"]):
            st.markdown("### Monthly Spending Summary")
            ms_df = pd.DataFrame(data["monthly_spending"])
            st.dataframe(ms_df)
        else:
            st.info("No monthly spending summary available.")

        # 6. Download Dialog (CSV/Excel)
        if not tx_df.empty:
            open_download = st.button("Download Results")
            if open_download:
                st.markdown("""
                    <div class="download-dialog">
                        <h4>Choose Format to Download</h4>
                    </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    csv = tx_df.to_csv(index=False).encode("utf-8")
                    st.download_button(label="Download as CSV", data=csv, file_name="transactions.csv", mime="text/csv", key="csvbtn")

    st.caption("AI-powered | Fast | Secure | Exportable")
else:
    st.info("Please upload your statement PDF to begin.")

st.markdown("---")
st.caption("© 2025 | Built by Manav Bhatt")
