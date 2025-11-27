import click
import json
import dspy
import os
from your_project.agent.graph_hybrid import RetailAgent

# Configure DSPy
lm = dspy.LM('ollama/phi3.5:3.8b-mini-instruct-q4_K_M', api_base='http://localhost:11434')
dspy.settings.configure(lm=lm)

@click.command()
@click.option('--batch', required=True, help='Path to input JSONL file')
@click.option('--out', required=True, help='Path to output JSONL file')
def main(batch, out):
    """Run the Retail Analytics Copilot."""
    
    # Initialize Agent
    agent = RetailAgent(
        db_path='your_project/data/northwind.sqlite',
        docs_dir='your_project/docs'
    )
    
    results = []
    
    with open(batch, 'r') as f:
        questions = [json.loads(line) for line in f]
        
    for item in questions:
        print(f"Processing: {item['id']}")
        
        initial_state = {
            "question": item["question"],
            "format_hint": item["format_hint"],
            "classification": "",
            "retrieved_docs": [],
            "constraints": "",
            "sql_query": "",
            "sql_result": {},
            "final_answer": None,
            "explanation": "",
            "citations": [],
            "error": None,
            "repair_count": 0
        }
        
        try:
            final_state = agent.graph.invoke(initial_state)
            
            output = {
                "id": item["id"],
                "final_answer": final_state.get("final_answer"),
                "sql": final_state.get("sql_query", ""),
                "confidence": 0.0, 
                "explanation": final_state.get("explanation", ""),
                "citations": final_state.get("citations", [])
            }
            
            # Simple confidence heuristic
            if final_state.get("error"):
                output["confidence"] = 0.1
            elif output["sql"] and final_state.get("sql_result", {}).get("rows"):
                output["confidence"] = 0.9
            elif output["citations"]:
                output["confidence"] = 0.8
            else:
                output["confidence"] = 0.5
                
            results.append(output)
            
        except Exception as e:
            print(f"Error processing {item['id']}: {e}")
            results.append({
                "id": item["id"],
                "final_answer": None,
                "sql": "",
                "confidence": 0.0,
                "explanation": f"Error: {str(e)}",
                "citations": []
            })

    # Write results
    with open(out, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
            
    print(f"Done. Results written to {out}")

if __name__ == '__main__':
    main()
