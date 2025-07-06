import streamlit as st
import requests
import json
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Thai AI Lawyer - ระบบวิเคราะห์กฎหมายไทย",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS สำหรับ Minimal Design
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Thai:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* ตั้งค่าหน้าเว็บ */
    .main {
        background: #fafafa;
        padding: 0;
        font-family: 'Inter', 'Noto Sans Thai', sans-serif;
    }
    
    /* ปรับแต่ง sidebar */
    .css-1d391kg {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    /* ปรับแต่งปุ่ม */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        font-family: 'Inter', 'Noto Sans Thai', sans-serif;
        transition: all 0.2s ease;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        color: #374151;
    }
    
    .stButton > button:hover {
        background: #f9fafb;
        border-color: #d1d5db;
        transform: translateY(-1px);
    }
    
    .stButton > button[data-baseweb="button"] {
        background: #1f2937;
        color: #ffffff;
        border: none;
    }
    
    .stButton > button[data-baseweb="button"]:hover {
        background: #111827;
    }
    
    /* ปรับแต่ง text area */
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-family: 'Inter', 'Noto Sans Thai', sans-serif;
        transition: all 0.2s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* ปรับแต่ง selectbox */
    .stSelectbox select {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-family: 'Inter', 'Noto Sans Thai', sans-serif;
    }
    
    /* ปรับแต่ง expander */
    .streamlit-expanderHeader {
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-weight: 500;
        font-family: 'Inter', 'Noto Sans Thai', sans-serif;
    }
    
    /* ปรับแต่ง warning และ error */
    .stAlert {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-family: 'Inter', 'Noto Sans Thai', sans-serif;
    }
    
    /* ปรับแต่ง spinner */
    .stSpinner {
        border-radius: 8px;
    }
    
    /* ปรับแต่ง markdown */
    .markdown-text-container {
        line-height: 1.6;
        font-family: 'Inter', 'Noto Sans Thai', sans-serif;
    }
    
    /* ปรับแต่ง scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* ปรับแต่ง focus states */
    *:focus {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
    }
    
    /* ปรับแต่ง responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
    }
    
    /* Custom classes */
    .minimal-header {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        color: #ffffff;
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 16px 16px;
    }
    
    .minimal-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .minimal-section {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .minimal-button {
        background: #1f2937;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .minimal-button:hover {
        background: #111827;
        transform: translateY(-1px);
    }
    
    /* Animation สำหรับ pulse effect */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.5;
            transform: scale(1.1);
        }
    }
    
    /* Sidebar specific styles */
    .sidebar-section {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .sidebar-section:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .sidebar-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .sidebar-indicator {
        width: 4px;
        height: 20px;
        border-radius: 2px;
        margin-right: 0.8rem;
    }
    
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    /* Hover effects สำหรับปุ่ม */
    .stButton > button:hover {
        background: #f9fafb;
        border-color: #d1d5db;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Custom selectbox styling */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border: 1px solid #22c55e;
        border-radius: 8px;
        color: #166534;
    }
    
    /* Error message styling */
    .stError {
        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
        border: 1px solid #ef4444;
        border-radius: 8px;
        color: #991b1b;
    }
</style>
""", unsafe_allow_html=True)

# API URL
API_URL = "http://localhost:8003"

def main():
    # Header แบบ Minimal
    st.markdown("""
    <div class="minimal-header">
        <div style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.025em;">
                Thai AI Lawyer
            </div>
            <div style="font-size: 1.1rem; font-weight: 400; opacity: 0.9; margin-bottom: 1rem;">
                ระบบวิเคราะห์และให้คำปรึกษากฎหมายไทย
            </div>
            <div style="font-size: 0.9rem; opacity: 0.8; background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 6px; display: inline-block;">
                พัฒนาโดยทีมงานผู้เชี่ยวชาญด้านกฎหมายและเทคโนโลยี
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar แบบ Minimal ที่ปรับปรุงแล้ว
    with st.sidebar:
        # Header ของ Sidebar
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <div style="font-size: 1.3rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem; letter-spacing: -0.025em;">
                ตัวเลือกการค้นหา
            </div>
            <div style="font-size: 0.9rem; color: #d1d5db; opacity: 0.9;">
                เลือกหมวดหมู่และตัวเลือกที่ต้องการ
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # หมวดหมู่กฎหมาย - ปรับปรุง UI
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="width: 4px; height: 20px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 2px; margin-right: 0.8rem;"></div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #1f2937;">เลือกหมวดหมู่</div>
            </div>
        """, unsafe_allow_html=True)
        
        categories = ["ทั้งหมด", "กฎหมายอาญา", "กฎหมายแพ่ง", "กฎหมายแรงงาน", "กฎหมายครอบครัว", "กฎหมายมรดก", "กฎหมายที่ดิน", "กฎหมายภาษี", "กฎหมายทรัพย์สินทางปัญญา", "กฎหมายคอมพิวเตอร์", "กฎหมายยาเสพติด"]
        selected_category = st.selectbox("", categories, index=0, key="category_select")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ตัวเลือกระบบ - ปรับปรุง UI
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="width: 4px; height: 20px; background: linear-gradient(135deg, #10b981, #059669); border-radius: 2px; margin-right: 0.8rem;"></div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #1f2937;">ตัวเลือกระบบ</div>
            </div>
        """, unsafe_allow_html=True)
        
        # ปุ่มควบคุมแบบใหม่
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("ดูกฎหมายทั้งหมด", use_container_width=True, key="view_laws"):
                try:
                    response = requests.get(f"{API_URL}/laws")
                    if response.status_code == 200:
                        laws = response.json()
                        st.session_state.show_laws = True
                        st.session_state.laws_data = laws
                        st.success("โหลดข้อมูลกฎหมายสำเร็จ!")
                    else:
                        st.error("ไม่สามารถโหลดข้อมูลกฎหมายได้")
                except:
                    st.error("ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้")
        
        with col2:
            if st.button("ดูหมวดหมู่", use_container_width=True, key="view_categories"):
                try:
                    response = requests.get(f"{API_URL}/categories")
                    if response.status_code == 200:
                        categories_data = response.json()
                        st.session_state.show_categories = True
                        st.session_state.categories_data = categories_data
                        st.success("โหลดหมวดหมู่สำเร็จ!")
                    else:
                        st.error("ไม่สามารถโหลดหมวดหมู่ได้")
                except:
                    st.error("ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ข้อมูลระบบ - ปรับปรุง UI
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border: 1px solid #cbd5e1; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="width: 4px; height: 20px; background: linear-gradient(135deg, #f59e0b, #d97706); border-radius: 2px; margin-right: 0.8rem;"></div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #1f2937;">ข้อมูลระบบ</div>
            </div>
            <div style="background: #ffffff; border-radius: 8px; padding: 1rem; border: 1px solid #e2e8f0;">
                <div style="display: grid; gap: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9;">
                        <span style="font-weight: 500; color: #64748b;">เวอร์ชัน</span>
                        <span style="font-weight: 600; color: #1f2937; background: #f1f5f9; padding: 0.2rem 0.6rem; border-radius: 4px;">2.0.0</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9;">
                        <span style="font-weight: 500; color: #64748b;">ฐานข้อมูล</span>
                        <span style="font-weight: 600; color: #1f2937; background: #f1f5f9; padding: 0.2rem 0.6rem; border-radius: 4px;">1,219 ข้อ</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9;">
                        <span style="font-weight: 500; color: #64748b;">หมวดหมู่</span>
                        <span style="font-weight: 600; color: #1f2937; background: #f1f5f9; padding: 0.2rem 0.6rem; border-radius: 4px;">29 หมวด</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0;">
                        <span style="font-weight: 500; color: #64748b;">อัปเดตล่าสุด</span>
                        <span style="font-weight: 600; color: #1f2937; background: #f1f5f9; padding: 0.2rem 0.6rem; border-radius: 4px;">""" + datetime.now().strftime("%d/%m/%Y") + """</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # คำแนะนำการใช้งาน - ปรับปรุง UI
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 1px solid #f59e0b; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="width: 4px; height: 20px; background: linear-gradient(135deg, #f59e0b, #d97706); border-radius: 2px; margin-right: 0.8rem;"></div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #92400e;">คำแนะนำการใช้งาน</div>
            </div>
            <div style="background: #ffffff; border-radius: 8px; padding: 1rem; border: 1px solid #fde68a;">
                <div style="display: grid; gap: 0.8rem;">
                    <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                        <div style="width: 6px; height: 6px; background: #f59e0b; border-radius: 50%; margin-top: 0.5rem; flex-shrink: 0;"></div>
                        <span style="font-size: 0.9rem; color: #92400e; line-height: 1.5;">ใช้คำถามที่ชัดเจนและเฉพาะเจาะจง</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                        <div style="width: 6px; height: 6px; background: #f59e0b; border-radius: 50%; margin-top: 0.5rem; flex-shrink: 0;"></div>
                        <span style="font-size: 0.9rem; color: #92400e; line-height: 1.5;">ระบุหมวดหมู่กฎหมายที่เกี่ยวข้อง</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                        <div style="width: 6px; height: 6px; background: #f59e0b; border-radius: 50%; margin-top: 0.5rem; flex-shrink: 0;"></div>
                        <span style="font-size: 0.9rem; color: #92400e; line-height: 1.5;">อ่านหมายเหตุสำคัญทุกครั้ง</span>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                        <div style="width: 6px; height: 6px; background: #f59e0b; border-radius: 50%; margin-top: 0.5rem; flex-shrink: 0;"></div>
                        <span style="font-size: 0.9rem; color: #92400e; line-height: 1.5;">ปรึกษาทนายความสำหรับคดีความจริงจัง</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # สถานะการเชื่อมต่อ
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); border: 1px solid #22c55e; border-radius: 10px; padding: 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%; animation: pulse 2s infinite;"></div>
                        <span style="font-weight: 600; color: #166534;">ระบบพร้อมใช้งาน</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #15803d;">เชื่อมต่อกับเซิร์ฟเวอร์สำเร็จ</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); border: 1px solid #ef4444; border-radius: 10px; padding: 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="width: 8px; height: 8px; background: #ef4444; border-radius: 50%;"></div>
                        <span style="font-weight: 600; color: #991b1b;">ไม่สามารถเชื่อมต่อ</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #dc2626;">ตรวจสอบการเชื่อมต่อเซิร์ฟเวอร์</div>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); border: 1px solid #ef4444; border-radius: 10px; padding: 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="width: 8px; height: 8px; background: #ef4444; border-radius: 50%;"></div>
                    <span style="font-weight: 600; color: #991b1b;">ไม่สามารถเชื่อมต่อ</span>
                </div>
                <div style="font-size: 0.8rem; color: #dc2626;">ตรวจสอบการเชื่อมต่อเซิร์ฟเวอร์</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # ช่องกรอกคำถามแบบ Minimal
        st.markdown("""
        <div class="minimal-card">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 1.4rem; font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">
                    สอบถามข้อมูลกฎหมาย
                </div>
                <div style="font-size: 0.95rem; color: #6b7280;">
                    กรอกคำถามของคุณเพื่อรับการวิเคราะห์ทางกฎหมาย
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        question = st.text_area(
            "คำถามของคุณ",
            placeholder="เช่น โดนไล่ออกจากงานโดยไม่บอกล่วงหน้าทำอย่างไร? การพรากเด็กอายุต่ำกว่า 18 ปีมีโทษอย่างไร?",
            height=120,
            help="กรุณากรอกคำถามที่ชัดเจนและเฉพาะเจาะจง"
        )
        
        # หมวดหมู่ที่เลือก
        category = None
        if selected_category != "ทั้งหมด":
            category = selected_category
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("วิเคราะห์กฎหมาย", type="primary", use_container_width=True):
                if question.strip():
                    ask_question(question, category)
                else:
                    st.warning("กรุณากรอกคำถามก่อนดำเนินการ")
        
        with col_btn2:
            if st.button("ล้างคำถาม", use_container_width=True):
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # แสดงผลลัพธ์
        if 'answer' in st.session_state and st.session_state.answer is not None:
            display_answer()
        
        # แสดงรายการกฎหมาย
        if st.session_state.get('show_laws', False):
            display_laws()
        
        # แสดงหมวดหมู่
        if st.session_state.get('show_categories', False):
            display_categories()

    # เพิ่มกล่องข้อมูลความน่าเชื่อถือ/ทีมงานด้านล่าง
    st.markdown('''
    <div class="minimal-card" style="margin-top: 3rem; text-align: center;">
        <div style="font-size: 1.3rem; font-weight: 600; color: #1f2937; margin-bottom: 1rem;">
            Thai AI Lawyer
        </div>
        <div style="font-size: 1rem; color: #6b7280; margin-bottom: 1rem; line-height: 1.6;">
            เป็นระบบที่พัฒนาโดยทีมงานผู้เชี่ยวชาญด้านกฎหมายและเทคโนโลยี<br>
            ข้อมูลและคำตอบมีแหล่งอ้างอิงจากกฎหมายไทยที่เชื่อถือได้
        </div>
        <div style="font-size: 0.9rem; color: #3b82f6; font-weight: 500; background: #eff6ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
            โปรดใช้วิจารณญาณและปรึกษาทนายความสำหรับคดีสำคัญ
        </div>
    </div>
    ''', unsafe_allow_html=True)

def ask_question(question, category=None):
    """ส่งคำถามไปยัง API"""
    try:
        with st.spinner("กำลังค้นหาข้อมูล..."):
            payload = {"question": question}
            if category:
                payload["category"] = category
            
            response = requests.post(f"{API_URL}/ask", json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                # ตรวจสอบว่า result ไม่เป็น None และมีข้อมูลที่จำเป็น
                if result and isinstance(result, dict):
                    st.session_state.answer = result
                    st.session_state.question = question
                else:
                    st.error("ได้รับข้อมูลที่ไม่ถูกต้องจากเซิร์ฟเวอร์")
                    st.session_state.answer = None
            else:
                st.error(f"เกิดข้อผิดพลาด: {response.status_code}")
                st.session_state.answer = None
    except requests.exceptions.RequestException:
        st.error("ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาตรวจสอบว่าเซิร์ฟเวอร์กำลังทำงานอยู่")
        st.session_state.answer = None
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")
        st.session_state.answer = None

def display_answer():
    """แสดงคำตอบแบบ Minimal Design"""
    try:
        answer_data = st.session_state.get('answer')
        question = st.session_state.get('question', 'ไม่ระบุคำถาม')
        
        # ตรวจสอบข้อมูลก่อนใช้งาน
        if answer_data is None:
            st.error("ไม่พบข้อมูลคำตอบ กรุณาลองใหม่อีกครั้ง")
            return
            
        if not isinstance(answer_data, dict):
            st.error("ข้อมูลคำตอบไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
            return
            
        if 'answer' not in answer_data:
            st.error("ไม่พบคำตอบในข้อมูล กรุณาลองใหม่อีกครั้ง")
            return
        
        # เริ่มต้นการแสดงผลแบบ Minimal
        st.markdown('<div class="minimal-card">', unsafe_allow_html=True)
        
        # หัวข้อหลัก
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 1.6rem; font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">
                สรุปข้อกฎหมาย
            </div>
            <div style="font-size: 1rem; color: #6b7280; font-weight: 400;">
                การวิเคราะห์ทางกฎหมายสำหรับ: "{question}"
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ข้อกฎหมายที่เกี่ยวข้อง
        if answer_data.get('related_laws'):
            st.markdown("""
            <div class="minimal-section">
                <div style="font-size: 1.2rem; font-weight: 600; color: #1f2937; margin-bottom: 1rem;">
                    ข้อกฎหมายที่เกี่ยวข้อง
                </div>
            """, unsafe_allow_html=True)
            
            for i, law in enumerate(answer_data['related_laws'][:3], 1):
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                        <div style="background: #f3f4f6; padding: 0.8rem; border-radius: 6px; border-left: 3px solid #3b82f6;">
                            <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.3rem;">หมวดหมู่</div>
                            <div style="color: #6b7280;">{law.get('category', 'ไม่ระบุ')}</div>
                        </div>
                        <div style="background: #f3f4f6; padding: 0.8rem; border-radius: 6px; border-left: 3px solid #8b5cf6;">
                            <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.3rem;">รหัส</div>
                            <div style="color: #6b7280;">{law.get('code', 'ไม่ระบุ')}</div>
                        </div>
                    </div>
                    <div style="background: #f9fafb; padding: 1rem; border-radius: 6px; border-left: 3px solid #f59e0b; margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">คำอธิบาย</div>
                        <div style="color: #6b7280; line-height: 1.6;">{law['text']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # วิเคราะห์ข้อเท็จจริง
        if answer_data.get('analysis'):
            st.markdown(f"""
            <div class="minimal-section">
                <div style="font-size: 1.2rem; font-weight: 600; color: #1f2937; margin-bottom: 1rem;">
                    วิเคราะห์ข้อเท็จจริง
                </div>
                <div style="font-size: 0.95rem; line-height: 1.6; color: #374151; background: #ffffff; padding: 1.2rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                    {answer_data['analysis']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ข้อควรปฏิบัติ
        if answer_data.get('advice'):
            st.markdown(f"""
            <div class="minimal-section">
                <div style="font-size: 1.2rem; font-weight: 600; color: #1f2937; margin-bottom: 1rem;">
                    คำแนะนำเชิงปฏิบัติ
                </div>
                <div style="font-size: 0.95rem; line-height: 1.6; color: #374151; background: #ffffff; padding: 1.2rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                    {answer_data['advice']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # หมายเหตุสำคัญ
        st.markdown(f"""
        <div class="minimal-section" style="background: #fef2f2; border-color: #fecaca;">
            <div style="font-size: 1.2rem; font-weight: 600; color: #991b1b; margin-bottom: 1rem;">
                หมายเหตุสำคัญ
            </div>
            <div style="font-size: 0.95rem; line-height: 1.6; color: #374151; background: #ffffff; padding: 1.2rem; border-radius: 8px; border: 1px solid #fecaca;">
                {answer_data.get('disclaimer','• ข้อมูลนี้เป็นเพียงแนวทางเบื้องต้น ไม่ใช่คำปรึกษาทางกฎหมายโดยตรง<br>• กฎหมายมีการเปลี่ยนแปลงได้เสมอ ข้อมูลนี้อาจไม่เป็นปัจจุบัน<br>• สำหรับคดีความหรือกรณีซับซ้อน กรุณาปรึกษาทนายความโดยตรง<br>• ระบบนี้ไม่รับผิดชอบต่อการตัดสินใจที่ใช้ข้อมูลนี้เป็นพื้นฐาน')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ข้อมูลเพิ่มเติม
        st.markdown("""
        <div class="minimal-section" style="background: #f8fafc; border-color: #cbd5e1;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #475569; margin-bottom: 1rem; text-align: center;">
                ข้อมูลเพิ่มเติม
            </div>
            <div style="font-size: 0.9rem; color: #64748b; text-align: center; line-height: 1.6;">
                ระบบนี้พัฒนาขึ้นเพื่อให้ข้อมูลเบื้องต้นเท่านั้น<br>
                สำหรับคำปรึกษาทางกฎหมายที่เฉพาะเจาะจง กรุณาติดต่อทนายความหรือหน่วยงานที่เกี่ยวข้อง
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการแสดงผล: {str(e)}")
        if 'answer' in st.session_state:
            del st.session_state.answer
        if 'question' in st.session_state:
            del st.session_state.question

def display_laws():
    """แสดงรายการกฎหมายทั้งหมดแบบ Minimal"""
    st.markdown("""
    <div class="minimal-section">
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 1.6rem; font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">
                รายการกฎหมายทั้งหมด
            </div>
            <div style="font-size: 1rem; color: #6b7280;">
                ฐานข้อมูลกฎหมายไทยที่ครอบคลุมและอัปเดตล่าสุด
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    laws_data = st.session_state.laws_data
    st.markdown(f"""
    <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; text-align: center;">
        <div style="font-size: 1.2rem; font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">
            สถิติฐานข้อมูล
        </div>
        <div style="font-size: 1rem; color: #6b7280;">
            <strong>จำนวนทั้งหมด:</strong> {laws_data['total']} ข้อกฎหมาย
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for i, law in enumerate(laws_data['laws'], 1):
        with st.expander(f"{law['title']}", expanded=False):
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.2rem; margin-bottom: 1rem;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: #f3f4f6; padding: 0.8rem; border-radius: 6px; border-left: 3px solid #3b82f6;">
                        <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.3rem;">หมวดหมู่</div>
                        <div style="color: #6b7280;">{law.get('category', 'ไม่ระบุ')}</div>
                    </div>
                    <div style="background: #f3f4f6; padding: 0.8rem; border-radius: 6px; border-left: 3px solid #8b5cf6;">
                        <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.3rem;">รหัส</div>
                        <div style="color: #6b7280;">{law.get('code', 'ไม่ระบุ')}</div>
                    </div>
                </div>
                <div style="background: #f9fafb; padding: 1rem; border-radius: 6px; border-left: 3px solid #f59e0b; margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">คำอธิบาย</div>
                    <div style="color: #6b7280; line-height: 1.6;">{law.get('description', 'ไม่มีคำอธิบาย')}</div>
                </div>
                <div style="background: #f0fdf4; padding: 1rem; border-radius: 6px; border-left: 3px solid #10b981;">
                    <div style="font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">เนื้อหากฎหมาย</div>
                    <div style="color: #374151; line-height: 1.6; white-space: pre-wrap;">{law['text']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_categories():
    """แสดงหมวดหมูกฎหมายแบบ Minimal"""
    st.markdown("""
    <div class="minimal-section">
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 1.6rem; font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">
                หมวดหมู่กฎหมาย
            </div>
            <div style="font-size: 1rem; color: #6b7280;">
                ระบบจัดหมวดหมู่กฎหมายไทยเพื่อการค้นหาที่สะดวกและรวดเร็ว
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    categories_data = st.session_state.categories_data
    st.markdown(f"""
    <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; text-align: center;">
        <div style="font-size: 1.2rem; font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">
            สถิติหมวดหมู่
        </div>
        <div style="font-size: 1rem; color: #6b7280;">
            <strong>จำนวนหมวดหมู่:</strong> {categories_data['total']} หมวด
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # สร้าง grid layout สำหรับหมวดหมู่
    cols = st.columns(2)
    for i, category in enumerate(categories_data['categories']):
        col_idx = i % 2
        with cols[col_idx]:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size: 1rem; font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">
                    {category}
                </div>
                <div style="font-size: 0.85rem; color: #6b7280; background: #f9fafb; padding: 0.5rem; border-radius: 4px;">
                    กฎหมายที่เกี่ยวข้องกับ{category.lower()}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    # Initialize session state
    if 'answer' not in st.session_state:
        st.session_state.answer = None
    if 'question' not in st.session_state:
        st.session_state.question = None
    if 'show_laws' not in st.session_state:
        st.session_state.show_laws = False
    if 'show_categories' not in st.session_state:
        st.session_state.show_categories = False
    
    main() 