"""Humanize lint: flags writing patterns that read as AI-generated.
Usage: python3 hzlint.py [--doc] [--msa] [--reply] FILE [FILE ...]
  default: a post, caption, email or script paragraph (Egyptian or English)
  --reply  text to one person (a reply, a comment on their post, a DM): singular address is allowed, blank-line and closer checks skipped
  --doc  long documents with real headings (playbooks, articles, metadata): skips heading, section-label, blank-line and closer checks
  --msa  Modern Standard Arabic text: skips the Egyptian-only calque and written-MSA lists
BLOCK hits must be rewritten. REVIEW hits are read in context.
Exit 1 when any BLOCK hit exists.
"""
import json, os, re, statistics, sys

# Arabic letters only; punctuation such as ، ؛ ؟ must count as a word boundary
AR = chr(0x0621) + '-' + chr(0x065F) + chr(0x0671) + '-' + chr(0x06D3)
BULLETS = ''.join(chr(c) for c in (0x25AA, 0x25AB, 0x25B8, 0x25BA, 0x2022, 0x27A1, 0x2714, 0x2705, 0x274C, 0x1F449, 0x1F447, 0x1F4CC, 0x1F525, 0x1F680, 0x1F4A1, 0x1F4CA, 0x1F3AF))
DASHES = chr(0x2014) + chr(0x2013)

# "not X, it's Y" and its relatives, the most overused AI construction
CONTRAST = [
    r'\b\w+ [^.\n]{3,60}, no (guessing|fluff|hassle|surprises)\b',
    rf'(?<![{AR}])مش [^،.\n؟]{{1,45}}،\s*(ده|دي|دول|هو|هي|هم|إنما|انما|لكن|بل|النتيجة|الحقيقة)(?![{AR}])',
    rf'(?<![{AR}])(ليس|ليست|لا يتعلق|لم يعد|لم تعد)[^،.\n؟]{{1,45}}،?\s*(بل|وإنما|إنما|وانما)(?![{AR}])',
    rf'(?<![{AR}])(مش|ليس|ليست) (مجرد|بس|فقط)(?![{AR}])',
    rf'(?<![{AR}])[^،.\n]{{2,35}}، مش [^،.\n]{{2,30}}[.،\n]',
    r"\b(it'?s|this is|that'?s|this isn'?t|it isn'?t)\s+(not\s+)?(just\s+|only\s+)?(about\s+)?[^.,;\n]{1,45}[,;]\s*(it'?s|but|this is)\b",
    r'\bnot (just|only|merely) [^.\n]{1,45}\bbut\b',
    r"\bisn'?t about [^.\n]{1,40}\. it'?s about\b",
]
STOCK_AR = ['الحقيقة إن', 'الحقيقة أن', 'في الحقيقة', 'خلاصة القول', 'في عالم اليوم', 'في عصر', 'اللعبة اتغيرت', 'قواعد اللعبة',
    'ركزوا معايا', 'خلوني أقولكم', 'والأهم', 'الأهم من ده', 'ببساطة', 'المفاجأة', 'الخبر الحلو', 'الخبر السيئ', 'بمعنى آخر',
    'دعونا', 'في النهاية', 'في نهاية اليوم', 'الرسالة واضحة', 'القصة مش', 'السؤال الحقيقي', 'مش صدفة', 'ليس صدفة',
    'السر في', 'السر هو', 'الفرق كبير', 'اقرأ ده تاني', 'اقرأوها تاني', 'الإجابة بسيطة', 'باختصار', 'خد عندك', 'والنتيجة؟',
    'تخيلوا', 'لنكن صريحين', 'بصراحة كده', 'مش هتصدقوا', 'المعادلة بسيطة', 'الكلام ده مهم', 'نقطة ومن أول السطر']
STOCK_EN = ["here's the thing", 'the truth is', 'let that sink in', 'read that again', 'game[- ]changer', "in today'?s", 'landscape',
    'navigate', 'delve', 'leverage', 'seamless', 'unlock', 'elevate', 'robust', 'tapestry', 'supercharge', 'empower',
    "here'?s why", "here'?s what", 'the real (question|problem|story)', 'plot twist', 'spoiler', 'the bottom line', 'moreover',
    'furthermore', 'in conclusion', "it'?s worth noting", 'at the end of the day', r'stop \w+ing\. start', 'ready to',
    'the best part', 'the kicker', 'buckle up', 'no fluff', 'hot take', 'unpopular opinion']

# the reader addressed in the singular (posts and all audience text use the plural)
SINGULAR = ['إنت', 'انت', 'أنت', 'عندك', 'ليك', 'بتاعك', 'شركتك', 'موقعك', 'فريقك', 'هقولك', 'أقولك', 'هيلاقيلك', 'هتحتاجه',
    'هتحتاج', 'هتعرف', 'تقدر', 'حسيت', 'جربت', 'اتأكد', 'خد بالك', 'خلي بالك', 'يمكنك', 'لديك', 'إليك', 'ستتعلم']

# Arabized or transliterated technical terms: the term stays in English
ARABIZED = ['الإيراد لكل زيارة', 'الايراد لكل زيارة', 'معدل التحويل', 'متوسط قيمة الطلب', 'متوسط قيمة الأوردر', 'الأوردر', 'أوردر',
    'الترافيك', 'ترافيك', 'الكونفرجن', 'كونفرجن', 'العضوي', 'العضويين', 'البحث العضوي', 'سيو', 'السيو', 'معدل الارتداد',
    'الباونس', 'القناة', 'قناة التسويق', 'صفحات المنتجات', 'صفحة المنتج', 'المواصفات', 'الداشبورد', 'داشبورد', 'الفانل',
    'قمع المبيعات', 'مسار التحويل', 'العملاء المحتملين', 'الليدز', 'ليدز', 'البراند', 'الماركتنج', 'الذكاء الاصطناعي',
    'التعلم الآلي', 'محركات البحث', 'نية البحث', 'الكلمات المفتاحية', 'الروابط الخلفية', 'الباك لينك', 'الزحف', 'الفهرسة', 'أونلاين', 'الأونلاين', 'إي كوميرس', 'الميزانية التسويقية',
    'نسبة الإغلاق', 'معدل الإغلاق', 'نسبة الفوز', 'معدل الفوز', 'الإغلاق', 'مراحل البيع', 'المرحلة البيعية', 'خط المبيعات', 'التوقعات البيعية', 'توقعات المبيعات', 'الفجوة', 'فجوة الإيرادات', 'عرض القيمة', 'القيمة المقترحة', 'أهداف النمو', 'التنفيذيين', 'تنفيذي', 'معدل الاحتفاظ', 'الاحتفاظ بالعملاء', 'تكلفة الاستحواذ', 'القيمة الدائمة للعميل', 'الإيراد المتكرر', 'الإيرادات المتكررة', 'فريق المبيعات', 'مؤشرات الأداء', 'العائد على الاستثمار', 'نموذج العمل', 'ريادة الأعمال', 'العملاء الحاليين', 'أصحاب المصلحة', 'أصحاب القرار', 'التوقعات المرجحة']

# literal English calques inside Egyptian text (blocking)
CALQUE_EG = ['هدوء آخر السنة', 'في نفس مكان ناس', 'بتتكتب كأن', 'بيأكد ده', 'بيدعم القراءة دي', 'المعدل الفعلي', 'نسب فرق', 'في حجمها الطبيعي', 'بتوصف', 'على نفس الفترة', 'من سنة واحدة']
# written MSA connectors inside Egyptian text: fine in a serious spoken register only if natural spoken (review)
WRITTEN_EG = ['في حين إن', 'في حين أن', 'تفسيري', 'لو افترضنا', 'فهي', 'فهو', 'قرار في محله', 'يطابق', 'سبب كافي',
    'بشرط إن', 'وبالتالي', 'حيث إن', 'حيث أن', 'لذلك', 'إلا أن', 'هكون غلطان', 'هكون مخطئ']
# religious words and expressions: off unless the profile enables the religious group (blocking)
RELIGIOUS_AR = ['الله', 'لله', 'بالله', 'والله', 'إن شاء', 'ان شاء', 'إنشاء الله', 'انشاء الله', 'الحمدلله', 'ماشاء', 'يا رب', 'يارب', 'ربنا',
    'اللهم', 'سبحان', 'بسم', 'آمين', 'امين', 'دعاء', 'ادعوا', 'ادعولي', 'رمضان', 'صلاة', 'الجنة', 'توفيق ربنا']
RELIGIOUS_EN = ['god', 'godspeed', 'god willing', 'inshallah', 'insha allah', 'mashallah', 'alhamdulillah', 'allah', 'blessed', 'blessing',
    'blessings', 'amen', 'pray', 'prayer', 'prayers', 'jesus']
# words that are religious in some sentences and ordinary in others (review, read the sentence)
RELIGIOUS_REVIEW = ['بركة', 'مبارك', 'مباركة', 'رزق', 'faith', 'lord', 'heaven', 'divine']
# street-casual or loose words that do not fit a researcher and professor (blocking in posts)
CASUAL = ['أوي', 'اوي', 'خالص', 'جامد', 'جامدة', 'تحفة', 'يلا', 'طب', 'بص', 'بصوا', 'يا جماعة', 'حبة', 'فشخ', 'ماشي مع الكلام ده', 'أحا', 'قشطة', 'عادي يعني', 'تلزق', 'تلزقه', 'تلزقوا', 'لزق']

def sentences(t):
    return [s.strip() for s in re.split(r'[.!؟?\n]+', t) if len(s.split()) >= 2]

# English AI-writing tells (26 patterns), numbered #1 to #26.
# BLOCK = strong alone, REVIEW = weak alone (needs company, read in context). Applied to mostly-Latin text only.
EN_BLOCK = {
    '#2 closer': [r"that('s| is) the real (win|point|story)", r'that distinction matters', r'the message was clear', r'it was a lesson in', r'this shows the importance of', r'this highlights the importance of'],
    '#3 deep saying': [r'the real question is', r'at its core', r'what really matters', r'the deeper issue', r'the heart of the matter', r'the (language|currency|architecture) of'],
    '#4 run-up': [r"let'?s (dive|explore|break (this|it) down)", r"here'?s what you need to know", r"now let'?s look at", r'without further ado', r'real talk', r"let'?s be honest", r'the thing is', r'honestly\?', r'heads up'],
    '#5 arguing with no one': [r"this isn'?t (mainly |really )?about", r"i'?m not (saying|arguing)", r'to be clear', r"don'?t get me wrong", r'this is not to say', r'a tempting approach', r'one might be tempted', r'an obvious approach would be', r'you might think\b[^.]{0,60}\bbut', r'it would be easy to just'],
    '#12 AI word': [r'delv(e|es|ing)', r'intric(ate|acies)', r'pivotal', r'meticulous(ly)?', r'showcas(e|es|ing)', r'bolstered', r'garner(ed|s)?', r'interplay', r'testament', r'underscor(e|es|ed|ing)', r'vibrant', r'crucial', r'tapestry'],
    '#13 inflated significance': [r'stands as a testament', r'plays a key role', r'setting the stage for', r'evolving landscape', r'indelible mark', r'(enduring|lasting) legacy', r'(pivotal|crucial) moment', r'continues to thrive', r'underscores its importance', r'reflects a broader', r'the future looks bright', r'exciting times ahead', r'a step in the right direction'],
    '#16 sales language': [r'nestled', r'in the heart of', r'breathtaking', r'must-visit', r'diverse array', r'renowned', r'natural beauty', r'stunning', r'groundbreaking', r'exemplifies'],
    '#17 borrowed authority': [r'experts argue', r'observers have cited', r'industry reports', r'some critics', r'several publications', r'trade publications', r'independent coverage'],
    '#22 chatbot residue': [r'i hope this helps', r'certainly!', r'of course!', r'great question', r"you'?re absolutely right", r'would you like me', r'want me to\b', r'should i continue'],
    '#23 knowledge-limit': [r'as of my last', r'up to my last training', r'while specific details are limited', r'based on available information', r'not publicly available', r'not widely documented', r'in the (provided|available) sources', r'maintains a low profile', r'keeps personal details private', r'it is believed that'],
}
EN_REVIEW = {
    '#1 split contrast': [r"(does not|doesn'?t|do not) mean[^.]{1,90}\.\s+it means"],
    '#2 fragment row': [r'(?:\bNo [^.\n]{2,30}\.\s*){3,}'],
    '#3 deep saying (weak)': [r'\bfundamentally\b', r'\bin reality\b'],
    '#6 triad': [r'\b[a-z]{4,}, [a-z]{4,},? and [a-z]{4,}\b'],
    '#9 stacked qualifier': [r'to be fair', r'could potentially', r'might arguably', r'in some cases it may', r'this is an inference', r"it'?s also possible"],
    '#10 hyphen after noun': [r'\b(is|are|was|were)\s+(high-quality|well-known|well-documented|real-time|long-term|client-facing)\b'],
    '#12 AI word (common)': [r'\bactually\b', r'\badditionally\b', r'align(s|ed)? with', r'deep dive', r'\benduring\b', r'\benhance[sd]?\b', r'\bhighlights?\b', r'\bkey\b', r'\bquietly\b', r'\bvaluable\b'],
    '#14 vague connection': [r'associated with', r'in association with', r'connected to', r'in connection with', r'linked to', r'tied to'],
    '#15 -ing rider': [r', (highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|contributing to|cultivating|fostering|encompassing|showcasing)\b'],
    '#16 sales (weak)': [r'commitment to', r'\bfeaturing\b', r'\bprofound\b'],
    '#18 avoids is/are': [r'serves as', r'stands as', r'functions as', r'operates as', r'\bboasts\b', r'refers to'],
    '#21 curly quotes': ['[“”]'],
    '#22 offer (weak)': [r'let me know'],
    '#25 about the document': [r'the (table|list|section) (below|above)', r'this section is organi[sz]ed', r'generated from', r'compiled from', r'was added to replace', r'anything unconfirmed'],
}
CHATBOT_AR = ['سؤال ممتاز', 'أتمنى أن يفيدك', 'أتمنى أن يكون هذا مفيد', 'بالتأكيد!', 'هل تريدني أن', 'هل تريد مني']

def en_tells(t, doc, add):
    """English tells that apply to English text; lines report the pattern number."""
    for kind, pats in EN_BLOCK.items():
        for p in pats:
            for m in re.finditer(r'(?<![\w])' + p + r'(?![\w])' if p[-1] != '!' else p, t, re.I):
                add('BLOCK', kind, m.group(0))
    for kind, pats in EN_REVIEW.items():
        for p in pats:
            for m in re.finditer(p, t, re.I):
                add('REVIEW', kind, m.group(0))
    heads = [l for l in t.split('\n') if re.match(r'#{1,6} ', l)]
    for h in heads:
        w = [x for x in re.findall(r"[A-Za-z][\w'-]*", h) if len(x) > 3 or x[0].isupper()]
        if len(w) >= 3 and sum(x[0].isupper() for x in w) / len(w) > 0.7: add('REVIEW', '#20 Title Case heading', h)
        if re.search('[\U0001F300-\U0001FAFF→]', h): add('BLOCK', '#20 emoji or arrow in heading', h)
    if t.count('\n---') >= 3: add('REVIEW', '#20 rule between every section', f"{t.count(chr(10) + '---')} horizontal rules")
    if len(re.findall(r'(?m)^\s*(?:[-*]\s+)?\*\*[^*\n]+\*\*:?', t)) >= 2: add('REVIEW' if doc else 'BLOCK', '#19 bold labels', 'bold label list')
    paras = [p.strip() for p in re.split(r'\n\s*\n', t) if p.strip()]
    for a, b in zip(paras, paras[1:]):
        if re.match(r'#{1,6} ', a) and not b.startswith('#'):
            hw = {x.lower() for x in re.findall(r'[A-Za-z]{4,}', a)}
            bw = [x.lower() for x in re.findall(r'[A-Za-z]{4,}', b)]
            if hw and len(b.split()) <= 12 and sum(x in hw for x in bw) / max(len(hw), 1) >= 0.6 and len(bw) <= 12:
                add('REVIEW', '#24 heading repeated in first sentence', a + ' / ' + b)
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', t) if s.strip()]
    firsts = [s.split()[0].lower() for s in sents if s.split()]
    for i in range(len(firsts) - 3):
        if firsts[i] == firsts[i + 1] == firsts[i + 2] == firsts[i + 3] and firsts[i] in ('she', 'he', 'it', 'they', 'we', 'this', 'the'):
            add('REVIEW', '#7 repeated sentence opening', ' / '.join(sents[i:i + 4])[:90])
            break


def load_profile():
    """Pick the rule profile: ADAMS_PROFILE, else the nearest .adams/config.json upward from the working folder,
    else ~/.config/adams/config.json, else the plugin option CLAUDE_PLUGIN_OPTION_PROFILE, else "default". Profiles are <name>.json files in $ADAMS_PROFILE_DIR, ~/.config/adams/profiles, then <toolkit>/config/profiles (first hit wins); a profile may \"extends\" another."""
    name = os.environ.get('ADAMS_PROFILE')
    if not name:
        d = os.getcwd()
        while True:
            f = os.path.join(d, '.adams', 'config.json')
            if os.path.isfile(f): name = json.load(open(f, encoding='utf-8')).get('profile'); break
            if os.path.dirname(d) == d: break
            d = os.path.dirname(d)
    if not name:
        f = os.path.expanduser('~/.config/adams/config.json')
        if os.path.isfile(f): name = json.load(open(f, encoding='utf-8')).get('profile')
    name = name or os.environ.get('CLAUDE_PLUGIN_OPTION_PROFILE') or 'default'  # plugin userConfig "profile", set by Claude Code in hook environments
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    dirs = [d for d in (os.environ.get('ADAMS_PROFILE_DIR'), os.path.expanduser('~/.config/adams/profiles'), os.path.join(root, 'config', 'profiles')) if d]
    def groups(n, seen=()):
        for d in dirs:
            f = os.path.join(d, n + '.json')
            if os.path.isfile(f):
                data = json.load(open(f, encoding='utf-8'))
                base = groups(data['extends'], seen + (n,)) if data.get('extends') and data['extends'] not in seen else {}
                return {**base, **data.get('groups', {})}
        raise SystemExit(f'hzlint: unknown profile "{n}" (searched {", ".join(dirs)})')
    return name, groups(name)

EN_STOP = set('the and of to is in that for with on as are was it this be by not or have from at you your we they will can has had but if so do'.split())

def detect_lang(t):
    """ar, en, latin-other (fr, es, de ...), other (Cyrillic, CJK, Hebrew ...) or none. Arabic and English have word lists; the rest get structural checks only."""
    letters = [c for c in t if c.isalpha()]
    if not letters: return 'none'
    ar = sum('\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F' for c in letters)
    lat = sum(c.isascii() or '\u00C0' <= c <= '\u024F' for c in letters)
    if (len(letters) - ar - lat) / len(letters) >= 0.3: return 'other'
    if ar / len(letters) >= 0.5: return 'ar'
    words = re.findall(r"[A-Za-z']+", t)
    if len(words) >= 12 and sum(w.lower() in EN_STOP for w in words) / len(words) < 0.12: return 'latin-other'
    return 'en'

def lint(path, doc=False, msa=False, reply=False):
    t = open(path, encoding='utf-8').read()
    low = t.lower()
    lines = t.split('\n')
    paras = [p for p in re.split(r'\n\s*\n', t) if p.strip()]
    hits = []
    add = lambda sev, kind, s: hits.append((sev, kind, s.strip().replace('\n', ' / ')[:90]))
    pname, G = load_profile()
    def sev_of(group, strong='BLOCK'):
        v = G.get(group, False)
        return strong if v is True or v == 'block' else ('REVIEW' if v == 'review' else None)

    for ch in BULLETS:
        if ch in t and sev_of('bullets'): add(sev_of('bullets'), 'EMOJI/SYMBOL BULLET', repr(ch) + ' x' + str(t.count(ch)))
    for ch in DASHES:
        if ch in t and sev_of('dashes'): add(sev_of('dashes'), 'DASH', repr(ch))
    # contrast formula: at most one per text, a second one blocks
    seen = []
    for rx in CONTRAST:
        for m in re.finditer(rx, t, re.I):
            if not any(m.start() < e and m.end() > b for b, e in seen):
                seen.append((m.start(), m.end()))
    for i, (b, e) in enumerate(sorted(seen)):
        add('REVIEW' if len(seen) == 1 else 'BLOCK', f'NOT-X-BUT-Y ({len(seen)} found, max 1)', t[b:e])
    for p in ([] if reply or not G.get('arabic_style') else SINGULAR):
        for m in re.finditer(rf'(?<![{AR}])[وفبل]?{re.escape(p)}(?![{AR}])', t):
            add('BLOCK', 'SINGULAR ADDRESS', m.group(0))
    tags = re.findall(r'#\w+', t)
    if len(tags) > 3 and G.get('post_format'): add('BLOCK', 'HASHTAGS', f'{len(tags)} (max 3)')
    for p in (ARABIZED if G.get('arabic_style') else []):
        for m in re.finditer(rf'(?<![{AR}])[وفبل]?{re.escape(p)}(?![{AR}])', t):
            add('BLOCK', 'ARABIZED TERM', m.group(0))
    for p in ([] if msa or not G.get('arabic_style') else CALQUE_EG):
        for m in re.finditer(rf'(?<![{AR}])[وفبل]?{re.escape(p)}(?![{AR}])', t):
            add('BLOCK', 'CALQUE IN EGYPTIAN', m.group(0))
    for p in ([] if msa or not G.get('arabic_style') else WRITTEN_EG):
        for m in re.finditer(rf'(?<![{AR}])[وفبل]?{re.escape(p)}(?![{AR}])', t):
            add('REVIEW', 'WRITTEN MSA IN EGYPTIAN', m.group(0))
    for p in (CASUAL if G.get('register') else []):
        for m in re.finditer(rf'(?<![{AR}])[وفبل]?{re.escape(p)}(?![{AR}])', t):
            add('BLOCK', 'CASUAL REGISTER', m.group(0))
    for p in (RELIGIOUS_AR if G.get('religious') else []):
        for m in re.finditer(rf'(?<![{AR}])[وفبل]?{re.escape(p)}(?![{AR}])', t):
            add('BLOCK', 'RELIGIOUS', m.group(0))
    for p in (RELIGIOUS_EN if G.get('religious') else []):
        for m in re.finditer(r'\b' + p + r'\b', low):
            add('BLOCK', 'RELIGIOUS', m.group(0))
    for p in (RELIGIOUS_REVIEW if G.get('religious') else []):
        rx = rf'(?<![{AR}])[وفبل]?{re.escape(p)}(?![{AR}])' if re.match(rf'[{AR}]', p) else r'\b' + p + r'\b'
        for m in re.finditer(rx, low):
            add('REVIEW', 'RELIGIOUS?', m.group(0))
    for m in re.finditer(rf'(?<![{AR}])واللي [^،.\n]{{2,20}} هو(?![{AR}])', t):
        add('BLOCK', 'CLEFT REVEAL', m.group(0))
    for p in STOCK_AR:
        if p in t: add('BLOCK', 'STOCK PHRASE', p)
    lang = detect_lang(t)
    if lang == 'en': en_tells(t, doc, add)
    elif lang == 'ar':  # English sentences inside Arabic text still get the English patterns
        runs = re.findall(r"(?:[A-Za-z][A-Za-z'-]*[ ,.;:!?]+){6,}", t)
        if runs: en_tells('\n'.join(runs), doc, add)
    elif lang in ('latin-other', 'other'):
        add('INFO', 'LANGUAGE NOT COVERED', f'detected {lang}: word lists exist for Arabic and English only; the structural checks ran, read the wording by hand and with a native-level reviewer')
    for p in CHATBOT_AR:
        if p in t: add('BLOCK', '#22 chatbot residue', p)
    for p in STOCK_EN:
        for m in re.finditer(r'\b' + p + r'\b', low):
            add('BLOCK', 'STOCK PHRASE', m.group(0))

    if doc:
        lines = [l for l in lines if not l.lstrip().startswith('#')]
    # label-style section headers: short line, no end punctuation, followed by text
    heads = [l for i, l in enumerate(lines) if 0 < len(l.split()) <= 5 and not re.search(r'[.،,:؟?!%]$', l.strip())
             and i + 1 < len(lines) and lines[i + 1].strip()]
    if len(heads) >= 2 and not doc and G.get('post_format'): add('BLOCK', 'SECTION-LABEL TEMPLATE', ' | '.join(heads))
    # posts: a blank line after every line, never two text lines stacked together
    if not doc and not reply and G.get('post_format'):
        for i in range(len(lines) - 1):
            if lines[i].strip() and lines[i + 1].strip():
                add('BLOCK', 'NO BLANK LINE', lines[i] + ' / ' + lines[i + 1])
    # line ending with a colon that introduces a reveal or list
    for l in lines:
        if l.strip().endswith(':'): add('REVIEW', 'COLON LEAD-IN', l)
    # uniform rhythm: sentence lengths too even
    lens = [len(s.split()) for s in sentences(t)]
    if len(lens) >= 6:
        cv = statistics.pstdev(lens) / statistics.mean(lens)
        # review only: a best-performing post scored 0.31, so uneven rhythm is a nudge, not a gate
        if cv < 0.35: add('REVIEW', 'UNIFORM RHYTHM', f'sentence length variation {cv:.2f} (< 0.35)')
    # anaphora: three consecutive lines opening with the same word
    # a list marker, table pipe or heading hash is markup, not the opening word
    def _first(l):
        if l.lstrip().startswith('<'): return ''  # an HTML tag line is markup, not an opening word
        w = re.sub(r'^\s*(?:[-*+>|#]+|\d+[.)])\s*', '', l).split()
        return w[0] if w else ''
    firsts = [_first(l) for l in lines]
    for i in range(len(firsts) - 2):
        if firsts[i] and firsts[i] == firsts[i + 1] == firsts[i + 2]:
            add('BLOCK', 'REPEATED OPENER', ' / '.join(lines[i:i + 3]))
    # tidy triads of short items: "a b، c d، e f"
    for m in re.finditer(rf'(?:[^،,\n.]{{2,22}}[،,]\s*){{2}}و?[^،,\n.]{{2,22}}[.\n]', t):
        parts = re.split(r'[،,]', m.group(0))
        if len(parts) == 3 and all(1 <= len(x.split()) <= 3 for x in parts):
            add('REVIEW', 'TRIAD', m.group(0))
    # balanced antithesis "X عالية، وY محدود" as a one-line maxim
    for l in lines:
        w = l.split()
        if 4 <= len(w) <= 9 and re.search(r'^[^،]+،\s*و[^،]+[.]?$', l.strip()) and len(paras) > 1:
            add('REVIEW', 'MAXIM/ANTITHESIS', l)
    # colon reveal in the opening sentence ("these numbers caught my eye: ...")
    first = re.split(r'[.؟?!\n]', t.strip(), maxsplit=1)[0]
    if ':' in first: add('BLOCK', 'COLON-REVEAL OPENER', first)
    # hook reversal in the opening
    if re.search(r'بالعكس|اتقلب|انقلبت|plot twist|flipped|the opposite', ' '.join(lines[:2]), re.I):
        add('BLOCK', 'REVERSAL HOOK', ' / '.join(lines[:2]))
    # aphorism or rhetorical question as the closing line
    # a hashtag-only line is a footer, never the closing line
    body = [l for l in lines if l.strip() and not re.fullmatch(r'(\s*#\w+)+\s*', l)]
    last = body[-1] if body else ''
    paras = [p for p in paras if not re.fullmatch(r'(\s*#\w+)+\s*', p)]
    if G.get('post_format') and not doc and not reply and len(last.split()) <= 12 and len(paras) > 1 and len(paras[-1].split('\n')) > 1:
        add('REVIEW', 'PUNCHLINE CLOSER', last)
    if G.get('post_format') and re.search(r'[؟?]\s*$', last): add('REVIEW', 'QUESTION CLOSER', last)
    # rhetorical question answered on the next line
    for i, l in enumerate(lines[:-1]):
        if re.search(r'[؟?]\s*$', l) and 0 < len(lines[i + 1].split()) <= 8:
            add('BLOCK', 'Q-THEN-ANSWER', l + ' / ' + lines[i + 1])
    # rhetorical question answered right after, inside a line
    for m in re.finditer(r'[^.؟?\n]{3,60}[؟?]\s+[^.؟?\n]{1,40}[.]', t):
        add('BLOCK', 'Q-THEN-ANSWER', m.group(0))
    # filler connector overuse
    for w, cap in (('يعني', 2), ('ببساطة', 0), ('في تقديري', 1), ('actually', 1), ('really', 1)):
        n = len(re.findall(rf'(?<![{AR}\w]){w}(?![{AR}\w])', t))
        if n > cap: add('REVIEW', 'FILLER OVERUSE', f'{w} x{n}')
    return hits

if __name__ == '__main__':
    args = sys.argv[1:]
    doc, msa, reply = '--doc' in args, '--msa' in args, '--reply' in args
    block = 0
    for f in [a for a in args if not a.startswith('--')]:
        hs = lint(f, doc, msa, reply)
        for sev, kind, s in hs:
            print(f'{f}  {sev:6} {kind:28} {s}')
        b = sum(1 for h in hs if h[0] == 'BLOCK')
        block += b
        print(f'{f}: {b} BLOCK, {len(hs) - b} REVIEW\n')
    sys.exit(1 if block else 0)
