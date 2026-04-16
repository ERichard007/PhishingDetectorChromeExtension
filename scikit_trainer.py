from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib as jl
import pandas as pd

import os

# Dataset used for training the model:
# Champa, Arifa Islam; Rabbi, Md Fazle (2024). Seven Phishing Email Datasets. 
# figshare. Dataset. https://doi.org/10.6084/m9.figshare.25432108.v1

class scikit_trainer:
    """
    Machine learning model trained with scikit-learn 
    using the Multinomial Naive Bayes algorithm and TF-IDF vectorization 
    On Champa, Arifa Islam; Rabbi, Md Fazle (2024). Seven Phishing Email Datasets. figshare. Dataset. https://doi.org/10.6084/m9.figshare.25432108.v1
    """
    def __init__(self):

        if os.path.exists('scikit_vectorizer.pkl') and os.path.exists('scikit_model.pkl'):
            self.vectorizer = jl.load('scikit_vectorizer.pkl')
            self.classifier = jl.load('scikit_model.pkl')
        else:
            self.vectorizer = TfidfVectorizer()
            self.classifier = MultinomialNB() 

            base_dir = os.path.dirname(os.path.abspath(__file__))
            ling_path = os.path.normpath(os.path.join(base_dir, "assets", "training_sets", "SevenPhishingEmails", "Ling.csv"))

            print("BASE DIR:", base_dir)
            print("FINAL PATH:", ling_path)
            print("EXISTS?:", os.path.exists(ling_path))

            self._train(ling_path)

    def _train(self, csv_file : str) -> None:
        """
        Private method that trains the model using the provided CSV file.
        Args:
            csv_file (str): Path to the CSV file containing the training data.
            The CSV file should have the following columns:
                - 'subject': The subject of the email.
                - 'body': The body content of the email.
                - 'label': The label indicating whether the email is phishing (1) or not (0).
        """

        df = pd.read_csv(csv_file)

        texts = (df['subject'].fillna('') + ' ' + df['body'].fillna(''))
        labels = df['label']

        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)

        jl.dump(self.classifier, 'scikit_model.pkl')
        jl.dump(self.vectorizer, 'scikit_vectorizer.pkl')

        print("scikit_trainer: Model trained successfully!")

    def predict(self, subject : str, body : str) -> dict:
        """
        Public method that takes an email's subject and body as input and returns a prediction indicating whether the email is phishing or not.
        Args:
            subject (str): The subject of the email.
            body (str): The body content of the email.
        Returns:
            tuple[int, float]: A tuple containing the prediction (1 for phishing, 0 for not phishing) and the probability of the prediction.
        """

        text = subject + ' ' + body

        X = self.vectorizer.transform([text])

        prediction = self.classifier.predict(X)[0]
        print("Prediction:", prediction)
        pred_prob = self.classifier.predict_proba(X)[0]
        print("Prediction probabilities:", pred_prob)

        feature_names = self.vectorizer.get_feature_names_out()
        print("Feature names:", feature_names)

        tdidf_values = X.toarray()[0]
        print("TF-IDF values:", tdidf_values)

        phishing_weights = self.classifier.feature_log_prob_[1]
        print("Phishing weights:", phishing_weights)

        contributions = tdidf_values * phishing_weights
        print("Contributions:", contributions)

        top_indices = contributions.argsort()[::-1][:10]
        print ("Top contributing feature indices:", top_indices)

        explanation = [
            {
                "word": feature_names[i],
                "contribution": float(contributions[i])
            }
            for i in top_indices if contributions[i] > 0
        ]
        print("Explanation:", explanation)
        
        print("scikit_trainer: Prediction made successfully!")

        return {
            "prediction": int(prediction), 
            "probability": float(pred_prob[1]), 
            "explanation": explanation
            }


