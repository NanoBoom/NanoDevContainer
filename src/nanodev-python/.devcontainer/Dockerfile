FROM python:3.13-bookworm

LABEL org.opencontainers.image.source https://github.com/NanoBoom/NanoDevContainer

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# ============================================================================
# ARG 声明区域：集中管理所有构建参数
# ============================================================================
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=1000
ARG HOST_USER

# ============================================================================
# 用户创建：Python 官方镜像默认是 root，需要创建开发用户
# ============================================================================
RUN \
    # 创建开发用户组和用户
    groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} --shell /bin/bash --create-home ${USERNAME} \
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
    unzip \
    zip \
    wget \
    curl \
    git \
    # Node.js（用于安装 claude-code CLI）
    nodejs \
    npm \
    # 彻底清理 APT 缓存、临时文件和文档
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/* /usr/share/man/*

# ============================================================================
# Python：使用 uv 安装器（全局单次安装）
# ============================================================================
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv ~/.local/bin/uv* /usr/local/bin/ \
    && rm -rf ~/.local ~/.cargo ~/.rustup
ENV PATH="/usr/local/bin:${PATH}"

# ============================================================================
# Claude Code CLI：通过 npm 全局安装
# ============================================================================
RUN npm install -g @anthropic-ai/claude-code \
    && npm cache clean --force \
    && rm -rf ~/.npm

# ============================================================================
# 环境变量配置
# ============================================================================

# 工作目录
WORKDIR /workspace
RUN chown ${USERNAME}:${USERNAME} /workspace

# 切换到开发用户
USER ${USERNAME}
