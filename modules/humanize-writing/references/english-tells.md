## 6. English tells (26 patterns)

The project's own rules (sections 1 to 3 and the active profile) win wherever they are stricter, for example a profile that blocks dashes. `hzlint.py` carries the lintable patterns and reports each hit with the pattern number (`#1` to `#26`). It applies them to mostly-English text only. Arabic text keeps its own lists above.

Why AI text sounds that way: a model writes what fits the widest reader, a person writes for one reader and one subject. Every pattern is one form of that default choice: staging, rhythm by rule, inflation, formatting by rule, chat leftovers, wrong reader. Every sentence you keep must add something the reader did not already have.

**Process for rewrites (English):**
1. Mark the tells, strongest first, at paragraph level as well as sentence level (a contrast split over two sentences, the same closer after every section).
2. Draft: keep every supported claim; never add a fact, name, number, date, quote or citation that is not in the source. If a sentence needs a detail you lack, ask or write a simpler sentence. Fiction is exempt.
3. Check: read aloud; confirm nothing was added or lost; search again for the tells that survive rewrites (#1 contrasts, #2 closers, #6 triads, #8 dashes, #19 bold labels).
4. Final: say each point naturally instead of patching phrases; vary sentence length.

**Voice:** if the author gives a writing sample, match its sentence length, words, punctuation, openings and transitions. The sample overrides the English patterns but never the bans the active profile enables (dashes, religious words). Without a sample: opinion, essay and personal text keep the author's uncertainty, mixed feelings and asides; reference, technical and legal text stays neutral and plain.

**Return format:** pasted text returns the draft, a short list of remaining patterns, and the final rewrite. File mode: write only the final text to the file, change prose only (keep code, commands, paths, YAML, data, link targets), then give a short summary. Embedded mode (a PR, commit message or document): return only the final text.

**Pattern index** (L = hzlint flags it, M = manual, read the text):

| # | Pattern | How |
|---|---|---|
| 1 | Not X but Y, split contrasts, clipped tails | L (max 1, then BLOCK) |
| 2 | One-line closers, fragment rows, "explains the example" lines | L for phrases, M for the rest |
| 3 | Sayings that sound deep | L |
| 4 | Staged run-up (Let's dive in, Honestly?) | L |
| 5 | Arguing with no one (To be clear, I'm not saying) | L |
| 6 | Forced triads | L (REVIEW), M |
| 7 | Repeated sentence openings | L (4 in a row, REVIEW) |
| 8 | Dashes as the connector | L (BLOCK, banned outright) |
| 9 | Stacked qualifiers | L (REVIEW) |
| 10 | Hyphenated pairs after the noun | L (REVIEW) |
| 11 | Passive voice, missing subjects | M (weak alone) |
| 12 | Overused AI words | L (strong words BLOCK, common words REVIEW) |
| 13 | Inflated significance | L |
| 14 | Vague connection or association | L (REVIEW) |
| 15 | Shallow -ing riders | L (REVIEW) |
| 16 | Sales language | L |
| 17 | Borrowed authority | L |
| 18 | Avoiding is, are, has | L (REVIEW) |
| 19 | Bold as decoration, bold-label lists | L |
| 20 | Decorative headings (Title Case, emoji, arrows, rules) | L |
| 21 | Curly quotes | L (REVIEW, weak alone) |
| 22 | Chatbot residue | L (English and Arabic) |
| 23 | Knowledge-limit disclaimers and guesses | L |
| 24 | Heading repeated in the first sentence | L (REVIEW) |
| 25 | Writing about the document instead of its subject | L (REVIEW), M |
| 26 | Re-explaining what the reader knows | M: in a reply, lead with the decision, keep only the one fact the reader lacks, move diagnosis and proof to the ticket or doc |

**When not to act:** leave a watched phrase alone inside a quotation, a title, a proper name, or a passage that discusses the phrase. Letter salutations and sign-offs predate chatbots. Text written before 30 Nov 2022 is not AI-written. Keep what carries the writer's voice: a specific unusual detail, mixed feelings, dated slang, a first-person choice he can explain, a genuine aside. A weak-alone pattern needs company from other tells in the same passage before you edit.

**Not a goal:** getting past AI detectors. The goal is text that reads like the author and says something.
