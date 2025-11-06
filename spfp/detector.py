import re

RULES = {
  "SPFP-01": [r"\b(donate|charity|ช่วย|บุญ)\b.*\b(ดังนั้น|therefore)\b"],
  "SPFP-02": [r"\b(unsubscribe|ออกไป|ไสหัว)\b", r"\bคนโง่\b.*\bไม่ต้อนรับ\b"],
  "SPFP-03": [r"\b(ศาล)\b.*\b(ตัดสินก่อน|คิดไม่ได้)\b"],
  "SPFP-04": [r"\b(ส่วนตัว|private)\b.*\b(เปิดเผยไม่ได้)\b"],
  "SPFP-05": [r"\bฉันตรรกะ\b|\bI am logic\b"],
  "SPFP-06": [r"\b(บาป|บุญ|ธรรมะ)\b.*\bห้ามวิจารณ์\b"]
}

def detect(text:str):
    flags, notes = [], []
    for code, patterns in RULES.items():
        if any(re.search(p, text, flags=re.I|re.U) for p in patterns):
            flags.append(code)
    if not flags:
        notes.append("No SPFP pattern detected.")
    return {"flags": flags, "notes": " | ".join(notes)}
