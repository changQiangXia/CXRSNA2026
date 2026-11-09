# Baker12 timeout and current runtime risk

> 历史快照：文中的“当前”、`PENDING`、未提交等状态仅对应文首时间。
> 终盘状态见 [`final_submissions/README.md`](../final_submissions/README.md)。

**北京时间：2026-10-22 22:25 CST**

## 事实

```text
submission ref 57509367
kernel        rsna-knee-newtable-a5eff30-baker12 Version 1
dev           PASS
scoring       TIMEOUT
result        COMPLETE with no score
```

Baker12 是低成本 residual：20 个底座 cell 未改，只追加一个 A5 residual cell。
它仍然超时，说明瓶颈在 hidden rerun 的底座推理，而不是 residual 计算。

## 当前 allgold / allproxy 为什么更高风险

两者与 Baker12 共用同一套重底座，并额外增加：

```text
CoAtFull f0 K94        cap 90 min
f01soup75 K94          cap 90 min
R7-Coat384FT K24       cap 45 min
```

底座已经包含：

```text
Raptor main            3.5 h process cap
R224                   2.5 h process cap / 9 h global guard
stack + own reader     S6 gate at 4 h; own stage deadline 8.2 h
A5 worker              hard guard at 8.0 h
```

因此 Baker12 超时后，不能把 `dev PASS` 当作 `hidden runtime PASS`。
当前 allgold/allproxy 的隐含风险是：

```text
PASS      底座能在 8.5-9 h 内完成，且追加 child 被 deadline gate 跳过或很快完成
TIMEOUT   底座本身超过 9 h；追加 child 根本来不及触发
```

结合 Baker12 的直接反例，当前两发仍有较高风险；但不能把底座判成“必然
超过 9h”。2026-10-22 23:11 CST 的最新事实是：

```text
mm08 ref 57514882  COMPLETE public 0.959
```

因此底座确实能够完成，且 mm08 比 allgold/allproxy 少两段 child。
allgold/allproxy 的合理判断应改为：

```text
底座完成 + 后续 child 被 deadline 跳过/部分执行
    -> 仍可能出有效分，但分数可能退化到 fallback

底座 + 当前 child 仍越 9h
    -> TIMEOUT
```

所以它们是“有条件可完成”，不是必然超时；仍需看真实的 hidden 回执。

## 下一步原则

不再提交“重底座 + 多个追加 child”的变体。要保分必须换成：

1. **替换而非追加**：用更轻的 f01/R384 替换某个重分支。
2. **降低 K/TTA**：优先单 pass K24，关闭 mirror pair TTA。
3. **减少 K94 名额**：保留一个强主干，其他分支改成低 K 或跳过。
4. **全局预算内建**：把 hard deadline 从 8.0 h 降到 7.0-7.5 h。
5. **runtime-first 验证**：在 hidden-like 规模上先测完整耗时，再谈分数。

## 当前 pending

```text
allgold  ref 57525829  kernel V6  PENDING
allproxy ref 57525824  kernel V4  PENDING
```

它们已经提交，配额已消耗。保留观察；若同样超时，就按上述 runtime-first 路线重做，
不再向该底座追加 child。
