# Humanize Writing

Most people now publish AI-written text, and it all reads the same. Published text must not. Run this on every piece of text before it is delivered or published, in Arabic (Egyptian or MSA) and English. It sits on top of the project's other language rules; it never replaces them. Which rule groups apply comes from the active profile (`default`, `strict-ar` or a personal one in `~/.config/adams/profiles/`); `adams check` prints it.

## 1. Language and terms

- **Coverage:** `hzlint.py` detects the language first. Arabic (Egyptian or MSA) and English have full word lists. English sentences inside Arabic text still get the English patterns. Any other language gets the structural checks (dashes, bullets, hashtags, blank lines, repeated openers) and a `LANGUAGE NOT COVERED` notice: read the wording yourself and have a native-level reviewer check it. Never report such a text as clean on wording.

- Spoken and social content (posts, video scripts, chat): Egyptian dialect, the way people actually talk. Other published Arabic: simple MSA. Replies and DMs in any Arabic dialect get Egyptian in the same calm register; English gets English. Rule group `arabic_style`, profile `strict-ar`.
- Every business or technical term stays in English letters: Revenue per Visit, Conversion Rate, Average Order Value, Traffic, Orders, Channel, Organic Search, Product Pages, Specs, Budget, AI, and sales terms: Win rate, Closing, Stage, Gap, Forecast, Pipeline, Growth targets, Executives, Value proposition, Stakeholders, Late-stage Deals, Weighted forecast, Existing customers, Expansion, Revenue, Retention, CAC, LTV, ROI. Before delivery, re-read every Arabic noun and ask whether a practitioner would say it in English; if so, write it in English. Never translate it ("معدل التحويل") and never transliterate it ("أوردر", "ترافيك", "أونلاين", "سيو").
- Any translation of any content, in any direction, is contextual and adapted (بالسياق وبتصرف), never literal: write the meaning the way a native speaker says it, and keep every term exactly as it is in its original language.
- Register: serious, calm and educated, soft and never street-casual. "جداً" instead of "أوي", "تضيفه" instead of "تلزقه"; no loose slang (أوي، خالص، جامد، تحفة، يلا، طب، بص، يا جماعة، ماشي مع الكلام ده، حبة). Educated connectors are fine when they sound natural spoken (لكن، في تقديري، بينما، فقط), as long as the sentence still sounds like the author talking, not like a written article. Rule group `register`.
- No Arabic sentence starts with a Latin word (it breaks RTL); put an Arabic word or "الـ" first.
- Who is addressed decides singular or plural, never one fixed form. Text to an audience (posts, first comments, scripts, captions) speaks to the readers in the plural (عندكم، بتاعكم، اعملوا). Text to ONE person (a reply under the author's post, a comment on someone's post, a DM) uses the person's name once, then singular matched to their gender when it is clear from their name or profile (شايف / شايفة، عندك / عندِك); when it is not clear, rephrase neutrally (النقطة دي، الفكرة اللي في البوست) instead of guessing. Plural inside a one-person text only when it means that person's team or company (عندكم في الـ Team). Never address one person as انتو. The author's own first person (أنا شايف، لو كان عندي) is fine. Lint one-person text with `--reply`.

## 2. Banned patterns (blocking)

- Contrast formula: "مش X، ده Y"، "X، مش Y"، "مش بس"، "ليس X بل Y"، "مش مجرد"، "not X, it's Y"، "not just X but Y". At most one per post; every other one says the positive point directly.
- Stacked lines: two text lines with no blank line between them in a post.
- Visual templates: ▪️, emoji or symbol bullets (👉 ✅ 🔥 •), label-style section headers inside a post ("الأرقام"، "قراءتي للأرقام"، "تعملوا إيه دلوقتي").
- Openers: reversal hooks ("بقوا X، وقبل سنة كانت بالعكس"), colon reveals ("الرقمين دول لفتوا نظري: ..."), staged either/or hooks ("هتبقوا مع اللي وصلوا ولا مع الـ 42%"), "تخيلوا"، "الحقيقة إن".
- Rhetorical question answered right after it ("الـ Conversion Rate كام؟ مش مكتوب.").
- Neat triads of short items ("سعر واضح، Specs كاملة، مقارنة صريحة").
- Maxim or punchline as the closer ("الجودة عالية، والحجم لسه محدود."، "زائر الـ AI بيوصل وهو حاسم نص القرار."). A post may end on one real question about the readers' own experience (see the method below); never a rhetorical "جاهزين ولا لأ؟".
- In text to an audience, the reader in the singular (إنت، شركتك، هقولك، حسيت); use the plural: شركتكم، هقولكم، حسيتوا. In text to one person, "انتو" for that person. Section 1 sets which case applies.
- More than three hashtags, or niche invented hashtags nobody follows (#Q4Planning).
- Mirrored endings ("لو قريب... ولو بعيد...").
- Cleft reveals ("واللي اتغير هو...", "what changed is...").
- Stock phrases in both languages: ببساطة، باختصار، في النهاية، اللعبة اتغيرت، السر في، السؤال الحقيقي، here's the thing, let that sink in, game-changer, in today's, landscape, navigate, delve, leverage, seamless, unlock, elevate, robust.
- Em-dash or en-dash anywhere.
- Religious words, phrases and references (إن شاء الله، الحمد لله، ما شاء الله، بإذن الله، والله، يا رب، ربنا, God willing, blessed, amen) are blocked only when the `religious` group is on in the active profile. It is a personal choice, off in `default` and `strict-ar`. When on: no religious holidays or seasons as hooks or topics, no commenting on religious topics, and when someone else writes a religious phrase, reply to the substance only and never echo it.
- Street-casual or loose words in published posts (أوي، خالص، جامد، تحفة، يلا، طب، بص، يا جماعة) are blocked by the `register` group.
- In Egyptian text, literal English calques (blocking): المعدل الفعلي، نسب فرق، بتوصف، من سنة واحدة، في حجمها الطبيعي، على نفس الفترة، بيأكد ده، بيدعم القراءة دي. Written MSA connectors are reviewed, and kept only if they sound natural in the author's serious spoken register: تفسيري، في حين إن، لو افترضنا، فهي، قرار في محله، يطابق، سبب كافي، بشرط إن، وبالتالي، لذلك، هكون غلطان. Say it the way the author would say it out loud: في تقديري، مع إن، يعني لو، بيقول نفس الكلام، يعمل Match.

## 3. What to do instead

- Post layout (group `post_format`): short lines, one sentence per line, and a blank line after every line. Two text lines stuck together with no gap block delivery. Mix line lengths where it reads naturally; the lint flags a very even beat for review only.
- Vary the skeleton. Never the fixed order hook, numbers, analysis, caveat, steps, punchline. Open on the data or on the point itself; merge caveat and action when it reads more naturally.
- Include at least one thing only the author would write: a number computed from the source (labeled as the author's calculation), a place where the author disagrees with or limits the source, or an exact step (the Regex, the GA4 setting, the command). No personal stories.
- Illustrative numbers are labeled in the text in a natural way ("مثلاً"), not with a bracketed disclaimer.
- Precision: a figure that compares two groups (AI vs other traffic) is "أعلى بـ", never "زاد" or "اتضاعف", which describe change over time. Use "زاد" only for a real change over time.
- No source names in LinkedIn post text; keep them in the chat report.

## 4. Process (every time)

1. Write the draft from the meaning, not by translating an English draft.
2. Run `adams check FILE` (it picks the lint mode and adds `arlint.py` for Arabic; `scripts/hzlint.py` is what it calls, with the flags below). Default mode for posts, captions, emails and script paragraphs; `--reply` for a reply or DM to one person; `--doc` for long documents with real headings; `--msa` for MSA text. Fix every BLOCK hit by rewriting the whole sentence; read every REVIEW hit in context.
3. Fresh eyes (blocking; when the Agent tool is available you MUST spawn the reviewer, self-review is only the fallback): use the ready prompt in `fresh-eyes-prompt.md` and give the text alone, without your intent, to a separate reviewer agent. Ask it to quote every sentence that sounds AI-generated or templated, sounds translated or not like spoken Egyptian (or natural MSA/English), contains an Arabized term, or breaks the addressing rule in section 1 (an audience in the singular, one person as انتو, or a guessed gender), and to say whether a LinkedIn reader would suspect AI. Fix everything it raises, then send the revised text back for a second pass. Stop only when the verdict is that a reader would not suspect AI. If no reviewer agent is available (for example in an unattended scheduled run), do a written self-review against sections 2 and 3 and say in the report that no separate reviewer was used.
4. Anything the reviewer or a teammate catches that the lint missed is added to the lint (lists or a new check) so it is caught automatically next time. A team-wide miss goes into the repo; a personal preference goes into your own profile or `~/.config/adams/humanize-personal.md`.
5. Report: lint result (BLOCK and REVIEW counts), reviewer verdict, and what changed.

The lint does not prove the text is human. It removes known patterns; the fresh-eyes pass and reading aloud do the rest.

## 5. Lint (run `python3 hzlint.py [--doc] [--msa] [--reply] FILE ...`)

For pptx speaker notes, extract the notes to a .txt file first and lint that.

Code: `scripts/hzlint.py` in this module (run it from there, do not paste it).

**Personal addendum:** if `~/.config/adams/humanize-personal.md` exists, read it after this guide. It holds one person's dated decisions and voice and is never shipped with the toolkit.

## On demand

- LinkedIn post or opinion post shape (group `post_format`): `references/linkedin-post.md`.
- English long-form or an AI-sounding draft: `references/english-tells.md`.
- Load only when the task needs it.
