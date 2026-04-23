from sklearn import svm
import joblib
import os

# 1. Feature Engineering: [Failed_Attempts, Time_Gap_Seconds]
# [1, 60] -> 1 fail in a minute (Normal)
# [10, 2] -> 10 fails every 2 seconds (Attack!)
X = [[1, 60], [2, 45], [1, 30], [8, 3], [12, 1], [15, 2], [2, 90]]
y = [0, 0, 0, 1, 1, 1, 0] # 0 = Normal, 1 = Intrusion

# 2. Train the SVM (Lightweight Linear Kernel)
clf = svm.SVC(kernel='linear', probability=True)
clf.fit(X, y)

# 3. Save the model for Portability
model_path = os.path.join(os.path.dirname(__file__), 'intrusion_model.pkl')
joblib.dump(clf, model_path)

print(f"[+] SVM Brain trained successfully and saved to: {model_path}")