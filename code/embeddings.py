from transformers import LlamaTokenizer, LlamaModel
import torch
import pandas as pd
import numpy as np

# Initialize tokenizer and model
tokenizer = LlamaTokenizer.from_pretrained('llama-base')
model = LlamaModel.from_pretrained('llama-base')

# Read app names from a CSV file
# Assuming the CSV file is named 'app_names.csv' and has no header
df = pd.read_csv('data/app_names.csv', header=None)
app_names = df[0].tolist()

# Get embeddings
embeddings = []
for app in app_names:
    inputs = tokenizer(app, return_tensors='pt')
    outputs = model(**inputs)
    # Use the last hidden state of the first token (e.g., CLS token)
    embedding = outputs.last_hidden_state[:, 0, :].detach().numpy()
    embeddings.append(embedding)

# Convert list to array for analysis
embeddings = np.array(embeddings).squeeze()
