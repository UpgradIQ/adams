---
type: llm
weight: 3
---
The agent stops before building anything and asks the user the open decisions in one round (at most 4 questions).
Every question carries a recommended answer with a short reason. No page, code or file is produced yet.
Fail if it builds first, asks a bare list of questions with no recommendation, or asks more than 4.
