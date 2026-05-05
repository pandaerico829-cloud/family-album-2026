"""
啟動和部署腳本
"""
import sys
import os
from pathlib import Path

def install_dependencies():
    """安裝依賴"""
    print("📦 安裝依賴包...")
    os.system(f"{sys.executable} -m pip install -q -r requirements.txt")
    print("✓ 依賴安裝完成")

def run_organizer():
    """運行相冊整理程序"""
    print("\n開始整理相冊...")
    os.system(f"{sys.executable} organize.py")

def run_server(port=5000):
    """運行密碼保護服務器"""
    print(f"\n啟動相冊服務器（端口: {port}）...")
    config_path = Path(__file__).parent / 'config.json'
    
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    from src.protected_server import ProtectedAlbumServer
    
    album_path = config.get('output_path', './output/web')
    password = config.get('password', '0829')
    
    server = ProtectedAlbumServer(album_path, password, port=port)
    server.run(debug=False)

def main():
    """主菜單"""
    print("""
╔════════════════════════════════════════╗
║   🏠 家庭相冊管理系統                   ║
╚════════════════════════════════════════╝

請選擇操作：
1. 安裝依賴
2. 整理相冊（分析 + 分類 + 生成HTML）
3. 啟動服務器（密碼保護訪問）
4. 安裝依賴 + 整理相冊 + 啟動服務器
0. 退出
    """)
    
    choice = input("請輸入選項 (0-4): ").strip()
    
    if choice == '1':
        install_dependencies()
    elif choice == '2':
        run_organizer()
    elif choice == '3':
        port = input("請輸入服務器端口 (默認5000): ").strip() or '5000'
        try:
            run_server(int(port))
        except KeyboardInterrupt:
            print("\n✓ 服務器已停止")
    elif choice == '4':
        install_dependencies()
        run_organizer()
        port = input("\n請輸入服務器端口 (默認5000): ").strip() or '5000'
        try:
            run_server(int(port))
        except KeyboardInterrupt:
            print("\n✓ 服務器已停止")
    elif choice == '0':
        print("再見！")
    else:
        print("❌ 無效選項")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'install':
            install_dependencies()
        elif sys.argv[1] == 'organize':
            run_organizer()
        elif sys.argv[1] == 'server':
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
            run_server(port)
        elif sys.argv[1] == 'all':
            install_dependencies()
            run_organizer()
            run_server(5000)
    else:
        main()
