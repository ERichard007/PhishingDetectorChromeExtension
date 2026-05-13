import joblib as jl
import os

# Dataset used for training the model:
# Champa, Arifa Islam; Rabbi, Md Fazle (2024). Seven Phishing Email Datasets. 
# figshare. Dataset. https://doi.org/10.6084/m9.figshare.25432108.v1

class scikit_predicter:
    """
    Machine learning model trained with scikit-learn 
    using the Random Forest algorithm and TF-IDF vectorization 
    On Champa, Arifa Islam; Rabbi, Md Fazle (2024). Seven Phishing Email Datasets. figshare. Dataset. https://doi.org/10.6084/m9.figshare.25432108.v1
    """
    def __init__(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(base_dir)
        self.model = jl.load(os.path.join(base_dir, "assets", "models", "scikit_model.pkl"))
        self.vectorizer = jl.load(os.path.join(base_dir, "assets", "vectorizers", "scikit_vectorizer.pkl"))
        self.metadata = jl.load(os.path.join(base_dir, "assets", "metadata", "scikit_metadata.pkl"))

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

        prediction = self.model.predict(X)[0]
        probs = self.model.predict_proba(X)[0]

        print("scikit_trainer: Prediction made successfully!")

        return {
            "prediction": int(prediction),
            "probability_phishing": float(probs[1]),
            "probability_safe": float(probs[0]),
            "Accuracy": float(self.metadata["test_accuracy"])
        }


