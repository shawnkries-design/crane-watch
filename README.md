# Crane Watch — Glasgow, Kentucky

iPhone-friendly Sandhill crane activity dashboard for Glasgow and Barren River Lake. It uses recent public eBird observations (not real-time GPS tracking). The largest reported flock of 500+ birds, or 100+ birds reported at three separate sites in the past day, triggers high activity. The GitHub Actions monitor checks approximately hourly and sends no more than one ntfy notification per 24 hours.

## Activate — one-time setup

1. Request your free personal eBird API key at https://ebird.org/api/keygen
2. In this GitHub repository go to **Settings → Secrets and variables → Actions → New repository secret**. Add a secret named `EBIRD_API_KEY` and paste your key as the value. Never put a key in public files.
3. On your iPhone install **ntfy** from https://apps.apple.com/us/app/ntfy/id1625396347 . Subscribe to an unpredictable topic of at least 24 randomly chosen characters using the default `ntfy.sh` server; allow notifications. Public ntfy topics are not authenticated, so do not use a simple name or send private messages.
4. Add another GitHub Actions secret named `NTFY_TOPIC`, using exactly the same topic as your iPhone subscription.
5. Under **Settings → Pages**, choose **GitHub Actions** as the Build and deployment source. Under **Settings → Actions → General → Workflow permissions**, give GitHub Actions **Read and write permissions** if needed to preserve history in `site/data.json`.
6. Open **Actions → Monitor cranes & publish app → Run workflow**. When it finishes successfully, open https://shawnkries-design.github.io/crane-watch/ .
7. On your iPhone, open the Pages URL in **Safari**, then Share → **Add to Home Screen**.

The dashboard won't be live until these steps are completed.

## Configuration

`.github/workflows/monitor.yml` sets `ALERT_THRESHOLD: '500'` and `RADIUS_KM: '25'`. The monitoring circles cover Glasgow and Barren River Lake; the overlapping observations are deduplicated. An alert is based on recent **reported** flock sizes and does not mean birds are currently present or that the annual peak has arrived.

GitHub Actions scheduled tasks can run late and can be disabled for inactive public repositories. Public eBird reports may be delayed or incomplete. Never treat the map or reports as a live wildlife census. The GitHub Pages site is public.