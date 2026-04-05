"""
Generate 2500+ realistic training samples for Cognitive Shield TN.
Categories: safe, phishing, manipulation, disinformation
Languages: English, French, Tunisian Arabic (Derja)
"""
import json
import random
import os

random.seed(42)
samples = []

# ============================================================
# PHISHING TEMPLATES (600+ samples)
# ============================================================
# Tunisian institutions
tn_banks = ["بنك الزيتونة", "البنك الوطني الفلاحي", "بنك تونس العربي الدولي", "أمان بنك", "بنك الإسكان", "البنك التونسي الكويتي", "بنك BIAT", "STB بنك", "بنك ABC", "بنك الأمان", "بنك BH", "بنك QNB تونس"]
fr_banks = ["Banque Zitouna", "BNA", "BIAT", "Amen Bank", "Banque de l'Habitat", "STB", "Banque de Tunisie", "ATB", "BH Bank", "QNB Tunisie", "ABC Banque", "BTK"]
en_banks = ["Zitouna Bank", "National Agricultural Bank", "BIAT Tunisia", "Amen Bank", "Housing Bank Tunisia", "STB Bank"]
tn_services = ["بريد تونس", "اتصالات تونس", "أوريدو", "الستاغ", "الصوناد", "CNAM", "CNSS", "ANETI"]
fr_services = ["La Poste Tunisienne", "Tunisie Telecom", "Ooredoo Tunisie", "STEG", "SONEDE", "CNAM", "CNSS", "ANETI"]

# Arabic phishing templates
ar_phishing = [
    "عاجل: حسابك في {bank} تم تعليقه بسبب نشاط مشبوه! أدخل بياناتك فورا لاسترجاعه",
    "تنبيه أمني من {bank}: تم اكتشاف محاولة اختراق لحسابك. أكد هويتك الآن",
    "{bank} يعلمك: حسابك باش يتسكر خلال 24 ساعة إذا ما حدثتش بياناتك",
    "مبروك! ربحت {amount} دينار من {service}. ادخل معلوماتك البنكية لاستلام الجائزة",
    "{service} تعلمك: فاتورتك ما تخلصتش. خلص تو قبل ما يقطعوا عليك الخدمة",
    "عاجل من {bank}: تم رصد عملية تحويل غير مصرح بها من حسابك. أكد هويتك فورا",
    "حسابك في {service} فيه مشكل تقني. لازم تدخل رقم CIN و كلمة السر باش يتحل",
    "تم اختيارك للحصول على قرض بدون فائدة من {bank}. أرسل CIN و RIB",
    "{bank}: بطاقتك البنكية باش تنتهي صلاحيتها. جدد معلوماتك عبر الرابط",
    "ربحت هاتف جديد في مسابقة {service}! سجل بياناتك و رقم حسابك البنكي",
    "{service} تعلمك: طردك واصل. خلص {amount} دينار مصاريف التوصيل",
    "عاجل: لازم تحدث تطبيق {service} تو و إلا ما تنجمش تدخل لحسابك",
    "تنبيه من {bank}: حدث بيانات حسابك قبل {hours} ساعة و إلا حسابك يتسكر",
    "عندك رصيد مجاني من {service}! ادخل رقم هاتفك و الكود السري باش تستفاد",
    "{bank} يبشرك: تم قبول طلب القرض متاعك. أرسل وثائقك عبر الرابط",
    "وزارة الشؤون الاجتماعية: تم قبول ملفك للمساعدة. أرسل CIN و RIB لتحويل المبلغ",
    "حسابك في e-DINAR تعرض لمحاولة اختراق! غير كلمة السر فورا عبر هالرابط",
    "{bank}: عملية سحب {amount} دينار من حسابك. إذا ماكش أنت أكد فورا",
    "تنبيه أمني: شخص حاول يدخل لحسابك في {bank} من جهاز غريب. تحقق الآن",
    "خلي بالك! راهم يسرقوا فلوسك. ادخل على رابط {bank} الآمن و غير كلمة السر",
    "عرض حصري من {bank}: فتح حساب توفير بربح 15%! سجل بياناتك تو",
    "{service}: خطك باش يتوقف لعدم الدفع. خلص فاتورتك عبر الرابط هذا",
    "فاتورة {service} متاعك فيها خطأ و تستحق تعويض {amount} دينار. أدخل RIB",
    "وكالة التشغيل: تم قبول ملفك لتكوين مهني مدفوع. أرسل CIN و RIB",
    "منحة جامعية جديدة! تم اختيارك. أدخل بياناتك الشخصية و البنكية لاستلام المنحة",
]

# French phishing templates
fr_phishing = [
    "URGENT {bank}: Activité suspecte détectée sur votre compte. Vérifiez immédiatement via ce lien",
    "Alerte sécurité {bank}: Votre compte a été compromis. Confirmez vos informations maintenant",
    "{bank} vous informe: Votre carte bancaire expire bientôt. Renouvelez en cliquant sur ce lien",
    "Félicitations! Vous avez gagné {amount} DT de {service}. Entrez vos coordonnées bancaires",
    "{service} alerte: Votre facture est impayée. Payez via ce lien ou votre service sera coupé dans 24h",
    "{bank}: Tentative de connexion suspecte à votre compte. Vérifiez vos identifiants maintenant",
    "Votre compte {service} sera suspendu pour inactivité. Connectez-vous via ce lien pour le maintenir",
    "{bank}: Mise à jour obligatoire de sécurité. Cliquez ici pour confirmer vos données",
    "Votre colis {service} est arrivé. Payez {amount} DT de frais de livraison pour le recevoir",
    "{bank} vous informe: Un virement de {amount} DT a été effectué. Si ce n'est pas vous, cliquez ici",
    "Offre spéciale {service}: Double crédit gratuit! Envoyez votre code de recharge par SMS",
    "Ministère des Finances: Votre remboursement d'impôt de {amount} DT est prêt. Entrez votre RIB",
    "{service}: Votre ligne sera suspendue dans 48h pour impayé. Régularisez via ce lien",
    "Alerte {bank}: Votre compte en ligne nécessite une vérification urgente. Cliquez ici",
    "{bank}: Nouveau service de paiement mobile activé. Confirmez avec votre code secret",
    "CNSS: Votre dossier de retraite nécessite une mise à jour urgente. Envoyez vos documents",
    "ANETI: Vous êtes sélectionné pour une formation rémunérée. Envoyez CIN et RIB",
    "{bank}: Transaction inhabituelle de {amount} DT détectée. Bloquez votre carte maintenant",
    "Douane tunisienne: Votre colis est en attente. Payez les frais de dédouanement de {amount} DT",
    "{service}: Mise à jour de votre profil requise avant le {date}. Connectez-vous ici",
]

# English phishing templates
en_phishing = [
    "URGENT: Your {bank} account shows unauthorized transactions. Verify at {bank}-secure.com now",
    "Security Alert from {bank}: Suspicious login attempt detected. Confirm your identity immediately",
    "{bank} Notice: Your account will be suspended in 24 hours unless you update your information",
    "Congratulations! You won {amount} TND from {service}. Enter your bank details to claim",
    "Your {service} bill is overdue. Pay now via this link or your service will be disconnected",
    "{bank}: Unusual activity detected on your account. Click here to secure your account now",
    "Important: Your {bank} debit card has been flagged. Verify your details to avoid suspension",
    "{bank} Security: Someone tried to access your account from a new device. Confirm your identity",
    "Your {service} subscription is expiring. Enter your payment details to continue service",
    "{bank}: A transfer of {amount} TND was initiated from your account. If not you, click here",
    "Tax refund of {amount} TND approved by the Tunisian Ministry of Finance. Enter your bank details",
    "Your {bank} online banking password will expire today. Reset it immediately via this link",
    "{service}: Package delivery failed. Pay {amount} TND shipping fee to reschedule",
    "Exclusive offer from {bank}: Get a 0% interest loan! Apply now with your personal details",
    "Your {bank} account has been temporarily locked for security reasons. Verify to unlock",
]

amounts = ["500", "1000", "2000", "3500", "5000", "150", "200", "850", "1500", "300"]
hours_list = ["24", "48", "12", "6", "72"]
dates = ["31/12/2025", "15/01/2026", "28/02/2026", "30/03/2026"]

# Generate ALL combinations for phishing
for t_template in ar_phishing:
    for bank in tn_banks:
        for svc in tn_services:
            for amt in amounts:
                t = t_template.replace("{bank}", bank).replace("{service}", svc).replace("{amount}", amt).replace("{hours}", random.choice(hours_list))
                if t != t_template:
                    samples.append({"text": t, "label": "phishing"})

for t_template in fr_phishing:
    for bank in fr_banks:
        for svc in fr_services:
            for amt in amounts:
                t = t_template.replace("{bank}", bank).replace("{service}", svc).replace("{amount}", amt).replace("{date}", random.choice(dates))
                if t != t_template:
                    samples.append({"text": t, "label": "phishing"})

for t_template in en_phishing:
    for bank in en_banks:
        for svc in fr_services:
            for amt in amounts:
                t = t_template.replace("{bank}", bank).replace("{service}", svc).replace("{amount}", amt)
                if t != t_template:
                    samples.append({"text": t, "label": "phishing"})

# ============================================================
# MANIPULATION TEMPLATES (600+ samples)
# ============================================================
ar_manipulation = [
    "اصحى يا تونسي! {topic} و ما حد يحكي! شارك قبل ما يمسحوا البوست",
    "لازم تشارك هالفيديو تو! الحقيقة اللي ما يحبوكش تعرفها على {topic}",
    "آخر فرصة! {action} يسكر غدوة. سجل تو و إلا تخسر الفرصة للأبد",
    "خطير! {threat} و الدولة ما تعمل شي. كل أم تونسية لازم تشارك هالخبر",
    "إذا ما تشاركش هالرسالة مع 10 أشخاص راح {consequence}. شاركها تو!",
    "كل تونسي حر لازم يشارك هالمعلومة. اللي ما يشاركش خاين لبلادو!",
    "فزع! {topic} الأسبوع الجاي. اشري تو قبل فوات الأوان!",
    "عيب عليك تسكت! ناس تعاني و أنت تتفرج! شارك هالرسالة تو!",
    "اللي عندو ضمير يشارك هالخبر! اللي ساكت شريك في الجريمة!",
    "يا شعب تونس! فيقوا قبل ما يفوت الأوان! {topic}!",
    "هل تقبل اللي يصير في بلادك؟ إذا أنت راجل شارك هالبوست!",
    "ناس تموت و أنت تتفرج؟ شارك و خلي صوتك يتسمع!",
    "كفى صمت! {topic} و هوما يسرقوا! لازم نتحركوا تو!",
    "يا أمهات تونس! ولادكم في خطر من {threat}! لازم تقراو هالمقال!",
    "اللي ساكت على الحق شيطان أخرس! شارك و بين إنك إنسان!",
    "آش بيك ساكت؟ ما عندكش ولاد؟ ما تحبش مستقبلهم يكون أحسن؟",
    "قلبي يوجعني على بلادي! كل تونسي شريف لازم يشارك هالحقيقة!",
    "الوقت يجري! باقي {hours} ساعة باش {action} و إلا خسرت حقك!",
    "إذا كنت تونسي حقيقي ما ينفعش تسكت على هالظلم!",
    "حرام عليهم! شوفوا شنوة يعملوا في الشعب المسكين! لازم الكل يعرف!",
    "هاذي آخر مرة نحكي! إذا ما تشاركش تو ما عاد تلوم حد!",
    "راك تونسي و تسكت؟ هاذي بلادك تتهرس قدام عينيك!",
    "الصمت جريمة! كل واحد يشوف هالظلم و يسكت هو شريك فيه!",
    "هل تعلم أنو {topic} و أنت ما تعرف؟ فيق و شارك مع عبادك!",
    "شارك هالبوست إذا عندك قلب! الشعب محتاج صوتك تو مش باكر!",
]

fr_manipulation = [
    "URGENT pour tous les Tunisiens! Partagez avant qu'ils ne suppriment la vérité sur {topic}!",
    "Dernière chance! {action} ferme dans 24h. Ne ratez pas cette opportunité unique!",
    "Attention parents tunisiens! Vos enfants sont en danger à cause de {threat}. Partagez d'urgence!",
    "Si vous êtes un vrai Tunisien, partagez ce message! {topic}!",
    "Tunisiens réveillez-vous! On nous ment depuis des années sur {topic}! Partagez massivement!",
    "Honte à ceux qui se taisent! Le peuple tunisien souffre à cause de {topic}!",
    "Vous acceptez ça pour vos enfants? Si vous avez du courage, partagez! Sinon restez esclaves!",
    "Alerte rouge pour la Tunisie! {topic}! Si vous aimez votre pays, partagez immédiatement!",
    "Ne soyez pas complice du silence! Chaque Tunisien doit voir cette vidéo avant suppression!",
    "C'est maintenant ou jamais! {topic}! Partagez avec tous vos contacts!",
    "Le silence est complicité! Partagez cette information vitale pour nos enfants!",
    "On nous prend pour des idiots! Réveillez-vous et partagez la vérité sur {topic}!",
    "Qui aime la Tunisie partage! Qui se tait trahit son pays et ses enfants!",
    "Dernière alerte! Si on ne partage pas la vérité sur {topic} maintenant, il sera trop tard!",
    "Parents tunisiens, protégez vos enfants de {threat}! Partagez cet avertissement!",
]

en_manipulation = [
    "ACT NOW Tunisians! Share this before they delete it! {topic}!",
    "Every Tunisian must see this! If you love Tunisia, share immediately! Silence is betrayal!",
    "Wake up Tunisia! {topic}! Share before it's too late!",
    "WARNING: If you're Tunisian and you stay silent, you're part of the problem! Share NOW!",
    "This affects EVERY Tunisian family! Don't be the one who stayed quiet! Share immediately!",
    "Your silence means you agree with {topic}! Real Tunisians speak up and share!",
    "LAST CHANCE to save Tunisia! {topic}! Share with everyone you know!",
    "If you have children, you MUST share this! {threat} is destroying their future!",
    "Don't let them silence us! {topic}! Share before they take this down!",
    "Every second you stay silent, Tunisia suffers more! Share and make your voice heard!",
]

topics = [
    "الحكومة تبيع البلاد", "الأسعار تزيد كل يوم", "الفساد يزيد", "الشعب يموت جوع",
    "فلوسك راهي تتسرق", "المواد الغذائية راح تنقص", "التعليم يتراجع", "البطالة تزيد",
    "المستشفيات خاوية", "الأدوية مفقودة", "النقل العمومي منهار", "الطرقات مهترئة",
    "التلوث يقتل الناس", "المصانع تسكر", "الشباب يهرب من البلاد", "الفقر يزيد",
    "الماء مقطوع", "الكهرباء تنقص", "المحروقات غالية", "الإيجارات طلعت",
    "la hausse des prix", "la corruption", "le chômage", "la crise économique",
    "la pollution", "le système éducatif", "la santé publique", "les transports",
    "l'inflation", "la dette publique", "le système bancaire", "la sécurité alimentaire",
    "rising prices", "corruption", "unemployment", "the economic crisis",
    "they are stealing your money", "education is failing", "healthcare is collapsing",
    "les prix augmentent", "nos droits sont violés", "l'avenir de nos enfants",
    "the housing crisis", "food prices", "fuel costs", "public safety",
    "water shortage", "infrastructure decay", "brain drain", "poverty rates",
]
threats = [
    "ولادنا في خطر", "المنتوجات الغذائية فيها سموم", "التطبيقات تسرق بياناتنا",
    "الماء الملوث", "المبيدات في الخضر", "الهواء الملوث", "المدارس المهترئة",
    "التلاقيح المشبوهة", "الأكل المعلب", "الحليب المغشوش", "المواد الحافظة",
    "cette application dangereuse", "les produits chimiques dans la nourriture",
    "les pesticides dans nos aliments", "la pollution de l'air", "l'eau contaminée",
    "les additifs alimentaires", "les écrans pour les enfants", "la malbouffe",
    "toxic food products", "dangerous apps stealing data", "environmental pollution",
    "contaminated water", "air pollution", "processed food additives", "screen addiction",
]
actions = [
    "التسجيل في البرنامج الحكومي", "التقديم على المنحة", "الاشتراك في الحملة",
    "التصويت في الاستطلاع", "إمضاء العريضة", "التسجيل في المنصة",
    "l'inscription au programme", "la pétition en ligne", "registration for the program",
    "le vote en ligne", "signing the petition", "joining the movement",
    "التبرع للجمعية", "المشاركة في الوقفة", "الانضمام للمجموعة",
]
consequences = [
    "تصيبك مشاكل", "تخسر حقك", "تندم باكر", "ما تلقاش مساعدة",
]

for _ in range(800):
    t = random.choice(ar_manipulation)
    t = t.replace("{topic}", random.choice(topics))
    t = t.replace("{threat}", random.choice(threats))
    t = t.replace("{action}", random.choice(actions))
    t = t.replace("{consequence}", random.choice(consequences))
    t = t.replace("{hours}", random.choice(hours_list))
    samples.append({"text": t, "label": "manipulation"})

for _ in range(600):
    t = random.choice(fr_manipulation)
    t = t.replace("{topic}", random.choice(topics))
    t = t.replace("{threat}", random.choice(threats))
    t = t.replace("{action}", random.choice(actions))
    samples.append({"text": t, "label": "manipulation"})

for _ in range(500):
    t = random.choice(en_manipulation)
    t = t.replace("{topic}", random.choice(topics))
    t = t.replace("{threat}", random.choice(threats))
    samples.append({"text": t, "label": "manipulation"})

# ============================================================
# DISINFORMATION TEMPLATES (600+ samples)
# ============================================================
ar_disinfo = [
    "فضيحة: {claim_ar}! وثائق مسربة تثبت كل شي!",
    "اكتشاف {cure_ar} لكن اللوبيات الصيدلانية منعت نشره!",
    "خطير: {danger_ar} و {authority_ar} تخبي الحقيقة",
    "معلومة خطيرة: {tech_ar} في تونس تسبب أمراض خطيرة!",
    "وثائق مسربة تكشف {conspiracy_ar}!",
    "طبيب تونسي يكتشف {cure_ar}! الأطباء يخبيوها!",
    "صادم: {food_ar} فيه مواد كيميائية خطيرة. الحقيقة المخفية!",
    "مؤامرة كبرى ضد تونس! {conspiracy_ar}!",
    "100% مثبت: {cure_ar}!",
    "الحقيقة اللي ما يحبوكش تعرفها: {danger_ar}!",
    "عالم الفلك يتنبأ ب{disaster_ar}! الحكومة تعرف و ساكتة!",
    "الحقيقة الصادمة: {food_ar} مغشوش و يسبب أمراض خطيرة!",
    "أثبتت الدراسات أنو {cure_ar} في 30 يوم!",
    "{authority_ar} تخبي عليكم: {danger_ar}!",
    "خبير أجنبي يكشف: {conspiracy_ar}!",
    "السبب الحقيقي ل{crisis_ar}: مؤامرة لبيع تونس!",
    "باحث تونسي يكتشف أنو {tech_ar} يسبب أمراض خطيرة!",
    "فضيحة: {food_ar} مستورد من بلاد ملوثة!",
    "عالم تونسي مقيم بالخارج يكتشف أنو {danger_ar}!",
    "اكتشفوا أنو {food_ar} فيه مواد مسرطنة! وزارة الصحة ساكتة!",
]

fr_disinfo = [
    "EXCLUSIF: Des documents prouvent que {conspiracy_fr}!",
    "La vérité sur {crisis_fr} que les médias cachent!",
    "RÉVÉLATION: {conspiracy_fr}! Personne n'en parle!",
    "Scandale sanitaire en Tunisie: {food_fr} contient des substances interdites!",
    "Un médecin tunisien découvre que {cure_fr}! Big Pharma le censure!",
    "La vérité choquante sur {food_fr}: contaminé par des produits dangereux!",
    "Des scientifiques tunisiens prouvent que {cure_fr}! L'industrie pharmaceutique bloque!",
    "EXCLUSIF: {tech_fr} émettent des ondes dangereuses intentionnellement!",
    "Les vaccins distribués en Tunisie sont {danger_fr}! Le ministère cache la vérité!",
    "{authority_fr} nous ment: {conspiracy_fr}!",
    "Selon des sources fiables: {conspiracy_fr}. On nous cache tout!",
    "URGENT: {food_fr} vendu en Tunisie contient des substances cancérigènes!",
    "Information censurée: {cure_fr}. Les lobbies empêchent sa diffusion!",
    "Alerte: {tech_fr} provoque des maladies graves chez les enfants tunisiens!",
    "Document confidentiel révèle que {conspiracy_fr}!",
]

en_disinfo = [
    "BREAKING: Secret documents reveal that {conspiracy_en}!",
    "Tunisian water supply contaminated with {danger_en}! Government cover-up!",
    "Secret documents show {conspiracy_en}! The truth they don't want you to know!",
    "Scientists PROVE that {cure_en} but pharmaceutical companies are hiding it!",
    "{food_en} sold in Tunisia found to contain {danger_en}! Media blackout!",
    "EXPOSED: {conspiracy_en}! Share before they censor this!",
    "A Tunisian researcher discovers {cure_en}! Mainstream media refuses to report!",
    "The REAL reason for {crisis_en}: {conspiracy_en}!",
    "Independent study confirms {danger_en} in Tunisian {food_en}! Government silent!",
    "SHOCKING: {tech_en} is causing serious health problems in Tunisia! Proof inside!",
]

claim_ar = ["الحكومة تبيع أراضي البلاد للأجانب في السر", "الوزراء يهربوا الفلوس لسويسرا", "مخطط لتهجير التونسيين من أراضيهم", "بيع شركات الدولة بأثمان بخسة", "تهريب الفوسفاط لشركات أجنبية", "مخطط لتدمير الفلاحة التونسية"]
cure_ar = ["علاج للسرطان بالأعشاب", "وصفة تشفي من السكري في أسبوع", "التين التونسي يقضي على السرطان", "زيت الزيتون يشفي من كل الأمراض", "حبة البركة تعالج كل شي", "الحجامة تشفي من كل الأمراض", "العسل يعالج السرطان", "الثوم يقضي على كل الفيروسات", "الكركم يشفي من الالتهابات", "الزنجبيل يعالج الضغط"]
danger_ar = ["ماء الحنفية فيه مواد سامة", "التلاقيح فيها مواد مشبوهة", "الأدوية الجنيسة مغشوشة", "الفلور في معجون الأسنان يسبب الغباء", "الويفي يسبب العقم", "المبيدات في الخضر تسبب السرطان"]
tech_ar = ["شبكة 5G", "أبراج الاتصالات", "الويفي في المدارس", "الهواتف الذكية", "الميكروويف"]
conspiracy_ar = ["قوى أجنبية تتحكم في سياسات البلاد", "مخطط دولي لإفقار الشعب التونسي", "شركات أجنبية تسرق ثروات تونس", "البنك الدولي يتحكم في اقتصادنا", "مؤامرة لتدمير التعليم في تونس"]
food_ar = ["الخبز", "الحليب", "الزيت النباتي", "الفرينة", "الشاي الأخضر", "المعلبات", "اللحوم المستوردة", "السكر الأبيض", "الأرز المستورد", "العصير", "الياغورت", "البسكويت", "الشوكولاتة", "المياه المعدنية", "التونة المعلبة"]
authority_ar = ["وزارة الصحة", "الصوناد", "الحكومة", "الإعلام الرسمي"]
disaster_ar = ["كارثة طبيعية في تونس", "زلزال قريب", "فيضانات مدمرة", "موجة حر قاتلة"]
crisis_ar = ["نقص المياه", "غلاء الأسعار", "البطالة", "انهيار الدينار"]

conspiracy_fr = ["le FMI contrôle l'économie tunisienne", "un complot international vise à déstabiliser la Tunisie", "des entreprises étrangères pillent les ressources naturelles", "le gouvernement cache la vérité sur la dette", "les multinationales empoisonnent notre alimentation"]
cure_fr = ["l'huile de nigelle guérit toutes les maladies", "le jeûne guérit le cancer", "un remède naturel tunisien guérit le diabète", "le miel et le citron guérissent toutes les infections"]
food_fr = ["le lait", "le pain", "l'huile végétale", "les conserves", "le sucre", "la viande importée"]
danger_fr = ["périmés", "contaminés par des métaux lourds", "mélangés avec des produits chimiques interdits"]
tech_fr = ["Les antennes 5G", "Les antennes relais", "Le Wi-Fi dans les écoles", "Les compteurs intelligents"]
authority_fr = ["Le ministère de la Santé", "Le gouvernement", "Les médias officiels"]
crisis_fr = ["la crise de l'eau", "la hausse des prix", "le chômage", "la dévaluation du dinar"]

conspiracy_en = ["international corporations are buying Tunisia's resources", "the IMF is secretly controlling Tunisia's economy", "foreign powers are destabilizing Tunisia intentionally", "the government is hiding the real debt figures", "multinational pharma companies are testing drugs on Tunisians", "foreign banks are manipulating the dinar exchange rate", "tech companies are spying on Tunisian citizens", "agricultural companies are poisoning Tunisian soil"]
cure_en = ["olive oil cures all diseases", "fasting cures cancer", "a simple herb cures diabetes in days"]
food_en = ["milk", "bread", "vegetable oil", "imported meat", "canned food", "rice", "flour", "sugar", "juice", "yogurt", "chocolate", "bottled water", "canned tuna", "breakfast cereal"]
danger_en = ["industrial chemicals", "heavy metals", "banned pesticides", "toxic substances"]
tech_en = ["5G towers", "Wi-Fi in schools", "smart meters"]
crisis_en = ["the water shortage", "rising prices", "unemployment"]

for _ in range(800):
    t = random.choice(ar_disinfo)
    t = t.replace("{claim_ar}", random.choice(claim_ar))
    t = t.replace("{cure_ar}", random.choice(cure_ar))
    t = t.replace("{danger_ar}", random.choice(danger_ar))
    t = t.replace("{tech_ar}", random.choice(tech_ar))
    t = t.replace("{conspiracy_ar}", random.choice(conspiracy_ar))
    t = t.replace("{food_ar}", random.choice(food_ar))
    t = t.replace("{authority_ar}", random.choice(authority_ar))
    t = t.replace("{disaster_ar}", random.choice(disaster_ar))
    t = t.replace("{crisis_ar}", random.choice(crisis_ar))
    samples.append({"text": t, "label": "disinformation"})

for _ in range(600):
    t = random.choice(fr_disinfo)
    t = t.replace("{conspiracy_fr}", random.choice(conspiracy_fr))
    t = t.replace("{cure_fr}", random.choice(cure_fr))
    t = t.replace("{food_fr}", random.choice(food_fr))
    t = t.replace("{danger_fr}", random.choice(danger_fr))
    t = t.replace("{tech_fr}", random.choice(tech_fr))
    t = t.replace("{authority_fr}", random.choice(authority_fr))
    t = t.replace("{crisis_fr}", random.choice(crisis_fr))
    samples.append({"text": t, "label": "disinformation"})

for _ in range(500):
    t = random.choice(en_disinfo)
    t = t.replace("{conspiracy_en}", random.choice(conspiracy_en))
    t = t.replace("{cure_en}", random.choice(cure_en))
    t = t.replace("{food_en}", random.choice(food_en))
    t = t.replace("{danger_en}", random.choice(danger_en))
    t = t.replace("{tech_en}", random.choice(tech_en))
    t = t.replace("{crisis_en}", random.choice(crisis_en))
    samples.append({"text": t, "label": "disinformation"})

# ============================================================
# SAFE TEMPLATES (700+ samples)
# ============================================================
ar_safe = [
    "وزارة التربية التونسية تعلن عن {education_ar}",
    "بلدية {city_ar} تعلن عن مشروع جديد ل{project_ar}",
    "الجامعة التونسية لكرة القدم تعلن عن {sports_ar}",
    "{event_ar} يفتح أبوابه للزوار بداية من الأسبوع القادم",
    "وزارة الصحة تعلن عن {health_ar}",
    "{company_ar} تعلن عن {business_ar}",
    "اليوم الطقس {weather_ar} في أغلب المناطق",
    "المعهد الوطني للإحصاء ينشر {stats_ar}",
    "جامعة تونس المنار تنظم {academic_ar}",
    "السوق المركزية في تونس تشهد {market_ar}",
    "برنامج جديد لدعم {support_ar} في الجهات الداخلية",
    "افتتاح {facility_ar} جديد في {city_ar}",
    "الديوان الوطني للسياحة يعلن عن {tourism_ar}",
    "{festival_ar} يعلن عن برنامجه لهذا الموسم",
    "وزارة الفلاحة تعلن عن {agriculture_ar}",
    "المنتخب التونسي {sports_result_ar}",
    "مدينة العلوم بتونس تنظم {science_ar}",
    "البنك المركزي التونسي {finance_ar}",
    "جمعية تونسية تنظم {charity_ar}",
    "المعهد الوطني للأرصاد الجوية: {forecast_ar}",
    "وزارة الثقافة تعلن عن {culture_ar}",
    "مركز البحوث ينظم {research_ar}",
    "نجاح {medical_ar} في مستشفى {hospital_ar}",
    "مؤتمر دولي حول {conference_ar} ينعقد في تونس",
    "وزارة التعليم العالي تعلن عن {university_ar}",
]

fr_safe = [
    "La municipalité de {city_fr} annonce {project_fr}.",
    "Le ministère de l'Éducation publie {education_fr}.",
    "Météo Tunisie: {weather_fr} demain avec des températures autour de {temp}°C.",
    "L'Université de Tunis organise {academic_fr}.",
    "La Fédération Tunisienne de Football annonce {sports_fr}.",
    "Le marché central de {city_fr} affiche {market_fr}.",
    "{company_fr} annonce {business_fr}.",
    "L'Institut National de la Statistique publie {stats_fr}.",
    "Le {festival_fr} annonce sa programmation pour cette saison.",
    "Le Salon International {event_fr} ouvre ses portes ce weekend.",
    "La Cité des Sciences de Tunis organise {science_fr}.",
    "Le ministère du Tourisme lance {tourism_fr}.",
    "{team_fr} remporte {sports_result_fr}.",
    "La {company_fr2} annonce des travaux de {maintenance_fr}.",
    "L'ONAT publie {tourism_stats_fr}.",
    "La Banque Centrale de Tunisie {finance_fr}.",
    "Le nouveau {infrastructure_fr} progresse selon le calendrier prévu.",
    "Un colloque sur {conference_fr} se tient à Tunis.",
    "Le gouvernement annonce {policy_fr}.",
    "La société civile tunisienne organise {civic_fr}.",
]

en_safe = [
    "Today's weather in {city_en} is {weather_en} with temperatures around {temp} degrees.",
    "The Tunisian Football Federation announced {sports_en}.",
    "A new study from University of Tunis examines {research_en}.",
    "{festival_en} announces this season's lineup of performers.",
    "Tunisia's {export_en} exports reach record levels this year.",
    "The new {infrastructure_en} project is progressing on schedule.",
    "Tunisian startups secure funding at the {event_en}.",
    "The national library hosts {culture_en} this month.",
    "Tunisia's tourism sector reports {tourism_en} for this quarter.",
    "The Ministry of Education announces {education_en}.",
    "Local farmers report {agriculture_en} this harvest season.",
    "A new hospital opens in {city_en} to improve healthcare access.",
    "Tunisia ranks higher in the latest {ranking_en}.",
    "The Central Bank of Tunisia {finance_en}.",
    "International conference on {conference_en} held in Tunis.",
    "Tunisian athletes win medals at {sports_event_en}.",
    "New public transportation routes launched in {city_en}.",
    "Tunisian researchers publish breakthrough findings on {research_en}.",
    "The annual {event_en2} kicks off in Tunis this weekend.",
    "Tunisia signs cooperation agreement with {country_en} on {topic_en}.",
]

city_ar = ["تونس", "صفاقس", "سوسة", "قابس", "بنزرت", "المنستير", "جندوبة", "سيدي بوزيد", "القيروان", "نابل", "باجة", "الكاف", "قفصة", "توزر", "تطاوين", "مدنين", "بن عروس", "أريانة", "المنزه", "زغوان"]
city_fr = ["Tunis", "Sfax", "Sousse", "Gabès", "Bizerte", "Monastir", "Nabeul", "Kairouan", "Béja", "Le Kef", "Gafsa", "Tozeur", "Tataouine", "Médenine", "Ben Arous", "Ariana", "Manouba", "Zaghouan"]
city_en = ["Tunis", "Sfax", "Sousse", "Gabes", "Bizerte", "Monastir", "Nabeul", "Kairouan", "Beja", "Gafsa", "Tozeur", "Tataouine", "Medenine"]
education_ar = ["رزنامة الامتحانات للثلاثي الثاني", "منح دراسية جديدة للطلبة المتفوقين", "افتتاح مدارس جديدة", "تحسينات في المناهج الدراسية", "برنامج تكوين للمعلمين", "مسابقة وطنية للتلاميذ", "توزيع كتب مدرسية مجانية", "افتتاح معاهد عليا جديدة"]
project_ar = ["تحسين النقل العمومي", "تهيئة الحدائق العامة", "بناء مركز ثقافي", "توسيع شبكة الصرف الصحي"]
sports_ar = ["موعد انطلاق الموسم الجديد", "نتائج المباريات الأخيرة", "برنامج التدريبات للمنتخب"]
event_ar = ["معرض الكتاب الدولي", "صالون الفلاحة", "معرض تكنولوجيا المعلومات"]
health_ar = ["حملة تلقيح مجانية", "افتتاح مراكز صحية جديدة", "برنامج فحوصات مجانية"]
company_ar = ["الخطوط التونسية", "اتصالات تونس", "الستاغ"]
business_ar = ["عروض جديدة بأسعار تنافسية", "توسيع خدماتها", "رحلات جديدة"]
weather_ar = ["مشمس", "صحو مع سحب خفيفة", "معتدل مع رياح خفيفة", "دافئ مع نسيم بحري"]
stats_ar = ["تقريره السنوي حول النمو", "إحصائيات التجارة الخارجية", "مؤشرات التشغيل"]
academic_ar = ["ملتقى علمي حول الذكاء الاصطناعي", "مؤتمر حول الطاقات المتجددة", "ندوة حول التنمية المستدامة"]
market_ar = ["استقرارا في أسعار الخضر", "وفرة في المنتوجات الموسمية", "تراجعا في أسعار اللحوم"]
support_ar = ["المشاريع الصغرى", "الفلاحين", "الحرفيين", "المرأة الريفية"]
facility_ar = ["مستشفى", "مركز ثقافي", "ملعب رياضي", "مكتبة عمومية", "حديقة عامة", "مركز شباب", "مسبح أولمبي", "مركز تكوين مهني", "روضة أطفال", "مركز صحي أساسي"]
tourism_ar = ["أرقام إيجابية للموسم السياحي", "مشاريع سياحية جديدة", "تطوير السياحة الداخلية"]
festival_ar = ["مهرجان قرطاج الدولي", "مهرجان الحامة", "أيام قرطاج السينمائية", "مهرجان الجاز بطبرقة"]
agriculture_ar = ["موسم حصاد جيد للحبوب", "زيادة في إنتاج زيت الزيتون", "تطوير الزراعة البيولوجية"]
sports_result_ar = ["يفوز في مباراة ودية", "يتأهل لدور المجموعات", "يحقق نتيجة إيجابية"]
science_ar = ["أبواب مفتوحة للتلاميذ", "ورشات علمية للشباب", "معرض الابتكارات"]
finance_ar = ["ينشر التقرير السنوي", "يحافظ على نسبة الفائدة", "يعلن عن إجراءات جديدة"]
charity_ar = ["حملة تنظيف الشواطئ", "جمع تبرعات للمحتاجين", "توزيع مساعدات غذائية"]
forecast_ar = ["طقس مستقر الأيام القادمة", "أمطار متوقعة نهاية الأسبوع", "درجات حرارة معتدلة"]
culture_ar = ["دعم المشاريع الثقافية", "مسابقة وطنية للإبداع", "معرض فني جديد"]
research_ar = ["يوم دراسي حول الزراعة المستدامة", "ندوة حول البيئة", "ملتقى حول التكنولوجيا"]
medical_ar = ["عملية زراعة كلى", "عملية قلب مفتوح", "جراحة ناجحة"]
hospital_ar = ["شارل نيكول", "الرابطة", "فطومة بورقيبة", "سهلول"]
conference_ar = ["الأمن السيبراني", "الطاقة المتجددة", "التنمية المستدامة", "الصحة العامة", "الذكاء الاصطناعي", "التجارة الإلكترونية", "الزراعة الذكية", "حقوق الإنسان", "البيئة و المناخ"]
university_ar = ["منح دراسية للطلبة المتفوقين", "شراكات مع جامعات أجنبية", "برامج تكوين جديدة"]

# French safe variables
education_fr = ["le calendrier des examens", "les résultats du baccalauréat", "de nouvelles bourses d'études"]
project_fr = ["l'ouverture d'un nouveau parc", "un programme de rénovation urbaine", "l'extension du réseau de transport"]
weather_fr = ["Temps ensoleillé", "Ciel dégagé", "Temps doux et agréable", "Quelques nuages avec éclaircies"]
academic_fr = ["un colloque sur les énergies renouvelables", "une conférence sur l'IA", "un séminaire sur l'innovation"]
sports_fr = ["le début de la nouvelle saison", "les résultats de la dernière journée", "le calendrier des matchs"]
market_fr = ["des prix stables pour les légumes", "une bonne offre en fruits de saison", "des prix en baisse"]
company_fr = ["Tunisair", "Tunisie Telecom", "STEG"]
company_fr2 = ["STEG", "SONEDE", "SNCFT"]
business_fr = ["de nouvelles lignes", "des offres promotionnelles", "l'expansion de ses services"]
stats_fr = ["son rapport trimestriel", "les chiffres du commerce extérieur", "les indicateurs économiques"]
festival_fr = ["Festival de Carthage", "Festival de Hammamet", "Journées Cinématographiques de Carthage"]
event_fr = ["du Livre de Tunis", "de l'Agriculture", "des Technologies"]
science_fr = ["des ateliers gratuits pour les jeunes", "une exposition scientifique", "des journées portes ouvertes"]
tourism_fr = ["une campagne de promotion du tourisme", "un plan de développement touristique", "de nouvelles destinations"]
team_fr = ["L'Espérance de Tunis", "Le Club Africain", "L'Étoile du Sahel", "Le CS Sfaxien"]
sports_result_fr = ["le championnat national", "la coupe de Tunisie", "un match important"]
maintenance_fr = ["maintenance dans la zone industrielle", "rénovation du réseau", "amélioration des infrastructures"]
tourism_stats_fr = ["les chiffres encourageants du tourisme", "un bilan positif de la saison", "une hausse des arrivées"]
finance_fr = ["maintient son taux directeur inchangé", "publie son rapport annuel", "annonce de nouvelles mesures"]
infrastructure_fr = ["projet d'autoroute Tunis-Sfax", "tramway de Sfax", "extension du métro de Tunis"]
conference_fr = ["l'intelligence artificielle", "la cybersécurité", "le développement durable", "l'énergie solaire"]
policy_fr = ["de nouvelles mesures de soutien aux PME", "un plan de relance économique", "des réformes administratives"]
civic_fr = ["une campagne de nettoyage des plages", "un forum sur les droits civiques", "une action de solidarité"]

# English safe variables
weather_en = ["sunny", "partly cloudy", "warm and pleasant", "mild with light breeze"]
sports_en = ["the new season schedule", "match results", "team selections"]
research_en = ["renewable energy", "artificial intelligence", "cybersecurity", "sustainable agriculture", "marine biology", "nanotechnology", "space exploration", "climate change", "quantum computing", "blockchain technology", "genetic engineering", "water desalination"]
festival_en = ["Carthage International Festival", "Hammamet Festival", "Tunis Film Festival"]
export_en = ["olive oil", "date", "textile", "phosphate", "citrus", "seafood", "handicraft", "organic produce", "electronics"]
infrastructure_en = ["Tunis-Sfax highway", "Sfax light rail", "Tunis metro extension"]
event_en = ["international tech conference", "startup summit", "innovation forum"]
culture_en = ["a free photography exhibition", "an art showcase", "a cultural festival"]
tourism_en = ["strong growth", "record visitor numbers", "increased revenue"]
education_en = ["new scholarship programs", "curriculum updates", "school renovation plans"]
agriculture_en = ["excellent yields", "strong harvests", "improved crop quality"]
ranking_en = ["global innovation index", "ease of doing business report", "education quality rankings"]
finance_en = ["maintains interest rates", "reports stable economic growth", "announces new policies"]
conference_en = ["cybersecurity", "renewable energy", "public health", "AI and technology"]
sports_event_en = ["the Mediterranean Games", "the African Championships", "an international tournament"]
event_en2 = ["book fair", "technology expo", "food festival", "cultural week", "science fair", "art exhibition", "music festival", "film festival", "startup showcase", "agriculture expo"]
country_en = ["Japan", "Germany", "South Korea", "Canada", "France", "Italy"]
topic_en = ["renewable energy", "education", "technology transfer", "agriculture", "healthcare"]
temp = ["25", "28", "30", "22", "27", "32", "20", "24"]

for _ in range(800):
    t = random.choice(ar_safe)
    for k, v in [("{city_ar}", city_ar), ("{education_ar}", education_ar), ("{project_ar}", project_ar),
                 ("{sports_ar}", sports_ar), ("{event_ar}", event_ar), ("{health_ar}", health_ar),
                 ("{company_ar}", company_ar), ("{business_ar}", business_ar), ("{weather_ar}", weather_ar),
                 ("{stats_ar}", stats_ar), ("{academic_ar}", academic_ar), ("{market_ar}", market_ar),
                 ("{support_ar}", support_ar), ("{facility_ar}", facility_ar), ("{tourism_ar}", tourism_ar),
                 ("{festival_ar}", festival_ar), ("{agriculture_ar}", agriculture_ar),
                 ("{sports_result_ar}", sports_result_ar), ("{science_ar}", science_ar),
                 ("{finance_ar}", finance_ar), ("{charity_ar}", charity_ar), ("{forecast_ar}", forecast_ar),
                 ("{culture_ar}", culture_ar), ("{research_ar}", research_ar), ("{medical_ar}", medical_ar),
                 ("{hospital_ar}", hospital_ar), ("{conference_ar}", conference_ar),
                 ("{university_ar}", university_ar)]:
        if k in t:
            t = t.replace(k, random.choice(v), 1)
    samples.append({"text": t, "label": "safe"})

for _ in range(600):
    t = random.choice(fr_safe)
    for k, v in [("{city_fr}", city_fr), ("{education_fr}", education_fr), ("{project_fr}", project_fr),
                 ("{weather_fr}", weather_fr), ("{academic_fr}", academic_fr), ("{sports_fr}", sports_fr),
                 ("{market_fr}", market_fr), ("{company_fr}", company_fr), ("{company_fr2}", company_fr2),
                 ("{business_fr}", business_fr), ("{stats_fr}", stats_fr), ("{festival_fr}", festival_fr),
                 ("{event_fr}", event_fr), ("{science_fr}", science_fr), ("{tourism_fr}", tourism_fr),
                 ("{team_fr}", team_fr), ("{sports_result_fr}", sports_result_fr),
                 ("{maintenance_fr}", maintenance_fr), ("{tourism_stats_fr}", tourism_stats_fr),
                 ("{finance_fr}", finance_fr), ("{infrastructure_fr}", infrastructure_fr),
                 ("{conference_fr}", conference_fr), ("{policy_fr}", policy_fr), ("{civic_fr}", civic_fr),
                 ("{temp}", temp)]:
        if k in t:
            t = t.replace(k, random.choice(v), 1)
    samples.append({"text": t, "label": "safe"})

for _ in range(500):
    t = random.choice(en_safe)
    for k, v in [("{city_en}", city_en), ("{weather_en}", weather_en), ("{sports_en}", sports_en),
                 ("{research_en}", research_en), ("{festival_en}", festival_en), ("{export_en}", export_en),
                 ("{infrastructure_en}", infrastructure_en), ("{event_en}", event_en),
                 ("{culture_en}", culture_en), ("{tourism_en}", tourism_en), ("{education_en}", education_en),
                 ("{agriculture_en}", agriculture_en), ("{ranking_en}", ranking_en),
                 ("{finance_en}", finance_en), ("{conference_en}", conference_en),
                 ("{sports_event_en}", sports_event_en), ("{event_en2}", event_en2),
                 ("{country_en}", country_en), ("{topic_en}", topic_en), ("{temp}", temp)]:
        if k in t:
            t = t.replace(k, random.choice(v), 1)
    samples.append({"text": t, "label": "safe"})

# Deduplicate
seen = set()
unique = []
for s in samples:
    if s["text"] not in seen:
        seen.add(s["text"])
        unique.append(s)

# Group by label and cap each at 650 samples, target 2500+ total
from collections import Counter, defaultdict
grouped = defaultdict(list)
for s in unique:
    grouped[s["label"]].append(s)

TARGET_PER_LABEL = 1000
balanced = []
for label, items in grouped.items():
    random.shuffle(items)
    balanced.extend(items[:TARGET_PER_LABEL])

random.shuffle(balanced)
unique = balanced

counts = Counter(s["label"] for s in unique)
print(f"Total unique samples: {len(unique)}")
for label, count in sorted(counts.items()):
    print(f"  {label}: {count}")

# Save
out_path = os.path.join(os.path.dirname(__file__), "data", "training_data.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"Saved to {out_path}")
