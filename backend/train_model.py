import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def generate_training_data():
    """Generate synthetic training data for skill level prediction"""
    np.random.seed(42)
    
    data = []
    
    # Beginner data (0-40% score, slower time)
    for _ in range(300):
        score = np.random.randint(0, 5)  # 0-4 correct out of 10
        total_questions = 10
        avg_time = np.random.uniform(45, 90)  # 45-90 seconds per question
        data.append([score, total_questions, avg_time, score/total_questions, "Beginner"])
    
    # Intermediate data (40-75% score, moderate time)
    for _ in range(300):
        score = np.random.randint(4, 8)  # 4-7 correct out of 10
        total_questions = 10
        avg_time = np.random.uniform(25, 50)  # 25-50 seconds per question
        data.append([score, total_questions, avg_time, score/total_questions, "Intermediate"])
    
    # Expert data (75-100% score, fast time)
    for _ in range(300):
        score = np.random.randint(7, 11)  # 7-10 correct out of 10
        total_questions = 10
        avg_time = np.random.uniform(10, 30)  # 10-30 seconds per question
        data.append([score, total_questions, avg_time, score/total_questions, "Expert"])
    
    df = pd.DataFrame(data, columns=['correct_answers', 'total_questions', 'avg_time', 'accuracy', 'skill_level'])
    return df

def train_skill_predictor():
    """Train and save the skill level prediction model"""
    print("[INFO] Generating training data...")
    df = generate_training_data()
    
    # Features and target
    X = df[['correct_answers', 'total_questions', 'avg_time', 'accuracy']]
    y = df['skill_level']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    print("[INFO] Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"[SUCCESS] Model training complete!")
    print(f"[INFO] Model accuracy: {accuracy:.2f}")
    print(f"[INFO] Classification report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'skill_predictor_model.pkl')
    joblib.dump(model, model_path)
    print(f"[SUCCESS] Model saved to: {model_path}")
    
    return model

if __name__ == "__main__":
    train_skill_predictor()