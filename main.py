from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import pythainlp
import logging
from typing import List, Optional
import re
from datetime import datetime

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Thai AI Lawyer",
    description="ระบบตอบคำถามกฎหมายไทยอัจฉริยะ",
    version="1.0.0"
)

# เพิ่ม CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# โหลดข้อมูลกฎหมาย
try:
    with open("law_data.json", "r", encoding="utf-8") as f:
        LAW_DATA = json.load(f)
    logger.info(f"โหลดข้อมูลกฎหมายสำเร็จ: {len(LAW_DATA)} ข้อ")
except Exception as e:
    logger.error(f"ไม่สามารถโหลดข้อมูลกฎหมายได้: {e}")
    LAW_DATA = []

class Question(BaseModel):
    question: str
    category: Optional[str] = None

class LawResponse(BaseModel):
    answer: str
    related_laws: List[dict]
    confidence: float
    disclaimer: str
    timestamp: str

@app.get("/", response_class=HTMLResponse)
async def root():
    """หน้าแรกของเว็บไซต์"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
        <head><title>Thai AI Lawyer</title></head>
        <body>
            <h1>Thai AI Lawyer API</h1>
            <p>ยินดีต้อนรับสู่ Thai AI Lawyer API</p>
            <p>กรุณาเปิดไฟล์ index.html ในเบราว์เซอร์</p>
        </body>
        </html>
        """)

@app.post("/ask", response_model=LawResponse)
async def ask_law(question: Question):
    """ถามคำถามกฎหมาย"""
    try:
        q = question.question.strip()
        if not q:
            raise HTTPException(status_code=400, detail="กรุณากรอกคำถาม")
        
        logger.info(f"ได้รับคำถาม: {q}")
        
        # ค้นหาข้อกฎหมายที่เกี่ยวข้อง
        results = search_laws(q, question.category)
        
        if results:
            # สร้างคำตอบ
            answer = create_answer(results, q)
            confidence = calculate_confidence(results, q)
        else:
            answer = "ขออภัย ไม่พบข้อมูลกฎหมายที่เกี่ยวข้องกับคำถามนี้ กรุณาลองใช้คำอื่นหรือปรึกษาทนายความ"
            confidence = 0.0
            results = []
        
        disclaimer = "ข้อมูลนี้เป็นเพียงข้อมูลเบื้องต้น ไม่ใช่คำปรึกษาทางกฎหมายโดยตรง"
        
        return LawResponse(
            answer=answer,
            related_laws=results,
            confidence=confidence,
            disclaimer=disclaimer,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาด: {e}")
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดภายในระบบ")

@app.get("/laws")
async def get_all_laws():
    """ดูรายการกฎหมายทั้งหมด"""
    return {
        "total": len(LAW_DATA),
        "laws": LAW_DATA
    }

@app.get("/search")
async def search_laws_endpoint(q: str, category: Optional[str] = None):
    """ค้นหากฎหมาย"""
    try:
        results = search_laws(q, category)
        return {
            "query": q,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาดในการค้นหา: {e}")
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดในการค้นหา")

@app.get("/categories")
async def get_categories():
    """ดูหมวดหมูกฎหมาย"""
    categories = set()
    for law in LAW_DATA:
        if "category" in law:
            categories.add(law["category"])
    
    return {
        "categories": list(categories),
        "total": len(categories)
    }

def search_laws(query: str, category: Optional[str] = None) -> List[dict]:
    """ค้นหาข้อกฎหมายที่เกี่ยวข้อง - ปรับปรุงให้แม่นยำและครอบคลุมมากขึ้น"""
    query_words = pythainlp.word_tokenize(query, keep_whitespace=False)
    results = []
    
    # คำสำคัญและคำพ้องความหมายที่ครอบคลุม
    keyword_mappings = {
        # อาญา - ความผิดต่อชีวิตและร่างกาย
        'ฆ่า': ['ฆ่า', 'ฆาตกรรม', 'ประหาร', 'ฆ่าคนตาย', 'ฆาตกร', 'ฆาตร'],
        'ทำร้ายร่างกาย': ['ทำร้าย', 'ร่างกาย', 'ตบ', 'ตี', 'ทุบ', 'เตะ', 'ต่อย', 'ชก', 'ทำร้ายร่างกาย', 'บาดเจ็บ'],
        'ชำเรา': ['ชำเรา', 'ข่มขืน', 'อนาจาร', 'ข่มขืนกระทำชำเรา', 'กระทำชำเรา', 'ข่มขืนใจ'],
        'พรากผู้เยาว์': ['พราก', 'ผู้เยาว์', 'เยาว์', 'เด็ก', 'พรากเด็ก', 'ลักพา', 'พาไป'],
        
        # อาญา - ความผิดต่อทรัพย์
        'ลักทรัพย์': ['ลัก', 'ทรัพย์', 'ขโมย', 'ลักขโมย', 'ลักทรัพย์', 'ขโมยของ', 'ลักของ'],
        'ฉ้อโกง': ['ฉ้อ', 'โกง', 'หลอก', 'ฉ้อโกง', 'หลอกลวง', 'โกงกิน', 'ทุจริต'],
        'ปล้น': ['ปล้น', 'ชิง', 'โจร', 'ปล้นทรัพย์', 'ชิงทรัพย์', 'โจรกรรม'],
        'ยักยอก': ['ยักยอก', 'ยักยอกทรัพย์', 'ยักยอกเงิน', 'ยักยอกของ'],
        
        # อาญา - ความผิดต่อความสงบสุข
        'ยาเสพติด': ['ยาเสพติด', 'ยา', 'เสพ', 'ติด', 'เฮโรอีน', 'มอร์ฟีน', 'โคเคน', 'กัญชา', 'ยาบ้า', 'ไอซ์', 'แอมเฟตามีน'],
        'คอร์รัปชัน': ['คอร์รัปชัน', 'ทุจริต', 'รับสินบน', 'สินบน', 'คอร์รัปชั่น', 'ทุจริตคอร์รัปชัน'],
        
        # อาญา - ความผิดเกี่ยวกับคอมพิวเตอร์
        'คอมพิวเตอร์': ['คอมพิวเตอร์', 'ระบบ', 'ข้อมูล', 'แฮก', 'ไวรัส', 'สแปม', 'ลามก', 'เท็จ', 'ไซเบอร์', 'อินเทอร์เน็ต'],
        'แฮก': ['แฮก', 'แฮกเกอร์', 'เข้าถึง', 'เจาะระบบ', 'เจาะข้อมูล'],
        'ไวรัส': ['ไวรัส', 'มัลแวร์', 'สปายแวร์', 'ทรอยจัน', 'แรนซัมแวร์'],
        
        # แพ่ง - สัญญาและหนี้
        'สัญญา': ['สัญญา', 'ข้อตกลง', 'สัญญาซื้อขาย', 'สัญญาเช่า', 'สัญญาจ้าง'],
        'หนี้': ['หนี้', 'เงินกู้', 'เงินยืม', 'ชำระหนี้', 'ผิดนัด', 'ผิดสัญญา'],
        'ละเมิด': ['ละเมิด', 'เสียหาย', 'ค่าสินไหม', 'ชดใช้', 'ชดเชย'],
        
        # แพ่ง - ครอบครัว
        'สมรส': ['สมรส', 'แต่งงาน', 'จดทะเบียนสมรส', 'คู่สมรส'],
        'หย่า': ['หย่า', 'หย่าร้าง', 'เลิกสมรส', 'แยกทาง'],
        'มรดก': ['มรดก', 'พินัยกรรม', 'ทายาท', 'แบ่งมรดก', 'ผู้จัดการมรดก'],
        
        # แพ่ง - ที่ดินและอสังหาริมทรัพย์
        'ที่ดิน': ['ที่ดิน', 'โฉนด', 'กรรมสิทธิ์', 'ภาระจำยอม', 'จำนอง', 'ขายฝาก'],
        
        # ภาษี
        'ภาษี': ['ภาษี', 'vat', 'มูลค่าเพิ่ม', 'เงินได้', 'ยื่นแบบ', 'เสียภาษี', 'สรรพากร'],
        
        # ทรัพย์สินทางปัญญา
        'ลิขสิทธิ์': ['ลิขสิทธิ์', 'ลิขสิทธิ์', 'ละเมิดลิขสิทธิ์'],
        'สิทธิบัตร': ['สิทธิบัตร', 'สิทธิบัตร', 'ละเมิดสิทธิบัตร'],
        'เครื่องหมายการค้า': ['เครื่องหมายการค้า', 'แบรนด์', 'โลโก้', 'เครื่องหมายการค้า'],
        
        # แรงงาน
        'แรงงาน': ['แรงงาน', 'ลูกจ้าง', 'นายจ้าง', 'ไล่ออก', 'เลิกจ้าง', 'ค่าชดเชย'],
        
        # รัฐธรรมนูญ
        'รัฐธรรมนูญ': ['รัฐธรรมนูญ', 'สิทธิ', 'เสรีภาพ', 'รัฐสภา', 'รัฐบาล', 'ศาล'],
        'สิทธิ': ['สิทธิ', 'เสรีภาพ', 'สิทธิพลเมือง', 'สิทธิพื้นฐาน'],
        
        # คำถามทั่วไป
        'โทษ': ['โทษ', 'จำคุก', 'ปรับ', 'ประหาร', 'กักขัง', 'คุมขัง'],
        'อายุ': ['อายุ', 'ปี', 'ขวบ', 'ผู้เยาว์', 'ผู้ใหญ่', 'เด็ก'],
        'เงิน': ['เงิน', 'บาท', 'ค่าปรับ', 'ค่าชดเชย', 'ค่าสินไหม', 'เงินกู้', 'เงินยืม']
    }
    
    # คำหยุดที่ไม่ต้องค้นหา
    stop_words = {'คือ', 'ที่', 'ใน', 'ของ', 'กับ', 'และ', 'หรือ', 'แต่', 'แล้ว', 'จะ', 'ได้', 'ให้', 'มี', 'เป็น', 'อยู่', 'ไป', 'มา', 'ทำ', 'ให้', 'ได้', 'ต้อง', 'ควร', 'จะ', 'อาจ', 'คง', 'น่าจะ', 'คงจะ', 'อาจจะ'}
    
    for law in LAW_DATA:
        # กรองตามหมวดหมู่
        if category and law.get("category") != category:
            continue
            
        # คำนวณคะแนนความเกี่ยวข้อง
        score = 0
        law_text = f"{law.get('title', '')} {law.get('text', '')}".lower()
        query_lower = query.lower()
        
        # 1. ค้นหาตามเลขมาตรา (ให้คะแนนสูงสุด)
        section_match = re.search(r'มาตรา\s*(\d+)', query_lower)
        if section_match:
            section_number = section_match.group(1)
            if section_number in law.get('code', '') or section_number in law.get('title', ''):
                score += 1000  # คะแนนสูงสุดสำหรับการค้นหาตามเลขมาตรา
        
        # 2. ค้นหาตามคำสำคัญและคำพ้องความหมาย
        for keyword_group, synonyms in keyword_mappings.items():
            if any(synonym in query_lower for synonym in synonyms):
                if any(synonym in law_text for synonym in synonyms):
                    score += 50  # คะแนนสูงสำหรับคำสำคัญ
                    
                    # ให้คะแนนเพิ่มถ้าคำสำคัญอยู่ในชื่อมาตรา
                    if any(synonym in law.get('title', '').lower() for synonym in synonyms):
                        score += 30
        
        # 3. ค้นหาตามคำทั่วไป (ยกเว้นคำหยุด)
        for word in query_words:
            word_lower = word.lower()
            if word_lower not in stop_words and len(word_lower) > 1:
                if word_lower in law_text:
                    score += 2
                    
                    # ให้คะแนนเพิ่มถ้าคำอยู่ในชื่อมาตรา
                    if word_lower in law.get('title', '').lower():
                        score += 5
        
        # 4. ค้นหาตามวลีหรือประโยคที่เกี่ยวข้อง
        # แบ่งคำถามเป็นวลี 2-3 คำ
        query_phrases = []
        for i in range(len(query_words) - 1):
            phrase = ' '.join(query_words[i:i+2])
            if len(phrase) > 3:
                query_phrases.append(phrase)
        
        for phrase in query_phrases:
            if phrase.lower() in law_text:
                score += 10
        
        # 5. ค้นหาตามหมวดกฎหมายที่เกี่ยวข้อง
        law_category = law.get('category', '').lower()
        if 'อาญา' in law_category and any(word in query_lower for word in ['ผิด', 'โทษ', 'อาญา', 'จำคุก', 'ปรับ', 'ประหาร']):
            score += 15
        elif 'แพ่ง' in law_category and any(word in query_lower for word in ['สัญญา', 'หนี้', 'ละเมิด', 'มรดก', 'ครอบครัว']):
            score += 15
        elif 'รัฐธรรมนูญ' in law_category and any(word in query_lower for word in ['สิทธิ', 'เสรีภาพ', 'รัฐสภา', 'รัฐบาล']):
            score += 15
        
        # 6. ค้นหาตามบริบทพิเศษ
        # กรณีชำเราผู้เยาว์
        if any(word in query_lower for word in ['ท้อง', 'ทำท้อง', 'ชำเรา', 'ข่มขืน', 'เด็ก', 'ผู้เยาว์']):
            if '277' in law.get('title', '') or '277' in law.get('code', ''):
                score += 200
            elif 'ชำเรา' in law_text:
                score += 150
            elif 'ผู้เยาว์' in law_text:
                score += 100
        
        # กรณีลักทรัพย์
        if any(word in query_lower for word in ['ลัก', 'ขโมย', 'ทรัพย์']):
            if 'ลักทรัพย์' in law_text or 'ขโมย' in law_text:
                score += 100
        
        # กรณีทำร้ายร่างกาย
        if any(word in query_lower for word in ['ทำร้าย', 'ตบ', 'ตี', 'ต่อย']):
            if 'ทำร้าย' in law_text:
                score += 100
        
        # กรณีฆ่า
        if any(word in query_lower for word in ['ฆ่า', 'ฆาตกรรม']):
            if 'ฆ่า' in law_text:
                score += 100
        
        # 7. ค้นหาตามความถี่ของคำ
        for word in query_words:
            word_lower = word.lower()
            if word_lower not in stop_words and len(word_lower) > 1:
                word_count = law_text.count(word_lower)
                if word_count > 0:
                    score += min(word_count, 10)  # จำกัดคะแนนสูงสุดที่ 10
        
        # 8. ค้นหาตามความยาวของคำที่ตรงกัน
        for word in query_words:
            word_lower = word.lower()
            if word_lower not in stop_words and len(word_lower) > 2:
                if word_lower in law_text:
                    score += len(word_lower)  # ยิ่งคำยาวยิ่งให้คะแนนสูง
        
        if score > 0:
            results.append({
                **law,
                "relevance_score": score
            })
    
    # เรียงตามคะแนนความเกี่ยวข้อง
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:10]  # เพิ่มผลลัพธ์เป็น 10 อันดับแรก

def analyze_case(question: str, main_law: dict) -> tuple[str, str, str]:
    """
    วิเคราะห์ข้อเท็จจริงและให้คำแนะนำเชิงปฏิบัติแบบ rule-based ครอบคลุมทุกหมวดกฎหมาย
    ปรับปรุงให้ฉลาดขึ้นสำหรับกรณี 'ทำผู้หญิงท้อง' โดยแยกแยะอายุ ความยินยอม ข่มขืน และแสดงข้อกฎหมายที่เกี่ยวข้องเสมอ
    """
    q = question.lower()
    verdict = ""
    analysis = []
    advice = []
    related_laws = []

    # ตรวจจับอายุและความยินยอม
    is_child = any(word in q for word in ['เด็ก', 'ผู้เยาว์', 'อายุต่ำกว่า', 'อายุไม่เกิน', 'อายุไม่ถึง', 'อายุ 13', 'อายุ 14', 'อายุ 15', 'สิบสาม', '13', 'สิบสี่', '14', 'สิบห้า', '15'])
    is_minor = any(word in q for word in ['อายุ 16', 'อายุ 17', 'อายุ 18', 'สิบหก', '16', 'สิบเจ็ด', '17', 'สิบแปด', '18'])
    is_adult = any(word in q for word in ['อายุ 20', 'อายุ 19', 'อายุ 21', 'บรรลุนิติภาวะ', 'ผู้ใหญ่'])
    is_consent = any(word in q for word in ['ยินยอม', 'เต็มใจ', 'สมยอม'])
    is_rape = any(word in q for word in ['ข่มขืน', 'บังคับ', 'ขู่เข็ญ', 'ข่มขู่', 'ขืนใจ', 'ไม่มีความยินยอม'])
    is_pregnant = any(word in q for word in ['ท้อง', 'ตั้งครรภ์', 'ทำท้อง'])
    is_woman = any(word in q for word in ['ผู้หญิง', 'หญิง', 'เด็กหญิง'])

    # กรณี "ทำผู้หญิงท้อง" หรือ "ทำท้อง"
    if is_pregnant and is_woman:
        if is_child:
            verdict = "❌ ผิด - ฐานชำเราเด็กอายุต่ำกว่า 15 ปี"
            analysis.append("- การมีเพศสัมพันธ์กับเด็กอายุต่ำกว่า 15 ปี ไม่ว่าด้วยความยินยอมหรือไม่ เป็นความผิดตามกฎหมาย")
            analysis.append("- ตามประมวลกฎหมายอาญา มาตรา 277")
            advice.append("- แจ้งผู้ปกครองและแจ้งความกับตำรวจ")
            advice.append("- รวบรวมหลักฐานและพยาน")
            related_laws.append("มาตรา 277")
        elif is_minor:
            verdict = "⚠️ ต้องสอบข้อเท็จจริงเพิ่มเติม"
            analysis.append("- การมีเพศสัมพันธ์กับผู้เยาว์อายุ 15-18 ปี อาจเข้าข่ายความผิด หากไม่มีความยินยอม หรือมีการหลอกลวง ข่มขู่")
            analysis.append("- ต้องตรวจสอบรายละเอียดเพิ่มเติม")
            analysis.append("- ตามประมวลกฎหมายอาญา มาตรา 277, 279, 282")
            advice.append("- ควรปรึกษาทนายความ")
            related_laws.extend(["มาตรา 277", "มาตรา 279", "มาตรา 282"])
        elif is_rape:
            verdict = "❌ ผิด - ฐานข่มขืนกระทำชำเรา"
            analysis.append("- การมีเพศสัมพันธ์โดยไม่มีความยินยอมของฝ่ายหญิง เป็นความผิดฐานข่มขืน")
            analysis.append("- ตามประมวลกฎหมายอาญา มาตรา 276")
            advice.append("- แจ้งความกับตำรวจทันที")
            advice.append("- รวบรวมหลักฐานและพยาน")
            related_laws.append("มาตรา 276")
        elif is_adult and is_consent:
            verdict = "✅ ไม่ผิด - มีความยินยอมและบรรลุนิติภาวะ"
            analysis.append("- การมีเพศสัมพันธ์กับผู้หญิงที่บรรลุนิติภาวะและมีความยินยอม ไม่เป็นความผิดอาญา")
            advice.append("- หากมีปัญหาทางแพ่ง เช่น การเลี้ยงดูบุตร ให้ปรึกษาทนายความ")
        else:
            verdict = "⚠️ ต้องสอบข้อเท็จจริงเพิ่มเติม"
            analysis.append("- ต้องตรวจสอบอายุของฝ่ายหญิงและความยินยอม")
            analysis.append("- หากฝ่ายหญิงอายุต่ำกว่า 15 ปี หรือไม่มีความยินยอม อาจเข้าข่ายความผิดอาญา")
            analysis.append("- หากบรรลุนิติภาวะและมีความยินยอม ไม่เป็นความผิดอาญา")
            advice.append("- ควรสอบถามรายละเอียดเพิ่มเติม หรือปรึกษาทนายความ")
            related_laws.extend(["มาตรา 276", "มาตรา 277"])
    # กรณี "ทำเด็กท้อง" หรือ "ชำเราเด็ก"
    elif is_pregnant and is_child:
        verdict = "❌ ผิด - ฐานชำเราเด็กอายุต่ำกว่า 15 ปี"
        analysis.append("- การมีเพศสัมพันธ์กับเด็กอายุต่ำกว่า 15 ปี ไม่ว่าด้วยความยินยอมหรือไม่ เป็นความผิดตามกฎหมาย")
        analysis.append("- ตามประมวลกฎหมายอาญา มาตรา 277")
        advice.append("- แจ้งผู้ปกครองและแจ้งความกับตำรวจ")
        advice.append("- รวบรวมหลักฐานและพยาน")
        related_laws.append("มาตรา 277")
    # กรณี "ข่มขืน"
    elif is_rape:
        verdict = "❌ ผิด - ฐานข่มขืนกระทำชำเรา"
        analysis.append("- การมีเพศสัมพันธ์โดยไม่มีความยินยอมของฝ่ายหญิง เป็นความผิดฐานข่มขืน")
        analysis.append("- ตามประมวลกฎหมายอาญา มาตรา 276")
        advice.append("- แจ้งความกับตำรวจทันที")
        advice.append("- รวบรวมหลักฐานและพยาน")
        related_laws.append("มาตรา 276")
    # กรณี "มีเพศสัมพันธ์กับเด็ก/ผู้เยาว์"
    elif is_child:
        verdict = "❌ ผิด - ฐานชำเราเด็กอายุต่ำกว่า 15 ปี"
        analysis.append("- การมีเพศสัมพันธ์กับเด็กอายุต่ำกว่า 15 ปี ไม่ว่าด้วยความยินยอมหรือไม่ เป็นความผิดตามกฎหมาย")
        analysis.append("- ตามประมวลกฎหมายอาญา มาตรา 277")
        advice.append("- แจ้งผู้ปกครองและแจ้งความกับตำรวจ")
        advice.append("- รวบรวมหลักฐานและพยาน")
        related_laws.append("มาตรา 277")
    else:
        verdict = "⚠️ ต้องสอบข้อเท็จจริงเพิ่มเติม"
        analysis.append("- ต้องสอบข้อเท็จจริงเกี่ยวกับอายุของฝ่ายหญิงและความยินยอม")
        analysis.append("- หากฝ่ายหญิงอายุต่ำกว่า 15 ปี หรือไม่มีความยินยอม อาจเข้าข่ายความผิดอาญา")
        analysis.append("- หากบรรลุนิติภาวะและมีความยินยอม ไม่เป็นความผิดอาญา")
        advice.append("- ควรสอบถามรายละเอียดเพิ่มเติม หรือปรึกษาทนายความ")
        related_laws.extend(["มาตรา 276", "มาตรา 277"])

    # เพิ่มการแสดงข้อกฎหมายที่เกี่ยวข้องเสมอ
    if related_laws:
        analysis.append("\nข้อกฎหมายที่เกี่ยวข้อง: " + ', '.join(related_laws))

    return verdict, '\n'.join(analysis), '\n'.join(advice)

def create_answer(results: List[dict], question: str) -> str:
    """สร้างคำตอบจากผลการค้นหา พร้อมวิเคราะห์และคำแนะนำ (template มาตรฐาน)"""
    if not results:
        return "ไม่พบข้อมูลที่เกี่ยวข้อง"

    q = question.lower()
    main_law = results[0]
    # เลือก main_law ให้ตรงกับคำถามมากที่สุด
    if any(word in q for word in ['พราก']):
        for law in results:
            if 'พราก' in law.get('title', '') or 'พราก' in law.get('text', ''):
                main_law = law
                break
    elif any(word in q for word in ['ขโมย', 'ลัก', 'ลักทรัพย์']):
        for law in results:
            if any(w in law.get('title', '') for w in ['ลักทรัพย์', 'ขโมย']) or any(w in law.get('text', '') for w in ['ลักทรัพย์', 'ขโมย']):
                main_law = law
                break
    elif any(word in q for word in ['ทำร้าย', 'ตบ', 'ตี']):
        for law in results:
            if 'ทำร้าย' in law.get('title', '') or 'ทำร้าย' in law.get('text', ''):
                main_law = law
                break
    elif any(word in q for word in ['ท้อง', 'ทำท้อง', 'ชำเรา', 'ข่มขืน']):
        for law in results:
            if '277' in law.get('title', '') or '277' in law.get('code', '') or 'ชำเรา' in law.get('title', '') or 'ชำเรา' in law.get('text', ''):
                main_law = law
                break

    # วิเคราะห์ข้อเท็จจริงและคำแนะนำ
    verdict, analysis, advice = analyze_case(question, main_law)

    law_text = main_law.get('text', '')

    answer = f"""
## 🎯 **คำตัดสิน**
{verdict}

## 📋 **ข้อกฎหมายที่เกี่ยวข้อง**
**{main_law.get('title', 'ไม่ระบุชื่อกฎหมาย')}**
{law_text}

## 🔎 **การวิเคราะห์ข้อเท็จจริง**
{analysis}

## 💡 **คำแนะนำเชิงปฏิบัติ**
{advice}

## **หมายเหตุสำคัญ**
ข้อมูลนี้เป็นเพียงข้อมูลเบื้องต้น ไม่ใช่คำปรึกษาทางกฎหมายโดยตรง
"""

    if len(results) > 1:
        answer += "\n## 📚 **ข้อมูลเพิ่มเติม**\n"
        for i, law in enumerate(results[1:3], 1):
            clean_text = law.get('text', '')
            answer += f"**{i}. {law.get('title', 'ไม่ระบุชื่อกฎหมาย')}**\n{clean_text}\n\n"

    return answer.strip()

def calculate_confidence(results: List[dict], question: str) -> float:
    """คำนวณความเชื่อมั่นของคำตอบ"""
    if not results:
        return 0.0
    
    # คำนวณจากคะแนนความเกี่ยวข้อง
    max_score = max(result["relevance_score"] for result in results)
    total_words = len(pythainlp.word_tokenize(question, keep_whitespace=False))
    
    if total_words == 0:
        return 0.0
    
    confidence = min(max_score / total_words, 1.0)
    return round(confidence, 2)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """จัดการข้อผิดพลาดทั่วไป"""
    logger.error(f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "เกิดข้อผิดพลาดภายในระบบ กรุณาลองใหม่อีกครั้ง"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003) 