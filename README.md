# JOMOO SQ9650 for Home Assistant — 0.1.1 验证版（统一 domain：jomoo_ha）

> 未经真实 SQ9650 / 冬瓜 HAOS 测试。只供个人实验，不保证兼容或设备动作执行。不是九牧官方集成。

## 当前功能
- 手动填写马桶 BLE 地址，使用 HA 内置 Bluetooth 管理器连接（不是独立 BLE 扫描器）
- 按需连接、监听 FFE1 通知、查询 0x30 状态、自动断开
- `button.查询状态`，`switch.夜灯（上次查询）`，`sensor.座温档位（上次查询）`
- 不开启自动轮询，不占用官方小程序的常驻连接；只在明确操作时连接
- BLE 写入无法证明物理动作完成；有通知+对应夜灯状态时才确认控制成功
- 暂不开放冲水、翻盖、翻圈、脚感、加热设定等机械动作与高风险操作

## 前提
1. 在 HA 的“设置 → 连接 → 蓝牙 → 适配器”看到本地、可主动连接的蓝牙适配器
2. 在蓝牙广播监视器或其他可信来源，取得**你自己** SQ9650 的 BLE 地址
3. 官方微信小程序先断开与马桶的 BLE 连接
4. 使用设备时不要有人正在使用马桶，先在现场测试夜灯
5. 先创建完整 HA 备份；升级固件之前另行查验固件适配（本项目不需要刷机）

## 安装
1. 下载 `jomoo_ha_ha_install_v0.1.1.zip`，解压后将其中的 `jomoo_ha/` 整个目录放进 HA 的 `/config/custom_components/`，不要增加额外父目录。
   - 或者在 `/config/custom_components/` 直接 `git clone https://github.com/sorrymakeeeer/JOMOO_HA.git jomoo_ha`（适用于本仓库这种代码直接在根目录的结构）。
   - **请勿**把 GitHub 自动生成的 `JOMOO_HA-main/` 或其他 ZIP 名称当成 HA 集成目录。
2. 核对 `/config/custom_components/jomoo_ha/manifest.json` 中 `domain` 为 `jomoo_ha`，且同一目录有 `config_flow.py` 和 `const.py`；再重启 Home Assistant Core
3. `设置 → 设备与服务 → 添加集成`，搜索 `JOMOO SQ9650 (Experimental)`
4. 输入**你自己**马桶的 BLE 地址，格式 `AA:BB:CC:DD:EE:FF`
5. 设备添加后先点 `查询状态`；若显示原始座温档位，再测试夜灯开/关
6. 通过“设置 → 系统 → 日志”查看相关报错；BLE 无响应不等于设备必然未执行

可使用 File editor / Studio Code Server 添加文件，不需要在 HAOS 宿主系统 pip 安装软件。项目用到了 Home Assistant 本身依赖的 bleak。

## 升级方向
- 在取得真机 0x30 状态响应后补全状态解析与确认机制
- 在确认座温档位映射后加入 `select` 实体和 HA 定时策略
- 完善配置流、重试策略、异常处理；针对 OH2P 的小爱桥接单独验证

## 原始协议和许可证
协议格式参考 <https://github.com/caokang1997/JMGatt_client> 的公开说明。原仓库是否允许复制、发布或重新许可需要再确认；本验证版没有搬运其 ESP32 原始源码，未替原作者授予任何许可证。

## 测试
`python -m unittest discover -s tests -v`
仅覆盖纯 Python 协议单元测试，不包括实机 BLE/HA 集成测试。

## 命名一致性（避免 Invalid handler specified）
- 文件夹：`/config/custom_components/jomoo_ha/`
- `manifest.json`：`"domain": "jomoo_ha"`
- `const.py`：`DOMAIN = "jomoo_ha"`
- `config_flow.py` 使用 `domain=DOMAIN` 注册配置向导
- 之前安装过其他名字的测试目录时，先备份并移走旧目录，避免两个副本同时被加载。
- 在 HA Core 中添加新集成不会修改仓库；如果通过旧的 GitHub ZIP 重新下载，会重新引入旧的代码，所以先更新你自己的 GitHub 仓库。
