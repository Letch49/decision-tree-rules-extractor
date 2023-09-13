from decision_tree_rules_extractor.extractor import (
    RuleExtractor,
    TreeBuilder,
    TreeSimplifier,
    RulePrinter,
)
from sklearn.tree import DecisionTreeClassifier


def process_decision_tree(
    tree: DecisionTreeClassifier, feature_names: list[str]
) -> list[list[str, int]]:
    # Extract rules from the tree
    extractor = RuleExtractor(tree, feature_names)
    rules = extractor.extract_rules()

    # Build the tree using the rules
    built_tree = TreeBuilder.build(rules)

    # Simplify the tree
    TreeSimplifier.simplify(built_tree)

    # rules
    rules = RulePrinter.print_and_count(built_tree)

    return rules
