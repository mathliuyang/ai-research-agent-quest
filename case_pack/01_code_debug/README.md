# Case 01: Code Debug Agent

这个案例用于展示普通聊天框和 IDE Agent 的区别。

## Demo goal

修复 `src/analyze_experiment.py`，让它读取 `data/experiment_log.csv`，并输出：

- `results/summary.csv`
- `results/trend.txt`

## Suggested flow

1. 先让 Agent 阅读项目结构。
2. 让 Agent 运行 `python src/analyze_experiment.py`。
3. 根据报错和异常输出定位问题。
4. 要求最小修改，不改变 CSV 字段含义。
5. 再次运行验证结果。

## Notes

`src/analyze_experiment_solution.py` 是参考答案，现场演示时可以先不打开。
