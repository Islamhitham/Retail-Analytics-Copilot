import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class Retriever:
    def __init__(self, docs_dir):
        self.docs_dir = docs_dir
        self.chunks = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self._load_and_chunk_docs()
        self._build_index()

    def _load_and_chunk_docs(self):
        """Load markdown files and chunk them by headers or paragraphs."""
        md_files = glob.glob(os.path.join(self.docs_dir, "*.md"))
        for file_path in md_files:
            filename = os.path.basename(file_path).replace('.md', '')
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple chunking by double newlines (paragraphs) or headers
            # We'll split by double newlines for now as a simple heuristic
            raw_chunks = content.split('\n\n')
            for i, chunk in enumerate(raw_chunks):
                if chunk.strip():
                    self.chunks.append({
                        'id': f"{filename}::chunk{i}",
                        'content': chunk.strip(),
                        'source': filename
                    })

    def _build_index(self):
        if not self.chunks:
            return
        corpus = [chunk['content'] for chunk in self.chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query, k=3):
        if not self.chunks:
            return []
        
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top k indices
        top_k_indices = similarities.argsort()[-k:][::-1]
        
        results = []
        for idx in top_k_indices:
            if similarities[idx] > 0: # Only return relevant results
                result = self.chunks[idx].copy()
                result['score'] = float(similarities[idx])
                results.append(result)
        
        return results
