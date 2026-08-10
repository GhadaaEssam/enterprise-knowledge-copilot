# src/ingestion/embedder.py
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
from pathlib import Path


class Embedder:
    def __init__(self, path: str | Path):
        model_dir = Path(path)
        tokenizer_file = model_dir / "tokenizer.json"
        if not tokenizer_file.exists():
            raise FileNotFoundError(f"tokenizer.json not found at {tokenizer_file.resolve()}")
            
        self.tokenizer = Tokenizer.from_file(str(tokenizer_file))

        self.session = ort.InferenceSession(
            str(model_dir / "model.onnx"), providers=["CPUExecutionProvider"]
        )
        self.input_names = {inp.name for inp in self.session.get_inputs()}

    def encode(self, text: str, normalize: bool = True) -> np.ndarray:
        """Encodes a single text string into a 1D vector of shape (D,)."""
        vector = self.encode_batch([text], normalize=normalize)[0]
        # Ensure array is strictly 1D and float32
        return np.asarray(vector, dtype=np.float32).reshape(-1)

    def encode_batch(
        self, texts: list[str], normalize: bool = True
    ) -> np.ndarray:
        """Encodes a list of texts into a 2D array of shape (N, D)."""
        self.tokenizer.enable_padding()
        encoded = self.tokenizer.encode_batch(texts)
        feed = {}

        if "input_ids" in self.input_names:
            feed["input_ids"] = np.array(
                [e.ids for e in encoded], dtype=np.int64
            )
        if "attention_mask" in self.input_names:
            feed["attention_mask"] = np.array(
                [e.attention_mask for e in encoded], dtype=np.int64
            )
        if "token_type_ids" in self.input_names:
            feed["token_type_ids"] = np.array(
                [e.type_ids for e in encoded], dtype=np.int64
            )

        hidden = self.session.run(None, feed)[0]

        # Mean pooling over token embeddings
        mask = feed["attention_mask"][..., None]
        sum_embeddings = (hidden * mask).sum(axis=1)
        sum_mask = np.clip(mask.sum(axis=1), a_min=1e-9, a_max=None)
        pooled = sum_embeddings / sum_mask

        if normalize:
            norms = np.linalg.norm(pooled, axis=1, keepdims=True)
            norms = np.clip(norms, a_min=1e-9, a_max=None)
            pooled = pooled / norms

        return pooled.astype(np.float32)