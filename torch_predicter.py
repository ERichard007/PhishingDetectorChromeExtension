import torch
import torch.nn as nn

import joblib as jb

import os


class torch_predicter:
    """
    Deep learning model trained with PyTorch
    """
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        model_path = os.path.join(base_dir, "assets", "models", "deeplearning_model.pth")
        vectorizer_path = os.path.join(base_dir, "assets", "vectorizers", "deeplearning_vectorizer.pkl")
        metadata_path = os.path.join(base_dir, "assets", "metadata", "deeplearning_metadata.pth")

        self.metadata = torch.load(metadata_path)

        self.width = self.metadata['width']
        self.depth = self.metadata['depth']
        self.dropout = self.metadata['dropout']
        self.input_size = self.metadata['input_size']
        self.acc = self.metadata['val_acc']

        self.vectorizer = jb.load(vectorizer_path)
        self.model = PhishingNN(input_size=self.input_size, width=self.width, depth=self.depth, dropout=self.dropout)

        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def predict(self, subject : str, body : str) -> dict:
        """
        Public method that takes an email's subject and body as input and returns a prediction indicating whether the email is phishing or not.
        Args:
            subject (str): The subject of the email.
            body (str): The body content of the email.
        Returns:
            dict: A dictionary containing the prediction (1 for phishing, 0 for not phishing) and the probability of the prediction.
        """
        text = subject + ' ' + body

        X = self.vectorizer.transform([text])
        X_tensor = torch.tensor(X.toarray(), dtype=torch.float32)

        with torch.no_grad():
            output = self.model(X_tensor)

        prob_phishing = torch.sigmoid(output).item()
        prob_safe = 1 - prob_phishing
        prediction = 1 if prob_phishing >= 0.5 else 0

        print("torch_trainer: Prediction made successfully!")

        return {
            "prediction": int(prediction),
            "probability_phishing": float(prob_phishing),
            "probability_safe": float(prob_safe),
            "Accuracy": float(self.acc),
        }
    
class PhishingNN(nn.Module):
    """
    Defines the architecture of the neural network.
    Args:
        input_size (int): The size of the input layer (number of features).
        width (int): The number of neurons in each hidden layer.
        depth (int): The number of hidden layers in the network.
        dropout (float): The dropout rate for regularization.
    """
    def __init__(self, input_size : int, width : int, depth : int, dropout : float):
        super().__init__()

        layers = []

        # input layer
        layers.append(nn.Linear(input_size, width))
        layers.append(nn.GELU())
        layers.append(nn.Dropout(dropout))

        # hidden layers
        for _ in range(depth - 1):
            layers.append(nn.Linear(width, width))
            layers.append(nn.GELU())
            layers.append(nn.Dropout(dropout))

        # output layer
        layers.append(nn.Linear(width, 1))

        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)