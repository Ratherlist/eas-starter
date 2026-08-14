# Engineering at Scale — practice spine

This repository is the **Engineering at Scale** course practice repo. It contains **intentional** problems. Do not copy it into a work repo. Do not treat `README.md` as documentation.

## Fake secret

`.env` holds `STOCKROOM_SYNC_TOKEN=sk_test_FAKE_eas_stockroom_not_a_real_secret`.

That value is **fake**. It is not a credential. If you put a *real* secret into this clone, stop, rotate that secret, and tell nobody it lived here — the course did not ask you to.

Lesson 7.1 is when you remove it.

## Defects (lesson numbers only)

The course pages teach the fixes. This list is a map so you can search.

| ID | Lesson |
|---|---|
| D1 README | 1.2, 6.2 |
| D2 bad commit subjects | 2.1 |
| D3 no Conventional Commits / CHANGELOG | 2.2 |
| D4 THE_GIANT | 2.3, 4.4 |
| D5 mixed style, `doStuff`, `fetchItem` | 3.1, 3.2 |
| D6 no formatter / hooks / CI | 3.2 |
| D7 branch `pr/overstock-alerts` | 4.2 |
| D8 branch `pr/sync-retry` | 4.4 |
| D9 THE_GIANT as a retrospective review | 4.4 |
| D10 branch `pr/rename-everything` | 4.4 |
| D11 unprotected `main`, no CODEOWNERS | 5.1, 5.2 |
| D12 no CONTRIBUTING / templates | 5.3 |
| D13 untested pick / zero / missing sku | 6.1 |
| D14 uncommented `parse_when`, unused expiry | 6.2 |
| D15 JSON store, sqlite note | 6.3 |
| D16 no ADR for the toolchain | 6.3 |
| D17 committed `.env` | 7.1 |
| D18 `tag` vs `category` | 7.2 |
| D19 TODO / FIXME without a policy | 7.2 |
| D20 wildcard import, qty as float | capstone |

## Hashes (filled by the replay script)

- THE_GIANT: `HASH_THE_GIANT`
- `pr/overstock-alerts`: `HASH_OVERSTOCK`
- `pr/sync-retry`: `HASH_SYNC`
- `pr/rename-everything`: `HASH_RENAME`

`main` is the `final` commit. Run `git rev-parse main` after clone.

## How this copy got here

You cloned the course starter and pushed it to **your** GitHub account. Keep `upstream` pointing at the course starter if you want to compare; do your work on `origin`.
