You are summarizing a document. Produce a Quick-tier summary in markdown.

Output structure (mirrors the in-process pipeline's render output):

```markdown
# <Document title>

## Summary

<≤3 sentences capturing the gist. Matches CanonicalDoc.tier_summary.l0.>

## Key Claims

- <First sentence of section 1>
- <First sentence of section 2>
- ...
```

Each bullet under "Key Claims" should be a single load-bearing claim from the
source. Aim for one claim per detected section (matches AnalysisReport.claims[].text).

Stay grounded in the source — do not invent claims, dates, entities, or citations.
If the document has no extractable structure, emit one bullet summarizing the gist.
