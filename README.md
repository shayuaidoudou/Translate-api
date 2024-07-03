# Translate-api@鲨鱼爱兜兜

该项目集成了百度翻译，有道翻译，金山词霸，360翻译 多种翻译api接口，开发者均可直接调用。

项目依赖库：

- requests
- pycryptodome
- execjs
- Pyside6

Node运行环境

- 20.13.1

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

![image](https://github.com/shayuaidoudou/Translate-api/assets/140249561/dbc2bcb5-0ca5-42cf-9a91-ef73677e613e)

![image](https://github.com/shayuaidoudou/Translate-api/assets/140249561/c87c4a9e-a722-42e7-87aa-a8cf99aed8c2)

![image](https://github.com/shayuaidoudou/Translate-api/assets/140249561/08eab80b-6024-4e2a-95da-83c5b7f2fd74)

![image](https://github.com/shayuaidoudou/Translate-api/assets/140249561/16a8b672-e778-4b03-8586-413c8c73c226)


## 翻译接口解析

[有道翻译逆向详细解析](https://blog.csdn.net/m0_73641772/article/details/139907510)
[金山词霸逆向详细解析](https://blog.csdn.net/m0_73641772/article/details/140152668)

### 百度翻译（老版本）

类似md5加密，使用`JavaScript`动态生成令牌，携带参数进行post请求

![image](https://github.com/shayuaidoudou/Translate-api/assets/140249561/e476166d-5510-49e9-a04f-36c2035a0837)

### 有道翻译

md5加密 + AES加密，携带参数post请求

![image](https://github.com/shayuaidoudou/Translate-api/assets/140249561/83124b30-8b23-4342-ba34-52c25ba5943a)

![image](https://github.com/shayuaidoudou/Translate-api/assets/140249561/8cf5e28d-31a4-450d-ba8a-db2b489dd148)

这里接口返回的是密文，还需对其进行AES解密

### 金山词霸

md5加密 + AES加密，携带参数post请求

![image](https://github.com/shayuaidoudou/Translate-api/assets/140249561/2c1bfc8e-b4cf-4a68-9c56-41e1316ec38a)

### 360翻译

无任何加密，直接post请求即可

![image](https://github.com/shayuaidoudou/Translate-api/assets/140249561/8f1badb9-dcc8-4119-acc2-5f3f4c4787e7)
____

## 声明

注：所有翻译资源均来自互联网，该项目仅供学习和技术交流。

​										@鲨鱼爱兜兜

