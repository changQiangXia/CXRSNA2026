# mm08 online result

> 历史快照：文中的“当前”、`PENDING`、未提交等状态仅对应文首时间。
> 终盘状态见 [`final_submissions/README.md`](../final_submissions/README.md)。

**北京时间：2026-10-22 23:11 CST**

## 回执

```text
candidate   RSNA Knee A5eff30 CoAtFull stable11 mm08
ref         57514882
status      COMPLETE
public      0.959
```

用户观察到的高精度排序：

```text
A5eff30-only V1 > mm08
mm08 > A5eff20-only V1
```

因此系统当前选中的我方 top-two 变为：

```text
1  intoxicatinglips/rsna-knee-newtable-a5eff30-only V1
2  intoxicatinglips/rsna-knee-a5eff30-coatfull-stable11-mm08 V1
```

A5eff20-only 退出当前 top-two，保留为已验证的历史 fallback。

## 解释

- mm08 的 Medial Meniscus `.08` 增量没有超过 A5eff30-only anchor；
- 但它高于 A5eff20-only，因此成功替换了旧的第二候选；
- 三个候选显示分同为 `0.959`，排序来自未显示的更高精度；
- mm08 没有赢得第一位，不应把“被选中”误写成“超过 anchor”。

## 运行期修正

此前根据 Baker12 timeout 推断“重底座必然超时”过于粗糙。现在的事实是：

```text
Baker12   timeout
mm08      COMPLETE and selected
```

两者说明同一底座存在明显运行方差。最终候选仍应坚持：

```text
零额外模型前向
明确 deadline
exact fail-open
不追加新的 CoAt/R384 child
```

## 对 A5eff30 R150 dev 的含义

A5eff30 R150 的计算链比 mm08 更短：它不包含 CoAtFull child，只修改
既有 reader 权重。mm08 能完成提高了 R150 dev 可完成的信心，但不构成
runtime guarantee；仍以实际 dev 回执为准。
