#!/usr/bin/env python3
"""
Streamlit Frontend for RAG Policy QA System

A beautiful web interface for the RAG Policy Question Answering system.
Users can upload PDF files, ask natural language questions, and get
structured responses with clause citations.

Author: Copilot Assistant
Date: July 2025
Version: 1.0.0

Usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import json
import os
import time
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

# Import the RAG system
try:
    from rag_policy_qa import RAGPolicyQA, QueryResult
except ImportError:
    st.error("❌ Could not import RAG system. Make sure rag_policy_qa.py is in the same directory.")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="RAG Policy QA System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #f0fff0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #fff5f5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .query-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #0d5aa7;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'current_pdf' not in st.session_state:
        st.session_state.current_pdf = None
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'processing_stats' not in st.session_state:
        st.session_state.processing_stats = {}

def display_header():
    """Display the main header and description."""
    st.markdown('<h1 class="main-header">📋 RAG Policy QA System</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>🎯 What is this?</strong><br>
        An intelligent document analysis system that uses <strong>Retrieval-Augmented Generation (RAG)</strong> 
        to answer questions about insurance policy documents. Upload a PDF, ask questions in natural language, 
        and get structured responses with precise clause citations.
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display the sidebar with system information and settings."""
    with st.sidebar:
        st.image("https://via.placeholder.com/300x150/1f77b4/ffffff?text=RAG+System", 
                caption="Policy Document AI Assistant")
        
        st.markdown("### 🛠️ System Configuration")
        
        # OpenAI API Key input
        api_key = st.text_input(
            "OpenAI API Key (Optional)",
            type="password",
            help="Enter your OpenAI API key for enhanced LLM reasoning. Leave empty to use fallback logic."
        )
        
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            st.success("✅ API Key configured")
        else:
            st.info("ℹ️ Using fallback reasoning")
        
        st.markdown("### 📊 System Status")
        
        # Display system status
        if st.session_state.rag_system:
            st.success("🟢 RAG System: Active")
        else:
            st.warning("🟡 RAG System: Not initialized")
        
        if st.session_state.pdf_processed:
            st.success("📄 Document: Processed")
            if st.session_state.processing_stats:
                st.metric("Chunks Extracted", st.session_state.processing_stats.get('chunks', 0))
                st.metric("Pages Processed", st.session_state.processing_stats.get('pages', 0))
        else:
            st.info("📄 Document: Not loaded")
        
        st.markdown("### 📈 Query Statistics")
        st.metric("Total Queries", len(st.session_state.query_history))
        
        # Sample queries
        st.markdown("### 💡 Sample Queries")
        sample_queries = [
            "What are the exclusions for pre-existing conditions?",
            "46-year-old male, knee surgery in Pune, 3-month-old policy",
            "Emergency hospitalization coverage limits",
            "Maternity benefits waiting period",
            "Network hospital cashless treatment process",
            "Day care procedure coverage and limits"
        ]
        
        for i, query in enumerate(sample_queries):
            if st.button(f"📝 {query[:30]}...", key=f"sample_{i}"):
                st.session_state.sample_query = query

def upload_and_process_pdf():
    """Handle PDF upload and processing."""
    st.markdown('<h2 class="sub-header">📤 Upload Policy Document</h2>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload your insurance policy document in PDF format"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Check if this is a new file
        if st.session_state.current_pdf != uploaded_file.name:
            st.session_state.current_pdf = uploaded_file.name
            st.session_state.pdf_processed = False
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 File Name", uploaded_file.name)
        with col2:
            st.metric("📏 File Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("📄 File Type", uploaded_file.type)
        
        # Process button
        if not st.session_state.pdf_processed:
            if st.button("🚀 Process Document", key="process_btn"):
                process_document(tmp_path, uploaded_file.name)
        else:
            st.markdown("""
            <div class="success-box">
                <strong>✅ Document processed successfully!</strong><br>
                You can now ask questions about this policy document.
            </div>
            """, unsafe_allow_html=True)
        
        return tmp_path if st.session_state.pdf_processed else None
    
    return None

def process_document(file_path: str, filename: str):
    """Process the uploaded PDF document."""
    try:
        with st.spinner("🔄 Processing document... This may take a few moments."):
            # Initialize RAG system if not exists
            if not st.session_state.rag_system:
                st.session_state.rag_system = RAGPolicyQA()
            
            # Process the document
            start_time = time.time()
            st.session_state.rag_system.process_document(file_path)
            processing_time = time.time() - start_time
            
            # Get processing statistics
            chunks = st.session_state.rag_system.embedding_engine.chunks
            st.session_state.processing_stats = {
                'chunks': len(chunks),
                'pages': max([chunk.page_number for chunk in chunks]) if chunks else 0,
                'processing_time': processing_time
            }
            
            st.session_state.pdf_processed = True
            
        st.success(f"✅ Document '{filename}' processed successfully!")
        st.balloons()
        
        # Display processing stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⚡ Processing Time", f"{processing_time:.2f}s")
        with col2:
            st.metric("📊 Text Chunks", st.session_state.processing_stats['chunks'])
        with col3:
            st.metric("📑 Pages Analyzed", st.session_state.processing_stats['pages'])
            
    except Exception as e:
        st.error(f"❌ Error processing document: {str(e)}")
        st.session_state.pdf_processed = False

def query_interface():
    """Display the query interface."""
    if not st.session_state.pdf_processed:
        st.warning("⚠️ Please upload and process a PDF document first.")
        return
    
    st.markdown('<h2 class="sub-header">💬 Ask Questions</h2>', unsafe_allow_html=True)
    
    # Query input
    query_input = st.text_area(
        "Enter your question about the policy document:",
        height=100,
        placeholder="E.g., What are the exclusions for pre-existing conditions?",
        help="Ask any question about the policy document in natural language."
    )
    
    # Use sample query if selected
    if hasattr(st.session_state, 'sample_query'):
        query_input = st.session_state.sample_query
        del st.session_state.sample_query
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            top_k = st.slider("Number of relevant chunks to retrieve", 3, 10, 5)
        with col2:
            show_chunks = st.checkbox("Show retrieved document chunks", value=False)
    
    # Query button
    if st.button("🔍 Ask Question", key="query_btn") and query_input.strip():
        execute_query(query_input, top_k, show_chunks)

def execute_query(query: str, top_k: int, show_chunks: bool):
    """Execute the query and display results."""
    try:
        with st.spinner("🧠 Analyzing document and generating response..."):
            start_time = time.time()
            result = st.session_state.rag_system.query(query, top_k=top_k)
            query_time = time.time() - start_time
            
            # Add to query history
            st.session_state.query_history.append({
                'query': query,
                'result': result,
                'timestamp': time.time(),
                'query_time': query_time
            })
        
        # Display results
        display_query_results(query, result, query_time, show_chunks)
        
    except Exception as e:
        st.error(f"❌ Error processing query: {str(e)}")

def display_query_results(query: str, result: QueryResult, query_time: float, show_chunks: bool):
    """Display the query results in a formatted way."""
    st.markdown('<h2 class="sub-header">📋 Analysis Results</h2>', unsafe_allow_html=True)
    
    # Display query
    st.markdown(f"""
    <div class="query-box">
        <strong>❓ Your Question:</strong><br>
        "{query}"
    </div>
    """, unsafe_allow_html=True)
    
    # Display main results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        decision_color = "🟢" if result.decision == "approved" else "🔴" if result.decision == "rejected" else "🟡"
        st.markdown(f"""
        <div class="metric-card">
            <h3>{decision_color} Decision</h3>
            <h2 style="color: {'green' if result.decision == 'approved' else 'red' if result.decision == 'rejected' else 'orange'}">
                {result.decision.upper()}
            </h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        amount_display = f"₹{result.amount:,.2f}" if result.amount else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Amount</h3>
            <h2 style="color: #1f77b4">{amount_display}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚡ Query Time</h3>
            <h2 style="color: #ff7f0e">{query_time:.2f}s</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Display justification
    st.markdown("### 📝 Justification")
    st.markdown(f"""
    <div class="info-box">
        {result.justification}
    </div>
    """, unsafe_allow_html=True)
    
    # Display clause mappings
    if result.clause_mapping:
        st.markdown("### 📚 Referenced Clauses")
        
        for i, clause in enumerate(result.clause_mapping):
            with st.expander(f"📄 Clause {i+1} - Page {clause['source']['page']}, Section: {clause['source']['section']}"):
                st.markdown(f"**Source:** {clause['source']['filename']}")
                st.markdown(f"**Page:** {clause['source']['page']}")
                st.markdown(f"**Section:** {clause['source']['section']}")
                st.markdown("**Text:**")
                st.text(clause['clause_text'])
    
    # Show retrieved chunks if requested
    if show_chunks:
        st.markdown("### 🔍 Retrieved Document Chunks")
        chunks = st.session_state.rag_system.embedding_engine.semantic_search(query, top_k=5)
        
        for i, (chunk, score) in enumerate(chunks):
            with st.expander(f"📄 Chunk {i+1} - Relevance Score: {score:.3f}"):
                st.markdown(f"**Chunk ID:** {chunk.chunk_id}")
                st.markdown(f"**Page:** {chunk.page_number}")
                st.markdown(f"**Section:** {chunk.section}")
                st.markdown(f"**Relevance Score:** {score:.3f}")
                st.markdown("**Text:**")
                st.text(chunk.text)
    
    # JSON download
    json_result = {
        "query": query,
        "decision": result.decision,
        "amount": result.amount,
        "justification": result.justification,
        "clause_mapping": result.clause_mapping,
        "query_time": query_time
    }
    
    st.download_button(
        label="📥 Download Results as JSON",
        data=json.dumps(json_result, indent=2),
        file_name=f"policy_analysis_{int(time.time())}.json",
        mime="application/json"
    )

def display_query_history():
    """Display query history."""
    if not st.session_state.query_history:
        return
    
    st.markdown('<h2 class="sub-header">📊 Query History</h2>', unsafe_allow_html=True)
    
    # Create history dataframe
    history_data = []
    for i, entry in enumerate(reversed(st.session_state.query_history[-10:])):  # Show last 10
        history_data.append({
            "#": len(st.session_state.query_history) - i,
            "Query": entry['query'][:50] + "..." if len(entry['query']) > 50 else entry['query'],
            "Decision": entry['result'].decision,
            "Amount": f"₹{entry['result'].amount:,.2f}" if entry['result'].amount else "N/A",
            "Time": f"{entry['query_time']:.2f}s",
            "Timestamp": time.strftime('%H:%M:%S', time.localtime(entry['timestamp']))
        })
    
    if history_data:
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()

def display_footer():
    """Display footer information."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🤖 <strong>RAG Policy QA System</strong> | Built with Streamlit & OpenAI | 
        📧 Contact: support@example.com</p>
        <p>⚡ Powered by: PyMuPDF • sentence-transformers • OpenAI GPT-4 • scikit-learn</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Display components
    display_header()
    display_sidebar()
    
    # Main content area
    pdf_path = upload_and_process_pdf()
    
    st.markdown("---")
    
    # Query interface
    query_interface()
    
    st.markdown("---")
    
    # Query history
    display_query_history()
    
    # Footer
    display_footer()

if __name__ == "__main__":
    main()
