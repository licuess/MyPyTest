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
                    uv sync --frozen
                '''
            }
        }

        stage('执行 Pytest 并生成 Allure 结果') {
            steps {
                sh '''
                    set -eu
                    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

                    rm -rf allure-results allure-report
                    uv run pytest -v --alluredir=allure-results

                    # 没有生成测试结果时直接失败，避免产生“0 test cases”的空报告
                    find allure-results -name '*-result.json' -print -quit | grep -q .
                '''
            }
        }
    }

    post {
        always {
            allure results: [[path: 'allure-results']]
        }

        success {
            script {
                def branch = env.BRANCH_NAME ?: env.DEPLOY_BRANCH

                if (branch == env.DEPLOY_BRANCH) {
                    echo '正在部署 Allure 报告到 gh-pages...'

                    withCredentials([
                        string(credentialsId: 'git-author-name', variable: 'GIT_AUTHOR_NAME'),
                        string(credentialsId: 'git-author-email', variable: 'GIT_AUTHOR_EMAIL')
                    ]) {
                        sshagent(credentials: ['9cc8c7e3-03dd-44a3-be28-3a53e8fd4b77']) {
                            sh '''
                                set -eu

                                test -d allure-report

                                git config user.name "$GIT_AUTHOR_NAME"
                                git config user.email "$GIT_AUTHOR_EMAIL"

                                git checkout --orphan gh-pages || git checkout gh-pages
                                git rm -rf . || true
                                cp -a allure-report/. .

                                git add .
                                if ! git diff --cached --quiet; then
                                    git commit -m "Jenkins: deploy Allure report #${BUILD_NUMBER}"
                                    git push origin HEAD:gh-pages --force
                                else
                                    echo "报告内容没有变化，跳过提交。"
                                fi
                            '''
                        }
                    }
                }
            }
        }
    }
}