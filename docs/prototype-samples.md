# Prototype sample selection

Five samples drive the v1 [E2E prototype](prototype-plan.md), one per
use case, covering the file-type spectrum (PDF, DOCX, XLSX, text, image).
Sample binaries are gitignored; obtain them with:

```bash
bash scripts/download-samples.sh --download
```

## Selection criteria

| Use case | Format | `samples/` category | Why |
| --- | --- | --- | --- |
| Bidtender / contract | PDF | `contracts/` | Long-form structured prose; multi-section headings test normalize |
| Legal | PDF | `legal/us/` | Citation-rich, formal language; tests claim extraction |
| Invoice | PDF or image | `invoices/` | Tabular content + small text blocks; table-extraction stress |
| Spec / certification | PDF + DOCX | `mech-elec-cert/` | Heading hierarchy + technical terms; multi-format A/B |
| Diagrams / scanned | image / scanned PDF | `generic/` | Layout-only or image-only; OCR path stress |

## Locking the five filenames

Concrete filenames are confirmed at first harness run. Until then, the
selection criteria above stand in. After the first run, this file gets
updated with the exact paths and sha256 of each sample, and the eval
results land in [prototype-results.md](prototype-results.md).
