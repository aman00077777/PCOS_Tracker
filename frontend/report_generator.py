from fpdf import FPDF
from datetime import datetime
import pandas as pd
import re

def sanitize_text(text):
    """Strip any characters outside the Latin-1 range (emojis, special Unicode) for safe PDF rendering."""
    if not isinstance(text, str):
        text = str(text)
    # Keep only characters in the Basic Latin + Latin-1 Supplement range (U+0000–U+00FF)
    return re.sub(r'[^\u0000-\u00FF]', '', text).strip()

class PCOSReportPDF(FPDF):
    def header(self):
        # Header layout
        self.set_fill_color(240, 240, 245)
        self.rect(0, 0, 210, 35, "F")
        self.set_text_color(50, 50, 100)
        self.set_font("Helvetica", "B", 20)
        self.cell(0, 10, "PCOS TRACKER HEALTH REPORT", ln=True, align="L")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 120)
        self.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}", ln=True, align="L")
        self.ln(12)

    def footer(self):
        # Footer layout
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Confidential Medical Log", align="C")

def generate_pdf_report(user_name: str, symptoms: list, cycles: list) -> bytes:
    pdf = PCOSReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # User Profile Block
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(60, 60, 120)
    safe_name = sanitize_text(user_name or 'PCOS Tracker User')
    pdf.cell(0, 10, f"Patient Profile: {safe_name}", ln=True)
    pdf.set_draw_color(180, 180, 200)
    pdf.line(10, 45, 200, 45)
    pdf.ln(5)
    
    # Section 1: Symptom Averages
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(80, 80, 140)
    pdf.cell(0, 8, "1. Symptom & Lifestyle Summary (Past 30 Logs)", ln=True)
    pdf.ln(2)
    
    if symptoms:
        df_sym = pd.DataFrame(symptoms)
        avg_sleep = df_sym["sleep_hours"].mean()
        avg_exec = df_sym["exercise_minutes"].mean()
        avg_stress = df_sym["stress_level"].mean()
        avg_pain = df_sym["pain_level"].mean()
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(90, 8, f"- Average Sleep Hours: {avg_sleep:.1f} hours/day", ln=False)
        pdf.cell(90, 8, f"- Average Exercise Time: {avg_exec:.1f} minutes/day", ln=True)
        pdf.cell(90, 8, f"- Average Pain Intensity (0-10): {avg_pain:.1f}", ln=False)
        pdf.cell(90, 8, f"- Average Stress Level (1-10): {avg_stress:.1f}", ln=True)
        
        # Mild / Severe logs counts
        hirsutism_severe = len(df_sym[df_sym["hair_growth"] >= 2])
        acne_severe = len(df_sym[df_sym["acne"] >= 2])
        pdf.cell(90, 8, f"- Severe Hirsutism Logs (Mild/Severe): {hirsutism_severe}", ln=False)
        pdf.cell(90, 8, f"- Severe Acne Logs (Mild/Severe): {acne_severe}", ln=True)
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 8, "No daily symptom logs recorded yet.", ln=True)
        
    pdf.ln(5)
    
    # Section 2: Menstrual Cycle History
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(80, 80, 140)
    pdf.cell(0, 8, "2. Menstrual Cycle History Log", ln=True)
    pdf.ln(2)
    
    if cycles:
        # Create table header
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(230, 230, 240)
        pdf.set_text_color(60, 60, 90)
        pdf.cell(45, 8, "Period Start Date", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Period End Date", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Cycle Length (Days)", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Bleeding Days", border=1, fill=True, align="C")
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        
        # Fill table rows
        for cycle in cycles[:8]:  # Show latest 8 cycles
            start = sanitize_text(str(cycle.get("start_date", "N/A")))
            end = sanitize_text(str(cycle.get("end_date", "Active"))) if cycle.get("end_date") else "Active"
            c_len = sanitize_text(str(cycle.get("cycle_length", "N/A"))) if cycle.get("cycle_length") else "N/A"
            p_len = sanitize_text(str(cycle.get("period_length", "N/A"))) if cycle.get("period_length") else "N/A"
            
            pdf.cell(45, 8, start, border=1, align="C")
            pdf.cell(45, 8, end, border=1, align="C")
            pdf.cell(45, 8, c_len, border=1, align="C")
            pdf.cell(45, 8, p_len, border=1, align="C")
            pdf.ln()
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 8, "No menstrual cycle periods logged yet.", ln=True)
        
    pdf.ln(8)
    
    # Section 3: Recommendations Engine
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(80, 80, 140)
    pdf.cell(0, 8, "3. Clinical PCOS Recommendations & Guidance", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    
    clinical_notes = (
        "- Insulin Sensitivity: Managing insulin resistance is fundamental to controlling PCOS. "
        "A low-glycemic, anti-inflammatory diet high in fiber and proteins is highly recommended.\n"
        "- Muscle Mass & Exercise: Combining progressive strength training with moderate cardio "
        "regulates androgen levels and significantly improves metabolic health.\n"
        "- Sleep and Stress: High cortisol triggers androgen production. Sleep at least 7.5 to 8 hours "
        "and implement daily stress management practices (deep breathing, yoga, limits on stimulants)."
    )
    pdf.multi_cell(0, 6, clinical_notes)
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 130)
    pdf.multi_cell(0, 5, "Disclaimer: This document is a generated personal logging report and is not a replacement for professional clinical advice, diagnosis, or treatment. Please consult with a healthcare professional.")
    
    # Output to bytes
    return bytes(pdf.output())
