pipeline {
    agent any
    stages {
        stage('拉取代码 (Checkout)') {
            steps {
                echo '正在拉取代码...'
            }
        }
        stage('安装依赖 (Install Dependencies)') {
            steps {
                // 确保 Jenkins 服务器已安装 Python
                sh 'pip install -r requirements.txt'
            }
        }
        stage('运行测试 (Run Tests)') {
            steps {
                // 执行 pytest 测试
                sh 'pytest --alluredir=allure-results'
            }
        }
    }
    post {
        always {
            echo '构建流水线执行完毕！'
        }
        success {
            echo '恭喜！所有测试全部通过！'
        }
    }
}
