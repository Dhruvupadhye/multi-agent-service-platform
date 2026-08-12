import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

def train_and_save_model():
    # Sample Dataset for Spam Classification
    data = [
        ("Win a $1000 Amazon gift card now! Click here", "spam"),
        ("Claim your free lottery prize immediately", "spam"),
        ("Urgent: Production DB connection latency issue", "important"),
        ("Q3 Financial Report and Board Meeting Agenda", "important"),
        ("Invoice #9082 payment overdue notice", "important"),
        ("Hey, are we still getting coffee today?", "casual"),
        ("Check out this funny meme I found", "casual"),
        ("Team lunch on Friday discussion", "casual")
    ]

    texts, labels = zip(*data)

    # Scikit-Learn Pipeline: TF-IDF Extraction + Multinomial Naive Bayes
    pipeline = make_pipeline(TfidfVectorizer(), MultinomialNB())
    pipeline.fit(texts, labels)

    os.makedirs("app/models", exist_ok=True)
    model_path = "app/models/spam_classifier.pkl"
    joblib.dump(pipeline, model_path)
    print(f"ML Classifier trained and saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()