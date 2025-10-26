# Функция для преобразования категориальных признаков
import math
from copy import deepcopy
from anytree import Node


def convert_categorical_rules(rules, binary_features):
    optimized_rules = deepcopy(rules)
    for item_idx, item in enumerate(optimized_rules):
        for rule_idx, rule in enumerate(item[0]):
            variable, sign, value = rule.split(" ")
            if variable in binary_features:
                if sign == ">":
                    value = math.ceil(float(value))
                else:
                    value = math.floor(float(value))
                optimized_rules[item_idx][0][rule_idx] = f"{variable} == {int(value)}"
    return optimized_rules


# Функция для создания структуры дерева правил
def create_rule_structure(rules, position=0):
    if not rules or not rules[0][0]:
        return {"result": rules[0][1]} if rules else None

    root = {}
    unique_rules = set()
    for item in rules:
        rule = item[0][0]
        unique_rules.add(rule)

    for rule in unique_rules:
        filtered_rules = [r for r in rules if r[0][0] == rule]
        processed_rules = deepcopy(filtered_rules)
        for r in processed_rules:
            del r[0][0]
        child = create_rule_structure(processed_rules, position + 1)
        root[rule] = child
    return {"children": root}


# Функция для упрощения дерева правил
def simplify_tree_rules(node):
    if "children" in node:
        children = node["children"]
        for key in list(children.keys()):
            simplify_tree_rules(children[key])
        results = [
            children[key]["result"] for key in children if "result" in children[key]
        ]
        if len(results) == len(children) and all(r == results[0] for r in results):
            node["result"] = results[0]
            del node["children"]


# Функция для конвертации дерева правил обратно в список правил
def convert_tree_to_list(node, current_path=None, result=None):
    if current_path is None:
        current_path = []
    if result is None:
        result = []
    if "children" in node:
        for key, child in node["children"].items():
            new_path = current_path + [key]
            if "result" in child:
                result.append((new_path, child["result"]))
            else:
                convert_tree_to_list(child, new_path, result)
    elif "result" in node:
        result.append((current_path, node["result"]))
    return result


# Функция для парсинга условий
def parse_condition(condition):
    parts = condition.strip().split()
    variable = parts[0]
    operator = parts[1]
    value = float(parts[2])
    return variable, operator, value


# Функция для построения дерева из правил
def build_tree(rules):
    root = Node("Start", variable=None, operator=None, value=None)
    for conditions, class_label in rules:
        current_node = root
        for condition in conditions:
            variable, operator, value = parse_condition(condition)
            # Проверяем, есть ли уже такой узел среди детей
            found = False
            for child in current_node.children:
                if (
                    child.variable == variable
                    and child.operator == operator
                    and abs(child.value - value) < 1e-6
                ):
                    current_node = child
                    found = True
                    break
            if not found:
                # Создаем новый узел
                new_node = Node(
                    condition,
                    parent=current_node,
                    variable=variable,
                    operator=operator,
                    value=value,
                )
                current_node = new_node
        # Добавляем лист с классом
        Node(
            f"Класс {class_label}",
            parent=current_node,
            variable=None,
            operator=None,
            value=None,
        )
    return root
