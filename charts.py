import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests
import yfinance as yf
import pandas as pd
from datetime import date
import os
import requests

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
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.label.set_color("white")
        ax.xaxis.label.set_color("white")

        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45, ha="right")
        plt.setp(ax.get_xticklabels(), color='white')
        plt.setp(ax.get_yticklabels(), color='white')

        cutoff=hist.index[-1]-pd.Timedelta(days=30)
        recent= hist[hist.index>= cutoff]
        min_idx=recent["Close"].idxmin()
        min_val=recent['Close'].min()
        ax.annotate("Iran deal\nselloff",xy=(min_idx, min_val),xytext=(min_idx-pd.Timedelta(days=10), min_val+6),color="#ff6b6b",fontsize=9, arrowprops=dict(arrowstyle="->", color="#ff6b6b"),ha="center")

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
    
def chart_storage_vs_lastyear():
    """Chart2: EU gas storage this year vs last year"""
    print("Generating Chart 2: Storage deficit chart...")
    try:
        api_key="91a8dd63fa7af616f006d96cccd17e1b"
        headers={"x-key":api_key}
        from datetime import timedelta
        import datetime

        dates_this_year=[]
        fills_this_year=[]
        dates_last_year=[]
        fills_last_year=[]

        today=date.today()
        for weeks_ago in range(26,0,-1):
            d=today-timedelta(weeks=weeks_ago)
            try: 
                r=requests.get("https://agsi.gie.eu/api", params={"country":"eu","size":1,"date":str(d)}, headers=headers, timeout=8)
                data=r.json()
                if data.get("data"):
                    fill=float(data["data"][0]["full"])
                    dates_this_year.append(d)
                    fills_this_year.append(fill)
            except:
                pass
            
        for d in dates_this_year:
                d_ly=d-timedelta(days=365)
                try:
                    r=requests.get("https://agsi.gie.eu/api", params={"country":"eu","size":1,"date":str(d_ly)}, headers=headers, timeout=8)
                    data=r.json()
                    if data.get("data"):
                        fill=float(data["data"][0]["full"])
                        dates_last_year.append(d)
                        fills_last_year.append(fill)
                except:
                    pass

        fig,ax=plt.subplots(figsize=(12,5))

        BG       = "#0a0e1a"
        COL_2026 = "#f0a500"   # amber — 2026 this year
        COL_2025 = "#c0c0c0"   # silver — 2025 last year
        COL_DEFICIT = "#f0a500"
        COL_TARGET  = "#ff4444"

        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)

        current_deficit=0
        if fills_this_year and fills_last_year:
            min_len=min(len(fills_this_year), len(fills_last_year))
            current_deficit=round(fills_last_year[min_len-1]-fills_this_year[min_len-1],1)
        ax.plot(dates_this_year, fills_this_year, color=COL_2026, linewidth=2.5, label=f"2026 (this year) - current:{fills_this_year[-1]:.1f}%", zorder=3)
        ax.plot(dates_last_year, fills_last_year, color=COL_2025, linewidth=2.0, linestyle="--", label=f"2025 (last year) - current:{fills_last_year[-1]:.1f}%", zorder=2)

        min_len = min(len(fills_this_year), len(fills_last_year))
        if min_len > 0:
            
            ax.fill_between(
                dates_this_year[:min_len],
                fills_this_year[:min_len],
                fills_last_year[:min_len],
                alpha=0.35,
                color=COL_DEFICIT,
                label="Storage deficit")
            
            current_this = fills_this_year[-1]
            current_last = fills_last_year[-1]
            current_deficit = round(current_last - current_this, 1)
            current_date = dates_this_year[-1]
            if current_deficit > 0:
                ax.annotate(
                    f"Current deficit: {current_deficit}pp vs 2025",
                    xy=(current_date, current_this),
                    xytext=(current_date - pd.Timedelta(days=30), current_this - 10),
                    color="white", fontsize=10,
                    arrowprops=dict(arrowstyle="->", color="white"),
                    ha="center")

            ax.axhline(y=80, color=COL_TARGET, linewidth=1.2, linestyle=":", label="EU 80% winter target")
            
            ax.set_title("EU Gas Storage:2026 vs 2025 - Injection Season Deficit", color="white", fontsize=14, pad=15)
            ax.set_ylabel("Storage Fill(%)", color="white")
            ax.set_ylim(0,105)
            
            for spine in ["bottom", "left"]:
                ax.spines[spine].set_color("#444455")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.tick_params(axis='x',color="white")
            ax.tick_params(axis='y',color="white")
            plt.setp(ax.get_xticklabels(), color='white')
            plt.setp(ax.get_yticklabels(), color='white')
            ax.yaxis.label.set_color("white")

            import matplotlib.dates as mdates
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=3))
            plt.xticks(rotation=45, ha="right")

            ax.legend(facecolor="#1a1a2e", labelcolor="white",fontsize=9)
            plt.tight_layout()

            path=os.path.join(OUTPUT_DIR,"chart2_storage_percentage.png")
            plt.savefig(path,dpi=150, facecolor="#0d1117")
            plt.close()
            print(f"Saved:{path}")
            return path
    except Exception as e:
        print(f"Chart 2 error:{e}")
        return None

def generate_all_charts(metrics):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        chart1= chart_ttf_history()
        chart2= chart_storage_vs_lastyear()
        return chart1, chart2


if __name__=="__main__":
    chart_storage_vs_lastyear()
    print("\nDone! Check your output/folder for the charts")