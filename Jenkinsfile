pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    tools {
        // 名称必须与 Jenkins → Tools 中的 Allure 配置一致
        allure 'allure-cli'
    }

    environment {
        DEPLOY_BRANCH = 'master'
        UV_CACHE_DIR  = "${WORKSPACE}/.uv-cache"
    }

    stages {
        stage('1. 拉取代码') {
            steps {
                script {
                    def branch = env.BRANCH_NAME ?: env.DEPLOY_BRANCH
                    echo "正在拉取 ${branch} 分支代码..."
                }

                checkout scm
            }
        }

        stage('2. 同步 Python 依赖') {
            steps {
                sh '''
                    set -eu

                    if ! command -v uv >/dev/null 2>&1; then
                        echo "正在安装 uv..."
                        curl -LsSf https://astral.sh/uv/install.sh | sh
                    fi

                    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

                    if [ -f uv.lock ]; then
                        echo "检测到 uv.lock，使用锁定依赖安装。"
                        uv sync --frozen
                    else
                        echo "未检测到 uv.lock，依据 pyproject.toml 同步依赖。"
                        uv sync
                    fi
                '''
            }
        }

        stage('3. 执行 Pytest 并生成 Allure 结果') {
            steps {
                sh '''
                    set -eu
                    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

                    rm -rf allure-results allure-report

                    uv run pytest -v --alluredir=allure-results

                    # 若 pytest 未生成 Allure 结果，直接使构建失败，避免空报告。
                    find allure-results -name '*-result.json' -print -quit | grep -q .
                '''
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('allure-results')) {
                    allure results: [[path: 'allure-results']]
                } else {
                    echo '未找到 allure-results：测试未执行或未生成 Allure 结果。'
                }
            }
        }

        success {
            script {
                // 普通 Pipeline 不存在 BRANCH_NAME，因此默认按 master 处理。
                def branch = env.BRANCH_NAME ?: env.DEPLOY_BRANCH

                if (branch == env.DEPLOY_BRANCH) {
                    echo '正在部署 Allure 报告到 gh-pages 分支...'

                    withCredentials([
                        string(credentialsId: 'git-author-name', variable: 'GIT_AUTHOR_NAME'),
                        string(credentialsId: 'git-author-email', variable: 'GIT_AUTHOR_EMAIL')
                    ]) {
                        // Jenkins 中的 Git SSH 凭证 ID
                        sshagent(credentials: ['9cc8c7e3-03dd-44a3-be28-3a53e8fd4b77']) {
                            sh '''
                                set -eu

                                report_source="$WORKSPACE/allure-report"
                                test -d "$report_source"

                                # 用独立 worktree 发布，避免将 .venv、uv.lock 等
                                # 工作区临时文件误提交到 gh-pages。
                                deploy_dir="$(mktemp -d)"
                                trap 'git -C "$WORKSPACE" worktree remove --force "$deploy_dir" 2>/dev/null || true; rm -rf "$deploy_dir"' EXIT

                                git -C "$WORKSPACE" worktree add --force --detach "$deploy_dir" HEAD
                                cd "$deploy_dir"

                                if git show-ref --verify --quiet refs/remotes/origin/gh-pages; then
                                    git checkout -B gh-pages origin/gh-pages
                                else
                                    git checkout --orphan gh-pages
                                fi

                                git rm -rf . || true
                                cp -a "$report_source/." .

                                git config user.name "$GIT_AUTHOR_NAME"
                                git config user.email "$GIT_AUTHOR_EMAIL"

                                git add .

                                if git diff --cached --quiet; then
                                    echo "报告内容没有变化，跳过提交。"
                                else
                                    git commit -m "Jenkins: deploy Allure report #${BUILD_NUMBER}"
                                    git push origin HEAD:gh-pages --force
                                fi
                            '''
                        }
                    }
                } else {
                    echo "当前分支 ${branch} 不需要部署 GitHub Pages。"
                }
            }
        }
    }
}