import os

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

tokenizer = AutoTokenizer.from_pretrained('tamu_features/rec_model')
model = AutoModelForSequenceClassification.from_pretrained('tamu_features/rec_model')
toLabel={0:'Target Sentiment Not Found',1:'Positive-Consistent',2:'Negative-Inconsistent'}

class Sentiment():
    def __init__(self):
        self.tokenizer = tokenizer
        self.model = model
        self.toLabel={0:'Target Sentiment Not Found',1:'Positive-Consistent',2:'Negative-Inconsistent'}
        
    def classify(self,text):
        inputs = self.tokenizer(text, return_tensors="pt")
        logits = self.model(**inputs)[0]
        result = torch.softmax(logits, dim=1).tolist()[0]
        return self.toLabel[np.argmax(result)]