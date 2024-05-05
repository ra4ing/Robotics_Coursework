from torchvision import transforms
from tensorboardX import SummaryWriter
from torch import nn
from torch.utils.data import DataLoader
from dataset import myDataset
from module import *

#loader大小
batch_size = 16
#训练速率

# 记录训练的次数
total_train_step = 0
# 记录测试的次数
total_test_step = 0
# 训练的轮数
epoch = 151

device = torch.device("cuda")
ra4ing = Ra4ing().cuda()
# ra4ing = torch.load("ra4ing_pre.pth", map_location=torch.device('cuda'))

img_size = 224
#训练数据
train_data = myDataset("./data/origin",
                       transform=transforms.Compose([
                           transforms.Resize((img_size, img_size)),
                           transforms.ToTensor(),
                       ]),
                       train=True)
train_dataloader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
#测试数据
test_data = myDataset("./data/origin",
                      transform=transforms.Compose([
                          transforms.Resize((img_size, img_size)),
                          transforms.ToTensor(),
                      ]),
                      train=False)
test_dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=True)

loss_fn = nn.CrossEntropyLoss().to(device)
lr_init = 0.0001
lr_stepsize = 30
weight_decay = 3.0517578125e-05
optimizer = torch.optim.SGD(ra4ing.parameters(),
                            momentum=0.875,
                            lr=lr_init,
                            weight_decay=weight_decay)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
                                            step_size=lr_stepsize,
                                            gamma=0.1,
                                            verbose=True)
# 添加tensorboard
writer = SummaryWriter("./logs")
train_data_size = len(train_data)
test_data_size = len(test_data)
print("训练数据集的长度为：{}".format(train_data_size))
print("测试数据集的长度为：{}".format(test_data_size))

for i in range(epoch):
    print("-----------------第{}轮开始-----------------".format(i + 1))
    ra4ing.train()
    for data in train_dataloader:

        imgs, targets = data
        imgs = imgs.to(device)
        targets = targets.to(device)
        outputs = ra4ing(imgs)
        loss = loss_fn(outputs, targets)

        # 优化器优化模型
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_train_step = total_train_step + 1
        if total_train_step % 100 == 0:
            print("训练次数：{}, Loss: {}".format(total_train_step, loss.item()))
            writer.add_scalar("train_loss", loss.item(), total_train_step)

    ra4ing.eval()
    total_test_loss = 0
    total_accuracy = 0
    with torch.no_grad():
        for data in test_dataloader:
            imgs, targets = data
            imgs = imgs.to(device)
            targets = targets.to(device)
            outputs = ra4ing(imgs)
            loss = loss_fn(outputs, targets)
            total_test_loss += loss.item()
            accuracy = (outputs.argmax(1) == targets).sum()
            total_accuracy += accuracy

    accuracy_rate = total_accuracy / test_data_size
    print("整体测试集上的Loss: {}".format(total_test_loss))
    print("整体测试集上的正确率: {}".format(accuracy_rate))
    writer.add_scalar("test_loss", total_test_loss, total_test_step)
    writer.add_scalar("test_accuracy", accuracy_rate, total_test_step)
    total_test_step += 1

    if (i + 1) % 50 == 0:
        torch.save(ra4ing, "ra4ing_{}.pth".format(i + 1))

    scheduler.step()

torch.save(ra4ing, "ra4ing_final.pth")
writer.close()