.PHONY: all test smoke html clean

# 默认运行全部测试
all:
	pytest testcases -v --html=reports/report.html --self-contained-html

# 运行全部测试（简写）
test:
	pytest testcases -v

# 运行 Smoke 测试
smoke:
	pytest -m smoke -v

# 运行回归测试
regression:
	pytest -m regression -v

# 生成 HTML 报告
html:
	pytest testcases -v --html=reports/report.html --self-contained-html

# 生成 Allure 报告
allure:
	pytest testcases -v --alluredir=reports/allure-results
	allure serve reports/allure-results

# 清理报告
clean:
	rmdir /s /q reports 2>nul || true

# 运行指定文件，用法: make file=test_audio
file:
	pytest testcases/$(file).py -v

# 运行指定类，用法: make cls=TestAudio::test_audio_list
cls:
	pytest testcases/$(cls) -v
