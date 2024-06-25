# Translate-api@鲨鱼爱兜兜

该项目集成了百度翻译，有道翻译，金山词霸，360翻译 多种翻译api接口，开发者均可直接调用。

项目依赖库：

- requests
- pycryptodome
- execjs
- Pyside6

```python
pip install requests
pip install pycryptodome
pip install execjs
pip install Pyside6
```



## 个性化GUI翻译窗口（使用Pyside6搭建）

项目根目录下运行命令

```python
python shark_translate.py
```

运行结果如下图：

![image-20240625112104714](res\image-20240625112104714.png)

![image-20240625112137157](res\image-20240625112137157.png)

![image-20240625112214450](res\image-20240625112214450.png)

![image-20240625112302031](res\image-20240625112302031.png)

## 翻译接口解析

[有道翻译逆向详细解析](https://blog.csdn.net/m0_73641772/article/details/139907510)

### 百度翻译（老版本）

类似md5加密，使用`JavaScript`动态生成令牌，携带参数进行post请求

![image-20240625104741625](res\image-20240625104741625.png)

### 有道翻译

md5加密 + AES加密，携带参数post请求

![image-20240625104926377](res\image-20240625104926377.png)

这里接口返回的是密文，还需对其进行AES解密

![image-20240625105011708](res\image-20240625105011708.png)

### 金山词霸

md5加密 + AES加密，携带参数post请求

![image-20240625105356749](res\image-20240625105356749.png)

### 360翻译

无任何加密，直接post请求即可

![image-20240625105132059](res\image-20240625105132059.png)

____

## 声明

注：所有翻译资源均来自互联网，该项目仅供学习和技术交流。

​										@鲨鱼爱兜兜

