import dspy
from dspy.teleprompt import BootstrapFewShot
from your_project.agent.dspy_signatures import GenerateSQL
from your_project.agent.train_data import train_examples
import os

# Configure DSPy
lm = dspy.LM('ollama/phi3.5:3.8b-mini-instruct-q4_K_M', api_base='http://localhost:11434')
dspy.settings.configure(lm=lm)

def validate_sql(example, pred, trace=None):
    # Simple validation: check if SQL starts with SELECT and contains basic keywords
    sql = pred.sql_query.upper()
    return sql.startswith("SELECT")

def optimize():
    print("Optimizing GenerateSQL module...")
    
    # Define the module to optimize
    # We need a module that uses the signature
    class SQLGenerator(dspy.Module):
        def __init__(self):
            super().__init__()
            self.generate = dspy.ChainOfThought(GenerateSQL)
            
        def forward(self, question, db_schema, constraints):
            return self.generate(question=question, db_schema=db_schema, constraints=constraints)

    module = SQLGenerator()
    
    # Define optimizer
    teleprompter = BootstrapFewShot(metric=validate_sql, max_bootstrapped_demos=4, max_labeled_demos=4)
    
    # Compile
    compiled_module = teleprompter.compile(module, trainset=train_examples)
    
    # Save
    save_path = 'your_project/agent/compiled_sql_generator.json'
    compiled_module.save(save_path)
    print(f"Optimization complete. Saved to {save_path}")
    
    # Evaluate (simple print)
    print("Evaluation on train set:")
    for ex in train_examples[:2]:
        pred = compiled_module(question=ex.question, db_schema=ex.db_schema, constraints=ex.constraints)
        print(f"Q: {ex.question}")
        print(f"Predicted SQL: {pred.sql_query}")
        print("-" * 20)

if __name__ == '__main__':
    optimize()
