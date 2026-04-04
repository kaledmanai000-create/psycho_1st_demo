import json

with open("backend/data/training_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

new_safe = [
    # Tunisian Derja - daily life
    {"text": "اليوم الطقس باهي في تونس، نهار ملاح للخروج", "label": "safe"},
    {"text": "الكسكسي التونسي أحسن ماكلة في العالم", "label": "safe"},
    {"text": "رحت للسوق و شريت خضرة و غلة طازجة", "label": "safe"},
    {"text": "نحب القهوة التركية الصباح مع كعكة", "label": "safe"},
    {"text": "الولاد رجعوا من المدرسة و قراوا دروسهم", "label": "safe"},
    {"text": "قريت كتاب جديد هالأسبوع، حكاية باهية بالحق", "label": "safe"},
    {"text": "مبروك على صاحبي اللي نجح في الباكالوريا", "label": "safe"},
    {"text": "الحمد لله على كل شيء، الصحة نعمة كبيرة", "label": "safe"},
    {"text": "عملت بسيسة تونسية للفطور، طعمها خيال", "label": "safe"},
    {"text": "نحبوا نتفرجوا في ماتش الترجي مع العايلة", "label": "safe"},
    {"text": "ماشي للحمامات هالويكاند مع صحابي", "label": "safe"},
    {"text": "عرس خويا الشهر الجاي، حفل كبير إن شاء الله", "label": "safe"},
    {"text": "الحر هالصيف قوي بزاف، لازم نشربوا ماء بكثرة", "label": "safe"},
    {"text": "سيدي بوسعيد مكان جميل للتصوير", "label": "safe"},
    {"text": "المدينة العتيقة في تونس عندها تاريخ كبير", "label": "safe"},
    {"text": "نحب الموسيقى التونسية التراثية، المالوف خاصة", "label": "safe"},
    {"text": "الليلة عندنا عشاء عائلي في الدار", "label": "safe"},
    {"text": "صاحبتي ولدت بنية اسمها مريم، الله يبارك", "label": "safe"},
    {"text": "مشيت للطبيب للفحص السنوي، كل شيء لاباس", "label": "safe"},
    {"text": "الكرة في تونس تجمع الناس كل، خاصة الداربي", "label": "safe"},
    {"text": "تعلمت طبخة جديدة من يوتوب، طلعت ناجحة", "label": "safe"},
    {"text": "نحب نقرا الكتب بالعربي و بالفرنساوي", "label": "safe"},
    {"text": "هالشهر بديت رياضة، نجري كل صباح", "label": "safe"},
    {"text": "رحنا لجربة في العطلة، شواطئ خيالية", "label": "safe"},
    {"text": "المطعم الجديد في المرسى ماكلتو باهية", "label": "safe"},
    # French - daily life
    {"text": "Le marché central de Tunis est toujours animé le dimanche matin.", "label": "safe"},
    {"text": "J'ai visité le musée du Bardo, la collection est impressionnante.", "label": "safe"},
    {"text": "La plage de Hammamet est magnifique en été.", "label": "safe"},
    {"text": "Le couscous tunisien est un plat traditionnel délicieux.", "label": "safe"},
    {"text": "Les résultats du baccalauréat seront publiés la semaine prochaine.", "label": "safe"},
    {"text": "La température à Tunis aujourd'hui est de 28 degrés.", "label": "safe"},
    {"text": "Le festival de Carthage commence en juillet cette année.", "label": "safe"},
    {"text": "J'apprends la programmation Python pour mon projet universitaire.", "label": "safe"},
    {"text": "Le nouveau tramway de Tunis facilite le transport quotidien.", "label": "safe"},
    {"text": "Les oliviers tunisiens produisent une huile d'olive de qualité mondiale.", "label": "safe"},
    {"text": "L'équipe nationale de football a un match amical samedi.", "label": "safe"},
    {"text": "Le café turc est une tradition tunisienne qu'on adore.", "label": "safe"},
    {"text": "Ma grand-mère fait le meilleur makroudh de toute la famille.", "label": "safe"},
    {"text": "Le Ramadan est un mois de partage et de spiritualité en Tunisie.", "label": "safe"},
    {"text": "L'université de Tunis El Manar propose de nouvelles formations.", "label": "safe"},
    # English - daily life
    {"text": "Tunisia has beautiful Mediterranean beaches and amazing culture.", "label": "safe"},
    {"text": "The old medina of Tunis is a UNESCO World Heritage Site.", "label": "safe"},
    {"text": "Tunisian olive oil is among the best in the world.", "label": "safe"},
    {"text": "The weather in Tunis is sunny and warm today.", "label": "safe"},
    {"text": "The startup ecosystem in Tunisia is growing rapidly.", "label": "safe"},
    {"text": "Tunisian students excel in international science competitions.", "label": "safe"},
    {"text": "The Carthage Film Festival showcases amazing Arab cinema.", "label": "safe"},
    {"text": "Learning Arabic and French is common for Tunisian students.", "label": "safe"},
    {"text": "The local football league has exciting matches this weekend.", "label": "safe"},
    {"text": "Traditional Tunisian crafts include ceramics and carpet weaving.", "label": "safe"},
    # Tunisian news (neutral/factual)
    {"text": "وزير التربية أعلن على رزنامة الامتحانات للسنة الدراسية", "label": "safe"},
    {"text": "تونس تستضيف مؤتمر دولي حول التكنولوجيا الخضراء الشهر الجاي", "label": "safe"},
    {"text": "افتتاح خط ميترو جديد في العاصمة يربط بين باب سعدون و المنزه", "label": "safe"},
    {"text": "البنك المركزي التونسي نشر التقرير السنوي حول الاقتصاد الوطني", "label": "safe"},
    {"text": "معرض الكتاب الدولي بتونس يستقبل آلاف الزوار هالعام", "label": "safe"},
    {"text": "الفلاحون في الشمال بداو في موسم جني الزيتون", "label": "safe"},
    {"text": "La STEG annonce des travaux de maintenance dans la banlieue nord.", "label": "safe"},
    {"text": "Le taux de chômage a légèrement baissé selon les dernières statistiques.", "label": "safe"},
    {"text": "La Tunisie a exporté 200 000 tonnes d'huile d'olive cette saison.", "label": "safe"},
    {"text": "Le nouveau parc technologique de Sousse crée 500 emplois.", "label": "safe"},
    # Code-switching safe
    {"text": "خرجت من la fac et j'ai mangé بريك في المطعم الصغير", "label": "safe"},
    {"text": "Weekend prochain نمشيو للبحر en famille إن شاء الله", "label": "safe"},
    {"text": "Mon ami تونسي et il fait les meilleurs مقروض", "label": "safe"},
    {"text": "J'ai commencé un stage في شركة IT à la Marsa", "label": "safe"},
    {"text": "الخدمة today كانت normale, rien de spécial", "label": "safe"},
    # Technology & education safe
    {"text": "تعلم البرمجة أونلاين مجاني على مواقع كثيرة", "label": "safe"},
    {"text": "الذكاء الاصطناعي يتطور بسرعة و فيه فرص كبيرة", "label": "safe"},
    {"text": "الجامعة التونسية تقدم شهادات معترف بها دوليا", "label": "safe"},
    {"text": "التلامذة التوانسة يشاركوا في أولمبياد الرياضيات العالمي", "label": "safe"},
    {"text": "Le hackathon de Tunis rassemble des développeurs talentueux.", "label": "safe"},
]

# Also add more manipulation samples to cover edge cases
new_manipulation = [
    {"text": "إذا ما شاركتش هالبوست، معناها ما تحبش بلادك! تونسي حقيقي يشارك!", "label": "manipulation"},
    {"text": "كل واحد ما يعملش شير هو خاين و ما عندوش ضمير", "label": "manipulation"},
    {"text": "أنا نعرف الحقيقة و اللي ما يآمنش بيا ضد الشعب", "label": "manipulation"},
    {"text": "ما تكونش جبان! شارك الحقيقة و إلا إنت جزء من المشكل!", "label": "manipulation"},
    {"text": "99% من التوانسة ما عندهمش الشجاعة باش يشاركوا هذا. وإنت؟", "label": "manipulation"},
    {"text": "Si tu ne partages pas, tu fais partie du problème! La Tunisie a besoin de toi!", "label": "manipulation"},
    {"text": "Chaque Tunisien patriote doit partager ce message MAINTENANT!", "label": "manipulation"},
    {"text": "حرام عليك إذا قريت هذا و ما عملتش شير! فكر في ولادك!", "label": "manipulation"},
    {"text": "ربي يحاسبك إذا ما وقفتش مع الحق! شارك تو!", "label": "manipulation"},
    {"text": "آخر مرة نقول: اللي ما يشاركش هو عدو الشعب التونسي!", "label": "manipulation"},
    {"text": "يا تونسي يا خاين! ما فماش وسط! شارك باش تثبت وطنيتك!", "label": "manipulation"},
    {"text": "Un vrai Tunisien ne resterait pas silencieux! Partagez ou vous êtes complice!", "label": "manipulation"},
    {"text": "هذا المعلومة باش تتمسح بعد ساعة! شاركها قبل ما يفوت الوقت!", "label": "manipulation"},
    {"text": "90% اللي قراو هالبوست شاركوه. إنت من العشرة في المية الباقية؟", "label": "manipulation"},
    {"text": "أمك و بوك يستاهلوا تحميهم! شارك هالتحذير تو!", "label": "manipulation"},
]

# More phishing
new_phishing = [
    {"text": "تنبيه أمني عاجل: حسابك في بنك الأمان تم اختراقه! غير كلمة السر فورا عبر هذا الرابط المؤمن", "label": "phishing"},
    {"text": "Alerte Banque de Tunisie: Transaction non autorisée de 500 DT. Confirmez via bt-securite.com", "label": "phishing"},
    {"text": "بريد تونس: ربحت جائزة 10000 دينار! أدخل معلومات حسابك البريدي لاستلام المبلغ", "label": "phishing"},
    {"text": "STEG: Votre compteur sera coupé dans 2h. Payez immédiatement via steg-urgence.tn", "label": "phishing"},
    {"text": "حسابك في e-DINAR Smart معلق. أدخل رقم البطاقة و الرمز السري لإعادة التفعيل فورا", "label": "phishing"},
    {"text": "Ooredoo: Vous avez gagné un iPhone 15! Réclamez votre prix en entrant vos données sur ooredoo-cadeau.com", "label": "phishing"},
    {"text": "البنك الوطني الفلاحي: تم حظر بطاقتك. أرسل رقم CIN و رمز البطاقة للإلغاء الفوري", "label": "phishing"},
    {"text": "CNAM alerte: Votre carte de soins expire demain. Mettez à jour via cnam-renouvellement.tn", "label": "phishing"},
    {"text": "عاجل: لازم تأكد حسابك البنكي في الـ24 ساعة الجاية و إلا يتسكر نهائيا!", "label": "phishing"},
    {"text": "Votre colis Aramex est bloqué en douane. Payez 15 DT de frais via aramex-tunisie-paiement.com", "label": "phishing"},
]

# More disinformation
new_disinfo = [
    {"text": "تحقيق حصري: الطماطم في تونس فيها هرمونات خطيرة! الحكومة تعرف و ساكتة!", "label": "disinformation"},
    {"text": "EXCLUSIF: L'eau du robinet en Tunisie contient du plomb! Les analyses le prouvent!", "label": "disinformation"},
    {"text": "فضيحة مدوية: اكتشاف أن الأدوية في الصيدليات التونسية مزورة! شاركوا!", "label": "disinformation"},
    {"text": "خبر مؤكد: الدينار التونسي باش يولي ما يسواش شيء الشهر الجاي! بيعوا كل شيء!", "label": "disinformation"},
    {"text": "RÉVÉLATION: Les universités tunisiennes vont fermer l'année prochaine! Plan secret du gouvernement!", "label": "disinformation"},
    {"text": "عاجل: اكتشاف مادة سامة في الحليب التونسي تسبب العقم! انشروا التحذير!", "label": "disinformation"},
    {"text": "معلومة مسربة: الحكومة تخطط لبيع جزيرة جربة لشركة أجنبية! وثائق سرية!", "label": "disinformation"},
    {"text": "Les médias tunisiens sont tous payés par des lobbys étrangers! La preuve ici!", "label": "disinformation"},
    {"text": "صدمة: تم اكتشاف أن شبكات الواي فاي في تونس تسبب سرطان الدماغ!", "label": "disinformation"},
    {"text": "URGENT: La Banque Centrale va confisquer l'épargne des Tunisiens! Retirez votre argent!", "label": "disinformation"},
]

data.extend(new_safe)
data.extend(new_manipulation)
data.extend(new_phishing)
data.extend(new_disinfo)

# Deduplicate
seen = set()
unique = []
for item in data:
    if item["text"] not in seen:
        seen.add(item["text"])
        unique.append(item)

# Count
from collections import Counter
counts = Counter(d["label"] for d in unique)
print(f"Total: {len(unique)}")
for label, count in sorted(counts.items()):
    print(f"  {label}: {count}")

with open("backend/data/training_data.json", "w", encoding="utf-8") as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print("Saved!")
