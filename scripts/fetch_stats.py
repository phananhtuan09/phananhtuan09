"""Fetch last-year GitHub activity for the profile card and write it as JSON.

Usage: GH_TOKEN=... python scripts/fetch_stats.py <login> data/stats.json
"""
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

API = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests(states: MERGED) { totalCount }
    contributionsCollection {
      totalRepositoriesWithContributedCommits
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false) { totalCount }
  }
}
"""


def graphql(token, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        body = json.load(res)
    if body.get("errors"):
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def longest_streak(days):
    best = run = 0
    for day in days:
        run = run + 1 if day["contributionCount"] > 0 else 0
        best = max(best, run)
    return best


def current_streak(days):
    # Today may have no contributions yet, so a streak ending yesterday still counts.
    counts = [d["contributionCount"] for d in days]
    if counts and counts[-1] == 0:
        counts.pop()
    run = 0
    for c in reversed(counts):
        if c == 0:
            break
        run += 1
    return run


def main():
    login, out = sys.argv[1], Path(sys.argv[2])
    token = os.environ["GH_TOKEN"]

    user = graphql(token, {"login": login})

    cc = user["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    stats = {
        "season": date.today().year,
        "xp": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "issues": cc["totalIssueContributions"],
        "repos": user["repositories"]["totalCount"],
        "longest_streak": longest_streak(days),
        # Extra stats the card can show instead of the ones above.
        "current_streak": current_streak(days),
        "active_days": sum(1 for d in days if d["contributionCount"] > 0),
        "repos_contributed": cc["totalRepositoriesWithContributedCommits"],
        "merged_prs_all_time": user["pullRequests"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "years_on_github": date.today().year - int(user["createdAt"][:4]),
        "sample": False,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
