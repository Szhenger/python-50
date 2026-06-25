import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

# Hyperparameters
EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4
BATCH_SIZE = 32

class TrafficNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3)
        self.pool1 = nn.MaxPool2d(3, 3)
        self.conv2 = nn.Conv2d(64, 32, kernel_size=2)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.flatten = nn.Flatten()
        # Input size: 32 channels * 4 * 4 features
        self.fc1 = nn.Linear(32 * 4 * 4, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, NUM_CATEGORIES)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = self.pool1(x)
        # Maintaining original architecture's softmax placement
        x = torch.softmax(self.conv2(x), dim=1)
        x = self.pool2(x)
        x = self.flatten(x)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return torch.log_softmax(x, dim=1)

def get_data(data_dir):
    # Transforms replicate the C++ cv::Mat normalization and resizing
    transform = transforms.Compose([
        transforms.Resize((IMG_HEIGHT, IMG_WIDTH)),
        transforms.ToTensor(), # Normalizes to [0, 1] automatically
    ])
    dataset = datasets.ImageFolder(data_dir, transform=transform)
    
    test_size = int(len(dataset) * TEST_SIZE)
    train_size = len(dataset) - test_size
    return random_split(dataset, [train_size, test_size])

def main():
    if len(sys.argv) < 2:
        print("Usage: python traffic.py data_directory [model.pth]")
        sys.exit(1)

    data_dir = sys.argv[1]
    
    print("Loading data...")
    train_ds, test_ds = get_data(data_dir)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False)
    
    model = TrafficNet()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.NLLLoss()

    print(f"Training model on {len(train_ds)} images...")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        running_loss = 0.0
        for data, target in train_loader:
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        print(f"Epoch {epoch}/{EPOCHS} - Loss: {running_loss / len(train_loader):.4f}")

    print("Evaluating model...")
    model.eval()
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            prediction = output.argmax(dim=1)
            correct += prediction.eq(target).sum().item()

    print(f"Test Accuracy: {correct / len(test_ds):.4f}")

    if len(sys.argv) == 3:
        torch.save(model.state_dict(), sys.argv[2])
        print(f"Model saved to {sys.argv[2]}.")

if __name__ == "__main__":
    main()
