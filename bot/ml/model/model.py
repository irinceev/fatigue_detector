import torch.nn as nn

class FatigueRegressor(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(512, 1)
    def forward(self, x):
        return self.linear(x).squeeze(1)