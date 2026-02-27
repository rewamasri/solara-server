import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# 1. Load the data
df = pd.read_csv('mock_rover_sustainability_data.csv')

# 2. Select features (excluding non-numeric metadata like timestamp)
features = ['ambient_temp_c', 'surface_temp_avg_c', 'humidity_pct', 'lux', 'soil_moisture_pct']
x = df[features]

# 3. Scale the data (Crucial for K-means!)
scaler = StandardScaler()
x_scaled = scaler.fit_transform(x)

# 4. Determine K using the Elbow Method
inertia = []
K_range = range(1, 10)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10) # Added n_init here
    km.fit(x_scaled)
    inertia.append(km.inertia_)

# Plot the Elbow
plt.plot(K_range, inertia, 'bx-')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method For Optimal k')
plt.show()



from sklearn.metrics import silhouette_score

# Calculate score for k=2
score_2 = silhouette_score(x_scaled, KMeans(n_clusters=2, n_init=10).fit_predict(x_scaled))
# Calculate score for k=3
score_3 = silhouette_score(x_scaled, KMeans(n_clusters=3, n_init=10).fit_predict(x_scaled))

print(f"Silhouette Score for k=2: {score_2}")
print(f"Silhouette Score for k=3: {score_3}")



# Assuming the elbow was at k=2 (based on your silhouette scores)
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10) # Added n_init here
df['cluster_label'] = kmeans.fit_predict(x_scaled)        # Use fit_predict, not fit_transform

# View the characteristics of each cluster
print(df.groupby('cluster_label')[features].mean())
