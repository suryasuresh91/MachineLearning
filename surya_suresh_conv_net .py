# -*- coding: utf-8 -*-
"""Surya_Suresh_Conv_net.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1X1FsZhscIBy6wDOmKW96a2IxIIG6x8Ru
"""

#@author: suryasuresh
import pandas as pd;
from scipy.stats import zscore
import torch as torch;
import numpy as np
import torchvision.datasets as datasets
from torchvision import transforms
import torch.nn as nn;
import torch.nn.functional as F;
import tensorflow as tf
import matplotlib as plt
import matplotlib.pyplot as pt

np.random.seed(42)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#read in the dataset


num_classes=10;

transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])])

full_train_dataset = datasets.CIFAR10(root='./data', train=True, download=True, 
                             transform=transform )
full_test_dataset = datasets.CIFAR10(root='./data', train=False, download=True,
                             transform=transform )

batch_size=64;

trainloader = torch.utils.data.DataLoader(full_train_dataset, batch_size=batch_size,shuffle=True)
testloader = torch.utils.data.DataLoader(full_test_dataset, batch_size=batch_size,shuffle=False)

# create a neural network (inherit from nn.Module)
class ConvNetWithBatchNorm(nn.Module):
    # architecture of the network is specified in the constructor
    def __init__(self): 
        super(ConvNetWithBatchNorm, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5),         
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=2, stride=2),  
            nn.Conv2d(in_channels=6, out_channels=12, kernel_size=3),
            nn.BatchNorm2d(num_features=12)           
        )
        self.features1 = nn.Sequential(
            nn.ReLU(),
            nn.AvgPool2d(kernel_size=2, stride=2)   
        )
        self.classifier = nn.Sequential(
            nn.Linear(12*6*6, 50),         
            nn.Dropout(p=0.2),
            nn.ReLU(),
            nn.Linear(50,num_classes)            
        )
        
    # here we specify the computation (forward phase of training) how "x" is transfered into output "y"
    def forward(self, x):
        x = self.features(x)
        x = self.features1(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return F.log_softmax(x)

model=ConvNetWithBatchNorm().to(device);
criterion = F.nll_loss;

# this optimizer will do gradient descent for us
# experiment with learning rate and optimizer type
learning_rate = 0.01;
# note that we have to add all weights&biases, for both layers, to the optimizer
optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate)

# we add a learning rate scheduler, which will modify the learning rate during training
# will initially start low, then increase it ("warm up"), and then gradually descrease it
n_epochs = 30;
num_updates = n_epochs*int(np.ceil(len(trainloader.dataset)/batch_size))
print(num_updates)
warmup_steps=1000;
def warmup_linear(x):
    if x < warmup_steps:
        lr=x/warmup_steps
    else:
        lr=max( (num_updates - x ) / (num_updates - warmup_steps), 0.)
    return lr;
scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, warmup_linear);

train_acc=list()
test_acc=list()
for i in range(n_epochs):
    correct=0
    for j, data in enumerate(trainloader):
      
        inputs, labels = data        
        inputs=inputs.to(device);
        labels=labels.to(device);
        
        optimizer.zero_grad();
        #forward phase - predictions by the model
        outputs = model(inputs);
        outputs = model(inputs);
        pred = outputs.data.max(dim=1, keepdim=True)[1]
        correct += pred.eq(labels.data.view_as(pred)).sum().item();
        #forward phase - risk/loss for the predictions
        risk = criterion(outputs, labels);
  
        # calculate gradients
        risk.backward();
        
        # take the gradient step
        optimizer.step();
        scheduler.step();
        
        batch_risk=risk.item();

    train_acc.append(correct / len(trainloader.dataset))

    with (torch.no_grad()):
      correct = 0;
      for j, data in enumerate(testloader):
        
          inputs, labels = data        
          inputs=inputs.to(device);
          labels=labels.to(device);
          outputs = model(inputs);
          pred = outputs.data.max(dim=1, keepdim=True)[1]
          correct += pred.eq(labels.data.view_as(pred)).sum().item();
    print(i, batch_risk, correct / len(testloader.dataset))
    test_acc.append(correct / len(testloader.dataset))

#plotting the train and test accuracy
itr =[x for x in range(n_epochs)]
pt.plot(itr,train_acc,label='Train_Accuracy')
pt.plot(itr,test_acc,label='Test_Accuracy')
pt.xlabel("Iterrations/Epochs)")
pt.ylabel("accuracy")
pt.title("Accuracy plots- Convolution Network")
pt.legend(loc='upper left', frameon=False)
plt.pyplot.show()