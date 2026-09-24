# 公开源码快照

本仓库是 `legalDesign` 当前源码的单次公开快照，不包含原私有仓库的提交历史。
公开前已检查常见密钥文件和凭据模式；这不等同于安全审计，也不表示服务可直接用于生产。
请在本地按 `.env.example` 配置自己的环境变量，**不要提交真实密码、令牌或用户数据**。

为避免将来源和授权状态不明的大型案例数据或运行日志公开，`services/lawshow/data*.json` 使用明确标注的空结构，`services/qa/ragtest/inputs/reports/logs.json` 未收录；需要相关功能时请自行准备合法的数据。首次创建管理员必须设置 `ADMIN_DEFAULT_PASSWORD`。
