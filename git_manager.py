#!/usr/bin/env python3
"""
自動 git 管理腳本 - 在每個分類完成後自動 commit 和 push
"""

import subprocess
import sys
from pathlib import Path


class GitManager:
    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path or '.')
        self.git_available = self._check_git()

    def _check_git(self) -> bool:
        """檢查 git 是否可用"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def init_repo(self) -> bool:
        """初始化 git 倉庫"""
        if not self.git_available:
            print("❌ Git 未安裝。請先安裝 Git:")
            print("   Windows: https://git-scm.com/download/win")
            print("   macOS: brew install git")
            print("   Linux: sudo apt-get install git")
            return False

        try:
            subprocess.run(['git', 'init'], cwd=self.repo_path, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Claude'], cwd=self.repo_path, check=True)
            subprocess.run(['git', 'config', 'user.email', 'claude@album-2026.local'], 
                         cwd=self.repo_path, check=True)
            print("✓ Git 倉庫已初始化")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 初始化失敗: {e}")
            return False

    def add_all(self) -> bool:
        """添加所有檔案"""
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True)
            print("✓ 所有檔案已添加到暫存區")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 添加失敗: {e}")
            return False

    def commit(self, message: str) -> bool:
        """提交變更"""
        try:
            subprocess.run(['git', 'commit', '-m', message], cwd=self.repo_path, check=True)
            print(f"✓ 已提交: {message}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 提交失敗: {e}")
            return False

    def add_remote(self, url: str) -> bool:
        """添加遠程倉庫"""
        try:
            subprocess.run(['git', 'remote', 'add', 'origin', url], cwd=self.repo_path, check=True)
            print(f"✓ 遠程倉庫已添加: {url}")
            return True
        except subprocess.CalledProcessError as e:
            if 'already exists' in str(e):
                print("✓ 遠程倉庫已存在")
                return True
            print(f"❌ 添加遠程失敗: {e}")
            return False

    def push(self, branch: str = 'main') -> bool:
        """推送到遠程倉庫"""
        try:
            # 確保分支存在
            subprocess.run(['git', 'branch', '-M', branch], cwd=self.repo_path, check=False)
            subprocess.run(['git', 'push', '-u', 'origin', branch], cwd=self.repo_path, check=True)
            print(f"✓ 已推送到 origin/{branch}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 推送失敗: {e}")
            print("   請檢查 GitHub token 或網路連線")
            return False

    def commit_with_auto_push(self, message: str, push_enabled: bool = False) -> bool:
        """提交並可選自動推送"""
        if not self.add_all():
            return False
        if not self.commit(message):
            return False
        if push_enabled:
            return self.push()
        return True


def main():
    """主程式 - 演示用法"""
    manager = GitManager('.')
    
    # 示例：初始化和設置
    if not manager.git_available:
        print("⚠️  Git 未可用")
        return 1
    
    if manager.init_repo():
        manager.add_all()
        manager.commit("🎉 初始化家庭相冊項目")
        print("\n✓ 項目已初始化")
        print("\n📌 下一步:")
        print("  1. 在 GitHub 上建立 repository: family-album-2026")
        print("  2. 運行此指令添加遠程倉庫:")
        print("     git remote add origin https://github.com/YOUR_USERNAME/family-album-2026.git")
        print("  3. 推送到 GitHub:")
        print("     git push -u origin main")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
