import yaml
import hashlib
import os

def generate_proxy_hash(proxy):
    """生成节点的唯一哈希值"""
    # 使用更完整的字段来避免哈希冲突
    core_fields = {
        'type': proxy.get('type', ''),
        'server': proxy.get('server', ''),
        'port': proxy.get('port', 0),
        'uuid': proxy.get('uuid', ''),
        'password': proxy.get('password', ''),
        'cipher': proxy.get('cipher', ''),
        'sni': proxy.get('sni', ''),
        'alpn': proxy.get('alpn', []),
        'network': proxy.get('network', ''),
        'ws-opts': proxy.get('ws-opts', {}),
        'h2-opts': proxy.get('h2-opts', {})
    }
    
    # 转换为字符串并计算哈希
    core_str = str(sorted(core_fields.items()))
    return hashlib.md5(core_str.encode('utf-8')).hexdigest()

def main():
    if not os.path.exists('proxies_decoded.yaml'):
        print("proxies_decoded.yaml 不存在")
        return
    
    with open('proxies_decoded.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    proxies = data.get('proxies', [])
    seen_hashes = set()
    unique_proxies = []
    
    for proxy in proxies:
        proxy_hash = generate_proxy_hash(proxy)
        if proxy_hash not in seen_hashes:
            seen_hashes.add(proxy_hash)
            unique_proxies.append(proxy)
    
    with open('proxies_dedup.yaml', 'w', encoding='utf-8') as f:
        yaml.dump({'proxies': unique_proxies}, f, allow_unicode=True, default_flow_style=False)
    
    print(f"去重完成: {len(proxies)} -> {len(unique_proxies)} 个节点")

if __name__ == '__main__':
    main()
