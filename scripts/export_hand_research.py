"""Build a public, read-only research report from the frozen local records.

Run: python3 scripts/export_hand_research.py --workspace /path/to/research
No model calls, training, or source dataset mutations. Only curated evidence and
already-created display previews are published; original files remain untouched.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--workspace', type=Path, required=True)
args = parser.parse_args()
root = args.workspace
out = Path(__file__).resolve().parents[1] / 'docs'
(out / 'evidence').mkdir(parents=True, exist_ok=True)
(out / 'assets').mkdir(exist_ok=True)
sources = []


def read(name):
    return json.loads((root / name).read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clean(value):
    if isinstance(value, dict):
        return {clean(k): clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, str):
        value = re.sub(r'/root/[^\s"<>，。；）]+', '[server-path]', value)
        value = re.sub(r'/home/[^\s"<>，。；）]+', '[local-path]', value)
        value = re.sub(r'http://127\.0\.0\.1:\d+[^\s"<>）]*', '[local-preview]', value)
        value = re.sub(r'root@connect\.[^\s"<>；]+', '[remote-host]', value)
        return value
    return value


def evidence(key, title, name, select=None):
    src = root / name
    value = read(name) if src.suffix == '.json' else src.read_text()
    if select is not None:
        value = select(value)
    body = {'title': title, 'source': name, 'source_sha256': sha(src),
            'publication_note': 'Curated and path-redacted snapshot. Source hash refers to the original local artifact.',
            'content': clean(value)}
    path = out / 'evidence' / (key + '.json')
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + '\n')
    sources.append({'id': key, 'title': title, 'path': 'evidence/' + path.name,
                    'source': name, 'source_sha256': sha(src), 'public_sha256': sha(path)})
    return value


dataset = evidence('dataset', '人工采用配对数据快照', 'deliverables/hand-pairs-reviewed-20261028/statistics.json')
evidence('generation', '10,000 张原始生成数据的固定流程', 'sana-hand-dataset-1000x10/README.md')
evidence('baseline', '已发布的人像基线与原生去噪图册', 'portrait-comparison-github-site/README.md')
evidence('batch', '双方法候选批次与人工筛选范围', 'sana-hand-batch-repair-20261023/RUNNING.txt')
evidence('pair-protocol', '配对数据的 Mask、来源和标注语义', 'deliverables/hand-pairs-reviewed-20261028/README.txt')
evidence('vae', '200 对 VAE 表达能力与局部性诊断', 'deliverables/sana-vae-validation-200-20261028/report.txt')
evidence('oracle', '20 对真实轨迹 Oracle 干预', 'deliverables/sana-oracle-20-20261028/report.txt')
evidence('timing', '20 对回退时刻实验结论', 'sana-hand-rollback-timing-20261029/conclusion.json')
evidence('early-controller', '早期纠错外挂的试跑门槛', 'deliverables/sana-cfg-corrector-20261028/scaleup_decision.json',
         lambda d: {k: d[k] for k in ['engineering_path_verified','pilot_quality_gate_passed','engineering_evidence','pilot_results','decision']})
evidence('direction-rounds', '方向搜索与编辑前瞻：前四轮总结', 'hand-direction-search-20261101/output/conclusions.json')
state = evidence('direction-final', '独立辅助模块：最后已完成状态', 'hand-direction-search-20261101/output/research_state.json',
         lambda d: {k: d[k] for k in ['updated_at','batch_status','generator_retrained','reliable_anatomy_correction_achieved','output_records','frozen_editor_proposals','main_unresolved','completed_phase2']})
evidence('direction-log-final', '离散轨迹四组消融的完成证据', 'hand-direction-search-20261101/phase2/WORKLOG.txt',
         lambda s: s[s.rfind('2026-11-04T05:51:55'):])
evidence('provenance', '历史测试与确认集的来源更正', 'hand-direction-search-20261101/output/phase2/data_provenance_summary_20261104.json')
evidence('lora-history', '旧 LoRA 各阶段完整结果记录', 'sana-hand-lora-pilot-20261104/RESULTS.md')
evidence('lora-frozen', '旧 LoRA 最终冻结权重与停止状态', 'sana-hand-lora-pilot-20261104/RESEARCH_STATE.json',
         lambda d: {k: d[k] for k in ['phase11_completed','phase12_completed','phase13_completed','phase14_training_stopped','phase14_completed','user_stop']})
direction = evidence('direction-diagnostic', '210 对端点模型：方向与幅度诊断', 'sana-hand-lora-pilot-20261104/diagnostics/phase14_direction3360_reproducible/result.json')
inpaint = evidence('inpaint', '官方 inpainting：8 组 × 10 噪声', 'sana-official-inpaint8x10-20261105/SUMMARY.json')
noise = evidence('good-noise', 'Good 加噪还原诊断', 'sana-good-noise8-20261105/SUMMARY.json')
evidence('ranker', '第一版 DINO 偏好评分器', 'hand-quality-ranker-20261105/RESULTS.md')
evidence('composite', '人工选择与 DiffDoctor 融合对照', 'hand-reward-composite-20261105/MODEL_CARD.json')
evidence('skeleton', '手骨架诊断结果', 'hand-skeleton-eval-20261105/STATE.json',
         lambda d: {k: d[k] for k in ['status','record_count','human_cases','findings','decision','trained_parameters','generator_updates']})
evidence('fusion', '骨架、图像与伪影融合试验', 'hand-reward-fused-20261105/SUMMARY.json')
evidence('handcraft', 'HandCraft 冻结检测器评估', 'handcraft-detector-eval-20261105/SUMMARY.json')
scorer = evidence('unified', '四模块统一评分器及对照', 'hand-quality-unified-20261105/SUMMARY.json')
evidence('unified-protocol', '统一评分器：特征、划分及训练协议', 'hand-quality-unified-20261105/EXPERIMENT.json')
evidence('sft-results', 'Good 去噪 LoRA + inpainting：最终结论', 'sana-lora-inpaint-sft-20261105/RESULTS.md')
evidence('sft-protocol', 'SFT 开跑前固定协议（不是当前运行状态）', 'sana-lora-inpaint-sft-20261105/EXPERIMENT.json')
delivery = evidence('sft-check', 'SFT 交付检查、分数和耗时', 'sana-lora-inpaint-sft-20261105/DELIVERY_CHECK.json')
scores = evidence('scores', 'SFT 全部同种子分数', 'sana-lora-inpaint-sft-20261105/SCORE_COMPARISON.json')
visual = evidence('visual', 'SFT 逐图助手视觉记录', 'sana-lora-inpaint-sft-20261105/VISUAL_NOTES.json')
evidence('labels', 'SFT 64 训练 / 8 开发的人工来源检查', 'sana-lora-inpaint-sft-20261105/HUMAN_LABEL_AUDIT.json')

review = read('sana-lora-inpaint-sft-20261105/review/data.json')
gallery = []
asset_manifest = []
for group in review['groups']:
    records = []
    for r in group['records']:
        if 'review_assets' not in r:
            continue
        assets = r['review_assets']
        for name in [assets['full']] + assets['crops']:
            src = root / 'sana-lora-inpaint-sft-20261105/review' / name
            target = out / name
            shutil.copyfile(src, target)
            asset_manifest.append({'path': name, 'sha256': sha(src), 'bytes': src.stat().st_size})
        records.append({k: r[k] for k in ['variant','seed','review_assets','score'] if k in r})
    notes = next(n for n in visual['groups'] if n['split'] == group['split'] and n['group'] == group['group'])
    gallery.append({'split': group['split'], 'group': group['group'], 'sample_id': group['sample_id'],
                    'prompt': group['prompt'], 'records': records, 'notes': notes})

old = 'sana-hand-lora-pilot-20261104/review/phase14_final3360/development_000_hf-971cb9020d6c662f_seed2026102203_hand0.jpg'
shutil.copyfile(root / old, out / 'assets/endpoint210-development.jpg')
asset_manifest.append({'path': 'assets/endpoint210-development.jpg', 'sha256': sha(root / old), 'bytes': (root/old).stat().st_size})

# Ordered research ledger. All values below are annotated interpretations of the
# linked frozen records; plans are kept separate from completed experiments.
routes = [
 ['2026-10-08—15','基线','生成与去噪观察','人像模型比较、Sana 原生 20 步轨迹图册','既有 300 组人像对照；图册 16 prompt / 26 案例','保存基线、生成参数和阶段图，定位手部数量、连接与接触问题。图册是观察材料，不是修复实验。','背景建设','baseline'],
 ['2026-10-22—28','数据','原图生成 → 定位 → 人工配对','Sana → MediaPipe / DWPose / DiffDoctor → Qwen / RealisHuman → 人工三选一','10,000 原图；6,425 固定候选；4,454 人工采用配对','形成 Bad / Good / Mask / 原 Prompt / Seed / 来源快照。Good 表示人工采用，未等同逐指结构金标准。','已交付','dataset'],
 ['2026-10-28','诊断','VAE 能否表达正确手','Bad / Good 编码与重建、局部残差','200 对；36 手定向视觉抽查','29 个裁剪未见明确新增结构错误，7 个无法判断。说明部分 Good 可由现有 DC-AE 表达；不能直接证明可从 Bad 预测。','机制支持','vae'],
 ['2026-10-28','诊断','真实轨迹 Oracle 注入','已知 Good 残差注入第 10 / 15 / 18 步','20 对；120 主干预输出；60 个零干预精确续跑','较晚注入多例更贴近 Good，但第 10 步可出现新缺陷；读了 Good，只是离线机制试验。','有参考有效','oracle'],
 ['2026-10-28—29','回退','连续回退引导与时刻选择','参考流反馈、状态 / 求解器历史桥接','20 对 × 17 条件 = 340 干预输出','10–18 步持续引导平均 LPIPS 0.07636；15–16 两次引导为 0.10159。没有证实统一“错误尚未形成”的窗口。','有参考有效','timing'],
 ['2026-10-28','外挂','小型残差 / CFG 纠错器','从 Bad 预测局部 latent 修正，原 Sana 冻结','4 对记忆检查；16 验证案例的双模型 pilot','4 对残差 loss 可降 99.6%，验证两模型相对 LPIPS 改善均为负，未通过质量门槛。','开发失败','early-controller'],
 ['2026-10-29—11-01','外挂','DiT / 原生流 / 学生状态训练','独立纠错网络、真实回放、学生访问状态再标注、空间特征','4 对工程验证、512 对 pilot 等多轮；后续 469 例复用验证','工程拟合可行，后续 20 epoch 纠错网络在 469 例相对 LPIPS 改善 −21.86%，结构审查失败。不能用训练拟合代替开发效果。','泛化失败','direction-rounds'],
 ['2026-11-01','搜索','奖励选路与编辑前瞻','局部候选搜索 → 冻结编辑器提案 → 原 Sana 续采样','24 例搜索；8 例匹配前瞻；4 例裁剪归属','清晰前瞻使匹配 8 例桥接 LPIPS 改善由 −29.32% 到 +8.60%；95% 区间跨零，仍有残影、姿态改变。','局部收益','direction-rounds'],
 ['2026-11-01—03','搜索','结构提案与多种接回方式','检索、骨架 / HaMeR、SAM 轮廓、意图约束、隐藏层与端点干预','多轮固定小样本对照；与真实原生轨迹分别核查','单例参考姿态可改善手形，但共享自动流程仍有目标归属、旧指残影、接触及纹理问题；没有独立确认结果。','未形成稳定方法','direction-final'],
 ['2026-11-03—04','外挂','原生求解器一致的离散动作监督','直接监督实际下一步状态修正；状态分布 × 损失归一化','32 训练组；8 复用内部组；4 臂各 2,400 更新；80 输出','训练方向余弦约 0.92–0.96，内部约 0.09–0.15；四臂内部 8 例均无明确结构修复。混合状态没有解决迁移。','泛化失败','direction-log-final'],
 ['2026-11-04','LoRA','标准 FM / 配对 bridge','随机加噪的去噪监督或 Bad–Good bridge，局部采样','首轮 64 训练 / 8 验证；各 128 更新；后续 512 对组合对照','首轮 8 步 bridge MAE 33.80、原模型 34.44、Bad 28.56。更接近老师一点，不代表手部结构修好。','未通过结构检查','lora-history'],
 ['2026-11-04','LoRA','直接 Correction Flow','同一 Sana 启用 / 关闭 LoRA 的输出差；不加随机噪声','8 对能力探针、源条件和 T50 消融；512 对止于 1,536','T50 强化训练拟合；开发仍错误连接、模糊和残影。原计划 2,048 未完成，没有对应权重。','提前止损','lora-history'],
 ['2026-11-04','LoRA','少步 / 整图与裁剪对照','固定 CF 比较 1 / 2 / 4 / 8 步；纯 Bad 一步端点','同一 1,536 权重；64 对整图 / 裁剪各 512 更新','一步 MAE 更低但主要平滑；整图和裁剪均未学到可靠 Good 手形。不是蒸馏。','结构失败','lora-history'],
 ['2026-11-04','LoRA','端点模型容量与曝光诊断','8 对过拟合；64 对延长到 2,048；同 prompt 新图','8 对 / 512；64 对 / 2,048；32 同 prompt 不同 seed','8 对训练可贴近 Good，开发失败；64 对部分训练拟合，32 同 prompt 新图也无可信迁移。','能拟合，未泛化','lora-frozen'],
 ['2026-11-04','LoRA','210 对多种子扩充','同 64 个 prompt 的 64 原对 + 146 新 seed 对','完整权重冻结 3,360；210 训练 + 32 开发 + 32 诊断','部分训练近 Good，另有严重未拟合；开发仍失败。停止前日志 3,704 不等于正式权重；原 6,720 计划未完成。','提前止损','lora-frozen'],
 ['2026-11-04','诊断','210 对模型方向 / 幅度分析','预测残差与 Good 目标的离线几何比较','训练探针 8 + 开发 32 + 同 prompt 32','开发残差放大 2 倍反而更差；即使用 Good 选最佳非负幅度也有残余误差。不是单纯“力度不足”。','排除单一解释','direction-diagnostic'],
 ['2026-11-05','重绘','官方 masked inpainting','原 Sana 官方遮罩求解器 + 反演 / 新噪声 / 逐步约束','8 组 × 10 新噪声；不改 Prompt / Mask；不训练','能生成不同手形，部分更清楚，但结果依赖种子，动作 / 接触不稳；硬回贴还会截断新手形。','有变化，不稳定','inpaint'],
 ['2026-11-05','诊断','给 Good 加噪后还原','原生 flow 部分加噪：0 / .25 / .50 / .75','8 组 × 3 噪声程度 + 8 个 VAE 基线','低噪声保留部分正确结构，高噪声增加形状 / 接触漂移。输入本来就是 Good，不能叫 Bad 修复。','机制诊断','good-noise'],
 ['2026-11-05','评分','DINO → 人工选择 / 伪影 / 骨架融合','冻结特征、小型偏好头、同来源与压力测试','第一版实际训练 3,179 对；多版固定对照','历史 Good > Bad 准确率高，简单颜色纹理统计也达 91.6%；加入 DiffDoctor / 骨架未显示稳健收益。','有来源偏差风险','ranker'],
 ['2026-11-05','评分','HandCraft 与四模块统一打分','DINO + DiffDoctor + MediaPipe + HandCraft → 893→64→1','599 fit / 149 calibration prompt 组；开发 444 张 / 63 组','开发平衡准确率 70.2%，坏样本召回 52.3%；“好 / 坏”是对人工采用标签的预测，不是解剖认证。','辅助排序','unified'],
 ['2026-11-05','LoRA','Good 去噪 SFT + 官方 inpainting','原生 flow 目标训练 attention LoRA；冻结评分器排候选','64 训练 / 8 开发；512 更新；80 同 seed 开发对照','开发分数 24.15→29.51，有局部形状改善，也有拳头膨大、截断和手区画出人脸；尚未形成稳定修复器。','当前交付','sft-results'],
]

payload = {
 'version': 1, 'report_date': '2026-11-17', 'last_completed_experiment': '2026-11-05',
 'scope': 'Sana-0.6B 手部修复研究；根据截至整理日的已归档证据总结，不恢复训练。',
 'dataset': {k: dataset[k] for k in ['accepted_pairs','methods','unique_prompts','target_hands','hand_records','outside_mask_changed_pixels_total']},
 'routes': [dict(zip(['date','family','name','method','scale','result','status','source'],r)) for r in routes],
 'noise': noise['metrics_not_success_rates'],
 'direction': {k: {'n': v['n'], 'summary': v['summary']} for k,v in direction['groups'].items()},
 'scorer': {k: {'classification': v['dev']['classification'], 'stress': v['stress']} for k,v in scorer['comparison'].items()},
 'score_groups': scores['groups'], 'delivery': clean(delivery), 'gallery': gallery,
 'intermediate_reviews': {'step00128': visual['intermediate128'], 'step00256': visual['intermediate256']},
 'sources': sources,
 'not_completed': ['未形成独立确认的稳定手部修复器','未把约 4,500 对数据用于最新 LoRA 全量训练','未训练以评分器为奖励的 GRPO / RL，也未将最高分候选自动回灌为 Good','33 通道 Mask patch-LoRA 对照仅设计，未实现或开跑','confirm32 未用于当前候选调参；历史 test 和重复开发集不称全新盲测'],
 'review_policy': '助手视觉初筛与人工历史采用标签分开；没有新生成结果的独立人工成功率。',
}
(out / 'data.json').write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n')
(out / 'publication-manifest.json').write_text(json.dumps({'report_date': '2026-11-17','assets': asset_manifest,'sources': sources,'privacy': 'No credentials, server configuration, model weights, or full dataset copied. Display previews only.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'sources':len(sources),'routes':len(routes),'gallery_groups':len(gallery),'preview_assets':len(asset_manifest),'preview_bytes':sum(x['bytes'] for x in asset_manifest)},ensure_ascii=False))
