### 漫画下载器


**注意事项**

为了保护其他用户的体验和站长的钱包，请不要使用多线程下载，也不要把线程休眠时间改为 0，如不能接受，请勿以任何方式使用本脚本的任何代码。

**功能**

- 下载 [噢哩噢哩onlionli](https://m.onlionli.cn) 指定漫画到本地
- 支持代理池反爬（默认开启），详见 [https://github.com/jhao104/proxy_pool](https://github.com/jhao104/proxy_pool)
- 支持下载记录，已下载的图片不会再次下载，减少服务器压力，详见 `download_img` 方法（基于 url ，可改成基于本地文件名）

**环境**

1. Windows 10
2. python 3.9.5

**使用方法**

1. 安装依赖

```bash
pip install -r requirements.txt -i https://pypi.douban.com/simple
```

2. 下载
   1. 打开 [噢哩噢哩onlionli](https://m.onlionli.cn)，找到你需要下载的漫画，进到漫画主页，然后复制 漫画id
   2. 运行
   
    ```bash
    python spider.py 漫画id
    ```