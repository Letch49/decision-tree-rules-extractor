from copy import deepcopy

import numpy as np
from sklearn.tree import DecisionTreeClassifier


class RuleExtractor:
    def __init__(self, tree: DecisionTreeClassifier, feature_names):
        self.tree = tree
        self.feature_names = feature_names

    def extract_rules(self):
        rules = []
        self._traverse_tree(0, [], rules)
        return rules

    def _traverse_tree(self, node_id, conditions, rules):
        tree = self.tree.tree_
        feature = tree.feature
        threshold = tree.threshold
        left_child = tree.children_left
        right_child = tree.children_right
        value = tree.value

        if left_child[node_id] == -1 and right_child[node_id] == -1:
            class_label = np.argmax(value[node_id])
            rules.append((deepcopy(conditions), class_label))
        else:
            feature_name = self.feature_names[feature[node_id]]
            threshold_value = threshold[node_id]

            # Левый потомок
            condition = f"{feature_name} <= {threshold_value:.5f}"
            conditions.append(condition)
            self._traverse_tree(left_child[node_id], conditions, rules)
            conditions.pop()

            # Правый потомок
            condition = f"{feature_name} > {threshold_value:.5f}"
            conditions.append(condition)
            self._traverse_tree(right_child[node_id], conditions, rules)
            conditions.pop()
