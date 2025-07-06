#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thai AI Lawyer - Server Starter
เริ่มต้นเซิร์ฟเวอร์และเปิดหน้าเว็บอัตโนมัติ
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def check_dependencies():
    """ตรวจสอบ dependencies ที่จำเป็น"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pythainlp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ พบ packages ที่ขาดหายไป:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nกรุณาติดตั้งด้วยคำสั่ง:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ Dependencies ทั้งหมดพร้อมใช้งาน")
    return True

def start_server():
    """เริ่มต้น FastAPI server"""
    print("🚀 กำลังเริ่มต้น Thai AI Lawyer Server...")
    
    try:
        # เริ่มต้น server ใน background
        server_process = subprocess.Popen([
            sys.executable, "main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # รอให้ server เริ่มต้น
        print("⏳ รอสักครู่...")
        time.sleep(3)
        
        # ตรวจสอบว่า server ทำงานหรือไม่
        if server_process.poll() is None:
            print("✅ Server เริ่มต้นสำเร็จที่ http://127.0.0.1:8003")
            return server_process
        else:
            stdout, stderr = server_process.communicate()
            print("❌ ไม่สามารถเริ่มต้น server ได้")
            print("Error:", stderr.decode())
            return None
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

def open_browser():
    """เปิดเบราว์เซอร์ไปยังหน้าเว็บ"""
    try:
        # รอสักครู่ให้ server พร้อม
        time.sleep(2)
        
        # เปิดหน้าเว็บ
        webbrowser.open('http://127.0.0.1:8003')
        print("🌐 เปิดเบราว์เซอร์ไปยังหน้าเว็บแล้ว")
        
    except Exception as e:
        print(f"❌ ไม่สามารถเปิดเบราว์เซอร์ได้: {e}")
        print("กรุณาเปิดเบราว์เซอร์และไปที่: http://127.0.0.1:8003")

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 50)
    print("🎯 Thai AI Lawyer - Server Starter")
    print("=" * 50)
    
    # ตรวจสอบ dependencies
    if not check_dependencies():
        return
    
    # ตรวจสอบไฟล์ที่จำเป็น
    required_files = ['main.py', 'law_data.json', 'index.html']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ ไม่พบไฟล์ที่จำเป็น: {', '.join(missing_files)}")
        return
    
    print("✅ ไฟล์ทั้งหมดพร้อมใช้งาน")
    
    # เริ่มต้น server
    server_process = start_server()
    if not server_process:
        return
    
    # เปิดเบราว์เซอร์
    open_browser()
    
    print("\n" + "=" * 50)
    print("🎉 Thai AI Lawyer พร้อมใช้งานแล้ว!")
    print("=" * 50)
    print("📱 หน้าเว็บ: http://127.0.0.1:8003")
    print("📚 API Docs: http://127.0.0.1:8003/docs")
    print("🔧 API Endpoints:")
    print("   - POST /ask - ถามคำถามกฎหมาย")
    print("   - GET /laws - ดูรายการกฎหมายทั้งหมด")
    print("   - GET /search - ค้นหากฎหมาย")
    print("   - GET /categories - ดูหมวดหมูกฎหมาย")
    print("\n💡 กด Ctrl+C เพื่อหยุด server")
    print("=" * 50)
    
    try:
        # รอให้ผู้ใช้กด Ctrl+C
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 กำลังหยุด server...")
        server_process.terminate()
        server_process.wait()
        print("✅ หยุด server แล้ว")

if __name__ == "__main__":
    main() 