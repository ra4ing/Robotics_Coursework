from torch import nn
import torch

from torchvision import models
from torchvision import transforms


class Ra4ing(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.module = models.resnet50(pretrained=True)
        fc_inputs = self.module.fc.in_features
        self.module.fc = nn.Linear(fc_inputs, 3)

    def forward(self, x):
        x = self.module(x)
        return x


if __name__ == '__main__':
    ra4ing = Ra4ing()
    input = torch.ones(64, 3, 5, 5)
    output = ra4ing(input)