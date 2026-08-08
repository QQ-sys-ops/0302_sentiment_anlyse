from modelscope import snapshot_download
from sentence_transformers import SentenceTransformer

if __name__ == "__main__":
    local_dir = "D:/ai_models/modelscope_cache/models/BAAI"

    model_dir = snapshot_download("BAAI/bge-small-zh-v1.5", local_dir=local_dir)

    # 1. 加载下载好的本地模型
    model = SentenceTransformer(model_dir)

    # 2. 简单测试
    embeddings = model.encode(["测试语句"])

    print(f"模型已保存至: {model_dir}")
    print(f"嵌入向量 Shape: {embeddings.shape}")