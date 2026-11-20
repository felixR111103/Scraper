# Publication Audit

Audit date: 20 November 2026

## Scope

This project was reviewed for publication in a public GitHub repository. The review covered the working tree, tracked files, reachable Git history, ignore rules, dependencies, setup documentation, generated datasets, and common indicators of secrets or personal data.

Automated pattern checks can reduce risk, but they cannot prove that a repository contains no sensitive information.

## Checks performed

- Reviewed Git status, tracked files, ignored local files, and filenames in reachable history.
- Checked tracked content and reachable history for common credential, private-key, access-token, and email patterns without recording sensitive values.
- Reviewed `.gitignore` coverage for virtual environments, caches, local environment files, and operating-system metadata.
- Reviewed `requirements.txt`, scraper configuration, frontend data loading, tests, and README setup instructions.
- Confirmed that the README covers purpose, data collection, persistence, user interaction, setup, learning, limitations, assistance, and responsible use.
- Inspected the saved datasets for broken character encoding and reviewed which generated data files are intentionally tracked.

## Issues found and fixes made

### Missing audit evidence

The initial review found that the repository did not yet contain the required `AUDIT.md`. This document was added to record the checks performed, the original findings, the actions taken, and the limitations that remain.

### Broken character encoding

The initial review found that descriptions containing punctuation or accented characters had been decoded incorrectly. The scraper now explicitly decodes source pages as UTF-8, and the four saved datasets were repaired and validated. A regression test was also added to check UTF-8 response decoding in future runs.

### Local and generated files

The virtual environment, Python caches, `.env`, pytest cache, and `.DS_Store` are ignored and are not tracked. The four datasets are intentionally tracked because they are part of the project demonstration. The unnecessary `data/.gitkeep` placeholder was removed because the directory now contains tracked files.

## Recommendations from the initial audit

The following items were identified as recommended improvements rather than publication blockers. Each item was reviewed and either addressed or consciously accepted by the project owner.

### 1. Review personal references

**Initial finding:** The README discusses the earlier Job Hunt Builder project and identifies Ricardo by first name. The audit recommended confirming that these references were appropriate for a public repository.

**Decision:** The project owner reviewed the references and confirmed that they are appropriate for publication. No change was required.

### 2. Add a license

**Initial finding:** The repository does not contain a `LICENSE` file. Without a license, other people do not automatically receive permission to reuse or modify the project even though they can view it in a public repository.

**Decision:** The project owner decided that a separate software license is not needed for this educational submission. No license was added.

### 3. Remove the redundant placeholder

**Initial finding:** `data/.gitkeep` was no longer needed because the `data/` directory already contained tracked datasets.

**Action taken:** The redundant placeholder was removed.

### 4. Consider broader ignore rules

**Initial finding:** The existing `.gitignore` correctly excludes the local artifacts currently present. The audit noted that optional rules for editor settings, coverage output, and build directories could prevent possible future commits of those files.

**Decision:** The project owner chose to keep the current ignore rules because they cover the files used by this project. No additional rules were added.

### 5. Review data-republication rights

**Initial finding:** The repository republishes book descriptions and references cover images obtained from Books to Scrape. The audit recommended confirming that this was appropriate for the public course repository.

**Decision:** The project owner confirmed that the data is being used for educational purposes. Books to Scrape is designed for scraping practice, the source is identified in the README, and responsible-use guidance is included. No change to the stored data was requested.

## Other checks that passed

- No credential-like values were detected in the currently tracked files.
- A high-confidence scan of reachable Git history did not detect private keys or common access-token formats.
- Historical Supabase files referred to configuration variable names, but no credential value was detected.
- Local virtual environments, caches, `.env`, and operating-system metadata are ignored and not tracked.
- Direct Python dependencies are pinned in `requirements.txt`.
- The README covers purpose, data collection, persistence, user interaction, setup, learning, limitations, assistance, and responsible use.
- The tracked datasets are intentional, documented, and reasonably sized for the repository.

## Remaining limitations

- The data is a static snapshot and must be regenerated to reflect source changes.
- Changes to the source website's HTML may require updates to the scraper selectors.
- Two source records have no description.
- Some source categories are placeholders rather than meaningful genres.
- Tax and review fields contain only zeroes in the current source data.
- The source does not provide authors, ISBNs, publishers, or publication dates in the collected fields.
- The frontend has no backend, accounts, favourites, or automatic refresh process.
- An interrupted full scrape cannot resume from a checkpoint.
- Dependency-vulnerability status, repository-host settings, and legal rights beyond the stated educational use were not independently verified.

## Second audit — updated working tree

The project was audited a second time on 20 November 2026 after the fixes described above were applied locally. This review checked the updated working tree rather than the older version on GitHub.

At the time of this second review, the changes passed the content and security checks. Two Git housekeeping steps still remained before publication.

### Confirmed results

- No high-confidence credentials, private keys, access tokens, JWTs, or email addresses were detected.
- No credential patterns were detected in reachable Git history.
- No mojibake patterns remained in any of the four datasets.
- The dataset structure remained correct:
  - `books.json`: 1,000 records
  - `demo_3.json`: 3 records
  - `sample_5.json`: 5 records
  - `three_pages.csv`: 60 records plus its header
- The scraper explicitly used UTF-8.
- A regression test existed for UTF-8 response decoding.
- `data/.gitkeep` had been removed.
- `AUDIT.md` contained the original findings, decisions, fixes, checks, and remaining limitations.
- The README included `AUDIT.md` in the project structure and no longer listed broken encoding as a limitation.
- `.venv`, caches, `.env`, `.DS_Store`, and other local artifacts remained untracked.
- Dependencies remained pinned.
- `git diff --check` found no formatting errors.

### Git housekeeping at the time of the second audit

1. The repaired datasets, scraper fix, test, README update, and `.gitkeep` deletion were still uncommitted in the local working tree.
2. `AUDIT.md` was still untracked and would not appear on GitHub until it was added, committed, and pushed.

Following this second audit, the reviewed changes will be committed and pushed. Once that is complete, `AUDIT.md` and the other fixes will be visible in the GitHub repository.

## Publication assessment

No credential values or tracked local dependency/cache folders were detected during this review. The documented issues relevant to this project were addressed or accepted by the project owner. This assessment reflects the repository state at the audit date and is not a guarantee that every possible security or privacy issue has been identified.
