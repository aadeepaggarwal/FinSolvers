#!/usr/bin/env python3
"""
Flask Web Frontend for RAG Policy QA System

A beautiful web interface for the RAG Policy Question Answering system.
Users can upload PDF files, ask natural language questions, and get
structured responses with clause citations.

Author: Copilot Assistant
Date: July 2025
Version: 1.0.0

Usage:
    python flask_app.py
    Then open: http://localhost:5001
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
import json
import time
import tempfile
from werkzeug.utils import secure_filename
from pathlib import Path

# Import the RAG system
try:
    from rag_policy_qa import RAGPolicyQA, QueryResult
except ImportError:
    print("❌ Could not import RAG system. Make sure rag_policy_qa.py is in the same directory.")
    exit(1)

# Flask app configuration
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Global variables
rag_system = None
current_document = None
processing_stats = {}
query_history = []

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html', 
                         document_loaded=current_document is not None,
                         stats=processing_stats,
                         history_count=len(query_history))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    global rag_system, current_document, processing_stats
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file and file.filename.lower().endswith('.pdf'):
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process document
            start_time = time.time()
            
            if not rag_system:
                rag_system = RAGPolicyQA()
            
            rag_system.process_document(filepath)
            processing_time = time.time() - start_time
            
            # Update stats
            chunks = rag_system.embedding_engine.chunks
            processing_stats = {
                'filename': filename,
                'chunks': len(chunks),
                'pages': max([chunk.page_number for chunk in chunks]) if chunks else 0,
                'processing_time': processing_time,
                'file_size': os.path.getsize(filepath)
            }
            
            current_document = filename
            flash(f'Document "{filename}" processed successfully!', 'success')
            
        except Exception as e:
            flash(f'Error processing document: {str(e)}', 'error')
    else:
        flash('Please upload a PDF file', 'error')
    
    return redirect(url_for('index'))

@app.route('/query', methods=['POST'])
def process_query():
    """Process a query and return results."""
    global rag_system, query_history
    
    if not rag_system or not current_document:
        return jsonify({'error': 'No document loaded. Please upload a PDF first.'}), 400
    
    data = request.get_json()
    query = data.get('query', '').strip()
    top_k = data.get('top_k', 5)
    
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        start_time = time.time()
        result = rag_system.query(query, top_k=top_k)
        query_time = time.time() - start_time
        
        # Add to history
        query_entry = {
            'query': query,
            'result': {
                'decision': result.decision,
                'amount': result.amount,
                'justification': result.justification,
                'clause_mapping': result.clause_mapping
            },
            'query_time': query_time,
            'timestamp': time.time()
        }
        query_history.append(query_entry)
        
        # Keep only last 50 queries
        if len(query_history) > 50:
            query_history = query_history[-50:]
        
        return jsonify({
            'success': True,
            'query': query,
            'decision': result.decision,
            'amount': result.amount,
            'justification': result.justification,
            'clause_mapping': result.clause_mapping,
            'query_time': query_time
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_history():
    """Get query history."""
    return jsonify({'history': query_history[-10:]})  # Last 10 queries

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear query history."""
    global query_history
    query_history = []
    return jsonify({'success': True})

@app.route('/stats')
def get_stats():
    """Get system statistics."""
    return jsonify({
        'document_loaded': current_document is not None,
        'current_document': current_document,
        'processing_stats': processing_stats,
        'query_count': len(query_history)
    })

# Create templates directory and HTML template
def create_templates():
    """Create HTML templates."""
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Main HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Policy QA System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .main-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin: 2rem auto;
            padding: 2rem;
            backdrop-filter: blur(10px);
        }
        
        .header-section {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .header-section h1 {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 25px;
            padding: 10px 30px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .alert {
            border-radius: 15px;
            border: none;
        }
        
        .form-control {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        .stats-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .result-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
        }
        
        .decision-approved {
            color: #28a745;
            font-weight: bold;
        }
        
        .decision-rejected {
            color: #dc3545;
            font-weight: bold;
        }
        
        .clause-item {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
        }
        
        .loading {
            display: none;
        }
        
        .spinner-border {
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-container">
            <!-- Header -->
            <div class="header-section">
                <h1><i class="fas fa-file-medical-alt"></i> RAG Policy QA System</h1>
                <p class="lead">Intelligent Document Analysis with AI-Powered Question Answering</p>
            </div>
            
            <!-- Flash Messages -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }} alert-dismissible fade show" role="alert">
                            <i class="fas fa-{{ 'check-circle' if category == 'success' else 'exclamation-circle' }}"></i>
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="row">
                <!-- Left Column: Upload and System Info -->
                <div class="col-md-4">
                    <!-- File Upload -->
                    <div class="card mb-4">
                        <div class="card-header bg-primary text-white">
                            <h5><i class="fas fa-cloud-upload-alt"></i> Upload Document</h5>
                        </div>
                        <div class="card-body">
                            <form action="/upload" method="POST" enctype="multipart/form-data">
                                <div class="mb-3">
                                    <label for="file" class="form-label">Select PDF File</label>
                                    <input type="file" class="form-control" id="file" name="file" accept=".pdf" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">
                                    <i class="fas fa-upload"></i> Upload & Process
                                </button>
                            </form>
                        </div>
                    </div>
                    
                    <!-- System Status -->
                    <div class="card mb-4">
                        <div class="card-header bg-info text-white">
                            <h5><i class="fas fa-info-circle"></i> System Status</h5>
                        </div>
                        <div class="card-body">
                            <div class="stats-card">
                                <h6>Document Status</h6>
                                <p class="mb-0">
                                    {% if document_loaded %}
                                        <i class="fas fa-check-circle text-success"></i> Ready
                                    {% else %}
                                        <i class="fas fa-times-circle text-warning"></i> No Document
                                    {% endif %}
                                </p>
                            </div>
                            
                            {% if stats %}
                            <div class="row">
                                <div class="col-6">
                                    <div class="text-center">
                                        <h6>{{ stats.chunks }}</h6>
                                        <small>Chunks</small>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="text-center">
                                        <h6>{{ stats.pages }}</h6>
                                        <small>Pages</small>
                                    </div>
                                </div>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    
                    <!-- Sample Queries -->
                    <div class="card">
                        <div class="card-header bg-warning text-dark">
                            <h5><i class="fas fa-lightbulb"></i> Sample Queries</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary btn-sm sample-query" 
                                        data-query="What are the exclusions for pre-existing conditions?">
                                    Pre-existing conditions
                                </button>
                                <button class="btn btn-outline-primary btn-sm sample-query" 
                                        data-query="46-year-old male, knee surgery in Pune, 3-month-old policy">
                                    Knee surgery coverage
                                </button>
                                <button class="btn btn-outline-primary btn-sm sample-query" 
                                        data-query="Emergency hospitalization coverage limits">
                                    Emergency coverage
                                </button>
                                <button class="btn btn-outline-primary btn-sm sample-query" 
                                        data-query="Maternity benefits waiting period">
                                    Maternity benefits
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Right Column: Query Interface -->
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5><i class="fas fa-question-circle"></i> Ask Questions</h5>
                        </div>
                        <div class="card-body">
                            <form id="queryForm">
                                <div class="mb-3">
                                    <label for="query" class="form-label">Your Question</label>
                                    <textarea class="form-control" id="query" name="query" rows="3" 
                                            placeholder="Ask any question about the policy document..." required></textarea>
                                </div>
                                
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <label for="top_k" class="form-label">Chunks to Retrieve</label>
                                        <select class="form-control" id="top_k" name="top_k">
                                            <option value="3">3</option>
                                            <option value="5" selected>5</option>
                                            <option value="7">7</option>
                                            <option value="10">10</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6 d-flex align-items-end">
                                        <button type="submit" class="btn btn-primary w-100" id="submitBtn">
                                            <i class="fas fa-search"></i> Ask Question
                                        </button>
                                    </div>
                                </div>
                            </form>
                            
                            <!-- Loading Spinner -->
                            <div class="loading text-center" id="loading">
                                <div class="spinner-border" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                                <p class="mt-2">Analyzing document...</p>
                            </div>
                            
                            <!-- Results Container -->
                            <div id="results"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Sample query buttons
        document.querySelectorAll('.sample-query').forEach(button => {
            button.addEventListener('click', function() {
                document.getElementById('query').value = this.dataset.query;
            });
        });
        
        // Query form submission
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value.trim();
            const top_k = document.getElementById('top_k').value;
            
            if (!query) {
                alert('Please enter a question');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '';
            document.getElementById('submitBtn').disabled = true;
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query, top_k: parseInt(top_k) })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                } else {
                    showError(data.error || 'An error occurred');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('submitBtn').disabled = false;
            }
        });
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            const decisionClass = data.decision === 'approved' ? 'decision-approved' : 'decision-rejected';
            const decisionIcon = data.decision === 'approved' ? 'check-circle' : 'times-circle';
            const amountDisplay = data.amount ? `₹${data.amount.toLocaleString()}` : 'N/A';
            
            let clausesHtml = '';
            if (data.clause_mapping && data.clause_mapping.length > 0) {
                clausesHtml = '<h6><i class="fas fa-book"></i> Referenced Clauses:</h6>';
                data.clause_mapping.forEach((clause, index) => {
                    clausesHtml += `
                        <div class="clause-item">
                            <strong>Clause ${index + 1}</strong> - Page ${clause.source.page}<br>
                            <small class="text-muted">Section: ${clause.source.section}</small><br>
                            <p class="mt-2 mb-0">${clause.clause_text}</p>
                        </div>
                    `;
                });
            }
            
            resultsDiv.innerHTML = `
                <div class="result-container">
                    <div class="row mb-4">
                        <div class="col-md-4 text-center">
                            <div class="stats-card">
                                <i class="fas fa-${decisionIcon} fa-2x mb-2"></i>
                                <h5 class="${decisionClass}">${data.decision.toUpperCase()}</h5>
                            </div>
                        </div>
                        <div class="col-md-4 text-center">
                            <div class="stats-card">
                                <i class="fas fa-rupee-sign fa-2x mb-2"></i>
                                <h5>${amountDisplay}</h5>
                                <small>Amount</small>
                            </div>
                        </div>
                        <div class="col-md-4 text-center">
                            <div class="stats-card">
                                <i class="fas fa-clock fa-2x mb-2"></i>
                                <h5>${data.query_time.toFixed(2)}s</h5>
                                <small>Query Time</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <h6><i class="fas fa-comment-alt"></i> Justification:</h6>
                        <div class="alert alert-info">
                            ${data.justification}
                        </div>
                    </div>
                    
                    ${clausesHtml}
                    
                    <div class="mt-3">
                        <button class="btn btn-outline-primary" onclick="downloadJSON()">
                            <i class="fas fa-download"></i> Download Results
                        </button>
                    </div>
                </div>
            `;
            
            // Store current result for download
            window.currentResult = data;
        }
        
        function showError(message) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </div>
            `;
        }
        
        function downloadJSON() {
            if (window.currentResult) {
                const dataStr = JSON.stringify(window.currentResult, null, 2);
                const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                
                const exportFileDefaultName = `policy_analysis_${Date.now()}.json`;
                
                const linkElement = document.createElement('a');
                linkElement.setAttribute('href', dataUri);
                linkElement.setAttribute('download', exportFileDefaultName);
                linkElement.click();
            }
        }
    </script>
</body>
</html>'''
    
    with open(templates_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

if __name__ == '__main__':
    # Create templates
    create_templates()
    
    print("🚀 Starting Flask Web Interface...")
    print("📱 Open your browser and go to: http://localhost:5001")
    print("💡 Features:")
    print("   • Upload PDF documents")
    print("   • Ask natural language questions")
    print("   • Get structured responses with clause citations")
    print("   • View query history")
    print("   • Download results as JSON")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
