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
        allure 'allure-cli'
    }

    environment {
        DEPLOY_BRANCH = 'master'
        UV_CACHE_DIR = "${WORKSPACE}/.uv-cache"
    }

    stages {
        stage('拉取代码') {
            steps {
                script {
                    def branch = env.BRANCH_NAME ?: env.DEPLOY_BRANCH
                    echo "正在拉取 ${branch} 分支代码..."
                }
                checkout scm
            }
        }

        stage('同步 Python 依赖') {
            steps {
                sh '''
                    set -eu

                    if ! command -v uv >/dev/null 2>&1; then
                        curl -LsSf https://astral.sh/uv/install.sh | sh
                    fi

                    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

                    if [ -f uv.lock ]; then
                        uv sync --frozen
                    else
                        uv sync
                    fi
                '''
            }
        }

        stage('执行 Pytest') {
            steps {
                sh '''
                    set -eu
                    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

                    rm -rf allure-results allure-report
                    uv run pytest -v --alluredir=allure-results

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
                    echo '未生成 allure-results，跳过 Allure 报告。'
                }
            }
        }

        success {
            script {
                def branch = env.BRANCH_NAME ?: env.DEPLOY_BRANCH

                if (branch == env.DEPLOY_BRANCH) {
                    withCredentials([
                        string(
                            credentialsId: 'git-author-name',
                            variable: 'GIT_AUTHOR_NAME'
                        ),
                        string(
                            credentialsId: 'git-author-email',
                            variable: 'GIT_AUTHOR_EMAIL'
                        ),
                        sshUserPrivateKey(
                            credentialsId: '9cc8c7e3-03dd-44a3-be28-3a53e8fd4b77',
                            keyFileVariable: 'SSH_KEY',
                            usernameVariable: 'SSH_USER'
                        )
                    ]) {
                        sh '''
                            set -eu

                            report_source="$WORKSPACE/allure-report"
                            test -d "$report_source"

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

                            export GIT_SSH_COMMAND="ssh -i '$SSH_KEY' -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"

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
            }
        }
    }
}