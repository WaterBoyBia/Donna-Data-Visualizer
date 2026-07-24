# 曲线图边框显示规则实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 单曲线图隐藏顶部和右侧边框，双曲线图仅隐藏顶部边框，并保证界面预览与保存图片一致。

**Architecture:** 边框规则集中在 `plotter.create_plot()` 中，通过 Matplotlib `spines` 控制可见性。GUI 继续复用该函数返回的 Figure，不增加界面层分支。

**Tech Stack:** Python 3.12、Matplotlib 3.10、NumPy 2.4、pytest；测试仅使用 `donna` 虚拟环境。

---

### Task 1: 为单曲线和双曲线边框规则补充回归测试

**Files:**
- Modify: `tests/test_plotter.py:20-36`
- Test: `tests/test_plotter.py`

- [ ] **Step 1: 添加单曲线边框测试**

在 `TestCreatePlot` 中添加：

```python
def test_single_series_hides_top_and_right_spines(self):
    x = np.array([0, 1, 2])
    y_series = [np.array([1, 2, 3])]
    labels = ["Signal"]

    fig = create_plot(x, y_series, labels)

    assert len(fig.axes) == 1
    ax = fig.axes[0]
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
```

- [ ] **Step 2: 添加双曲线边框测试**

在 `TestCreatePlot` 中添加：

```python
def test_multiple_series_hides_only_top_spines(self):
    x = np.array([0, 1, 2])
    y_series = [np.array([1, 2, 3]), np.array([4, 5, 6])]
    labels = ["A", "B"]

    fig = create_plot(
        x,
        y_series,
        labels,
        y_labels=["Left signal", "Right signal"],
    )

    assert len(fig.axes) == 2
    ax1, ax2 = fig.axes
    assert not ax1.spines["top"].get_visible()
    assert not ax2.spines["top"].get_visible()
    assert ax2.spines["right"].get_visible()
    assert ax2.get_ylabel() == "Right signal"
```

- [ ] **Step 3: 在 donna 环境验证新测试按预期失败**

Run:

```powershell
& 'D:\miniconda\envs\donna\python.exe' -m pytest tests/test_plotter.py -k 'spines' -v
```

Expected: 两个新测试均因顶部边框仍可见而失败；失败发生在 `spines["top"].get_visible()` 断言，而不是导入或测试配置错误。

### Task 2: 在绘图入口实现按曲线数量控制边框

**Files:**
- Modify: `plotter.py:51-98`
- Test: `tests/test_plotter.py`

- [ ] **Step 1: 隐藏主坐标轴顶部边框，并在单曲线时隐藏右侧边框**

在 `fig, ax1 = plt.subplots()` 后添加：

```python
ax1.spines["top"].set_visible(False)
if len(y_series) < 2:
    ax1.spines["right"].set_visible(False)
```

- [ ] **Step 2: 双曲线时隐藏右侧坐标轴顶部边框**

在 `ax2 = ax1.twinx()` 后添加：

```python
ax2.spines["top"].set_visible(False)
```

右侧坐标轴的 `right` spine、刻度和 Y 轴标签保持现有默认可见状态。

- [ ] **Step 3: 在 donna 环境验证新增测试通过**

Run:

```powershell
& 'D:\miniconda\envs\donna\python.exe' -m pytest tests/test_plotter.py -k 'spines' -v
```

Expected: `2 passed`。

- [ ] **Step 4: 运行绘图模块测试**

Run:

```powershell
& 'D:\miniconda\envs\donna\python.exe' -m pytest tests/test_plotter.py -v
```

Expected: 新增边框测试通过；若旧的默认标题断言仍失败，则记录为已知的既有测试与当前默认参数不一致，不在本次视觉改动中修改。

- [ ] **Step 5: 运行完整测试套件**

Run:

```powershell
& 'D:\miniconda\envs\donna\python.exe' -m pytest tests -v
```

Expected: 新增边框测试及其他现有有效测试通过；如仍出现 CSV 支持状态或默认标题的既有断言失败，明确报告具体测试名，不将其描述为本次改动造成的回归。

### Task 3: 核对改动范围

**Files:**
- Inspect: `plotter.py`
- Inspect: `tests/test_plotter.py`

- [ ] **Step 1: 检查差异**

Run:

```powershell
git diff -- plotter.py tests/test_plotter.py docs/superpowers/specs/2026-07-24-plot-spines-design.md docs/superpowers/plans/2026-07-24-plot-spines.md
```

Expected: 生产代码只包含三个 `spines` 可见性设置，测试只包含两个边框规则测试；设计和计划文档为中文说明。

- [ ] **Step 2: 确认未执行 Git 写操作**

不运行 `git add`、`git commit`、`git push` 或任何分支操作，版本控制交由用户手动完成。
