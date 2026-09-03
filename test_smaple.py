import allure

@allure.epic("用户登录功能测试")
@allure.feature("登录模块")
class TestLogin:

    @allure.story("正常登录")
    @allure.title("使用正确的用户名和密码登录")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self):
        """正常登录场景"""
        with allure.step("打开登录页面"):
            # 你的登录页面操作代码
            pass
        with allure.step("输入用户名和密码"):
            # 输入账号密码
            pass
        with allure.step("点击登录按钮"):
            # 点击登录
            pass
        with allure.step("验证登录成功"):
            assert True  # 断言登录成功

    @allure.story("异常登录")
    @allure.title("使用错误的密码登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_fail(self):
        """异常登录场景"""
        with allure.step("打开登录页面"):
            pass
        with allure.step("输入错误的密码"):
            pass
        with allure.step("点击登录按钮"):
            pass
        with allure.step("验证登录失败提示"):
            assert True  # 断言出现错误提示