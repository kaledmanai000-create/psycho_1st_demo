import json

# ── Expand phishing_patterns.json ─────────────────────────────
with open("backend/data/phishing_patterns.json", "r", encoding="utf-8") as f:
    phishing = json.load(f)

new_phishing = [
    {"text": "QNB Tunisia: Your debit card has been blocked due to suspicious activity. Click here to unblock immediately.", "template": "qnb_block_en"},
    {"text": "عاجل من CNAM: بطاقة التأمين الصحي متاعك معلقة. أدخل رقم CIN و معلوماتك لإعادة التفعيل", "template": "cnam_card_scam"},
    {"text": "Attijari Bank: Votre compte sera bloqué dans 12h. Mettez à jour vos informations personnelles via ce lien.", "template": "attijari_block_fr"},
    {"text": "بريد تونس: تم تعليق بطاقة e-DINAR متاعك. أدخل الكود السري و رقم البطاقة للتفعيل", "template": "edinar_suspend_scam"},
    {"text": "STEG vous informe: Dernière chance de payer votre facture avant coupure. Cliquez ici: steg-paiement.xyz", "template": "steg_lastchance_fr"},
    {"text": "Banque de l'Habitat: Votre prêt a été approuvé! Envoyez CIN et RIB pour finaliser le dossier.", "template": "bh_loan_approved_fr"},
    {"text": "اتصالات تونس تعلمك: خطك باش ينقطع خلال 24 ساعة. خلص الفاتورة تو عبر الرابط هذا", "template": "tt_cutoff_derja"},
    {"text": "CNRPS: Votre pension de retraite est en cours de révision. Envoyez documents et CIN pour éviter la suspension.", "template": "cnrps_pension_fr"},
    {"text": "Orange Tunisie: Vous avez un cadeau spécial! Entrez votre numéro et code PIN pour l'activer.", "template": "orange_gift_fr"},
    {"text": "بنك تونس العربي الدولي: تم رصد عملية مشبوهة. أكد هويتك فورا و إلا حسابك يتسكر", "template": "biat_suspicious_derja"},
    {"text": "UIB: Alerte fraude sur votre compte! Vérifiez vos informations bancaires immédiatement via ce lien sécurisé.", "template": "uib_fraud_fr"},
    {"text": "Tunisair: Votre billet gratuit vous attend! Entrez vos données personnelles pour le récupérer.", "template": "tunisair_ticket_fr"},
    {"text": "الضمان الاجتماعي: تم قبول ملفك للتعويض. أرسل رقم الحساب البنكي و CIN لتحويل المبلغ", "template": "cnss_compensation_scam"},
    {"text": "Topnet: Votre abonnement internet expire demain. Renouvelez en entrant vos coordonnées bancaires ici.", "template": "topnet_renewal_fr"},
    {"text": "بريد تونس الرقمي: حسابك فيه محاولة اختراق. غير كلمة السر تو عبر الرابط هذا", "template": "poste_digital_hack"},
    {"text": "ABC Bank Tunisia: Urgent security update required. Verify your account at abcbank-tn-secure.com", "template": "abc_security_en"},
    {"text": "BTE: Votre carte de crédit a été utilisée frauduleusement. Bloquez-la immédiatement via ce lien.", "template": "bte_card_fraud_fr"},
    {"text": "المندوبية الجهوية للتعليم: تم قبول ابنك في المنحة. أرسل CIN و وثائق عبر هذا الرابط", "template": "education_scholarship_scam"},
    {"text": "SNCFT: Votre remboursement de billet de 35 DT est prêt. Entrez votre RIB pour le recevoir.", "template": "sncft_refund_fr"},
    {"text": "أمان بنك يعلمك: تم تحويل مبلغ من حسابك. إذا ما عملتش التحويل أكد هويتك فورا", "template": "amen_transfer_scam"},
    {"text": "Hexabyte: Votre connexion sera coupée pour impayé. Payez 12.500 DT via ce lien sécurisé.", "template": "hexabyte_cutoff_fr"},
    {"text": "وزارة الداخلية: تم اكتشاف مشكل في بطاقة التعريف الوطنية متاعك. أدخل معلوماتك للتصحيح", "template": "interior_cin_scam"},
    {"text": "BFPME: Votre demande de micro-crédit est acceptée. Envoyez CIN, RIB et justificatifs pour débloquer les fonds.", "template": "bfpme_microcredit_fr"},
    {"text": "الصيدلية المركزية تعلمك: ربحت كارت صحي مجاني. أدخل رقم CIN و العنوان للتوصيل", "template": "pharmacy_card_scam"},
    {"text": "Enda Tamweel: Félicitations, votre crédit personnel est approuvé! Cliquez pour confirmer avec vos coordonnées.", "template": "enda_credit_fr"},
    {"text": "ربحت رحلة مجانية من نوفوتيل تونس! أدخل معلومات بطاقتك البنكية لتأكيد الحجز", "template": "novotel_trip_scam"},
    {"text": "Lycamobile Tunisie: Votre solde double! Envoyez votre code de recharge par SMS au 99999.", "template": "lyca_double_fr"},
    {"text": "البنك التونسي الكويتي: حسابك محظور مؤقتا. أدخل كلمة السر و رقم الحساب لإعادة التفعيل", "template": "btk_block_scam"},
    {"text": "BNA Mobile: Erreur critique sur votre compte épargne. Connectez-vous via ce lien pour sécuriser vos fonds.", "template": "bna_mobile_error_fr"},
    {"text": "DHL Tunisie: Votre colis est en attente. Payez les frais de douane de 8.900 DT pour le recevoir.", "template": "dhl_customs_fr"},
]

phishing.extend(new_phishing)
seen = set()
unique_phishing = []
for p in phishing:
    if p["text"] not in seen:
        seen.add(p["text"])
        unique_phishing.append(p)
phishing = unique_phishing

with open("backend/data/phishing_patterns.json", "w", encoding="utf-8") as f:
    json.dump(phishing, f, ensure_ascii=False, indent=2)

print(f"Phishing patterns: {len(phishing)}")

# ── Expand disinfo_patterns.json ─────────────────────────────
with open("backend/data/disinfo_patterns.json", "r", encoding="utf-8") as f:
    disinfo = json.load(f)

new_disinfo = [
    {"text": "صادم: الأرز المستورد لتونس بلاستيك مش حقيقي! جربوا بالنار و شوفوا بعينكم!", "template": "plastic_rice_hoax"},
    {"text": "خطير: اكتشفوا أن السكر الأبيض في تونس فيه سموم بطيئة. الحقيقة المرعبة!", "template": "sugar_poison_hoax"},
    {"text": "عالم تونسي يؤكد: الأرض مسطحة و ناسا كذبت علينا! الأدلة واضحة!", "template": "flat_earth_tn"},
    {"text": "وثائق مسربة: الحكومة باعت مخزون القمح الاستراتيجي للخارج! كارثة غذائية قادمة!", "template": "wheat_sale_conspiracy"},
    {"text": "الحقيقة الصادمة: البيض في تونس مصنوع في مختبرات و مش طبيعي! فضيحة!", "template": "fake_eggs_hoax"},
    {"text": "EXCLUSIF: La 5G installée en Tunisie provoque des tumeurs cérébrales! Des médecins témoignent!", "template": "5g_tumors_fr"},
    {"text": "دراسة مخفية: الفلور في معجون الأسنان المباع في تونس يقتل ببطء!", "template": "fluoride_conspiracy"},
    {"text": "INFO CACHÉE: Les banques tunisiennes vont geler tous les comptes la semaine prochaine!", "template": "bank_freeze_fr"},
    {"text": "كارثة: اكتشاف مواد مسرطنة في الهريسة التونسية! الشركات تعرف و ساكتة!", "template": "harissa_cancer_hoax"},
    {"text": "Alerte: Les fruits importés en Tunisie sont irradiés! Le gouvernement refuse d'agir!", "template": "irradiated_fruits_fr"},
    {"text": "خبر عاجل: زلزال قوي باش يضرب تونس الأسبوع الجاي! خبير فلكي يحذر!", "template": "earthquake_prediction"},
    {"text": "فضيحة: المياه المعدنية في تونس ملوثة بمواد كيميائية خطيرة! لا تشربوها!", "template": "mineral_water_hoax"},
    {"text": "SCANDALE: Le thon en conserve tunisien contient du mercure à des niveaux dangereux! Boycottez!", "template": "tuna_mercury_fr"},
    {"text": "الحقيقة المرة: الدواء الجنيس في تونس ما يداويش! الصيدلة المركزية تغش الشعب!", "template": "generic_medicine_hoax"},
    {"text": "RÉVÉLATION: Les compteurs d'eau intelligents de la SONEDE vous espionnent! Preuves exclusives!", "template": "sonede_spy_fr"},
    {"text": "عاجل: اكتشاف أن زيت الزيتون التونسي المصدر يرجعلنا مغشوش! فضيحة عالمية!", "template": "olive_oil_fraud_hoax"},
    {"text": "CHOQUANT: Les antennes relais en Tunisie causent la stérilité! Des études internationales le prouvent!", "template": "antenna_sterility_fr"},
    {"text": "خطير جدا: التلقيح ضد كوفيد في تونس فيه شريحة تتبع! الحكومة تخبي!", "template": "covid_chip_conspiracy"},
    {"text": "INFO EXCLUSIVE: Le gouvernement tunisien prépare une taxe secrète sur les réseaux sociaux!", "template": "social_media_tax_fr"},
    {"text": "صادم: اللحوم المجمدة المستوردة لتونس عمرها 10 سنين! وثائق حصرية!", "template": "old_meat_hoax"},
    {"text": "ALERTE SANTÉ: Les climatiseurs en Tunisie propagent un virus mortel! Éteignez-les immédiatement!", "template": "ac_virus_fr"},
    {"text": "مؤامرة عالمية: يحبوا يخليو تونس بلاد سياحة فقط و يقضيو على الصناعة!", "template": "tourism_only_conspiracy"},
    {"text": "الحقيقة اللي كلنا نعرفوها: الانتخابات في تونس كلها مزورة من الأول للتالي!", "template": "election_fraud_hoax"},
    {"text": "Les produits cosmétiques tunisiens contiennent des métaux lourds! Danger pour votre santé!", "template": "cosmetics_metals_fr"},
    {"text": "فضيحة تعليمية: المناهج الجديدة في تونس تهدف لتجهيل الشباب! مخطط خطير!", "template": "education_dumbing_conspiracy"},
    {"text": "URGENT: Des sources fiables confirment la faillite imminente de 5 banques tunisiennes!", "template": "bank_bankruptcy_fr"},
    {"text": "عاجل: الأطباء في تونس يعطيو أدوية منتهية الصلاحية! شاركوا باش يعرف الكل!", "template": "expired_medicine_hoax"},
    {"text": "EXCLUSIF: Les engrais utilisés en Tunisie causent le cancer! Les agriculteurs savent mais ne disent rien!", "template": "fertilizer_cancer_fr"},
    {"text": "صدمة: اكتشاف شبكة تجسس دولية تتنصت على مكالمات التوانسة! الحكومة متواطئة!", "template": "spy_network_conspiracy"},
    {"text": "La vérité sur le pain tunisien: Il contient des additifs chimiques interdits en Europe depuis 2010!", "template": "bread_additives_fr"},
]

disinfo.extend(new_disinfo)
seen = set()
unique_disinfo = []
for d in disinfo:
    if d["text"] not in seen:
        seen.add(d["text"])
        unique_disinfo.append(d)
disinfo = unique_disinfo

with open("backend/data/disinfo_patterns.json", "w", encoding="utf-8") as f:
    json.dump(disinfo, f, ensure_ascii=False, indent=2)

print(f"Disinfo patterns: {len(disinfo)}")
print("Done! All patterns expanded.")
