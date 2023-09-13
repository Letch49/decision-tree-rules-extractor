from typing import List, Tuple, Optional
from sklearn.tree import DecisionTreeClassifier


class RuleExtractor:
    def __init__(self, tree: DecisionTreeClassifier, feature_names: list[str]):
        self.tree = tree
        self.feature_names = feature_names

    def extract_rules(self) -> list[tuple[list[str], int]]:
        rules = []
        self._traverse_tree(0, [], rules)
        return rules

    def _traverse_tree(self, node, path_conditions, rules):
        children_left = self.tree.tree_.children_left
        children_right = self.tree.tree_.children_right
        feature = self.tree.tree_.feature
        threshold = self.tree.tree_.threshold
        values = self.tree.tree_.value

        if children_left[node] == children_right[node]:
            class_label = values[node].argmax()
            rules.append((path_conditions, class_label))
            return

        left_condition = f"{self.feature_names[feature[node]]} <= {threshold[node]:.2f}"
        self._traverse_tree(
            children_left[node], path_conditions + [left_condition], rules
        )

        right_condition = f"{self.feature_names[feature[node]]} > {threshold[node]:.2f}"
        self._traverse_tree(
            children_right[node], path_conditions + [right_condition], rules
        )


class TreeNode:
    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None
        self.rule = None

    def add_rule(self, rule, result):
        current_node = self
        for condition in rule:
            if "<=" in condition or "<" in condition:
                if not current_node.left:
                    current_node.left = TreeNode()
                current_node = current_node.left
            else:
                if not current_node.right:
                    current_node.right = TreeNode()
                current_node = current_node.right
        current_node.rule = (rule, result)


class TreeBuilder:
    @staticmethod
    def build(rules: List[Tuple[List[str], int]]) -> TreeNode:
        root = TreeNode()
        for rule, result in rules:
            root.add_rule(rule, result)
        return root


class TreeSimplifier:
    @staticmethod
    def simplify(node: TreeNode):
        if not node.left and not node.right:
            return

        if node.left:
            TreeSimplifier.simplify(node.left)
        if node.right:
            TreeSimplifier.simplify(node.right)

        if node.left and node.right and node.left.rule and node.right.rule:
            left_rule, left_result = node.left.rule
            right_rule, right_result = node.right.rule

            if left_result == right_result and left_rule[:-1] == right_rule[:-1]:
                node.rule = (left_rule[:-1], left_result)
                node.left.rule = None
                node.right.rule = None


class RulePrinter:
    @staticmethod
    def print_rules(node: TreeNode) -> List[Tuple[List[str], int]]:
        if not node:
            return []
        if node.rule:
            return [node.rule]
        return RulePrinter.print_rules(node.left) + RulePrinter.print_rules(node.right)

    @staticmethod
    def print_and_count(node: TreeNode):
        rules = RulePrinter.print_rules(node)

        return rules
