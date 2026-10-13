# ml_progress_analyzer.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime, timedelta
import json

class CodingProgressAnalyzer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'total_problems', 'easy_problems', 'medium_problems', 'hard_problems',
            'leetcode_ranking', 'hackerrank_stars', 'weekly_activity', 'consistency_score',
            'difficulty_progression', 'platform_diversity', 'recent_activity_trend'
        ]
        
    def extract_features(self, leetcode_data, hackerrank_data, historical_data=None):
        """Extract ML features from platform data"""
        features = {}
        
        # LeetCode features
        if leetcode_data and leetcode_data.get('success'):
            solved = leetcode_data.get('solved_problems', {})
            features['total_problems'] = solved.get('total', 0)
            features['easy_problems'] = solved.get('easy', 0)
            features['medium_problems'] = solved.get('medium', 0)
            features['hard_problems'] = solved.get('hard', 0)
            features['leetcode_ranking'] = min(leetcode_data.get('ranking', 1000000), 1000000)
            features['weekly_activity'] = leetcode_data.get('weekly_solved', 0)
        else:
            features.update({
                'total_problems': 0, 'easy_problems': 0, 'medium_problems': 0,
                'hard_problems': 0, 'leetcode_ranking': 1000000, 'weekly_activity': 0
            })
        
        # HackerRank features
        if hackerrank_data and hackerrank_data.get('success'):
            features['hackerrank_stars'] = hackerrank_data.get('scores', {}).get('total_score', 0) // 10
        else:
            features['hackerrank_stars'] = 0
        
        # Advanced features
        features['consistency_score'] = self._calculate_consistency(historical_data)
        features['difficulty_progression'] = self._calculate_difficulty_progression(features)
        features['platform_diversity'] = 1 if features['total_problems'] > 0 and features['hackerrank_stars'] > 0 else 0
        features['recent_activity_trend'] = self._calculate_activity_trend(historical_data)
        
        return features
    
    def _calculate_consistency(self, historical_data):
        """Calculate consistency score based on historical activity"""
        if not historical_data or len(historical_data) < 7:
            return 0.5
        
        # Calculate daily activity variance (lower variance = higher consistency)
        daily_activity = [day.get('problems_solved', 0) for day in historical_data[-30:]]
        if len(daily_activity) < 7:
            return 0.5
        
        variance = np.var(daily_activity)
        mean_activity = np.mean(daily_activity)
        
        if mean_activity == 0:
            return 0
        
        # Normalize consistency score (0-1, higher is better)
        consistency = max(0, 1 - (variance / (mean_activity + 1)))
        return min(consistency, 1.0)
    
    def _calculate_difficulty_progression(self, features):
        """Calculate how well user progresses through difficulty levels"""
        total = features['total_problems']
        if total == 0:
            return 0
        
        easy_ratio = features['easy_problems'] / total
        medium_ratio = features['medium_problems'] / total
        hard_ratio = features['hard_problems'] / total
        
        # Ideal progression: balanced with increasing difficulty
        ideal_progression = 0.4 * easy_ratio + 0.6 * medium_ratio + 1.0 * hard_ratio
        return min(ideal_progression, 1.0)
    
    def _calculate_activity_trend(self, historical_data):
        """Calculate recent activity trend (increasing/decreasing)"""
        if not historical_data or len(historical_data) < 14:
            return 0.5
        
        recent_activity = [day.get('problems_solved', 0) for day in historical_data[-14:]]
        older_activity = [day.get('problems_solved', 0) for day in historical_data[-28:-14]]
        
        if len(older_activity) < 7:
            return 0.5
        
        recent_avg = np.mean(recent_activity)
        older_avg = np.mean(older_activity)
        
        if older_avg == 0:
            return 1.0 if recent_avg > 0 else 0.5
        
        trend = recent_avg / older_avg
        return min(max(trend / 2, 0), 1.0)  # Normalize to 0-1
    
    def generate_synthetic_training_data(self, n_samples=1000):
        """Generate synthetic training data for the model"""
        np.random.seed(42)
        
        data = []
        for _ in range(n_samples):
            # Generate realistic feature combinations
            total_problems = np.random.exponential(50)
            
            # Difficulty distribution (beginners solve more easy, experts more hard)
            skill_level = np.random.uniform(0, 1)
            easy_ratio = max(0.1, 0.8 - skill_level * 0.6)
            hard_ratio = min(0.4, skill_level * 0.5)
            medium_ratio = 1 - easy_ratio - hard_ratio
            
            features = {
                'total_problems': total_problems,
                'easy_problems': total_problems * easy_ratio,
                'medium_problems': total_problems * medium_ratio,
                'hard_problems': total_problems * hard_ratio,
                'leetcode_ranking': np.random.exponential(100000),
                'hackerrank_stars': np.random.poisson(3),
                'weekly_activity': np.random.poisson(5),
                'consistency_score': np.random.beta(2, 2),
                'difficulty_progression': skill_level + np.random.normal(0, 0.1),
                'platform_diversity': np.random.choice([0, 1], p=[0.3, 0.7]),
                'recent_activity_trend': np.random.beta(2, 2)
            }
            
            # Calculate target progress score (0-100)
            progress_score = self._calculate_target_score(features)
            
            data.append({**features, 'progress_score': progress_score})
        
        return pd.DataFrame(data)
    
    def _calculate_target_score(self, features):
        """Calculate target progress score for training"""
        # Weighted combination of factors
        weights = {
            'volume': 0.25,      # Total problems solved
            'difficulty': 0.20,   # Difficulty progression
            'consistency': 0.15,  # Regular practice
            'ranking': 0.15,      # Platform ranking
            'activity': 0.15,     # Recent activity
            'diversity': 0.10     # Multi-platform usage
        }
        
        # Volume score (0-25)
        volume_score = min(features['total_problems'] / 200 * 25, 25)
        
        # Difficulty score (0-20)
        difficulty_score = features['difficulty_progression'] * 20
        
        # Consistency score (0-15)
        consistency_score = features['consistency_score'] * 15
        
        # Ranking score (0-15, inverse of ranking)
        ranking_score = max(0, 15 - (features['leetcode_ranking'] / 100000 * 15))
        
        # Activity score (0-15)
        activity_score = min(features['weekly_activity'] / 10 * 15, 15)
        
        # Diversity score (0-10)
        diversity_score = features['platform_diversity'] * 10
        
        total_score = (volume_score + difficulty_score + consistency_score + 
                      ranking_score + activity_score + diversity_score)
        
        return min(max(total_score, 0), 100)
    
    def train_model(self):
        """Train the progress analysis model"""
        print("Training progress analysis model...")
        
        # Generate training data
        df = self.generate_synthetic_training_data(2000)
        
        # Prepare features and target
        X = df[self.feature_names].values
        y = df['progress_score'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Model trained - Train R2: {train_score:.3f}, Test R2: {test_score:.3f}")
        
        self.is_trained = True
        return train_score, test_score
    
    def predict_progress_score(self, leetcode_data, hackerrank_data, historical_data=None):
        """Predict overall progress score"""
        if not self.is_trained:
            self.train_model()
        
        # Extract features
        features = self.extract_features(leetcode_data, hackerrank_data, historical_data)
        
        # Prepare for prediction
        feature_vector = np.array([[features[name] for name in self.feature_names]])
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # Predict
        progress_score = self.model.predict(feature_vector_scaled)[0]
        progress_score = max(0, min(100, progress_score))
        
        # Generate detailed breakdown
        breakdown = self._generate_score_breakdown(features, progress_score)
        
        return {
            'overall_score': round(progress_score, 1),
            'breakdown': breakdown,
            'features': features,
            'level': self._determine_skill_level(progress_score),
            'recommendations': self._generate_recommendations(features, progress_score)
        }
    
    def _generate_score_breakdown(self, features, total_score):
        """Generate detailed score breakdown"""
        return {
            'problem_solving': min(features['total_problems'] / 200 * 25, 25),
            'difficulty_mastery': features['difficulty_progression'] * 20,
            'consistency': features['consistency_score'] * 15,
            'platform_ranking': max(0, 15 - (features['leetcode_ranking'] / 100000 * 15)),
            'recent_activity': min(features['weekly_activity'] / 10 * 15, 15),
            'platform_diversity': features['platform_diversity'] * 10
        }
    
    def _determine_skill_level(self, score):
        """Determine skill level based on score"""
        if score >= 80:
            return "Expert"
        elif score >= 60:
            return "Advanced"
        elif score >= 40:
            return "Intermediate"
        elif score >= 20:
            return "Beginner"
        else:
            return "Novice"
    
    def _generate_recommendations(self, features, score):
        """Generate personalized recommendations"""
        recommendations = []
        
        if features['weekly_activity'] < 3:
            recommendations.append("Increase weekly problem-solving frequency to 5+ problems")
        
        if features['difficulty_progression'] < 0.3:
            recommendations.append("Challenge yourself with more medium and hard problems")
        
        if features['consistency_score'] < 0.5:
            recommendations.append("Maintain regular daily practice for better consistency")
        
        if features['platform_diversity'] == 0:
            recommendations.append("Explore multiple platforms to diversify your skills")
        
        if features['total_problems'] < 50:
            recommendations.append("Focus on building problem-solving volume")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def save_model(self, filepath='ml_progress_model.pkl'):
        """Save trained model"""
        if self.is_trained:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }, filepath)
            print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='ml_progress_model.pkl'):
        """Load trained model"""
        try:
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data['feature_names']
            self.is_trained = True
            print(f"Model loaded from {filepath}")
            return True
        except FileNotFoundError:
            print(f"Model file {filepath} not found, will train new model")
            return False

# Global instance
progress_analyzer = CodingProgressAnalyzer()