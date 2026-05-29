# 云服务器部署常见问题

## 1. Docker 构建超时

**现象：** `docker compose up -d --build` 超过 120 秒未完成

**原因：** 从 Docker Hub 拉取基础镜像（如 `python:3.11-slim`）在中国大陆速度慢

**解决：**
```bash
# 检查是否已配置镜像加速
cat /etc/docker/daemon.json

# 如未配置，添加 DaoCloud / 阿里云镜像
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://ud6340vz.mirror.aliyuncs.com"
  ]
}

# 重启 Docker 后生效
systemctl restart docker
```

## 2. Docker bind mount 文件不存在报错

**现象：**
```
Error: not a directory: Are you trying to mount a directory onto a file (or vice-versa)?
```

**原因：** docker-compose.yml 中 `volumes: - ./skills.db:/app/skills.db`，但 `skills.db` 被 `.dockerignore` 排除，源文件不存在。Docker 会创建一个同名目录，然后无法挂载到容器的文件路径。

**解决：** 改用 Docker 命名卷（named volumes）：
```yaml
volumes:
  - app-data:/app/data    # ✅ 挂载目录而非文件

volumes:
  app-data:               # 声明命名卷
```

在应用代码中用环境变量指定数据库路径：
```python
# models.py
DATABASE = os.environ.get('DATABASE', '/app/data/skills.db')
```

## 3. Flask 容器外无法访问

**现象：** 容器运行正常、端口映射正确，但 `curl http://IP:5050` 返回 `000` 或连接拒绝

**原因：** Flask 默认 `app.run()` 绑定 `127.0.0.1`，只接受容器内 localhost 连接

**解决：** 显式绑定 `0.0.0.0`：
```python
# app.py — 错误 ❌
app.run(debug=True, port=5050)

# app.py — 正确 ✅
app.run(host='0.0.0.0', port=5050, debug=False)
```

> 同时关闭 debug 模式（`debug=False`），生产环境不应开启。

**验证方法：**
```bash
# 登录服务器，先测试容器内 localhost
docker exec openclaw-skill-store curl -s localhost:5050

# 再测试宿主机 localhost（排除安全组问题）
curl -s localhost:5050

# 最后从外部测试（需要安全组已开放）
curl -s http://<公网IP>:5050
```

> **关键排查顺序：容器内 → 宿主机 → 外网。** 前两步通过但外网不通 = 安全组问题；前两步都不通 = 应用问题。

## 4. 阿里云安全组未开放端口

**现象：** 宿主机 `curl localhost:5050` 返回 200，但外部 `curl http://<IP>:5050` 超时

**原因：** 阿里云 ECS 默认安全组只开放 22/80/443 等常用端口

**解决：** 阿里云控制台 → ECS → 安全组 → 添加入方向规则：
```
端口范围: 5050/5050
协议: TCP
授权对象: 0.0.0.0/0
描述: OpenClaw Skill Store
```

## 5. 部署后文件更新不生效

**现象：** 本地修改了代码并 push GitHub，但服务器上运行旧代码

**原因：** scp 上传时被中断，或上传后未重建镜像

**解决：**
```bash
# 确认本地修改已推送
git push

# 上传单个文件到服务器
scp app.py root@<IP>:/opt/<项目名>/

# 重建并重启（关键：--build 才能应用新代码）
docker compose up -d --build
```

## 6. docker compose version 字段废弃警告

**现象：** `the attribute 'version' is obsolete, it will be ignored`

**解决：** 移除 docker-compose.yml 顶部的 `version: '3.8'` 行（Docker Compose v2+ 不再需要）

## 部署检查清单

部署完成后，按顺序验证：

```bash
# 1. 容器状态
docker ps | grep <项目名>

# 2. 容器日志（确认无报错）
docker logs <项目名> --tail 10

# 3. 容器内自检
docker exec <项目名> curl -s -o /dev/null -w "%{http_code}" localhost:<端口>

# 4. 宿主机自检
curl -s -o /dev/null -w "%{http_code}" localhost:<端口>

# 5. 外网访问（需安全组已放行）
curl -s -o /dev/null -w "%{http_code}" http://<公网IP>:<端口>
```

全部返回 200 即部署成功。
