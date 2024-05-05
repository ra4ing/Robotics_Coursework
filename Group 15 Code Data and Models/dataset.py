from torch.utils.data import Dataset
import os
from PIL import Image
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


class myDataset(Dataset):
    def __init__(self, names_file, transform=None, train=False):
        self.names_file = names_file
        self.transform = transform
        self.size = 0
        self.names_list = []

        dic = os.listdir(names_file)
        for kinds in range(len(dic)):
            d = os.listdir(names_file + "/" + dic[kinds])
            if train:
                for img in d[:int(len(d) * 4 / 5)]:
                    self.names_list.append(
                        (names_file + "/" + dic[kinds] + "/" + img, kinds))
                    self.size += 1
            else:
                for img in d[int(len(d) * 4 / 5):]:
                    self.names_list.append(
                        (names_file + "/" + dic[kinds] + "/" + img, kinds))
                    self.size += 1

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        image = Image.open(self.names_list[idx][0])  # use skitimage
        image = image.convert('RGB')
        image = self.transform(image)
        label = int(self.names_list[idx][1])
        return image, label
