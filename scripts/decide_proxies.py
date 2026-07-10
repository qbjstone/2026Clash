import os
import base64
import yaml

def parse_proxy_line(line):
    """解析单行代理配置"""
    line = line.strip()
    if not line:
        return None
    
    try:
        if line.startswith('vmess://'):
            return parse_vmess(line[8:])
        elif line.startswith('trojan://'):
            return parse_trojan(line[9:])
        elif line.startswith('ss://'):
            return parse_ss(line[5:])
        elif line.startswith('ssr://'):
            return parse_ssr(line[6:])
        elif line.startswith('vless://'):
            return parse_vless(line[8:])
    except Exception as e:
        print(f"解析失败: {type(e).__name__}")
        return None
    
    return None

def parse_vmess(encoded):
    """解析 VMess 协议"""
    try:
        decoded = base64.b64decode(encoded + '==', validate=True).decode('utf-8')
        import json
        config = json.loads(decoded)
        return {
            'name': config.get('ps', 'VMess'),
            'type': 'vmess',
            'server': config.get('add'),
            'port': int(config.get('port', 0)),
            'uuid': config.get('id'),
            'alterId': int(config.get('aid', 0)),
            'cipher': config.get('scy', 'auto'),
            'tls': config.get('tls') == 'tls',
            'sni': config.get('sni', ''),
            'skip-cert-verify': False
        }
    except Exception:
        return None

def parse_trojan(encoded):
    """解析 Trojan 协议"""
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(f'trojan://{encoded}')
        params = parse_qs(parsed.query)
        return {
            'name': parsed.fragment or 'Trojan',
            'type': 'trojan',
            'server': parsed.hostname,
            'port': parsed.port,
            'password': parsed.username,
            'sni': params.get('sni', [''])[0],
            'skip-cert-verify': False
        }
    except Exception:
        return None

def parse_ss(encoded):
    """解析 Shadowsocks 协议"""
    try:
        from urllib.parse import urlparse
        if '@' in encoded:
            parsed = urlparse(f'ss://{encoded}')
            method_password = base64.b64decode(parsed.username + '==', validate=True).decode('utf-8')
            method, password = method_password.split(':', 1)
            return {
                'name': parsed.fragment or 'SS',
                'type': 'ss',
                'server': parsed.hostname,
                'port': parsed.port,
                'cipher': method,
                'password': password
            }
    except Exception:
        return None

def parse_ssr(encoded):
    """解析 ShadowsocksR 协议"""
    try:
        decoded = base64.b64decode(encoded + '==', validate=True).decode('utf-8')
        parts = decoded.split(':')
        if len(parts) >= 6:
            return {
                'name': 'SSR',
                'type': 'ssr',
                'server': parts[0],
                'port': int(parts[1]),
                'protocol': parts[2],
                'cipher': parts[3],
                'obfs': parts[4],
                'password': base64.b64decode(parts[5] + '==', validate=True).decode('utf-8')
            }
    except Exception:
        return None

def parse_vless(encoded):
    """解析 VLESS 协议"""
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(f'vless://{encoded}')
        params = parse_qs(parsed.query)
        return {
            'name': parsed.fragment or 'VLESS',
            'type': 'vless',
            'server': parsed.hostname,
            'port': parsed.port,
            'uuid': parsed.username,
            'flow': params.get('flow', [''])[0],
            'tls': params.get('security', [''])[0] == 'tls',
            'sni': params.get('sni', [''])[0],
            'skip-cert-verify': False
        }
    except Exception:
        return None

def main():
    if not os.path.exists('raw_proxies'):
        print("raw_proxies 目录不存在")
        return
    
    all_proxies = []
    for filename in os.listdir('raw_proxies'):
        if not filename.endswith('.txt'):
            continue
        
        filepath = os.path.join('raw_proxies', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for line in content.split('\n'):
            proxy = parse_proxy_line(line)
            if proxy:
                all_proxies.append(proxy)
    
    if all_proxies:
        with open('proxies_decoded.yaml', 'w', encoding='utf-8') as f:
            yaml.dump({'proxies': all_proxies}, f, allow_unicode=True, default_flow_style=False)
        print(f"解码完成，共 {len(all_proxies)} 个节点")
    else:
        print("未解析到任何节点")

if __name__ == '__main__':
    main()
