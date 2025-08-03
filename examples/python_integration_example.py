#!/usr/bin/env python3
"""
Example Python script that can be called from n8n using Execute Command node
This script demonstrates how to process data from n8n and return results
"""

import sys
import json
import argparse
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def process_text_with_ai(text, operation="summarize"):
    """
    Example function that processes text using local AI libraries
    In a real scenario, this might use transformers, spacy, etc.
    """
    try:
        if operation == "summarize":
            # Simulate text summarization
            words = text.split()
            summary = " ".join(words[:min(20, len(words))]) + "..."
            return {"summary": summary, "word_count": len(words)}
        
        elif operation == "sentiment":
            # Simulate sentiment analysis
            positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                sentiment = "positive"
            elif neg_count > pos_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
                
            return {
                "sentiment": sentiment,
                "positive_score": pos_count,
                "negative_score": neg_count
            }
        
        else:
            return {"error": f"Unknown operation: {operation}"}
            
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Process text with AI")
    parser.add_argument("--text", required=True, help="Text to process")
    parser.add_argument("--operation", default="summarize", 
                       choices=["summarize", "sentiment"],
                       help="Operation to perform")
    parser.add_argument("--output-format", default="json",
                       choices=["json", "text"],
                       help="Output format")
    
    args = parser.parse_args()
    
    # Process the text
    result = process_text_with_ai(args.text, args.operation)
    
    # Output result in requested format
    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        else:
            # Format as readable text
            if args.operation == "summarize":
                print(f"Summary: {result['summary']}")
                print(f"Word count: {result['word_count']}")
            elif args.operation == "sentiment":
                print(f"Sentiment: {result['sentiment']}")
                print(f"Scores - Positive: {result['positive_score']}, Negative: {result['negative_score']}")

if __name__ == "__main__":
    main()
