"""
Anki导出模块 - 使用AnkiConnect自动添加卡片
"""
import requests
import json

class AnkiExporter:
    def __init__(self, deck_name, ankiconnect_url='http://localhost:8765',
                 model_name='问答题', tags=None):
        self.deck_name = deck_name
        self.ankiconnect_url = ankiconnect_url
        self.model_name = model_name
        self.tags = tags or []

    def _invoke(self, action, **params):
        """
        调用AnkiConnect API
        :param action:
        :param params:
        :return:
        """
        payload = {
            'action': action,
            'version': 6,
            'params': params
        }

        try:
            response = requests.post(
                self.ankiconnect_url,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()

            if result.get('error'):
                raise Exception(f"AnkiConnect错误: {result['error']}")

            return result.get('result')
        except Exception as e:
            raise Exception(f"AnkiConnect调用失败: {e}")

    def test_connection(self):
        """测试AnkiConnect连接"""
        try:
            version = self._invoke('version')
            return f"AnkiConnect version: {version}"
        except Exception as e:
            raise e

    def ensure_deck_exists(self):
        """确保牌组存在,不存在则创建"""
        decks = self._invoke('deckNames')
        if self.deck_name not in decks:
            self._invoke('createDeck', deck=self.deck_name)
            print(f"  创建牌组: {self.deck_name}")
        return True

    def add_note(self, question, answer):
        """
        添加单个笔记到Anki
        """

        note = {
            'deckName': self.deck_name,
            'modelName': self.model_name,
            'fields': {
                '正面': question,
                '背面': answer
            },
            'tags': self.tags,
            'options': {
                'allowDuplicate': False,  # 不允许重复
            }
        }

        try:
            note_id = self._invoke('addNote', note=note)
            return note_id
        except Exception as e:
            # 如果是重复卡片，返回None而不是抛出异常
            if 'duplicate' in str(e).lower():
                return None
            raise e

    def export(self, qa_pairs):
        """批量添加卡片到Anki"""
        # 1.测试链接
        print("  测试AnkiConnect连接...")
        self.test_connection()

        # 2. 确保牌组存在
        print(f"  检查牌组 '{self.deck_name}'...")
        self.ensure_deck_exists()

        # 3. 添加卡片
        print(f"  开始添加 {len(qa_pairs)} 个卡片...")

        added = 0
        skipped = 0
        failed = 0

        for i, qa in enumerate(qa_pairs, 1):
            try:
                note_id = self.add_note(qa['question'], qa['answer'])

                if note_id:
                    added += 1
                    print(f"    [{i}/{len(qa_pairs)}] ✓ 添加成功 (ID: {note_id})")
                else:
                    skipped += 1
                    print(f"    [{i}/{len(qa_pairs)}] ⊘ 跳过（重复卡片）")
            except Exception as e:
                failed += 1
                print(f"    [{i}/{len(qa_pairs)}] ✗ 添加失败: {e}")

        # 4. 返回统计
        return {
            'total': len(qa_pairs),
            'added': added,
            'skipped': skipped,
            'failed': failed,
        }

    def get_deck_stats(self):
        """获取牌组统计信息"""
        try:
            card_count = self._invoke('findCards', query=f'deck:"{self.deck_name}"')
            return {
                'deck_name': self.deck_name,
                'card_count': len(card_count) if card_count else 0
            }
        except Exception as e:
            return {'error': str(e)}

