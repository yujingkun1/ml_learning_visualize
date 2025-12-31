import logging
from flask import Blueprint, request, jsonify
from models import (
    db,
    User,
    Algorithm,
    AlgorithmCategory,
    UserKnowledge,
    Post,
    Comment,
    Like,
    Favorite,
    AlgorithmPost,
    SystemLog,
    Friend,
    ChatMessage,
)
from routes.auth import token_required, log_action
import os
import json
import re
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import numpy as np

try:
    import requests
except Exception:
    requests = None
try:
    import imghdr
except Exception:
    imghdr = None

# Import vector service
from services.vector_service import vector_service

# Try to load converted scraped algorithm data
# (contains full theory and image references)
_CONVERTED_ALG_MAP = None


def _load_converted_map():
    global _CONVERTED_ALG_MAP
    if _CONVERTED_ALG_MAP is not None:
        return _CONVERTED_ALG_MAP

    data = {}
    candidates = [
        os.path.join(os.getcwd(), "scraped_data", "converted_algorithms.json"),
        os.path.join(os.getcwd(), "scraped_data", "missing_algorithms_converted.json"),
        os.path.join(os.getcwd(), "converted_algorithms.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    for it in items:
                        name = it.get("name")
                        if name:
                            data[name] = it
            except Exception:
                continue

    _CONVERTED_ALG_MAP = data
    return _CONVERTED_ALG_MAP


def _rewrite_image_paths(markdown_text, repo=None):
    """Rewrite relative image paths.
    If repo is provided, map relative paths (plot/, _images/) to local
    /ml_images/<repo>/... Otherwise, rewrite to raw GitHub URLs (legacy behavior).
    """
    if not markdown_text:
        return markdown_text

    if repo:
        text = markdown_text
        text = text.replace("](" + "plot/", "](/ml_images/" + repo + "/plot/")
        text = text.replace("(plot/", "(/ml_images/" + repo + "/plot/")
        text = text.replace("](" + "../" + "plot/", "](/ml_images/" + repo + "/plot/")
        text = text.replace("](" + "_images/", "](/ml_images/" + repo + "/_images/")
        text = text.replace("../_images/", "/ml_images/" + repo + "/_images/")
        text = text.replace("(_images/", "(/ml_images/" + repo + "/_images/")
        # src="plot/...
        text = text.replace('src="plot/', 'src="/ml_images/' + repo + "/plot/")
        return text

    # Fallback: rewrite to the original repo's raw GitHub path
    base_raw = (
        "https://raw.githubusercontent.com/gavinkhung/machine-learning-visualized/"
        "main/book/"
    )
    # replace markdown image paths: ![alt](plot/...)
    markdown_text = re.sub(
        r"!\[([^\]]*)\]\((?:\.\./)*(plot/[^)]+)\)",
        r"![\\1](" + base_raw + r"\\2)",
        markdown_text,
    )
    # replace HTML img src attributes: src="plot/..."
    markdown_text = re.sub(
        r"(src=[\"\\\'])(?:\.\./)*(plot/[^\"\\\']+)([\"\\\'])",
        r"\\1" + base_raw + r"\\2\\3",
        markdown_text,
    )
    return markdown_text


api_bp = Blueprint("api", __name__)


# 算法相关API
@api_bp.route("/algorithms", methods=["GET"])
def get_algorithms():
    try:
        category_id = request.args.get("category_id", type=int)
        difficulty = request.args.get("difficulty")
        search = request.args.get("search")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        query = Algorithm.query

        if category_id:
            query = query.filter_by(category_id=category_id)

        if difficulty:
            query = query.filter_by(difficulty=difficulty)

        if search:
            query = query.filter(
                db.or_(
                    Algorithm.name.ilike(f"%{search}%"),
                    Algorithm.chinese_name.ilike(f"%{search}%"),
                    Algorithm.description.ilike(f"%{search}%"),
                )
            )

        algorithms = query.paginate(page=page, per_page=per_page, error_out=False)

        return (
            jsonify(
                {
                    "algorithms": [alg.to_dict() for alg in algorithms.items],
                    "total": algorithms.total,
                    "pages": algorithms.pages,
                    "current_page": algorithms.page,
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Get algorithms error: {e}")
        return jsonify({"message": "Failed to get algorithms"}), 500


@api_bp.route("/algorithms/<int:algorithm_id>", methods=["GET"])
def get_algorithm(algorithm_id):
    try:
        algorithm = Algorithm.query.get_or_404(algorithm_id)
        alg_dict = algorithm.to_dict()

        # Attempt to attach full theory from converted scraped data (if available)
        try:
            converted_map = _load_converted_map()
            conv = converted_map.get(algorithm.name) or converted_map.get(
                algorithm.chinese_name or ""
            )
            theory_text = None
            if conv:
                # theory might be under 'theory' (list) or 'theory' string
                if isinstance(conv.get("theory"), list):
                    theory_text = "\n\n".join(conv.get("theory"))
                else:
                    theory_text = conv.get("theory") or conv.get("description")
            # Fallback: if algorithm model has attribute 'theory', use it
            if not theory_text and hasattr(algorithm, "theory"):
                theory_text = getattr(algorithm, "theory", None)

            if theory_text:
                repo_name = conv.get("repo") if conv else None
                alg_dict["theory"] = _rewrite_image_paths(theory_text, repo=repo_name)
            else:
                alg_dict["theory"] = None
        except Exception as e:
            logging.warning(f"Failed to attach converted theory: {e}")
            alg_dict["theory"] = None

        return jsonify({"algorithm": alg_dict}), 200
    except Exception as e:
        logging.error(f"Get algorithm error: {e}")
        return jsonify({"message": "Algorithm not found"}), 404


@api_bp.route("/categories", methods=["GET"])
def get_categories():
    try:
        categories = AlgorithmCategory.query.order_by(AlgorithmCategory.order).all()

        # 构建树形结构
        def build_tree(parent_id=None):
            result = []
            for cat in categories:
                if cat.parent_id == parent_id:
                    cat_dict = cat.to_dict()
                    cat_dict["children"] = build_tree(cat.id)
                    result.append(cat_dict)
            return result

        tree = build_tree()
        return jsonify({"categories": tree}), 200

    except Exception as e:
        logging.error(f"Get categories error: {e}")
        return jsonify({"message": "Failed to get categories"}), 500


# 用户算法点击记录API
@api_bp.route("/user/algorithm/<int:algorithm_id>/click", methods=["POST"])
@token_required
def record_algorithm_click(current_user_id, algorithm_id):
    """记录用户点击算法的行为"""
    try:
        # 检查算法是否存在（仅用于验证存在性）
        Algorithm.query.get_or_404(algorithm_id)

        # 查找或创建用户知识记录
        knowledge = UserKnowledge.query.filter_by(
            user_id=current_user_id, algorithm_id=algorithm_id
        ).first()

        if knowledge:
            # 更新最后访问时间
            knowledge.last_accessed = db.func.now()
        else:
            # 创建新的点击记录（不设置进度）
            knowledge = UserKnowledge(
                user_id=current_user_id,
                algorithm_id=algorithm_id,
                progress=0.0,  # 点击记录不设置进度
                last_accessed=db.func.now(),
            )
            db.session.add(knowledge)

        db.session.commit()

        log_action(current_user_id, "click_algorithm", "algorithm", algorithm_id)

        return jsonify({"message": "Algorithm click recorded successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Record algorithm click error: {e}")
        return jsonify({"message": "Failed to record click"}), 500


# 用户知识记录API
@api_bp.route("/user/knowledge/<int:algorithm_id>", methods=["PUT"])
@token_required
def update_user_knowledge(current_user_id, algorithm_id):
    try:
        data = request.get_json()
        progress = data.get("progress", 0.0)
        interests = data.get("interests", [])

        knowledge = UserKnowledge.query.filter_by(
            user_id=current_user_id, algorithm_id=algorithm_id
        ).first()

        if knowledge:
            knowledge.progress = progress
            knowledge.interests = interests
            knowledge.last_accessed = db.func.now()
        else:
            knowledge = UserKnowledge(
                user_id=current_user_id,
                algorithm_id=algorithm_id,
                progress=progress,
                interests=interests,
            )
            db.session.add(knowledge)

        db.session.commit()

        log_action(
            current_user_id,
            "update_knowledge",
            "algorithm",
            algorithm_id,
            {"progress": progress, "interests": interests},
        )

        return (
            jsonify(
                {
                    "message": "Knowledge updated successfully",
                    "knowledge": knowledge.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Update knowledge error: {e}")
        return jsonify({"message": "Failed to update knowledge"}), 500


@api_bp.route("/user/knowledge", methods=["GET"])
@token_required
def get_user_knowledge(current_user_id):
    try:
        knowledge_records = UserKnowledge.query.filter_by(user_id=current_user_id).all()
        return jsonify({"knowledge": [k.to_dict() for k in knowledge_records]}), 200
    except Exception as e:
        logging.error(f"Get user knowledge error: {e}")
        return jsonify({"message": "Failed to get knowledge"}), 500


# 推荐算法API - 基于向量相似度的现代化推荐系统
@api_bp.route("/recommendations", methods=["GET"])
@token_required
def get_recommendations(current_user_id):
    """
    基于向量相似度的现代化推荐算法

    算法推荐策略：
    1. 基于用户学习历史的向量相似度推荐（权重70%）
    2. 基于用户兴趣标签的语义相似度推荐（权重20%）
    3. 基于学习进度的个性化调整（权重10%）

    帖子推荐策略：
    1. 基于用户兴趣向量的语义相似度（权重60%）
    2. 基于学习内容的关联性（权重25%）
    3. 基于社区热度和新鲜度（权重15%）
    """
    try:
        from datetime import datetime

        # 初始化向量服务
        vector_service.initialize()

        # 获取用户数据
        user = User.query.get(current_user_id)
        user_knowledge = UserKnowledge.query.filter_by(user_id=current_user_id).all()
        user_posts = Post.query.filter_by(author_id=current_user_id).all()
        _user_likes = Like.query.filter_by(user_id=current_user_id).all()
        _user_favorites = Favorite.query.filter_by(user_id=current_user_id).all()
        user_comments = Comment.query.filter_by(author_id=current_user_id).all()

        # 预加载帖子数据，避免N+1查询和None值
        liked_post_ids = [like.post_id for like in _user_likes]
        favorited_post_ids = [fav.post_id for fav in _user_favorites]
        commented_post_ids = list(set([comment.post_id for comment in user_comments]))

        # 批量获取帖子数据
        all_post_ids = set(liked_post_ids + favorited_post_ids + commented_post_ids)
        posts_dict = {}
        if all_post_ids:
            posts = Post.query.filter(Post.id.in_(all_post_ids)).all()
            posts_dict = {post.id: post for post in posts}

        current_time = datetime.utcnow()
        learned_algorithm_ids = [k.algorithm_id for k in user_knowledge]

        # ===== 算法推荐系统 =====

        # 1. 构建用户兴趣向量（基于学习历史和行为）
        user_interest_vector = None
        algorithm_recommendations = []

        try:
            # 获取或创建用户兴趣向量
            user_vector_result = vector_service.collections["users"].get(
                ids=[str(current_user_id)], include=["embeddings"]
            )

            if user_vector_result["embeddings"]:
                user_interest_vector = np.array(user_vector_result["embeddings"][0])
            else:
                # 如果没有预计算的用户向量，实时构建
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "knowledge_records": [
                        {
                            "algorithm": (
                                Algorithm.query.get(k.algorithm_id).to_dict()
                                if Algorithm.query.get(k.algorithm_id)
                                else None
                            ),
                            "progress": k.progress,
                            "interests": k.interests or [],
                        }
                        for k in user_knowledge
                    ],
                    "own_posts": [p.to_dict() for p in user_posts[:10]],  # 限制数量
                    "liked_posts": [
                        posts_dict.get(like.post_id).to_dict()
                        for like in _user_likes[:10]
                        if like.post_id in posts_dict
                    ],
                    "favorited_posts": [
                        posts_dict.get(fav.post_id).to_dict()
                        for fav in _user_favorites[:10]
                        if fav.post_id in posts_dict
                    ],
                    "commented_posts": list(
                        set(
                            [
                                posts_dict.get(c.post_id).to_dict()
                                for c in user_comments[:10]
                                if c.post_id in posts_dict
                            ]
                        )
                    ),
                }
                user_interest_vector = vector_service.vectorize_user_interests(
                    user_data
                )

            # 2. 基于向量相似度推荐算法
            if (user_interest_vector is not None and
                    not np.allclose(user_interest_vector, 0)):
                similar_algorithms = vector_service.find_similar_algorithms(
                    user_interest_vector,
                    limit=15,  # 多取一些用于后续过滤
                    exclude_ids=[],  # 不排除已学习的算法，让用户看到所有相关内容
                )

                logging.info(f"Found {len(similar_algorithms)} similar algorithms")

                # 简化推荐逻辑，直接使用相似度分数
                for alg in similar_algorithms:
                    algorithm = Algorithm.query.get(alg["id"])
                    if not algorithm:
                        continue

                    # 直接使用相似度作为分数
                    final_score = alg["similarity_score"] * 100  # 转换为0-100分

                    alg["final_score"] = round(final_score, 2)
                    alg["recommendation_reasons"] = ["基于兴趣推荐"]

                    logging.info(
                        f"Algorithm {alg['name']}: similarity "
                        f"{alg['similarity_score']:.4f}, final_score {final_score:.2f}"
                    )

                # 按相似度排序并限制数量
                algorithm_recommendations = sorted(
                    similar_algorithms,
                    key=lambda x: x["similarity_score"],
                    reverse=True,
                )[
                    :8
                ]  # 返回前8个

                logging.info(
                    f"Returning {len(algorithm_recommendations)} "
                    "algorithm recommendations"
                )

        except Exception as e:
            logging.warning(f"Vector-based algorithm recommendation failed: {e}")

        # 如果向量推荐失败或没有足够数据，使用改进的回退方法
        if not algorithm_recommendations:
            algorithm_recommendations = get_improved_fallback_algorithm_recommendations(
                current_user_id, learned_algorithm_ids, current_time
            )

        # ===== 帖子推荐系统 =====

        post_recommendations = []

        try:
            # 1. 基于用户兴趣向量推荐帖子
            if user_interest_vector is not None:
                similar_posts = vector_service.find_similar_posts(
                    user_interest_vector,
                    limit=12,  # 多取一些用于过滤
                    author_id=current_user_id,  # 排除自己的帖子
                    min_similarity=0.3,  # 最小相似度阈值
                )

                # 增强帖子推荐（添加学习相关性和社区因素）
                for post in similar_posts:
                    base_score = post["similarity_score"] * 100

                    # 学习相关性加成
                    learning_bonus = 0
                    post_obj = Post.query.get(post["id"])
                    if post_obj and post_obj.tags:
                        for knowledge in user_knowledge:
                            alg = Algorithm.query.get(knowledge.algorithm_id)
                            if alg and alg.tags:
                                tag_overlap = len(set(alg.tags) & set(post_obj.tags))
                                if tag_overlap > 0:
                                    learning_bonus += (
                                        knowledge.progress * 0.1 * tag_overlap
                                    )

                    # 社区热度加成
                    community_bonus = min(
                        (post.get("like_count", 0) + post.get("comment_count", 0))
                        * 0.5,
                        15,
                    )

                    # 新鲜度加成
                    time_bonus = 0
                    if post.get("created_at"):
                        days_old = (
                            current_time
                            - datetime.fromisoformat(
                                post["created_at"].replace("Z", "+00:00")
                            )
                        ).days
                        time_bonus = max(0, 10 - days_old)  # 新帖子加成更多

                    final_score = (
                        base_score + learning_bonus + community_bonus + time_bonus
                    )

                    post["final_score"] = round(final_score, 2)
                    post["recommendation_reasons"] = []
                    if base_score > 60:
                        post["recommendation_reasons"].append("内容相关")
                    if learning_bonus > 5:
                        post["recommendation_reasons"].append("学习相关")
                    if community_bonus > 5:
                        post["recommendation_reasons"].append("社区热门")

                # 排序并限制数量
                post_recommendations = sorted(
                    similar_posts, key=lambda x: x["final_score"], reverse=True
                )[
                    :6
                ]  # 返回前6个

        except Exception as e:
            logging.warning(f"Vector-based post recommendation failed: {e}")
            # 回退到传统方法
            post_recommendations = get_fallback_post_recommendations(
                current_user_id, current_time
            )

        # 如果向量推荐和传统推荐都没有结果，至少返回一些热门帖子
        if not post_recommendations:
            try:
                fallback_posts = (
                    Post.query.filter(Post.author_id != current_user_id)
                    .order_by(
                        Post.like_count.desc(),
                        Post.comment_count.desc(),
                        Post.created_at.desc(),
                    )
                    .limit(6)
                    .all()
                )

                post_recommendations = []
                for post in fallback_posts:
                    post_dict = post.to_dict()
                    post_dict["final_score"] = 50.0
                    post_dict["recommendation_reasons"] = ["热门内容"]
                    post_recommendations.append(post_dict)

                logging.info(
                    f"Using fallback popular posts: {len(post_recommendations)} posts"
                )

            except Exception as e:
                logging.error(f"Fallback post recommendation also failed: {e}")
                post_recommendations = []

        # 获取统计信息
        total_algorithms = Algorithm.query.count()
        total_posts = Post.query.count()
        total_interactions = (
            len(_user_likes) + len(_user_favorites) + len(user_comments)
        )

        return (
            jsonify(
                {
                    "algorithms": algorithm_recommendations,
                    "posts": post_recommendations,
                    "stats": {
                        "algorithms_analyzed": total_algorithms,
                        "posts_analyzed": total_posts,
                        "user_knowledge_count": len(user_knowledge),
                        "user_interactions": total_interactions,
                        "recommendation_method": "vector_similarity",
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Get recommendations error: {e}")
        return jsonify({"message": "Failed to get recommendations"}), 500


def get_improved_fallback_algorithm_recommendations(
    current_user_id, learned_algorithm_ids, current_time
):
    """改进的传统推荐算法回退方案"""
    try:
        # 如果用户没有学习任何算法，返回最热门的算法
        if not learned_algorithm_ids:
            # 按创建时间倒序，返回最新的算法
            algorithms = (Algorithm.query
                          .order_by(Algorithm.created_at.desc())
                          .limit(8)
                          .all())
            recommendations = []
            for alg in algorithms:
                alg_dict = alg.to_dict()
                alg_dict["final_score"] = 60.0  # 给新算法稍高的分数
                alg_dict["recommendation_reasons"] = ["最新算法"]
                recommendations.append(alg_dict)
            return recommendations

        # 如果用户已经学习了一些算法，推荐不同难度或类别的算法
        learned_algorithms = (Algorithm.query
                              .filter(Algorithm.id.in_(learned_algorithm_ids))
                              .all())
        learned_difficulties = {alg.difficulty for alg in learned_algorithms}

        # 优先推荐用户未尝试的难度级别
        preferred_difficulties = []
        if "beginner" not in learned_difficulties:
            preferred_difficulties.append("beginner")
        if "intermediate" not in learned_difficulties:
            preferred_difficulties.append("intermediate")
        if "advanced" not in learned_difficulties:
            preferred_difficulties.append("advanced")

        recommendations = []

        # 推荐不同难度的算法
        if preferred_difficulties:
            for difficulty in preferred_difficulties:
                alg = Algorithm.query.filter(
                    Algorithm.difficulty == difficulty,
                    ~Algorithm.id.in_(learned_algorithm_ids)
                ).first()
                if alg:
                    alg_dict = alg.to_dict()
                    alg_dict["final_score"] = 70.0
                    alg_dict["recommendation_reasons"] = [
                        f"适合{alg_dict.get('difficulty', '新手')}学习者"
                    ]
                    recommendations.append(alg_dict)
                    if len(recommendations) >= 4:
                        break

        # 如果还没够8个，补充其他未学习的算法
        if len(recommendations) < 8:
            remaining_algorithms = Algorithm.query.filter(
                ~Algorithm.id.in_(learned_algorithm_ids)
            ).limit(8 - len(recommendations)).all()

            for alg in remaining_algorithms:
                alg_dict = alg.to_dict()
                alg_dict["final_score"] = 50.0
                alg_dict["recommendation_reasons"] = ["探索新算法"]
                recommendations.append(alg_dict)

        # 如果还是没有推荐（用户学习了所有算法），返回所有算法中用户进步最慢的
        if not recommendations:
            slowest_progress = UserKnowledge.query.filter_by(
                user_id=current_user_id
            ).order_by(UserKnowledge.progress.asc()).first()

            if slowest_progress:
                alg = Algorithm.query.get(slowest_progress.algorithm_id)
                if alg:
                    alg_dict = alg.to_dict()
                    alg_dict["final_score"] = 80.0
                    alg_dict["recommendation_reasons"] = ["建议复习巩固"]
                    recommendations.append(alg_dict)

        return recommendations[:8]

    except Exception as e:
        logging.error(f"Improved fallback algorithm recommendation failed: {e}")
        # 最后的回退：返回任意算法
        try:
            algorithms = Algorithm.query.limit(8).all()
            return [
                {
                    **alg.to_dict(),
                    "final_score": 40.0,
                    "recommendation_reasons": ["系统推荐"]
                }
                for alg in algorithms
            ]
        except Exception:
            return []


def get_fallback_post_recommendations(current_user_id, current_time):
    """传统帖子推荐的回退方案"""
    try:
        posts = (
            Post.query.filter(Post.author_id != current_user_id)
            .order_by(Post.like_count.desc(), Post.created_at.desc())
            .limit(6)
            .all()
        )

        recommendations = []
        for post in posts:
            post_dict = post.to_dict()
            post_dict["final_score"] = 50.0
            post_dict["recommendation_reasons"] = ["热门内容"]
            recommendations.append(post_dict)

        return recommendations
    except Exception:
        return []


def calculate_time_weight(past_time, current_time):
    """计算时间权重（越近的活动权重越高）"""
    if not past_time:
        return 0.1  # 默认低权重

    days_diff = (current_time - past_time).days
    if days_diff <= 0:
        return 1.0  # 今天
    elif days_diff <= 7:
        return 0.8  # 一周内
    elif days_diff <= 30:
        return 0.6  # 一个月内
    elif days_diff <= 90:
        return 0.4  # 三个月内
    else:
        return 0.2  # 更早


def get_difficulty_score(difficulty):
    """根据难度返回基础分数"""
    scores = {"beginner": 0.8, "intermediate": 1.0, "advanced": 0.6}
    return scores.get(difficulty, 0.5)


# 帖子相关API
@api_bp.route("/posts", methods=["GET"])
def get_posts():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        filter_param = request.args.get("filter", "all")  # 新增filter参数处理
        search = request.args.get("search")
        algorithm_id = request.args.get("algorithm_id", type=int)
        tag = request.args.get("tag")  # 新增标签筛选
        sort_by = request.args.get("sort_by", "created_at")  # 新增排序字段
        sort_order = request.args.get("sort_order", "desc")  # 新增排序顺序

        query = Post.query

        # 处理filter参数
        if filter_param == "featured":
            query = query.filter_by(is_featured=True)
        elif filter_param == "recent":
            # 最近的帖子（最近7天）
            from datetime import datetime, timedelta

            week_ago = datetime.utcnow() - timedelta(days=7)
            query = query.filter(Post.created_at >= week_ago)
        elif filter_param == "popular":
            # 热门帖子（点赞数+评论数 >= 5）
            query = query.filter((Post.like_count + Post.comment_count) >= 5)

        if search:
            query = query.filter(
                db.or_(
                    Post.title.ilike(f"%{search}%"), Post.content.ilike(f"%{search}%")
                )
            )

        if algorithm_id:
            # 通过AlgorithmPost关联表过滤与指定算法相关的帖子
            query = query.join(AlgorithmPost).filter(
                AlgorithmPost.algorithm_id == algorithm_id
            )

        author_id = request.args.get("author_id", type=int)
        if author_id:
            query = query.filter_by(author_id=author_id)

        if tag:
            # 筛选包含指定标签的帖子
            # 对于SQLite，tags存储为Unicode转义的JSON字符串
            import json

            # 将标签转换为JSON字符串中的Unicode转义形式进行匹配
            json_tag = json.dumps(tag, ensure_ascii=True).strip('"')
            query = query.filter(Post.tags.like(f"%{json_tag}%"))

        # 排序逻辑
        if sort_by == "created_at":
            order_column = Post.created_at
        elif sort_by == "view_count":
            order_column = Post.view_count
        elif sort_by == "like_count":
            order_column = Post.like_count
        elif sort_by == "comment_count":
            order_column = Post.comment_count
        else:
            order_column = Post.created_at

        if sort_order == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())

        posts = query.paginate(page=page, per_page=per_page, error_out=False)

        return (
            jsonify(
                {
                    "posts": [post.to_dict() for post in posts.items],
                    "total": posts.total,
                    "pages": posts.pages,
                    "current_page": posts.page,
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Get posts error: {e}")
        return jsonify({"message": "Failed to get posts"}), 500


@api_bp.route("/posts/tags", methods=["GET"])
def get_post_tags():
    """获取所有帖子标签"""
    try:
        # 从数据库中收集所有唯一的标签
        posts = Post.query.all()
        all_tags = set()

        for post in posts:
            if post.tags:
                all_tags.update(post.tags)

        # 也可以从算法标签中获取一些常用标签
        algorithms = Algorithm.query.all()
        for alg in algorithms:
            if alg.tags:
                all_tags.update(alg.tags)

        return jsonify({"tags": sorted(list(all_tags))}), 200

    except Exception as e:
        logging.error(f"Get post tags error: {e}")
        return jsonify({"message": "Failed to get post tags"}), 500


@api_bp.route("/posts", methods=["POST"])
# @token_required
def create_post(current_user_id=None):
    try:
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        algorithm_ids = data.get("algorithm_ids", [])
        tags = data.get("tags", [])

        if not all([title, content]):
            return jsonify({"message": "Title and content are required"}), 400

        # 暂时使用admin用户ID进行测试
        if current_user_id is None:
            admin_user = User.query.filter_by(username="admin").first()
            if admin_user:
                current_user_id = admin_user.id
            else:
                return jsonify({"message": "No admin user found"}), 500

        post = Post(title=title, content=content, author_id=current_user_id, tags=tags)
        db.session.add(post)
        db.session.flush()  # 获取post.id

        # 关联算法
        for alg_id in algorithm_ids:
            alg_post = AlgorithmPost(algorithm_id=alg_id, post_id=post.id)
            db.session.add(alg_post)

        db.session.commit()

        # 异步向量化新帖子（不阻塞API响应）
        try:
            from services.vector_service import vector_service
            import threading

            def vectorize_new_post(post_id, post_data):
                try:
                    vector_service.initialize()
                    vector_service.add_post(post_id, post_data)
                    logging.info(f"Vectorized new post: {post_id}")
                except Exception as e:
                    logging.error(f"Failed to vectorize post {post_id}: {e}")

            # 在后台线程中进行向量化
            post_data = post.to_dict()
            threading.Thread(
                target=vectorize_new_post, args=(post.id, post_data), daemon=True
            ).start()

        except Exception as e:
            logging.warning(f"Failed to start post vectorization: {e}")
            # 不影响主要功能

        log_action(current_user_id, "create_post", "post", post.id)

        return (
            jsonify({"message": "Post created successfully", "post": post.to_dict()}),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Create post error: {e}")
        return jsonify({"message": "Failed to create post"}), 500


@api_bp.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)

        # 增加浏览量
        post.view_count += 1
        db.session.commit()

        return jsonify({"post": post.to_dict()}), 200

    except Exception as e:
        logging.error(f"Get post error: {e}")
        return jsonify({"message": "Post not found"}), 404


@api_bp.route("/posts/<int:post_id>/like", methods=["POST"])
@token_required
def like_post(current_user_id, post_id):
    try:
        post = Post.query.get_or_404(post_id)

        like = Like.query.filter_by(user_id=current_user_id, post_id=post_id).first()

        if like:
            # 取消点赞
            db.session.delete(like)
            post.like_count -= 1
            action = "unlike_post"
        else:
            # 点赞
            like = Like(user_id=current_user_id, post_id=post_id)
            db.session.add(like)
            post.like_count += 1
            action = "like_post"

        db.session.commit()

        log_action(current_user_id, action, "post", post_id)

        return jsonify({"message": f"Post {action}d successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Like post error: {e}")
        return jsonify({"message": "Failed to like post"}), 500


# 管理员API
@api_bp.route("/admin/posts/<int:post_id>", methods=["DELETE"])
@token_required
def delete_post(current_user_id, post_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()

        log_action(current_user_id, "delete_post", "post", post_id)

        return jsonify({"message": "Post deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete post error: {e}")
        return jsonify({"message": "Failed to delete post"}), 500


@api_bp.route("/admin/logs", methods=["GET"])
@token_required
def get_system_logs(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)

        logs = SystemLog.query.order_by(SystemLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return (
            jsonify(
                {
                    "logs": [log.to_dict() for log in logs.items],
                    "total": logs.total,
                    "pages": logs.pages,
                    "current_page": logs.page,
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Get logs error: {e}")
        return jsonify({"message": "Failed to get logs"}), 500


# 收藏相关API
@api_bp.route("/favorites", methods=["GET"])
@token_required
def get_user_favorites(current_user_id):
    try:
        favorites = Favorite.query.filter_by(user_id=current_user_id).all()
        favorite_posts = []
        for favorite in favorites:
            post_dict = favorite.post.to_dict()
            post_dict["favorited_at"] = favorite.created_at.isoformat()
            favorite_posts.append(post_dict)

        return jsonify({"favorites": favorite_posts}), 200

    except Exception as e:
        logging.error(f"Get favorites error: {e}")
        return jsonify({"message": "Failed to get favorites"}), 500


@api_bp.route("/posts/<int:post_id>", methods=["DELETE"])
@token_required
def delete_own_post(current_user_id, post_id):
    """用户删除自己的帖子"""
    try:
        post = Post.query.get_or_404(post_id)

        # 检查是否是帖子的作者
        if post.author_id != current_user_id:
            return jsonify({"message": "You can only delete your own posts"}), 403

        # 删除相关的点赞、收藏、评论等
        Like.query.filter_by(post_id=post_id).delete()
        Favorite.query.filter_by(post_id=post_id).delete()
        Comment.query.filter_by(post_id=post_id).delete()
        AlgorithmPost.query.filter_by(post_id=post_id).delete()

        # 删除帖子
        db.session.delete(post)
        db.session.commit()

        log_action(current_user_id, "delete_post", "post", post_id)

        return jsonify({"message": "Post deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete own post error: {e}")
        return jsonify({"message": "Failed to delete post"}), 500


@api_bp.route("/posts/<int:post_id>/favorite", methods=["POST"])
@token_required
def favorite_post(current_user_id, post_id):
    try:
        # Ensure post exists
        Post.query.get_or_404(post_id)

        favorite = Favorite.query.filter_by(
            user_id=current_user_id, post_id=post_id
        ).first()

        if favorite:
            # 取消收藏
            db.session.delete(favorite)
            action = "unfavorite_post"
        else:
            # 收藏
            favorite = Favorite(user_id=current_user_id, post_id=post_id)
            db.session.add(favorite)
            action = "favorite_post"

        db.session.commit()

        log_action(current_user_id, action, "post", post_id)

        return jsonify({"message": f"Post {action}d successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Favorite post error: {e}")
        return jsonify({"message": "Failed to favorite post"}), 500


# 评论相关API
@api_bp.route("/posts/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    try:
        comments = (
            Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at).all()
        )

        # 构建评论树结构
        def build_comment_tree(comments_list, parent_id=None):
            result = []
            for comment in comments_list:
                if comment.parent_id == parent_id:
                    comment_dict = comment.to_dict()
                    comment_dict["replies"] = build_comment_tree(
                        comments_list, comment.id
                    )
                    result.append(comment_dict)
            return result

        comment_tree = build_comment_tree(comments)
        return jsonify({"comments": comment_tree}), 200

    except Exception as e:
        logging.error(f"Get comments error: {e}")
        return jsonify({"message": "Failed to get comments"}), 500


@api_bp.route("/posts/<int:post_id>/comments", methods=["POST"])
@token_required
def create_comment(current_user_id, post_id):
    try:
        data = request.get_json()
        content = data.get("content")
        parent_id = data.get("parent_id")

        if not content:
            return jsonify({"message": "Content is required"}), 400

        comment = Comment(
            content=content,
            post_id=post_id,
            author_id=current_user_id,
            parent_id=parent_id,
        )
        db.session.add(comment)
        db.session.commit()

        # 更新帖子评论数
        post = Post.query.get(post_id)
        post.comment_count += 1
        db.session.commit()

        log_action(current_user_id, "create_comment", "post", post_id)

        return (
            jsonify(
                {
                    "message": "Comment created successfully",
                    "comment": comment.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Create comment error: {e}")
        return jsonify({"message": "Failed to create comment"}), 500


@api_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@token_required
def delete_comment(current_user_id, comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)
        user = User.query.get(current_user_id)

        # 检查权限：只能删除自己的评论或管理员可以删除任何评论
        if comment.author_id != current_user_id and user.role != "admin":
            return jsonify({"message": "Permission denied"}), 403

        # 获取所有子评论
        def get_all_replies(comment_id):
            replies = Comment.query.filter_by(parent_id=comment_id).all()
            all_replies = []
            for reply in replies:
                all_replies.append(reply)
                all_replies.extend(get_all_replies(reply.id))
            return all_replies

        all_comments_to_delete = [comment] + get_all_replies(comment_id)

        # 删除所有相关评论
        for c in all_comments_to_delete:
            db.session.delete(c)

        # 更新帖子评论数
        post = Post.query.get(comment.post_id)
        post.comment_count -= len(all_comments_to_delete)
        db.session.commit()

        log_action(current_user_id, "delete_comment", "comment", comment_id)

        return jsonify({"message": "Comment deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete comment error: {e}")
        return jsonify({"message": "Failed to delete comment"}), 500


# 用户点赞相关API
@api_bp.route("/user/likes", methods=["GET"])
@token_required
def get_user_likes(current_user_id):
    try:
        likes = Like.query.filter_by(user_id=current_user_id).all()
        return jsonify({"likes": [like.to_dict() for like in likes]}), 200

    except Exception as e:
        logging.error(f"Get user likes error: {e}")
        return jsonify({"message": "Failed to get likes"}), 500


# 管理员专用API
@api_bp.route("/admin/stats", methods=["GET"])
@token_required
def get_admin_stats(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        stats = {
            "totalUsers": User.query.count(),
            "totalPosts": Post.query.count(),
            "totalComments": Comment.query.count(),
            "totalAlgorithms": Algorithm.query.count(),
        }

        return jsonify(stats), 200

    except Exception as e:
        logging.error(f"Get admin stats error: {e}")
        return jsonify({"message": "Failed to get stats"}), 500


# 数据分析API
@api_bp.route("/admin/analytics/user-activity", methods=["GET"])
@token_required
def get_user_activity_rankings(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        # 计算用户活跃度得分
        users_data = []
        users = User.query.all()

        for user in users:
            posts_count = Post.query.filter_by(author_id=user.id).count()
            comments_count = Comment.query.filter_by(author_id=user.id).count()

            # 计算获赞数（用户所有帖子的点赞总数）
            likes_received = (
                db.session.query(db.func.coalesce(db.func.sum(Post.like_count), 0))
                .filter_by(author_id=user.id)
                .scalar()
            )

            # 活跃度得分 = 帖子数 * 3 + 评论数 * 1 + 获赞数 * 0.5
            activity_score = (
                posts_count * 3 + comments_count * 1 + float(likes_received) * 0.5
            )

            users_data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "posts_count": posts_count,
                    "comments_count": comments_count,
                    "likes_received": likes_received,
                    "activity_score": round(activity_score, 2),
                }
            )

        # 按活跃度得分降序排序
        rankings = sorted(users_data, key=lambda x: x["activity_score"], reverse=True)[
            :20
        ]

        return jsonify({"rankings": rankings}), 200

    except Exception as e:
        logging.error(f"Get user activity rankings error: {e}")
        return jsonify({"message": "Failed to get rankings"}), 500


@api_bp.route("/admin/analytics/post-popularity", methods=["GET"])
@token_required
def get_post_popularity_rankings(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        # 计算帖子热度得分
        posts_data = []
        posts = Post.query.all()

        for post in posts:
            # 热度得分 = 浏览量 * 0.1 + 点赞数 * 2 + 评论数 * 3 + (精华帖加成)
            popularity_score = (
                post.view_count * 0.1
                + post.like_count * 2
                + post.comment_count * 3
                + (10 if post.is_featured else 0)
            )

            posts_data.append(
                {
                    "id": post.id,
                    "title": (
                        post.title[:50] + "..." if len(post.title) > 50 else post.title
                    ),
                    "author": post.author.to_dict() if post.author else None,
                    "view_count": post.view_count,
                    "like_count": post.like_count,
                    "comment_count": post.comment_count,
                    "popularity_score": round(popularity_score, 2),
                    "is_featured": post.is_featured,
                }
            )

        # 按热度得分降序排序
        rankings = sorted(
            posts_data, key=lambda x: x["popularity_score"], reverse=True
        )[:20]

        return jsonify({"rankings": rankings}), 200

    except Exception as e:
        logging.error(f"Get post popularity rankings error: {e}")
        return jsonify({"message": "Failed to get rankings"}), 500


@api_bp.route("/admin/analytics/system-stats", methods=["GET"])
@token_required
def get_system_stats(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        # 计算系统统计信息
        from datetime import datetime, timedelta

        # 用户增长率（最近30天）
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()
        total_users = User.query.count()
        growth_rate = (
            round((new_users_30d / total_users) * 100, 2) if total_users > 0 else 0
        )

        # 平均页面浏览量
        total_views = db.session.query(
            db.func.coalesce(db.func.sum(Post.view_count), 0)
        ).scalar()
        total_posts = Post.query.count()
        avg_page_views = round(total_views / total_posts, 1) if total_posts > 0 else 0

        # 平均会话时长（基于日志数据估算） - 暂时使用默认估算值
        avg_session_time = "25分钟"  # 默认值

        stats = {
            "avgSessionTime": avg_session_time,
            "avgPageViews": f"{avg_page_views}页",
            "growthRate": growth_rate,
        }

        return jsonify({"stats": stats}), 200

    except Exception as e:
        logging.error(f"Get system stats error: {e}")
        return jsonify({"message": "Failed to get stats"}), 500


# 数据库管理API
@api_bp.route("/admin/database/cleanup-users", methods=["POST"])
@token_required
def cleanup_inactive_users(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        from datetime import datetime, timedelta

        # 定义非活跃用户：90天内没有登录且没有发帖
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)

        inactive_users = User.query.filter(
            User.created_at < ninety_days_ago,
            ~User.posts.any(),  # 没有发过帖子
            ~User.comments.any(),  # 没有发过评论
        ).all()

        deleted_count = 0
        for inactive_user in inactive_users:
            # 记录删除操作
            log_action(
                current_user_id,
                "cleanup_inactive_user",
                "user",
                inactive_user.id,
                {"username": inactive_user.username, "reason": "inactive_user"},
            )
            db.session.delete(inactive_user)
            deleted_count += 1

        db.session.commit()

        return (
            jsonify(
                {
                    "message": (
                        f"Successfully cleaned up {deleted_count} inactive users"
                    ),
                    "deleted_count": deleted_count,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Cleanup inactive users error: {e}")
        return jsonify({"message": "Failed to cleanup users"}), 500


@api_bp.route("/admin/database/export-users", methods=["GET"])
@token_required
def export_users_data(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        users = User.query.all()
        export_data = []

        for user in users:
            user_data = user.to_dict()
            # 添加额外统计信息
            user_data["stats"] = {
                "posts_count": Post.query.filter_by(author_id=user.id).count(),
                "comments_count": Comment.query.filter_by(author_id=user.id).count(),
                "likes_received": db.session.query(db.func.sum(Post.like_count))
                .filter_by(author_id=user.id)
                .scalar()
                or 0,
                "favorites_count": Favorite.query.filter_by(user_id=user.id).count(),
            }
            export_data.append(user_data)

        import json

        json_data = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)

        from flask import Response

        return Response(
            json_data,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment;filename=users_export.json"},
        )

    except Exception as e:
        logging.error(f"Export users data error: {e}")
        return jsonify({"message": "Failed to export data"}), 500


@api_bp.route("/admin/database/cleanup-posts", methods=["POST"])
@token_required
def cleanup_old_posts(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        from datetime import datetime, timedelta

        # 清理1年前的帖子（且浏览量少于5，点赞少于2）
        one_year_ago = datetime.utcnow() - timedelta(days=365)

        old_posts = Post.query.filter(
            Post.created_at < one_year_ago,
            Post.view_count < 5,
            Post.like_count < 2,
            Post.comment_count == 0,
        ).all()

        deleted_count = 0
        for post in old_posts:
            log_action(
                current_user_id,
                "cleanup_old_post",
                "post",
                post.id,
                {"title": post.title, "reason": "old_inactive_post"},
            )
            db.session.delete(post)
            deleted_count += 1

        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Successfully cleaned up {deleted_count} old posts",
                    "deleted_count": deleted_count,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Cleanup old posts error: {e}")
        return jsonify({"message": "Failed to cleanup posts"}), 500


@api_bp.route("/admin/database/export-content", methods=["GET"])
@token_required
def export_content_data(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        posts = Post.query.all()
        export_data = {
            "posts": [post.to_dict() for post in posts],
            "comments": [comment.to_dict() for comment in Comment.query.all()],
            "export_time": datetime.utcnow().isoformat(),
        }

        import json

        json_data = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)

        from flask import Response

        return Response(
            json_data,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment;filename=content_export.json"},
        )

    except Exception as e:
        logging.error(f"Export content data error: {e}")
        return jsonify({"message": "Failed to export data"}), 500


@api_bp.route("/admin/database/backup", methods=["POST"])
@token_required
def backup_database(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        # 这里可以实现数据库备份逻辑
        # 由于是SQLite/MySQL，我们可以创建数据库文件的副本
        import shutil
        from datetime import datetime

        backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"database_backup_{backup_time}.db"

        # 假设数据库文件在instance目录下
        db_path = "instance/ml_learner.db"
        backup_path = f"backups/{backup_filename}"

        if os.path.exists(db_path):
            os.makedirs("backups", exist_ok=True)
            shutil.copy2(db_path, backup_path)

            log_action(
                current_user_id,
                "database_backup",
                "system",
                None,
                {"backup_file": backup_filename},
            )

            return (
                jsonify(
                    {
                        "message": "Database backup created successfully",
                        "backup_file": backup_filename,
                    }
                ),
                200,
            )
        else:
            return jsonify({"message": "Database file not found"}), 404

    except Exception as e:
        logging.error(f"Database backup error: {e}")
        return jsonify({"message": "Failed to backup database"}), 500


@api_bp.route("/admin/database/optimize", methods=["POST"])
@token_required
def optimize_database(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        # 对于SQLite，VACUUM可以优化数据库
        if "sqlite" in str(db.engine.url):
            db.engine.execute("VACUUM")
            log_action(current_user_id, "database_optimize", "system", None)
            return jsonify({"message": "Database optimized successfully"}), 200
        else:
            # 对于MySQL，可以运行一些优化查询
            log_action(current_user_id, "database_optimize", "system", None)
            return jsonify({"message": "Database optimization completed"}), 200

    except Exception as e:
        logging.error(f"Database optimize error: {e}")
        return jsonify({"message": "Failed to optimize database"}), 500


@api_bp.route("/admin/posts", methods=["GET"])
@token_required
def get_admin_posts(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search")

        query = Post.query

        if search:
            query = query.filter(
                db.or_(
                    Post.title.ilike(f"%{search}%"), Post.content.ilike(f"%{search}%")
                )
            )

        posts = query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return (
            jsonify(
                {
                    "posts": [post.to_dict() for post in posts.items],
                    "total": posts.total,
                    "pages": posts.pages,
                    "current_page": posts.page,
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Get admin posts error: {e}")
        return jsonify({"message": "Failed to get posts"}), 500


@api_bp.route("/admin/users", methods=["GET"])
@token_required
def get_admin_users(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search")

        query = User.query

        if search:
            query = query.filter(
                db.or_(
                    User.username.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")
                )
            )

        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return (
            jsonify(
                {
                    "users": [u.to_dict() for u in users.items],
                    "total": users.total,
                    "pages": users.pages,
                    "current_page": users.page,
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Get admin users error: {e}")
        return jsonify({"message": "Failed to get users"}), 500


@api_bp.route("/admin/posts/<int:post_id>/featured", methods=["PUT"])
@token_required
def toggle_post_featured(current_user_id, post_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        data = request.get_json()
        featured = data.get("featured", False)

        post = Post.query.get_or_404(post_id)
        post.is_featured = featured
        db.session.commit()

        log_action(
            current_user_id, "toggle_featured", "post", post_id, {"featured": featured}
        )

        return jsonify({"message": "Post featured status updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Toggle featured error: {e}")
        return jsonify({"message": "Failed to update featured status"}), 500


@api_bp.route("/admin/users/<int:user_id>/role", methods=["PUT"])
@token_required
def change_user_role(current_user_id, user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        data = request.get_json()
        new_role = data.get("role")

        if new_role not in ["user", "admin"]:
            return jsonify({"message": "Invalid role"}), 400

        target_user = User.query.get_or_404(user_id)
        target_user.role = new_role
        db.session.commit()

        log_action(
            current_user_id, "change_role", "user", user_id, {"new_role": new_role}
        )

        return jsonify({"message": "User role updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Change user role error: {e}")
        return jsonify({"message": "Failed to update user role"}), 500


@api_bp.route("/admin/users/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user_admin(current_user_id, user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        target_user = User.query.get_or_404(user_id)

        # 防止删除自己
        if target_user.id == current_user_id:
            return jsonify({"message": "Cannot delete yourself"}), 400

        db.session.delete(target_user)
        db.session.commit()

        log_action(current_user_id, "delete_user", "user", user_id)

        return jsonify({"message": "User deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete user error: {e}")
        return jsonify({"message": "Failed to delete user"}), 500


@api_bp.route("/user/summary", methods=["GET"])
@token_required
def get_user_summary(current_user_id):
    """
    Return user's favorites, liked posts, commented posts, and recent replies
    to user's comments.
    """
    try:
        # Favorites: posts favorited by user
        favorites = Favorite.query.filter_by(user_id=current_user_id).all()
        favorite_posts = [fav.post.to_dict() for fav in favorites]

        # Likes: posts liked by user
        likes = Like.query.filter_by(user_id=current_user_id).all()
        liked_post_ids = [like.post_id for like in likes]
        liked_posts = []
        if liked_post_ids:
            liked_posts = Post.query.filter(Post.id.in_(liked_post_ids)).all()
            liked_posts = [p.to_dict() for p in liked_posts]

        # Comments: posts where user has commented
        user_comments = Comment.query.filter_by(author_id=current_user_id).all()
        commented_post_ids = list(set([c.post_id for c in user_comments]))
        commented_posts = []
        if commented_post_ids:
            commented_posts = Post.query.filter(Post.id.in_(commented_post_ids)).all()
            commented_posts = [p.to_dict() for p in commented_posts]

        # Replies: comments that are replies to this user's comments
        user_comment_ids = [c.id for c in user_comments]
        replies = []
        if user_comment_ids:
            replies_q = (
                Comment.query.filter(Comment.parent_id.in_(user_comment_ids))
                .order_by(Comment.created_at.desc())
                .limit(50)
                .all()
            )
            replies = [r.to_dict() for r in replies_q]

        return (
            jsonify(
                {
                    "favorites": favorite_posts,
                    "likes": liked_posts,
                    "comments": commented_posts,
                    "replies": replies,
                }
            ),
            200,
        )
    except Exception as e:
        logging.error(f"Get user summary error: {e}")
        return jsonify({"message": "Failed to get user summary"}), 500


@api_bp.route("/admin/fetch_avatars", methods=["POST"])
@token_required
def admin_fetch_avatars(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if not user or user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        body = request.get_json() or {}
        items = body.get("items") or []
        if not isinstance(items, list) or not items:
            return (
                jsonify(
                    {"message": 'Provide items list [{"user_id":..., "url":...}, ...]'}
                ),
                400,
            )

        results = []
        for it in items:
            uid = it.get("user_id")
            url = it.get("url")
            if not uid or not url:
                results.append({"user_id": uid, "status": "missing_fields"})
                continue
            target = User.query.get(uid)
            if not target:
                results.append({"user_id": uid, "status": "user_not_found"})
                continue
            try:
                r = requests.get(url, timeout=15)
                if r.status_code != 200:
                    results.append({"user_id": uid, "status": f"http_{r.status_code}"})
                    continue
                content = r.content
                if len(content) > 2 * 1024 * 1024:
                    results.append({"user_id": uid, "status": "too_large"})
                    continue
                kind = None
                if imghdr:
                    try:
                        kind = imghdr.what(None, h=content)
                    except Exception:
                        kind = None
                if not kind:
                    try:
                        img = Image.open(BytesIO(content))
                        kind = (img.format or "").lower()
                    except Exception:
                        results.append({"user_id": uid, "status": "invalid_image"})
                        continue
                ext = kind or "png"
                data_url = f"data:image/{ext};base64," + base64.b64encode(
                    content
                ).decode("utf-8")
                target.avatar = data_url
                db.session.commit()
                results.append({"user_id": uid, "status": "ok"})
            except Exception as e:
                logging.error(f"fetch avatar failed for {uid} {url}: {e}")
                results.append({"user_id": uid, "status": "error", "error": str(e)})

        return jsonify({"results": results}), 200
    except Exception as e:
        logging.error(f"admin_fetch_avatars error: {e}")
        return jsonify({"message": "Failed to fetch avatars"}), 500


# 管理员专用算法管理API
@api_bp.route("/admin/algorithms", methods=["POST"])
@token_required
def create_algorithm(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        data = request.get_json()
        name = data.get("name")
        chinese_name = data.get("chinese_name")
        description = data.get("description")
        category_id = data.get("category_id")
        difficulty = data.get("difficulty", "intermediate")
        tags = data.get("tags", [])
        paper_url = data.get("paper_url")
        code_url = data.get("code_url")
        visualization_data = data.get("visualization_data", {})

        if not all([name, description, category_id]):
            return (
                jsonify({"message": "Name, description and category_id are required"}),
                400,
            )

        # 检查算法名称是否已存在
        existing = Algorithm.query.filter_by(name=name).first()
        if existing:
            return jsonify({"message": "Algorithm with this name already exists"}), 400

        algorithm = Algorithm(
            name=name,
            chinese_name=chinese_name,
            description=description,
            category_id=category_id,
            difficulty=difficulty,
            tags=tags,
            paper_url=paper_url,
            code_url=code_url,
            visualization_data=visualization_data,
        )

        db.session.add(algorithm)
        db.session.commit()

        # 异步向量化新算法（不阻塞API响应）
        try:
            from services.vector_service import vector_service
            import threading

            def vectorize_new_algorithm(alg_id, alg_data):
                try:
                    vector_service.initialize()
                    vector_service.add_algorithm(alg_id, alg_data)
                    logging.info(f"Vectorized new algorithm: {alg_id}")
                except Exception as e:
                    logging.error(f"Failed to vectorize algorithm {alg_id}: {e}")

            # 在后台线程中进行向量化
            alg_data = algorithm.to_dict()
            threading.Thread(
                target=vectorize_new_algorithm,
                args=(algorithm.id, alg_data),
                daemon=True,
            ).start()

        except Exception as e:
            logging.warning(f"Failed to start algorithm vectorization: {e}")
            # 不影响主要功能

        log_action(
            current_user_id,
            "create_algorithm",
            "algorithm",
            algorithm.id,
            {"name": name, "category_id": category_id},
        )

        return (
            jsonify(
                {
                    "message": "Algorithm created successfully",
                    "algorithm": algorithm.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Create algorithm error: {e}")
        return jsonify({"message": "Failed to create algorithm"}), 500


@api_bp.route("/admin/algorithms/<int:algorithm_id>", methods=["PUT"])
@token_required
def update_algorithm(current_user_id, algorithm_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        algorithm = Algorithm.query.get_or_404(algorithm_id)
        data = request.get_json()

        # 检查新名称是否与其他算法重复
        new_name = data.get("name")
        if new_name and new_name != algorithm.name:
            existing = Algorithm.query.filter_by(name=new_name).first()
            if existing:
                return (
                    jsonify({"message": "Algorithm with this name already exists"}),
                    400,
                )

        # 更新字段
        for field in [
            "name",
            "chinese_name",
            "description",
            "category_id",
            "difficulty",
            "tags",
            "paper_url",
            "code_url",
            "visualization_data",
        ]:
            if field in data:
                setattr(algorithm, field, data[field])

        db.session.commit()

        log_action(current_user_id, "update_algorithm", "algorithm", algorithm_id, data)

        return (
            jsonify(
                {
                    "message": "Algorithm updated successfully",
                    "algorithm": algorithm.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Update algorithm error: {e}")
        return jsonify({"message": "Failed to update algorithm"}), 500


@api_bp.route("/admin/algorithms/<int:algorithm_id>", methods=["DELETE"])
@token_required
def delete_algorithm(current_user_id, algorithm_id):
    try:
        user = User.query.get(current_user_id)
        if user.role != "admin":
            return jsonify({"message": "Admin access required"}), 403

        algorithm = Algorithm.query.get_or_404(algorithm_id)

        # 删除相关的用户知识记录
        UserKnowledge.query.filter_by(algorithm_id=algorithm_id).delete()

        # 删除相关的帖子关联
        AlgorithmPost.query.filter_by(algorithm_id=algorithm_id).delete()

        # 删除算法
        db.session.delete(algorithm)
        db.session.commit()

        log_action(
            current_user_id,
            "delete_algorithm",
            "algorithm",
            algorithm_id,
            {"name": algorithm.name},
        )

        return jsonify({"message": "Algorithm deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete algorithm error: {e}")
        return jsonify({"message": "Failed to delete algorithm"}), 500


# 好友相关API
@api_bp.route("/friends/search", methods=["GET"])
@token_required
def search_users(current_user_id):
    """搜索用户（用于添加好友）"""
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"users": []}), 200

        # 搜索用户名或邮箱（排除自己和已经是好友的用户）
        users = (
            User.query.filter(
                db.and_(
                    db.or_(
                        User.username.ilike(f"%{query}%"),
                        User.email.ilike(f"%{query}%"),
                    ),
                    User.id != current_user_id,
                )
            )
            .limit(10)
            .all()
        )

        # 检查每个用户是否已经是好友
        result = []
        for user in users:
            # 检查是否存在好友关系（无论谁发起的）
            existing_friend = Friend.query.filter(
                db.or_(
                    db.and_(
                        Friend.user_id == current_user_id, Friend.friend_id == user.id
                    ),
                    db.and_(
                        Friend.user_id == user.id, Friend.friend_id == current_user_id
                    ),
                )
            ).first()

            user_dict = user.to_dict()
            if existing_friend:
                user_dict["friend_status"] = existing_friend.status
                if existing_friend.user_id == current_user_id:
                    user_dict["is_sender"] = True
                else:
                    user_dict["is_sender"] = False
            else:
                user_dict["friend_status"] = None
                user_dict["is_sender"] = False

            result.append(user_dict)

        return jsonify({"users": result}), 200

    except Exception as e:
        logging.error(f"Search users error: {e}")
        return jsonify({"message": "Failed to search users"}), 500


@api_bp.route("/friends/request", methods=["POST"])
@token_required
def send_friend_request(current_user_id):
    """发送好友请求"""
    try:
        data = request.get_json()
        friend_id = data.get("friend_id")

        if not friend_id:
            return jsonify({"message": "Friend ID is required"}), 400

        if friend_id == current_user_id:
            return jsonify({"message": "Cannot add yourself as friend"}), 400

        # 检查是否已经是好友
        existing_friend = Friend.query.filter(
            db.or_(
                db.and_(
                    Friend.user_id == current_user_id, Friend.friend_id == friend_id
                ),
                db.and_(
                    Friend.user_id == friend_id, Friend.friend_id == current_user_id
                ),
            )
        ).first()

        if existing_friend:
            if existing_friend.status == "accepted":
                return jsonify({"message": "Already friends"}), 400
            elif existing_friend.status == "pending":
                return jsonify({"message": "Friend request already sent"}), 400

        # 创建好友请求
        friend_request = Friend(
            user_id=current_user_id, friend_id=friend_id, status="pending"
        )

        db.session.add(friend_request)
        db.session.commit()

        log_action(current_user_id, "send_friend_request", "user", friend_id)

        return (
            jsonify(
                {
                    "message": "Friend request sent successfully",
                    "friend_request": friend_request.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Send friend request error: {e}")
        return jsonify({"message": "Failed to send friend request"}), 500


@api_bp.route("/friends/requests", methods=["GET"])
@token_required
def get_friend_requests(current_user_id):
    """获取好友请求列表"""
    try:
        # 获取收到的好友请求
        received_requests = Friend.query.filter_by(
            friend_id=current_user_id, status="pending"
        ).all()
        # 获取发出的好友请求
        sent_requests = Friend.query.filter_by(
            user_id=current_user_id, status="pending"
        ).all()

        return (
            jsonify(
                {
                    "received": [req.to_dict() for req in received_requests],
                    "sent": [req.to_dict() for req in sent_requests],
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Get friend requests error: {e}")
        return jsonify({"message": "Failed to get friend requests"}), 500


@api_bp.route("/friends/requests/<int:request_id>", methods=["PUT"])
@token_required
def respond_friend_request(current_user_id, request_id):
    """响应好友请求（接受或拒绝）"""
    try:
        data = request.get_json()
        action = data.get("action")  # 'accept' or 'reject'

        if action not in ["accept", "reject"]:
            return jsonify({"message": "Invalid action"}), 400

        friend_request = Friend.query.get_or_404(request_id)

        # 确保当前用户是接收者
        if friend_request.friend_id != current_user_id:
            return jsonify({"message": "Permission denied"}), 403

        if action == "accept":
            friend_request.status = "accepted"
        else:
            friend_request.status = "rejected"

        db.session.commit()

        log_action(
            current_user_id,
            "respond_friend_request",
            "user",
            friend_request.user_id,
            {"action": action},
        )

        return jsonify({"message": f"Friend request {action}ed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Respond friend request error: {e}")
        return jsonify({"message": "Failed to respond to friend request"}), 500


@api_bp.route("/friends", methods=["GET"])
@token_required
def get_friends(current_user_id):
    """获取好友列表"""
    try:
        # 获取所有已接受的好友关系
        friends1 = Friend.query.filter_by(
            user_id=current_user_id, status="accepted"
        ).all()
        friends2 = Friend.query.filter_by(
            friend_id=current_user_id, status="accepted"
        ).all()

        friend_users = []
        for friend in friends1:
            friend_users.append(friend.friend)
        for friend in friends2:
            friend_users.append(friend.user)

        # 去重
        seen_ids = set()
        unique_friends = []
        for friend in friend_users:
            if friend.id not in seen_ids:
                seen_ids.add(friend.id)
                unique_friends.append(friend.to_dict())

        return jsonify({"friends": unique_friends}), 200

    except Exception as e:
        logging.error(f"Get friends error: {e}")
        return jsonify({"message": "Failed to get friends"}), 500


@api_bp.route("/friends/<int:friend_id>", methods=["DELETE"])
@token_required
def remove_friend(current_user_id, friend_id):
    """删除好友"""
    try:
        # 查找好友关系
        friend_relation = Friend.query.filter(
            db.or_(
                db.and_(
                    Friend.user_id == current_user_id, Friend.friend_id == friend_id
                ),
                db.and_(
                    Friend.user_id == friend_id, Friend.friend_id == current_user_id
                ),
            ),
            Friend.status == "accepted",
        ).first()

        if not friend_relation:
            return jsonify({"message": "Friend relationship not found"}), 404

        db.session.delete(friend_relation)
        db.session.commit()

        log_action(current_user_id, "remove_friend", "user", friend_id)

        return jsonify({"message": "Friend removed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Remove friend error: {e}")
        return jsonify({"message": "Failed to remove friend"}), 500


@api_bp.route("/users/<int:user_id>/profile", methods=["GET"])
def get_user_profile(user_id):
    """获取用户公开资料"""
    try:
        user = User.query.get_or_404(user_id)

        # 获取用户的帖子数量、点赞数等公开信息
        posts_count = Post.query.filter_by(author_id=user_id).count()
        likes_received = (
            db.session.query(db.func.sum(Post.like_count))
            .filter_by(author_id=user_id)
            .scalar()
            or 0
        )
        comments_count = Comment.query.filter_by(author_id=user_id).count()

        # 获取最近的几个帖子
        recent_posts = (
            Post.query.filter_by(author_id=user_id)
            .order_by(Post.created_at.desc())
            .limit(3)
            .all()
        )

        profile_data = user.to_dict()
        profile_data.update(
            {
                "stats": {
                    "posts_count": posts_count,
                    "likes_received": likes_received,
                    "comments_count": comments_count,
                },
                "recent_posts": [post.to_dict() for post in recent_posts],
            }
        )

        return jsonify({"profile": profile_data}), 200

    except Exception as e:
        logging.error(f"Get user profile error: {e}")
        return jsonify({"message": "Failed to get user profile"}), 404


# 聊天相关API
@api_bp.route("/chat/messages", methods=["GET"])
@token_required
def get_chat_messages(current_user_id):
    """获取与指定好友的聊天消息"""
    try:
        friend_id = request.args.get("friend_id", type=int)
        if not friend_id:
            return jsonify({"messages": []}), 200

        # 检查是否是好友关系
        friendship = Friend.query.filter(
            db.or_(
                db.and_(
                    Friend.user_id == current_user_id, Friend.friend_id == friend_id
                ),
                db.and_(
                    Friend.user_id == friend_id, Friend.friend_id == current_user_id
                ),
            ),
            Friend.status == "accepted",
        ).first()

        if not friendship:
            return jsonify({"message": "Not friends with this user"}), 403

        # 获取聊天消息
        messages = (
            ChatMessage.query.filter(
                db.or_(
                    db.and_(
                        ChatMessage.sender_id == current_user_id,
                        ChatMessage.receiver_id == friend_id,
                    ),
                    db.and_(
                        ChatMessage.sender_id == friend_id,
                        ChatMessage.receiver_id == current_user_id,
                    ),
                )
            )
            .order_by(ChatMessage.created_at)
            .all()
        )

        # 标记接收到的消息为已读
        unread_messages = ChatMessage.query.filter_by(
            sender_id=friend_id, receiver_id=current_user_id, is_read=False
        ).all()

        for msg in unread_messages:
            msg.is_read = True

        db.session.commit()

        return jsonify({"messages": [msg.to_dict() for msg in messages]}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Get chat messages error: {e}")
        return jsonify({"message": "Failed to get chat messages"}), 500


@api_bp.route("/chat/messages", methods=["POST"])
@token_required
def send_chat_message(current_user_id):
    """发送聊天消息"""
    try:
        data = request.get_json()
        receiver_id = data.get("receiver_id")
        content = data.get("content", "").strip()
        message_type = data.get("message_type", "text")

        if not receiver_id or not content:
            return jsonify({"message": "Receiver ID and content are required"}), 400

        # 检查是否是好友关系
        friendship = Friend.query.filter(
            db.or_(
                db.and_(
                    Friend.user_id == current_user_id, Friend.friend_id == receiver_id
                ),
                db.and_(
                    Friend.user_id == receiver_id, Friend.friend_id == current_user_id
                ),
            ),
            Friend.status == "accepted",
        ).first()

        if not friendship:
            return jsonify({"message": "Not friends with this user"}), 403

        # 创建消息
        message = ChatMessage(
            sender_id=current_user_id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type,
        )

        db.session.add(message)
        db.session.commit()

        log_action(
            current_user_id,
            "send_message",
            "user",
            receiver_id,
            {"message_type": message_type},
        )

        return (
            jsonify(
                {
                    "message": "Message sent successfully",
                    "chat_message": message.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Send chat message error: {e}")
        return jsonify({"message": "Failed to send message"}), 500


# AI分析相关API
@api_bp.route("/algorithms/<int:algorithm_id>/related-posts", methods=["GET"])
@token_required
def get_algorithm_related_posts(current_user_id, algorithm_id):
    """
    获取与算法相关的帖子 - 基于向量相似度的智能推荐

    推荐策略：
    1. 直接关联的帖子（权重最高）
    2. 基于算法向量相似度的语义相关帖子
    3. 基于用户学习进度的个性化调整
    """
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 5))  # 默认5个，更适合推荐场景

        # 初始化向量服务
        vector_service.initialize()

        algorithm = Algorithm.query.get_or_404(algorithm_id)
        related_posts_data = []

        # 1. 获取直接关联的帖子（最高优先级）
        direct_posts = (
            db.session.query(Post)
            .join(AlgorithmPost)
            .filter(AlgorithmPost.algorithm_id == algorithm_id)
            .all()
        )

        for post in direct_posts:
            post_dict = post.to_dict()
            post_dict["relation_type"] = "direct"  # 直接关联
            post_dict["relevance_score"] = 100  # 最高相关度
            post_dict["recommendation_reason"] = "官方关联内容"
            related_posts_data.append(post_dict)

        # 2. 基于向量相似度推荐相关帖子
        try:
            # 获取算法的向量表示
            algorithm_vector = vector_service.vectorize_algorithm(algorithm.to_dict())

            # 查找语义相似的帖子
            similar_posts = vector_service.find_similar_posts(
                algorithm_vector,
                limit=20,  # 多取一些用于过滤
                author_id=None,  # 不排除作者，可以看到官方内容
                min_similarity=0.4,  # 相似度阈值
            )

            # 获取用户学习数据，用于个性化调整
            user_knowledge = UserKnowledge.query.filter_by(
                user_id=current_user_id, algorithm_id=algorithm_id
            ).first()

            user_progress = user_knowledge.progress if user_knowledge else 0

            for post_data in similar_posts:
                post = Post.query.get(post_data["id"])
                if not post:
                    continue

                # 避免重复（如果已经是直接关联的）
                if any(p["id"] == post.id for p in related_posts_data):
                    continue

                # 计算个性化相关度
                base_similarity = post_data["similarity_score"]

                # 学习进度相关性加成
                progress_bonus = 0
                if (
                    user_progress > 50 and post.like_count > 10
                ):  # 学习有进展的用户推荐高质量内容
                    progress_bonus = 10
                elif user_progress < 30 and post.like_count < 5:  # 新手用户推荐基础内容
                    progress_bonus = 5

                # 社区互动加成
                community_bonus = min((post.like_count + post.comment_count) * 0.5, 15)

                # 时间新鲜度加成
                time_bonus = 0
                if post.created_at:
                    days_old = (datetime.utcnow() - post.created_at).days
                    time_bonus = max(0, 8 - days_old * 0.5)  # 新内容加成递减

                final_score = (
                    (base_similarity * 100)
                    + progress_bonus
                    + community_bonus
                    + time_bonus
                )

                post_dict = post.to_dict()
                post_dict["relation_type"] = "semantic"  # 语义相关
                post_dict["relevance_score"] = round(final_score, 2)
                post_dict["recommendation_reason"] = get_post_recommendation_reason(
                    base_similarity, progress_bonus, community_bonus, time_bonus
                )

                related_posts_data.append(post_dict)

        except Exception as e:
            logging.warning(
                f"Vector-based post recommendation failed for algorithm "
                f"{algorithm_id}: {e}"
            )
            # 回退到传统标签匹配方法
            fallback_posts = get_fallback_related_posts(algorithm)
            for post in fallback_posts:
                if not any(p["id"] == post.id for p in related_posts_data):
                    post_dict = post.to_dict()
                    post_dict["relation_type"] = "fallback"
                    post_dict["relevance_score"] = 50
                    post_dict["recommendation_reason"] = "标签匹配"
                    related_posts_data.append(post_dict)

        # 3. 按相关度排序
        related_posts_data.sort(key=lambda x: x["relevance_score"], reverse=True)

        # 分页
        total_posts = len(related_posts_data)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_posts = related_posts_data[start_idx:end_idx]

        # 格式化返回数据
        formatted_posts = []
        for post_data in paginated_posts:
            formatted_post = {
                "id": post_data["id"],
                "title": post_data["title"],
                "content": (
                    post_data["content"][:200] + "..."
                    if len(post_data["content"]) > 200
                    else post_data["content"]
                ),
                "author": (
                    post_data.get("author", {}).get("username", "Anonymous")
                    if isinstance(post_data.get("author"), dict)
                    else "Anonymous"
                ),
                "created_at": post_data["created_at"],
                "like_count": post_data["like_count"],
                "comment_count": post_data["comment_count"],
                "tags": post_data["tags"] or [],
                "relation_type": post_data["relation_type"],
                "relevance_score": post_data["relevance_score"],
                "recommendation_reason": post_data["recommendation_reason"],
            }
            formatted_posts.append(formatted_post)

        return (
            jsonify(
                {
                    "posts": formatted_posts,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": total_posts,
                        "pages": (total_posts + per_page - 1) // per_page,
                    },
                    "algorithm": {
                        "id": algorithm.id,
                        "name": algorithm.name,
                        "tags": algorithm.tags or [],
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Get algorithm related posts error: {e}")
        return jsonify({"message": "Failed to get related posts"}), 500


def get_post_recommendation_reason(
    base_similarity, progress_bonus, community_bonus, time_bonus
):
    """生成帖子推荐理由"""
    reasons = []

    if base_similarity > 0.7:
        reasons.append("高度相关")
    elif base_similarity > 0.5:
        reasons.append("内容相似")

    if progress_bonus > 5:
        reasons.append("适合学习进度")

    if community_bonus > 8:
        reasons.append("社区热门")

    if time_bonus > 5:
        reasons.append("最新内容")

    return " · ".join(reasons) if reasons else "相关推荐"


def get_fallback_related_posts(algorithm):
    """传统方法回退：基于标签和关键词匹配"""
    related_posts = []

    # 标签匹配
    if algorithm.tags:
        tag_conditions = [Post.tags.contains([tag]) for tag in algorithm.tags]
        if tag_conditions:
            tag_posts = (
                db.session.query(Post).filter(db.or_(*tag_conditions)).limit(10).all()
            )
            related_posts.extend(tag_posts)

    # 关键词匹配
    algorithm_keywords = get_algorithm_keywords(algorithm.name.lower())
    if algorithm_keywords:
        keyword_conditions = []
        for keyword in algorithm_keywords:
            keyword_conditions.extend(
                [Post.title.contains(keyword), Post.content.contains(keyword)]
            )

        if keyword_conditions:
            keyword_posts = (
                db.session.query(Post)
                .filter(db.or_(*keyword_conditions))
                .limit(10)
                .all()
            )
            # 避免重复
            for post in keyword_posts:
                if post not in related_posts:
                    related_posts.append(post)

    return related_posts[:15]  # 限制数量


def get_algorithm_keywords(algorithm_name_lower):
    """获取算法相关的关键词"""
    keyword_map = {
        "gradient descent": ["gradient", "descent", "optimization", "optimizer"],
        "k-means clustering": ["k-means", "kmeans", "clustering", "cluster"],
        "logistic regression": ["logistic", "regression", "classification"],
        "neural network": ["neural", "network", "deep learning", "neural network"],
        "principal component analysis": [
            "pca",
            "principal component",
            "dimensionality reduction",
        ],
        "perceptron": ["perceptron", "single layer", "basic neural"],
    }

    chinese_keywords = {
        "gradient descent": ["梯度下降", "优化算法", "梯度"],
        "k-means clustering": ["k-means", "聚类", "k均值"],
        "logistic regression": ["逻辑回归", "分类", "sigmoid"],
        "neural network": ["神经网络", "深度学习", "神经元"],
        "principal component analysis": ["主成分分析", "pca", "降维"],
        "perceptron": ["感知机", "单层神经网络"],
    }

    keywords = []
    if algorithm_name_lower in keyword_map:
        keywords.extend(keyword_map[algorithm_name_lower])
    if algorithm_name_lower in chinese_keywords:
        keywords.extend(chinese_keywords[algorithm_name_lower])

    return keywords


@api_bp.route("/ai/generate-learning-report", methods=["POST"])
@token_required
def generate_learning_report(current_user_id):
    """使用DeepSeek API生成个性化学习报告"""
    try:
        import requests

        # DeepSeek API配置
        DEEPSEEK_API_KEY = "sk-760cc5069ecd43bf90e868e4b31de037"
        DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

        # 获取用户数据
        user_knowledge = UserKnowledge.query.filter_by(user_id=current_user_id).all()
        user_posts = Post.query.filter_by(author_id=current_user_id).all()

        # 获取所有算法数据用于分析
        all_algorithms = Algorithm.query.all()

        # 构建学习分析数据
        knowledge_data = []
        for knowledge in user_knowledge:
            algorithm = Algorithm.query.get(knowledge.algorithm_id)
            knowledge_data.append(
                {
                    "algorithm_name": algorithm.name if algorithm else "Unknown",
                    "progress": knowledge.progress,
                    "last_accessed": (
                        knowledge.last_accessed.isoformat() + "Z"
                        if knowledge.last_accessed
                        else None
                    ),
                    "interests": knowledge.interests or [],
                }
            )

        # 构建帖子数据
        posts_data = []
        for post in user_posts[:10]:  # 限制为最近10个帖子
            posts_data.append(
                {
                    "title": post.title,
                    "content": (
                        post.content[:200] + "..."
                        if len(post.content) > 200
                        else post.content
                    ),
                    "created_at": (
                        post.created_at.isoformat() + "Z" if post.created_at else None
                    ),
                    "tags": post.tags or [],
                }
            )

        # 获取所有算法用于推荐
        all_algorithms = Algorithm.query.all()
        algorithms_for_recommendation = []
        for alg in all_algorithms:
            algorithms_for_recommendation.append(
                {
                    "id": alg.id,
                    "name": alg.name,
                    "description": alg.description or "",
                    "difficulty": alg.difficulty,
                    "category": alg.category.name if alg.category else "其他",
                }
            )

        # 获取所有帖子用于推荐
        all_posts = Post.query.order_by(Post.created_at.desc()).limit(50).all()
        posts_for_recommendation = []
        for post in all_posts:
            posts_for_recommendation.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "content": (
                        post.content[:200] + "..."
                        if len(post.content) > 200
                        else post.content
                    ),
                    "author": post.author.username if post.author else "Anonymous",
                    "tags": post.tags or [],
                    "created_at": (
                        post.created_at.isoformat() + "Z" if post.created_at else None
                    ),
                }
            )

        # 构建提示词
        prompt = f"""
你是一位专业的人工智能学习助手。请基于以下用户数据，生成一份个性化的机器学习学习报告。

## 用户学习数据：
{json.dumps(knowledge_data, indent=2, ensure_ascii=False)}

## 用户发布的帖子：
{json.dumps(posts_data, indent=2, ensure_ascii=False)}

## 重要要求：
1. **只能推荐系统中已有的算法和帖子** - 请从下面提供的列表中选择推荐内容
2. **格式要求** - 请严格按照以下格式输出，不要添加额外内容：

### 📊 学习概况分析
[分析用户的学习进度、活跃度和掌握情况]

### 🎯 知识薄弱点
[指出用户需要加强的具体领域]

### 📈 学习建议
**优先学习：[算法名称]** - [简要理由]
**进阶学习：[算法名称]** - [简要理由]
**专项突破：[算法名称]** - [简要理由]

### 📚 推荐帖子
1. **[帖子标题]** (ID: [帖子ID]) - [推荐理由]
2. **[帖子标题]** (ID: [帖子ID]) - [推荐理由]
3. **[帖子标题]** (ID: [帖子ID]) - [推荐理由]

## 系统可用算法列表：
{json.dumps(algorithms_for_recommendation, indent=2, ensure_ascii=False)}

## 系统可用帖子列表：
{json.dumps(posts_for_recommendation, indent=2, ensure_ascii=False)}

请用中文回复，严格按照上述格式输出，确保推荐的算法和帖子都来自系统列表。
"""

        # 调用DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()

        report_content = response.json()["choices"][0]["message"]["content"]

        # 记录操作日志
        log_action(
            current_user_id,
            "generate_learning_report",
            "ai",
            None,
            {"report_length": len(report_content)},
        )

        # 解析AI响应中的推荐算法和帖子
        import re

        # 从结构化输出中提取推荐的算法名称
        recommended_algorithm_names = []
        algorithm_matches = re.findall(r"\*\*.*?:\s*\[([^\]]+)\]", report_content)
        for match in algorithm_matches:
            if match and len(recommended_algorithm_names) < 3:
                recommended_algorithm_names.append(match.strip())

        # 如果没有找到结构化的算法，尝试其他模式
        if not recommended_algorithm_names:
            algorithm_patterns = [
                r"优先学习[：:]\s*([^\n\-]+)",
                r"进阶学习[：:]\s*([^\n\-]+)",
                r"专项突破[：:]\s*([^\n\-]+)",
            ]
            for pattern in algorithm_patterns:
                matches = re.findall(pattern, report_content)
                for match in matches:
                    clean_name = match.strip()
                    if clean_name and clean_name not in recommended_algorithm_names:
                        recommended_algorithm_names.append(clean_name)
                        if len(recommended_algorithm_names) >= 3:
                            break
                if len(recommended_algorithm_names) >= 3:
                    break

        # 从报告中提取推荐的帖子ID
        recommended_post_ids = []
        post_id_matches = re.findall(r"\(ID:\s*(\d+)\)", report_content)
        for post_id in post_id_matches:
            if post_id and len(recommended_post_ids) < 3:
                try:
                    recommended_post_ids.append(int(post_id))
                except Exception:
                    pass

        # 获取推荐算法的详细信息
        recommended_algorithm_objects = []
        for alg_name in recommended_algorithm_names:
            # 尝试精确匹配
            alg = Algorithm.query.filter_by(name=alg_name).first()
            if not alg:
                # 尝试模糊匹配
                for sys_alg in all_algorithms:
                    if (
                        alg_name.lower() in sys_alg.name.lower()
                        or sys_alg.name.lower() in alg_name.lower()
                    ):
                        alg = sys_alg
                        break
            if alg:
                recommended_algorithm_objects.append(alg.to_dict())

        # 获取推荐帖子的详细信息
        recommended_post_objects = []
        for post_id in recommended_post_ids:
            post = Post.query.get(post_id)
            if post:
                recommended_post_objects.append(
                    {
                        "id": post.id,
                        "title": post.title,
                        "author": post.author.username if post.author else "Anonymous",
                    }
                )

        return (
            jsonify(
                {
                    "success": True,
                    "report": report_content,
                    "recommendations": {
                        "algorithms": recommended_algorithm_objects,
                        "posts": recommended_post_objects,
                    },
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Generate learning report error: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to generate learning report",
                    "error": str(e),
                }
            ),
            500,
        )
