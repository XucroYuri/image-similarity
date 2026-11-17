import numpy as np

from image_similarity.stores.vector_store import VectorStore


def test_top_k_cosine(tmp_path):
    dim = 8
    vs = VectorStore(tmp_path / "v.bin", tmp_path / "ids.json", dim)
    a = np.array([[1, 0, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
    b = np.array([[0.9, 0.1, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
    c = np.array([[0, 1, 0, 0, 0, 0, 0, 0]], dtype=np.float32)
    vs.append(["a", "b", "c"], np.vstack([a, b, c]))
    hits = vs.top_k(a[0], k=2)
    assert hits[0][0] == "a"
    assert hits[0][1] > 0.99
