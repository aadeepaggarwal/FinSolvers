#!/usr/bin/env python3
"""
End-to-End RAG System for Policy Document Question Answering

This module implements a complete Retrieval-Augmented Generation (RAG) pipeline
for natural language queries over PDF policy documents. It extracts text from PDFs,
creates semantic embeddings, performs similarity search, and uses an LLM to generate
structured responses with proper clause citations.

Author: Copilot Assistant
Date: July 2025
Version: 1.0.0

Usage:
    python rag_policy_qa.py --policy ./policy.pdf --query "46M, knee surgery, Pune, 3-month policy"
    
    or as Flask API:
    python rag_policy_qa.py --api
    curl -X POST http://localhost:5000/query -H "Content-Type: application/json" \
         -d '{"policy_path": "./policy.pdf", "query": "your query here"}'
"""

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Third-party imports
try:
    import fitz  # PyMuPDF for PDF text extraction
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import openai  # For GPT-4 API calls
    from flask import Flask, request, jsonify
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install PyMuPDF sentence-transformers scikit-learn openai flask numpy")
    sys.exit(1)


# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_audit.log'),
        logging.StreamHandler(sys.stderr)  # Log to stderr to keep stdout clean for JSON
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """
    Represents a semantic chunk of text from a PDF document.
    
    Attributes:
        text: The actual text content of the chunk
        page_number: Page number where this chunk appears (1-indexed)
        section: Section or heading name if available
        filename: Source filename
        chunk_id: Unique identifier for this chunk
        embedding: Vector embedding of the text (set after embedding)
    """
    text: str
    page_number: int
    section: str
    filename: str
    chunk_id: str
    embedding: Optional[np.ndarray] = None


@dataclass
class QueryResult:
    """
    Structured result from the RAG system.
    
    Attributes:
        decision: "approved" or "rejected"
        amount: Numerical amount if applicable, None otherwise
        justification: Human-readable explanation with clause references
        clause_mapping: List of relevant document chunks with source info
    """
    decision: str
    amount: Optional[float]
    justification: str
    clause_mapping: List[Dict[str, Any]]


class PDFProcessor:
    """
    Handles PDF text extraction and chunking operations.
    
    This class provides methods to extract text from PDF files, split content
    into semantic chunks, and maintain metadata about document structure.
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.chunk_size = 500  # Target characters per chunk
        self.overlap = 50      # Overlap between chunks for context preservation
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[DocumentChunk]:
        """
        Extract text from PDF and split into semantic chunks.
        
        Uses PyMuPDF to extract text while preserving page numbers and
        attempting to identify section headings.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of DocumentChunk objects containing text and metadata
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF processing fails
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Processing PDF: {pdf_path}")
        chunks = []
        filename = os.path.basename(pdf_path)
        
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            doc_pages = len(doc)
            
            for page_num in range(doc_pages):
                page = doc[page_num]
                text = page.get_text()
                
                if not text.strip():
                    continue
                
                # Extract potential section headings (lines in ALL CAPS or with specific formatting)
                lines = text.split('\n')
                current_section = "General"
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if len(line) > 5 and line.isupper() and len(line) < 100:
                        current_section = line
                
                # Split page text into chunks
                page_chunks = self._split_text_into_chunks(text)
                
                for chunk_idx, chunk_text in enumerate(page_chunks):
                    if len(chunk_text.strip()) < 50:  # Skip very short chunks
                        continue
                    
                    chunk_id = f"{filename}_p{page_num+1}_c{chunk_idx+1}"
                    
                    chunk = DocumentChunk(
                        text=chunk_text.strip(),
                        page_number=page_num + 1,
                        section=current_section,
                        filename=filename,
                        chunk_id=chunk_id
                    )
                    chunks.append(chunk)
            
            doc.close()
            logger.info(f"Extracted {len(chunks)} chunks from {doc_pages} pages")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            # Make sure document is closed even on error
            try:
                if 'doc' in locals():
                    doc.close()
            except:
                pass
            raise
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation.
        
        Uses sentence boundaries and paragraph breaks to create natural chunks
        while maintaining target size limits.
        
        Args:
            text: Input text to split
            
        Returns:
            List of text chunks
        """
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        
        # Split by sentences and paragraphs
        sentences = re.split(r'[.!?]+\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk)
                # Start new chunk with overlap from previous chunk
                words = current_chunk.split()
                overlap_words = words[-self.overlap//5:] if len(words) > self.overlap//5 else words
                current_chunk = ' '.join(overlap_words) + ' ' + sentence
            else:
                current_chunk += (' ' + sentence if current_chunk else sentence)
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk)
        
        return chunks


class EmbeddingEngine:
    """
    Handles text embedding and similarity search operations.
    
    Uses sentence-transformers to create dense vector representations of text
    chunks and performs cosine similarity search for retrieval.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding engine.
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.chunks: List[DocumentChunk] = []
        self.embeddings: Optional[np.ndarray] = None
    
    def create_embeddings(self, chunks: List[DocumentChunk]) -> None:
        """
        Create embeddings for all document chunks.
        
        Args:
            chunks: List of DocumentChunk objects to embed
        """
        logger.info(f"Creating embeddings for {len(chunks)} chunks")
        self.chunks = chunks
        
        # Extract text from chunks
        texts = [chunk.text for chunk in chunks]
        
        # Create embeddings in batch for efficiency
        embeddings = self.model.encode(texts, show_progress_bar=False)
        self.embeddings = np.array(embeddings)
        
        # Store embeddings in chunk objects
        for i, chunk in enumerate(self.chunks):
            chunk.embedding = embeddings[i]
        
        logger.info("Embeddings created successfully")
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """
        Perform semantic search to find most relevant chunks.
        
        Args:
            query: User's natural language query
            top_k: Number of top results to return
            
        Returns:
            List of (chunk, similarity_score) tuples, sorted by relevance
        """
        if self.embeddings is None or len(self.chunks) == 0:
            raise ValueError("No embeddings available. Call create_embeddings first.")
        
        logger.info(f"Performing semantic search for query: {query[:100]}...")
        
        # Embed the query
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            score = float(similarities[idx])  # Convert to Python float
            results.append((chunk, score))
            logger.info(f"Found relevant chunk: {chunk.chunk_id} (score: {score:.3f})")
        
        return results


class LLMReasoningEngine:
    """
    Handles LLM-based reasoning and response generation.
    
    Uses OpenAI's GPT-4 API to analyze retrieved document chunks and generate
    structured responses with proper justification and clause citations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM reasoning engine.
        
        Args:
            api_key: OpenAI API key. If None, will try to read from environment
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
    
    def generate_response(self, query: str, relevant_chunks: List[Tuple[DocumentChunk, float]]) -> QueryResult:
        """
        Generate structured response using LLM reasoning.
        
        Combines user query with retrieved document chunks to make policy decisions
        with proper justification and clause citations.
        
        Args:
            query: Original user query
            relevant_chunks: List of (chunk, score) tuples from semantic search
            
        Returns:
            QueryResult object with decision, amount, justification, and clause mapping
        """
        logger.info("Generating LLM response")
        
        # Prepare context from retrieved chunks
        context_sections = []
        for i, (chunk, score) in enumerate(relevant_chunks):
            context_sections.append(f"""
CHUNK {i+1} (Relevance: {score:.3f}):
Source: {chunk.filename}, Page {chunk.page_number}, Section: {chunk.section}
Text: {chunk.text}
""")
        
        context = "\n".join(context_sections)
        
        # Create structured prompt for LLM
        system_prompt = """You are an expert insurance policy analyst. Your task is to analyze insurance policy documents and make decisions on claims based on the provided context.

You must respond with ONLY a valid JSON object in the exact format specified below. Do not include any other text, explanations, or markdown formatting.

Required JSON format:
{
  "decision": "approved" or "rejected",
  "amount": <number or null>,
  "justification": "<explanation referencing specific clauses>",
  "clause_mapping": [
    {
      "clause_text": "<exact text snippet from document>",
      "source": {
        "filename": "<filename>",
        "page": <page_number>,
        "section": "<section_name>"
      }
    }
  ]
}

Guidelines:
1. Base your decision strictly on the provided policy document chunks
2. Reference specific clauses in your justification
3. Include exact text snippets in clause_mapping
4. Set amount to null if not applicable or not specified
5. Be precise and cite sources accurately"""
        
        user_prompt = f"""
Query: {query}

Policy Document Context:
{context}

Analyze the query against the policy context and provide your decision in the required JSON format."""
        
        try:
            if not self.api_key:
                # Fallback to rule-based reasoning if no API key
                logger.warning("No OpenAI API key available, using fallback reasoning")
                return self._fallback_reasoning(query, relevant_chunks)
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent, factual responses
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            logger.info(f"LLM response received: {response_text[:200]}...")
            
            # Parse JSON response
            try:
                result_dict = json.loads(response_text)
                return QueryResult(**result_dict)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}")
                return self._fallback_reasoning(query, relevant_chunks)
                
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return self._fallback_reasoning(query, relevant_chunks)
    
    def _fallback_reasoning(self, query: str, relevant_chunks: List[Tuple[DocumentChunk, float]]) -> QueryResult:
        """
        Fallback rule-based reasoning when LLM is not available.
        
        Implements basic heuristics for policy decisions based on keywords
        and document content analysis.
        
        Args:
            query: User query
            relevant_chunks: Retrieved document chunks
            
        Returns:
            QueryResult with basic rule-based decision
        """
        logger.info("Using fallback rule-based reasoning")
        
        query_lower = query.lower()
        
        # Extract potential numeric amounts from chunks
        amounts = []
        for chunk, _ in relevant_chunks:
            # Look for currency amounts
            amount_matches = re.findall(r'(?:rs\.?\s*|₹\s*|inr\s*)?([\d,]+(?:\.\d{2})?)', chunk.text, re.IGNORECASE)
            for match in amount_matches:
                try:
                    amount = float(match.replace(',', ''))
                    if 100 <= amount <= 10000000:  # Reasonable range for policy amounts
                        amounts.append(amount)
                except ValueError:
                    continue
        
        # Basic decision logic
        decision = "approved"  # Default to approved
        amount = max(amounts) if amounts else None
        
        # Simple rejection criteria
        rejection_keywords = ['excluded', 'not covered', 'rejected', 'denied', 'invalid']
        for chunk, _ in relevant_chunks:
            if any(keyword in chunk.text.lower() for keyword in rejection_keywords):
                decision = "rejected"
                break
        
        # Create clause mapping
        clause_mapping = []
        for chunk, score in relevant_chunks[:3]:  # Top 3 chunks
            clause_mapping.append({
                "clause_text": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                "source": {
                    "filename": chunk.filename,
                    "page": chunk.page_number,
                    "section": chunk.section
                }
            })
        
        justification = f"Decision based on analysis of {len(relevant_chunks)} relevant clauses from the policy document. "
        if decision == "approved" and amount:
            justification += f"Claim approved for amount ₹{amount:,.2f}."
        elif decision == "rejected":
            justification += "Claim rejected based on policy exclusions or limitations."
        else:
            justification += "Policy terms analyzed but no specific amount determined."
        
        return QueryResult(
            decision=decision,
            amount=amount,
            justification=justification,
            clause_mapping=clause_mapping
        )


class RAGPolicyQA:
    """
    Main RAG system orchestrator.
    
    Coordinates all components of the RAG pipeline: PDF processing,
    embedding creation, semantic search, and LLM reasoning.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the RAG system.
        
        Args:
            openai_api_key: OpenAI API key for LLM reasoning
        """
        self.pdf_processor = PDFProcessor()
        self.embedding_engine = EmbeddingEngine()
        self.llm_engine = LLMReasoningEngine(openai_api_key)
        self.is_initialized = False
    
    def process_document(self, pdf_path: str) -> None:
        """
        Process a PDF document and prepare it for querying.
        
        Args:
            pdf_path: Path to the PDF policy document
        """
        logger.info(f"Processing document: {pdf_path}")
        
        # Extract text and create chunks
        chunks = self.pdf_processor.extract_text_from_pdf(pdf_path)
        
        if not chunks:
            raise ValueError(f"No text extracted from PDF: {pdf_path}")
        
        # Create embeddings
        self.embedding_engine.create_embeddings(chunks)
        
        self.is_initialized = True
        logger.info("Document processing completed")
    
    def query(self, user_query: str, top_k: int = 5) -> QueryResult:
        """
        Process a natural language query against the loaded document.
        
        Args:
            user_query: User's natural language question
            top_k: Number of document chunks to retrieve for context
            
        Returns:
            QueryResult with decision, amount, justification, and clause mapping
        """
        if not self.is_initialized:
            raise ValueError("No document loaded. Call process_document first.")
        
        logger.info(f"Processing query: {user_query}")
        
        # Perform semantic search
        relevant_chunks = self.embedding_engine.semantic_search(user_query, top_k)
        
        if not relevant_chunks:
            logger.warning("No relevant chunks found for query")
            return QueryResult(
                decision="rejected",
                amount=None,
                justification="No relevant policy clauses found for the query.",
                clause_mapping=[]
            )
        
        # Generate LLM response
        result = self.llm_engine.generate_response(user_query, relevant_chunks)
        
        # Log audit trail
        logger.info(f"Query result: {result.decision}, Amount: {result.amount}")
        for i, clause in enumerate(result.clause_mapping):
            logger.info(f"Referenced clause {i+1}: {clause['source']}")
        
        return result


# Flask API Setup
app = Flask(__name__)
rag_system = None


@app.route('/query', methods=['POST'])
def api_query():
    """
    Flask API endpoint for processing queries.
    
    Expected JSON payload:
    {
        "policy_path": "/path/to/policy.pdf",
        "query": "natural language query"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'policy_path' not in data or 'query' not in data:
            return jsonify({"error": "Missing required fields: policy_path, query"}), 400
        
        policy_path = data['policy_path']
        query = data['query']
        
        # Initialize RAG system if not already done
        global rag_system
        if not rag_system:
            rag_system = RAGPolicyQA()
        
        # Process document if needed
        if not rag_system.is_initialized or not hasattr(rag_system, 'current_document') or rag_system.current_document != policy_path:
            rag_system.process_document(policy_path)
            rag_system.current_document = policy_path
        
        # Process query
        result = rag_system.query(query)
        
        return jsonify(asdict(result))
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "RAG Policy QA"})


def main():
    """
    Main entry point for the RAG system.
    
    Supports both CLI and Flask API modes.
    """
    parser = argparse.ArgumentParser(description="RAG System for Policy Document Q&A")
    parser.add_argument("--policy", type=str, help="Path to policy PDF file")
    parser.add_argument("--query", type=str, help="Natural language query")
    parser.add_argument("--api", action="store_true", help="Run as Flask API")
    parser.add_argument("--port", type=int, default=5000, help="API server port")
    parser.add_argument("--openai-key", type=str, help="OpenAI API key")
    
    args = parser.parse_args()
    
    # Set OpenAI API key if provided
    if args.openai_key:
        os.environ['OPENAI_API_KEY'] = args.openai_key
    
    if args.api:
        # Run Flask API
        logger.info(f"Starting Flask API on port {args.port}")
        app.run(host='0.0.0.0', port=args.port, debug=False)
        
    elif args.policy and args.query:
        # Run CLI mode
        try:
            rag_system = RAGPolicyQA()
            rag_system.process_document(args.policy)
            result = rag_system.query(args.query)
            
            # Output only JSON to stdout
            print(json.dumps(asdict(result), indent=2))
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            error_result = {
                "decision": "error",
                "amount": None,
                "justification": f"System error: {str(e)}",
                "clause_mapping": []
            }
            print(json.dumps(error_result, indent=2))
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
