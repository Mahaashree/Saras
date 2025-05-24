import streamlit as st
import os
from pathlib import Path

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def load_css():
    """Load custom CSS from external file"""
    css_file = Path("styles.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS file not found. Please ensure 'styles.css' is in the same directory.")

def get_file_stats():
    """Calculate file statistics"""
    files = st.session_state.get("uploaded_files", [])
    total_files = len(files)
    pdf_count = sum(1 for f in files if f.get('type') == 'application/pdf')
    pptx_count = total_files - pdf_count
    
    return total_files, pdf_count, pptx_count

def format_file_size(size):
    """Format file size in human readable format"""
    if size > 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    elif size > 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size} bytes"

def get_file_icon_and_color(file_type):
    """Get appropriate icon and color for file type"""
    if file_type == 'application/pdf':
        return "📄", "#dc3545"
    else:
        return "📊", "#28a745"

def render_header():
    """Render the main header section"""
    st.markdown('<h1 class="main-header">🎓 Saras AI Tutor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform your presentations into interactive learning experiences</p>', unsafe_allow_html=True)

def render_statistics():
    """Render the statistics section"""
    total_files, pdf_count, pptx_count = get_file_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{total_files}</div>
            <div class="stat-label">Files Uploaded</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{pdf_count}</div>
            <div class="stat-label">PDF Files</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{pptx_count}</div>
            <div class="stat-label">PPTX Files</div>
        </div>
        """, unsafe_allow_html=True)

def render_upload_section():
    """Render the file upload section"""
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📁 Upload Your Files")
    st.markdown("Drag and drop your **PPTX** or **PDF** files here, or click to browse.")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pptx", "pdf"],
        accept_multiple_files=True,
        help="You can upload multiple PowerPoint (.pptx) and PDF files at once."
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    return uploaded_files

def process_uploads(uploaded_files):
    """Process and save uploaded files"""
    if not uploaded_files:
        return False
    
    new_files_added = False
    for file in uploaded_files:
        file_path = UPLOAD_DIR / file.name
        
        # Save if not already in session
        existing_names = [f["name"] for f in st.session_state.uploaded_files]
        if file.name not in existing_names:
            with open(file_path, "wb") as f_out:
                f_out.write(file.read())
            
            st.session_state.uploaded_files.append({
                "name": file.name,
                "path": file_path,
                "type": file.type,
                "size": len(file.getvalue()) if hasattr(file, 'getvalue') else 0
            })
            new_files_added = True
    
    if new_files_added:
        st.markdown('<div class="success-message">✅ Files uploaded successfully!</div>', unsafe_allow_html=True)
        st.rerun()  # Refresh to update statistics
    
    return new_files_added

def render_file_list():
    """Render the list of uploaded files"""
    if not st.session_state.uploaded_files:
        render_empty_state()
        return
    
    st.markdown("### 📚 Your Uploaded Files")
    
    for i, file_info in enumerate(st.session_state.uploaded_files):
        icon, type_color = get_file_icon_and_color(file_info['type'])
        size_str = format_file_size(file_info.get('size', 0))
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown(f"""
            <div class="file-item">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <span class="file-name">{file_info['name']}</span>
                <span class="file-type" style="color: {type_color};">
                    {file_info['type'].split('/')[-1].upper()}
                </span>
                <br>
                <small style="color: #999;">📏 {size_str}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🗑️", key=f"delete_{i}", help="Delete file", type="secondary"):
                delete_file(i)

def delete_file(index):
    """Delete a file from both disk and session state"""
    file_info = st.session_state.uploaded_files[index]
    
    # Remove file from disk
    try:
        os.remove(file_info["path"])
        st.success(f"Deleted {file_info['name']}")
    except Exception as e:
        st.error(f"Failed to delete file: {e}")
    
    # Remove from session state
    st.session_state.uploaded_files.pop(index)
    st.rerun()

def render_action_buttons():
    """Render action buttons for file operations"""
    if len(st.session_state.uploaded_files) == 0:
        return
    
    st.markdown("### 🚀 Ready to Start?")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("✨ Generate Lecture", type="primary", use_container_width=True):
            st.balloons()
            st.success("🎉 Lecture generation started! (Feature coming soon)")
        
        if st.button("🧹 Clear All Files", use_container_width=True):
            clear_all_files()

def clear_all_files():
    """Clear all uploaded files"""
    for file_info in st.session_state.uploaded_files:
        try:
            os.remove(file_info["path"])
        except:
            pass
    st.session_state.uploaded_files = []
    st.rerun()

def render_empty_state():
    """Render empty state when no files are uploaded"""
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📁</div>
        <h3>No files uploaded yet</h3>
        <p>Upload your first presentation or PDF to get started with AI-powered lectures!</p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Render the footer section"""
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>💡 <strong>Tip:</strong> Upload multiple files to create comprehensive lecture series</p>
        <p>Built with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Saras - AI Tutor", 
        layout="centered",
        page_icon="🎓"
    )
    
    # Load custom CSS
    load_css()
    
    # Initialize session state
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Render components
    render_header()
    render_statistics()
    
    uploaded_files = render_upload_section()
    process_uploads(uploaded_files)
    
    render_file_list()
    render_action_buttons()
    render_footer()

if __name__ == "__main__":
    main()