# Live Jobs HTTP API examples: company jobs in one GET request

Get the open jobs of the companies you name in one GET or POST request, from Greenhouse, Lever, Ashby, Workday and 18 more job boards. No run to start, no dataset to fetch: the jobs are in the response.

The API is [Live Jobs HTTP API](https://apify.com/conserving_celerytop/live-jobs-http-api), a hosted Actor on Apify that runs as a live HTTP server. This repo holds curl and Python examples and MCP setup for 5 AI clients. There is no scraper code here. The example code is MIT licensed.

## What it returns

Send job board links, company websites or names, up to 500 per request. The response is one JSON object:

```json
{
  "companies": [
    {"company": "stripe", "companyStatus": "ok", "charged": true}
  ],
  "jobs": [
    {
      "company": "stripe",
      "ats": "greenhouse",
      "title": "Backend Engineer, Payments",
      "department": "Engineering",
      "location": "Seattle, WA",
      "workplaceType": "hybrid",
      "salaryMin": 180000,
      "salaryMax": 250000,
      "salaryCurrency": "USD",
      "postedAt": "2026-09-22T16:40:00.000Z",
      "url": "https://..."
    }
  ],
  "closedJobs": [],
  "spendingLimitReached": false
}
```

The fragment above is shortened. Every job has the same fields on all 22 boards, the same as in [ATS Jobs API](https://apify.com/conserving_celerytop/live-career-page-jobs-api). `companies` has one status per company, such as `ok`, `no_matching_jobs` or `not_found`. `GET /openapi.json` describes every parameter and field, for free.

## curl

You need an Apify account and its API token (Apify Console > **Settings** > **API & Integrations**).

```bash
export APIFY_TOKEN=<YOUR_APIFY_TOKEN>

curl -H "Authorization: Bearer $APIFY_TOKEN" \
  "https://conserving-celerytop--live-jobs-http-api.apify.actor/?companies=stripe,linear.app,https://jobs.ashbyhq.com/openai&department=engineering&postedSince=7%20days"
```

A POST to the same URL with a JSON body also works:

```bash
curl -X POST -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  "https://conserving-celerytop--live-jobs-http-api.apify.actor/" \
  -d '{"companies": ["https://boards.greenhouse.io/stripe", "https://jobs.lever.co/palantir"], "remoteOnly": true}'
```

## Python quick start

This API is a plain HTTP endpoint, so the quick start uses `requests`.

```bash
pip install requests
```

```python
import os
import requests

resp = requests.get(
    "https://conserving-celerytop--live-jobs-http-api.apify.actor/",
    params={"companies": "stripe,linear.app,https://jobs.ashbyhq.com/openai", "postedSince": "7 days"},
    headers={"Authorization": f"Bearer {os.environ['APIFY_TOKEN']}"},
    timeout=300,
)
for job in resp.json()["jobs"]:
    print(job["company"], "|", job["title"], "|", job["location"], "|", job["url"])
```

The full script is [examples/quickstart.py](examples/quickstart.py): it takes companies as arguments, prints each company's status and saves the jobs to `jobs.csv`.

```bash
pip install -r examples/requirements.txt
python examples/quickstart.py stripe figma https://jobs.lever.co/palantir
```

To start a normal Apify run with the official `apify-client` package instead, use [ATS Jobs API](https://apify.com/conserving_celerytop/live-career-page-jobs-api): same data, no platform usage on top. Its Python quick start is in the repo [ats-jobs-api-python](https://github.com/donmangudata-ops/ats-jobs-api-python).

## Parameters

Only `companies` is needed. In a URL, separate several values with commas.

| Parameter | Example |
|---|---|
| `companies` | `stripe,linear.app,https://jobs.lever.co/palantir` |
| `companyLists` | `ai-companies`, `tech-companies`, `remote-first` or `europe-tech` |
| `titleIncludes`, `titleExcludes` | `data engineer` |
| `department` | `engineering,sales` |
| `location`, `locationExcludes` | `London` (repeat the parameter for several places) |
| `workplaceTypes` | `remote,hybrid` |
| `postedSince`, `postedBefore` | `7 days` |
| `hasSalary`, `minAnnualSalary` | `120000` |
| `includeDescription` | `true` |
| `outputMode` | `jobs`, `companies` (one summary per company) or `both` |
| `onlyNewJobs`, `monitorName` | `true`: only jobs new or closed since your last check |
| `maxJobsPerCompany` | `20` |

Each request has 240 seconds. Companies not read by then come back as `skipped_time_limit` and are free, so send fewer per request.

## Use it as an MCP tool in Claude, Cursor, VS Code or ChatGPT

Apify hosts the MCP server. This URL adds only this Actor as a tool:

```
https://mcp.apify.com/?tools=fetch-actor-details,conserving_celerytop/live-jobs-http-api
```

An agent that calls it starts a normal run, which charges the events plus Apify platform usage. For agents, the same URL with `conserving_celerytop/live-career-page-jobs-api` in place of `conserving_celerytop/live-jobs-http-api` gives the same data with no platform usage on top. On first use, the client opens a browser window to sign in to Apify (OAuth).

**Claude Code**

```bash
claude mcp add --transport http live-jobs-http-api "https://mcp.apify.com/?tools=fetch-actor-details,conserving_celerytop/live-jobs-http-api"
```

Then run `/mcp` in Claude Code and sign in.

**Claude (desktop app and claude.ai)**

**Settings** > **Connectors** > **Add custom connector**. Name: `Live Jobs HTTP API`. URL: the URL above.

**Cursor** (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "live-jobs-http-api": {
      "url": "https://mcp.apify.com/?tools=fetch-actor-details,conserving_celerytop/live-jobs-http-api"
    }
  }
}
```

**VS Code** (`.vscode/mcp.json`)

```json
{
  "servers": {
    "live-jobs-http-api": {
      "type": "http",
      "url": "https://mcp.apify.com/?tools=fetch-actor-details,conserving_celerytop/live-jobs-http-api"
    }
  }
}
```

**ChatGPT** (Developer mode on)

**Settings** > **Apps & Connectors** > **Create**. MCP Server URL: the URL above. Authentication: OAuth.

To use a token instead of OAuth, send the header `Authorization: Bearer <YOUR_APIFY_TOKEN>`.

## Pricing

$0.01 per company, including up to 1,000 of its open jobs ($0.0095 on Starter, $0.009 on Scale, $0.008 on Business), plus the Apify platform usage of the request, because the Actor runs as a live server. Each further 1,000 jobs of the same company costs $0.01, a later check with `onlyNewJobs` $0.002 per 1,000 open jobs, and descriptions on Workday, Eightfold and 8 other boards $0.01 per 200 jobs. Invalid, unsupported, duplicate and skipped entries are free. For many companies or daily schedules, [ATS Jobs API](https://apify.com/conserving_celerytop/live-career-page-jobs-api) costs less. These are the prices in September 2026; the [Store page](https://apify.com/conserving_celerytop/live-jobs-http-api) has the current ones.

## Related

- [ATS Jobs API](https://apify.com/conserving_celerytop/live-career-page-jobs-api): the same data as a normal Apify run, with schedules and new-job alerts.
- [Tech Jobs Search](https://apify.com/conserving_celerytop/tech-jobs-search): search the open jobs of 574 tech, AI and remote-first companies by keyword, $1 per 1,000 matching jobs.

Found a problem? Open an issue on the **Issues** tab of the [Actor's page](https://apify.com/conserving_celerytop/live-jobs-http-api).

## Not affiliated

This repo and the Actor are not affiliated with or endorsed by Greenhouse, Lever, Ashby, Workday, Eightfold or any other job board. Their names are trademarks of their owners. The Actor reads only job postings that companies publish on public job boards, with no login.

## License

MIT. See [LICENSE](LICENSE). Made by Don Mangu.
