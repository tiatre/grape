from collections import defaultdict


def b_cubed(true_clusters, predicted_clusters):
    # Mapping of cluster indices to labels
    true_cluster_labels = defaultdict(set)
    predicted_cluster_labels = defaultdict(set)

    for label, true_cluster in true_clusters.items():
        true_cluster_labels[true_cluster].add(label)

    for label, predicted_cluster in predicted_clusters.items():
        predicted_cluster_labels[predicted_cluster].add(label)

    # Calculate the B-cubed precision and recall
    precision_sums = 0
    recall_sums = 0
    num_items = len(true_clusters)

    for label, true_cluster in true_clusters.items():
        predicted_cluster = predicted_clusters[label]

        true_cluster_size = len(true_cluster_labels[true_cluster])
        predicted_cluster_size = len(predicted_cluster_labels[predicted_cluster])

        true_positives = len(
            true_cluster_labels[true_cluster].intersection(
                predicted_cluster_labels[predicted_cluster]
            )
        )

        precision = (
            true_positives / predicted_cluster_size if predicted_cluster_size > 0 else 0
        )
        recall = true_positives / true_cluster_size if true_cluster_size > 0 else 0

        precision_sums += precision
        recall_sums += recall

    b_cubed_precision = precision_sums / num_items
    b_cubed_recall = recall_sums / num_items
    b_cubed_f1 = (
        (2 * b_cubed_precision * b_cubed_recall) / (b_cubed_precision + b_cubed_recall)
        if (b_cubed_precision + b_cubed_recall) > 0
        else 0
    )

    return b_cubed_precision, b_cubed_recall, b_cubed_f1


datasets = {
    "Example 1: High Precision, Low Recall": (
        {"A": 1, "B": 1, "C": 1, "D": 2, "E": 2, "F": 2},
        {"A": 1, "B": 1, "C": 2, "D": 3, "E": 3, "F": 4},
    ),
    "Example 2: Low Precision, High Recall": (
        {"A": 1, "B": 1, "C": 1, "D": 2, "E": 2, "F": 2},
        {"A": 1, "B": 1, "C": 1, "D": 1, "E": 1, "F": 1},
    ),
    "Example 3: Moderate Precision and Recall": (
        {"A": 1, "B": 1, "C": 2, "D": 2, "E": 3, "F": 3},
        {"A": 1, "B": 1, "C": 1, "D": 2, "E": 2, "F": 2},
    ),
    "Example 4: Perfect Scores": (
        {"A": 1, "B": 1, "C": 1, "D": 2, "E": 2, "F": 3},
        {"A": 1, "B": 1, "C": 1, "D": 2, "E": 2, "F": 3},
    ),
}

for description, (golden, hypothesis) in datasets.items():
    precision, recall, f1_score = b_cubed(golden, hypothesis)
    print(description)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1_score)
    print()
