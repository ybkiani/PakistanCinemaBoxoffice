# PAK CINEMA — automatic Pakistan cinema guide

A static GitHub Pages front-end with a serverless daily data refresh powered by GitHub Actions.

## Automatic updates
`.github/workflows/daily-update.yml` runs every day at **08:15 Pakistan Standard Time** and can also be run manually from **GitHub → Actions → Daily Pakistan cinema update → Run workflow**.

The updater checks supported public cinema listing pages, rebuilds `data/movies.json`, validates the JSON, and commits only when data changes. A fail-safe preserves the previous healthy section if a source changes markup or temporarily fails.

## Publish
1. Create a public GitHub repository.
2. Upload **all files and folders**, including `.github`.
3. Open **Settings → Pages**.
4. Under Build and deployment choose **Deploy from a branch**, branch `main`, folder `/ (root)`.
5. Open **Actions** and confirm workflows are enabled.
6. Run the workflow once manually to test it.

## Important
Cinema websites can change their markup without notice. This architecture is automatic, but no scraper is maintenance-free. Source URLs and last-update metadata are retained so visitors can verify schedules before booking.
