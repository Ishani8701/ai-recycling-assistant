from typing import Tuple, List, Dict, Any
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

def calculate_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return accuracy_score(y_true, y_pred)

def calculate_precision(y_true: np.ndarray, y_pred: np.ndarray, average: str = 'weighted') -> float:
    return precision_score(y_true, y_pred, average=average, zero_division=0)

def calculate_recall(y_true: np.ndarray, y_pred: np.ndarray, average: str = 'weighted') -> float:
    return recall_score(y_true, y_pred, average=average, zero_division=0)

def get_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, labels: List[Any] = None) -> np.ndarray:
    return confusion_matrix(y_true, y_pred, labels=labels)

def get_classification_report(y_true: np.ndarray, y_pred: np.ndarray, target_names: List[str] = None) -> Dict[str, Dict[str, float]]:
    from sklearn.metrics import classification_report
    
    report = classification_report(
        y_true, 
        y_pred, 
        target_names=target_names,
        output_dict=True,
        zero_division=0
    )
    return report

def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray, target_names: List[str] = None) -> Dict[str, Any]:
    metrics = {
        'accuracy': calculate_accuracy(y_true, y_pred),
        'precision': calculate_precision(y_true, y_pred),
        'recall': calculate_recall(y_true, y_pred),
        'confusion_matrix': get_confusion_matrix(y_true, y_pred).tolist(),
        'classification_report': get_classification_report(y_true, y_pred, target_names)
    }
    
    return metrics