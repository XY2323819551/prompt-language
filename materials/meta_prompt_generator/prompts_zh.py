"""
此模块包含元提示生成器中使用的提示模板。
您可以根据需要自定义它们。
"""

META_PROMPT = """
根据任务描述或现有提示，生成一个详细的系统提示，以有效地指导语言模型完成任务。

# 指导原则

- 理解任务：把握主要目标、目的、要求、约束条件和预期输出。
- 最小化更改：如果提供了现有提示，仅在简单的情况下改进它。对于复杂的提示，在不改变原始结构的情况下增强清晰度并添加缺失的元素。
- 先推理后结论：在得出任何结论之前鼓励推理步骤。注意！如果用户提供的示例中推理在后面，请颠倒顺序！切勿以结论开始示例！
    - 推理顺序：标出提示中的推理部分和结论部分（按具体字段名称）。对于每个部分，确定执行顺序，并判断是否需要颠倒。
    - 结论、分类或结果应始终放在最后。
- 示例：如果有帮助，包含高质量的示例，对复杂元素使用[方括号]占位符。
   - 需要包含什么类型的示例，数量多少，以及它们是否复杂到需要使用占位符。
- 清晰简洁：使用清晰、具体的语言。避免不必要的指令或平淡的陈述。
- 格式化：使用markdown功能提高可读性。除非特别要求，否则不要使用```代码块。
- 保留用户内容：如果输入的任务或提示包含详细的指南或示例，完整保留它们，或尽可能接近。如果它们模糊不清，考虑分解成子步骤。保留用户提供的任何细节、指南、示例、变量或占位符。
- 常量：在提示中包含常量，因为它们不容易受到提示注入的影响。比如指南、评分标准和示例。
- 输出格式：详细说明最合适的输出格式。这应包括长度和语法（例如短句、段落、JSON等）
    - 对于输出明确定义或结构化数据（分类、JSON等）的任务，倾向于输出JSON。
    - 除非明确要求，否则JSON不应该包装在代码块（```）中。

你输出的最终提示应遵循以下结构。不要包含任何额外的评论，只输出完整的系统提示。具体来说，不要在提示的开头或结尾包含任何额外的消息。（例如，不要加"---"）

[简洁的任务描述指令 - 这应该是提示的第一行，没有章节标题]

[根据需要添加其他详细信息]

[可选的章节，带有标题或项目符号，用于详细步骤]

# 步骤 [可选]

[可选：完成任务所需的详细步骤分解]

# 输出格式

[具体说明输出应如何格式化，无论是响应长度、结构（如JSON、markdown等）]

# 示例 [可选]

[可选：1-3个定义明确的示例，必要时使用占位符。清楚标明示例的开始和结束，以及输入和输出是什么。根据需要使用占位符。]
[如果示例比预期的实际示例短，用()解释实际示例应该如何更长/更短/不同。并使用占位符！]

# 注意事项 [可选]

[可选：边缘情况、细节，以及重复或强调特定重要考虑事项的区域]
""".strip()


META_SCHEMA = {
    "name": "元模式",
    "schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "模式的名称"},
            "type": {
                "type": "string",
                "enum": ["object", "array", "string", "number", "boolean", "null"],
            },
            "properties": {
                "type": "object",
                "additionalProperties": {"$ref": "#/$defs/schema_definition"},
            },
            "items": {
                "anyOf": [
                    {"$ref": "#/$defs/schema_definition"},
                    {"type": "array", "items": {"$ref": "#/$defs/schema_definition"}},
                ]
            },
            "required": {"type": "array", "items": {"type": "string"}},
            "additionalProperties": {"type": "boolean"},
        },
        "required": ["type"],
        "additionalProperties": False,
        "if": {"properties": {"type": {"const": "object"}}},
        "then": {"required": ["properties"]},
        "$defs": {
            "schema_definition": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "object",
                            "array",
                            "string",
                            "number",
                            "boolean",
                            "null",
                        ],
                    },
                    "properties": {
                        "type": "object",
                        "additionalProperties": {"$ref": "#/$defs/schema_definition"},
                    },
                    "items": {
                        "anyOf": [
                            {"$ref": "#/$defs/schema_definition"},
                            {
                                "type": "array",
                                "items": {"$ref": "#/$defs/schema_definition"},
                            },
                        ]
                    },
                    "required": {"type": "array", "items": {"type": "string"}},
                    "additionalProperties": {"type": "boolean"},
                },
                "required": ["type"],
                "additionalProperties": False,
                "if": {"properties": {"type": {"const": "object"}}},
                "then": {"required": ["properties"]},
            }
        },
    },
}

META_SCHEMA_PROMPT = """
# 指令
返回所描述JSON的有效模式。

你必须确保：
- 对象中的所有字段都设置为必需
- 我重复一遍，所有字段都必须标记为必需
- 所有对象必须将additionalProperties设置为false
    - 因此，像"attributes"或"metadata"这样通常允许额外属性的属性应该改为有固定的属性集
- 所有对象必须定义properties
- 字段顺序很重要。任何形式的"思考"或"解释"都应该在结论之前
- $defs必须定义在schema参数下

不支持的重要关键字包括：
- 对于字符串：minLength、maxLength、pattern、format
- 对于数字：minimum、maximum、multipleOf
- 对于对象：patternProperties、unevaluatedProperties、propertyNames、minProperties、maxProperties
- 对于数组：unevaluatedItems、contains、minContains、maxContains、minItems、maxItems、uniqueItems

其他注意事项：
- 支持定义和递归
- 只有在必要包含引用（如"$defs"）时，它必须在"schema"对象内部

# 示例
输入：生成一个包含步骤和最终答案的数学推理模式。
输出：{
    "name": "数学推理",
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "description": "解决数学问题涉及的步骤序列。",
            "items": {
                "type": "object",
                "properties": {
                    "explanation": {
                        "type": "string",
                        "description": "本步骤使用的推理或方法的描述。"
                    },
                    "output": {
                        "type": "string",
                        "description": "此特定步骤的结果或输出。"
                    }
                },
                "required": [
                    "explanation",
                    "output"
                ],
                "additionalProperties": false
            }
        },
        "final_answer": {
            "type": "string",
            "description": "数学问题的最终解决方案或答案。"
        }
    },
    "required": [
        "steps",
        "final_answer"
    ],
    "additionalProperties": false
}

输入：给我一个链表
输出：{
    "name": "链表",
    "type": "object",
    "properties": {
        "linked_list": {
            "$ref": "#/$defs/linked_list_node",
            "description": "链表的头节点。"
        }
    },
    "$defs": {
        "linked_list_node": {
            "type": "object",
            "description": "定义单链表中的节点。",
            "properties": {
                "value": {
                    "type": "number",
                    "description": "存储在此节点中的值。"
                },
                "next": {
                    "anyOf": [
                        {
                            "$ref": "#/$defs/linked_list_node"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "description": "指向下一个节点的引用；如果是最后一个节点则为null。"
                }
            },
            "required": [
                "value",
                "next"
            ],
            "additionalProperties": false
        }
    },
    "required": [
        "linked_list"
    ],
    "additionalProperties": false
}

输入：动态生成的UI
输出：{
    "name": "用户界面",
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "description": "UI组件的类型",
            "enum": [
                "div",
                "button",
                "header",
                "section",
                "field",
                "form"
            ]
        },
        "label": {
            "type": "string",
            "description": "UI组件的标签，用于按钮或表单字段"
        },
        "children": {
            "type": "array",
            "description": "嵌套的UI组件",
            "items": {
                "$ref": "#"
            }
        },
        "attributes": {
            "type": "array",
            "description": "UI组件的任意属性，适用于任何元素",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "属性的名称，例如onClick或className"
                    },
                    "value": {
                        "type": "string",
                        "description": "属性的值"
                    }
                },
                "required": [
                    "name",
                    "value"
                ],
                "additionalProperties": false
            }
        }
    },
    "required": [
        "type",
        "label",
        "children",
        "attributes"
    ],
    "additionalProperties": false
}
""".strip() 