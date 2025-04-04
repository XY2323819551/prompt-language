







# promtp language rules V 0.1.0

## 0. 概述

相比拖拉拽形式的工作流，prompt language可以更容易、清晰的表达agentic workflow。属于agent的调度语言。

prompt language的介绍将从以下几部分展开：

### 语句支持

- 变量标识符
- 赋值语句

### 5种基础语句

- llm调用语句
- 函数调用语句
- 代码块调用语句
- 条件判断语句
- exit退出语句

### 2种高级语句

- for循环语句
- if-else判断语句

### agent模式

- @agent调用agent

### 保留关键字：

- 基础语句：condition_judge、exit、code
- 高级语句：IF、elif、else、END、FOR
- agent模式：agent

### 说明

- 大小写敏感
- 需要明确的缩进，4个空格
- 使用@符号调用各语句时，必须使用->或>>接收返回值，如果没有返回值则"->None"
- 执行过程中产生的所有变量都会被存入全局变量池，作为agentic workflow的中间结果

## 1. 变量标识符

- 变量以数字字母下划线组成并且不能以数字开头，要用`$variable`表示，如果变量后有其它数字、字母、下划线，需要在末尾加空格。
- 支持list的取值，但是要用`${}`包裹，例如`${variable[0]}`，（loop_block和judgment_block中的变量暂时不支持此方式）
- 支持dict和对象的取值，但是要用`${}`包裹，例如`${variable.key}`，（loop_block和judgment_block中的变量暂时不支持此方式）
- 所有的变量名最好不重名，重名会覆盖。尤其是for循环中的临时变量名，不支持和任何变量重名。

## 2. 赋值语句

- `->` 表示赋值
- `>>` 表示列表追加

tips: 使用 `>>` 会自动将变量类型转换为list

## 3. 五种基础语句

基础语句都以`@`开头，赋值 `-> / >> `结尾（下述语句仅使用`->`作为示例）

### 3.1. LLM调用语句

- 标识符：自然语言指令 `->` 结果变量名；
- examples：

  ```
  查一下上海的天气 -> climate
  根据${climate.status}写一首诗 -> poem
  把$poem发到我的邮箱 -> result
  ```

### 3.2. 函数调用语句

- 标识符：`@func_name(args, args=xxx) -> result`
- 规范：目前1⃣️位置参数和2⃣️关键字参数（顺序要求：位置参数必须要在关键字参数之前）
- examples：

  ```
  @serpapi_search($question) -> result
  @serpapi_search("后羿射日") -> result
  ```

### 3.3 代码块调用语句

- 标识符：`@code() -> result`

- 规范（代码块支持3种模式）：

- **模式1：**自定义python代码，适合临时注入，短小的代码补丁

  代码块需要使用三个反引号包裹，符合markdown规范，示例如下：

  ```
  @code(```python
      def add_one(a):
          return a+1
      python_res = add_one($a)
  ```) -> result
	```

- **模式2：**注入外部json数据，可以充当数据mock，灵活引入任务数据

   json数据块需要使用三个反引号包裹，示例如下：

  ```
  @code(```json
  {
      "status":"晴天",
      "humidity":"65%",
      "wind_speed":"5m/s"
  }
  ```) -> weather_schema
  ```

- **模式3：**输入自然语言

  直接输入自然语言即可，LLM会先理解任务，生成python代码，并且执行，拿到最终结果，赋值给result

  ```
  @code(计算一下10+89等于多少) -> result
  ```

### 3.4 条件判断语句

- 标识符：`@condition_judge($variable, [结果分类列表]) -> result`

- examples：

  ```
  @code(```json
  {"question": "在上海擅长劳动法的律师有哪些呢？",
  "content": "上海擅长劳动法的律师有张律师、李律师。徐律师也擅长劳动法但是在北京。"}
  ```) -> question
  
  @condition_judge(${question.question}, ["找律师", "找案件"]) -> condition_flag
  ```

### 3.5 exit退出语句

- 标识符：`@exit(msg="")`

- examples：

  ```
  @exit(msg="不玩啦，退出程序！")
  ```

## 4. 两种高级语句

### 4.1 循环语句

- 标识符：`FOR - END`
- 规范：以大写的`FOR`开头，大写`END`结尾。必须有明确的缩进（4个空格）
- examples：

```
FOR $item in $variable:
    根据$item写一首诗 -> result
    @func1_name(args1) -> result1
    @func2_name(args2) -> result2
END
```

### 4.2 条件判断语句

- 标识符：`IF - else - elif - END`

- 规范：以大写的`IF`开头，大写`END`结尾。必须有明确的缩进（4个空格）

- examples：

  ```
  @code(```json
  {"question": "在上海擅长劳动法的律师有哪些呢？",
  "content": "上海擅长劳动法的律师有张律师、李律师。徐律师也擅长劳动法但是在北京。"}
  ```) -> question
  
  @condition_judge(${question.question}, ["找律师", "找案件"]) -> condition_flag
  IF $condition_flag == "找律师":
      请根据参考信息回答问题：
      ${question.content}
      问题：${question.question}
  
      ## 限制
      不许捏造不存在的信息 -> result
  else:
      @serpapi_search($question) -> result
  END
  ```

## 5. agent语句

- 标识符：`@agent(type="", task="", roles={}, tools=[]) -> agent_name`

  - 参数type：`prompt-based`、`bambo`、`auto-decision`。（默认为`auto-decision`模式）
  - 参数task：用户任务，自然语言表述。（必填项）
  - 参数roles：主要给`bambo`使用
  - 参数tools：可以指定tools的范围。（默认使用全局变量池中的所有工具）

- 规范：以`@agent`开头，赋值语句结束，并且为该agent指定一个名称。
  - 运行之后agent会作为工具注册进全局工具池，key是agent_name，value是agent实例
  - 运行之后agent的结果也会保存进全局变量池，key是agent_name，value是agent运行过程中的message

- examples

  ```
  @agent(type="auto-decision", task="查一下上海的天气，根据天气情况写一首诗，并将结果发送到我的邮箱", tools=[]) -> weather_agent
  ```

- **Tips：**self-refine、self-reflection、self-critical、plan-and-execute都可以通过workflow配置出来。

## to do something

### (bp) debug功能

```
- 说明：
- 1. 断点工具用于调试，只能写在5种基础语句块之间，在程序运行到指定位置时，程序会暂停运行，并返回当前步骤的output和所有变量的状态值；
- 2. 继续执行时，需要附带所有的状态（因为prompt language是无状态的）
```

### 流式输出

各个阶段都支持流样式输出，交互友好。

