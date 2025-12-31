"""
向量数据库服务模块
提供算法、用户、帖子的向量化存储和相似度计算功能
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from datetime import datetime
import threading
import hashlib

logger = logging.getLogger(__name__)


class VectorService:
    """向量数据库服务类"""

    def __init__(self, persist_directory: str = "./vector_db"):
        """
        初始化向量服务

        Args:
            persist_directory: 向量数据库持久化目录
        """
        self.persist_directory = persist_directory
        self.model_name = "all-MiniLM-L6-v2"  # 轻量级但效果好的模型
        self.embedding_model = None
        self.client = None
        self.collections = {}

        # 线程锁确保并发安全
        self._lock = threading.Lock()

        # 延迟初始化
        self._initialized = False

    def initialize(self):
        """初始化向量数据库和模型"""
        if self._initialized:
            return

        try:
            with self._lock:
                if self._initialized:
                    return

                logger.info("Initializing vector service...")

                # 初始化embedding模型
                self.embedding_model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")

                # 初始化ChromaDB客户端
                os.makedirs(self.persist_directory, exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False, allow_reset=True),
                )

                # 创建或获取集合
                self._create_collections()

                self._initialized = True
                logger.info("Vector service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise

    def _create_collections(self):
        """创建向量数据库集合"""
        collections_config = {
            "algorithms": {
                "description": "Algorithm content embeddings",
                "metadata": {
                    "type": "algorithm",
                    "created_at": datetime.utcnow().isoformat(),
                },
            },
            "posts": {
                "description": "Post content embeddings",
                "metadata": {
                    "type": "post",
                    "created_at": datetime.utcnow().isoformat(),
                },
            },
            "users": {
                "description": "User interest embeddings",
                "metadata": {
                    "type": "user",
                    "created_at": datetime.utcnow().isoformat(),
                },
            },
        }

        for collection_name, config in collections_config.items():
            try:
                collection = self.client.get_or_create_collection(
                    name=collection_name, metadata=config["metadata"]
                )
                self.collections[collection_name] = collection
                logger.info(f"Created/get collection: {collection_name}")
            except Exception as e:
                logger.error(f"Failed to create collection {collection_name}: {e}")
                raise

    def _ensure_initialized(self):
        """确保服务已初始化"""
        if not self._initialized:
            self.initialize()

    def _get_text_hash(self, text: str) -> str:
        """获取文本的哈希值，用于去重"""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    # ==================== 算法向量化 ====================

    def vectorize_algorithm(self, algorithm_data: Dict[str, Any]) -> np.ndarray:
        """
        将算法数据转换为向量

        Args:
            algorithm_data: 算法数据字典

        Returns:
            算法的向量表示
        """
        self._ensure_initialized()

        # 构建算法的文本表示
        texts = []

        # 主要内容
        if algorithm_data.get("name"):
            texts.append(f"算法名称: {algorithm_data['name']}")
        if algorithm_data.get("chinese_name"):
            texts.append(f"中文名称: {algorithm_data['chinese_name']}")
        if algorithm_data.get("description"):
            texts.append(f"描述: {algorithm_data['description']}")

        # 标签
        if algorithm_data.get("tags"):
            tags_text = "标签: " + " ".join(algorithm_data["tags"])
            texts.append(tags_text)

        # 难度
        if algorithm_data.get("difficulty"):
            texts.append(f"难度: {algorithm_data['difficulty']}")

        # 理论内容（如果有的话）
        if algorithm_data.get("theory"):
            theory_preview = algorithm_data["theory"][:500]  # 限制长度
            texts.append(f"理论: {theory_preview}")

        # 代码示例（如果有的话）
        if algorithm_data.get("code_example"):
            code_preview = algorithm_data["code_example"][:300]  # 限制长度
            texts.append(f"代码: {code_preview}")

        # 合并所有文本
        combined_text = " ".join(texts)

        # 生成向量
        vector = self.embedding_model.encode(combined_text, normalize_embeddings=True)
        return vector

    def add_algorithm(self, algorithm_id: int, algorithm_data: Dict[str, Any]):
        """
        添加算法到向量数据库

        Args:
            algorithm_id: 算法ID
            algorithm_data: 算法数据
        """
        self._ensure_initialized()

        try:
            vector = self.vectorize_algorithm(algorithm_data)

            # 准备元数据
            metadata = {
                "id": algorithm_id,
                "name": algorithm_data.get("name", ""),
                "difficulty": algorithm_data.get("difficulty", ""),
                "category": (
                    algorithm_data.get("category", {}).get("name", "")
                    if algorithm_data.get("category")
                    else ""
                ),
                "tags": json.dumps(algorithm_data.get("tags", [])),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # 添加到集合
            self.collections["algorithms"].add(
                embeddings=[vector.tolist()],
                documents=[algorithm_data.get("description", "")],
                metadatas=[metadata],
                ids=[str(algorithm_id)],
            )

            logger.info(f"Added algorithm {algorithm_id} to vector database")

        except Exception as e:
            logger.error(f"Failed to add algorithm {algorithm_id}: {e}")
            raise

    def update_algorithm(self, algorithm_id: int, algorithm_data: Dict[str, Any]):
        """更新算法向量"""
        try:
            # 删除旧向量
            self.collections["algorithms"].delete(ids=[str(algorithm_id)])
            # 添加新向量
            self.add_algorithm(algorithm_id, algorithm_data)
        except Exception as e:
            logger.error(f"Failed to update algorithm {algorithm_id}: {e}")
            raise

    def find_similar_algorithms(
        self, query_vector: np.ndarray, limit: int = 10, exclude_ids: List[int] = None
    ) -> List[Dict[str, Any]]:
        """
        查找相似的算法

        Args:
            query_vector: 查询向量
            limit: 返回结果数量
            exclude_ids: 要排除的算法ID列表

        Returns:
            相似算法列表
        """
        self._ensure_initialized()

        try:
            # 构建过滤条件
            where = None
            if exclude_ids:
                where = {"id": {"$nin": [str(id) for id in exclude_ids]}}

            # 获取所有算法向量进行相似度计算
            all_algorithms = self.collections["algorithms"].get(
                where=where, include=["embeddings", "metadatas"]
            )

            similar_algorithms = []
            if all_algorithms["embeddings"] and all_algorithms["metadatas"]:
                algorithm_vectors = np.array(all_algorithms["embeddings"])
                query_vector_norm = query_vector / np.linalg.norm(query_vector)
                algorithm_vectors_norm = algorithm_vectors / np.linalg.norm(
                    algorithm_vectors, axis=1, keepdims=True
                )

                # 计算余弦相似度
                similarities = np.dot(algorithm_vectors_norm, query_vector_norm)

                # 创建结果列表
                results = []
                for i, metadata in enumerate(all_algorithms["metadatas"]):
                    similarity_score = float(similarities[i])
                    results.append(
                        {
                            "id": int(metadata["id"]),
                            "name": metadata["name"],
                            "difficulty": metadata["difficulty"],
                            "category": metadata["category"],
                            "tags": json.loads(metadata.get("tags", "[]")),
                            "similarity_score": round(similarity_score, 4),
                            "metadata": metadata,
                        }
                    )

                # 按相似度排序并限制数量
                results.sort(key=lambda x: x["similarity_score"], reverse=True)
                similar_algorithms = results[:limit]

            return similar_algorithms

        except Exception as e:
            logger.error(f"Failed to find similar algorithms: {e}")
            return []

    # ==================== 帖子向量化 ====================

    def vectorize_post(self, post_data: Dict[str, Any]) -> np.ndarray:
        """
        将帖子数据转换为向量

        Args:
            post_data: 帖子数据字典

        Returns:
            帖子的向量表示
        """
        self._ensure_initialized()

        # 构建帖子的文本表示
        texts = []

        # 主要内容
        if post_data.get("title"):
            texts.append(f"标题: {post_data['title']}")
        if post_data.get("content"):
            content_preview = post_data["content"][:1000]  # 限制长度
            texts.append(f"内容: {content_preview}")

        # 标签
        if post_data.get("tags"):
            tags_text = "标签: " + " ".join(post_data["tags"])
            texts.append(tags_text)

        # 作者信息
        if post_data.get("author") and post_data["author"].get("username"):
            texts.append(f"作者: {post_data['author']['username']}")

        # 合并所有文本
        combined_text = " ".join(texts)

        # 生成向量
        vector = self.embedding_model.encode(combined_text, normalize_embeddings=True)
        return vector

    def add_post(self, post_id: int, post_data: Dict[str, Any]):
        """
        添加帖子到向量数据库

        Args:
            post_id: 帖子ID
            post_data: 帖子数据
        """
        self._ensure_initialized()

        try:
            vector = self.vectorize_post(post_data)

            # 准备元数据
            metadata = {
                "id": post_id,
                "title": post_data.get("title", ""),
                "author_id": post_data.get("author", {}).get("id", 0),
                "author_username": post_data.get("author", {}).get("username", ""),
                "tags": json.dumps(post_data.get("tags", [])),
                "like_count": post_data.get("like_count", 0),
                "comment_count": post_data.get("comment_count", 0),
                "is_featured": post_data.get("is_featured", False),
                "created_at": post_data.get(
                    "created_at", datetime.utcnow().isoformat()
                ),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # 添加到集合
            self.collections["posts"].add(
                embeddings=[vector.tolist()],
                documents=[
                    f"{post_data.get('title', '')} {post_data.get('content', '')[:500]}"
                ],
                metadatas=[metadata],
                ids=[str(post_id)],
            )

            logger.info(f"Added post {post_id} to vector database")

        except Exception as e:
            logger.error(f"Failed to add post {post_id}: {e}")
            raise

    def update_post(self, post_id: int, post_data: Dict[str, Any]):
        """更新帖子向量"""
        try:
            # 删除旧向量
            self.collections["posts"].delete(ids=[str(post_id)])
            # 添加新向量
            self.add_post(post_id, post_data)
        except Exception as e:
            logger.error(f"Failed to update post {post_id}: {e}")
            raise

    def find_similar_posts(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        exclude_ids: List[int] = None,
        author_id: int = None,
        min_similarity: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        查找相似的帖子

        Args:
            query_vector: 查询向量
            limit: 返回结果数量
            exclude_ids: 要排除的帖子ID列表
            author_id: 排除指定作者的帖子
            min_similarity: 最小相似度阈值

        Returns:
            相似帖子列表
        """
        self._ensure_initialized()

        try:
            # 构建过滤条件
            where = {}
            if exclude_ids:
                where["id"] = {"$nin": [str(id) for id in exclude_ids]}
            if author_id:
                where["author_id"] = {"$ne": str(author_id)}

            # 获取所有帖子向量进行相似度计算
            all_posts = self.collections["posts"].get(
                where=where if where else None, include=["embeddings", "metadatas"]
            )

            similar_posts = []
            if all_posts["embeddings"] and all_posts["metadatas"]:
                post_vectors = np.array(all_posts["embeddings"])
                query_vector_norm = query_vector / np.linalg.norm(query_vector)
                post_vectors_norm = post_vectors / np.linalg.norm(
                    post_vectors, axis=1, keepdims=True
                )

                # 计算余弦相似度
                similarities = np.dot(post_vectors_norm, query_vector_norm)

                # 创建结果列表
                results = []
                for i, metadata in enumerate(all_posts["metadatas"]):
                    similarity_score = float(similarities[i])

                    # 过滤相似度过低的
                    if similarity_score < min_similarity:
                        continue

                    post_info = {
                        "id": int(metadata["id"]),
                        "title": metadata["title"],
                        "author": {
                            "id": int(metadata["author_id"]),
                            "username": metadata["author_username"],
                        },
                        "tags": json.loads(metadata.get("tags", "[]")),
                        "like_count": metadata.get("like_count", 0),
                        "comment_count": metadata.get("comment_count", 0),
                        "is_featured": metadata.get("is_featured", False),
                        "created_at": metadata.get("created_at", ""),
                        "similarity_score": round(similarity_score, 4),
                        "metadata": metadata,
                    }
                    results.append(post_info)

                # 按相似度排序并限制数量
                results.sort(key=lambda x: x["similarity_score"], reverse=True)
                similar_posts = results[:limit]

            return similar_posts

        except Exception as e:
            logger.error(f"Failed to find similar posts: {e}")
            return []

    def find_posts_by_text(
        self, query_text: str, limit: int = 10, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        通过文本查找相似帖子

        Args:
            query_text: 查询文本
            limit: 返回结果数量
            **kwargs: 其他参数传递给find_similar_posts

        Returns:
            相似帖子列表
        """
        self._ensure_initialized()

        try:
            # 将查询文本转换为向量
            query_vector = self.embedding_model.encode(
                query_text, normalize_embeddings=True
            )
            return self.find_similar_posts(query_vector, limit=limit, **kwargs)
        except Exception as e:
            logger.error(f"Failed to find posts by text '{query_text}': {e}")
            return []

    # ==================== 用户兴趣向量化 ====================

    def vectorize_user_interests(self, user_data: Dict[str, Any]) -> np.ndarray:
        """
        将用户兴趣数据转换为向量

        Args:
            user_data: 用户兴趣数据

        Returns:
            用户兴趣的向量表示
        """
        self._ensure_initialized()

        # 提取用户兴趣相关的文本
        interest_texts = []

        # 学习记录
        if user_data.get("knowledge_records"):
            for record in user_data["knowledge_records"]:
                if record.get("progress", 0) > 50:  # 只考虑进度>50%的
                    algorithm_name = record.get("algorithm", {}).get("name", "")
                    interests = record.get("interests", [])
                    progress = record.get("progress", 0)

                    text = (
                        f"学习了算法: {algorithm_name}, 进度: {progress}%, "
                        f"兴趣: {' '.join(interests)}"
                    )
                    interest_texts.append(text)

        # 点赞的帖子
        if user_data.get("liked_posts"):
            for post in user_data["liked_posts"][:5]:  # 限制数量
                if post:  # 确保post不为None
                    title = post.get("title", "")
                    tags = post.get("tags", [])
                    text = f"点赞了帖子: {title}, 标签: {' '.join(tags)}"
                    interest_texts.append(text)

        # 收藏的帖子
        if user_data.get("favorited_posts"):
            for post in user_data["favorited_posts"][:5]:  # 限制数量
                if post:  # 确保post不为None
                    title = post.get("title", "")
                    tags = post.get("tags", [])
                    text = f"收藏了帖子: {title}, 标签: {' '.join(tags)}"
                    interest_texts.append(text)

        # 评论的帖子
        if user_data.get("commented_posts"):
            for post in user_data["commented_posts"][:5]:  # 限制数量
                if post:  # 确保post不为None
                    title = post.get("title", "")
                    tags = post.get("tags", [])
                    text = f"评论了帖子: {title}, 标签: {' '.join(tags)}"
                    interest_texts.append(text)

        # 发布的帖子（自己的兴趣体现）
        if user_data.get("own_posts"):
            for post in user_data["own_posts"][:10]:  # 限制数量
                if post:  # 确保post不为None
                    title = post.get("title", "")
                    content = post.get("content", "")[:200]  # 限制内容长度
                    tags = post.get("tags", [])
                    text = f"发布了帖子: {title} {content}, 标签: {' '.join(tags)}"
                    interest_texts.append(text)

        # 如果没有足够的数据，返回零向量
        if not interest_texts:
            return np.zeros(384)  # sentence-transformers默认维度

        # 合并所有兴趣文本
        combined_text = " ".join(interest_texts)

        # 生成向量
        vector = self.embedding_model.encode(combined_text, normalize_embeddings=True)
        return vector

    def add_user_interests(self, user_id: int, user_data: Dict[str, Any]):
        """
        添加用户兴趣到向量数据库

        Args:
            user_id: 用户ID
            user_data: 用户数据
        """
        self._ensure_initialized()

        try:
            vector = self.vectorize_user_interests(user_data)

            # 准备元数据
            metadata = {
                "id": user_id,
                "username": user_data.get("username", ""),
                "total_posts": len(user_data.get("own_posts", [])),
                "total_likes": len(user_data.get("liked_posts", [])),
                "total_favorites": len(user_data.get("favorited_posts", [])),
                "learned_algorithms": len(user_data.get("knowledge_records", [])),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # 添加到集合
            self.collections["users"].add(
                embeddings=[vector.tolist()],
                documents=[f"User {user_id} interests"],
                metadatas=[metadata],
                ids=[str(user_id)],
            )

            logger.info(f"Added user {user_id} interests to vector database")

        except Exception as e:
            logger.error(f"Failed to add user {user_id} interests: {e}")
            raise

    def update_user_interests(self, user_id: int, user_data: Dict[str, Any]):
        """更新用户兴趣向量"""
        try:
            # 删除旧向量
            self.collections["users"].delete(ids=[str(user_id)])
            # 添加新向量
            self.add_user_interests(user_id, user_data)
        except Exception as e:
            logger.error(f"Failed to update user {user_id} interests: {e}")
            raise

    # ==================== 工具方法 ====================

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """获取集合统计信息"""
        self._ensure_initialized()

        try:
            collection = self.collections.get(collection_name)
            if not collection:
                return {"error": f"Collection {collection_name} not found"}

            count = collection.count()
            return {
                "collection": collection_name,
                "total_items": count,
                "last_updated": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get stats for collection {collection_name}: {e}")
            return {"error": str(e)}

    def reset_collection(self, collection_name: str):
        """重置集合"""
        self._ensure_initialized()

        try:
            if collection_name in self.collections:
                self.client.delete_collection(collection_name)
                logger.info(f"Reset collection: {collection_name}")

                # 重新创建集合
                self._create_collections()
        except Exception as e:
            logger.error(f"Failed to reset collection {collection_name}: {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            stats = {}
            for name in self.collections.keys():
                stats[name] = self.get_collection_stats(name)

            return {
                "status": "healthy" if self._initialized else "not_initialized",
                "model": self.model_name,
                "collections": stats,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# 全局向量服务实例
vector_service = VectorService()
