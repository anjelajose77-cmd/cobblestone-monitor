import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
import os
from dotenv import load_dotenv
load_dotenv()

OUTPUT_DIR = "output"


def chart_ttf_history():
    """Chart 1: TTF gas price - last 3 months"""
    print("Generating Chart 1: TTF price history...")
    try:
        ttf = yf.Ticker("TTF=F")
        hist = ttf.history(period="3mo")
        hist.index = hist.index.tz_localize(None)

        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#0d1117")

        ax.plot(hist.index, hist["Close"], color="#00d4aa", linewidth=2, label="TTF Front-Month")
        ax.fill_between(hist.index, hist["Close"], alpha=0.15, color="#00d4aa")

        ax.set_title("TTF Natural Gas - 3 Month Price History", color="white", fontsize=14, pad=15)
        ax.set_ylabel("EUR/MWh", color="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.label.set_color("white")
        ax.xaxis.label.set_color("white")
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        plt.setp(ax.get_xticklabels(), color='white')
        plt.setp(ax.get_yticklabels(), color='white')

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.xticks(rotation=45, ha="right")

        # Calculate stats
        high_3m = round(hist["Close"].max(), 2)
        low_3m = round(hist["Close"].min(), 2)
        today_price = round(hist["Close"].iloc[-1], 2)
        yday_price = round(hist["Close"].iloc[-2], 2)
        pct_change = round((today_price - yday_price) / yday_price * 100, 2)
        change_sign = "+" if pct_change > 0 else ""

        ax.plot(hist.index, hist["Close"], color="#00d4aa", linewidth=2,
                label=f"TTF Front-Month  |  Today: {today_price}  |  {change_sign}{pct_change}% vs yday  |  3M High: {high_3m}  |  3M Low: {low_3m}")
        ax.fill_between(hist.index, hist["Close"], alpha=0.15, color="#00d4aa")

        ax.legend(facecolor="#1a1a2e", labelcolor="white", fontsize=8)

  
        ax.legend(facecolor="#1a1a2e", labelcolor="white")
        ax.set_xlim(left=hist.index[0], right=hist.index[-1] + pd.Timedelta(days=5))
        plt.tight_layout()

        path = os.path.join(OUTPUT_DIR, "chart1_ttf_history.png")
        plt.savefig(path, dpi=150, facecolor="#0d1117")
        plt.close()
        print(f"  Saved: {path}")
        return path

    except Exception as e:
        print(f"  Chart 1 error: {e}")
        return None


def chart_storage_vs_lastyear():
    """Chart 2: EU gas storage this year vs last year"""
    print("Generating Chart 2: Storage deficit chart...")
    try:
        api_key = os.getenv("GIE_API_KEY")
        headers = {"x-key": api_key}

        dates_this_year = []
        fills_this_year = []
        dates_last_year = []
        fills_last_year = []

        today = date.today() - timedelta(days=2)

        for weeks_ago in range(26, 0, -1):
            d = today - timedelta(weeks=weeks_ago)
            try:
                r = requests.get(
                    "https://agsi.gie.eu/api",
                    params={"country": "eu", "size": 1, "date": str(d)},
                    headers=headers, timeout=8
                )
                data = r.json()
                if data.get("data"):
                    fill = float(data["data"][0]["full"])
                    dates_this_year.append(d)
                    fills_this_year.append(fill)
            except:
                pass

        print(f"  Data points this year: {len(fills_this_year)}")

        for d in dates_this_year:
            d_ly = d - timedelta(days=365)
            try:
                r = requests.get(
                    "https://agsi.gie.eu/api",
                    params={"country": "eu", "size": 1, "date": str(d_ly)},
                    headers=headers, timeout=8
                )
                data = r.json()
                if data.get("data"):
                    fill = float(data["data"][0]["full"])
                    dates_last_year.append(d)
                    fills_last_year.append(fill)
            except:
                pass

        print(f"  Data points last year: {len(fills_last_year)}")

        if not fills_this_year or not fills_last_year:
            print("  No data returned - check GIE_API_KEY in .env")
            return None

        BG = "#0a0e1a"
        COL_2026 = "#00d4aa"
        COL_2025 = "#c0c0c0"
        COL_TARGET = "#ff4444"

        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)

        min_len = min(len(fills_this_year), len(fills_last_year))
        current_deficit = round(fills_last_year[min_len - 1] - fills_this_year[min_len - 1], 1)

        ax.plot(dates_this_year, fills_this_year, color=COL_2026,
                linewidth=2.5,
                label=f"2026 (this year)  |  current: {fills_this_year[-1]:.1f}%",
                zorder=3)
        ax.plot(dates_last_year, fills_last_year, color=COL_2025,
                linewidth=2.0, linestyle="--",
                label=f"2025 (last year)  |  current: {fills_last_year[-1]:.1f}%",
                zorder=2)

        ax.fill_between(
            dates_this_year[:min_len],
            fills_this_year[:min_len],
            fills_last_year[:min_len],
            alpha=0.35, color=COL_2026,
            label=f"Storage deficit  |  {current_deficit}pp below 2025"
        )

        ax.axhline(y=80, color=COL_TARGET, linewidth=1.2,
                   linestyle=":", label="EU 80% winter target")

        ax.set_title("EU Gas Storage: 2026 vs 2025 - Injection Season Deficit",
                     color="white", fontsize=14, pad=15)
        ax.set_ylabel("Storage Fill (%)", color="white")
        ax.set_ylim(0, 105)
        ax.spines["bottom"].set_color("#444455")
        ax.spines["left"].set_color("#444455")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        plt.setp(ax.get_xticklabels(), color='white')
        plt.setp(ax.get_yticklabels(), color='white')
        ax.yaxis.label.set_color("white")

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=3))
        plt.xticks(rotation=45, ha="right")

        ax.legend(facecolor="#1a1a2e", labelcolor="white", fontsize=9)
        plt.tight_layout()

        path = os.path.join(OUTPUT_DIR, "chart2_storage_deficit.png")
        plt.savefig(path, dpi=150, facecolor="#0d1117")
        plt.close()
        print(f"  Saved: {path}")
        return path

    except Exception as e:
        print(f"  Chart 2 error: {e}")
        return None


def generate_all_charts(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    chart1 = chart_ttf_history()
    chart2 = chart_storage_vs_lastyear()
    return chart1, chart2


if __name__ == "__main__":
    generate_all_charts([])
    print("\nDone! Check your output/ folder for the charts.")