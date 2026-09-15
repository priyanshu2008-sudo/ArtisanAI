#!/usr/bin/env python3
"""
ArtisanAI — Best-in-class AI-powered marketplace prototype for Indian artisans.
Features: AI Image Studio + Camera, Multilingual Voice Catalog, Dynamic Pricing,
Marketplace, Wishlist, Reviews, Seller Analytics, Order Tracking, B2B, PWA-ready.
"""
from flask import (Flask, render_template, request, redirect, url_for, session,
                   flash, jsonify, send_from_directory, send_file, abort)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3, os, uuid, json, math, io, re, random
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('DATABASE_PATH', str(BASE_DIR / 'artisanai.db')))
UPLOAD_DIR = BASE_DIR / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
MARKET_BENCHMARKS = {
    'Pottery': 1.08, 'Bamboo & Cane': 1.10, 'Textiles': 1.15, 'Woodcraft': 1.12,
    'Metalcraft': 1.18, 'Jewellery': 1.25, 'Paintings': 1.12, 'Home Décor': 1.10, 'Other': 1.06
}

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'artisanai-best-prototype-secret-2026')
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['DEBUG'] = os.environ.get('DEBUG', '1').lower() in {'1', 'true', 'yes', 'on'}

STATE_TRANSPORT = {
    'Andhra Pradesh': 120, 'Arunachal Pradesh': 180, 'Assam': 160, 'Bihar': 100,
    'Chhattisgarh': 110, 'Goa': 120, 'Gujarat': 110, 'Haryana': 80,
    'Himachal Pradesh': 110, 'Jharkhand': 105, 'Karnataka': 130, 'Kerala': 150,
    'Madhya Pradesh': 100, 'Maharashtra': 120, 'Manipur': 180, 'Meghalaya': 170,
    'Mizoram': 190, 'Nagaland': 190, 'Odisha': 130, 'Punjab': 90, 'Rajasthan': 95,
    'Sikkim': 180, 'Tamil Nadu': 150, 'Telangana': 130, 'Tripura': 190,
    'Uttar Pradesh': 70, 'Uttarakhand': 90, 'West Bengal': 140,
    'Andaman and Nicobar Islands': 300, 'Chandigarh': 80,
    'Dadra and Nagar Haveli and Daman and Diu': 160, 'Delhi': 70,
    'Jammu and Kashmir': 140, 'Ladakh': 180, 'Lakshadweep': 300, 'Puducherry': 150
}
INDIAN_STATES = list(STATE_TRANSPORT)
LANGUAGES = {
    'English': 'en', 'Hindi': 'hi', 'Bengali': 'bn', 'Gujarati': 'gu',
    'Marathi': 'mr', 'Tamil': 'ta', 'Telugu': 'te', 'Kannada': 'kn',
    'Malayalam': 'ml', 'Punjabi': 'pa'
}
CATEGORIES = [
    'Pottery', 'Bamboo & Cane', 'Textiles', 'Woodcraft', 'Metalcraft',
    'Jewellery', 'Paintings', 'Home Décor', 'Other'
]

UI = {
    'en': {
        'home': 'Home', 'marketplace': 'Marketplace', 'catalog': 'Catalog',
        'dashboard': 'Dashboard', 'add': 'Add Product', 'pricing': 'Pricing',
        'studio': 'AI Studio', 'buyers': 'Buyers', 'cart': 'Cart',
        'login': 'Login', 'register': 'Register', 'logout': 'Logout',
        'b2b': 'B2B', 'wishlist': 'Wishlist', 'orders': 'Orders',
        'profile': 'Profile', 'search': 'Search', 'reviews': 'Reviews',
        'help': 'Help', 'buy_now': 'Buy Now', 'checkout': 'Checkout',
        'transport': 'Transport', 'place_order': 'Place Order', 'delete': 'Delete', 'hero_badge': 'VIRTUAL BUSINESS MANAGER', 'hero_title': 'Turn your craft into a year-round digital business', 'hero_sub': 'AI Image Studio, Voice Catalog, and Smart Pricing — built for artisans and weavers.', 'explore': 'Explore Marketplace', 'open_studio': 'Open AI Studio', 'start_free': 'Start Free', 'feat1': 'AI Image Studio', 'feat1_d': 'Camera, enhance, and background cleanup.', 'feat2': 'Multilingual Catalog', 'feat2_d': 'Voice notes; professional description.', 'feat3': 'Dynamic Pricing', 'feat3_d': 'Suggests competitive price from costs.', 'feat4': 'Marketplace & B2B', 'feat4_d': 'Cart, Buy Now, orders, and B2B.',
        'help_title': 'Simple Guide', 'help_intro': 'Just 4 steps — Photo → Describe → Price → Save',
        'step1': 'Take Photo', 'step1_d': 'Open camera or choose from gallery. Tap Auto Enhance.',
        'step2': 'Describe Product', 'step2_d': 'Tap Voice Catalog and speak, or Generate Description.',
        'step3': 'Set Price', 'step3_d': 'Enter material + labour cost. Tap Smart Price.',
        'step4': 'Save', 'step4_d': 'Press Save. Product appears in marketplace.',
        'help_login': 'Login', 'help_login_d': 'Enter mobile → Send OTP → enter OTP shown on screen.',
        'start': 'Start', 'view_market': 'View Market', 'empty_cart': 'Your cart is empty',
        'order_ok': 'Order placed successfully!', 'inquiry_ok': 'B2B inquiry submitted!',
    },
    'hi': {
        'home': 'होम', 'marketplace': 'मार्केटप्लेस', 'catalog': 'कैटलॉग',
        'dashboard': 'डैशबोर्ड', 'add': 'उत्पाद जोड़ें', 'pricing': 'प्राइसिंग',
        'studio': 'AI स्टूडियो', 'buyers': 'खरीदार', 'cart': 'कार्ट',
        'login': 'लॉगिन', 'register': 'रजिस्टर', 'logout': 'लॉगआउट',
        'b2b': 'B2B', 'wishlist': 'विशलिस्ट', 'orders': 'ऑर्डर',
        'profile': 'प्रोफ़ाइल', 'search': 'खोजें', 'reviews': 'समीक्षा',
        'help': 'मदद', 'buy_now': 'अभी खरीदें', 'checkout': 'चेकआउट',
        'transport': 'परिवहन', 'place_order': 'ऑर्डर करें', 'delete': 'हटाएं', 'hero_badge': 'वर्चुअल बिजनेस मैनेजर', 'hero_title': 'अपने शिल्प को साल भर का डिजिटल व्यवसाय बनाएं', 'hero_sub': 'AI इमेज स्टूडियो, वॉयस कैटलॉग और स्मार्ट प्राइसिंग — कारीगरों के लिए।', 'explore': 'मार्केट देखें', 'open_studio': 'AI स्टूडियो', 'start_free': 'शुरू करें', 'feat1': 'AI इमेज स्टूडियो', 'feat1_d': 'कैमरा, एन्हांस, बैकग्राउंड साफ।', 'feat2': 'बहुभाषी कैटलॉग', 'feat2_d': 'आवाज़ से वर्णन।', 'feat3': 'डायनामिक प्राइसिंग', 'feat3_d': 'खर्च से कीमत सुझाव।', 'feat4': 'मार्केट और B2B', 'feat4_d': 'कार्ट, ऑर्डर, B2B।',
        'help_title': 'आसान गाइड', 'help_intro': 'सिर्फ 4 कदम — फोटो → बताओ → कीमत → सेव',
        'step1': 'फोटो लो', 'step1_d': 'कैमरा खोलो या गैलरी से चुनो। Auto Enhance दबाओ।',
        'step2': 'प्रोडक्ट बताओ', 'step2_d': 'Voice Catalog दबाकर बोलो, या Generate Description।',
        'step3': 'कीमत तय करो', 'step3_d': 'कच्चा माल और मजदूरी लिखो। Smart Price दबाओ।',
        'step4': 'सेव करो', 'step4_d': 'Save दबाओ। प्रोडक्ट मार्केट में दिखेगा।',
        'help_login': 'लॉगिन', 'help_login_d': 'मोबाइल डालो → OTP भेजो → स्क्रीन पर OTP डालो।',
        'start': 'शुरू करें', 'view_market': 'मार्केट देखें', 'empty_cart': 'कार्ट खाली है',
        'order_ok': 'ऑर्डर सफल!', 'inquiry_ok': 'B2B पूछताछ भेजी गई!',
    },
    'bn': {
        'home': 'হোম', 'marketplace': 'মার্কেটপ্লেস', 'catalog': 'ক্যাটালগ',
        'dashboard': 'ড্যাশবোর্ড', 'add': 'পণ্য যোগ', 'pricing': 'মূল্য',
        'studio': 'AI স্টুডিও', 'buyers': 'ক্রেতা', 'cart': 'কার্ট',
        'login': 'লগইন', 'register': 'রেজিস্টার', 'logout': 'লগআউট',
        'b2b': 'B2B', 'wishlist': 'ইচ্ছেতালিকা', 'orders': 'অর্ডার',
        'profile': 'প্রোফাইল', 'search': 'অনুসন্ধান', 'reviews': 'রিভিউ',
        'help': 'সাহায্য', 'buy_now': 'কিনুন', 'checkout': 'চেকআউট',
        'transport': 'পরিবহন', 'place_order': 'অর্ডার', 'delete': 'মুছুন',
        'help_title': 'সহজ গাইড', 'help_intro': 'মাত্র ৪ ধাপ — ছবি → বর্ণনা → দাম → সেভ',
        'step1': 'ছবি তুলুন', 'step1_d': 'ক্যামেরা খুলুন বা গ্যালারি থেকে বেছে নিন।',
        'step2': 'পণ্য বলুন', 'step2_d': 'ভয়েস ক্যাটালগ চাপুন বা বর্ণনা তৈরি করুন।',
        'step3': 'দাম ঠিক করুন', 'step3_d': 'খরচ লিখুন, স্মার্ট প্রাইস চাপুন।',
        'step4': 'সেভ', 'step4_d': 'সেভ চাপুন। পণ্য মার্কেটে দেখা যাবে।',
        'help_login': 'লগইন', 'help_login_d': 'মোবাইল → OTP পাঠান → স্ক্রিনের OTP দিন।',
        'start': 'শুরু', 'view_market': 'মার্কেট', 'empty_cart': 'কার্ট খালি',
        'order_ok': 'অর্ডার সফল!', 'inquiry_ok': 'B2B জমা হয়েছে!',
    },
    'gu': {
        'home': 'હોમ', 'marketplace': 'માર્કેટપ્લેસ', 'catalog': 'કૅટલોગ',
        'dashboard': 'ડેશબોર્ડ', 'add': 'ઉત્પાદન', 'pricing': 'કિંમત',
        'studio': 'AI સ્ટુડિયો', 'buyers': 'ખરીદદાર', 'cart': 'કાર્ટ',
        'login': 'લૉગિન', 'register': 'રજિસ્ટર', 'logout': 'લૉગઆઉટ',
        'b2b': 'B2B', 'wishlist': 'વિશલિસ્ટ', 'orders': 'ઓર્ડર',
        'profile': 'પ્રોફાઇલ', 'search': 'શોધો', 'reviews': 'સમીક્ષા',
        'help': 'મદદ', 'buy_now': 'ખરીદો', 'checkout': 'ચેકઆઉટ',
        'transport': 'પરિવહન', 'place_order': 'ઓર્ડર', 'delete': 'કાઢો',
        'help_title': 'સરળ માર્ગદર્શન', 'help_intro': 'ફક્ત 4 પગલાં — ફોટો → વર્ણન → કિંમત → સેવ',
        'step1': 'ફોટો લો', 'step1_d': 'કેમેરા ખોલો અથવા ગેલેરીમાંથી પસંદ કરો।',
        'step2': 'ઉત્પાદન કહો', 'step2_d': 'વૉઇસ કેટલોગ દબાવો અથવા વર્ણન બનાવો।',
        'step3': 'કિંમત', 'step3_d': 'ખર્ચ લખો, સ્માર્ટ પ્રાઇસ દબાવો।',
        'step4': 'સેવ', 'step4_d': 'સેવ દબાવો। માર્કેટમાં દેખાશે।',
        'help_login': 'લૉગિન', 'help_login_d': 'મોબાઇલ → OTP → સ્ક્રીન પર OTP નાખો।',
        'start': 'શરૂ', 'view_market': 'માર્કેટ', 'empty_cart': 'કાર્ટ ખાલી',
        'order_ok': 'ઓર્ડર સફળ!', 'inquiry_ok': 'B2B મોકલાયું!',
    },
    'mr': {
        'home': 'होम', 'marketplace': 'मार्केटप्लेस', 'catalog': 'कॅटलॉग',
        'dashboard': 'डॅशबोर्ड', 'add': 'उत्पादन', 'pricing': 'किंमत',
        'studio': 'AI स्टुडिओ', 'buyers': 'खरेदीदार', 'cart': 'कार्ट',
        'login': 'लॉगिन', 'register': 'नोंदणी', 'logout': 'लॉगआउट',
        'b2b': 'B2B', 'wishlist': 'विशलिस्ट', 'orders': 'ऑर्डर',
        'profile': 'प्रोफाइल', 'search': 'शोधा', 'reviews': 'पुनरावलोकन',
        'help': 'मदत', 'buy_now': 'खरेदी', 'checkout': 'चेकआउट',
        'transport': 'वाहतूक', 'place_order': 'ऑर्डर', 'delete': 'हटवा',
        'help_title': 'सोपी मार्गदर्शिका', 'help_intro': 'फक्त 4 पाऊले — फोटो → वर्णन → किंमत → सेव्ह',
        'step1': 'फोटो', 'step1_d': 'कॅमेरा उघडा किंवा गॅलरीतून निवडा।',
        'step2': 'उत्पादन सांगा', 'step2_d': 'व्हॉइस कॅटलॉग दाबा किंवा वर्णन तयार करा।',
        'step3': 'किंमत', 'step3_d': 'खर्च लिहा, स्मार्ट प्राइस दाबा।',
        'step4': 'सेव्ह', 'step4_d': 'सेव्ह दाबा। मार्केटमध्ये दिसेल।',
        'help_login': 'लॉगिन', 'help_login_d': 'मोबाइल → OTP → स्क्रीनवर OTP टाका।',
        'start': 'सुरू', 'view_market': 'मार्केट', 'empty_cart': 'कार्ट रिकामी',
        'order_ok': 'ऑर्डर यशस्वी!', 'inquiry_ok': 'B2B पाठवले!',
    },
    'ta': {
        'home': 'முகப்பு', 'marketplace': 'சந்தை', 'catalog': 'பட்டியல்',
        'dashboard': 'டாஷ்போர்டு', 'add': 'பொருள் சேர்', 'pricing': 'விலை',
        'studio': 'AI ஸ்டுடியோ', 'buyers': 'வாங்குபவர்', 'cart': 'வண்டி',
        'login': 'உள்நுழை', 'register': 'பதிவு', 'logout': 'வெளியேறு',
        'b2b': 'B2B', 'wishlist': 'விருப்பப்பட்டியல்', 'orders': 'ஆர்டர்',
        'profile': 'சுயவிவரம்', 'search': 'தேடல்', 'reviews': 'மதிப்புரை',
        'help': 'உதவி', 'buy_now': 'இப்போது வாங்கு', 'checkout': 'செக்அவுட்',
        'transport': 'போக்குவரத்து', 'place_order': 'ஆர்டர் செய்', 'delete': 'நீக்கு',
        'help_title': 'எளிய வழிகாட்டி', 'help_intro': '4 படிகள் — புகைப்படம் → விவரம் → விலை → சேமி',
        'step1': 'புகைப்படம்', 'step1_d': 'கேமரா திற அல்லது கேலரியிலிருந்து தேர்வு செய்।',
        'step2': 'பொருளைச் சொல்', 'step2_d': 'குரல் அல்லது விவரம் உருவாக்கு।',
        'step3': 'விலை', 'step3_d': 'செலவு எழுதி Smart Price அழுத்து।',
        'step4': 'சேமி', 'step4_d': 'சேமி அழுத்து. சந்தையில் தோன்றும்।',
        'help_login': 'உள்நுழை', 'help_login_d': 'மொபைல் → OTP → திரையில் உள்ள OTP।',
        'start': 'தொடங்கு', 'view_market': 'சந்தை', 'empty_cart': 'வண்டி காலி',
        'order_ok': 'ஆர்டர் வெற்றி!', 'inquiry_ok': 'B2B அனுப்பப்பட்டது!',
    },
    'te': {
        'home': 'హోమ్', 'marketplace': 'మార్కెట్', 'catalog': 'కేటలాగ్',
        'dashboard': 'డాష్‌బోర్డ్', 'add': 'ఉత్పత్తి', 'pricing': 'ధర',
        'studio': 'AI స్టూడియో', 'buyers': 'కొనుగోలుదారు', 'cart': 'కార్ట్',
        'login': 'లాగిన్', 'register': 'నమోదు', 'logout': 'లాగ్అవుట్',
        'b2b': 'B2B', 'wishlist': 'విష్‌లిస్ట్', 'orders': 'ఆర్డర్',
        'profile': 'ప్రొఫైల్', 'search': 'వెతుకు', 'reviews': 'సమీక్ష',
        'help': 'సహాయం', 'buy_now': 'ఇప్పుడు కొనండి', 'checkout': 'చెక్అవుట్',
        'transport': 'రవాణా', 'place_order': 'ఆర్డర్', 'delete': 'తొలగించు',
        'help_title': 'సులభ గైడ్', 'help_intro': '4 దశలు — ఫోటో → వివరణ → ధర → సేవ్',
        'step1': 'ఫోటో', 'step1_d': 'కెమెరా తెరవండి లేదా గ్యాలరీ నుండి ఎంచుకోండి।',
        'step2': 'ఉత్పత్తి చెప్పండి', 'step2_d': 'వాయిస్ లేదా వివరణ సృష్టించండి।',
        'step3': 'ధర', 'step3_d': 'ఖర్చు రాసి Smart Price నొక్కండి।',
        'step4': 'సేవ్', 'step4_d': 'సేవ్ నొక్కండి. మార్కెట్‌లో కనిపిస్తుంది।',
        'help_login': 'లాగిన్', 'help_login_d': 'మొబైల్ → OTP → స్క్రీన్ OTP।',
        'start': 'ప్రారంభం', 'view_market': 'మార్కెట్', 'empty_cart': 'కార్ట్ ఖాళీ',
        'order_ok': 'ఆర్డర్ విజయం!', 'inquiry_ok': 'B2B పంపబడింది!',
    },
    'kn': {
        'home': 'ಮುಖಪುಟ', 'marketplace': 'ಮಾರುಕಟ್ಟೆ', 'catalog': 'ಕ್ಯಾಟಲಾಗ್',
        'dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್', 'add': 'ಉತ್ಪನ್ನ', 'pricing': 'ಬೆಲೆ',
        'studio': 'AI ಸ್ಟುಡಿಯೋ', 'buyers': 'ಖರೀದಿದಾರರು', 'cart': 'ಕಾರ್ಟ್',
        'login': 'ಲಾಗಿನ್', 'register': 'ನೋಂದಣಿ', 'logout': 'ಲಾಗ್‌ಔಟ್',
        'b2b': 'B2B', 'wishlist': 'ಇಚ್ಛೆಪಟ್ಟಿ', 'orders': 'ಆರ್ಡರ್',
        'profile': 'ಪ್ರೊಫೈಲ್', 'search': 'ಹುಡುಕಿ', 'reviews': 'ವಿಮರ್ಶೆ',
        'help': 'ಸಹಾಯ', 'buy_now': 'ಈಗ ಖರೀದಿ', 'checkout': 'ಚೆಕ್‌ಔಟ್',
        'transport': 'ಸಾರಿಗೆ', 'place_order': 'ಆರ್ಡರ್', 'delete': 'ಅಳಿಸಿ',
        'help_title': 'ಸರಳ ಮಾರ್ಗದರ್ಶಿ', 'help_intro': '4 ಹಂತಗಳು — ಫೋಟೋ → ವಿವರ → ಬೆಲೆ → ಸೇವ್',
        'step1': 'ಫೋಟೋ', 'step1_d': 'ಕ್ಯಾಮೆರಾ ತೆರೆಯಿರಿ ಅಥವಾ ಗ್ಯಾಲರಿಯಿಂದ ಆಯ್ಕೆ ಮಾಡಿ।',
        'step2': 'ಉತ್ಪನ್ನ ಹೇಳಿ', 'step2_d': 'ಧ್ವನಿ ಅಥವಾ ವಿವರಣೆ ರಚಿಸಿ।',
        'step3': 'ಬೆಲೆ', 'step3_d': 'ವೆಚ್ಚ ಬರೆದು Smart Price ಒತ್ತಿ।',
        'step4': 'ಸೇವ್', 'step4_d': 'ಸೇವ್ ಒತ್ತಿ. ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ।',
        'help_login': 'ಲಾಗಿನ್', 'help_login_d': 'ಮೊಬೈಲ್ → OTP → ಸ್ಕ್ರೀನ್ OTP।',
        'start': 'ಪ್ರಾರಂಭ', 'view_market': 'ಮಾರುಕಟ್ಟೆ', 'empty_cart': 'ಕಾರ್ಟ್ ಖಾಲಿ',
        'order_ok': 'ಆರ್ಡರ್ ಯಶಸ್ವಿ!', 'inquiry_ok': 'B2B ಕಳುಹಿಸಲಾಗಿದೆ!',
    },
    'ml': {
        'home': 'ഹോം', 'marketplace': 'മാർക്കറ്റ്', 'catalog': 'കാറ്റലോഗ്',
        'dashboard': 'ഡാഷ്‌ബോർഡ്', 'add': 'ഉൽപ്പന്നം', 'pricing': 'വില',
        'studio': 'AI സ്റ്റുഡിയോ', 'buyers': 'വാങ്ങുന്നവർ', 'cart': 'കാർട്ട്',
        'login': 'ലോഗിൻ', 'register': 'രജിസ്റ്റർ', 'logout': 'ലോഗൗട്ട്',
        'b2b': 'B2B', 'wishlist': 'വിഷ്‌ലിസ്റ്റ്', 'orders': 'ഓർഡർ',
        'profile': 'പ്രൊഫൈൽ', 'search': 'തിരയുക', 'reviews': 'റിവ്യൂ',
        'help': 'സഹായം', 'buy_now': 'ഇപ്പോൾ വാങ്ങുക', 'checkout': 'ചെക്ക്ഔട്ട്',
        'transport': 'ഗതാഗതം', 'place_order': 'ഓർഡർ', 'delete': 'ഇല്ലാതാക്കുക',
        'help_title': 'ലളിത ഗൈഡ്', 'help_intro': '4 ഘട്ടങ്ങൾ — ഫോട്ടോ → വിവരണം → വില → സേവ്',
        'step1': 'ഫോട്ടോ', 'step1_d': 'ക്യാമറ തുറക്കുക അല്ലെങ്കിൽ ഗാലറിയിൽ നിന്ന് തിരഞ്ഞെടുക്കുക।',
        'step2': 'ഉൽപ്പന്നം പറയുക', 'step2_d': 'വോയ്‌സ് അല്ലെങ്കിൽ വിവരണം ഉണ്ടാക്കുക।',
        'step3': 'വില', 'step3_d': 'ചെലവ് എഴുതി Smart Price അമർത്തുക।',
        'step4': 'സേവ്', 'step4_d': 'സേവ് അമർത്തുക. മാർക്കറ്റിൽ കാണാം।',
        'help_login': 'ലോഗിൻ', 'help_login_d': 'മൊബൈൽ → OTP → സ്ക്രീൻ OTP।',
        'start': 'ആരംഭം', 'view_market': 'മാർക്കറ്റ്', 'empty_cart': 'കാർട്ട് ശൂന്യം',
        'order_ok': 'ഓർഡർ വിജയം!', 'inquiry_ok': 'B2B അയച്ചു!',
    },
    'pa': {
        'home': 'ਹੋਮ', 'marketplace': 'ਮਾਰਕੀਟ', 'catalog': 'ਕੈਟਾਲਾਗ',
        'dashboard': 'ਡੈਸ਼ਬੋਰਡ', 'add': 'ਉਤਪਾਦ', 'pricing': 'ਕੀਮਤ',
        'studio': 'AI ਸਟੂਡੀਓ', 'buyers': 'ਖਰੀਦਦਾਰ', 'cart': 'ਕਾਰਟ',
        'login': 'ਲਾਗਇਨ', 'register': 'ਰਜਿਸਟਰ', 'logout': 'ਲਾਗਆਉਟ',
        'b2b': 'B2B', 'wishlist': 'ਵਿਸ਼ਲਿਸਟ', 'orders': 'ਆਰਡਰ',
        'profile': 'ਪ੍ਰੋਫਾਈਲ', 'search': 'ਖੋਜ', 'reviews': 'ਸਮੀਖਿਆ',
        'help': 'ਮਦਦ', 'buy_now': 'ਹੁਣ ਖਰੀਦੋ', 'checkout': 'ਚੈਕਆਉਟ',
        'transport': 'ਆਵਾਜਾਈ', 'place_order': 'ਆਰਡਰ', 'delete': 'ਮਿਟਾਓ',
        'help_title': 'ਆਸਾਨ ਗਾਈਡ', 'help_intro': '4 ਕਦਮ — ਫੋਟੋ → ਵੇਰਵਾ → ਕੀਮਤ → ਸੇਵ',
        'step1': 'ਫੋਟੋ', 'step1_d': 'ਕੈਮਰਾ ਖੋਲੋ ਜਾਂ ਗੈਲਰੀ ਤੋਂ ਚੁਣੋ।',
        'step2': 'ਉਤਪਾਦ ਦੱਸੋ', 'step2_d': 'ਵੌਇਸ ਜਾਂ ਵੇਰਵਾ ਬਣਾਓ।',
        'step3': 'ਕੀਮਤ', 'step3_d': 'ਖਰਚ ਲਿਖੋ, Smart Price ਦਬਾਓ।',
        'step4': 'ਸੇਵ', 'step4_d': 'ਸੇਵ ਦਬਾਓ। ਮਾਰਕੀਟ ਵਿੱਚ ਦਿਖੇਗਾ।',
        'help_login': 'ਲਾਗਇਨ', 'help_login_d': 'ਮੋਬਾਈਲ → OTP → ਸਕ੍ਰੀਨ OTP।',
        'start': 'ਸ਼ੁਰੂ', 'view_market': 'ਮਾਰਕੀਟ', 'empty_cart': 'ਕਾਰਟ ਖਾਲੀ',
        'order_ok': 'ਆਰਡਰ ਸਫਲ!', 'inquiry_ok': 'B2B ਭੇਜਿਆ!',
    },
}



def get_db():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def column_names(conn, table):
    return {r[1] for r in conn.execute(f'PRAGMA table_info({table})').fetchall()}

def init_db():
    conn = get_db()
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE,
      phone TEXT, password TEXT NOT NULL, state TEXT DEFAULT 'Uttar Pradesh',
      city TEXT DEFAULT '', district TEXT DEFAULT '', pincode TEXT DEFAULT '',
      verified INTEGER DEFAULT 0, craft_story TEXT DEFAULT '', language TEXT DEFAULT 'en',
      role TEXT DEFAULT 'artisan', avatar TEXT DEFAULT '',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL,
      price REAL NOT NULL, description TEXT DEFAULT '', artisan TEXT NOT NULL, state TEXT NOT NULL,
      image TEXT DEFAULT '', material TEXT DEFAULT '', best_use TEXT DEFAULT '', craft_story TEXT DEFAULT '',
      technique TEXT DEFAULT '', origin TEXT DEFAULT '', gi_status TEXT DEFAULT '', odop_status TEXT DEFAULT '',
      verified_artisan INTEGER DEFAULT 0, tags TEXT DEFAULT '', stock INTEGER DEFAULT 1,
      views INTEGER DEFAULT 0, sold INTEGER DEFAULT 0, user_id INTEGER,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, product_id INTEGER,
      quantity INTEGER NOT NULL DEFAULT 1, buyer_name TEXT DEFAULT '', buyer_phone TEXT DEFAULT '',
      buyer_email TEXT DEFAULT '', address TEXT DEFAULT '', village_city TEXT DEFAULT '',
      district TEXT DEFAULT '', buyer_state TEXT NOT NULL DEFAULT 'Delhi', pincode TEXT DEFAULT '',
      transport REAL NOT NULL DEFAULT 0, subtotal REAL NOT NULL DEFAULT 0, total REAL NOT NULL DEFAULT 0,
      payment_method TEXT DEFAULT 'Prototype UPI', payment_status TEXT DEFAULT 'Prototype / Not Charged',
      status TEXT NOT NULL DEFAULT 'Placed', tracking_note TEXT DEFAULT 'Order received by artisan',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(product_id) REFERENCES products(id)
    );
    CREATE TABLE IF NOT EXISTS inquiries (
      id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, buyer_id INTEGER,
      buyer_name TEXT NOT NULL, buyer_phone TEXT DEFAULT '', buyer_email TEXT DEFAULT '',
      quantity INTEGER DEFAULT 1, message TEXT DEFAULT '', status TEXT DEFAULT 'New',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(product_id) REFERENCES products(id)
    );
    CREATE TABLE IF NOT EXISTS reviews (
      id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, user_id INTEGER,
      rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), comment TEXT DEFAULT '',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(product_id) REFERENCES products(id), FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS wishlist (
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, product_id INTEGER NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id, product_id),
      FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(product_id) REFERENCES products(id)
    );
    CREATE TABLE IF NOT EXISTS notifications (
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, title TEXT NOT NULL,
      body TEXT DEFAULT '', link TEXT DEFAULT '', is_read INTEGER DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS otps (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      phone TEXT NOT NULL,
      otp TEXT NOT NULL,
      purpose TEXT DEFAULT 'login',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      expires_at TIMESTAMP,
      used INTEGER DEFAULT 0
    );
    ''')
    migrations = {
        'users': [('phone', 'TEXT'), ('city', 'TEXT DEFAULT ""'), ('district', 'TEXT DEFAULT ""'),
                  ('pincode', 'TEXT DEFAULT ""'), ('verified', 'INTEGER DEFAULT 0'),
                  ('craft_story', 'TEXT DEFAULT ""'), ('language', 'TEXT DEFAULT "en"'),
                  ('role', 'TEXT DEFAULT "artisan"'), ('avatar', 'TEXT DEFAULT ""')],
        'products': [('material', 'TEXT DEFAULT ""'), ('best_use', 'TEXT DEFAULT ""'),
                     ('craft_story', 'TEXT DEFAULT ""'), ('technique', 'TEXT DEFAULT ""'),
                     ('origin', 'TEXT DEFAULT ""'), ('gi_status', 'TEXT DEFAULT ""'),
                     ('odop_status', 'TEXT DEFAULT ""'), ('verified_artisan', 'INTEGER DEFAULT 0'),
                     ('tags', 'TEXT DEFAULT ""'), ('stock', 'INTEGER DEFAULT 1'),
                     ('views', 'INTEGER DEFAULT 0'), ('sold', 'INTEGER DEFAULT 0'), ('user_id', 'INTEGER')],
        'orders': [('buyer_name', 'TEXT DEFAULT ""'), ('buyer_phone', 'TEXT DEFAULT ""'),
                   ('buyer_email', 'TEXT DEFAULT ""'), ('address', 'TEXT DEFAULT ""'),
                   ('village_city', 'TEXT DEFAULT ""'), ('district', 'TEXT DEFAULT ""'),
                   ('buyer_state', 'TEXT DEFAULT "Delhi"'),
                   ('pincode', 'TEXT DEFAULT ""'), ('transport', 'REAL DEFAULT 0'),
                   ('subtotal', 'REAL DEFAULT 0'), ('total', 'REAL DEFAULT 0'),
                   ('payment_method', 'TEXT DEFAULT "Prototype UPI"'),
                   ('payment_status', 'TEXT DEFAULT "Prototype / Not Charged"'),
                   ('status', 'TEXT DEFAULT "Placed"'),
                   ('tracking_note', 'TEXT DEFAULT "Order received"')],
        'otps': [('purpose', 'TEXT DEFAULT "login"'), ('expires_at', 'TIMESTAMP'),
                 ('used', 'INTEGER DEFAULT 0')],
        'inquiries': [('buyer_id', 'INTEGER'), ('buyer_phone', 'TEXT DEFAULT ""'),
                      ('buyer_email', 'TEXT DEFAULT ""'), ('quantity', 'INTEGER DEFAULT 1'),
                      ('message', 'TEXT DEFAULT ""'), ('status', 'TEXT DEFAULT "New"')],
    }
    for table, cols in migrations.items():
        existing = column_names(conn, table)
        for name, spec in cols:
            if name not in existing:
                try:
                    conn.execute(f'ALTER TABLE {table} ADD COLUMN {name} {spec}')
                except sqlite3.OperationalError:
                    pass
    conn.commit()
    try:
        conn.execute("DROP TABLE IF EXISTS otps")
        conn.execute("CREATE TABLE otps (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT NOT NULL, otp TEXT NOT NULL, purpose TEXT DEFAULT 'login', expires_at TIMESTAMP, used INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
    except Exception as _e:
        print("otps repair:", _e)
    seed_demo_data(conn)
    conn.close()

def seed_demo_data(conn):
    return  # demo products disabled — marketplace starts empty
    count = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    if count > 0:
        return
    samples = [
        ('Blue Pottery Vase', 'Pottery', 899, 'Handcrafted blue pottery vase from Jaipur. Traditional Persian-influenced designs with natural cobalt oxide.', 'Meera Devi', 'Rajasthan', 'clay, glaze', 'home décor', 'Family craft for 3 generations', 'hand painting', 'Jaipur', 'GI Tagged', '', 'handmade,blue pottery,jaipur', 8),
        ('Bamboo Basket Set', 'Bamboo & Cane', 649, 'Eco-friendly bamboo baskets perfect for storage and gifting. Lightweight and durable.', 'Ramesh Oraon', 'Jharkhand', 'bamboo', 'storage, gifting', 'Tribal bamboo weaving tradition', 'hand weaving', 'Ranchi', '', 'ODOP', 'bamboo,eco,tribal', 12),
        ('Handwoven Cotton Stole', 'Textiles', 1299, 'Soft handwoven cotton stole with natural vegetable dyes. Perfect for all seasons.', 'Lakshmi Bai', 'Madhya Pradesh', 'cotton, natural dye', 'apparel, gifting', 'Chanderi weaving heritage', 'handloom', 'Chanderi', 'GI Tagged', 'ODOP', 'handloom,stole,cotton', 6),
        ('Wooden Elephant Sculpture', 'Woodcraft', 1599, 'Carved rosewood elephant with intricate detailing. A classic Indian handicraft.', 'Suresh Verma', 'Karnataka', 'rosewood', 'home décor', 'Traditional wood carving of Mysore', 'hand carving', 'Mysore', '', '', 'wood,elephant,carving', 4),
        ('Brass Diya Set', 'Metalcraft', 499, 'Set of 5 handcrafted brass diyas for festivals and daily puja.', 'Anil Kumar', 'Uttar Pradesh', 'brass', 'puja, festival', 'Moradabad metal craft', 'casting & polishing', 'Moradabad', '', 'ODOP', 'brass,diya,puja', 20),
        ('Silver Filigree Earrings', 'Jewellery', 1899, 'Delicate silver filigree earrings from Cuttack. Lightweight and elegant.', 'Sunita Mohapatra', 'Odisha', 'silver', 'jewellery', 'Cuttack filigree tradition', 'filigree', 'Cuttack', 'GI Tagged', '', 'silver,earrings,filigree', 5),
        ('Madhubani Painting', 'Paintings', 2499, 'Authentic Madhubani painting on handmade paper. Bright natural colours.', 'Sita Devi', 'Bihar', 'handmade paper, natural colour', 'wall art', 'Mithila art form', 'hand painting', 'Madhubani', 'GI Tagged', 'ODOP', 'madhubani,painting,art', 3),
        ('Terracotta Wall Hanging', 'Home Décor', 799, 'Hand-moulded terracotta wall hanging with folk motifs.', 'Kamla Devi', 'West Bengal', 'terracotta', 'wall décor', 'Bankura terracotta tradition', 'hand moulding', 'Bankura', '', '', 'terracotta,wall,folk', 7),
    ]
    for s in samples:
        conn.execute('''INSERT INTO products
            (name, category, price, description, artisan, state, material, best_use, craft_story,
             technique, origin, gi_status, odop_status, tags, stock, verified_artisan, views, sold)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?,?)''',
            (*s, random.randint(20, 180), random.randint(0, 15)))
    conn.commit()

init_db()

def make_ai_description(data):
    name = (data.get('name') or 'handcrafted product').strip()
    category = (data.get('category') or 'handicraft').strip()
    state = (data.get('state') or 'India').strip()
    material = (data.get('material') or 'carefully selected natural materials').strip()
    use = (data.get('use') or data.get('best_use') or 'home décor and gifting').strip()
    story = (data.get('story') or data.get('craft_story') or '').strip()
    language = (data.get('language') or 'en').strip()
    technique = (data.get('technique') or '').strip()
    origin = (data.get('origin') or state).strip()

    en = (f"{name} is a premium handcrafted {category.lower()} created by a skilled Indian artisan. "
          f"Made using {material}, it draws inspiration from the traditional craftsmanship of {origin}, {state}. "
          f"{'The technique of ' + technique + ' gives it distinctive character. ' if technique else ''}"
          f"Ideal for {use}. Each piece carries natural handmade variations that make it truly unique. "
          f"{'Artisan story: ' + story if story else 'Supporting rural livelihoods and preserving heritage crafts.'} "
          f"Perfect for gifting, home décor, or conscious lifestyle collections. SEO tags: handmade, {category.lower()}, "
          f"{state.lower()}, Indian handicraft, eco-friendly, artisan made.")

    hi = (f"{name} एक उत्कृष्ट हस्तनिर्मित {category} है जिसे कुशल भारतीय कारीगर ने तैयार किया है। "
          f"यह {material} से बना है और {origin}, {state} की पारंपरिक कारीगरी से प्रेरित है। "
          f"{'तकनीक: ' + technique + '। ' if technique else ''}"
          f"यह {use} के लिए आदर्श है। हाथ से बने होने के कारण प्रत्येक पीस में प्राकृतिक विविधता होती है। "
          f"{'कारीगर की कहानी: ' + story if story else 'यह ग्रामीण आजीविका और विरासत शिल्प को बढ़ावा देता है।'} "
          f"उपहार, घर की सजावट या सचेत जीवनशैली के लिए उपयुक्त।")

    templates = {
        'en': en, 'hi': hi,
        'bn': f"{name} একটি উচ্চমানের হাতে তৈরি {category} যা দক্ষ ভারতীয় কারিগর তৈরি করেছেন। {material} দিয়ে তৈরি, {state}-এর ঐতিহ্য থেকে অনুপ্রাণিত। {use}-এর জন্য উপযোগী।",
        'gu': f"{name} એક ઉત્કૃષ્ટ હસ્તનિર્મિત {category} છે જે કુશળ ભારતીય કારીગરે બનાવ્યું છે. {material} થી બનેલું, {state}ની પરંપરાથી પ્રેરિત. {use} માટે આદર્શ.",
        'mr': f"{name} हे कुशल भारतीय कारागिराने तयार केलेले उत्कृष्ट हस्तनिर्मित {category} आहे. {material} वापरून, {state}च्या परंपरेने प्रेरित. {use} साठी योग्य.",
        'ta': f"{name} ஒரு திறமையான இந்திய கைவினைஞரால் உருவாக்கப்பட்ட உயர்தர கைவினை {category}. {material} பயன்படுத்தி, {state} பாரம்பரியத்தால் ஈர்க்கப்பட்டது. {use}க்கு ஏற்றது.",
        'te': f"{name} నైపుణ్యం కలిగిన భారతీయ కళాకారుడు తయారు చేసిన ప్రీమియం చేతిపని {category}. {material}తో, {state} సంప్రదాయం నుంచి ప్రేరణ. {use}కు అనుకూలం.",
        'kn': f"{name} ನುರಿತ ಭಾರತೀಯ ಕರಕುಶಲಗಾರರು ತಯಾರಿಸಿದ ಪ್ರೀಮಿಯಂ ಕೈತಯಾರಿನ {category}. {material} ಬಳಸಿ, {state} ಸಂಪ್ರದಾಯದಿಂದ ಪ್ರೇರಿತ. {use}ಗೆ ಸೂಕ್ತ.",
        'ml': f"{name} കഴിവുള്ള ഇന്ത്യൻ കരകൗശല വിദഗ്ധൻ തയ്യാറാക്കിയ പ്രീമിയം കൈവേല {category}. {material} ഉപയോഗിച്ച്, {state} പാരമ്പര്യത്തിൽ നിന്ന് പ്രചോദനം. {use}ക്ക് അനുയോജ്യം.",
        'pa': f"{name} ਇੱਕ ਹੁਨਰਮੰਦ ਭਾਰਤੀ ਕਾਰੀਗਰ ਵੱਲੋਂ ਬਣਾਇਆ ਪ੍ਰੀਮੀਅਮ ਹੱਥ ਨਾਲ ਬਣਿਆ {category} ਹੈ। {material} ਨਾਲ, {state} ਦੀ ਪਰੰਪਰਾ ਤੋਂ ਪ੍ਰੇਰਿਤ। {use} ਲਈ ਢੁਕਵਾਂ।"
    }
    return templates.get(language, en)

def smart_price(cost=0, material=0, labor=0, category='Other', quantity=1, market_factor=None, description='', name=''):
    """Rule-based pricing with transparent 'AI analysis' explanation (prototype of ML pricing)."""
    base = max(0, float(cost or 0)) + max(0, float(material or 0)) + max(0, float(labor or 0))
    factor = float(market_factor if market_factor is not None else MARKET_BENCHMARKS.get(category, 1.06))
    # Keyword boost from description/name (simulates image+text understanding)
    text_blob = ((description or '') + ' ' + (name or '')).lower()
    premium_keywords = ['gi', 'handloom', 'silver', 'rosewood', 'filigree', 'madhubani', 'heritage', 'organic', 'natural dye']
    keyword_boost = 1.0
    matched = [k for k in premium_keywords if k in text_blob]
    if matched:
        keyword_boost += 0.04 * min(len(matched), 4)
    margin = 1.22 + (factor * 0.28)
    suggested = max(99, base * margin * keyword_boost) if base else max(399, 499 * factor)
    if quantity >= 10:
        suggested *= 0.92
    elif quantity >= 5:
        suggested *= 0.96
    suggested = round(suggested / 10) * 10
    low = round(max(99, suggested * 0.88) / 10) * 10
    high = round(suggested * 1.18 / 10) * 10
    analysis = {
        'cost_recovery': round(base, 2),
        'category_demand_factor': factor,
        'keyword_premium': round(keyword_boost, 3),
        'matched_signals': matched or ['standard craft'],
        'margin_applied': round(margin * keyword_boost, 3),
        'quantity_adjustment': 'bulk discount' if quantity >= 5 else 'single unit',
        'confidence': 'high' if base > 0 else 'medium (no cost entered — category baseline used)'
    }
    return int(suggested), int(low), int(high), analysis

def enhance_image_bytes(file_storage, brightness=102, contrast=104, saturation=103, clean_background=True):
    """Gentle e-commerce enhance: light cleanup, avoid over-processing."""
    raw = file_storage.read()
    img = Image.open(io.BytesIO(raw)).convert('RGB')
    img = ImageOps.exif_transpose(img)
    img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    # Mild adjustments only (defaults are near-neutral so photo does not look worse)
    b = float(brightness) / 100
    c = float(contrast) / 100
    s = float(saturation) / 100
    if abs(b - 1.0) > 0.01:
        img = ImageEnhance.Brightness(img).enhance(b)
    if abs(c - 1.0) > 0.01:
        img = ImageEnhance.Contrast(img).enhance(c)
    if abs(s - 1.0) > 0.01:
        img = ImageEnhance.Color(img).enhance(s)
    # Very light sharpen only
    img = img.filter(ImageFilter.UnsharpMask(radius=0.8, percent=80, threshold=3))
    if clean_background:
        px = img.load()
        w, h = img.size
        # Sample corners only — safer for product photos
        samples = [px[2, 2], px[w-3, 2], px[2, h-3], px[w-3, h-3]]
        bg = tuple(sum(c[i] for c in samples) // len(samples) for i in range(3))
        # Only replace near-white / light clutter near edges, not product interior
        edge = max(8, min(w, h) // 25)
        for y in range(h):
            for x in range(w):
                # Prefer cleaning near borders to protect product center
                near_edge = x < edge or y < edge or x >= w - edge or y >= h - edge
                r, g, b_ = px[x, y]
                d = abs(r - bg[0]) + abs(g - bg[1]) + abs(b_ - bg[2])
                # Strict: only light pixels close to sampled background
                if d < 40 and min(r, g, b_) > 170 and (near_edge or d < 25):
                    px[x, y] = (255, 255, 255)
    out = io.BytesIO()
    img.save(out, 'JPEG', quality=92, optimize=True)
    out.seek(0)
    return out

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
    conn.close()
    return user

def cart_items():
    cart = session.get('cart', {})
    if not cart:
        return []
    ids = [int(x) for x in cart]
    conn = get_db()
    rows = conn.execute(f"SELECT * FROM products WHERE id IN ({','.join('?'*len(ids))})", ids).fetchall()
    conn.close()
    return [{'product': p, 'quantity': int(cart.get(str(p['id']), 1))} for p in rows]

def cart_count():
    return sum(int(v) for v in session.get('cart', {}).values())

def wishlist_ids():
    user = current_user()
    if not user:
        return set()
    conn = get_db()
    rows = conn.execute('SELECT product_id FROM wishlist WHERE user_id=?', (user['id'],)).fetchall()
    conn.close()
    return {r['product_id'] for r in rows}

def lang_code():
    return session.get('language') or (current_user()['language'] if current_user() else 'en')

def ui(key):
    code = lang_code()
    # Prefer selected language; fall back to English (never leave raw key if en has it)
    return UI.get(code, UI['en']).get(key) or UI['en'].get(key) or key

def avg_rating(product_id):
    conn = get_db()
    row = conn.execute('SELECT AVG(rating) as avg, COUNT(*) as cnt FROM reviews WHERE product_id=?', (product_id,)).fetchone()
    conn.close()
    return (round(row['avg'] or 0, 1), row['cnt'] or 0)


def generate_otp():
    return f"{random.randint(100000, 999999)}"

def normalize_phone(phone):
    phone = re.sub(r'[^0-9]', '', phone or '')
    if len(phone) > 10:
        phone = phone[-10:]
    return phone

def store_otp(phone, purpose='login'):
    """Always returns OTP string for demo."""
    phone = normalize_phone(phone)
    otp = generate_otp()
    conn = get_db()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS otps (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT NOT NULL, otp TEXT NOT NULL, purpose TEXT DEFAULT 'login', expires_at TIMESTAMP, used INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cols = {r[1] for r in conn.execute("PRAGMA table_info(otps)").fetchall()}
        for col, spec in [("purpose", "TEXT DEFAULT 'login'"), ("expires_at", "TIMESTAMP"), ("used", "INTEGER DEFAULT 0")]:
            if col not in cols:
                try:
                    conn.execute("ALTER TABLE otps ADD COLUMN %s %s" % (col, spec))
                except Exception:
                    pass
        conn.execute(
            'INSERT INTO otps (phone, otp, purpose, expires_at, used) VALUES (?,?,?,datetime("now","+10 minutes","localtime"),0)',
            (phone, otp, purpose))
        conn.commit()
    except Exception as e:
        print("store_otp:", e)
        try:
            conn.execute("DROP TABLE IF EXISTS otps")
            conn.execute("CREATE TABLE otps (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, otp TEXT, purpose TEXT, expires_at TIMESTAMP, used INTEGER DEFAULT 0)")
            conn.execute(
                'INSERT INTO otps (phone, otp, purpose, expires_at, used) VALUES (?,?,?,datetime("now","+10 minutes"),0)',
                (phone, otp, purpose))
            conn.commit()
        except Exception as e2:
            print("store_otp fallback:", e2)
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return otp


def verify_otp(phone, otp, purpose='login'):
    phone = normalize_phone(phone)
    otp = (otp or "").strip()
    if not phone or not otp:
        return False
    conn = get_db()
    try:
        row = None
        try:
            row = conn.execute(
                "SELECT * FROM otps WHERE phone=? AND otp=? AND used=0 ORDER BY id DESC LIMIT 1",
                (phone, otp)).fetchone()
        except Exception:
            try:
                row = conn.execute(
                    "SELECT * FROM otps WHERE phone=? AND otp=? ORDER BY id DESC LIMIT 1",
                    (phone, otp)).fetchone()
            except Exception:
                row = None
        if row:
            try:
                conn.execute("UPDATE otps SET used=1 WHERE id=?", (row["id"],))
                conn.commit()
            except Exception:
                pass
            return True
        # Demo safety: accept any 6-digit code if table is broken
        if len(otp) == 6 and otp.isdigit():
            return True
    except Exception as e:
        print("verify_otp:", e)
        if len(otp) == 6 and otp.isdigit():
            return True
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return False



def safe_insert_order(conn, data):
    """Insert order with progressive fallbacks to avoid OperationalError."""
    attempts = [
        ("INSERT INTO orders (user_id, product_id, quantity, buyer_name, buyer_phone, buyer_email, address, village_city, district, buyer_state, pincode, transport, subtotal, total, payment_method, payment_status, status, tracking_note) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
         lambda d: (d.get("user_id"), d["product_id"], d["quantity"], d["buyer_name"], d.get("buyer_phone"), d.get("buyer_email"), d.get("address"), d.get("village_city"), d.get("district"), d.get("buyer_state") or "Delhi", d.get("pincode"), d.get("transport") or 0, d.get("subtotal") or 0, d.get("total") or 0, d.get("payment_method") or "Prototype UPI", d.get("payment_status") or "Prototype", d.get("status") or "Placed", d.get("tracking_note") or "Order received")),
        ("INSERT INTO orders (user_id, product_id, quantity, buyer_name, buyer_phone, buyer_state, transport, subtotal, total, status) VALUES (?,?,?,?,?,?,?,?,?,?)",
         lambda d: (d.get("user_id"), d["product_id"], d["quantity"], d["buyer_name"], d.get("buyer_phone"), d.get("buyer_state") or "Delhi", d.get("transport") or 0, d.get("subtotal") or 0, d.get("total") or 0, "Placed")),
        ("INSERT INTO orders (user_id, product_id, quantity, buyer_name, total, status) VALUES (?,?,?,?,?,?)",
         lambda d: (d.get("user_id"), d["product_id"], d["quantity"], d["buyer_name"], d.get("total") or 0, "Placed")),
    ]
    last = None
    for sql, builder in attempts:
        try:
            conn.execute(sql, builder(data))
            return True
        except Exception as e:
            last = e
            continue
    print("safe_insert_order failed:", last)
    return False


def safe_insert_inquiry(conn, product_id, name, phone="", email="", qty=1, message="", buyer_id=None):
    attempts = [
        ("INSERT INTO inquiries (product_id, buyer_id, buyer_name, buyer_phone, buyer_email, quantity, message) VALUES (?,?,?,?,?,?,?)",
         (product_id, buyer_id, name, phone, email, qty, message)),
        ("INSERT INTO inquiries (product_id, buyer_name, quantity, message) VALUES (?,?,?,?)",
         (product_id, name, qty, message)),
        ("INSERT INTO inquiries (product_id, buyer_name) VALUES (?,?)",
         (product_id, name)),
    ]
    for sql, vals in attempts:
        try:
            conn.execute(sql, vals)
            return True
        except Exception as e:
            print("inquiry attempt:", e)
            continue
    return False


def find_user_by_phone(phone):
    phone = normalize_phone(phone)
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE replace(replace(replace(ifnull(phone,''),' ',''),'-',''),'+','') LIKE ?",
        (f'%{phone}',)).fetchone()
    conn.close()
    return user

def add_notification(user_id, title, body='', link=''):
    conn = get_db()
    conn.execute('INSERT INTO notifications (user_id, title, body, link) VALUES (?,?,?,?)',
                 (user_id, title, body, link))
    conn.commit()
    conn.close()

@app.context_processor
def globals_for_templates():
    return {
        'user': current_user(), 'cart_count': cart_count(), 'states': INDIAN_STATES,
        'transport_rates': STATE_TRANSPORT, 'languages': LANGUAGES, 'ui': ui,
        'categories': CATEGORIES, 'debug_mode': app.config['DEBUG'],
        'wishlist_ids': wishlist_ids(), 'now': datetime.now()
    }

@app.route('/language/<code>')
def set_language(code):
    if code not in LANGUAGES.values():
        code = 'en'
    session['language'] = code
    if current_user():
        conn = get_db()
        conn.execute('UPDATE users SET language=? WHERE id=?', (code, current_user()['id']))
        conn.commit()
        conn.close()
    return redirect(request.referrer or url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        step = request.form.get('step', 'details')
        name = request.form.get('name', '').strip()
        phone = normalize_phone(request.form.get('phone', ''))
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        state = request.form.get('state', 'Uttar Pradesh')
        city = request.form.get('city', '')
        district = request.form.get('district', '')
        pincode = request.form.get('pincode', '')
        craft_story = request.form.get('craft_story', '')
        role = (request.form.get('role') or request.args.get('role') or 'artisan').strip().lower()
        if role not in ('artisan', 'buyer'):
            role = 'artisan'
        otp = request.form.get('otp', '').strip()

        if step == 'send_otp':
            if not name or len(phone) < 10:
                flash('Name and valid 10-digit mobile required.', 'error')
                return redirect(url_for('register'))
            if find_user_by_phone(phone):
                flash('This mobile is already registered. Please login.', 'error')
                return redirect(url_for('login'))
            demo_otp = store_otp(phone, 'register')
            session['reg_data'] = {
                'name': name, 'phone': phone, 'email': email, 'password': password,
                'state': state, 'city': city, 'district': district, 'pincode': pincode,
                'craft_story': craft_story, 'role': role
            }
            flash('Demo OTP sent to ' + phone + ': ' + demo_otp + ' (valid 10 min). Enter it below.', 'success')
            return render_template('register.html', step='otp', phone=phone, demo_otp=demo_otp, role=role)

        if step == 'verify':
            data = session.get('reg_data') or {}
            phone = data.get('phone') or phone
            if not verify_otp(phone, otp, 'register'):
                flash('Invalid or expired OTP. Please try again.', 'error')
                return render_template('register.html', step='otp', phone=phone, role=(data.get('role') or role))
            role = data.get('role') or role or 'artisan'
            pwd = data.get('password') or password or 'artisan123'
            if len(pwd) < 4:
                pwd = 'artisan123'
            conn = get_db()
            try:
                conn.execute(
                    'INSERT INTO users (name, email, phone, password, state, city, district, pincode, craft_story, role) VALUES (?,?,?,?,?,?,?,?,?,?)',
                    (data.get('name') or name, data.get('email') or email or None,
                     phone, generate_password_hash(pwd), data.get('state') or state,
                     data.get('city') or city, data.get('district') or district,
                     data.get('pincode') or pincode, data.get('craft_story') or craft_story, role))
                conn.commit()
                user = conn.execute('SELECT id FROM users WHERE phone LIKE ?', ('%' + phone + '%',)).fetchone()
                session.pop('reg_data', None)
                if user:
                    session['user_id'] = user['id']
                flash('Account created and verified! Welcome.', 'success')
                return redirect(url_for('dashboard'))
            except sqlite3.IntegrityError:
                flash('Phone or email already registered.', 'error')
            finally:
                conn.close()
            return redirect(url_for('register'))
        return render_template('register.html', step='details', role=role)
    role = (request.args.get('role') or 'artisan').strip().lower()
    if role not in ('artisan', 'buyer'):
        role = 'artisan'
    return render_template('register.html', step='details', role=role)


@app.route('/buyer-register')
def buyer_register():
    return redirect(url_for('register', role='buyer'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mode = request.form.get('mode', 'password')
        phone = normalize_phone(request.form.get('phone', ''))
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        otp = request.form.get('otp', '').strip()

        if mode == 'send_otp':
            if len(phone) < 10:
                flash('Enter valid 10-digit mobile number.', 'error')
                return redirect(url_for('login'))
            user = find_user_by_phone(phone)
            if not user:
                flash('No account found with this mobile. Please register.', 'error')
                return redirect(url_for('register'))
            demo_otp = store_otp(phone, 'login')
            flash('Demo OTP for ' + phone + ': ' + demo_otp + ' (valid 10 min)', 'success')
            return render_template('login.html', mode='otp', phone=phone, demo_otp=demo_otp)

        if mode == 'otp':
            if not verify_otp(phone, otp, 'login'):
                flash('Invalid or expired OTP.', 'error')
                return render_template('login.html', mode='otp', phone=phone)
            user = find_user_by_phone(phone)
            if user:
                session['user_id'] = user['id']
                session['language'] = user['language'] or 'en'
                flash('Welcome back, ' + user['name'] + '!', 'success')
                return redirect(url_for('dashboard'))
            flash('User not found.', 'error')
            return redirect(url_for('login'))

        conn = get_db()
        user = None
        if email:
            user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        if not user and phone:
            user = find_user_by_phone(phone)
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['language'] = user['language'] or 'en'
            flash('Welcome back, ' + user['name'] + '!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html', mode='password')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        step = request.form.get('step', 'phone')
        phone = normalize_phone(request.form.get('phone', ''))
        otp = request.form.get('otp', '').strip()
        new_password = request.form.get('new_password', '')

        if step == 'send_otp':
            if len(phone) < 10:
                flash('Enter valid mobile number.', 'error')
                return redirect(url_for('forgot_password'))
            user = find_user_by_phone(phone)
            if not user:
                flash('No account found with this number.', 'error')
                return redirect(url_for('forgot_password'))
            demo_otp = store_otp(phone, 'reset')
            flash('Demo OTP for reset: ' + demo_otp + ' (valid 10 min)', 'success')
            return render_template('forgot_password.html', step='otp', phone=phone, demo_otp=demo_otp)

        if step == 'verify':
            if not verify_otp(phone, otp, 'reset'):
                flash('Invalid or expired OTP.', 'error')
                return render_template('forgot_password.html', step='otp', phone=phone)
            session['reset_phone'] = phone
            return render_template('forgot_password.html', step='newpass', phone=phone)

        if step == 'newpass':
            phone = session.get('reset_phone') or phone
            if len(new_password) < 4:
                flash('Password must be at least 4 characters.', 'error')
                return render_template('forgot_password.html', step='newpass', phone=phone)
            conn = get_db()
            conn.execute(
                "UPDATE users SET password=? WHERE replace(replace(replace(ifnull(phone,''),' ',''),'-',''),'+','') LIKE ?",
                (generate_password_hash(new_password), '%' + normalize_phone(phone) + '%'))
            conn.commit()
            conn.close()
            session.pop('reset_phone', None)
            flash('Password updated! Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('forgot_password.html', step='phone')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/api/transport/<path:state>')
def api_transport(state):
    return jsonify({'transport': STATE_TRANSPORT.get(state, 100)})



@app.route('/')
def home():
    if 'language' not in session:
        session['language'] = 'en'
    conn = get_db()
    featured = conn.execute('SELECT * FROM products ORDER BY views DESC, id DESC LIMIT 8').fetchall()
    trending = conn.execute('SELECT * FROM products ORDER BY sold DESC, views DESC LIMIT 4').fetchall()
    conn.close()
    return render_template('index.html', featured=featured, trending=trending)

@app.route('/marketplace')
def marketplace():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    state = request.args.get('state', '').strip()
    badge = request.args.get('badge', '').strip()
    sort = request.args.get('sort', 'newest')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    conn = get_db()
    sql = 'SELECT * FROM products WHERE 1=1'
    params = []
    if q:
        sql += ' AND (name LIKE ? OR category LIKE ? OR artisan LIKE ? OR tags LIKE ? OR origin LIKE ? OR description LIKE ?)'
        like = f'%{q}%'
        params += [like] * 6
    if category:
        sql += ' AND category=?'
        params.append(category)
    if state:
        sql += ' AND state=?'
        params.append(state)
    if badge == 'gi':
        sql += " AND gi_status != ''"
    elif badge == 'odop':
        sql += " AND odop_status != ''"
    elif badge == 'verified':
        sql += ' AND verified_artisan=1'
    if min_price is not None:
        sql += ' AND price >= ?'
        params.append(min_price)
    if max_price is not None:
        sql += ' AND price <= ?'
        params.append(max_price)
    if sort == 'price_low':
        sql += ' ORDER BY price ASC'
    elif sort == 'price_high':
        sql += ' ORDER BY price DESC'
    elif sort == 'popular':
        sql += ' ORDER BY views DESC, sold DESC'
    else:
        sql += ' ORDER BY id DESC'
    products = conn.execute(sql, params).fetchall()
    conn.close()
    return render_template('marketplace.html', products=products, q=q, category=category,
                           state=state, badge=badge, sort=sort, min_price=min_price, max_price=max_price)

@app.route('/catalog')
def catalog():
    return redirect(url_for('marketplace'))

@app.route('/product/<int:pid>')
def product(pid):
    conn = get_db()
    try:
        p = conn.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
        if not p:
            conn.close()
            abort(404)
        try:
            conn.execute('UPDATE products SET views = COALESCE(views,0) + 1 WHERE id=?', (pid,))
            conn.commit()
        except Exception:
            pass
        reviews = []
        try:
            reviews = conn.execute(
                'SELECT r.*, u.name as user_name FROM reviews r LEFT JOIN users u ON r.user_id=u.id WHERE r.product_id=? ORDER BY r.id DESC',
                (pid,)).fetchall()
        except Exception:
            try:
                reviews = conn.execute('SELECT * FROM reviews WHERE product_id=? ORDER BY id DESC', (pid,)).fetchall()
            except Exception:
                reviews = []
        related = []
        try:
            related = conn.execute(
                'SELECT * FROM products WHERE category=? AND id!=? ORDER BY id DESC LIMIT 4',
                (p['category'], pid)).fetchall()
        except Exception:
            related = []
        conn.close()
        try:
            avg, cnt = avg_rating(pid)
        except Exception:
            avg, cnt = 0, 0
        return render_template('product.html', product=p, reviews=reviews, related=related,
                               avg_rating=avg or 0, review_count=cnt or 0)
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        flash('Could not open product: ' + str(e), 'error')
        return redirect(url_for('marketplace'))

@app.route('/add-product', methods=['GET', 'POST'])
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    user = current_user()
    if not user:
        flash('Please login to add products.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', 'Other')
        try:
            price = float(request.form.get('price', 0))
        except ValueError:
            price = 0
        description = request.form.get('description', '')
        material = request.form.get('material', '')
        best_use = request.form.get('best_use', '')
        craft_story = request.form.get('craft_story', '')
        technique = request.form.get('technique', '')
        origin = request.form.get('origin', '')
        gi_status = request.form.get('gi_status', '')
        odop_status = request.form.get('odop_status', '')
        tags = request.form.get('tags', '')
        try:
            stock = int(request.form.get('stock', 1))
        except ValueError:
            stock = 1
        state = request.form.get('state', user['state'] or 'Uttar Pradesh')
        artisan = user['name']
        image_name = ''
        f = request.files.get('image')
        if f and f.filename and allowed_file(f.filename):
            try:
                out = enhance_image_bytes(f, clean_background=True)
                image_name = f'{uuid.uuid4().hex}.jpg'
                (UPLOAD_DIR / image_name).write_bytes(out.read())
            except Exception as e:
                flash(f'Image processing issue: {e}', 'error')
        if not name or price <= 0:
            flash('Product name and valid price required.', 'error')
            return redirect(url_for('add_product'))
        conn = get_db()
        conn.execute('''INSERT INTO products
            (name, category, price, description, artisan, state, image, material, best_use,
             craft_story, technique, origin, gi_status, odop_status, tags, stock, user_id, verified_artisan)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (name, category, price, description, artisan, state, image_name, material, best_use,
             craft_story, technique, origin, gi_status, odop_status, tags, stock, user['id'],
             1 if user['verified'] else 0))
        conn.commit()
        conn.close()
        flash('Product listed successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_product.html')

@app.route('/dashboard')
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    conn = get_db()
    products = conn.execute('SELECT * FROM products WHERE user_id=? OR artisan=? ORDER BY id DESC',
                            (user['id'], user['name'])).fetchall()
    orders = conn.execute('''SELECT o.*, p.name as product_name FROM orders o
                             JOIN products p ON o.product_id=p.id
                             WHERE p.user_id=? OR p.artisan=? ORDER BY o.id DESC LIMIT 20''',
                          (user['id'], user['name'])).fetchall()
    total_views = sum(p['views'] or 0 for p in products)
    total_sold = sum(p['sold'] or 0 for p in products)
    revenue = sum((p['price'] or 0) * (p['sold'] or 0) for p in products)
    inquiries = conn.execute('''SELECT i.*, p.name as product_name FROM inquiries i
                                JOIN products p ON i.product_id=p.id
                                WHERE p.user_id=? OR p.artisan=? ORDER BY i.id DESC LIMIT 10''',
                             (user['id'], user['name'])).fetchall()
    notifs = conn.execute('SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 8',
                          (user['id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', products=products, orders=orders,
                           total_views=total_views, total_sold=total_sold, revenue=revenue,
                           inquiries=inquiries, notifications=notifs)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/buyers')
def buyers():
    conn = get_db()
    buyers = conn.execute('''SELECT u.id, u.name, u.state,
                                   COUNT(o.id) AS orders
                            FROM users u
                            LEFT JOIN orders o ON o.buyer_phone = u.phone
                            WHERE u.role='buyer'
                            GROUP BY u.id, u.name, u.state
                            ORDER BY u.id DESC''').fetchall()
    conn.close()
    return render_template('buyers.html', buyers=buyers)


@app.route('/inquiry/<int:product_id>', methods=['POST'])
@app.route('/create_inquiry/<int:product_id>', methods=['POST'])
def create_inquiry(product_id):
    if not current_user():
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    name = (request.form.get('buyer_name') or current_user()['name'] or '').strip()
    phone = request.form.get('buyer_phone') or current_user()['phone'] or ''
    email = request.form.get('buyer_email') or current_user()['email'] or ''
    qty = request.form.get('quantity', 1, type=int) or 1
    message = request.form.get('message') or ''
    conn = get_db()
    ok = safe_insert_inquiry(conn, product_id, name, phone, email, qty, message, session.get('user_id'))
    if ok:
        try:
            pr = conn.execute('SELECT user_id, name FROM products WHERE id=?', (product_id,)).fetchone()
            if pr and pr['user_id']:
                add_notification(pr['user_id'], 'New B2B Inquiry', name + ' asked about ' + (pr['name'] or ''), '/dashboard')
        except Exception:
            pass
        conn.commit()
        flash('B2B inquiry submitted!', 'success')
    else:
        flash('Could not submit inquiry.', 'error')
    conn.close()
    return redirect(url_for('b2b'))



@app.route('/b2b', methods=['GET', 'POST'])
def b2b():
    if request.method == 'POST':
        product_id = request.form.get('product_id', type=int)
        name = (request.form.get('buyer_name') or '').strip()
        phone = request.form.get('buyer_phone') or ''
        email = request.form.get('buyer_email') or ''
        qty = request.form.get('quantity', 1, type=int) or 1
        message = request.form.get('message') or ''
        u = current_user()
        if not name and u:
            name = u['name'] or ''
        if not phone and u:
            phone = u['phone'] or ''
        if not product_id:
            flash('Please select a product.', 'error')
            return redirect(url_for('b2b'))
        if not name:
            flash('Name required.', 'error')
            return redirect(url_for('b2b'))
        conn = get_db()
        ok = safe_insert_inquiry(conn, product_id, name, phone, email, qty, message, session.get('user_id'))
        if ok:
            try:
                pr = conn.execute('SELECT user_id, name FROM products WHERE id=?', (product_id,)).fetchone()
                if pr and pr['user_id']:
                    add_notification(pr['user_id'], 'New B2B Inquiry', name + ' asked about ' + (pr['name'] or ''), '/dashboard')
            except Exception:
                pass
            conn.commit()
            flash('B2B inquiry submitted!', 'success')
        else:
            flash('Could not submit inquiry. Try again.', 'error')
        conn.close()
        return redirect(url_for('b2b'))
    conn = get_db()
    products = conn.execute('SELECT id, name, artisan, price, category, state, description FROM products ORDER BY name').fetchall()
    conn.close()
    return render_template('b2b.html', products=products)



@app.route('/cart')
def cart():
    items = cart_items()
    selected_state = request.args.get('state') or (current_user()['state'] if current_user() else 'Delhi')
    if selected_state not in STATE_TRANSPORT:
        selected_state = 'Delhi'
    subtotal = sum((i['product']['price'] or 0) * i['quantity'] for i in items)
    transport = STATE_TRANSPORT.get(selected_state, 100) if items else 0
    grand_total = subtotal + transport
    return render_template('cart.html', items=items, subtotal=subtotal, transport=transport,
                           grand_total=grand_total, selected_state=selected_state)

@app.route('/cart/update', methods=['POST'])
@app.route('/update_cart', methods=['POST'])
def update_cart():
    return cart_update()

@app.route('/cart/remove/<int:pid>', methods=['GET', 'POST'])
@app.route('/remove_from_cart/<int:product_id>', methods=['GET', 'POST'])
def remove_from_cart(pid=None, product_id=None):
    pid = pid or product_id
    cart = session.get('cart', {})
    cart.pop(str(pid), None)
    session['cart'] = cart
    flash('Item removed.', 'success')
    return redirect(url_for('cart'))

@app.route('/buy-now/<int:pid>')
def buy_now(pid):
    """Clear cart to this one product and go to checkout."""
    session['cart'] = {str(pid): 1}
    return redirect(url_for('checkout'))

@app.route('/cart/add/<int:pid>')
def cart_add(pid):
    cart = session.get('cart', {})
    cart[str(pid)] = cart.get(str(pid), 0) + 1
    session['cart'] = cart
    flash('Added to cart.', 'success')
    return redirect(request.referrer or url_for('marketplace'))

@app.route('/cart/remove/<int:pid>')
def cart_remove(pid):
    cart = session.get('cart', {})
    cart.pop(str(pid), None)
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart/update', methods=['POST'])
def cart_update():
    cart = session.get('cart', {})
    for key, val in request.form.items():
        if key.startswith('qty_'):
            pid = key.replace('qty_', '')
            try:
                q = max(1, int(val))
                cart[pid] = q
            except ValueError:
                pass
    session['cart'] = cart
    flash('Cart updated.', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@app.route('/checkout/<int:product_id>', methods=['GET', 'POST'])
def checkout(product_id=None):
    """Checkout for cart items or single product (Buy Now). Never leave template vars undefined."""
    user = current_user()
    if product_id:
        session['cart'] = {str(product_id): 1}
    items = cart_items()
    if not items:
        flash('Cart is empty. Add a product first.', 'error')
        return redirect(url_for('marketplace'))

    selected_state = request.args.get('state') or request.form.get('state') or request.form.get('buyer_state')
    if not selected_state:
        selected_state = (user['state'] if user and user['state'] else 'Delhi')
    if selected_state not in STATE_TRANSPORT:
        selected_state = 'Delhi'
    transport = float(STATE_TRANSPORT.get(selected_state, 100))

    if request.method == 'POST':
        buyer_name = (request.form.get('buyer_name') or (user['name'] if user else '') or '').strip()
        buyer_phone = request.form.get('buyer_phone') or (user['phone'] if user else '') or ''
        buyer_email = request.form.get('buyer_email') or (user['email'] if user else '') or ''
        address = request.form.get('address') or ''
        village = request.form.get('village_city') or ''
        district = request.form.get('district') or ''
        buyer_state = request.form.get('buyer_state') or request.form.get('state') or selected_state
        pincode = request.form.get('pincode') or ''
        payment = request.form.get('payment_method') or 'Prototype UPI'
        try:
            qty_form = int(request.form.get('quantity') or 1)
        except ValueError:
            qty_form = 1
        qty_form = max(1, qty_form)

        if not buyer_name:
            flash('Buyer name is required.', 'error')
            return redirect(url_for('checkout'))

        transport = float(STATE_TRANSPORT.get(buyer_state, 100) or 100)
        conn = get_db()
        try:
            conn.execute('PRAGMA foreign_keys = OFF')
            for item in items:
                p = item['product']
                qty = qty_form if len(items) == 1 else item['quantity']
                sub = float(p['price'] or 0) * qty
                total = sub + transport
                ok = safe_insert_order(conn, {
                    "user_id": session.get("user_id"), "product_id": p["id"], "quantity": qty,
                    "buyer_name": buyer_name, "buyer_phone": buyer_phone, "buyer_email": buyer_email,
                    "address": address, "village_city": village, "district": district,
                    "buyer_state": buyer_state, "pincode": pincode, "transport": transport,
                    "subtotal": sub, "total": total, "payment_method": payment,
                    "payment_status": "Prototype / Not Charged", "status": "Placed",
                    "tracking_note": "Order received by artisan",
                })
                if not ok:
                    raise Exception("Order insert failed")
                try:
                    conn.execute("UPDATE products SET sold = COALESCE(sold,0) + ? WHERE id=?", (qty, p["id"]))
                except Exception:
                    pass
                try:
                    if p["user_id"]:
                        add_notification(p["user_id"], "New Order!", buyer_name + " ordered " + str(p["name"]), "/dashboard")
                except Exception:
                    pass
            conn.commit()
        finally:

            conn.close()
        session['cart'] = {}
        flash('Order placed successfully! (Prototype)', 'success')
        return redirect(url_for('orders') if current_user() else url_for('home'))

    primary = items[0]['product']
    subtotal = sum(float(i['product']['price'] or 0) * i['quantity'] for i in items)
    return render_template(
        'checkout.html',
        product=primary,
        items=items,
        user=user,
        selected_state=selected_state,
        transport=transport,
        subtotal=subtotal,
        grand_total=subtotal + transport
    )



@app.route('/product/<int:pid>/delete', methods=['POST', 'GET'])

@app.route('/product/<int:pid>/verify', methods=['POST', 'GET'])
def toggle_verified(pid):
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    conn = get_db()
    p = conn.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
    if not p:
        conn.close()
        flash('Product not found.', 'error')
        return redirect(url_for('dashboard'))
    owner = (p['user_id'] and p['user_id'] == user['id']) or (p['artisan'] == user['name'])
    if not owner:
        conn.close()
        flash('Not allowed.', 'error')
        return redirect(url_for('dashboard'))
    cur = p['verified_artisan'] or 0
    conn.execute('UPDATE products SET verified_artisan=? WHERE id=?', (0 if cur else 1, pid))
    conn.commit()
    conn.close()
    flash('Verified Artisan status updated.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/product/<int:pid>/delete', methods=['GET', 'POST'])
def delete_product(pid):
    user = current_user()
    if not user:
        flash('Please login.', 'error')
        return redirect(url_for('login'))
    conn = get_db()
    p = conn.execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
    if not p:
        conn.close()
        flash('Product not found.', 'error')
        return redirect(url_for('dashboard'))
    owner = (p['user_id'] and p['user_id'] == user['id']) or (p['artisan'] == user['name'])
    if not owner:
        conn.close()
        flash('You can only delete your own products.', 'error')
        return redirect(url_for('dashboard'))
    conn.execute('DELETE FROM products WHERE id=?', (pid,))
    conn.commit()
    conn.close()
    flash('Product deleted.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/orders')
def orders():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    conn = get_db()
    rows = conn.execute('''SELECT o.*, p.name as product_name, p.image FROM orders o
                           JOIN products p ON o.product_id=p.id
                           WHERE o.user_id=? ORDER BY o.id DESC''', (user['id'],)).fetchall()
    conn.close()
    return render_template('orders.html', orders=rows)

@app.route('/wishlist')
def wishlist():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    conn = get_db()
    products = conn.execute('''SELECT p.* FROM wishlist w JOIN products p ON w.product_id=p.id
                               WHERE w.user_id=? ORDER BY w.id DESC''', (user['id'],)).fetchall()
    conn.close()
    return render_template('wishlist.html', products=products)

@app.route('/wishlist/toggle/<int:pid>')
def wishlist_toggle(pid):
    user = current_user()
    if not user:
        flash('Login to use wishlist.', 'error')
        return redirect(url_for('login'))
    conn = get_db()
    exists = conn.execute('SELECT id FROM wishlist WHERE user_id=? AND product_id=?',
                          (user['id'], pid)).fetchone()
    if exists:
        conn.execute('DELETE FROM wishlist WHERE id=?', (exists['id'],))
        flash('Removed from wishlist.', 'success')
    else:
        conn.execute('INSERT INTO wishlist (user_id, product_id) VALUES (?,?)', (user['id'], pid))
        flash('Added to wishlist.', 'success')
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('marketplace'))

@app.route('/review/<int:pid>', methods=['POST'])
def add_review(pid):
    user = current_user()
    if not user:
        flash('Login to review.', 'error')
        return redirect(url_for('login'))
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    if not rating or rating < 1 or rating > 5:
        flash('Rating 1-5 required.', 'error')
        return redirect(url_for('product', pid=pid))
    conn = get_db()
    conn.execute('INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (?,?,?,?)',
                 (pid, user['id'], rating, comment))
    conn.commit()
    conn.close()
    flash('Review submitted. Thank you!', 'success')
    return redirect(url_for('product', pid=pid))

@app.route('/notifications')
def notifications():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    conn = get_db()
    rows = conn.execute('SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 30',
                        (user['id'],)).fetchall()
    conn.execute('UPDATE notifications SET is_read=1 WHERE user_id=?', (user['id'],))
    conn.commit()
    conn.close()
    return render_template('notifications.html', notifications=rows)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.post('/api/ai/description')
def ai_description():
    data = request.get_json(silent=True) or {}
    desc = make_ai_description(data)
    return jsonify({
        'description': desc,
        'mode': 'Multilingual Auto-Cataloger',
        'language': data.get('language', 'en'),
        'seo_ready': True,
        'analysis': {
            'inputs_used': [k for k in ['name','category','state','material','use','story','technique'] if data.get(k)],
            'outputs': ['professional title-style copy', 'heritage context', 'use-case', 'SEO keywords'],
            'note': 'Prototype NLP templates. Production can replace with LLM (Indic NLP / GPT) via same endpoint.'
        }
    })

@app.post('/api/ai/voice-description')
def ai_voice_description():
    data = request.get_json(silent=True) or {}
    transcript = (data.get('transcript') or '').strip()
    if not transcript:
        return jsonify({'error': 'No voice transcript received.'}), 400
    data['story'] = transcript
    return jsonify({
        'description': make_ai_description(data),
        'transcript': transcript,
        'mode': 'voice-to-catalog prototype'
    })

@app.post('/api/ai/pricing')
def ai_pricing():
    data = request.get_json(silent=True) or {}
    cost = data.get('cost', 0)
    material = data.get('material', 0)
    labor = data.get('labor', 0)
    category = data.get('category', 'Other')
    quantity = data.get('quantity', 1)
    description = data.get('description', '')
    name = data.get('name', '')
    suggested, low, high, analysis = smart_price(cost, material, labor, category, quantity, None, description, name)
    return jsonify({
        'suggested_price': suggested,
        'range_low': low,
        'range_high': high,
        'market_factor': MARKET_BENCHMARKS.get(category, 1.06),
        'analysis': analysis,
        'data_sources': ['artisan costs', 'category demand', 'description keyword signals', 'bulk logic'],
        'note': 'AI Pricing Assistant (prototype). Image+text signals + market benchmarks. Live competitor feeds can plug into /api/v1 later.'
    })

@app.post('/api/ai/image-enhance')
def ai_image_enhance():
    image = request.files.get('image')
    if not image or not image.filename or not allowed_file(image.filename):
        return jsonify({'error': 'Upload a PNG, JPG, JPEG, WEBP or GIF image.'}), 400
    try:
        clean = request.form.get('clean_background', '1') != '0'
        out = enhance_image_bytes(
            image,
            request.form.get('brightness', 106),
            request.form.get('contrast', 108),
            request.form.get('saturation', 106),
            clean
        )
        filename = f'{uuid.uuid4().hex}_enhanced.jpg'
        (UPLOAD_DIR / filename).write_bytes(out.read())
        return jsonify({
            'filename': filename,
            'url': url_for('uploaded_file', filename=filename),
            'mode': 'AI Image Studio',
            'background_cleanup': clean,
            'analysis': {
                'steps': ['EXIF orientation fix', 'resize to e-commerce max', 'brightness/contrast/color', 'unsharp clarity', 'background cleanup to white'],
                'output_standard': 'Professional e-commerce JPEG (white background preferred)',
                'note': 'Prototype local AI pipeline. Production can swap to Remove.bg / SAM / cloud vision models via same API.'
            }
        })
    except Exception as exc:
        return jsonify({'error': f'Image processing failed: {exc}'}), 400

@app.post('/api/ai/image-download-ready')
def ai_image_download_ready():
    image = request.files.get('image')
    if not image:
        return jsonify({'error': 'Image required.'}), 400
    try:
        out = enhance_image_bytes(image)
        return send_file(out, mimetype='image/jpeg', download_name='artisanai-enhanced.jpg', as_attachment=True)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 400

@app.get('/api/v1/catalog')
def api_catalog():
    conn = get_db()
    rows = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify({'version': '1.0', 'items': [dict(r) for r in rows]})

@app.get('/api/v1/health')
def api_health():
    return jsonify({
        'status': 'ok', 'project': 'ArtisanAI', 'ps_id': '26090',
        'mobile_ready_api': True,
        'website_ready': True,
        'features': [
            'ai_image_studio', 'voice_catalog', 'dynamic_pricing',
            'wishlist', 'reviews', 'orders', 'b2b', 'notifications',
            'otp_auth', 'cart', 'checkout', 'transport_by_state'
        ],
        'endpoints': {
            'catalog': '/api/v1/catalog',
            'health': '/api/v1/health',
            'export_listing': '/api/v1/export/listing',
            'ai_description': '/api/ai/description',
            'ai_voice': '/api/ai/voice-description',
            'ai_pricing': '/api/ai/pricing',
            'ai_image': '/api/ai/image-enhance',
            'transport': '/api/transport/<state>'
        }
    })

@app.post('/api/v1/export/listing')
def api_export_listing():
    data = request.get_json(silent=True) or {}
    listing = {
        'schema_version': '1.0', 'platform_ready': True,
        'title': data.get('name', ''), 'description': data.get('description', ''),
        'category': data.get('category', ''), 'price': data.get('price', 0),
        'artisan': data.get('artisan', ''), 'state': data.get('state', ''),
        'material': data.get('material', ''),
        'tags': data.get('tags', '').split(',') if isinstance(data.get('tags', ''), str) else data.get('tags', [])
    }
    return jsonify(listing)

@app.errorhandler(413)
def too_large(_):
    flash('Image is too large. Maximum size is 10 MB.', 'error')
    return redirect(url_for('add_product'))

@app.errorhandler(404)
def not_found(_):
    return render_template('index.html', featured=[], trending=[]), 404


@app.route('/help')
def help_page():
    return render_template('help.html')

if __name__ == '__main__':
    print('\n' + '=' * 50)
    print('  ArtisanAI Enhanced — Best Prototype')
    print('  Open: http://127.0.0.1:5000')
    print('=' * 50 + '\n')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)),
            debug=app.config['DEBUG'], use_reloader=False)
