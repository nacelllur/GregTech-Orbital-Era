# GitHub 发布与邀请协作者指南

> 本地仓库已初始化完毕（commit `73d3ce4`，1877 文件，分支 `main`）。
> 以下步骤需要你本人操作，因为涉及 GitHub 账号认证。

---

## 第一步：安装 Git（如果尚未安装）

你的系统里已有便携版 Git（路径：`C:\Users\23737\.workbuddy\binaries\PortableGit\versions\1.2.0\cmd\git.exe`），但不在系统 PATH 中。

**推荐方案**：安装完整版 Git for Windows，这样资源管理器右键菜单也会有 Git 选项。

1. 打开 https://git-scm.com/download/win
2. 下载 **64-bit Git for Windows Setup**
3. 安装时一路 Next 即可（默认选项就行）
4. 安装完成后，**重新打开终端**，运行 `git --version` 确认

---

## 第二步：配置 Git 用户信息

打开 **PowerShell** 或 **Git Bash**，运行：

```bash
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的GitHub邮箱"
```

例如：
```bash
git config --global user.name "octocat"
git config --global user.email "octocat@github.com"
```

---

## 第三步：在 GitHub 上创建仓库

1. 登录 https://github.com
2. 点击右上角 **+** → **New repository**
3. 填写信息：
   - **Repository name**: `gregtech-orbital-era`（或你喜欢的名字）
   - **Description**: `格雷科技：星环纪元 - Minecraft 1.20.1 GregTech 整合包`
   - **Visibility**: **Private**（私有，只有你和邀请的人能访问）
   - **不要**勾选 "Add a README file"（我们已经有了）
   - **不要**勾选 ".gitignore"（我们已经有了）
   - **不要**选择 License（我们用 MIT，已有）
4. 点击 **Create repository**

创建后，GitHub 会显示一个仓库地址，类似：
```
https://github.com/你的用户名/gregtech-orbital-era.git
```

**记下这个地址**，下一步要用。

---

## 第四步：推送代码到 GitHub

在 **PowerShell** 中执行（注意替换仓库地址）：

```bash
# 进入项目目录
cd D:\GT-New

# 关联远程仓库（把下面的地址换成你的）
git remote add origin https://github.com/你的用户名/gregtech-orbital-era.git

# 推送到 GitHub
git push -u origin main
```

### 认证方式（二选一）

**方式 A：Personal Access Token（推荐）**

1. GitHub → 右上角头像 → **Settings** → **Developer settings**（最底部） → **Personal access tokens** → **Tokens (classic)**
2. 点 **Generate new token (classic)**
3. 设置：
   - **Note**: `push-token`（随便写，方便认）
   - **Expiration**: 90 days（或自定义）
   - **Scopes**: 勾选 `repo`（完整仓库权限）
4. 点 **Generate token**
5. **复制 token**（只显示一次！）
6. 推送时，Git 会弹出输入框：
   - **Username**: 你的 GitHub 用户名
   - **Password**: 粘贴刚才的 token（不是 GitHub 密码）

**方式 B：GitHub Desktop（图形界面，最简单）**

1. 下载 https://desktop.github.com/
2. 登录 GitHub 账号
3. 点 **Add an Existing Repository from your Hard Drive**
4. 选择 `D:\GT-New`
5. 点 **Publish repository**
6. 勾选 **Keep this code private**
7. 完成

---

## 第五步：邀请好友加入项目

仓库创建并推送成功后：

### 方法 A：通过 GitHub 网页邀请（推荐）

1. 打开你的仓库页面：`https://github.com/你的用户名/gregtech-orbital-era`
2. 点击 **Settings**（仓库设置，不是账号设置）
3. 左侧菜单 → **Access** → **Collaborators**
4. 点 **Add people**
5. 输入好友的 **GitHub 用户名** 或 **注册邮箱**
6. 选择权限级别：
   - **Write**（推荐）：可以 push 代码、管理分支
   - **Triage**：可以管理 issue/PR，不能 push
   - **Maintain**：可以管理仓库设置，不能删除仓库
   - **Admin**：最高权限（谨慎授予）
7. 点 **Add 好友用户名 to this repository**

好友会收到邮件邀请，也可以在 https://github.com/notifications 看到。**好友必须接受邀请才能开始协作**。

### 方法 B：通过 GitHub CLI 邀请（命令行）

如果安装了 GitHub CLI (`gh`)：
```bash
gh api repos/你的用户名/gregtech-orbital-era/collaborators/好友用户名 -X PUT -f permission=push
```

---

## 第六步：好友如何开始协作

好友接受邀请后：

1. **克隆仓库**：
   ```bash
   git clone https://github.com/你的用户名/gregtech-orbital-era.git GT-New
   ```

2. **放到启动器实例目录**：
   把 `GT-New` 文件夹放到启动器的 Minecraft 实例目录中。

3. **安装 Forge 1.20.1-47.4.18**：
   用启动器自动安装（HMCL / Prism / PCL2 均可）。

4. **启动游戏**，确认整合包正常运行。

5. **修改并提交**：
   ```bash
   # 创建分支
   git checkout -b feature/add-new-mod

   # 添加文件后...
   git add -A
   git commit -m "添加新 mod: XXX"
   git push origin feature/add-new-mod
   ```

6. **发起 Pull Request**：
   在 GitHub 网页上点 **Compare & pull request** → **Create pull request**。

---

## 常见问题

### Q: 推送时报错 "file too large"？

GitHub 单文件限制 100MB。检查：
```bash
git ls-files | while read f; do
  size=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f")
  if [ "$size" -gt 104857600 ]; then echo "$f: $((size/1048576))MB"; fi
done
```
如果有的话，加入 `.gitignore` 后重新提交。

### Q: 想要好友不通过 PR 直接 push？

在仓库 Settings → General → Pull Requests → 取消勾选 "Require a pull request before merging"（如果是私有仓库默认就不需要）。

好友有 Write 权限后可以直接：
```bash
git push origin main
```

### Q: 如何撤销某次提交？

```bash
# 撤销但保留改动
git reset --soft HEAD~1

# 撤销并丢弃改动（谨慎）
git reset --hard HEAD~1

# 推送撤销
git push origin main --force
```

### Q: 仓库太大了怎么办？

mods 文件夹 212MB 是主要原因。如果 GitHub 警告仓库过大：
1. 考虑用 **Git LFS** 管理大文件（`git lfs install && git lfs track "*.jar"`）
2. 或在 Release 页面上传 zip 压缩包，仓库只保留配置文件

---

## 总结清单

| 步骤 | 谁来做 | 状态 |
|---|---|---|
| 写 README / .gitignore / MOD_LIST | 已完成 | ✅ |
| 初始化本地 git 仓库 + 首次提交 | 已完成 | ✅ |
| 安装 Git for Windows | 你 | ⬜ |
| 配置 git 用户名邮箱 | 你 | ⬜ |
| 在 GitHub 建仓库（Private） | 你 | ⬜ |
| 推送代码到 GitHub | 你 | ⬜ |
| 邀请好友（Collaborators） | 你 | ⬜ |
| 好友接受邀请并克隆 | 好友 | ⬜ |
