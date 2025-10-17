FROM node:24-bookworm

LABEL org.opencontainers.image.source https://github.com/NanoBoom/NanoDevContainer

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# ============================================================================
# ARG 声明区域：集中管理所有构建参数
# ============================================================================
ARG USERNAME=node
ARG USER_UID=1000
ARG USER_GID=1000
ARG HOST_USER

# ============================================================================
# 用户调整：与宿主机 UID/GID 匹配 + 路径映射
# ============================================================================
RUN \
    # 调整 node 用户的 UID/GID 以匹配宿主机
    groupmod --gid ${USER_GID} ${USERNAME} \
    && usermod --uid ${USER_UID} --gid ${USER_GID} ${USERNAME} \
    # 安装 sudo 并配置权限
    && apt-get update \
    && apt-get install -y sudo \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME} \
    && rm -rf /var/lib/apt/lists/* \
    # 路径映射：解决 macOS 配置文件中的绝对路径问题
    # Claude Code 等工具的配置文件可能包含宿主机绝对路径
    # 通过软链接让容器内可以解析 /Users/$HOST_USER 和 /home/$HOST_USER
    && ([ -z "${HOST_USER}" ] || \
        (mkdir -p /home /Users && \
         ln -snf /home/${USERNAME} /home/${HOST_USER} && \
         ln -snf /home/${USERNAME} /Users/${HOST_USER}))

# ============================================================================
# 额外工具安装：补充官方镜像缺少的工具
# ============================================================================
RUN apt-get update && apt-get install -y \
    # 命令行工具
    ripgrep \
    fd-find \
    tree \
    jq \
    wget \
    curl \
    git \
    unzip \
    zip \
    # 彻底清理 APT 缓存、临时文件和文档
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/* /usr/share/man/*

# ============================================================================
# Node.js 全局工具：TypeScript 和前端/移动开发工具
# ============================================================================
RUN npm install -g \
    typescript \
    ts-node \
    yarn \
    pnpm \
    expo-cli \
    eas-cli \
    vercel \
    @anthropic-ai/claude-code \
    # 清理 npm 缓存和文档
    && npm cache clean --force \
    && rm -rf ~/.npm

# ============================================================================
# Python：使用 uv 安装器（全局单次安装）
# ============================================================================
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && sudo mv ~/.local/bin/uv* /usr/local/bin/ \
    && rm -rf ~/.local ~/.cargo ~/.rustup
ENV PATH="/usr/local/bin:${PATH}"

# ============================================================================
# 环境变量配置
# ============================================================================

# 工作目录
WORKDIR /workspace
RUN sudo chown ${USERNAME}:${USERNAME} /workspace

# 切换到开发用户
USER ${USERNAME}
