# 结构性掉期  产品架构

## 产品组成
结构性掉期 = 期权 + 掉期。 通过卖出期权，获取期权费，将期权费补贴到掉期近端或远端，使得原掉期的一端有更好的价格。

注意：
```
1  默认补贴近端 
2  仅支持近端结汇、远端购汇
3  支持多期参数
```

对客户的直观价值:
- 掉期近端或者远端实际成交价比标准掉期更优
- 代价是承担期权被行权的风险

## 报价

### 1.1 正算报价
- 输入货币对、方向、近远端交割日、中收

- 1.1.1 获取 原始掉期:（nearBasePrice + swapBasePoint = farBasePrice）
- 1.1.2 获取 期权: 默认strike -> premPips（期权费）

### 1.2 反算报价 (strike)
- 输入货币对、方向、近远端交割日、中收 + 反算类型（delta、pips）
- 1.2.1 获取原始掉期
- 1.2.2 通过 delta或者 premPips(期权费) 反算 获取strike。
- 1.2.3 获取 strike -> premPips

### 1.3 公共计算逻辑

- 若补贴近端
结构性掉期 近端价格 nearPrice = nearBasePrice + premPips 
结构性掉期 掉期点 swapPoint = farBasePrice - nearPrice - profit
结构性掉期 远端价格 farPrice = nearPrice + swapPoint

- 若补贴远端
结构性掉期 远端价格 farPrice = farBasePric + premPips
结构性掉期 掉期点 swapPoint = farPrice - nearPrice - profit
结构性掉期 近端价格 nearPrice = farPrice - swapPoint

### 最终报价结果：
+ 掉期格式（nearPrice 近端, swapPoint 掉期点, farPrice 远端）
+ strike（行权价）、premPips（期权费）、补贴前折年化、补贴后折年化、补贴点数等 






 