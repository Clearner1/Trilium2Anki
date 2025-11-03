"""
LLM问答生成模块
"""
from openai import OpenAI

from src.prompt import llm_prompt


class LLMGenerator:
    def __init__(self, api_base, api_key, model, temperature=0.7, max_tokens=2000):
        # 使用自定义API地址
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_qa_pairs(self, note_content, num_cards=5, difficulty="适中"):
        """
        根据笔记内容生成问答对
        """
        prompt = self._build_prompt(note_content, num_cards, difficulty)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的Anki卡片制作助手，擅长根据学习笔记生成高质量的问答对。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            result = response.choices[0].message.content
            return self._parse_qa_pairs(result)

        except Exception as e:
            raise Exception(f"LLM调用失败: {e}")

    def _build_prompt(self, note_content, num_cards, difficulty):
        """
        构建提示词
        """
        # 如果 num_cards 为 0，让 LLM 自己决定数量
        if num_cards == 0:
            card_requirement = "合适数量的（根据内容丰富度决定，问题不能太碎，也不能太宽泛）"
        else:
            card_requirement = f"{num_cards} 个"
        
        prompt = llm_prompt.format(
            note_content=note_content,
            num_cards=card_requirement,
            difficulty=difficulty
        )
        return prompt

    def _parse_qa_pairs(self, llm_output):
        """
        解析LLM输出的问答对
        返回: [{"question": "...", "answer": "..."}, ...]
        """
        qa_pairs = []

        # 分割成问答对
        lines = llm_output.strip().split('\n')

        current_q = None
        current_a = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('Q:') or line.startswith('问:'):
                # 保存上一个问答对
                if current_q and current_a:
                    qa_pairs.append({
                        'question': current_q,
                        'answer': '\n'.join(current_a).strip()
                    })
                # 开始新的问题
                current_q = line[2:].strip()
                current_a = []
            elif line.startswith('A:') or line.startswith('答:'):
                # 开始答案
                current_a = [line[2:].strip()]
            else:
                # 继续答案内容
                if current_q:
                    current_a.append(line)

        # 保存最后一个问答对
        if current_q and current_a:
            qa_pairs.append({
                'question': current_q,
                'answer': '\n'.join(current_a).strip()
            })

        return qa_pairs

