from groq import Groq
import json
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_market_context(client):
    """Fetch live energy market headlines via NewsAPI"""
    print("Fetching live market context...")
    try:
        import requests
        news_key = os.getenv("NEWS_API_KEY")
        if not news_key:
            raise ValueError("No NEWS_API_KEY in .env")

        queries = ["European gas TTF", "EU ETS carbon price", "European power price"]
        headlines = []

        for q in queries:
            r = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": q,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 3,
                    "apiKey": news_key
                },
                timeout=10
            )
            articles = r.json().get("articles", [])
            for a in articles:
                headlines.append(f"- {a['publishedAt'][:10]}: {a['title']} ({a['source']['name']})")

        context = "\n".join(headlines[:9])
        print(f"  Fetched {len(headlines)} headlines")
        return context

    except Exception as e:
        print(f"  News fetch failed ({e}) - metrics only mode")
        return ""


def generate_brief(metrics):
    """Call Groq API to generate a trading brief from live metrics + live context"""

    metrics_text = "\n".join([
        f"- {m['metric']}: {m['value']} {m['unit']}"
        for m in metrics
    ])

    client = Groq(api_key=GROQ_API_KEY)

    
    market_context = get_market_context(client)

    if market_context:
        context_section = f"""Latest market news (auto-fetched today):
{market_context}"""
    else:
        context_section = """Note: Live news unavailable - base analysis on metrics only."""

    prompt = f"""You are a senior European energy market analyst writing a morning brief for a gas and power trading desk.

Today is {date.today().strftime('%d %B %Y')}.

Today's market metrics (live data):
{metrics_text}

{context_section}

Write a concise 150-200 word trading brief covering:
1. Gas tightness signal (TTF + storage + LNG send-out)
2. Carbon risk (EUA price + policy context)
3. Power curve implication (spark spread + German DA)
4. Key risk to watch today

Be direct, quantitative, and decision-useful. Write like a trader, not an academic. No bullet points - flowing prose only."""

    print("Generating trading brief...")
    print(f"\n--- PROMPT SENT TO LLM ---\n{prompt}\n--------------------------\n")

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024
    )

    brief = completion.choices[0].message.content

    print("--- LLM OUTPUT ---")
    print(brief)
    print("------------------\n")

    log = {
        "date": str(date.today()),
        "market_context": market_context,
        "prompt": prompt,
        "output": brief,
        "model": "llama-3.3-70b-versatile",
        "input_tokens": completion.usage.prompt_tokens,
        "output_tokens": completion.usage.completion_tokens
    }

    os.makedirs("output", exist_ok=True)
    with open("output/llm_log.json", "w") as f:
        json.dump(log, f, indent=2)

    print("Logged to output/llm_log.json")
    return brief


if __name__ == "__main__":
    from data_ingestion import get_all_metrics
    metrics = get_all_metrics()
    generate_brief(metrics)