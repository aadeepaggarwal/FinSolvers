# RAG Policy QA System

A complete end-to-end Retrieval-Augmented Generation (RAG) system for natural language queries over PDF policy documents. This system extracts text from PDFs, creates semantic embeddings, performs similarity search, and uses LLM reasoning to provide structured responses with proper clause citations.

## Features

- **PDF Text Extraction**: Uses PyMuPDF for robust text extraction with page and section metadata
- **Semantic Search**: Employs sentence-transformers for dense vector embeddings and cosine similarity search
- **LLM Reasoning**: Integrates with OpenAI GPT-4 for intelligent policy analysis and decision making
- **Structured Output**: Returns JSON responses with decisions, amounts, justifications, and clause mappings
- **Audit Trail**: Comprehensive logging for compliance and debugging
- **Dual Interface**: Supports both CLI and REST API modes
- **Fallback Logic**: Rule-based reasoning when LLM is unavailable

## Installation

1. **Clone or download the files**:
   ```bash
   # Files needed:
   # - rag_policy_qa.py
   # - requirements.txt
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key** (optional but recommended):
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY = "your-openai-api-key-here"
   
   # Or create a .env file
   echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
   ```

## Usage

### CLI Mode

#### Basic Usage
```bash
python rag_policy_qa.py --policy "./Sample data/EDLHLGA23009V012223.pdf" --query "46-year-old male, knee surgery in Pune, 3-month-old policy"
```

#### With API Key
```bash
python rag_policy_qa.py --policy "./Sample data/BAJHLIP23020V012223.pdf" --query "What is the coverage for diabetes treatment?" --openai-key "your-key-here"
```

#### Example Queries
```bash
# Medical procedure coverage
python rag_policy_qa.py --policy "./Sample data/HDFHLIP23024V072223.pdf" --query "Emergency heart surgery, 55-year-old female, Mumbai hospital"

# Policy limits and exclusions  
python rag_policy_qa.py --policy "./Sample data/ICIHLIP22012V012223.pdf" --query "Pre-existing condition coverage for 2-year-old policy"

# Specific treatment costs
python rag_policy_qa.py --policy "./Sample data/CHOTGDP23004V012223.pdf" --query "Cancer treatment coverage, chemotherapy costs"
```

### API Mode

#### Start the Server
```bash
python rag_policy_qa.py --api --port 5000
```

#### API Endpoints

**Health Check**:
```bash
curl http://localhost:5000/health
```

**Query Processing**:
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "policy_path": "./Sample data/EDLHLGA23009V012223.pdf",
    "query": "46M, knee surgery, Pune, 3-month policy"
  }'
```

## Output Format

The system returns structured JSON responses:

```json
{
  "decision": "approved",
  "amount": 50000.0,
  "justification": "Claim approved based on Section 4.2 covering orthopedic procedures. The policy covers knee surgery for members with at least 90 days of coverage.",
  "clause_mapping": [
    {
      "clause_text": "Orthopedic procedures including knee, hip, and shoulder surgeries are covered under this policy after the waiting period of 90 days...",
      "source": {
        "filename": "EDLHLGA23009V012223.pdf",
        "page": 5,
        "section": "COVERAGE DETAILS"
      }
    }
  ]
}
```

## System Architecture

### 1. Document Ingestion & Chunking
- **PDFProcessor**: Extracts text using PyMuPDF
- **Smart Chunking**: Creates 500-character chunks with 50-character overlap
- **Metadata Preservation**: Maintains page numbers, sections, and filenames

### 2. Embedding & Indexing
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Storage**: In-memory numpy arrays for fast similarity computation
- **Batch Processing**: Efficient embedding creation for multiple chunks

### 3. Semantic Retrieval
- **Query Embedding**: Same model as document chunks for consistency
- **Similarity Search**: Cosine similarity with configurable top-k results
- **Score Filtering**: Returns relevance scores for audit purposes

### 4. LLM Reasoning
- **Primary**: OpenAI GPT-4 for sophisticated policy analysis
- **Fallback**: Rule-based system when API is unavailable
- **Structured Prompting**: Enforces JSON output format and clause citations

### 5. Response Generation
- **Structured Output**: QueryResult dataclass with validation
- **Audit Logging**: Complete trace of reasoning process
- **Error Handling**: Graceful degradation with meaningful error messages

## Configuration Options

### PDF Processing
- `chunk_size`: Target characters per chunk (default: 500)
- `overlap`: Character overlap between chunks (default: 50)

### Embedding Model
- Default: `all-MiniLM-L6-v2` (multilingual, 384 dimensions)
- Alternative models: `all-mpnet-base-v2`, `all-distilroberta-v1`

### LLM Settings
- Model: GPT-4 (configurable)
- Temperature: 0.1 (for consistent, factual responses)
- Max tokens: 1000

## Logging & Audit

The system maintains comprehensive logs in `rag_audit.log`:
- Document processing statistics
- Query processing details
- Chunk retrieval information
- LLM reasoning traces
- Error conditions and fallbacks

## Error Handling

- **File Not Found**: Clear error messages for missing PDFs
- **API Failures**: Automatic fallback to rule-based reasoning
- **Invalid JSON**: Robust parsing with error recovery
- **Empty Results**: Meaningful responses when no relevant content found

## Performance Considerations

- **Memory Usage**: Stores embeddings in-memory for fast access
- **Processing Time**: ~2-5 seconds per query depending on document size
- **Scalability**: Suitable for documents up to 100MB, 1000+ pages
- **Batch Processing**: Efficient for multiple queries on same document

## Security & Privacy

- **Local Processing**: Document analysis happens locally
- **API Security**: Only sends relevant chunks to LLM, not full documents
- **No Storage**: No persistent storage of sensitive document content
- **Audit Trail**: Complete logging for compliance requirements

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **OpenAI API Errors**:
   - Check API key validity
   - Verify rate limits and quotas
   - System will fall back to rule-based reasoning

3. **PDF Processing Errors**:
   - Ensure PDF is not password-protected
   - Check file permissions
   - Try alternative PDF files

4. **Memory Issues**:
   - Reduce chunk_size for large documents
   - Process documents in smaller sections

### Debug Mode
```bash
# Enable detailed logging
python -u rag_policy_qa.py --policy "document.pdf" --query "your query" 2>&1 | tee debug.log
```

## Development & Customization

The system is designed for easy extension:

- **Custom Embedding Models**: Modify `EmbeddingEngine.__init__()`
- **Different LLMs**: Extend `LLMReasoningEngine` class
- **Enhanced Chunking**: Customize `PDFProcessor._split_text_into_chunks()`
- **Additional Metadata**: Extend `DocumentChunk` dataclass

## Examples with Sample Data

Using the provided sample PDFs:

```bash
# Process Bajaj policy
python rag_policy_qa.py --policy "./Sample data/BAJHLIP23020V012223.pdf" --query "What are the exclusions for pre-existing conditions?"

# Check Cholamandalam coverage
python rag_policy_qa.py --policy "./Sample data/CHOTGDP23004V012223.pdf" --query "Emergency hospitalization coverage limits"

# Analyze Edelweiss policy
python rag_policy_qa.py --policy "./Sample data/EDLHLGA23009V012223.pdf" --query "Maternity benefits waiting period"

# Review HDFC terms
python rag_policy_qa.py --policy "./Sample data/HDFHLIP23024V072223.pdf" --query "Network hospital cashless treatment process"

# ICICI policy analysis
python rag_policy_qa.py --policy "./Sample data/ICIHLIP22012V012223.pdf" --query "Day care procedure coverage and limits"
```

## License

This code is provided as-is for educational and development purposes. Please ensure compliance with your organization's policies and applicable regulations when processing sensitive documents.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the audit logs in `rag_audit.log`
3. Test with different PDF files to isolate issues
4. Verify all dependencies are correctly installed
