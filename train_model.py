import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

print("Đang đọc dữ liệu từ CSV...")
df = pd.read_csv('gesture_dataset.csv')

X = df.drop('label', axis=1)
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("AI đang học... (Random Forest)")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred) * 100
print(f"====> ĐỘ CHÍNH XÁC CỦA AI: {accuracy:.2f}% <====")

joblib.dump(model, 'gesture_model.pkl')
print("Đã lưu bộ não AI thành công vào file 'gesture_model.pkl'!")