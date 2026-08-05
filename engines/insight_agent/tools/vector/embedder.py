"""BGE-M3 向量编码器：负责 Dense 与 Sparse 向量的生成"""

from functools import cached_property
from typing import  Iterable

from FlagEmbedding import BGEM3FlagModel

from engines.contracts.settings import get_settings


def _normalize_sparse_vector(sparse_vector: dict) -> dict[int, float]:
    return {
        int(token_id): float(weight)
        for token_id, weight in sparse_vector.items()
    }


class VectorEmbedder:
    """封装 BGE-M3 模型的向量编码服务。"""

    @cached_property
    def model(self) -> BGEM3FlagModel:
        settings = get_settings()
        device = settings.INSIGHT_EMBEDDING_DEVICE

        return BGEM3FlagModel(
            settings.INSIGHT_EMBEDDING_MODEL,
            use_fp16="cpu" not in device.lower(),
            devices=device,
        )

    def encode(
            self, texts: Iterable[str]
    ) -> list[tuple[list[float], dict[int, float]]]:
        """生成稠密与稀疏向量组合。"""
        text_items = list(texts)
        model_output = self.model.encode(
            text_items,
            return_dense=True,
            return_sparse=True
        )
        return [
            (dense.tolist(), _normalize_sparse_vector(sparse))
            for dense, sparse in zip(
                model_output["dense_vecs"], model_output["lexical_weights"]
            )
        ]


if __name__ == "__main__":
    texts = [
        "今天天气真好"
    ]
    embedder = VectorEmbedder()
    results = embedder.encode(texts)
    for idx, (dense_vec, sparse_vec) in enumerate(results,start=1):
        print(f"内容: {texts[idx]}")
        print(f"稠密向量维度: {len(dense_vec)}")
        print(f"稠密向量前 5 个元素: {dense_vec[:5]}")
        print(f"稀疏向量词数: {len(sparse_vec)}")
        # 打印稀疏向量前 3 个 token_id 及权重
        sparse = list(sparse_vec.items())[:3]
        print(f"稀疏向量采样: {sparse}")
