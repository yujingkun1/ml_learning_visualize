#!/usr/bin/env python3
"""
数据库初始化脚本
创建基础数据：算法分类、算法、示例帖子等
"""

from app import create_app
from models import db, AlgorithmCategory, Algorithm, User, Post, AlgorithmPost


def init_categories():
    """初始化算法分类"""
    categories_data = [
        # 一级分类
        {
            "name": "监督学习",
            "description": "有标签数据的学习方法",
            "level": 1,
            "order": 1,
        },
        {
            "name": "无监督学习",
            "description": "无标签数据的学习方法",
            "level": 1,
            "order": 2,
        },
        {
            "name": "深度学习",
            "description": "基于神经网络的学习方法",
            "level": 1,
            "order": 3,
        },
        {
            "name": "强化学习",
            "description": "通过奖励信号学习最优策略",
            "level": 1,
            "order": 4,
        },
        {
            "name": "集成学习",
            "description": "组合多个模型的方法",
            "level": 1,
            "order": 5,
        },
        # 二级分类 - 监督学习
        {
            "name": "线性模型",
            "description": "基于线性关系的模型",
            "level": 2,
            "order": 1,
            "parent_name": "监督学习",
        },
        {
            "name": "决策树",
            "description": "基于树结构的模型",
            "level": 2,
            "order": 2,
            "parent_name": "监督学习",
        },
        {
            "name": "支持向量机",
            "description": "最大化分类间隔的模型",
            "level": 2,
            "order": 3,
            "parent_name": "监督学习",
        },
        {
            "name": "贝叶斯方法",
            "description": "基于概率的分类方法",
            "level": 2,
            "order": 4,
            "parent_name": "监督学习",
        },
        # 二级分类 - 无监督学习
        {
            "name": "聚类算法",
            "description": "将数据分组的方法",
            "level": 2,
            "order": 1,
            "parent_name": "无监督学习",
        },
        {
            "name": "降维算法",
            "description": "降低数据维度的技术",
            "level": 2,
            "order": 2,
            "parent_name": "无监督学习",
        },
        {
            "name": "关联规则",
            "description": "发现数据间关联的方法",
            "level": 2,
            "order": 3,
            "parent_name": "无监督学习",
        },
        # 二级分类 - 深度学习
        {
            "name": "卷积神经网络",
            "description": "适用于图像数据的网络结构",
            "level": 2,
            "order": 1,
            "parent_name": "深度学习",
        },
        {
            "name": "循环神经网络",
            "description": "适用于序列数据的网络结构",
            "level": 2,
            "order": 2,
            "parent_name": "深度学习",
        },
        {
            "name": "生成对抗网络",
            "description": "生成数据的对抗性网络",
            "level": 2,
            "order": 3,
            "parent_name": "深度学习",
        },
        {
            "name": "图神经网络",
            "description": "适用于图结构数据的网络",
            "level": 2,
            "order": 4,
            "parent_name": "深度学习",
        },
    ]

    categories = {}
    # 先创建一级分类
    for cat_data in categories_data:
        if cat_data.get("level") == 1:
            category = AlgorithmCategory(
                name=cat_data["name"],
                description=cat_data["description"],
                level=cat_data["level"],
                order=cat_data["order"],
            )
            db.session.add(category)
            categories[cat_data["name"]] = category

    db.session.commit()

    # 再创建二级分类
    for cat_data in categories_data:
        if cat_data.get("level") == 2:
            parent_name = cat_data.get("parent_name")
            parent_id = (
                categories[parent_name].id if parent_name in categories else None
            )

            category = AlgorithmCategory(
                name=cat_data["name"],
                description=cat_data["description"],
                level=cat_data["level"],
                order=cat_data["order"],
                parent_id=parent_id,
            )
            db.session.add(category)
            categories[cat_data["name"]] = category

    db.session.commit()
    print("算法分类初始化完成")
    return categories


def clear_duplicate_algorithms():
    """清除重复的算法数据"""
    try:
        # 获取所有算法名称及其出现次数
        from sqlalchemy import text

        result = db.session.execute(
            text(
                """
            SELECT name, COUNT(*) as count
            FROM algorithms
            GROUP BY name
            HAVING COUNT(*) > 1
        """
            )
        ).fetchall()

        for row in result:
            alg_name = row[0]
            # 保留第一个，删除其他的
            algorithms = Algorithm.query.filter_by(name=alg_name).all()
            for alg in algorithms[1:]:  # 从第二个开始删除
                db.session.delete(alg)

        db.session.commit()
        print("清除重复算法完成")
    except Exception as e:
        print(f"清除重复算法时出错: {e}")
        db.session.rollback()


def init_algorithms():
    """初始化算法数据"""
    algorithms_data = [
        {
            "name": "Linear Regression",
            "chinese_name": "线性回归",
            "description": "通过最小化误差平方和来拟合数据点的直线",
            "category_name": "线性模型",
            "difficulty": "beginner",
            "tags": ["线性", "回归", "监督学习"],
            "paper_url": "https://en.wikipedia.org/wiki/Linear_regression",
            "code_url": (
                "https://scikit-learn.org/stable/modules/generated/"
                "sklearn.linear_model.LinearRegression.html"
            ),
            "code_example": """
# Linear Regression Implementation
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Generate sample data
np.random.seed(42)
X = np.random.rand(100, 1) * 10
y = 2.5 * X.flatten() + 1.5 + np.random.randn(100) * 2

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Coefficient: {model.coef_[0]:.2f}")
print(f"Intercept: {model.intercept_:.2f}")
print(f"Mean Squared Error: {mse:.2f}")
print(f"R² Score: {r2:.2f}")

# Visualize the results
plt.scatter(X_test, y_test, color='blue', label='Actual')
plt.plot(X_test, y_pred, color='red', linewidth=2, label='Predicted')
plt.xlabel('X')
plt.ylabel('y')
plt.title('Linear Regression Results')
plt.legend()
plt.show()
""",
            "visualization_data": {
                "type": "linear_regression",
                "description": (
                    "Interactive linear regression visualization with scatter plot "
                    "and regression line"
                ),
                "interactive": True,
                "steps": [
                    "Generate random data points",
                    "Apply linear regression algorithm",
                    "Visualize the regression line",
                    "Show model performance metrics",
                ],
            },
            "code_examples": {
                "python": """import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Generate sample data
np.random.seed(42)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X + np.random.randn(100, 1)

# Split the data
X_train, X_test = X[:80], X[80:]
y_train, y_test = y[:80], y[80:]

# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean squared error: {mse:.2f}")
print(f"Coefficient of determination: {r2:.2f}")
print(f"Intercept: {model.intercept_[0]:.2f}")
print(f"Slope: {model.coef_[0][0]:.2f}")

# Visualize the results
plt.scatter(X_test, y_test, color='blue', label='Actual data')
plt.plot(X_test, y_pred, color='red', linewidth=2, label='Regression line')
plt.xlabel('X')
plt.ylabel('y')
plt.title('Linear Regression Example')
plt.legend()
plt.show()"""
            },
        },
        {
            "name": "Logistic Regression",
            "chinese_name": "逻辑回归",
            "description": "用于二分类问题的线性模型，通过sigmoid函数将输出映射到0-1之间",
            "category_name": "线性模型",
            "difficulty": "beginner",
            "tags": ["线性", "分类", "监督学习", "sigmoid"],
            "paper_url": "https://en.wikipedia.org/wiki/Logistic_regression",
            "code_url": (
                "https://scikit-learn.org/stable/modules/generated/"
                "sklearn.linear_model.LogisticRegression.html"
            ),
            "code_example": """
# Logistic Regression Implementation
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.datasets import make_classification
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Generate sample classification data
X, y = make_classification(n_samples=200, n_features=2, n_informative=2,
                          n_redundant=0, n_clusters_per_class=1,
                          random_state=42)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Create and train the model
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
print("\\nClassification Report:")
print(classification_report(y_test, y_pred))

# Visualize decision boundary
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                     np.arange(y_min, y_max, 0.1))

Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

plt.contourf(xx, yy, Z, alpha=0.4, cmap=ListedColormap(['#FFAAAA', '#AAAAFF']))
plt.scatter(X[:, 0], X[:, 1], c=y, alpha=0.8, edgecolors='k')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('Logistic Regression Decision Boundary')
plt.show()
""",
            "visualization_data": {
                "type": "logistic_regression",
                "description": (
                    "Interactive logistic regression with decision boundary "
                    "visualization"
                ),
                "interactive": True,
                "steps": [
                    "Generate binary classification data",
                    "Train logistic regression model",
                    "Plot decision boundary",
                    "Show classification accuracy",
                ],
            },
            "code_examples": {
                "python": """import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score, classification_report

# Generate synthetic dataset
X, y = make_classification(n_samples=200, n_features=2, n_informative=2,
                          n_redundant=0, n_clusters_per_class=1, random_state=42)

# Split the data
X_train, X_test = X[:150], X[150:]
y_train, y_test = y[:150], y[150:]

# Create and train the model
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.3f}")
print("\\nClassification Report:")
print(classification_report(y_test, y_pred))

# Visualize decision boundary
def plot_decision_boundary(X, y, model):
    # Create mesh grid
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                         np.arange(y_min, y_max, 0.1))

    # Predict on mesh
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Plot
    plt.contourf(xx, yy, Z, alpha=0.4)
    plt.scatter(X[:, 0], X[:, 1], c=y, alpha=0.8)
    plt.xlabel('Feature 1')
    plt.ylabel('Feature 2')
    plt.title('Logistic Regression Decision Boundary')
    plt.show()

plot_decision_boundary(X, y, model)"""
            },
        },
        {
            "name": "Decision Tree",
            "chinese_name": "决策树",
            "description": "通过递归分割数据空间来构建分类或回归模型",
            "category_name": "决策树",
            "difficulty": "intermediate",
            "tags": ["树", "分类", "回归", "监督学习"],
            "paper_url": "https://en.wikipedia.org/wiki/Decision_tree_learning",
            "code_url": (
                "https://scikit-learn.org/stable/modules/generated/"
                "sklearn.tree.DecisionTreeClassifier.html"
            ),
            "visualization_data": {
                "type": "decision_tree",
                "description": (
                    "Interactive decision tree visualization with node splitting"
                ),
                "interactive": True,
                "steps": [
                    "Build decision tree from data",
                    "Visualize tree structure",
                    "Show feature importance",
                    "Demonstrate prediction process",
                ],
            },
            "code_examples": {
                "python": """import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Generate synthetic dataset
X, y = make_classification(n_samples=1000, n_features=4, n_informative=4,
                          n_redundant=0, n_classes=3, random_state=42)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Create and train decision tree
tree = DecisionTreeClassifier(max_depth=4, random_state=42)
tree.fit(X_train, y_train)

# Make predictions
y_pred = tree.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.3f}")
print("\\nClassification Report:")
print(classification_report(y_test, y_pred))

# Visualize the decision tree
plt.figure(figsize=(20, 10))
plot_tree(tree, feature_names=['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4'],
          class_names=['Class 0', 'Class 1', 'Class 2'],
          filled=True, rounded=True, fontsize=10)
plt.title('Decision Tree Structure')
plt.show()

# Feature importance
feature_importance = tree.feature_importances_
features = ['Feature 1', 'Feature 2', 'Feature 3', 'Feature 4']

plt.figure(figsize=(10, 6))
plt.barh(features, feature_importance)
plt.xlabel('Feature Importance')
plt.ylabel('Features')
plt.title('Decision Tree Feature Importance')
plt.show()

print("\\nFeature Importance:")
for feature, importance in zip(features, feature_importance):
    print(f"{feature}: {importance:.3f}")

# Demonstrate prediction process
print("\\nPrediction Example:")
sample = X_test[0:1]
print(f"Sample features: {sample[0]}")
prediction = tree.predict(sample)
print(f"Predicted class: {prediction[0]}")
print(f"Actual class: {y_test[0]}")"""
            },
        },
        {
            "name": "Random Forest",
            "chinese_name": "随机森林",
            "description": "基于决策树的集成学习方法，通过bootstrap采样和特征随机选择来构建多个决策树",
            "category_name": "集成学习",
            "difficulty": "intermediate",
            "tags": ["集成学习", "决策树", "bagging", "监督学习"],
            "paper_url": "https://en.wikipedia.org/wiki/Random_forest",
            "code_url": (
                "https://scikit-learn.org/stable/modules/generated/"
                "sklearn.ensemble.RandomForestClassifier.html"
            ),
            "visualization_data": {
                "type": "feature_importance",
                "description": "展示各特征的重要性",
            },
        },
        {
            "name": "K-Means Clustering",
            "chinese_name": "K-均值聚类",
            "description": "通过迭代优化簇内距离平方和来将数据点分配到K个簇中",
            "category_name": "聚类算法",
            "difficulty": "beginner",
            "tags": ["聚类", "无监督学习", "距离度量"],
            "paper_url": "https://en.wikipedia.org/wiki/K-means_clustering",
            "code_url": (
                "https://scikit-learn.org/stable/modules/generated/"
                "sklearn.cluster.KMeans.html"
            ),
            "code_example": """
# K-Means Clustering Implementation
import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# Generate sample data with 4 clusters
X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=42)

# Determine optimal number of clusters using Elbow method
inertias = []
K = range(1, 10)

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)

# Plot Elbow curve
plt.figure(figsize=(8, 4))
plt.plot(K, inertias, 'bx-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method for Optimal k')
plt.show()

# Perform K-means clustering with optimal k=4
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
y_kmeans = kmeans.fit_predict(X)

# Calculate silhouette score
silhouette_avg = silhouette_score(X, y_kmeans)
print(f"Silhouette Score: {silhouette_avg:.2f}")

# Visualize the clusters
plt.figure(figsize=(10, 6))

# Plot data points with cluster colors
colors = ['red', 'blue', 'green', 'orange']
for i in range(4):
    plt.scatter(X[y_kmeans == i, 0], X[y_kmeans == i, 1],
               c=colors[i], label=f'Cluster {i+1}', alpha=0.6)

# Plot cluster centers
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1],
           s=200, c='black', marker='X', label='Centroids')

plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.title('K-Means Clustering Results')
plt.legend()
plt.show()

# Print cluster centers
print("\\nCluster Centers:")
for i, center in enumerate(kmeans.cluster_centers_):
    print(f"Cluster {i+1}: ({center[0]:.2f}, {center[1]:.2f})")
""",
            "visualization_data": {
                "type": "kmeans_clustering",
                "description": (
                    "Interactive K-means clustering with step-by-step visualization"
                ),
                "interactive": True,
                "steps": [
                    "Initialize cluster centroids",
                    "Assign points to nearest centroid",
                    "Update centroid positions",
                    "Repeat until convergence",
                    "Show final clustering result",
                ],
            },
            "code_examples": {
                "python": """import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

# Generate sample data
np.random.seed(42)
X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)

# Create K-means model
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
kmeans.fit(X)

# Get cluster centers and labels
centers = kmeans.cluster_centers_
labels = kmeans.labels_

# Print results
print(f"Cluster centers:\\n{centers}")
print(f"Inertia (within-cluster sum of squares): {kmeans.inertia_:.2f}")

# Visualize the results
def plot_clusters(X, labels, centers):
    plt.figure(figsize=(10, 6))

    # Plot data points colored by cluster
    unique_labels = np.unique(labels)
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']

    for i, label in enumerate(unique_labels):
        mask = labels == label
        plt.scatter(X[mask, 0], X[mask, 1], c=colors[i % len(colors)],
                   label=f'Cluster {label}', alpha=0.6)

    # Plot cluster centers
    plt.scatter(centers[:, 0], centers[:, 1], c='black', marker='x',
               s=200, linewidth=3, label='Centroids')

    plt.xlabel('Feature 1')
    plt.ylabel('Feature 2')
    plt.title('K-Means Clustering Results')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

plot_clusters(X, labels, centers)

# Evaluate clustering quality
from sklearn.metrics import silhouette_score
silhouette_avg = silhouette_score(X, labels)
print(f"Silhouette Score: {silhouette_avg:.3f}")"""
            },
        },
        {
            "name": "Principal Component Analysis",
            "chinese_name": "主成分分析",
            "description": "通过线性变换将高维数据投影到低维空间，保留最大方差",
            "category_name": "降维算法",
            "difficulty": "intermediate",
            "tags": ["降维", "无监督学习", "线性变换", "方差"],
            "paper_url": "https://en.wikipedia.org/wiki/Principal_component_analysis",
            "code_url": (
                "https://scikit-learn.org/stable/modules/generated/"
                "sklearn.decomposition.PCA.html"
            ),
            "code_example": """
# Principal Component Analysis (PCA) Implementation
import numpy as np
from sklearn.decomposition import PCA
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Load the digits dataset
digits = load_digits()
X = digits.data
y = digits.target

# Standardize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Perform PCA
pca = PCA(n_components=2)  # Reduce to 2 dimensions for visualization
X_pca = pca.fit_transform(X_scaled)

# Calculate explained variance
explained_variance = pca.explained_variance_ratio_
print(f"Explained variance by component: {explained_variance}")
print(f"Total explained variance: {np.sum(explained_variance):.2f}")

# Visualize the results
plt.figure(figsize=(12, 5))

# Plot 1: Explained variance
plt.subplot(1, 2, 1)
components = range(1, len(explained_variance) + 1)
plt.bar(components, explained_variance * 100)
plt.xlabel('Principal Component')
plt.ylabel('Explained Variance (%)')
plt.title('Explained Variance by Principal Components')
plt.xticks(components)

# Plot 2: 2D PCA projection
plt.subplot(1, 2, 2)
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='tab10', alpha=0.7)
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title('PCA 2D Projection of Digits Dataset')
plt.colorbar(scatter, label='Digit Class')

plt.tight_layout()
plt.show()

# Show how much variance is preserved
cumulative_variance = np.cumsum(explained_variance)
plt.figure(figsize=(8, 5))
plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance * 100, 'bo-')
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance (%)')
plt.title('Cumulative Explained Variance')
plt.grid(True)
plt.show()

# Transform new data
print("\\nPCA Components shape:", pca.components_.shape)
print("Original data shape:", X.shape)
print("Reduced data shape:", X_pca.shape)
""",
            "visualization_data": {
                "type": "pca_visualization",
                "description": "Principal Component Analysis visualization in 2D space",
                "interactive": True,
                "steps": [
                    "Generate high-dimensional data",
                    "Compute principal components",
                    "Project data to 2D",
                    "Show explained variance ratio",
                ],
            },
            "code_examples": {
                "python": """import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler

# Load the digits dataset (64 features)
digits = load_digits()
X = digits.data
y = digits.target

# Standardize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Print explained variance
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
print(f"Total explained variance: {np.sum(pca.explained_variance_ratio_):.3f}")

# Visualize the results
def plot_pca(X_pca, y):
    plt.figure(figsize=(10, 8))

    # Plot the first two principal components
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='tab10',
                         alpha=0.7, s=50)

    plt.xlabel('First Principal Component')
    plt.ylabel('Second Principal Component')
    plt.title('PCA: Digits Dataset (64D → 2D)')
    plt.colorbar(scatter, label='Digit Label')
    plt.grid(True, alpha=0.3)
    plt.show()

plot_pca(X_pca, y)

# Show cumulative explained variance
plt.figure(figsize=(8, 6))
pca_full = PCA()
pca_full.fit(X_scaled)

cumulative_variance = np.cumsum(pca_full.explained_variance_ratio_)
plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, 'bo-')
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance')
plt.title('PCA: Cumulative Explained Variance')
plt.grid(True, alpha=0.3)
plt.show()

# Print how many components needed for 95% variance
n_components_95 = np.where(cumulative_variance >= 0.95)[0][0] + 1
print(f"Components needed for 95% variance: {n_components_95}")"""
            },
        },
        {
            "name": "Convolutional Neural Network",
            "chinese_name": "卷积神经网络",
            "description": "专为处理网格结构数据（如图像）设计的神经网络，通过卷积操作提取局部特征",
            "category_name": "卷积神经网络",
            "difficulty": "advanced",
            "tags": ["深度学习", "卷积", "图像处理", "CNN"],
            "paper_url": "https://arxiv.org/abs/1409.1556",
            "code_url": "https://pytorch.org/docs/stable/nn.html#conv2d",
            "code_example": """
# Convolutional Neural Network (CNN) Implementation
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

# Define the CNN architecture
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        # Convolutional layers
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)  # 28x28 -> 28x28
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1) # 14x14 -> 14x14
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)# 7x7 -> 7x7

        # Pooling layer
        self.pool = nn.MaxPool2d(2, 2)

        # Fully connected layers
        self.fc1 = nn.Linear(128 * 3 * 3, 512)
        self.fc2 = nn.Linear(512, 10)

        # Activation and dropout
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        # Convolutional layers with ReLU and pooling
        x = self.pool(self.relu(self.conv1(x)))  # 28x28 -> 14x14
        x = self.pool(self.relu(self.conv2(x)))  # 14x14 -> 7x7
        x = self.pool(self.relu(self.conv3(x)))  # 7x7 -> 3x3

        # Flatten for fully connected layers
        x = x.view(-1, 128 * 3 * 3)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Data preprocessing
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# Load MNIST dataset
train_dataset = datasets.MNIST('data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# Initialize model, loss function, and optimizer
model = SimpleCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
num_epochs = 5
train_losses = []
train_accuracies = []

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Statistics
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    epoch_loss = running_loss / len(train_loader)
    epoch_accuracy = 100 * correct / total
    train_losses.append(epoch_loss)
    train_accuracies.append(epoch_accuracy)

    print(
        f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss:.4f}, "
        f"Accuracy: {epoch_accuracy:.2f}%"
    )

# Evaluate on test set
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

test_accuracy = 100 * correct / total
print(f"\\nTest Accuracy: {test_accuracy:.2f}%")

# Visualize training results
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(train_losses, 'b-', label='Training Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss Over Time')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(train_accuracies, 'r-', label='Training Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy (%)')
plt.title('Training Accuracy Over Time')
plt.legend()

plt.tight_layout()
plt.show()
""",
            "visualization_data": {
                "type": "cnn_architecture",
                "description": (
                    "Convolutional Neural Network architecture visualization"
                ),
                "interactive": True,
                "steps": [
                    "Show input image",
                    "Visualize convolution operations",
                    "Display feature maps",
                    "Demonstrate pooling layers",
                    "Show fully connected layers",
                ],
            },
            "code_examples": {
                "python": """import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np

# Define CNN architecture
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.25)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = self.pool(x)
        x = torch.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(-1, 64 * 7 * 7)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# Load MNIST dataset
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, transform=transform)

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

# Initialize model, loss function, and optimizer
model = SimpleCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training function
def train(epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        if batch_idx % 100 == 0:
            print(
                f'Train Epoch: {epoch} [{batch_idx * len(data)}/'
                f'{len(train_loader.dataset)} '
                f'({100. * batch_idx / len(train_loader):.0f}%)]\t'
                f'Loss: {loss.item():.6f}'
            )

# Test function
def test():
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    accuracy = 100. * correct / len(test_loader.dataset)

    print(f'\\nTest set: Average loss: {test_loss:.4f}, '
          f'Accuracy: {correct}/{len(test_loader.dataset)} ({accuracy:.2f}%)\\n')
    return accuracy

# Train the model
num_epochs = 5
for epoch in range(1, num_epochs + 1):
    train(epoch)
    accuracy = test()

# Visualize feature maps
def visualize_feature_maps(model, input_image):
    model.eval()

    # Get feature maps after first conv layer
    with torch.no_grad():
        x = torch.relu(model.conv1(input_image.unsqueeze(0)))
        feature_maps = x.squeeze(0).cpu().numpy()

    # Plot first 16 feature maps
    fig, axes = plt.subplots(4, 4, figsize=(8, 8))
    for i in range(16):
        ax = axes[i//4, i%4]
        ax.imshow(feature_maps[i], cmap='viridis')
        ax.axis('off')
        ax.set_title(f'Filter {i+1}')
    plt.tight_layout()
    plt.show()

# Get a sample image
sample_image, _ = train_dataset[0]
visualize_feature_maps(model, sample_image)

print("\\nCNN Architecture Summary:")
print(model)
total_params = sum(p.numel() for p in model.parameters())
print(f"\\nTotal parameters: {total_params:,}")"""
            },
        },
        {
            "name": "Recurrent Neural Network",
            "chinese_name": "循环神经网络",
            "description": "能够处理序列数据的神经网络，通过循环连接保持历史信息",
            "category_name": "循环神经网络",
            "difficulty": "advanced",
            "tags": ["深度学习", "序列", "RNN", "LSTM", "GRU"],
            "paper_url": "https://arxiv.org/abs/1409.3215",
            "code_url": "https://pytorch.org/docs/stable/nn.html#rnn",
            "visualization_data": {
                "type": "rnn_architecture",
                "description": (
                    "Recurrent Neural Network sequence processing visualization"
                ),
                "interactive": True,
                "steps": [
                    "Show input sequence",
                    "Visualize hidden state updates",
                    "Demonstrate backpropagation through time",
                    "Show gradient flow",
                    "Display sequence predictions",
                ],
            },
        },
        {
            "name": "Graph Neural Network",
            "chinese_name": "图神经网络",
            "description": "专门处理图结构数据的神经网络，通过消息传递聚合邻居节点信息",
            "category_name": "图神经网络",
            "difficulty": "advanced",
            "tags": ["深度学习", "图", "GNN", "消息传递"],
            "paper_url": "https://arxiv.org/abs/1812.08434",
            "code_url": "https://pytorch-geometric.readthedocs.io/",
            "visualization_data": {
                "type": "gnn_visualization",
                "description": "Graph Neural Network message passing visualization",
                "interactive": True,
                "steps": [
                    "Show graph structure",
                    "Visualize node features",
                    "Demonstrate message passing",
                    "Show node embedding updates",
                    "Display graph-level predictions",
                ],
            },
        },
        {
            "name": "t-SNE",
            "chinese_name": "t-分布随机邻域嵌入",
            "description": "将高维数据降维到2D或3D空间进行可视化，保持局部结构",
            "category_name": "降维算法",
            "difficulty": "intermediate",
            "tags": ["降维", "可视化", "无监督学习", "非线性"],
            "paper_url": "https://www.jmlr.org/papers/v9/vandermaaten08a.html",
            "code_url": (
                "https://scikit-learn.org/stable/modules/generated/"
                "sklearn.manifold.TSNE.html"
            ),
            "visualization_data": {
                "type": "tsne_visualization",
                "description": "t-SNE dimensionality reduction visualization",
                "interactive": True,
                "steps": [
                    "Generate high-dimensional data",
                    "Apply t-SNE algorithm",
                    "Visualize 2D embedding",
                    "Show perplexity parameter effects",
                    "Compare with other methods",
                ],
            },
        },
    ]

    for alg_data in algorithms_data:
        category = AlgorithmCategory.query.filter_by(
            name=alg_data["category_name"]
        ).first()
        if not category:
            continue

        algorithm = Algorithm(
            name=alg_data["name"],
            chinese_name=alg_data["chinese_name"],
            description=alg_data["description"],
            category_id=category.id,
            difficulty=alg_data["difficulty"],
            tags=alg_data["tags"],
            paper_url=alg_data["paper_url"],
            code_url=alg_data["code_url"],
            code_example=alg_data.get("code_example", ""),
            visualization_data=alg_data["visualization_data"],
        )
        db.session.add(algorithm)

    db.session.commit()
    print("算法数据初始化完成")


def init_sample_posts():
    """初始化示例帖子"""
    # 创建示例用户
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(username="admin", email="admin@example.com")
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.commit()

    # 获取一些算法ID
    cnn_alg = Algorithm.query.filter_by(name="Convolutional Neural Network").first()
    rnn_alg = Algorithm.query.filter_by(name="Recurrent Neural Network").first()
    kmeans_alg = Algorithm.query.filter_by(name="K-Means Clustering").first()

    posts_data = [
        {
            "title": "CNN在图像分类中的应用心得",
            "content": """最近在做图像分类项目，用CNN取得了不错的效果。

主要收获：
1. 数据预处理很重要，适当的数据增强可以显著提升模型性能
2. ResNet结构比简单的CNN有更好的梯度传播特性
3. Batch Normalization能加速训练并提高稳定性

分享一些代码片段和实验结果...""",
            "algorithm_ids": [cnn_alg.id] if cnn_alg else [],
        },
        {
            "title": "LSTM处理时间序列数据的最佳实践",
            "content": """在处理股票价格预测时，LSTM的表现比传统方法好很多。

关键点：
1. 选择合适的时间窗口长度
2. 处理好序列数据的padding
3. 使用双向LSTM可以捕捉更多上下文信息
4. 适当的dropout可以防止过拟合

附上我的模型架构和训练代码...""",
            "algorithm_ids": [rnn_alg.id] if rnn_alg else [],
        },
        {
            "title": "K-means聚类算法的参数选择技巧",
            "content": """K-means虽然简单，但参数选择对结果影响很大。

经验总结：
1. 如何选择合适的K值（肘部法则、轮廓系数）
2. 不同的初始化方法对结果的影响
3. 处理高维数据的技巧
4. 聚类结果的评估方法

欢迎大家讨论交流！""",
            "algorithm_ids": [kmeans_alg.id] if kmeans_alg else [],
        },
        {
            "title": "机器学习算法选择指南",
            "content": """对于不同类型的问题，应该选择什么样的算法？

分类问题：
- 小数据集：朴素贝叶斯、决策树
- 大数据集：SVM、随机森林、神经网络

回归问题：
- 线性关系：线性回归
- 非线性关系：多项式回归、SVR、神经网络

聚类问题：
- 球形簇：K-means
- 任意形状：DBSCAN、层次聚类

分享一些选择算法的实用经验...""",
            "algorithm_ids": [],
        },
        {
            "title": "深度学习模型调参经验分享",
            "content": """调参真的是门手艺，需要大量的实践经验。

学习率：
- 从小开始，逐步增大
- 使用学习率调度器
- Adam通常比SGD收敛更快

正则化：
- Dropout在不同层设置不同比例
- L2正则化系数通常设为1e-4到1e-2
- Batch Normalization通常放在激活函数前

数据方面：
- 数据增强至关重要
- 交叉验证评估模型性能
- 监控训练和验证loss的差距

一些具体的调参案例...""",
            "algorithm_ids": [],
        },
    ]

    for post_data in posts_data:
        post = Post(
            title=post_data["title"],
            content=post_data["content"],
            author_id=admin_user.id,
            is_featured=len(post_data["algorithm_ids"]) > 0,  # 有算法关联的设为精华帖
        )
        db.session.add(post)
        db.session.flush()  # 获取post.id

        # 关联算法
        for alg_id in post_data["algorithm_ids"]:
            alg_post = AlgorithmPost(algorithm_id=alg_id, post_id=post.id)
            db.session.add(alg_post)

    db.session.commit()
    print("示例帖子初始化完成")


def main():
    app = create_app()
    with app.app_context():
        print("开始初始化数据库...")

        # 初始化分类
        init_categories()

        # 清除重复算法数据
        clear_duplicate_algorithms()

        # 初始化算法
        init_algorithms()

        # 初始化示例帖子
        # 创建示例用户
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(username="admin", email="admin@example.com")
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            db.session.commit()

        # 获取一些算法ID
        cnn_alg = Algorithm.query.filter_by(name="Convolutional Neural Network").first()
        rnn_alg = Algorithm.query.filter_by(name="Recurrent Neural Network").first()
        kmeans_alg = Algorithm.query.filter_by(name="K-Means Clustering").first()

        posts_data = [
            {
                "title": "CNN在图像分类中的应用心得",
                "content": """最近在做图像分类项目，用CNN取得了不错的效果。

主要收获：
1. 数据预处理很重要，适当的数据增强可以显著提升模型性能
2. ResNet结构比简单的CNN有更好的梯度传播特性
3. Batch Normalization能加速训练并提高稳定性

分享一些代码片段和实验结果...""",
                "algorithm_ids": [cnn_alg.id] if cnn_alg else [],
            },
            {
                "title": "LSTM处理时间序列数据的最佳实践",
                "content": """在处理股票价格预测时，LSTM的表现比传统方法好很多。

关键点：
1. 选择合适的时间窗口长度
2. 处理好序列数据的padding
3. 使用双向LSTM可以捕捉更多上下文信息
4. 适当的dropout可以防止过拟合

附上我的模型架构和训练代码...""",
                "algorithm_ids": [rnn_alg.id] if rnn_alg else [],
            },
            {
                "title": "K-means聚类算法的参数选择技巧",
                "content": """K-means虽然简单，但参数选择对结果影响很大。

经验总结：
1. 如何选择合适的K值（肘部法则、轮廓系数）
2. 不同的初始化方法对结果的影响
3. 处理高维数据的技巧
4. 聚类结果的评估方法

欢迎大家讨论交流！""",
                "algorithm_ids": [kmeans_alg.id] if kmeans_alg else [],
            },
            {
                "title": "机器学习算法选择指南",
                "content": """对于不同类型的问题，应该选择什么样的算法？

分类问题：
- 小数据集：朴素贝叶斯、决策树
- 大数据集：SVM、随机森林、神经网络

回归问题：
- 线性关系：线性回归
- 非线性关系：多项式回归、SVR、神经网络

聚类问题：
- 球形簇：K-means
- 任意形状：DBSCAN、层次聚类

分享一些选择算法的实用经验...""",
                "algorithm_ids": [],
            },
            {
                "title": "深度学习模型调参经验分享",
                "content": """调参真的是门手艺，需要大量的实践经验。

学习率：
- 从小开始，逐步增大
- 使用学习率调度器
- Adam通常比SGD收敛更快

正则化：
- Dropout在不同层设置不同比例
- L2正则化系数通常设为1e-4到1e-2
- Batch Normalization通常放在激活函数前

数据方面：
- 数据增强至关重要
- 交叉验证评估模型性能
- 监控训练和验证loss的差距

一些具体的调参案例...""",
                "algorithm_ids": [],
            },
        ]

        for post_data in posts_data:
            post = Post(
                title=post_data["title"],
                content=post_data["content"],
                author_id=admin_user.id,
                is_featured=len(post_data["algorithm_ids"])
                > 0,  # 有算法关联的设为精华帖
            )
            db.session.add(post)
            db.session.flush()  # 获取post.id

            # 关联算法
            for alg_id in post_data["algorithm_ids"]:
                alg_post = AlgorithmPost(algorithm_id=alg_id, post_id=post.id)
                db.session.add(alg_post)

        db.session.commit()
        print("示例帖子初始化完成")

        print("数据库初始化完成！")


if __name__ == "__main__":
    main()
