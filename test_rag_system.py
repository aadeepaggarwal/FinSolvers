#!/usr/bin/env python3
"""
Test script for RAG Policy QA System

This script helps verify that all dependencies are installed correctly
and tests the system with sample queries.

Usage:
    python test_rag_system.py
"""

import os
import sys
import json
import traceback
from pathlib import Path

def test_imports():
    """Test that all required dependencies can be imported."""
    print("Testing imports...")
    
    try:
        import PyMuPDF as fitz
        print("✓ PyMuPDF imported successfully")
    except ImportError as e:
        print(f"✗ PyMuPDF import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers imported successfully")
    except ImportError as e:
        print(f"✗ sentence-transformers import failed: {e}")
        return False
    
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        print("✓ scikit-learn imported successfully")
    except ImportError as e:
        print(f"✗ scikit-learn import failed: {e}")
        return False
    
    try:
        import openai
        print("✓ OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ OpenAI import failed: {e}")
        return False
    
    try:
        from flask import Flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    print("All imports successful!\n")
    return True

def test_embedding_model():
    """Test that the embedding model can be loaded."""
    print("Testing embedding model loading...")
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Test embedding creation
        test_text = "This is a test sentence for embedding."
        embedding = model.encode([test_text])
        
        print(f"✓ Embedding model loaded successfully")
        print(f"✓ Test embedding shape: {embedding.shape}")
        print(f"✓ Embedding dimension: {embedding.shape[1]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Embedding model test failed: {e}")
        traceback.print_exc()
        return False

def test_pdf_processing():
    """Test PDF processing with sample files."""
    print("\nTesting PDF processing...")
    
    # Look for sample PDFs
    sample_dir = Path("Sample data")
    if not sample_dir.exists():
        print("✗ Sample data directory not found")
        return False
    
    pdf_files = list(sample_dir.glob("*.pdf"))
    if not pdf_files:
        print("✗ No PDF files found in Sample data directory")
        return False
    
    print(f"Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    # Test with first PDF
    test_pdf = pdf_files[0]
    print(f"\nTesting with: {test_pdf.name}")
    
    try:
        # Import our system
        from rag_policy_qa import PDFProcessor
        
        processor = PDFProcessor()
        chunks = processor.extract_text_from_pdf(str(test_pdf))
        
        print(f"✓ PDF processed successfully")
        print(f"✓ Extracted {len(chunks)} chunks")
        
        if chunks:
            print(f"✓ First chunk preview: {chunks[0].text[:100]}...")
            print(f"✓ Chunk metadata: Page {chunks[0].page_number}, Section: {chunks[0].section}")
        
        return True
        
    except Exception as e:
        print(f"✗ PDF processing failed: {e}")
        traceback.print_exc()
        return False

def test_full_system():
    """Test the complete RAG system without API calls."""
    print("\nTesting complete RAG system (without LLM)...")
    
    try:
        from rag_policy_qa import RAGPolicyQA
        
        # Find a sample PDF
        sample_dir = Path("Sample data")
        pdf_files = list(sample_dir.glob("*.pdf"))
        if not pdf_files:
            print("✗ No PDF files found for testing")
            return False
        
        test_pdf = pdf_files[0]
        print(f"Testing with: {test_pdf.name}")
        
        # Initialize system without OpenAI key (will use fallback)
        rag_system = RAGPolicyQA()
        
        # Process document
        rag_system.process_document(str(test_pdf))
        print("✓ Document processed successfully")
        
        # Test query
        test_query = "What is covered under this policy?"
        result = rag_system.query(test_query)
        
        print("✓ Query processed successfully")
        print(f"✓ Decision: {result.decision}")
        print(f"✓ Amount: {result.amount}")
        print(f"✓ Justification length: {len(result.justification)} characters")
        print(f"✓ Clause mappings: {len(result.clause_mapping)} clauses")
        
        # Print result as JSON
        result_dict = {
            "decision": result.decision,
            "amount": result.amount,
            "justification": result.justification,
            "clause_mapping": result.clause_mapping
        }
        
        print(f"\nSample result:")
        print(json.dumps(result_dict, indent=2))
        
        return True
        
    except Exception as e:
        print(f"✗ Full system test failed: {e}")
        traceback.print_exc()
        return False

def check_openai_key():
    """Check if OpenAI API key is available."""
    print("\nChecking OpenAI API key...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✓ OpenAI API key found in environment")
        print(f"✓ Key starts with: {api_key[:10]}...")
        return True
    else:
        print("⚠ OpenAI API key not found in environment")
        print("  The system will use fallback reasoning instead of GPT-4")
        print("  Set OPENAI_API_KEY environment variable to enable LLM features")
        return False

def main():
    """Run all tests."""
    print("RAG Policy QA System - Test Suite")
    print("=" * 50)
    
    # Track test results
    tests_passed = 0
    total_tests = 5
    
    # Test imports
    if test_imports():
        tests_passed += 1
    
    # Test embedding model
    if test_embedding_model():
        tests_passed += 1
    
    # Test PDF processing
    if test_pdf_processing():
        tests_passed += 1
    
    # Test full system
    if test_full_system():
        tests_passed += 1
    
    # Check OpenAI key (optional)
    if check_openai_key():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set your OpenAI API key for best results:")
        print("   $env:OPENAI_API_KEY = 'your-key-here'")
        print("2. Run the system:")
        print("   python rag_policy_qa.py --policy './Sample data/EDLHLGA23009V012223.pdf' --query 'your query here'")
    elif tests_passed >= 4:
        print("✓ Core system is working! Only LLM integration needs setup.")
        print("  You can still use the system with fallback reasoning.")
    else:
        print("⚠ Some tests failed. Please check the error messages above.")
        print("  Try: pip install -r requirements.txt")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
