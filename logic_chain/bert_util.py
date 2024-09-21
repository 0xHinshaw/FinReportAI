import torch
from transformers import BertTokenizer, BertModel
from scipy.spatial.distance import cosine
from utils import timeit

# Check if CUDA is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load pre-trained BERT tokenizer and model on the selected device
pretrain_model_name = 'bert-base-chinese'
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = BertModel.from_pretrained('bert-base-chinese').to(device)

# from transformers import AutoModel, AutoTokenizer
# pretrain_model_name = 'uer/roberta-base-finetuned-chinanews-chinese'
# tokenizer = AutoTokenizer.from_pretrained(pretrain_model_name)
# model = AutoModel.from_pretrained(pretrain_model_name).to(device)

@timeit
def get_similarity(sent1, sents):
    # Tokenize and encode sent1 on the selected device
    inputs1 = tokenizer(sent1, return_tensors='pt', padding=True, truncation=True, max_length=512).to(device)
    with torch.no_grad():
        outputs1 = model(**inputs1)
    embeddings1 = outputs1.last_hidden_state.mean(dim=1)  # Mean pooling to get sentence embedding

    # Tokenize and encode sents on the selected device
    encoded_sents = []
    for sent in sents:
        inputs = tokenizer(sent, return_tensors='pt', padding=True, truncation=True, max_length=512).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean pooling to get sentence embedding
        encoded_sents.append(embeddings)

    # Calculate cosine similarity between sent1 and sents
    similarities = []
    for encoded_sent in encoded_sents:
        similarity = 1 - cosine(embeddings1.cpu().flatten(), encoded_sent.cpu().flatten())
        similarities.append(similarity.item())

    return similarities
