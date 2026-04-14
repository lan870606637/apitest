from appium import webdriver
from appium.options.android import UiAutomator2Options
import time

# 配置
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "Android Device"
options.app_package = "com.carbit.virtual.launcher"
options.app_activity = "com.carbit.virtual.launcher.ui.LauncherActivity"
options.no_reset = True

# 连接设备
print("正在连接设备...")
driver = webdriver.Remote("http://localhost:4723", options=options)
print("✅ 连接成功！")
time.sleep(3)

# 获取屏幕尺寸
window_size = driver.get_window_size()
width = window_size['width']
height = window_size['height']
print(f"屏幕尺寸: {width} x {height}")

# ========== 在这里修改你要点击的坐标 ==========
# 示例坐标（根据你的界面调整）
x, y = 500, 800
# ===========================================

# 点击坐标
print(f"正在点击坐标 ({x}, {y})")
driver.tap([(x, y)])
print("✅ 点击完成")

# 等待查看效果
time.sleep(2)

# 关闭连接
driver.quit()
print("脚本执行完毕")