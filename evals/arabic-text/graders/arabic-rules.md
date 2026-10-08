---
type: llm
weight: 3
focus: files
---
Every line of the Arabic text starts with an Arabic word, not a Latin letter or digit.
Professional terms (for example invoice-related product terms) stay in Latin letters, digits are Latin, and there is no em dash or exclamation mark.
Fail if any line starts with Latin text or if a common professional term is transliterated into Arabic letters.
