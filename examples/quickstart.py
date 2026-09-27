"""Open jobs of the companies you name, in one HTTP request, saved to jobs.csv.

Uses Live Jobs HTTP API, a hosted Actor on Apify that answers each GET or
POST request with the jobs, from Greenhouse, Lever, Ashby, Workday and 18
more job boards.

Install: pip install -r requirements.txt
Run:     APIFY_TOKEN=<YOUR_APIFY_TOKEN> python quickstart.py [company ...]

A company can be a job board link, a website or a name, such as
https://boards.greenhouse.io/stripe, linear.app or palantir.
Your token is in Apify Console > Settings > API & Integrations.
Price: $0.045 per company, up to 1,000 of its open jobs included,
plus the Apify platform usage of the request.
"""

import csv
import os
import sys

import requests

API_URL = "https://conserving-celerytop--live-jobs-http-api.apify.actor/"
DEFAULT_COMPANIES = ["stripe", "linear.app", "https://jobs.ashbyhq.com/openai"]
COLUMNS = [
    "company", "ats", "title", "department", "location", "countryCode", "workplaceType",
    "seniority", "jobFunction", "salaryMin", "salaryMax", "salaryCurrency", "salaryPeriod",
    "postedAt", "url",
]


def main() -> None:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first, for example: APIFY_TOKEN=<YOUR_APIFY_TOKEN> python quickstart.py")

    body = {
        "companies": sys.argv[1:] or DEFAULT_COMPANIES,  # up to 500 per request
        "postedSince": "30 days",
    }
    # A POST with a JSON body. Each request has up to 240 seconds on the server.
    resp = requests.post(
        API_URL,
        json=body,
        headers={"Authorization": f"Bearer {token}"},
        timeout=300,
    )
    if resp.status_code != 200:
        sys.exit(f"HTTP {resp.status_code}: {resp.text[:500]}")
    data = resp.json()

    for c in data["companies"]:
        print(f"{c.get('company')}: {c.get('companyStatus')}")
    if data.get("spendingLimitReached"):
        print("Your Apify spending limit stopped the request early.")

    with open("jobs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data["jobs"])

    print(f"Saved {len(data['jobs'])} jobs to jobs.csv")


if __name__ == "__main__":
    main()
