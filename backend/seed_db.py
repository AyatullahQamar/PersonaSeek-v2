from intent_db import init_db, connect
RULES = [
  (r"\b(ambulance|emergency ambulance)\b", "ambulance service", 100, 1),
  (r"\b(er|emergency room|casualty)\b", "emergency hospital", 100, 1),
  (r"\b(hospital|clinic|medical center)\b", "hospital", 100, 1),
  (r"\b(blood test|cbc|thyroid|lipid|pathology|lab test|diagnostic|diagnostics)\b", "diagnostic center", 100, 1),
  (r"\b(x[- ]?ray|mri|ct scan|sonography|ultrasound)\b", "diagnostic imaging center", 100, 1),
  (r"\b(pharmacy|chemist|medical store)\b", "pharmacy", 100, 1),

  (r"\b(headache|migraine)\b", "neurologist", 100, 1),
  (r"\b(fever|cold|cough|flu|body ?ache|weakness|viral)\b", "general physician", 100, 1),
  (r"\b(stomach|gas|acidity|indigestion|vomit|diarrhoea|diarrhea|constipation)\b", "gastroenterologist", 100, 1),
  (r"\b(chest pain|heart|bp|blood pressure|hypertension|cardiac)\b", "cardiologist", 100, 1),
  (r"\b(sugar|diabetes|hba1c)\b", "diabetologist", 100, 1),
  (r"\b(kidney|urine infection|uti|stones?|stone|renal)\b", "urologist", 100, 1),
  (r"\b(back pain|joint pain|arthritis|knee pain|shoulder pain)\b", "orthopedic doctor", 100, 1),
  (r"\b(physio|physiotherapy|rehab)\b", "physiotherapist", 100, 1),
  (r"\b(skin|acne|pimples?|rash|eczema|fungal|itch|allergy|hair fall|dandruff)\b", "dermatologist", 100, 1),
  (r"\b(tooth|teeth|gum|gums|cavity|root canal|braces|wisdom tooth|toothache|swelling)\b", "dentist", 100, 1),
  (r"\b(eye|eyes|vision|blurry|redness|irritation|spectacles|glasses)\b", "eye doctor", 100, 1),
  (r"\b(ear|ears|hearing|tinnitus|sinus|throat|tonsil|nose block)\b", "ENT specialist", 100, 1),
  (r"\b(pregnan|pregnancy|gynae|gyne|periods?|pcos|women[' ]s health)\b", "gynecologist", 100, 1),
  (r"\b(child|baby|newborn|pediatric|vaccination)\b", "pediatrician", 100, 1),
  (r"\b(mental|anxiety|depression|stress|therapy|counselling|counseling|psych)\b", "psychologist", 100, 1),
  (r"\b(psychiatrist|bipolar|adhd)\b", "psychiatrist", 100, 1),

  (r"(?:\bmobile\b|\bphone\b).*(?:\brepair\b|\bfix\b|\bservice\b|\bscreen\b|\bdisplay\b|\bbattery\b)"
   r"|(?:\brepair\b|\bfix\b|\bservice\b).*(?:\bmobile\b|\bphone\b)"
   r"|\biphone repair\b|\bandroid repair\b|\bscreen broken\b|\bdisplay broken\b|\bbattery replacement\b",
   "mobile repair shop", 100, 1),

  (r"(?:\blaptop\b|\bcomputer\b|\bpc\b).*(?:\brepair\b|\bfix\b|\bservice\b|\bslow\b|\bformat\b|\bwindows\b|\bvirus\b)"
   r"|(?:\brepair\b|\bfix\b|\bservice\b).*(?:\blaptop\b|\bcomputer\b|\bpc\b)"
   r"|\bdata recovery\b|\blaptop screen\b|\bkeyboard replacement\b|\blaptop not working",
   "computer repair shop", 100, 1),

  (r"\b(printer repair|printer not working|ink problem|cartridge)\b", "printer repair", 100, 1),
  (r"\b(tv repair|television repair|led tv|lcd tv|smart tv|screen lines)\b", "tv repair", 100, 1),
  (r"\b(camera repair|dslr repair)\b", "camera repair", 100, 1),

  (r"\b(ac not cooling|air conditioner|aircon|ac repair|split ac|window ac)\b", "ac repair", 100, 1),
  (r"\b(refrigerator|fridge|freezer|cooling issue)\b", "refrigerator repair", 100, 1),
  (r"\b(washing machine|washer|dryer|spin problem)\b", "washing machine repair", 100, 1),
  (r"\b(microwave|oven|otg)\b", "microwave repair", 100, 1),
  (r"\b(geyser|water heater)\b", "geyser repair", 100, 1),
  (r"\b(chimney repair|kitchen chimney)\b", "chimney repair", 100, 1),
  (r"\b(ro purifier|water purifier|aqua guard|aquaguard)\b", "water purifier service", 100, 1),

  (r"\b(leak|water leakage|pipe burst|tap leak|clog|choke|drain|sewer)\b", "plumber", 100, 1),
  (r"\b(short circuit|wiring|switch|socket|mcb|fuse|power cut|electric)\b", "electrician", 100, 1),
  (r"\b(carpenter|wood work|door repair|furniture repair|cupboard)\b", "carpenter", 100, 1),
  (r"\b(paint|painting|wall paint|house paint|painter)\b", "painter", 100, 1),
  (r"\b(tiles|tile fitting|marble|granite)\b", "tile contractor", 100, 1),
  (r"\b(mason|brick work|plaster|cement work)\b", "mason", 100, 1),
  (r"\b(roof leak|waterproofing|damp|seepage)\b", "waterproofing service", 100, 1),

  (r"\b(roof|terrace|ceiling)\b.*\b(leak|leaking|seep|seepage|water)\b|\b(leak|leaking|seepage|damp)\b.*\b(roof|terrace|ceiling)\b",
   "waterproofing service", 100, 1),

  (r"\b(damp|seepage|wall damp|paint peel|moisture|water marks)\b", "waterproofing service", 100, 1),
  (r"\b(terrace waterproofing|roof waterproofing|bathroom waterproofing)\b", "waterproofing service", 100, 1),

  (r"\b(pest|termite|cockroach|bed bugs|rats|mosquito)\b", "pest control", 100, 1),
  (r"\b(cleaning|deep cleaning|home cleaning|bathroom cleaning|sofa cleaning)\b", "cleaning service", 100, 1),
  (r"\b(packers|movers|shifting|relocation)\b", "packers and movers", 100, 1),
  (r"\b(locksmith|lock repair|key duplicate|lost key)\b", "locksmith", 100, 1),
  (r"\b(glass work|glass repair|window glass|mirror)\b", "glass contractor", 100, 1),

  (r"\b(cctv|camera installation|security camera|dvr|nvr)\b", "cctv installation", 100, 1),
  (r"\b(alarm system|home security|security system)\b", "security system installer", 100, 1),
  (r"\b(smart home|home automation)\b", "home automation service", 100, 1),

  (r"\b(car repair|garage|mechanic|engine issue|car service)\b", "car mechanic", 100, 1),
  (r"\b(bike repair|motorcycle repair|two wheeler service)\b", "bike mechanic", 100, 1),
  (r"\b(puncture|tyre puncture|tire puncture|tyre shop|alignment|balancing)\b", "tyre shop", 100, 1),
  (r"\b(car wash|detailing|ceramic coating)\b", "car wash", 100, 1),
  (r"\b(battery jumpstart|car battery|battery replacement)\b", "car battery shop", 100, 1),

  (r"\b(gst|itr|income tax|tax filing|tds|audit|accounting|bookkeeping)\b", "chartered accountant", 100, 1),
  (r"\b(company registration|startup registration|llp|pvt ltd|incorporation)\b", "company registration consultant", 100, 1),
  (r"\b(loan|home loan|personal loan|emi|credit score|cibil)\b", "loan consultant", 100, 1),
  (r"\b(insurance|policy|claim|health insurance|car insurance)\b", "insurance agent", 100, 1),
  (r"\b(money invest|investment|mutual fund|sip|stock broker)\b", "financial advisor", 100, 1),

  (r"\b(legal notice|court|case|bail|divorce|property dispute|agreement|drafting|contract)\b", "lawyer", 100, 1),
  (r"\b(criminal lawyer|fir|police case)\b", "criminal lawyer", 100, 1),
  (r"\b(divorce|maintenance|custody|family dispute)\b", "divorce lawyer", 100, 1),
  (r"\b(property|registry|sale deed|land dispute|rent agreement)\b", "property lawyer", 100, 1),
  (r"\b(notary|notarize|affidavit)\b", "notary", 100, 1),
  (r"\b(trademark|copyright|patent)\b", "intellectual property lawyer", 100, 1),

  (r"\b(real estate|property dealer|broker|buy flat|rent flat)\b", "real estate agent", 100, 1),
  (r"\b(architect|house plan|building plan)\b", "architect", 100, 1),
  (r"\b(interior|modular kitchen|home design|renovation|false ceiling)\b", "interior designer", 100, 1),
  (r"\b(civil engineer|structural engineer)\b", "civil engineer", 100, 1),
  (r"\b(contractor|construction|build house)\b", "building contractor", 100, 1),

  (r"\b(tutor|tuition|home tuition|coach|coaching)\b", "tutor", 100, 1),
  (r"\b(ielts|toefl|spoken english)\b", "english tutor", 100, 1),
  (r"\b(math tutor|physics tutor|chemistry tutor)\b", "home tutor", 100, 1),
  (r"\b(guitar|piano|music class)\b", "music teacher", 100, 1),
  (r"\b(yoga|zumba|fitness trainer|gym trainer|personal trainer)\b", "personal trainer", 100, 1),

  (r"\b(photography|photoshoot|wedding shoot|prewedding|videography)\b", "photographer", 100, 1),
  (r"\b(video editor|editing|reels editor|youtube editor)\b", "video editor", 100, 1),
  (r"\b(makeup artist|bridal makeup|salon|hair stylist)\b", "makeup artist", 100, 1),
  (r"\b(event planner|wedding planner|decorator|decoration)\b", "event planner", 100, 1),
  (r"\b(caterer|catering|food for party)\b", "caterer", 100, 1),
  (r"\b(dj|sound system)\b", "dj service", 100, 1),

  (r"\b(website|web site|webdev|wordpress|shopify|frontend|backend|developer|web developer)\b", "web developer", 100, 1),
  (r"\b(app developer|android developer|ios developer|mobile app)\b", "app developer", 100, 1),
  (r"\b(digital marketing|seo|social media marketing|ads|google ads|meta ads)\b", "digital marketing agency", 100, 1),
  (r"\b(graphic design|logo design|branding|poster design)\b", "graphic designer", 100, 1),
  (r"\b(ui ux|ui/ux|ux designer|product designer)\b", "ui ux designer", 100, 1),
  (r"\b(content writer|copywriter|blog writer)\b", "content writer", 100, 1),

  (r"\b(travel agent|tour package|holiday package|visa)\b", "travel agent", 100, 1),
  (r"\b(taxi|cab|car on rent|driver)\b", "taxi service", 100, 1),
  (r"\b(courier|parcel|delivery service)\b", "courier service", 100, 1),

  (r"\b(spa|massage|salon)\b", "salon", 100, 1),
  (r"\b(barber|haircut)\b", "barber shop", 100, 1),
  (r"\b(beautician|facial|waxing)\b", "beautician", 100, 1),

  (r"\b(cook|chef|home cook|tiffin|meal service)\b", "tiffin service", 100, 1),
  (r"\b(bakery|cake order|birthday cake)\b", "bakery", 100, 1),
  (r"\b(babysitter|nanny)\b", "nanny service", 100, 1),
  (r"\b(maid|house help|domestic help)\b", "maid service", 100, 1),

  (r"\b(repair|fix|service center|maintenance)\b", "repair service", 100, 1),
  (r"\b(consultant|advisor)\b", "consultant", 100, 1),
  (r"\b(gym|fitness|workout|bodybuilding|weight training)\b", "gym", 100, 1),
]



DESCS = [

# ================= HEALTH =================
("general physician", "General physicians handle common issues like fever, cold, body pain, weakness, and basic diagnosis."),
("dentist", "Tooth or gum problems can be due to cavities, infection, sensitivity, or gum inflammation. A dentist can examine and treat it."),
("dermatologist", "Skin issues like acne, rashes, itching, fungal infections, or hair problems are treated by a dermatologist."),
("eye doctor", "Eye irritation, redness, blurry vision, or vision check-ups are handled by an eye specialist."),
("ent specialist", "Ear, nose, throat issues like sinus, throat pain, ear pain, or hearing problems are treated by an ENT specialist."),
("gynecologist", "Women’s health concerns like periods, pregnancy-related care, or hormonal issues are handled by a gynecologist."),
("pediatrician", "Child and baby health issues, vaccinations, and growth-related concerns are handled by a pediatrician."),
("physiotherapist", "Physiotherapy helps in muscle/joint pain, posture issues, injury recovery, and improving movement."),
("orthopedic doctor", "Bone, joint, back, knee, or shoulder pain is typically handled by an orthopedic specialist."),

# ================= REPAIRS / ELECTRONICS =================
("mobile repair shop", "Mobile issues like screen damage, battery drain, charging problems, or speaker/mic faults are usually fixed by a mobile repair shop."),
("computer repair shop", "Laptop/PC issues like slow performance, OS problems, heating, hardware faults, or data recovery are handled by computer repair experts."),
("tv repair", "TV problems like display lines, no power, sound issues, or panel faults are handled by TV repair technicians."),

# ================= HOME SERVICES =================
("plumber", "Plumbing problems like leaks, clogged drains, tap issues, or pipe damage should be fixed early to avoid water damage."),
("electrician", "Electrical issues like wiring faults, short circuits, switch/socket problems, or MCB trips should be checked by an electrician for safety."),
("ac repair", "AC not cooling often happens due to gas leakage, dirty filters, or compressor/fan issues. An AC technician can diagnose and repair it."),
("cleaning service", "Deep cleaning helps with dust, stains, bathroom/kitchen cleaning, and sofa/carpet cleaning for better hygiene."),
("pest control", "Pest control helps remove cockroaches, termites, bed bugs, rats, and mosquitoes safely."),

# ================= PROFESSIONAL SERVICES =================
("chartered accountant", "For GST, ITR, TDS, audits, or accounting work, a Chartered Accountant can handle filings and compliance."),
("lawyer", "Legal issues like notices, agreements, property disputes, or court matters can be guided by a lawyer."),
("real estate agent", "Real estate agents help with buying, selling, or renting property and finding suitable options quickly."),

# ================= DIGITAL / CREATIVE =================
("web developer", "If you need a website, fixes, redesign, or new features, a web developer can build and maintain it."),
("app developer", "App developers build or fix Android/iOS apps, add features, and publish updates."),
("digital marketing agency", "Digital marketing includes SEO, social media, ads, and lead generation to grow your business online."),
("graphic designer", "Graphic designers create logos, posters, branding, banners, and social media creatives."),
("photographer", "Photographers help with weddings, events, portraits, product shoots, and professional photos."),
("video editor", "Video editors can edit reels, YouTube videos, wedding videos, add effects, and improve quality."),
("interior designer", "Interior designers help plan space, decor, modular kitchen, lighting, and full home/office design."),

# ================= LOGISTICS =================
("packers and movers", "Packers & movers help with shifting household/office items safely with packing and transport."),
("taxi service", "Taxi services provide local travel, outstation rides, and driver-on-demand options."),
("travel agent", "Travel agents help with bookings, visa guidance, and tour packages."),

]


def main():
    init_db()
    with connect() as conn:
        conn.executemany(
            "INSERT INTO intent_rules(pattern, search_term, priority, enabled) VALUES (?,?,?,?)",
            RULES
        )
        conn.executemany(
            """
            INSERT INTO intent_descriptions(search_term, description)
            VALUES (?,?)
            ON CONFLICT(search_term) DO UPDATE SET description=excluded.description
            """,
            DESCS
        )
        conn.commit()

if __name__ == "__main__":
    main()
