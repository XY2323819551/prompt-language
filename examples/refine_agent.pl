
@code(```json
{
    "source": "中文",
    "target": "英文",
    "source_text": "昨夜雨疏风骤，浓睡不消残酒"
}
```) -> data


你是一位专业的语言学家，专门从事【${data.source}】到【${data.target}】的翻译工作。请为以下文本提供【${data.source_text}】翻译。请只提供翻译结果，不要包含任何解释或其他文本。-> init_trans




你是一位专业的语言学家，专门从事【${data.source}】到【${data.target}】翻译编辑工作。
你的任务是仔细阅读源文本和其翻译，然后给出建设性的批评和有用的建议来改进翻译。

源文本和初始翻译用XML标签标记如下：

<SOURCE_TEXT>
${data.source_text}
</SOURCE_TEXT>

<TRANSLATION>
$init_trans
</TRANSLATION>

在提供建议时，请注意是否有以下方面可以改进：
(i) 准确性（通过纠正添加、误译、遗漏或未翻译的文本），
(ii) 流畅性（通过应用{config.target_language}语法、拼写和标点规则，确保没有不必要的重复），
(iii) 风格（通过确保翻译反映源文本的风格并考虑文化背景），
(iv) 术语（通过确保术语使用的一致性并反映源文本领域；确保使用恰当的{config.target_language}习语）。

请列出具体的、有帮助的和建设性的建议来改进翻译。
每个建议应针对翻译的一个具体部分。
只输出建议，不要输出其他内容。 -> trans_suggestions



你的任务是仔细阅读并编辑一个【${data.source}】到【${data.target}】的翻译，同时考虑专家提供的建议和建设性批评。
源文本、初始翻译和专家语言学家的建议用XML标签标记如下：

<SOURCE_TEXT>
${data.source_text}
</SOURCE_TEXT>

<TRANSLATION>
$init_trans
</TRANSLATION>

<EXPERT_SUGGESTIONS>
$trans_suggestions
</EXPERT_SUGGESTIONS>

请在编辑翻译时考虑专家建议。编辑翻译时请确保：

(i) 准确性（通过纠正添加、误译、遗漏或未翻译的文本），
(ii) 流畅性（通过应用{config.target_language}语法、拼写和标点规则，确保没有不必要的重复），
(iii) 风格（通过确保翻译反映源文本的风格），
(iv) 术语（避免上下文不当、使用不一致），
(v) 其他错误。

只输出新的翻译，不要输出其他内容。 -> refine_trans





