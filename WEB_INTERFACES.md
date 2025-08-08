# RAG Policy QA System - Web Interfaces

## 🎯 Overview

Your RAG Policy QA System now includes **two beautiful web interfaces** in addition to the command-line interface:

1. **🎨 Streamlit App** - Modern, interactive interface
2. **🌐 Flask Web App** - Professional, responsive interface  
3. **⚡ CLI** - Command-line interface

## 🚀 Quick Start

### Option 1: Use the Launcher
```bash
# Run the interactive launcher
python launcher.py

# Or use the batch file (Windows)
run_app.bat
```

### Option 2: Direct Launch

**Streamlit (Recommended):**
```bash
python -m streamlit run streamlit_app.py
# Opens at: http://localhost:8501
```

**Flask:**
```bash
python flask_app.py
# Opens at: http://localhost:5001
```

## 🎨 Streamlit Interface Features

### ✨ **Modern Design**
- **Gradient headers** and beautiful styling
- **Real-time feedback** with progress bars
- **Interactive sidebar** with system status
- **Responsive layout** that works on mobile

### 📤 **Smart File Upload**
- **Drag & drop** PDF upload
- **File validation** and size checking
- **Processing statistics** (chunks, pages, time)
- **Visual feedback** during processing

### 💬 **Intelligent Q&A**
- **Natural language queries**
- **Sample query suggestions** 
- **Advanced options** (chunk count, etc.)
- **Real-time processing** with spinners

### 📊 **Rich Results Display**
- **Color-coded decisions** (✅ Approved / ❌ Rejected)
- **Amount formatting** with currency symbols
- **Query timing** and performance metrics
- **Expandable clause citations** with source info

### 📈 **Analytics & History**
- **Query history table** with statistics
- **Processing metrics** and system status
- **Download results** as JSON
- **Clear history** functionality

## 🌐 Flask Interface Features

### 🎯 **Professional Design**
- **Bootstrap 5** responsive design
- **Gradient backgrounds** and modern cards
- **Font Awesome icons** throughout
- **Smooth animations** and hover effects

### 📋 **Upload & Processing**
- **Multi-file support** with secure handling
- **Progress tracking** during processing
- **File validation** and error handling
- **System status dashboard**

### 🔍 **Query Interface**
- **Large text area** for complex questions
- **Configurable parameters** (chunks to retrieve)
- **Sample query buttons** for quick testing
- **Real-time loading indicators**

### 📊 **Results Visualization**
- **Statistics cards** with key metrics
- **Collapsible clause sections**
- **Source attribution** with page numbers
- **JSON download** functionality

## 🛠️ Configuration Options

### Streamlit Configuration
```python
# In streamlit_app.py
st.set_page_config(
    page_title="RAG Policy QA System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### Flask Configuration
```python
# In flask_app.py
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

## 🎨 Customization

### Streamlit Styling
The app uses custom CSS for beautiful styling:
- **Gradient headers** with text effects
- **Card-based layouts** with shadows
- **Color-coded metrics** and status indicators
- **Custom buttons** with hover animations

### Flask Themes
The Flask app includes:
- **Bootstrap 5** components
- **Custom CSS** for gradients and cards
- **Responsive design** for all screen sizes
- **Font Awesome** icons for visual appeal

## 📱 Mobile Responsiveness

Both interfaces are fully responsive:
- **Streamlit**: Automatic responsive layout
- **Flask**: Bootstrap responsive grid system
- **Touch-friendly**: Large buttons and inputs
- **Mobile navigation**: Collapsible sidebars

## 🔧 Advanced Features

### API Integration
Both interfaces can work with the existing Flask API:
```python
# API endpoints available:
GET  /health          # System health check
POST /query           # Process queries
GET  /history         # Query history
POST /clear_history   # Clear history
GET  /stats           # System statistics
```

### Sample Queries
Pre-built sample queries help users get started:
- "What are the exclusions for pre-existing conditions?"
- "46-year-old male, knee surgery in Pune, 3-month-old policy"
- "Emergency hospitalization coverage limits"
- "Maternity benefits waiting period"

### File Management
- **Secure uploads** with filename sanitization
- **Temporary file handling** for processing
- **File size validation** and error handling
- **Multiple format support** (PDF focus)

## 🚀 Performance Features

### Streamlit Optimizations
- **Session state management** for data persistence
- **Caching** for expensive operations
- **Background processing** indicators
- **Memory-efficient** file handling

### Flask Optimizations
- **Async processing** for large files
- **Error handling** and graceful degradation
- **Static file serving** for better performance
- **Session management** for user state

## 📊 Usage Analytics

Both interfaces track:
- **Query history** with timestamps
- **Processing statistics** (time, chunks, pages)
- **System performance** metrics
- **User interaction** patterns

## 🎯 Use Cases

### Business Users
- **Policy analysis** and decision making
- **Claim processing** automation
- **Document comparison** and review
- **Compliance checking**

### Technical Users
- **System testing** and validation
- **Performance monitoring**
- **API integration** testing
- **Custom deployment** scenarios

## 🔒 Security Features

### File Upload Security
- **Filename sanitization** prevents path traversal
- **File type validation** (PDF only)
- **Size limits** prevent DoS attacks
- **Temporary storage** with cleanup

### Data Privacy
- **No persistent storage** of documents
- **Session-based** data handling
- **Local processing** (no external data sharing)
- **Secure file cleanup** after processing

## 🐛 Troubleshooting

### Common Issues

**Streamlit not starting:**
```bash
# Install/reinstall Streamlit
pip install --upgrade streamlit
python -m streamlit run streamlit_app.py
```

**Flask template not found:**
```bash
# Templates are created automatically
# Make sure flask_app.py has write permissions
```

**Upload errors:**
```bash
# Check file permissions
# Ensure 'uploads' directory exists
# Verify file size < 50MB
```

### Debug Mode
Enable debug output:
```bash
# Streamlit with debug
streamlit run streamlit_app.py --logger.level debug

# Flask with debug
python flask_app.py  # Debug=True by default
```

## 🌟 Next Steps

1. **Try both interfaces** to see which you prefer
2. **Upload a sample PDF** from your Sample data folder
3. **Ask questions** using the sample queries
4. **Explore advanced features** like history and downloads
5. **Customize styling** to match your brand

## 💡 Tips for Best Experience

- **Use Chrome/Firefox** for best compatibility
- **Enable JavaScript** for full functionality
- **Good internet connection** for model downloads
- **Set OpenAI API key** for enhanced reasoning
- **Use sample queries** to get started quickly

---

🎉 **Your RAG system is now ready with beautiful web interfaces!** Choose the one that best fits your needs and start analyzing policy documents with AI-powered intelligence.
