from pathlib import Path

import nonebot
from nonebot.adapters.red import Adapter as ConsoleAdapter  # 避免重复命名

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(ConsoleAdapter)

# 在这里加载插件
#nonebot.load_builtin_plugins("echo")  # 内置插件
# nonebot.load_plugin("thirdparty_plugin")  # 第三方插件
#nonebot.load_plugins("plugins")  # 本地插件
#nonebot.load_plugin(Path("run\\test.py"))
nonebot.load_plugin(Path("run/aiReply.py"))
nonebot.load_plugin(Path("run/singleModule.py"))
nonebot.load_plugin(Path("run/imgSearch.py"))
nonebot.load_plugin(Path("run/userSign.py"))
nonebot.load_plugin(Path("run/obsidianVault.py"))
#nonebot.load_plugin(Path("run/biliHelper.py"))

if __name__ == "__main__":
    nonebot.run()