"""Arabic language lint for scripts, lessons and published Arabic text.
Usage: python3 arlint.py FILE [FILE ...]
Flags singular address, literal-translation traps and phrases to review in context.
Exit 1 when there are hits; read every hit in context before changing it.
"""
import re, sys

# Arabic letters only, built from code points so copy and paste can never strip it.
# Punctuation (، ؛ ؟) is left out on purpose so it counts as a word boundary: with the full
# 0600-06FF block, a word followed by ؟ or ، ("موقعك؟") was silently missed.
AR = chr(0x0621) + '-' + chr(0x065F) + chr(0x0671) + '-' + chr(0x06D3)

SINGULAR = [
    'انت', 'إنت', 'أنت', 'هتعرف', 'هتقدر', 'هتلاقي', 'تقدر', 'خليني أقولك', 'أقولك', 'بيك', 'عندك', 'ليك', 'منك',
    'موقعك', 'بتاعك', 'إنك', 'انك', 'خد بالك', 'خلي بالك', 'تعالى', 'لاحظ', 'اسأل', 'شوف', 'اعمل', 'افتح',
    'ستتعلم', 'ستعرف', 'ستتبع', 'يمكنك', 'لديك', 'إليك', 'يعطيك', 'اكتب', 'قارن', 'اجلب', 'أدخل', 'اطلب',
    'نفّذ', 'رتّب', 'راجع', 'تقصد', 'تقصده', 'إشاراتك', 'صفحاتك', 'بياناتك', 'فريقك', 'شغلك', 'عملك',
    'ابدأ', 'ركّز', 'ركز', 'استخدم', 'حدّد', 'انظر', 'تذكّر', 'تذكر', 'خذ', 'اختر', 'تأكد', 'اتأكد',
]
TRAPS = [
    'فلوس الهندسة', 'وقت هندسي', 'وقت المهندسين', 'ساعة من المهندسين', 'جعان من فوق', 'متجوع',
    'نشحن', 'تشحن', 'هنشحن', 'يشحن', 'نصف قطر الانفجار', 'blast radius',
    'حدث لها crawl', 'مستندين', 'حدود عملية', 'القرار الأعلى',
]
# Correct in some contexts, literal in others: always read the sentence
REVIEW = ['يرجع', 'بيرجع', 'يستاهل وقت']

def lint(paths):
    hits = 0
    for f in paths:
        t = open(f, encoding='utf-8').read()
        for kind, lst in (('SINGULAR?', SINGULAR), ('TRAP', TRAPS), ('REVIEW', REVIEW)):
            for phrase in lst:
                # whole word, allowing an attached و / ف / ب prefix
                for m in re.finditer(rf'(?<![{AR}])[وفب]?{re.escape(phrase)}(?![{AR}])', t):
                    hits += 1
                    print(f, kind, phrase, repr(t[max(0, m.start() - 30):m.end() + 30]))
    print('arabic hits:', hits)
    return hits

if __name__ == '__main__':
    sys.exit(1 if lint(sys.argv[1:]) else 0)
