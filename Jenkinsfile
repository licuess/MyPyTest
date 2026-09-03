pipeline {
    agent any

    parameters {
        string(name: 'PYTHON_VERSION', defaultValue: '3.11', description: 'Python 版本号')
    }

    stages {
        stage('1. 拉取代码 (Checkout)') {
            steps {
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/${BRANCH_NAME}']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/licuess/MyPyTest.git', // 你的仓库地址
                        credentialsId: 'github-ssh-key' // 刚才在 Jenkins 配置的凭证 ID
                    ]]
                ])
                echo '代码拉取成功！'
            }
        }

        stage('2. 准备 uv 和 Python 环境') {
            steps {
                sh '''
                    # 检查并安装 uv (如果没有的话)
                    if ! command -v uv &> /dev/null; then
                        echo "正在安装 uv..."
                        curl -LsSf https://astral.sh/uv/install.sh | sh
                        export PATH="$HOME/.cargo/bin:$PATH"
                        echo "export PATH=\"$HOME/.cargo/bin:$PATH\"" >> $JENKINS_HOME/.env
                    else
                        echo "uv 已安装，版本: $(uv --version)"
                    fi
                    source $JENKINS_HOME/.env 2>/dev/null || true
                '''
            }
        }

        stage('3. 安装依赖 (Install Dependencies with uv)') {
            steps {
                sh '''
                    source $JENKINS_HOME/.env 2>/dev/null || true
                    echo "开始同步依赖 (uv sync)..."
                    uv sync
                '''
            }
        }

        stage('4. 运行测试 (Run Pytest with Allure)') {
            steps {
                sh '''
                    source $JENKINS_HOME/.env 2>/dev/null || true
                    # 运行测试并生成 Allure 结果数据
                    uv run pytest --alluredir=allure-results -v
                '''
            }
        }

        stage('5. 安装 Allure CLI') {
            steps {
                sh '''
                    ALLURE_VERSION="2.31.0"
                    ALLURE_URL="https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-2.31.0.tgz"

                    if ! command -v allure &> /dev/null; then
                        echo "正在下载并安装 Allure CLI..."
                        curl -o allure.tar.gz -L ${ALLURE_URL}
                        tar -zxvf allure.tar.gz -C /opt --strip-components=1
                        ln -s /opt/allure-2.31.0/bin/allure /usr/local/bin/allure
                        echo "Allure CLI 安装成功！"
                    else
                        echo "Allure CLI 已安装，版本: $(allure --version)"
                    fi
                '''
            }
        }

        stage('6. 生成 Allure 报告') {
            steps {
                script {
                    if (fileExists('allure-results')) {
                        echo "正在生成 Allure HTML 报告..."
                        sh 'allure generate allure-results -o allure-report --clean'
                    } else {
                        echo "警告: allure-results 目录不存在，无法生成报告。"
                    }
                }
            }
        }

        stage('7. 部署报告到 GitHub Pages') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    source $JENKINS_HOME/.env 2>/dev/null || true

                    echo "正在将报告推送至 gh-pages 分支..."

                    # 配置 Git
                    git config --global user.name 'Jenkins CI'
                    git config --global user.email 'jenkins@example.com'

                    # 检出 gh-pages 分支 (如果不存在则创建)
                    git checkout -B gh-pages origin/gh-pages 2>/dev/null || git checkout -b gh-pages

                    # 清空 gh-pages 上的旧文件，但保留 .git 目录
                    find . -mindepth 1 ! -name '.git' ! -name '.gitignore' -exec rm -rf {} +

                    # 将生成的报告复制过来
                    cp -R allure-report/* .
                    rm -rf allure-report

                    # 创建 HTML 索引文件 (GitHub Pages 需要)
                    echo '<meta http-equiv="refresh" content="0; url=allure/index.html">' > index.html

                    # 提交并推送
                    git add .
                    git commit -m "Deploy Allure Report: ${BUILD_NUMBER}" || echo "无变更"
                    git push origin gh-pages --force

                    echo "报告部署成功！请访问 GitHub Pages 查看。"
                '''
            }
        }
    }

    post {
        always {
            echo '=========================================='
            echo '流水线执行完毕！'
            echo '=========================================='
        }
        success {
            echo '恭喜！测试全部通过，报告已部署。'
        }
        failure {
            echo '构建失败！请检查测试日志。'
        }
    }
}