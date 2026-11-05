import requests
import json
import os
import time
import sys
import select
import urllib.parse

API_KEY = "vach_1ytE2CY5X2ERzLhX7GxdbYguiz0pleADjqBKFBrXyOOrCOJiJTFSKTtaugKRj0LM7xkPORwEt11y2hVXKHC7feBg1BIfpNai_196bbc3f513763933dd8c60fbb46e2a9"
EMERGENCY_CONTACT = "91*********"
DEFAULT_EXACT_COORDS = "22.5015,88.3610"

def speak(text_to_speak, lang_code="en-IN"):
    """Calls Gnani Timbre TTS with language support (en-IN, bn-IN, hi-en)"""
    print(f"\nAI Speech ({lang_code}): \"{text_to_speak}\"")
    print(f"[Connecting to Gnani Timbre ({lang_code})...]")
    url = "https://api.vachana.ai/api/v1/tts/inference"
    headers = {"X-API-Key-ID": API_KEY, "Content-Type": "application/json"}
    payload = {
        "text": text_to_speak,
        "voice": "Nalini",
        "model": "timbre-v2.5",
        "language": lang_code,
        "speed": 1.0,
        "audio_config": {
            "sample_rate": 48000,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav"
        }
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"[Server Status]: {res.status_code}")
        if res.status_code == 200:
            with open("response.wav", "wb") as f:
                f.write(res.content)
            print("[Success]: Voice audio generated from Gnani Timbre!")
            print("[Playing Audio...]")
            os.system("play response.wav >/dev/null 2>&1")
        else:
            print(f"[Error Details]: {res.text}")
    except Exception as e:
        print(f"[Connection Error]: {e}")

def trigger_emergency_dispatch(contact_number, reason="Accident"):
    maps_url = f"https://maps.google.com/?q={DEFAULT_EXACT_COORDS}"
    sms_text = f"EMERGENCY ALERT: {reason}. Live GPS Location: {maps_url}"
    encoded_body = urllib.parse.quote(sms_text)
    
    masked = contact_number[:2] + "******" + contact_number[-4:]
    print(f"\n[ACTION TRIGGER]: Pre-filling emergency SMS with live GPS to {masked}...")
    sms_cmd = f"am start -a android.intent.action.VIEW -d \"sms:{contact_number}?body={encoded_body}\" >/dev/null 2>&1"
    os.system(sms_cmd)

def timed_input(prompt, timeout=10):
    print(prompt)
    for remaining in range(timeout, 0, -1):
        sys.stdout.write(f"\r[Time remaining: {remaining}s] Press Enter or Speak if conscious: ")
        sys.stdout.flush()
        rlist, _, _ = select.select([sys.stdin], [], [], 1.0)
        if rlist:
            res = sys.stdin.readline().strip()
            return res if res else "conscious"
    return None

def handle_crash_detection():
    print("\n" + "!" * 55)
    print("CRITICAL ALERT: SEVERE IMPACT DETECTED (G-FORCE EXCEEDED)")
    print("!" * 55)
    
    # Check-in prompt in Hinglish/English for clear understanding
    speak("Severe impact detected. Aap thik hain? Please tap any key if you are conscious.", lang_code="hi-en")
    
    user_status = timed_input("\n[INITIATING CONSCIOUSNESS CHECK]", timeout=10)
    
    if user_status:
        print(f"\n\n[STATUS CONFIRMED]: User responded (\"{user_status}\"). Safety check canceled.")
        speak("Understood. Emergency broadcast canceled. Please take care.", lang_code="en-IN")
    else:
        print("\n\n" + "#" * 55)
        print("[STATUS]: NO RESPONSE DETECTED WITHIN 10 SECONDS.")
        print("[OVERRIDE]: USER UNRESPONSIVE / PRESUMED UNCONSCIOUS.")
        print("#" * 55)
        
        trigger_emergency_dispatch(EMERGENCY_CONTACT, reason="Severe Crash - User Unresponsive")
        
        # Dual-language Bystander Beacon: English followed by Bengali/Hindi
        bystander_msg = "Emergency alert. The owner of this device is unresponsive following a severe crash. Live GPS coordinates have been dispatched. Ekhaney ekjon durghotonay osustho hoye porechhen, doya kore 108 ambulance call korun."
        speak(bystander_msg, lang_code="hi-en")

def handle_voice_query(spoken_text):
    text = spoken_text.lower()
    print("\n" + "=" * 50)
    print(f"User Input: \"{spoken_text}\"")
    print("=" * 50)

    # 1. Bengali Language Intent Detection
    if any(k in text for k in ["hospitale", "ambulance", "daktar", "osukh", "durghotona", "bipod", "pathao"]):
        reply = "Aapnar emergency dispatch register kora hoyeche. Kacher hospitaley gari pathano hochhe ebong poribarer sathe jogajog kora hochhe."
        print("\n[ACTION]: Bengali Emergency Trigger -> Hospital transit & SOS active.")
        trigger_emergency_dispatch(EMERGENCY_CONTACT, reason="Accident Reported (Bengali Voice)")
        speak(reply, lang_code="bn-IN")

    # 2. Hindi / Hinglish Language Intent Detection
    elif any(k in text for k in ["madad", "chot", "bachao", "gaadi", "bhejo", "takkar"]):
        reply = "Emergency mode active hai. Aapke nearest hospital ke liye cab dispatch kar di gayi hai aur family ko alert bhej diya hai."
        print("\n[ACTION]: Hinglish Emergency Trigger -> Hospital transit & SOS active.")
        trigger_emergency_dispatch(EMERGENCY_CONTACT, reason="Accident Reported (Hinglish Voice)")
        speak(reply, lang_code="hi-en")

    # 3. Standard English Intent Detection
    elif any(k in text for k in ["hospital", "emergency", "cab", "doctor", "sick", "accident"]):
        reply = "Emergency mode active. Dispatching an emergency cab to your nearest hospital and sending your location to your emergency contact."
        print("\n[ACTION]: English Emergency Trigger -> Hospital transit & SOS active.")
        trigger_emergency_dispatch(EMERGENCY_CONTACT, reason="Accident Reported (English Voice)")
        speak(reply, lang_code="en-IN")

    else:
        reply = "Hello. Apnar emergency ride ba delivery lagle amake bolun. Kripya apni madad ke baare mein batayein."
        speak(reply, lang_code="hi-en")

if __name__ == "__main__":
    print("\n=== GNANI AI MULTI-LINGUAL EMERGENCY ASSISTANT ===")
    print("1. Interactive Voice Query Mode (English / Bengali / Hinglish)")
    print("2. Crash Detection & Unconscious Victim Simulation")
    mode = input("\nSelect mode (1 or 2): ").strip()
    
    if mode == "2":
        handle_crash_detection()
    else:
        spoken = input("\nEnter or Dictate spoken command: ")
        handle_voice_query(spoken)
