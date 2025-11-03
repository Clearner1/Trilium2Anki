"""
Trilium笔记获取模块
"""
import requests
from datetime import datetime


class TriliumFetcher:
    def __init__(self, server_url, api_token):
        self.server_url = server_url.rstrip('/')
        self.api_base = f"{self.server_url}/etapi"
        self.headers = {
            'Authorization': api_token,
            'Content-Type': 'application/json'
        }

    def test_connection(self):
        """测试连接"""
        try:
            response = requests.get(
                f"{self.api_base}/app-info",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"连接Trilium失败:{e}")

    def get_note_by_id(self, note_id):
        """
        通过ID获取笔记
        返回: {'noteId', 'title', 'type', ...}
        """
        try:
            response = requests.get(
                f"{self.api_base}/notes/{note_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"获取笔记失败: {e}")

    def get_note_contents(self, note_id):
        """
        获取笔记内容
        :param note_id:
        :return: 文本内容或HTML内容
        """
        try:
            response = requests.get(
                f"{self.api_base}/notes/{note_id}/content",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"获取笔记内容失败: {e}")

    def get_calendar_note(self, date=None):
        """
        获取指定日期的笔记
        date: datetime对象,默认为今天
        """
        date_str = date.strftime("%Y-%m-%d")

        try:
            response = requests.get(
                f"{self.api_base}/calendar/days/{date_str}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            note_info = response.json()

            # 获取笔记内容
            if note_info and 'noteId' in note_info:
                content = self.get_note_contents(note_info['noteId'])
                return {
                    'noteId': note_info['noteId'],
                    'title': note_info.get('title', date_str),
                    'content': content
                }
            return None
        except Exception as e:
            raise Exception(f"获取日历笔记失败: {e}")

    def search_notes(self, query):
        """
        搜索笔记
        返回:[{'noteId', 'title', ...},...]
        """
        try:
            response = requests.get(
                f"{self.api_base}/notes",
                params={'search': query},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            results = response.json()
            return results.get('results',[])
        except Exception as e:
            raise Exception(f"搜索笔记失败: {e}")

    def fetch_today_content(self, model='fixed_note', note_id=None, search_template=None):
        """
        获取今天的笔记内容
        mode: 'calendar' / 'search' / 'fixed_note'
        """
        today = datetime.now()

        if model == 'calendar':
            # 方式1： 使用日历笔记功能
            return self.get_calendar_note(today)

        elif model == 'search':
            # 方式2： 搜索日历笔记功能
            if not search_template:
                search_template = "{date}"

            # 替换日期占位符
            date_str = today.strftime("%Y年%m月%d日")
            query = search_template.replace("{date}", date_str)

            results = self.search_notes(query)
            if results:
                # 返回第一个结果
                first_note = results[0]
                content = self.get_note_contents(first_note['noteId'])
                return {
                    'noteId': first_note['noteId'],
                    'title': first_note.get('title', ''),
                    'content': content
                }
            return None

        elif model == 'fixed_note':
            # （默认)方式3：从固定笔记中提取今天的内容
            if not note_id:
                raise ValueError("fixed_note模式需要提供note_id")

            note_info = self.get_note_by_id(note_id)
            content = self.get_note_contents(note_id)

            return {
                "noteId": note_id,
                'title': note_info.get('title', ''),
                'content': content,
                'is_full_doc': True
            }

        else:
            raise ValueError(f"不支持的模式: {model}")
