# Prototype sample selection

Five samples drive the v1 [E2E prototype](plan.md), one per
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

## Locked filenames (first run, 2026-04-26)

| Use case | Path | sha256 (head) |
| --- | --- | --- |
| Contract | `samples/contracts/uk-short-form-contract.docx` | `88c177fe3a74` |
| Legal | `samples/legal/us/us-open-government-act-2007.pdf` | `3af32df1de87` |
| Invoice | `samples/invoices/nifc-sf1034-invoice.pdf` | `bedf3200fa3c` |
| Spec | `samples/mech-elec-cert/ti-ne555-datasheet.pdf` | `1df8d26a8bd7` |
| Diagram | `samples/mech-elec-cert/wikimedia-arduino-uno-r3.jpg` | _(extract failed; see results)_ |

Run findings live in [results.md](results.md).
