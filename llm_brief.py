from groq import Groq
import json
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

def generate_brief(metrics):
    """Call Groq API to generate a trading brief from today's metrics"""

    metrics_text = "\n".join([
        f"- {m['metric']}: {m['value']} {m['unit']}"
        for m in metrics
    ])

    prompt = f"""You are a senior European energy market analyst writing a morning brief for a gas and power trading desk.

Today is {date.today().strftime('%d %B %Y')}.

Today's market metrics:
{metrics_text}

Context:
- EU gas storage is significantly below last year's levels at the same date (~51%)
- TTF has sold off sharply this week on a preliminary US-Iran deal that could reopen the Strait of Hormuz
- EU ETS carbon prices are structurally supported by 2026 ETS reform and CBAM implementation
- The clean spark spread indicates whether gas-fired power generation is currently profitable

Write a concise 150-200 word trading brief covering:
1. Gas tightness signal (TTF + storage + LNG send-out)
2. Carbon risk (EUA price + policy context)
3. Power curve implication (spark spread + German DA)
4. Key risk to watch today

Be direct, quantitative, and decision-useful. Write like a trader, not an academic. No bullet points - flowing prose only."""

    print("Calling Groq API for trading brief...")
    print(f"\n--- PROMPT SENT TO LLM ---\n{prompt}\n--------------------------\n")

    client = Groq(api_key="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")

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

    # Log prompt and output
    log = {
        "date": str(date.today()),
        "prompt": prompt,
        "output": brief,
        "model": "llama3-70b-8192",
        "input_tokens": completion.usage.prompt_tokens,
        "output_tokens": completion.usage.completion_tokens
    }

    os.makedirs("output", exist_ok=True)
    with open("output/llm_log.json", "w") as f:
        json.dump(log, f, indent=2)

    print("Logged to output/llm_log.json")
    return brief


if __name__ == "__main__":
    dummy = [
        {"metric": "TTF Front-Month",    "value": 41.46,  "unit": "€/MWh"},
        {"metric": "EU Gas Storage Fill", "value": 45.3,   "unit": "%"},
        {"metric": "EU ETS Carbon (EUA)", "value": 75.43,  "unit": "€/tonne"},
        {"metric": "Clean Spark Spread",  "value": 16.02,  "unit": "€/MWh"},
        {"metric": "German Power DA",     "value": 117.63, "unit": "€/MWh"},
        {"metric": "EU LNG Send-Out",     "value": 3514.6, "unit": "GWh/day"},
    ]
    generate_brief(dummy)