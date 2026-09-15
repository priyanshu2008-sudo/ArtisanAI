# Path to Real Mobile App + Real AI (Production)

This prototype is deliberately API-first so you can evolve without rewriting everything.

## 1. Native / Cross-platform Mobile App
Current: Responsive Web + PWA (Add to Home Screen works on Android/iOS).

Recommended next steps:
1. Keep this Flask (or move to FastAPI) backend on a cloud server (Railway / Render / AWS).
2. Wrap the same UI with **Capacitor** (Ionic) → generates Android APK + iOS project.
3. Or rebuild only the UI in **Flutter** / **React Native** and call existing endpoints:
   - POST /api/ai/image-enhance
   - POST /api/ai/voice-description
   - POST /api/ai/pricing
   - GET  /api/v1/catalog
   - Auth + OTP routes

Trusted Web Activity (TWA) is the fastest path to Play Store from this PWA.

## 2. Real AI upgrades (same API contracts)
| Feature | Prototype today | Production swap |
|---------|-----------------|-----------------|
| Background remove | Pillow heuristics | remove.bg API / Segment Anything / custom U-Net |
| Lighting / enhance | Pillow filters | Cloud vision or local ESRGAN |
| Voice → text | Browser SpeechRecognition | Google / Azure Speech (Indic languages) |
| Description NLP | Multilingual templates | IndicBERT / GPT / Gemini with craft prompt |
| Pricing ML | Cost + category + keyword signals | Train regressor on marketplace data + image embeddings |

All production models can sit behind the **same** `/api/ai/*` routes — frontend does not need to change.

## 3. Scalable backend
- Replace SQLite → PostgreSQL
- Add Redis for OTP + sessions
- Object storage (S3) for product images
- Real SMS OTP: MSG91 / Twilio / Fast2SMS
- Payment: Razorpay / PayU (UPI + cards)

## 4. Low-literacy UX principles (already applied)
- Large touch targets
- Icon + short Hindi/English labels
- Step bar (Photo → Describe → Price → Save)
- Voice in + Speak out
- Demo OTP shown on screen for testing

