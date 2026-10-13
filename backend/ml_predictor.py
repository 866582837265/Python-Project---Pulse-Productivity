# ML predictor for skill level assessment
class MLPredictor:
    def __init__(self):
        self.model_loaded = False
    
    def load_model(self):
        """Load the ML model"""
        self.model_loaded = True
        print("[ML] Predictor model loaded")
    
    def predict_skill_level(self, correct_answers, total_questions, avg_time):
        """Predict skill level based on quiz performance"""
        if total_questions == 0:
            return "Beginner"
        
        accuracy = correct_answers / total_questions
        
        # Simple rule-based prediction
        if accuracy >= 0.8 and avg_time <= 20:
            return "Expert"
        elif accuracy >= 0.6 and avg_time <= 30:
            return "Intermediate"
        else:
            return "Beginner"

# Global instance
predictor = MLPredictor()