# Sana 手部修复研究总结

[在线阅读](https://wangwei64.github.io/sana-hand-repair-research/)

整理日期：2026-11-17。最近一轮已归档完整实验：2026-11-05。

本报告汇总数据构建、真实轨迹回退、独立纠错模块、方向搜索、旧 LoRA 修正场、官方 inpainting、Good 加噪诊断、综合评分器以及最新 Good 去噪 LoRA SFT。21 行路线是主要阶段归纳，不等于独立实验或独立样本数。

内容包括 7 张数据图表、数据构建和评分模块流程、31 份研究证据公开副本，以及全部最新开发 8 组 × 10 seed 的同条件图像对照。还可切换 128 / 256 更新各 8×2 个开发候选和最终训练示例 8×2 个候选。

## 文件与来源

- `index.html` / `style.css` / `app.js`：无第三方运行依赖的静态页面。
- `data.json`：经过整理的图表、路线、图库、分数及既有视觉记录。
- `evidence/`：原记录的公开副本，已去除机器路径。原文件哈希与公开副本哈希分别记录。
- `assets/`：565 张已有展示预览，约 7.9 MB；整图 WebP 为 384px、手部上下文为 512px，另有旧端点模型的 JPEG 对照。这些不是无损原始 PNG。
- `publication-manifest.json`：所有展示图的 SHA256、大小与证据来源。
- `validation.json`：发布完整性校验及对图库分数的独立重算结果。

原始实验文件、完整训练数据与模型权重留在研究工作区。本次只整理已归档记录，没有重新训练、重新生成候选或打开确认集。网页图像沿用原预览文件，不经过生成式重绘。

## 统计解释

4,454 对是人工采用配对数据资产；最新 SFT 实际只训练 64 对。训练集拟合、像素误差改善、评分升高和骨架检出都不能直接写成解剖成功率。Good 表示历史人工采用，不保证每个关节或姿态均无歧义。

最新 80 对开发图共享 8 个 prompt 组，使用相同 seed 做原模型与 LoRA 比较。分数来自冻结的统一评分器，只参与生成后的排序，不是训练奖励。所有新生成结果的视觉文字是既有助手初筛，未开展独立人工成功率评测。历史 test 与多次复用的开发数据不称新盲测。

## 构建与检查

从仓库根目录运行（Python 标准库即可）：

```bash
python3 scripts/export_hand_research.py --workspace /path/to/research
python3 scripts/validate_hand_research.py
node --check docs/app.js
python3 -m http.server 18810 --bind 127.0.0.1 --directory docs
```

导出需要原研究工作区。普通浏览不需要工作区、模型或 GPU；GitHub Pages 从 `main` 分支的 `docs/` 发布。

引用上游实现仅说明采用或参考范围，不声称复现 RealGen、DIAMOND 或 HandCraft 完整系统。

本报告单独发布于公开仓库 `wangwei64/sana-hand-repair-research`。旧人像对照仓库的当前可见性为 private，账户尚不能为其启用 Pages；本次没有改变旧仓库权限，也未复制它的原始照片、完整数据或提交历史。历史建设记录中的旧网址保留作为归档内容，不表示该旧站点当前仍在线。
