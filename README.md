# Pakistan Cinema Box Office

A GitHub Pages cinema-discovery site with a daily GitHub Actions data refresh.

## Correct repository structure

```
.
├── .github/
│   └── workflows/
│       └── daily-update.yml
├── data/
│   └── movies.json
├── scripts/
│   └── update_movies.py
├── index.html
├── style.css
├── script.js
└── README.md
```

## Install

1. Delete/replace the old repository contents with the contents of this ZIP.
2. Preserve the folder structure above. Do not upload the files flattened into the root.
3. In GitHub: Settings → Pages → Deploy from a branch → main → /(root).
4. In GitHub: Actions → Daily Pakistan cinema update → Run workflow.
5. Open the workflow run. It should complete with a green check.
6. Refresh the GitHub Pages site after deployment.

The workflow runs at 03:15 UTC daily (08:15 Pakistan time).

## Reliability note

Cinema websites can change markup or block automated requests. The updater is deliberately fail-safe: source failures do not erase the existing movie dataset. The page shows the last successful JSON timestamp and links to the configured sources.
