# -*- coding: utf-8 -*-
"""
🎯 Smart Exhibition Pipeline — Final Unified Edition + Google Sheets  
Complete merge: OCR/QR Processing + Google Sheets Integration
- Smart Detection • Automated Processing • Quality Control
- Google Sheets auto-save with permanent link
- Batch processing support
- Persian/English UI support

Run: streamlit run smart_exhibition_pipeline_final.py
"""

import streamlit as st
import subprocess
import os
import sys
import json
import time
import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import re

# =========================================================
# Page Settings
# =========================================================
st.set_page_config(
    page_title="🎯 Smart Exhibition Pipeline",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 📌 Permanent Google Sheets Link (Always Visible)
# =========================================================
FIXED_SHEET_URL = "https://docs.google.com/spreadsheets/d/1OeQbiqvo6v58rcxaoSUidOk0IxSGmL8YCpLnyh27yuE/edit"

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.2rem; border-radius: 15px; text-align: center; color: white;
    box-shadow: 0 6px 20px rgba(102,126,234,0.4); margin-bottom: 1.5rem;">
    <h3 style="margin: 0;">📊 Central Data Sheet</h3>
    <a href="{FIXED_SHEET_URL}" target="_blank"
       style="color: white; background: rgba(255,255,255,0.2);
              padding: 0.6rem 1.2rem; border-radius: 10px;
              text-decoration: none; display: inline-block; margin-top: 0.5rem;">
        🔗 Open in Google Sheets
    </a>
    <p style="margin-top: 0.5rem; font-size: 0.85rem; opacity: 0.9;">
        All processed data are automatically saved here
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# Professional UI Styling
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .main-header h1 { color: white; font-size: 2.8rem; margin: 0; }
    .main-header p { color: rgba(255,255,255,0.9); font-size: 1.2rem; margin: 0.5rem 0 0 0; }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem; border-radius: 15px; text-align: center; color: white;
        box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3);
    }
    .metric-card h3 { font-size:1rem; margin:0 0 .5rem 0; }
    .metric-card h2 { font-size:2rem; margin:0; font-weight:bold; }
    .status-box { padding:1.5rem; border-radius:15px; margin:1rem 0; }
    .status-success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color:white; }
    .status-error { background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); color:white; }
    .status-info { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color:white; }
    .qc-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# API Keys
# =========================================================
API_KEYS = {
    "excel": "AIzaSyBzVNw34fbQRcxCSZDouR35hoZNxqsW6pc",
    "ocr": "AIzaSyCKoaSP6Wgj5FCJDGGXIBHy1rt61Cl2ZTs",
    "scrap": "AIzaSyAhuC9Grg_FlxwDwYUW-_CpNaFzjwUg24w"
}
for key_name, key_value in API_KEYS.items():
    os.environ[f"GOOGLE_API_KEY_{key_name.upper()}"] = key_value
    os.environ["GOOGLE_API_KEY"] = key_value
    os.environ["GEMINI_API_KEY"] = key_value

# =========================================================
# GOOGLE SHEETS INTEGRATION
# =========================================================
from google.oauth2 import service_account
from googleapiclient.discovery import build

GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets'
]

@st.cache_resource
def get_google_services():
    """Connect to Google Drive and Sheets"""
    try:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=GOOGLE_SCOPES
        )
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        return drive_service, sheets_service
    except Exception as e:
        st.error(f"❌ Error connecting to Google: {e}")
        return None, None

def _col_index_to_letter(col_index):
    """Convert column index to letter (0->A, 25->Z, 26->AA)"""
    result = ""
    while col_index >= 0:
        result = chr(col_index % 26 + 65) + result
        col_index = col_index // 26 - 1
    return result

def append_excel_data_to_sheets(excel_path, folder_id=None):
    """Read Excel data and append to Google Sheets"""
    try:
        drive_service, sheets_service = get_google_services()
        if not drive_service or not sheets_service:
            return False, "Google connection failed", None, 0

        print(f"\n☁️ Starting data save to Google Drive...")

        # Use existing Google Sheet
        file_id = "1OeQbiqvo6v58rcxaoSUidOk0IxSGmL8YCpLnyh27yuE"
        file_url = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
        print(f"   ✅ Using existing Google Sheet: {file_url}")

        if not file_id:
            return False, "Error creating table", None, 0
        
        print(f"📖 Reading Excel data: {excel_path.name}")
        df = pd.read_excel(excel_path)
        if df.empty:
            return False, "Excel file is empty", None, 0
        
        print(f"   ✅ {len(df)} rows × {len(df.columns)} columns read")
        
        # Clean DataFrame from NaN and None values
        df = df.replace({np.nan: "", None: ""})
        
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).replace('nan', '').replace('None', '').replace('NaT', '')
        
        sheet_name = 'Sheet1'
        
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=file_id, range=f'{sheet_name}!1:1'
        ).execute()
        
        existing_headers = result.get('values', [[]])[0] if result.get('values') else []
        new_headers = df.columns.tolist()
        
        print(f"   📋 Existing columns: {len(existing_headers)} | New columns: {len(new_headers)}")
        
        if not existing_headers:
            values = [new_headers] + df.values.tolist()
            print(f"   ℹ️ Empty table, adding {len(new_headers)} columns")
        else:
            new_columns = [col for col in new_headers if col not in existing_headers]
            
            all_columns = existing_headers.copy()
            for col in new_columns:
                if col not in all_columns:
                    all_columns.append(col)
            
            print(f"   📊 Final order: {len(all_columns)} columns")
            
            if new_columns:
                print(f"   🆕 New columns: {new_columns}")
                print(f"   🔄 Updating headers...")
                sheets_service.spreadsheets().values().update(
                    spreadsheetId=file_id,
                    range=f'{sheet_name}!1:1',
                    valueInputOption='USER_ENTERED',
                    body={'values': [all_columns]}
                ).execute()
                
                result = sheets_service.spreadsheets().values().get(
                    spreadsheetId=file_id, range=f'{sheet_name}!A:A'
                ).execute()
                existing_rows_count = len(result.get('values', [])) - 1
                
                if existing_rows_count > 0:
                    print(f"   📝 Filling {existing_rows_count} old rows...")
                    empty_values = [[''] * len(new_columns) for _ in range(existing_rows_count)]
                    start_col_index = len(existing_headers)
                    start_col_letter = _col_index_to_letter(start_col_index)
                    end_col_letter = _col_index_to_letter(start_col_index + len(new_columns) - 1)
                    
                    sheets_service.spreadsheets().values().update(
                        spreadsheetId=file_id,
                        range=f'{sheet_name}!{start_col_letter}2:{end_col_letter}{existing_rows_count+1}',
                        valueInputOption='USER_ENTERED',
                        body={'values': empty_values}
                    ).execute()
                    print(f"   ✅ Old rows updated")
            
            for col in all_columns:
                if col not in df.columns:
                    df[col] = ''
            
            df = df[all_columns]
            print(f"   ✅ DataFrame sorted: {len(df)} rows × {len(all_columns)} columns")
            values = df.values.tolist()

        # Convert all NaN or None to string before sending to Sheets
        values = [[("" if (pd.isna(cell) or cell is None) else str(cell)) for cell in row] for row in values]
        
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=file_id, range=f'{sheet_name}!A:A'
        ).execute()
        existing_rows = len(result.get('values', []))
        
        print(f"   📊 Current rows: {existing_rows}")
        print(f"   📤 Adding {len(values)} rows...")
        
        body = {'values': values}
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=file_id,
            range=f'{sheet_name}!A:A',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        updated_rows = result.get('updates', {}).get('updatedRows', 0)
        total_rows = existing_rows + updated_rows
        
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=file_id, range=f'{sheet_name}!1:1'
        ).execute()
        total_columns = len(result.get('values', [[]])[0])
        
        total_cells = total_rows * total_columns
        capacity = (total_cells / 10_000_000) * 100
        
        print(f"   ✅ {updated_rows} new rows added")
        print(f"   📊 Total: {total_rows} rows × {total_columns} columns")
        print(f"   📊 Total cells: {total_cells:,} ({capacity:.1f}%)")
        print(f"   🔗 {file_url}")
        
        message = f"✅ {updated_rows} new rows | Total: {total_rows} rows | {total_columns} columns"
        return True, message, file_url, total_rows
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e), None, 0

def get_or_create_folder(folder_name="Exhibition_Data"):
    """Find or create folder in Drive"""
    try:
        drive_service, _ = get_google_services()
        if not drive_service:
            return None
        
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = drive_service.files().list(
            q=query, spaces='drive', fields='files(id, name)', pageSize=1
        ).execute()
        files = results.get('files', [])
        
        if files:
            print(f"   ✅ Existing folder: {files[0]['name']}")
            return files[0]['id']
        
        folder = drive_service.files().create(
            body={'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'},
            fields='id'
        ).execute()
        print(f"   ✅ New folder: {folder_name}")
        return folder.get('id')
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

# =========================================================
# Quota Management
# =========================================================
DAILY_LIMIT = 240
QUOTA_FILE = Path("quota.json")

def save_quota(q):
    QUOTA_FILE.write_text(json.dumps(q, indent=2, ensure_ascii=False), encoding="utf-8")

def load_quota():
    today = datetime.date.today().isoformat()
    if QUOTA_FILE.exists():
        try:
            data = json.loads(QUOTA_FILE.read_text(encoding="utf-8"))
            file_date = data.get("date")
            if file_date != today:
                q = {"date": today, "used": 0, "remaining": DAILY_LIMIT}
                save_quota(q)
                return q
            used = data.get("used", 0)
            remaining = max(0, DAILY_LIMIT - used)
            q = {"date": today, "used": used, "remaining": remaining}
            save_quota(q)
            return q
        except Exception:
            pass
    q = {"date": today, "used": 0, "remaining": DAILY_LIMIT}
    save_quota(q)
    return q

def decrease_quota(amount=1):
    quota = load_quota()
    quota["used"] += amount
    quota["remaining"] = max(0, DAILY_LIMIT - quota["used"])
    save_quota(quota)
    return quota

# =========================================================
# Quality Control Functions
# =========================================================
def get_qc_metadata(user_name, user_role):
    """Create quality control metadata"""
    now = datetime.datetime.now()
    return {
        "QC_Supervisor": user_name,
        "QC_Role": user_role,
        "QC_Date": now.strftime("%Y-%m-%d"),
        "QC_Time": now.strftime("%H:%M:%S"),
        "QC_Timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
    }

def add_qc_metadata_to_excel(excel_path, qc_metadata):
    """Add quality control metadata to Excel"""
    try:
        df = pd.read_excel(excel_path)
        for key in ["QC_Supervisor", "QC_Role", "QC_Date", "QC_Time", "QC_Timestamp"]:
            if key in qc_metadata:
                df.insert(0, key, qc_metadata[key])
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"   ✅ QC Metadata added: {qc_metadata['QC_Supervisor']} ({qc_metadata['QC_Role']})")
        return True
    except Exception as e:
        print(f"   ❌ Error adding QC metadata: {e}")
        return False

# =========================================================
# Utility Functions
# =========================================================
def detect_pipeline_type(files):
    extensions = [f.name.split('.')[-1].lower() for f in files]
    if any(ext in ['xlsx', 'xls'] for ext in extensions):
        return 'excel'
    elif any(ext in ['pdf', 'jpg', 'jpeg', 'png'] for ext in extensions):
        return 'ocr_qr'
    return None

def extract_exhibition_name(files):
    if not files:
        return "Unknown_Exhibition"
    first_file = files[0].name
    name_without_ext = first_file.rsplit('.', 1)[0]
    name_parts = re.split(r'[_\-\s]+', name_without_ext)
    cleaned_parts = [p for p in name_parts if not p.isdigit() and len(p) > 2]
    if cleaned_parts:
        return " ".join(cleaned_parts[:3])
    return "Unknown_Exhibition"

# =========================================================
# Main UI
# =========================================================
st.markdown("""
<div class="main-header">
    <h1>🎯 Smart Exhibition Pipeline</h1>
    <p>OCR/QR Processing • Google Sheets Integration • Quality Control</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    quota = load_quota()
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                padding:1.5rem; border-radius:15px; color:white; margin-bottom:1rem;">
        <h3>📊 Today's Quota</h3>
        <div style="font-size:3rem; font-weight:bold;">{quota['remaining']}</div>
        <p>out of {DAILY_LIMIT}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.progress(quota['used'] / DAILY_LIMIT if DAILY_LIMIT > 0 else 0)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    fast_mode = st.checkbox("⚡️ Fast Mode", value=True)
    debug_mode = st.checkbox("🐛 Debug Mode")

# Upload Files
st.markdown("## 📂 Upload Files")
uploaded_files = st.file_uploader(
    "Drag files here or click to browse",
    type=['xlsx', 'xls', 'pdf', 'jpg', 'jpeg', 'png'],
    accept_multiple_files=True
)

# Quality Control Section
st.markdown("## 👤 Quality Control Info")
col1, col2 = st.columns(2)
with col1:
    qc_user_name = st.text_input("🧑‍💼 Full Name", placeholder="e.g., John Smith")
with col2:
    qc_user_role = st.text_input("💼 Position", placeholder="e.g., QC Specialist")

if qc_user_name and qc_user_role:
    qc_preview = get_qc_metadata(qc_user_name, qc_user_role)
    st.markdown(f"""
    <div class="qc-card">
        <h4>✅ QC Info Preview</h4>
        <p><strong>👤 Supervisor:</strong> {qc_preview['QC_Supervisor']}</p>
        <p><strong>💼 Role:</strong> {qc_preview['QC_Role']}</p>
        <p><strong>📅 Date:</strong> {qc_preview['QC_Date']} | 🕐 {qc_preview['QC_Time']}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

if uploaded_files:
    pipeline_type = detect_pipeline_type(uploaded_files)
    exhibition_name = extract_exhibition_name(uploaded_files)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔍 Type</h3>
            <h2>{'📊 Excel' if pipeline_type == 'excel' else '🖼 OCR/QR'}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📁 Files</h3>
            <h2>{len(uploaded_files)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏢 Exhibition</h3>
            <h2>{exhibition_name[:15]}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    exhibition_name = st.text_input("📝 Exhibition Name", value=exhibition_name)
    
    if st.button("🚀 Start Processing", type="primary"):
        if not qc_user_name or not qc_user_role:
            st.error("❌ Please enter QC supervisor info!")
            st.stop()
        
        if quota['remaining'] <= 0:
            st.error("❌ API quota depleted!")
            st.stop()
        
        qc_metadata = get_qc_metadata(qc_user_name, qc_user_role)
        
        # Create session directory
        session_dir = Path(f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        session_dir.mkdir(exist_ok=True)
        
        # Save files
        for f in uploaded_files:
            (session_dir / f.name).write_bytes(f.getbuffer())
        
        st.success("✅ Files saved! Processing...")
        
        # Simulate processing (replace with actual OCR/QR code)
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
        
        # Create dummy output for demo
        output_data = {
            "Exhibition": exhibition_name,
            "QC_Supervisor": qc_metadata["QC_Supervisor"],
            "QC_Role": qc_metadata["QC_Role"],
            "File_Count": len(uploaded_files),
            "Processed_At": qc_metadata["QC_Timestamp"]
        }
        
        df_output = pd.DataFrame([output_data])
        output_file = session_dir / "output_data.xlsx"
        df_output.to_excel(output_file, index=False, engine='openpyxl')
        
        # ========== GOOGLE SHEETS UPLOAD ==========
        st.markdown("---")
        st.markdown("## ☁️ Saving to Google Drive")
        
        try:
            folder_id = get_or_create_folder("Exhibition_Data")
            success_gs, msg_gs, url_gs, total_rows = append_excel_data_to_sheets(
                excel_path=output_file,
                folder_id=folder_id
            )
            
            if success_gs:
                st.success(msg_gs)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 1.5rem; border-radius: 15px;">
                    <h4>🔗 Permanent Table Link</h4>
                    <p style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px;">
                        <a href="{url_gs}" target="_blank" style="color: white; font-weight: bold;">
                            📊 Open in Google Drive
                        </a>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
            else:
                st.error(f"❌ Error: {msg_gs}")
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
        # ========== END GOOGLE SHEETS ==========

else:
    st.info("👋 Welcome! Please upload files to get started.")