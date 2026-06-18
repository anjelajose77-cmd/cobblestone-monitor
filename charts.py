import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import yfinance as yf
import pandas as pd
from datetime import date
import os

OUTPUT_DIR = "output"
def chart_ttf_history():
    """Chart 1: TTF gas price - last months"""
    print("Generating Chart 1: TTF price history...")
    try:
        ttf = yf.Ticker("TTF=F")
        hist = ttf.history(period="3mo")
        hist.index = hist.index.tz_localize(None)
        fig,ax = plt. subplots(figsize=(12,5))
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#0d1117")
        ax.plot(hist.index, hist["Close"], color="#00d4aa", linewidth=2, label="TTF Front-Month")
        ax.fill_between(hist.index, hist["Close"], alpha=0.15, color="#0054da")
        ax.set_title("TTF natural Gas - 3 Month price History", color ="white", fontsize=14, pad = 15)
        ax.set_ylabel("€/MWh", color="white")
        ax.tick_params(color="white")
        ax.spines["bottom"].set_color("#444")
        ax.spines["left"].set_color("#444")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.label.set_color("white")
        ax.xaxis.label.set_color("white")

        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45, ha="right")

        cutoff=hist.index[-1]-pd.Timedelta(days=30)
        recent= hist[hist.index>= cutoff]
        min_idx=recent["Close"].idxmin()
        min_val=recent['Close'].min()
        ax.annotate("Iran dael\nselloff",xy=(min_idx, min_val),xytext=(min_idx-pd.Timedelta(days=10), min_val+6),color="#ff6b6b",fontsize=9, arrowprops=dict(arrowstyle="->", color="#ff6b6b"),ha="center")

        ax.legend(facecolor="#1a1a2e",labelcolor="white")
        ax.set_xlim(left=hist.index[0], right=hist.index[-1]+pd.Timedelta(days=5))
        plt.tight_layout()

        path=os.path.join(OUTPUT_DIR,"chart1_ttf_history.png")
        plt.savefig(path,dpi=150, facecolor="#0d1117")
        plt.close()
        print(f"Saved:{path}")
        return path
    except Exception as e:
        print(f"Chart 1 error:{e}")
        return None
    
def chart_metrics_dashboard(metrics):
    """Chart2: Daily metrics dashboard snapshot"""
    print("Generating Chart 2: Metrics dashboard...")
    try: 
        fig,axes=plt.subplots(2,3,figsize=(14,7))
        fig.patch.set_facecolor("#0d1117")
        fig.suptitle(f"European Cross-Commodity Monitor - {date.today().strftime('%d %b %Y')}", color="white", fontsize=14, y=1.01)
        colors=["#00d4aa","#4ecdc4", "#45b7d1", "#f7dc6f", "#ff6b9d","#c39bd3"]
        units=["€/MWh","%","€/tonne","€/MWh","€/MWh","GWh/day"]

        for i, (ax,m,color) in enumerate(zip(axes.flat,metrics,colors)):
            ax.set_facecolor("#1a1a2e")
            for spine in ax.spines.values():
                spine.set_color("#333")

            val=m["value"]
            label=m["metric"]
            unit=m["unit"]
            status=m["status"]

            display=str(val) if val is not None else "N/A"
            ax.text(0.5,0.55, display, transform=ax.transAxes, fontsize=26, fontweight="bold", color=color, ha="center", va="center")
            ax.text(0.5,0.25,unit, transform=ax.transAxes, fontsize=11, color="#888", ha="center",va="center")
            ax.text(0.5,0.82, label, transform=ax.transAxes, fontsize=10, color="white", ha="center", va="center", fontweight="bold")

            dot_color="#00d4aa" if status =="ok" else "#ff6b6b"
            ax.text(0.92,0.92,"●", transform=ax.transAxes,fontsize=10, color=dot_color,ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])
        plt.tight_layout()
        path=os.path.join(OUTPUT_DIR, "chart2_dashboard.png")
        plt.savefig(path, dpi=150, facecolor="#0d1117", bbox_inches="tight")
        plt.close()
        print(f"Saved:{path}")
        return path
    except Exception as e:
        print(f"Chart 2 error:{e}")
        return None
def generate_all_charts(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    chart1= chart_ttf_history()
    chart2=chart_metrics_dashboard(metrics)
    return chart1, chart2
if __name__=="__main__":

    dummy=[{"metric": "TTF Front-Month",    "value": 41.46,  "unit": "€/MWh",    "status": "ok"},
        {"metric": "EU Gas Storage Fill", "value": 45.3,   "unit": "%",         "status": "ok"},
        {"metric": "EU ETS Carbon (EUA)", "value": 75.43,  "unit": "€/tonne",  "status": "ok"},
        {"metric": "Clean Spark Spread",  "value": 16.02,  "unit": "€/MWh",    "status": "ok"},
        {"metric": "German Power DA",     "value": 117.63, "unit": "€/MWh",    "status": "ok"},
        {"metric": "EU LNG Send-Out",     "value": 3514.6, "unit": "GWh/day",  "status": "ok"},
    ]
    generate_all_charts(dummy)
    print("\nDone! Check your output/folder for the charts")