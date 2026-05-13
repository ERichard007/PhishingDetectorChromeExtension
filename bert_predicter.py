import torch
import torch.nn as nn

from transformers import BertTokenizer, BertModel

import os


class BertClassifier(nn.Module):

    def __init__(self):
        super().__init__()

        self.bert = BertModel.from_pretrained('bert-base-uncased')

        self.dropout = nn.Dropout(0.1)

        self.fc = nn.Linear(768, 1)

    def forward(self, input_ids, attention_mask):

        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        cls_embedding = outputs.last_hidden_state[:, 0, :]

        x = self.dropout(cls_embedding)

        x = self.fc(x)

        return x


class bert_predicter:

    def __init__(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))

        model_path = os.path.join(base_dir, "assets/models/bert_model.pth")
        metadata_path = os.path.join(base_dir, "assets/metadata/bert_metadata.pth")
        tokenizer_path = os.path.join(base_dir, "assets/tokenizers/bert_tokenizer")

        self.metadata = torch.load(metadata_path)
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_path)

        self.model = BertClassifier()
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))

        self.model.eval()

    def predict(self, subject, body):

        text = subject + " " + body

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors='pt'
        )

        with torch.no_grad():

            output = self.model(
                encoding['input_ids'],
                encoding['attention_mask']
            )

        print(output.item())
        print(torch.sigmoid(output).item())

        prob_phishing = torch.sigmoid(output).item()

        prediction = 1 if prob_phishing >= 0.5 else 0

        return {
            "prediction": prediction,
            "probability_phishing": prob_phishing,
            "probability_safe": 1 - prob_phishing,
            "Accuracy": self.metadata["test_accuracy"]
        }