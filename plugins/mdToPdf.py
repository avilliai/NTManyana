# 导入Aspose.PDF库
import aspose.pdf as ap

# 创建一个Document对象，加载md文件
doc = ap.Document("D:\\新建文件夹/repo/1/21212.md")

# 创建一个PngDevice对象，设置大小和分辨率
png_device = ap.PngDevice(ap.Size(800, 600), 300)

# 遍历文档的每一页，调用PngDevice.Process方法，传入页码和输出文件路径
for i in range(1, doc.Pages.Count + 1):
    png_device.Process(doc.Pages[i], f"output_{i}.png")

# 保存输出的png文件
doc.Save("test.png")
