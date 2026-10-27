# Registration record

The plan in `PREREGISTRATION.md` is registered on OSF Registries. From this point the plan is frozen; any change to
it, or to the registered code, is recorded in `DEVIATIONS.md`.

| Item | Value |
|---|---|
| Registration | https://osf.io/c53w9/ |
| DOI | 10.17605/OSF.IO/C53W9 |
| Registered (OSF timestamp) | 2026-10-26 13:22:16 UTC |
| Type | OSF Open-Ended Registration; public, no embargo (approved 2026-10-26) |
| Plan | `PREREGISTRATION.md` v0.6, sha256 `d0e374c8b493eb2f2fa7da1c0d8cbe46745a601233f11a81d2b2be73c402e8f2` |
| Code commit | `a4064f5` |
| Code zip | `mssp-benchmark-ratchet-a4064f5.zip`, sha256 `4c98d76a586151ab608851c69217a5ddb6b394201643a3de89a839bb1f659cd4` |
| Related OSF project | https://osf.io/z4an5/ (editable; cite the registration, not the project) |

Both files are attached to the registration; OSF's sha256 for each archived copy matches the values above. The
registration's summary is a plain-text copy of the plan (Markdown removed, column-name placeholders written `{e}`
and `{year}`); the attached `PREREGISTRATION.md` is the authoritative version.

The zip can be rebuilt from the repository and checked:

```bash
git archive --format=zip a4064f5 analysis/mssp-benchmark-ratchet pyproject.toml uv.lock | shasum -a 256
```

Before this file existed, no values from the results or county-level files had been read (plan section 2.2). This
file's existence unlocks those files in `ratchet/snapshot.py`.
