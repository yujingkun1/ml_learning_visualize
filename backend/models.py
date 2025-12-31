from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy实例将在app.py中初始化
db = SQLAlchemy()


# 用户表
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user")  # 'user' or 'admin'
    avatar = db.Column(
        db.Text(length=16777215)
    )  # LONGTEXT in MySQL, supports up to ~16MB
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关联
    knowledge_records = db.relationship(
        "UserKnowledge", back_populates="user", cascade="all, delete-orphan"
    )
    posts = db.relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )
    likes = db.relationship("Like", back_populates="user", cascade="all, delete-orphan")
    favorites = db.relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "avatar": self.avatar,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# 算法分类表
class AlgorithmCategory(db.Model):
    __tablename__ = "algorithm_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey("algorithm_categories.id"))
    level = db.Column(db.Integer, default=1)  # 层级：1-主要类别，2-子类别
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    parent = db.relationship("AlgorithmCategory", remote_side=[id], backref="children")
    algorithms = db.relationship(
        "Algorithm", back_populates="category", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "level": self.level,
            "order": self.order,
            "children": [child.to_dict() for child in self.children],
        }


# 算法表
class Algorithm(db.Model):
    __tablename__ = "algorithms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # 添加唯一约束
    chinese_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    category_id = db.Column(
        db.Integer, db.ForeignKey("algorithm_categories.id"), nullable=False
    )
    difficulty = db.Column(
        db.String(20), default="intermediate"
    )  # 'beginner', 'intermediate', 'advanced'
    tags = db.Column(db.JSON)  # 标签数组
    paper_url = db.Column(db.String(500))
    code_url = db.Column(db.String(500))
    code_example = db.Column(db.Text)  # Python代码示例
    visualization_data = db.Column(db.JSON)  # 可视化数据
    theory = db.Column(db.Text)  # 完整理论内容（Markdown）
    notebook_html_url = db.Column(db.String(500))  # notebook HTML URL
    has_interactive_demo = db.Column(db.Boolean, default=False)  # 是否有交互演示
    interactive_demo_url = db.Column(db.String(500))  # 交互演示Marimo URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关联
    category = db.relationship("AlgorithmCategory", back_populates="algorithms")
    knowledge_records = db.relationship(
        "UserKnowledge", back_populates="algorithm", cascade="all, delete-orphan"
    )
    related_posts = db.relationship(
        "AlgorithmPost", back_populates="algorithm", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "chinese_name": self.chinese_name,
            "description": self.description,
            "category": self.category.to_dict() if self.category else None,
            "difficulty": self.difficulty,
            "tags": self.tags or [],
            "paper_url": self.paper_url,
            "code_url": self.code_url,
            "code_example": self.code_example,
            "visualization_data": self.visualization_data,
            "theory": self.theory,
            "notebook_html_url": self.notebook_html_url,
            "has_interactive_demo": self.has_interactive_demo,
            "interactive_demo_url": self.interactive_demo_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# 用户知识记录表（多对多关系的核心）
class UserKnowledge(db.Model):
    __tablename__ = "user_knowledge"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    algorithm_id = db.Column(db.Integer, db.ForeignKey("algorithms.id"), nullable=False)
    progress = db.Column(db.Float, default=0.0)  # 学习进度 0-100
    interests = db.Column(db.JSON)  # 用户对该算法的兴趣标签
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关联
    user = db.relationship("User", back_populates="knowledge_records")
    algorithm = db.relationship("Algorithm", back_populates="knowledge_records")

    # 唯一约束，确保每个用户-算法对只有一条记录
    __table_args__ = (
        db.UniqueConstraint("user_id", "algorithm_id", name="unique_user_algorithm"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "algorithm_id": self.algorithm_id,
            "progress": self.progress,
            "interests": self.interests or [],
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# 帖子表
class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    tags = db.Column(db.JSON)  # 帖子标签数组
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关联
    author = db.relationship("User", back_populates="posts")
    comments = db.relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="Comment.created_at",
    )
    likes = db.relationship("Like", back_populates="post", cascade="all, delete-orphan")
    favorites = db.relationship(
        "Favorite", back_populates="post", cascade="all, delete-orphan"
    )
    algorithms = db.relationship(
        "AlgorithmPost", back_populates="post", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author.to_dict() if self.author else None,
            "is_featured": self.is_featured,
            "tags": self.tags or [],
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
        }


# 评论表
class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"))  # 回复评论
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关联
    post = db.relationship("Post", back_populates="comments")
    author = db.relationship("User", back_populates="comments")
    parent = db.relationship("Comment", remote_side=[id], backref="replies")

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "post_id": self.post_id,
            "author": self.author.to_dict() if self.author else None,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "replies": [reply.to_dict() for reply in self.replies],
        }


# 点赞表
class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    user = db.relationship("User", back_populates="likes")
    post = db.relationship("Post", back_populates="likes")

    # 唯一约束，确保用户不能重复点赞
    __table_args__ = (
        db.UniqueConstraint("user_id", "post_id", name="unique_user_post_like"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# 收藏表
class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    user = db.relationship("User", back_populates="favorites")
    post = db.relationship("Post", back_populates="favorites")

    # 唯一约束，确保用户不能重复收藏
    __table_args__ = (
        db.UniqueConstraint("user_id", "post_id", name="unique_user_post_favorite"),
    )


# 算法-帖子关联表（多对多）
class AlgorithmPost(db.Model):
    __tablename__ = "algorithm_posts"

    id = db.Column(db.Integer, primary_key=True)
    algorithm_id = db.Column(db.Integer, db.ForeignKey("algorithms.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    algorithm = db.relationship("Algorithm", back_populates="related_posts")
    post = db.relationship("Post", back_populates="algorithms")

    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint("algorithm_id", "post_id", name="unique_algorithm_post"),
    )


# 好友关系表
class Friend(db.Model):
    __tablename__ = "friends"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(
        db.String(20), default="pending"
    )  # 'pending', 'accepted', 'blocked'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关联
    user = db.relationship(
        "User", foreign_keys=[user_id], backref="sent_friend_requests"
    )
    friend = db.relationship(
        "User", foreign_keys=[friend_id], backref="received_friend_requests"
    )

    # 唯一约束，确保每对用户只有一个好友关系
    __table_args__ = (
        db.UniqueConstraint("user_id", "friend_id", name="unique_friendship"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "friend_id": self.friend_id,
            "status": self.status,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
            "friend": self.friend.to_dict() if self.friend else None,
        }


# 聊天消息表
class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default="text")  # 'text', 'image', 'file'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = db.relationship(
        "User", foreign_keys=[receiver_id], backref="received_messages"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "message_type": self.message_type,
            "is_read": self.is_read,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "sender": self.sender.to_dict() if self.sender else None,
            "receiver": self.receiver.to_dict() if self.receiver else None,
        }


# 系统日志表
class SystemLog(db.Model):
    __tablename__ = "system_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(
        db.String(100), nullable=False
    )  # 'login', 'register', 'create_post', etc.
    resource_type = db.Column(db.String(50))  # 'post', 'comment', 'algorithm', etc.
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)  # 额外详情
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    user = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
