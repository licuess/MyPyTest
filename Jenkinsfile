pipeline {
    agent any

    stages {
        stage('拉取代码 (Checkout)') {
            steps {
                echo '正在从 GitHub 拉取 MyPyTest 代码...'
            }
        }
        stage('安装依赖 (Install Dependencies)') {
            steps {
                // 安装项目所需依赖以及 pytest 生成 allure 结果的插件
                sh 'pip install -r requirements.txt allure-pytest'
            }
        }
        stage('运行测试 (Run Tests)') {
            steps {
                // 运行 pytest 测试，并将结果输出到 allure-results 目录
                sh 'pytest --alluredir=allure-results'
            }
        }
        stage('生成报告 (Generate Allure Report)') {
            steps {
                // 调用 Jenkins 的 Allure 插件展示报告（需 Jenkins 系统已安装并配置 Allure）
                allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
            }
        }
    }

    post {
        always {
            echo '========================================='
            echo '构建流水线执行完毕！'
            echo '========================================='
        }
        success {
            echo '🎉 恭喜！所有测试全部通过！'
        }
        failure {
            echo '❌ 构建失败，请检查控制台日志排查错误！'
        }
    }
}