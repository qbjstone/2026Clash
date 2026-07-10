import yaml
import os
import glob

def main():
    speedtest_files = glob.glob('shards/speedtest_*.yaml')
    if not speedtest_files:
        print("没有找到测速结果文件")
        return
    
    all_proxies = []
    for filepath in speedtest_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and 'proxies' in data:
                    all_proxies.extend(data['proxies'])
        except Exception as e:
            print(f"读取 {filepath} 失败: {type(e).__name__}")
    
    if all_proxies:
        with open('proxies_speedtest.yaml', 'w', encoding='utf-8') as f:
            yaml.dump({'proxies': all_proxies}, f, allow_unicode=True, default_flow_style=False)
        print(f"合并完成: 共 {len(all_proxies)} 个节点")
    else:
        print("没有有效的测速结果")

if __name__ == '__main__':
    main()
