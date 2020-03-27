"""Base classes for developing a Federated Learning model on PyTorch

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
                                                                                                                                                                                        
class PyTorchResnet(PyTorchFLModel):

    def __init__(self, data, device='cpu', num_classes=10, **kwargs):
        super().__init__(data, device=device)

        self.num_classes = num_classes
        self.init_network(device, **kwargs)
        self._init_optimizer()        

        #def loss_fn(output, target):
        #    return F.cross_entropy(output, target)

        # transform our numpy arrays into a pytorch dataloader
        # FIXME: we're holding a second copy for the sake of get_data. Need to make a version of this that really matchs pytorch
        self.data = data
        #self.train_loader, self.val_loader = self._data_to_pt_loader(data)

        self.loss_fn = cross_entropy

    def _init_optimizer(self):
        self.optimizer = optim.Adam(self.parameters(), lr=1e-4)
    '''
    @staticmethod
    def _data_to_pt_loader(data):
        tX = torch.stack([torch.Tensor(i) for i in data.X_train])
        # ty = torch.stack([torch.Tensor(i) for i in data.y_train])
        ty = torch.Tensor(data.y_train)
        train_loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(tX, ty), batch_size=data.batch_size, shuffle=True)
        
        tX = torch.stack([torch.Tensor(i) for i in data.X_val])
        # ty = torch.stack([torch.Tensor(i) for i in data.y_val])
        ty = torch.Tensor(data.y_val)
        val_loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(tX, ty), batch_size=data.batch_size, shuffle=True)

        return train_loader, val_loader
        '''

    def init_network(self, device):
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)
        self.to(device) 
        #
        '''
        '''

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))                                                                                                                                                        
        x = self.pool(F.relu(self.conv2(x)))                                                                                                                                                        
        x = x.view(-1, 16 * 5 * 5)                                                                                                                                                                  
        x = F.relu(self.fc1(x))                                                                                                                                                                     
        x = F.relu(self.fc2(x))                                                                                                                                                                     
        x = self.fc3(x) 
        #
        #x = F.relu(self.conv1(x))
        #x = F.max_pool2d(x, 2, 2)
        #x = F.relu(self.conv2(x))
        #x = F.max_pool2d(x, 2, 2)
        #x = x.view(-1, 4*4*50)
        #x = F.relu(self.fc1(x))
        #x = self.fc2(x)
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
                #TODO: diag problem
                #val_score += pred.eq(target).diag().sum().cpu().numpy()
                val_score += pred.eq(target).sum().cpu().numpy()

        return val_score / total_samples

    def train_epoch(self): 
        # set to "training" mode
        self.train()
        
        losses = []
        loader = self.data.get_train_loader()
        for data, target in loader:
            data, target = data.to(self.device), target.to(self.device, dtype=torch.int64)
            self.optimizer.zero_grad()
            output = self(data)
            #TODO: target loading problem
            target = torch.FloatTensor(output.shape).uniform_(0,10)
            #
            loss = self.loss_fn(output, target)
            loss.backward()
            self.optimizer.step()
            losses.append(loss.detach().cpu().numpy())

        return np.mean(losses)

    def get_data(self):
        return self.data

    '''
    def set_data(self, data):
        if data.get_feature_shape() != self.data.get_feature_shape():
            raise ValueError('Data feature shape is not compatible with model.')
        self.data = data
        self.train_loader, self.val_loader = self._data_to_pt_loader(data)
    
    '''
    def reset_opt_vars(self):
        self._init_optimizer()
