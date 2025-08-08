#!/usr/bin/env python3
"""
Launcher for RAG Policy QA System

Choose between Streamlit and Flask web interfaces for the RAG system.

Author: Copilot Assistant
Date: July 2025
Version: 1.0.0
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    """Print a welcome banner."""
    print("=" * 60)
    print("🚀 RAG Policy QA System Launcher")
    print("=" * 60)
    print("Choose your preferred web interface:")
    print()

def launch_streamlit():
    """Launch the Streamlit application."""
    try:
        print("🎯 Launching Streamlit application...")
        print("📱 Your browser will open automatically")
        print("🌐 URL: http://localhost:8501")
        print()
        print("✨ Features:")
        print("   • Beautiful, modern interface")
        print("   • Real-time processing feedback")
        print("   • Interactive components")
        print("   • Query history with statistics")
        print("   • Sample query suggestions")
        print()
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped.")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")

def launch_flask():
    """Launch the Flask application."""
    try:
        print("🌐 Launching Flask web application...")
        print("📱 Open your browser and go to: http://localhost:5001")
        print()
        print("✨ Features:")
        print("   • Professional web interface")
        print("   • File upload with drag & drop")
        print("   • JSON API endpoints")
        print("   • Bootstrap styling")
        print("   • Download results as JSON")
        print()
        
        # Launch Flask
        subprocess.run([sys.executable, "flask_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Flask application stopped.")
    except Exception as e:
        print(f"❌ Error launching Flask: {e}")

def test_system():
    """Test the RAG system with CLI."""
    try:
        print("🧪 Testing RAG system...")
        print()
        
        # Look for sample PDFs
        sample_dir = Path("Sample data")
        if sample_dir.exists():
            pdf_files = list(sample_dir.glob("*.pdf"))
            if pdf_files:
                test_pdf = pdf_files[0]
                print(f"📄 Using sample PDF: {test_pdf.name}")
                print("❓ Test query: 'What are the main coverage benefits?'")
                print()
                
                # Run test
                subprocess.run([
                    sys.executable, "rag_policy_qa.py",
                    "--policy", str(test_pdf),
                    "--query", "What are the main coverage benefits?"
                ])
            else:
                print("❌ No PDF files found in Sample data directory")
        else:
            print("❌ Sample data directory not found")
            print("💡 Please upload a PDF file to test the system")
    except Exception as e:
        print(f"❌ Error testing system: {e}")

def show_help():
    """Show help information."""
    print("📚 RAG Policy QA System Help")
    print("=" * 40)
    print()
    print("🎯 What is this system?")
    print("   A Retrieval-Augmented Generation (RAG) system for analyzing")
    print("   insurance policy documents using AI. Upload PDFs and ask")
    print("   questions in natural language to get structured responses.")
    print()
    print("🛠️ Available Interfaces:")
    print("   1. Streamlit - Modern, interactive web app")
    print("   2. Flask - Professional web interface")
    print("   3. CLI - Command-line interface")
    print()
    print("📋 System Requirements:")
    print("   • Python 3.10+")
    print("   • All dependencies installed (see requirements.txt)")
    print("   • PDF files to analyze")
    print("   • Optional: OpenAI API key for enhanced reasoning")
    print()
    print("🚀 Quick Start:")
    print("   1. Choose an interface (Streamlit recommended)")
    print("   2. Upload a PDF document")
    print("   3. Ask questions about the document")
    print("   4. Get structured responses with clause citations")
    print()
    print("🔧 Configuration:")
    print("   • Set OPENAI_API_KEY environment variable for GPT-4")
    print("   • Adjust chunk size and overlap in rag_policy_qa.py")
    print("   • Modify embedding model in EmbeddingEngine class")
    print()

def main():
    """Main launcher function."""
    print_banner()
    
    while True:
        print("Choose an option:")
        print("1. 🎨 Launch Streamlit App (Recommended)")
        print("2. 🌐 Launch Flask Web App")
        print("3. 🧪 Test System (CLI)")
        print("4. 📚 Help & Documentation")
        print("5. 👋 Exit")
        print()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                launch_streamlit()
            elif choice == '2':
                launch_flask()
            elif choice == '3':
                test_system()
            elif choice == '4':
                show_help()
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
            
            print("\n" + "=" * 60)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
