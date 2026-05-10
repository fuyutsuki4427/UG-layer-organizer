# UG Layer Organizer / NX 图层整理工具

[![NX 2406](https://img.shields.io/badge/NX-2406-blue)](https://www.plm.automation.siemens.com/)
[![Python](https://img.shields.io/badge/Python-3.x-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Siemens NX 2406 图层整理工具。一键将当前 Work Part 中**非实体、非组件**对象移动到 255 图层，快速清理模型中的曲线、草图、基准等辅助元素，保持模型树整洁。

---

## 功能

- **自动整理** — 扫描当前 Part 中所有可移动对象，将辅助元素归入 255 图层
- **类型判断** — 可靠区分 Solid Body 和 Sheet Body（基于 NXOpen API `IsSolidBody`/`IsSheetBody`）
- **组件保护** — 装配组件对象不会被移动
- **实体保护** — Solid Body 保持原图层不变
- **Undo 支持** — 操作通过 NX Undo Mark 包裹，可一键撤销
- **完整报告** — 在 NX Listing Window 中输出详细的分类统计报告
- **安全运行** — 不删除、不隐藏、不自动保存文件

## 不移动的对象

| 对象类型 | 原因 |
|---------|------|
| Solid Body（实体） | 破坏模型结构 |
| Assembly Component（装配组件） | 破坏装配关系 |
| 已位于 255 图层的对象 | 无需重复操作 |

## 移动到 255 图层的对象

- Curve（曲线）
- Sketch（草图）
- Datum Plane / Datum Axis / Datum CSYS（基准平面/轴/坐标系）
- Point（点）
- Sheet Body（片体）
- 其他非实体、非组件的 DisplayableObject

## 环境要求

- **Siemens NX 2406**（在 2406 版本上开发验证）
- **Python 3.x**（NX 2406 内置 Python 环境）
- **无需第三方库**（仅使用 NXOpen 和 Python 标准库）

## 使用方法

### 方法一：Journal 方式（推荐）

1. 打开 NX 2406
2. 在 NX 中打开或新建一个零件文件
3. 执行菜单：**File** → **Execute** → **NX Open...**
4. 选择 `nx_layer_organize.py`
5. 点击 **OK** 运行
6. 查看 **Listing Window** 中的运行报告

### 方法二：Journal Playback

1. 打开 NX 2406
2. **Tools** → **Journal** → **Play** (`Alt+F8`)
3. 选择 `nx_layer_organize.py`
4. 点击 **OK** 运行

### 方法三：Python 交互窗口

1. 打开 NX 2406
2. **Tools** → **Journal** → **Python**
3. 复制代码到交互窗口执行

## 输出报告示例

```
======================================================================
NX 图层整理工具 - 执行报告
======================================================================

【基本信息】
  工具版本: 1.0.0
  适用版本: NX 2406
  目标图层: 255

【部件信息】
  部件名称: test_part.prt
  完整路径: D:\NX\test_part.prt

【统计信息】
  扫描对象总数: 24
  成功移动数量: 18
  跳过对象数量: 5
  失败对象数量: 1

【对象检测】
  检测到装配组件: 是
  检测到实体对象: 是
  检测到片体对象: 是

【按类型统计 - 已移动】
  Curve: 8
  Sketch: 3
  DatumPlane: 4
  Point: 2
  Body(Sheet): 1

【按类型统计 - 已跳过】
  Body(Solid): 3
  Component: 2

【重要提示】
  ⚠ 本脚本未自动保存文件，请手动检查后再保存！
  ⚠ 如需撤销本次操作，请使用 NX 的撤销功能（Ctrl+Z）！
```

## 安全原则

> 此工具遵循 **安全优先** 的设计原则，第一版不包含以下操作：

- ❌ 不删除任何对象
- ❌ 不隐藏任何对象
- ❌ 不修改 Solid Body 所在图层
- ❌ 不修改 Assembly Component 所在图层
- ❌ 不自动保存文件
- ❌ 不递归处理子零件
- ✅ 只处理当前 Work Part

## 测试建议

1. **创建测试文件** — 不要在正式模型上直接测试
2. **准备测试对象** — 在不同图层创建实体、片体、曲线、草图、基准等
3. **运行脚本** — 观察 Listing Window 输出
4. **检查结果** — 确认实体和组件未被移动
5. **撤销测试** — `Ctrl+Z` 确认操作可撤销

## API 来源

本工具使用的 NXOpen API 全部来源于 **E:\NX2406\UGOPEN** 目录中的实际定义：

| API | 来源文件 |
|-----|---------|
| `Session.GetSession()` | `UGOPEN\pythonStubs\NXOpen\__init__.pyi` |
| `PartCollection.Work` | `UGOPEN\pythonStubs\NXOpen\__init__.pyi` |
| `DisplayableObject.Layer` | `UGOPEN\pythonStubs\NXOpen\__init__.pyi` |
| `Body.IsSolidBody` | `UGOPEN\NXOpen\Body.hxx` |
| `Body.IsSheetBody` | `UGOPEN\NXOpen\Body.hxx` |
| `Session.SetUndoMark` | `UGOPEN\pythonStubs\NXOpen\__init__.pyi` |

## TODO

- [ ] GUI 界面（选择目标图层/过滤对象类型）
- [ ] 递归处理装配子零件
- [ ] 导出 CSV 报告文件
- [ ] 预览模式（移动前显示列表）
- [ ] 多部件批量处理

## License

MIT
