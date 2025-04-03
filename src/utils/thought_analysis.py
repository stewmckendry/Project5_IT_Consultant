# src/utils/thought_analysis.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

def cluster_thoughts_by_similarity(thoughts, threshold=0.85):
    """
    Groups semantically similar thoughts using cosine similarity.
    Returns a list of lists of indices (clusters).
    Threshold: The minimum similarity score to consider thoughts as similar. Default is 0.85. Range from 0 to 1 (where 1 is identical).
    """
    if not thoughts:
        return []

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(thoughts)
    similarity_matrix = cosine_similarity(embeddings) # 2D matrix of shape (n, n) of similarity between all pairs of thoughts

    clusters = [] # List to hold clusters of similar thoughts (their indices)
    used = set() # Set to keep track of which thoughts have been clustered

    for i, row in enumerate(similarity_matrix):
        if i in used:
            continue
        group = [i]
        for j in range(i + 1, len(row)):
            if row[j] > threshold and j not in used: #
                group.append(j)
                used.add(j)
        used.update(group)
        clusters.append(group)

    return clusters
