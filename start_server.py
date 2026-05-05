#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
簡單的相冊服務器啟動腳本
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

if __name__ == '__main__':
    from src.protected_server import ProtectedAlbumServer
    
    album_path = 'D:\\ClaudeProjects\\Album_Reorganize\\output\\web'
    password = '0829'
    port = 5000
    
    server = ProtectedAlbumServer(album_path, password, port)
    try:
        print(f"Starting server on http://localhost:{port}")
        print(f"Password: {password}")
        print("Press Ctrl+C to stop")
        server.run(debug=False)
    except KeyboardInterrupt:
        print("\nServer stopped")
