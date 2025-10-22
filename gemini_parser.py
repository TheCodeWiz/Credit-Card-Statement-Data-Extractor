from dotenv import load_dotenv
import os
import google.generativeai as genai
import PyPDF2

load_dotenv()

def extract_pdf_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text

def gemini_extract_statement_details(pdf_text):
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-pro')
    prompt = (
        "From the credit card statement text below, respond in strict JSON format with the following keys:\n"
        '"card_last4": string,'
        '"statement_date": string,'
        '"total_due": string,'
        '"payment_due": string,'
        '"min_due": string,'
        '"credit_limit": string,'
        '"available_credit": string,'
        '"reward_points": string,'
        '"billing_address": string,'
        '"late_fees": string,'
        '"transactions": (array: {date, description, amount, category}),'
        '"merchant_summary": (array: {merchant, transactions_count, total_spent}, top 5),'
        '"monthly_spending": (array: {month, year, amount}),'
        '"summary_text": string (2-3 readable sentences summarizing the key statement points for a non-technical user; mention card ending, statement period, total due, payment date, transaction count and largest merchant if possible).\n'
        f"Credit card statement text:\n'''{pdf_text}'''"
    )
    response = model.generate_content(prompt)
    return response.text
