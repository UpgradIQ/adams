---
type: llm
weight: 2
focus: trace
---
The agent applies the humanize workflow: it loads the Adams skill or its humanize-writing guide, writes plain specific prose
(no stock AI phrases, no "it's not just X, it's Y", no triads, no em dash), and runs or plans `adams check post.md` before delivering.
Fail if it delivers the post with no check and no mention of one.
