import os
from datetime import date
from data_ingestion import get_all_metrics
from charts import generate_all_charts
from llm_brief import generate_brief

def run_monitor():
    print("="*55)
    print(" COBBLESTONE ENERGY - EUROPEAN CROSS-COMMODITY MONITOR")
    print(f" {date.today().strftime('%A,%d %B %Y')}")
    print("="*55)

    print("\n[1/3] PULLING MARKET DATA...")
    metrics= get_all_metrics

    print("\n[2/3] GENERATING CHARTS...")
    chart1, chart2 = generate_all_charts(metrics)

    print("\n[3/3] GENERATING AI TRADING BRIEF...")
    brief= generate_brief(metrics)

    print ("\n"+"="*55)
    print("TODAY'S TRADING BREIF")
    print("="*55)
    print(brief)

print("\n"+"="*55)
print("OUTPUT FILES")
print(f"Chart1: output/chart1_ttf_history.png")
print(f"Chart2: output/chart2_dashboard.png")
print(f" LLM Log: output/llm_log.json")
print("="*55)
print("\nMinitor complete!")

if __name__=="__main__":
    run_monitor()


