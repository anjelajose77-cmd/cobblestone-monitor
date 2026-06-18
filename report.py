from fpdf import FPDF
from datetime import date
import os

OUTPUT_DIR = "output"

class TradingReport(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, "COBBLESTONE ENERGY - EUROPEAN CROSS-COMMODITY MONITOR", align="L")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, date.today().strftime("%d %B %Y"), align="R")
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Automated monitor — Anjela Jose | Page {self.page_no()}", align="C")


def generate_report(metrics, brief, chart1_path, chart2_path):
    print("Generating PDF report...")

    pdf = TradingReport()
    pdf.add_font("DejaVu","","venv/Lib/site-packages/fpdf/fonts/DejaVuSnasCondensed.ttf")
    pdf.add_font("DejaVu","", "venv/Lib/site-packages/fpdf/fonts/DejaVuSansCondensed-Bold.ttf")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- TITLE ---
    pdf.set_font("DejaVu", "B", 16)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 10, "European Cross-Commodity Risk Pack", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 7, "Gas + Carbon -> Power Curve Implications", ln=True)
    pdf.ln(4)

    # --- DIVIDER ---
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # --- METRICS TABLE ---
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "Today's Monitor Metrics", ln=True)
    pdf.ln(2)

    # Table header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(80, 7, "Metric", border=1, fill=True)
    pdf.cell(35, 7, "Value", border=1, fill=True, align="C")
    pdf.cell(35, 7, "Unit", border=1, fill=True, align="C")
    pdf.cell(40, 7, "Status", border=1, fill=True, align="C")
    pdf.ln()

    # Table rows
    pdf.set_font("DejaVu", "", 9)
    fill = False
    for m in metrics:
        pdf.set_fill_color(250, 250, 250) if fill else pdf.set_fill_color(255, 255, 255)
        status = m["status"]
        val = str(m["value"]) if m["value"] is not None else "N/A"

        pdf.set_text_color(20, 20, 20)
        pdf.cell(80, 6, m["metric"], border=1, fill=True)
        pdf.cell(35, 6, val, border=1, fill=True, align="C")
        pdf.cell(35, 6, m["unit"], border=1, fill=True, align="C")

        # Colour status green/orange
        if status == "ok":
            pdf.set_text_color(0, 140, 0)
        else:
            pdf.set_text_color(200, 100, 0)
        pdf.cell(40, 6, "ok" if status == "ok" else "fallback", border=1, fill=True, align="C")
        pdf.set_text_color(20, 20, 20)
        pdf.ln()
        fill = not fill

    pdf.ln(6)

    # --- AI TRADING BRIEF ---
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "AI-Generated Trading Brief", ln=True)
    pdf.ln(2)
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 6, brief)
    pdf.ln(4)

    # --- CHART 1 ---
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "Chart 1 - TTF Natural Gas: 3 Month Price History", ln=True)
    pdf.ln(2)
    if chart1_path and os.path.exists(chart1_path):
        pdf.image(chart1_path, x=10, w=185)
    pdf.ln(4)

    # --- CHART 2 ---
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "Chart 2 - Daily Metrics Dashboard", ln=True)
    pdf.ln(2)
    if chart2_path and os.path.exists(chart2_path):
        pdf.image(chart2_path, x=10, w=185)
    pdf.ln(6)

    # --- METHODOLOGY NOTE ---
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 7, "Data Sources & Methodology", ln=True)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(80, 80, 80)
    sources = [
        "TTF Front-Month: Yahoo Finance (TTF=F) via yfinance",
        "EU Gas Storage Fill: GIE AGSI+ API (agsi.gie.eu)",
        "EU ETS Carbon (EUA): Yahoo Finance (CO2.L) via yfinance",
        "Clean Spark Spread: Derived — Power DA - (TTF x heat rate / 3.6) - (EUA x 0.202)",
        "German Power DA: Energy-Charts API (api.energy-charts.info)",
        "EU LNG Send-Out: GIE ALSI+ API (alsi.gie.eu)",
        "Trading Brief: LLM-generated via Groq API (llama-3.3-70b-versatile)",
    ]
    for s in sources:
        pdf.cell(0, 6, f"  • {s}", ln=True)

    # --- SAVE ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"output/cobblestone_monitor_{date.today().strftime('%Y%m%d')}.pdf"
    pdf.output(filename)
    print(f"  PDF saved: {filename}")
    return filename


if __name__ == "__main__":
    # Test run
    from data_ingestion import get_all_metrics
    from charts import generate_all_charts
    from llm_brief import generate_brief

    metrics = get_all_metrics()
    chart1, chart2 = generate_all_charts(metrics)
    brief = generate_brief(metrics)
    generate_report(metrics, brief, chart1, chart2)
    print("Done!")