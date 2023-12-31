# NTManyana
项目[Manyana](https://github.com/avilliai/Manyana) 的NTQQ对应版本<br>
基于[chronocat](https://chronocat.vercel.app/) 与 [NoneBot2 Red Protocol适配器](https://github.com/nonebot/adapter-red) 实现<br>
但目前功能并没有全部转移过来，仅是部分
- 如果遇到使用问题，请在QQ群628763673反馈
# 部署
下载release的NTM.rar并解压<br>
语音合成与Manyana原版相同，请自行复制模型目录
## 文字指引
- 下载NTM.rar
- 安装压缩包里的QQ
- 安装LiteLoaderQQNT与chronocat
  - release的NTM.rar中包含了这两个文件，具体使用参考下面两个
  - 推荐这个：只看安装liteloader和chronocat就行，[这里](https://blog.bingyue.top/2023/10/14/chronocat_1/)
  - 不推荐：安装[LiteLoaderQQNT](https://github.com/LiteLoaderQQNT/LiteLoaderQQNT/releases/tag/0.5.9) 与[chronocat](https://chronocat.vercel.app/install/llqqnt) 
- 获取token: win+r输入%USERPROFILE%/.chronocat/config 即可查看token
- 用管理员身份运行NTM.exe
- 输入1开始搭建
- 把获取的token填进NTM/.env
- 使用 启动脚本.bat
## 教程视频
下载HowToUse.mp4以参考<br>
(HowToUse.mp4中，演示用的设备已经安装了对应的软件，所以跳过了，如果你没装这些软件就不要跳过)
# 原Manyana用户的数据转移
- config/settings.yaml除外，你可以直接用Manyana的data和config文件夹覆盖NTManyana的对应文件夹