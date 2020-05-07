# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.


"""
You may copy this file as the starting point of your own model.
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from models.pytorch import PyTorchFLModel
import torch.optim as optim

from models.pytorch import PyTorchFLModel

def cross_entropy(output, target):
    return F.binary_cross_entropy_with_logits(input=output, target=target)

class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_planes, planes, stride=1):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != self.expansion*planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, self.expansion*planes, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(self.expansion*planes)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out

class PyTorchResnet(PyTorchFLModel):

    def __init__(self, data, device='cpu', **kwargs):
        super().__init__(data=data, device=device, **kwargs)

        self.num_classes = self.data.num_classes
        self.init_network(self.device, BasicBlock, [2,2,2,2], **kwargs)# Resnet18
        self._init_optimizer()        

        self.loss_fn = cross_entropy

    def _init_optimizer(self):
        self.optimizer = optim.Adam(self.parameters(), lr=1e-4)

    def init_network(self, device, block, num_blocks, num_classes=10, **kwargs):
        self.in_planes = 64
        channel = self.data.get_feature_shape()[0]
        self.conv1 = nn.Conv2d(channel, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.layer1 = self._make_layer(block, 64, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(block, 128, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(block, 256, num_blocks[2], stride=2)
        self.layer4 = self._make_layer(block, 512, num_blocks[3], stride=2)
        self.linear = nn.Linear(512*block.expansion, num_classes)
        self.to(device)

    def _make_layer(self, block, planes, num_blocks, stride):
        strides = [stride] + [1]*(num_blocks-1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_planes, planes, stride))
            self.in_planes = planes * block.expansion
        return nn.Sequential(*layers)

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = F.avg_pool2d(out, 4)
        out = out.view(out.size(0), -1)
        x = self.linear(out)
        return F.log_softmax(x, dim=1)

    def validate(self):
        self.eval()
        val_score = 0
        total_samples = 0
        
        loader = self.data.get_val_loader()
        with torch.no_grad():
            for data, target in loader:
                samples = target.shape[0]
                total_samples += samples
                data, target = data.to(self.device), target.to(self.device, dtype=torch.int64)
                output = self(data)                
                pred = output.argmax(dim=1, keepdim=True) # get the index of the max log-probability
                target_categorical = target.argmax(dim=1, keepdim=True)
                val_score += pred.eq(target_categorical).sum().cpu().numpy()

        return val_score / total_samples

    def train_epoch(self): 
        # set to "training" mode
        self.train()
        
        losses = []
        loader = self.data.get_train_loader()
        for data, target in loader:
            data, target = data.to(self.device), target.to(self.device, dtype=torch.float32)
            self.optimizer.zero_grad()
            output = self(data)
            loss = self.loss_fn(output, target)
            loss.backward()
            self.optimizer.step()
            losses.append(loss.detach().cpu().numpy())

        return np.mean(losses)

    def reset_opt_vars(self):
        self._init_optimizer()
