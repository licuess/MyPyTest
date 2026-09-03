pipeline {
    agent any

    // 配置 Allure 插件，名称需与 Jenkins 全局工具配置中的名称一致
    tools {
        allure 'allure-cli'
    }

    stages {
        stage('1. 拉取代码 (Checkout)') {
            steps {
                echo "正在拉取分支 ${BRANCH_NAME} 的代码..."
                checkout scm
            }
        }

        stage('2. 安装 uv 和同步依赖') {
            steps {
                // 自动安装 uv 包管理器
                sh 'curl -LsSf https://astral.sh/uv/install.sh | sh'

                // 确保 uv 在 PATH 中，并同步安装 pyproject.toml 中的依赖
                sh '''
                    export PATH="$HOME/.cargo/bin:$PATH"
                    uv sync
                '''
            }
        }

        stage('3. 运行 Pytest 测试') {
            steps {
                // 在 uv 的虚拟环境中运行测试，并生成 allure-results 目录
                sh '''
                    export PATH="$HOME/.cargo/bin:$PATH"
                    uv run pytest --alluredir=allure-results
                '''
            }
        }
    }

    post {
        // 无论成功或失败，都会生成 Allure 报告
        always {
            allure results: [[path: 'allure-results']]
        }

        // 仅在 master 分支构建成功时，自动部署报告到 GitHub Pages
        success {
            script {
                if (env.BRANCH_NAME == 'master') {
                    echo '正在将 Allure 报告部署到 gh-pages 分支...'
                    sh '''
                        # 配置 Git 用户信息
                        git config --global user.email "actions@github.com"
                        git config --global user.name "Jenkins Bot"

                        # 切换到或创建 gh-pages 分支，并清空历史
                        git checkout --orphan gh-pages || git checkout gh-pages
                        git rm -rf . || true

                        # 将生成的报告复制到 gh-pages
                        cp -R allure-report/* ./

                        # 提交并推送到 GitHub
                        git add .
                        git commit -m "Jenkins: 部署最新的 Allure 测试报告"

                        # 使用 Jenkins 中配置的凭证推送
                        git push origin gh-pages --force
                    '''
                    echo '部署成功！'
                }
            }
        }
    }
}