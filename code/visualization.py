from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Reduce dimensions
pca = PCA(n_components=2)
reduced_embeddings = pca.fit_transform(embeddings)

# Plot
plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1])

for i, app in enumerate(app_names):
    plt.annotate(app, (reduced_embeddings[i, 0], reduced_embeddings[i, 1]))

plt.show()
