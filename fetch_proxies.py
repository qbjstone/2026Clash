import os
import requests
import base64
import yaml

def fetch_subscription(url, index):
    """下载单个订阅链接"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.text.strip()
        
        # 尝试 Base64 解码
        try:
            decoded = base64.b64decode(content, validate=True).decode('utf-8')
            return decoded
        except Exception:
            # 如果不是 Base64，直接返回原始内容
            return content
    except Exception as e:
        print(f"下载第 {index+1} 个订阅失败: {type(e).__name__}")
        return None

def main():
    urls_env = os.environ.get('PROXIES_URLS', '')
    if not urls_env:
        print("未设置 PROXIES_URLS 环境变量")
        return
    
    urls = [u.strip() for u in urls_env.split(',') if u.strip()]
    if not urls:
        print("PROXIES_URLS 为空")
        return
    
    os.makedirs('raw_proxies', exist_ok=True)
    
    for i, url in enumerate(urls):
        print(f"正在下载第 {i+1}/{len(urls)} 个订阅...")
        content = fetch_subscription(url, i)
        if content:
            with open(f'raw_proxies/subscription_{i}.txt', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 第 {i+1} 个订阅下载成功")
        else:
            print(f"✗ 第 {i+1} 个订阅下载失败")

if __name__ == '__main__':
    main()
