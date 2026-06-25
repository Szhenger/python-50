import csv
import sys
import random
import math
from typing import List, Tuple

TEST_SIZE = 0.4

class KNeighborsClassifier:
    def __init__(self):
        self.X_train: List[List[float]] = []
        self.y_train: List[int] = []

    def fit(self, evidence: List[List[float]], labels: List[int]) -> None:
        self.X_train = evidence
        self.y_train = labels

    def predict(self, X_test: List[List[float]]) -> List[int]:
        predictions = []
        for test_point in X_test:
            # Finding the single nearest neighbor (k=1)
            min_dist = float('inf')
            best_label = 0
            
            for i, train_point in enumerate(self.X_train):
                # Calculate squared Euclidean distance
                dist = sum((a - b) ** 2 for a, b in zip(test_point, train_point))
                
                if dist < min_dist:
                    min_dist = dist
                    best_label = self.y_train[i]
            predictions.append(best_label)
        return predictions

def load_data(filename: str) -> Tuple[List[List[float]], List[int]]:
    evidence, labels = [], []
    
    # Mapping definitions
    visitor_map = {"Returning_Visitor": 1, "New_Visitor": 0, "Other": 0}
    bool_map = {"TRUE": 1, "FALSE": 0, "True": 1, "False": 0}
    month_map = {
        "Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4, "June": 5,
        "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11
    }

    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Map features to numeric values
            try:
                row_evidence = [
                    float(row["Administrative"]), float(row["Informational"]),
                    float(row["ProductRelated"]), float(row["Administrative_Duration"]),
                    float(row["Informational_Duration"]), float(row["ProductRelated_Duration"]),
                    float(row["BounceRates"]), float(row["ExitRates"]),
                    float(row["PageValues"]), float(row["SpecialDay"]),
                    month_map[row["Month"]], float(row["OperatingSystems"]),
                    float(row["Browser"]), float(row["Region"]),
                    float(row["TrafficType"]), visitor_map[row["VisitorType"]],
                    bool_map[row["Weekend"]]
                ]
                evidence.append(row_evidence)
                labels.append(bool_map[row["Revenue"]])
            except (ValueError, KeyError):
                continue
                
    return evidence, labels

def train_test_split(evidence, labels, test_size):
    data = list(zip(evidence, labels))
    random.shuffle(data)
    
    split_idx = int(len(data) * (1.0 - test_size))
    train, test = data[:split_idx], data[split_idx:]
    
    # Unzip back into separate lists
    X_train, y_train = zip(*train)
    X_test, y_test = zip(*test)
    return list(X_train), list(X_test), list(y_train), list(y_test)

def evaluate(labels, predictions):
    positives = [i for i, label in enumerate(labels) if label == 1]
    negatives = [i for i, label in enumerate(labels) if label == 0]
    
    sensitivity = sum(predictions[i] == 1 for i in positives) / len(positives) if positives else 0.0
    specificity = sum(predictions[i] == 0 for i in negatives) / len(negatives) if negatives else 0.0
    
    return sensitivity, specificity

def main():
    if len(sys.argv) != 2:
        print("Usage: python shopping.py data.csv", file=sys.stderr)
        sys.exit(1)

    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(evidence, labels, TEST_SIZE)

    model = KNeighborsClassifier()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    sensitivity, specificity = evaluate(y_test, predictions)
    
    correct = sum(1 for actual, pred in zip(y_test, predictions) if actual == pred)
    incorrect = len(y_test) - correct

    print(f"Correct: {correct}")
    print(f"Incorrect: {incorrect}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")

if __name__ == "__main__":
    main()
