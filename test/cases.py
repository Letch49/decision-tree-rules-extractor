from copy import deepcopy
import math
from collections import defaultdict, Counter


class RuleTransformer:
    def __init__(self, data):
        self.data = data

    def transform(self):
        # Шаг 1: Преобразование бинарных признаков
        binary_category_features = {"smoking", "diabets", "sex_male"}
        optimized_rules = deepcopy(self.data)
        for item_idx, item in enumerate(optimized_rules):
            for rule_idx, rule in enumerate(item[0]):
                variable, sign, value = rule.split(" ")
                if variable in binary_category_features:
                    if sign == ">":
                        value = math.ceil(float(value))
                    else:
                        value = math.floor(float(value))
                    optimized_rules[item_idx][0][rule_idx] = f"{variable} == {value}"

        # Шаг 2: Создание структуры правил
        def remove_indices_from_tuples(data, rule_to_remove):
            data = deepcopy(data)
            for item in data:
                idx = item[0].index(rule_to_remove)
                del item[0][idx]
            return data

        def create_rule_structure(rules, position=0):
            if not rules or not rules[0][0]:
                return None

            root = {}
            unique_rules = set(item[0][0] for item in rules)
            for rule in unique_rules:
                filtered_rules = [item for item in rules if item[0][0] == rule]
                processed_rule = remove_indices_from_tuples(filtered_rules, rule)
                root[rule] = {
                    "position": position,
                    "children": create_rule_structure(processed_rule, position + 1),
                    "result": filtered_rules[0][1]
                    if not filtered_rules[0][0]
                    else None,
                }
            return root

        tree_rules = create_rule_structure(optimized_rules)

        # Шаг 3: Упрощение структуры дерева
        def simplify_tree_rules(node):
            if isinstance(node, dict) and "children" in node:
                child_nodes = node["children"]
                if child_nodes is not None and isinstance(child_nodes, dict):
                    child_keys = list(child_nodes.keys())
                    if len(child_keys) == 2:
                        left_child = child_nodes[child_keys[0]]
                        right_child = child_nodes[child_keys[1]]
                        if (
                            left_child["result"] is not None
                            and right_child["result"] is not None
                            and left_child["result"] == right_child["result"]
                            and left_child["position"] == right_child["position"]
                        ):
                            node["result"] = left_child["result"]
                            node["children"] = None
                        else:
                            for child_key in child_keys:
                                simplify_tree_rules(child_nodes[child_key])

        for key in tree_rules:
            simplify_tree_rules(tree_rules[key])

        # Шаг 4: Преобразование дерева обратно в список правил
        def convert_tree_to_list(node, current_path=None, result=None):
            if current_path is None:
                current_path = []
            if result is None:
                result = []
            if "children" in node:
                child_nodes = node["children"]
                if child_nodes is not None:
                    for key, value in child_nodes.items():
                        new_path = current_path + [key]
                        if value["children"] is None:
                            result.append((new_path, value["result"]))
                        else:
                            convert_tree_to_list(value, new_path, result)
            return result

        simplified_rules_list = []
        for key in tree_rules:
            simplified_nodes = convert_tree_to_list(tree_rules[key])
            for item in simplified_nodes:
                item[0].insert(0, key)
            simplified_rules_list.extend(simplified_nodes)

        # Шаг 5: Удаление схожих правил
        def parse_rule(rule):
            out = ""
            for idx, item in enumerate(rule):
                if idx != len(rule) - 1:
                    out += f"{item},"
                else:
                    var, sign, val = item.split(" ")
                    out += f"{var}{sign}"
            return out

        def drop_same_rules(rules):
            rules = deepcopy(rules)
            parsed_rules = [parse_rule(item[0]) for item in rules]
            rules_by_count = Counter(parsed_rules)
            for key in rules_by_count:
                if rules_by_count[key] > 1:
                    indexes = [
                        idx for idx, item in enumerate(parsed_rules) if item == key
                    ]
                    rules_list = [rules[index] for index in indexes]
                    represent = defaultdict(list)
                    if all(x[1] == rules_list[0][1] for x in rules_list):
                        for item in rules_list:
                            el = item[0][-1]
                            variable, sign, value = el.split(" ")
                            represent[(variable, sign)].append(float(value))
                    for key in represent:
                        sign = key[1]
                        found_value = None
                        if sign == ">":
                            found_value = min(represent[key])
                        if sign == "<=":
                            found_value = max(represent[key])
                        if sign == "==":
                            found_value = represent[key][0]
                        nice_rule = f"{key[0]} {key[1]} {found_value}"
                        to_remove = [
                            item for item in rules_list if nice_rule not in item[0]
                        ][0]
                        idx = rules.index(to_remove)
                        del rules[idx]
            return rules

        rules = drop_same_rules(simplified_rules_list)
        return rules


# Пример использования
def test_case_1():
    """
    Тест для проверки верности алгоритма.
    :return: None
    """
    input_data = [
        (["smoking <= 0.16", "diabets <= 0.95", "age <= 62.31", "age <= 57.55"], 0),
        (["smoking <= 0.16", "diabets <= 0.95", "age <= 62.31", "age > 57.55"], 1),
        (["smoking <= 0.16", "diabets <= 0.95", "age > 62.31", "sex_male <= 0.34"], 0),
        (["smoking <= 0.16", "diabets <= 0.95", "age > 62.31", "sex_male > 0.34"], 1),
        (["smoking <= 0.16", "diabets > 0.95", "sex_male <= 0.92", "ОХС <= 4.62"], 1),
        (["smoking <= 0.16", "diabets > 0.95", "sex_male <= 0.92", "ОХС > 4.62"], 1),
        (["smoking <= 0.16", "diabets > 0.95", "sex_male > 0.92", "age <= 72.49"], 1),
        (["smoking <= 0.16", "diabets > 0.95", "sex_male > 0.92", "age > 72.49"], 1),
        (["smoking > 0.16", "ОХС <= 3.34"], 0),
        (["smoking > 0.16", "ОХС > 3.34", "ОХС <= 6.16", "age <= 62.18"], 1),
        (["smoking > 0.16", "ОХС > 3.34", "ОХС <= 6.16", "age > 62.18"], 1),
        (["smoking > 0.16", "ОХС > 3.34", "ОХС > 6.16", "sex_male <= 0.84"], 1),
        (["smoking > 0.16", "ОХС > 3.34", "ОХС > 6.16", "sex_male > 0.84"], 1),
    ]

    for item in input_data:
        # Объяснение правил
        rule = item[0]  # string with wiles, how we gettings result
        result = item[1]  # its binary classification base, Y = 0 or 1.

    expected_output = [
        # результат сжатых правил
        (["smoking == 0", "diabets == 0", "age <= 62.31", "age <= 57.55"], 0),
        (["smoking == 0", "diabets == 0", "age <= 62.31", "age > 57.55"], 1),
        (["smoking == 0", "diabets == 0", "age > 62.31", "sex_male <= 0.34"], 0),
        (["smoking == 0", "diabets == 0", "age > 62.31", "sex_male > 0.34"], 1),
        (["smoking == 0", "diabets == 1"], 1),
        (["smoking == 1", "ОХС <= 3.34"], 0),
        (["smoking == 1", "ОХС > 3.34"], 1),
    ]

    processed = RuleTransformer(data=input_data).transform()

    assert (
        processed == expected_output
    ), f"Expected {expected_output}, but got {processed}"


test_case_1()
