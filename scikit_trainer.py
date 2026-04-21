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

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.training_dir = os.path.normpath(os.path.join(self.base_dir, "assets", "training_sets", "SevenPhishingEmails"))

        if os.path.exists('scikit_vectorizer.pkl') and os.path.exists('scikit_model.pkl'):
            self.vectorizer = jl.load('scikit_vectorizer.pkl')
            self.classifier = jl.load('scikit_model.pkl')
        else:
            self.vectorizer = TfidfVectorizer()
            self.classifier = MultinomialNB() 

            #print("BASE DIR:", base_dir)
            #print("FINAL PATH:", ling_path)
            #print("EXISTS?:", os.path.exists(ling_path))

            self._clean_dataset()
            #self._train()

    def _clean_dataset(self) -> None:
        """
        Private method to clean training sets prior to training the model
        """

        dataframes = []

        for file in os.listdir(self.training_dir):
            print(file)
            if file.endswith('.csv'):
                print(f"{file} ENDS WITH CSV!")
                file_path = os.path.join(self.training_dir, file)

                df = pd.read_csv(file_path)

                dataframes.append(df)

        combined_df = pd.concat(dataframes,ignore_index=True)

        combined_df.drop_duplicates(inplace=True)
        
        cleaned_file_path = os.path.join(self.base_dir, "assets", "cleaned_data", "scikit_cleaned.csv")
        combined_df.to_csv(cleaned_file_path, index=False)

        #add a column with name of original file

        print(f"Data has been cleaned to {cleaned_file_path} \n DATA --> \n {combined_df.info()} \n MISSING --> \n {combined_df.isnull().sum()}")

    def _train(self) -> None:
        """
        Private method that trains the model using the provided CSV file.
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


