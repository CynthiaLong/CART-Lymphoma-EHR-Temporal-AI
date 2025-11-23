import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random
import numpy as np


# model architecture
class LSTMClassifier(nn.Module):

    def __init__(self, embedding_dim, hidden_dim, tagset_size):
        super(LSTMClassifier, self).__init__() 
        self.hidden_dim = hidden_dim
 
        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=2, batch_first=True)

        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(hidden_dim, tagset_size)

        # Initialize weights
        self.apply(self.init_weights)


    def forward(self, sentence):
        # Since the final prediction result is only taken once for multiple timestamps of a patient, 
        # the last hidden in the output is selected.
        lstm_out, _ = self.lstm(sentence)
        tag_space = self.hidden2tag(lstm_out[:, -1, :])
        tag_scores = F.log_softmax(tag_space, dim=1) # Compared with softmax, it can prevent overflow and underflow.
        return tag_scores

    def init_weights(self, m):
        if isinstance(m, nn.Linear):
            # Initialize the fully connected layer
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.LSTM):
            # Initialize LSTM weights and biases
            for name, param in m.named_parameters():
                if 'weight_ih' in name:
                    nn.init.xavier_uniform_(param.data)
                elif 'weight_hh' in name:
                    nn.init.orthogonal_(param.data)
                elif 'bias' in name:
                    nn.init.zeros_(param.data)

# make sure reproducibility
def set_random_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if you are using multi-GPU.
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False