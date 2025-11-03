"""
内容解析模块 - 提取指定日期的笔记
"""
import re
from datetime import datetime

from src.trilium_fetcher import TriliumFetcher


class ContentParser(object):
    def __init__(self, content):
        self.content = content

    def extract_today_section(self, target_date=None):
        """
        从完整文档中提取指定日期的部分
        用于fixed_note 模型
        :param target_date: datetime对象,默认今天
        :return:
        """
        if target_date is None:
            target_date = datetime.now()

        # 支持多种日期格式
        date_patterns = [
            # 1. 中文格式（无补零，匹配“2025年11月2日”）
            f"{target_date.year}年{target_date.month}月{target_date.day}日" if hasattr(target_date, 'year') else None,
            # 2. 中文格式（有补零，匹配“2025年11月02日”）
            target_date.strftime("%Y年%m月%d日") if hasattr(target_date, 'strftime') else None,
            # 3. 横线分隔（有补零，匹配“2025-11-02”）
            target_date.strftime("%Y-%m-%d") if hasattr(target_date, 'strftime') else None,
            # 4. 斜线分隔（有补零，匹配“2025/11/02”）
            target_date.strftime("%Y/%m/%d") if hasattr(target_date, 'strftime') else None,
            # 5. 横线分隔（无补零，匹配“2025-11-2”）
            f"{target_date.year}-{target_date.month}-{target_date.day}" if hasattr(target_date, 'year') else None,
            # 6. 斜线分隔（无补零，匹配“2025/11/2”）
            f"{target_date.year}/{target_date.month}/{target_date.day}" if hasattr(target_date, 'year') else None,
        ]
        date_patterns = [p for p in date_patterns if p]

        # 分割文档为各个部分（按标题）
        sections = self._split_by_headers(self.content)

        # 查找匹配的日期部分
        for pattern in date_patterns:
            for title, content in sections:
                if pattern in title:
                    return {
                        'date': title.strip(),
                        'content': content.strip()
                    }

        return None

    def _split_by_headers(self, text):
        """
        按标题分割文档（支持Markdown和HTML）
        返回: [(标题1, 内容1), (标题2, 内容2), ...]
        """
        # 尝试识别内容格式
        if '<h1' in text or '<h2' in text:
            return self._split_html_by_headers(text)
        else:
            return self._split_markdown_by_headers(text)

    def _split_markdown_by_headers(self, markdown_text):
        """按Markdown标题分割"""
        # 匹配 # 标题 或 ## 标题
        pattern = r'^(#{1,2})\s+(.+)$'

        lines = markdown_text.split('\n')
        sections = []
        current_title = None
        current_content = []

        for line in lines:
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                # 遇到新标题
                if current_title is not None:
                    sections.append((current_title, '\n'.join(current_content)))
                current_title = match.group(2)
                current_content = []
            else:
                if current_title is not None:
                    current_content.append(line)

        # 添加最后一个部分
        if current_title is not None:
            sections.append((current_title, '\n'.join(current_content)))

        return sections

    def _split_html_by_headers(self, html_text):
        """按HTML标题分割"""
        from bs4 import BeautifulSoup

        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            sections = []

            # 查找所有h1和h2标题
            headers = soup.find_all(['h1', 'h2'])

            for header in headers:
                title = header.get_text().strip()
                content_parts = []

                # 获取标题后的内容，直到下一个标题
                for sibling in header.next_siblings:
                    if sibling.name in ['h1', 'h2']:
                        break
                    if hasattr(sibling, 'get_text'):
                        content_parts.append(sibling.get_text())

                sections.append((title, '\n'.join(content_parts)))

            return sections
        except:
            # 如果解析失败，返回整个内容
            return [("全文", html_text)]

    def get_all_section_titles(self):
        """
        获取文档中所有的标题
        用于调试和查看
        """
        sections = self._split_by_headers(self.content)
        return [title for title, _ in sections]

    def clean_html(self, html_text):
        """清理HTML标签，保留纯文本"""
        from bs4 import BeautifulSoup
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            return soup.get_text()
        except:
            return html_text



