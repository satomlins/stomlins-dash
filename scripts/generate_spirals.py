"""
Generate seasonal spiral charts for stomlins.com/seasonal-spirals.

Run with: uv run python scripts/generate_spirals.py

Outputs:
  public/spirals/github-commits.html     — daily GitHub commit activity
  public/spirals/six-nations.html        — Six Nations Wikipedia pageviews
  public/spirals/skiing.html             — Skiing Wikipedia pageviews
  public/images/seasonal-spirals-demo.png — static PNG for homepage card
"""

from pathlib import Path
import os
import pandas as pd
import plotly.io as pio
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from seasonal_spirals import plot_spiral, plot_spiral_static, fetch_pageviews

load_dotenv()

OUT_HTML = Path("public/spirals")
OUT_IMG = Path("public/images")
OUT_HTML.mkdir(parents=True, exist_ok=True)
OUT_IMG.mkdir(parents=True, exist_ok=True)


def save_chart(fig, filename: str, title: str):
    # Equal margins so the spiral is centred, not cut off
    fig.update_layout(
        width=None,
        height=None,
        margin=dict(l=60, r=60, t=80, b=60),
        autosize=True,
    )
    path = OUT_HTML / filename
    pio.write_html(
        fig,
        file=str(path),
        include_plotlyjs="cdn",
        full_html=False,
        config={"displayModeBar": False},
    )
    print(f"✓ {title} → {path}")


# ── 1. GitHub commits ────────────────────────────────────────────────────────
def fetch_github_commits(username: str) -> pd.Series:
    """
    Fetches daily contribution counts for all years since account creation
    using the GitHub GraphQL API. Requires GITHUB_TOKEN in .env.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not set in .env")

    headers = {"Authorization": f"Bearer {token}"}

    # Get account creation year
    user_resp = requests.get(
        f"https://api.github.com/users/{username}",
        headers=headers,
        timeout=10,
    )
    user_resp.raise_for_status()
    created_at = datetime.fromisoformat(user_resp.json()["created_at"].replace("Z", "+00:00"))
    start_year = created_at.year
    current_year = datetime.now(timezone.utc).year
    print(f"  Account created {start_year}, fetching {start_year}–{current_year}")

    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    records = []
    for year in range(start_year, current_year + 1):
        from_dt = f"{year}-01-01T00:00:00Z"
        to_dt = f"{year}-12-31T23:59:59Z"
        resp = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"username": username, "from": from_dt, "to": to_dt}},
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        weeks = resp.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        for week in weeks:
            for day in week["contributionDays"]:
                records.append({"date": day["date"], "count": day["contributionCount"]})
        print(f"  ✓ {year}")

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    series = df.set_index("date")["count"]
    series.index = pd.DatetimeIndex(series.index)
    return series


print("Fetching GitHub commits for satomlins...")
github_series = fetch_github_commits("satomlins")
fig_github = plot_spiral(
    github_series,
    title="GitHub commits",
    dark_mode=True,
)
save_chart(fig_github, "github-commits.html", "GitHub commits")


# ── 2. Six Nations Wikipedia pageviews ───────────────────────────────────────
print("Fetching Six Nations Wikipedia pageviews...")
six_nations_series = fetch_pageviews("Six_Nations_Championship", start="2016-01-01")
fig_six_nations = plot_spiral(
    six_nations_series,
    title="Six Nations Championship — Wikipedia pageviews",
    dark_mode=True,
)
save_chart(fig_six_nations, "six-nations.html", "Six Nations Wikipedia pageviews")

# Also save as static PNG for homepage
print("Generating homepage PNG...")
fig_static, _ = plot_spiral_static(six_nations_series, title="seasonal-spirals")
fig_static.savefig(str(OUT_IMG / "seasonal-spirals-demo.png"), dpi=150, bbox_inches="tight")
import matplotlib.pyplot as plt
plt.close(fig_static)
print(f"✓ Homepage PNG → {OUT_IMG / 'seasonal-spirals-demo.png'}")


# ── 3. Skiing Wikipedia pageviews ────────────────────────────────────────────
print("Fetching Skiing Wikipedia pageviews...")
skiing_series = fetch_pageviews("Skiing", start="2016-01-01")
fig_skiing = plot_spiral(
    skiing_series,
    title="Skiing — Wikipedia pageviews",
    dark_mode=True,
)
save_chart(fig_skiing, "skiing.html", "Skiing Wikipedia pageviews")


print("\nAll done. Commit public/spirals/ and public/images/ to the repo.")
print("File sizes:")
for f in sorted(OUT_HTML.glob("*.html")):
    print(f"  {f.name}: {f.stat().st_size / 1024:.0f}KB")
