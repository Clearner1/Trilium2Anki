"""
主程序 - Trilium笔记 - Anki卡片
"""
import os
import yaml

from src.anki_exporter import AnkiExporter
from src.content_parser import ContentParser
from src.llm_generator import LLMGenerator
from src.trilium_fetcher import TriliumFetcher


def load_config(config_path=None):
    """加载配置文件"""
    if config_path is None:
        # 获取项目根目录的 config.yaml
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config.yaml'
        )
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    print("=" * 50)
    print("Trilium笔记 → Anki卡片 自动生成工具")
    print("=" * 50)

    # 1. 加载配置
    print("\n[1/6] 加载配置...")
    config = load_config()

    # 2. 连接Trilium
    print("[2/6] 连接Trilium服务器...")
    fetcher = TriliumFetcher(
        server_url=config['trilium']['server_url'],
        api_token=config['trilium']['api_token']
    )

    try:
        app_info = fetcher.test_connection()
        print(f"✓ 连接成功: {app_info.get('appVersion', 'Trilium')}")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return

    # 3. 获取今天的笔记
    print("[3/6] 获取今天的笔记...")

    try:
        note_result = fetcher.fetch_today_content(
            model=config['trilium']['fetch_mode'],
            note_id=config['trilium'].get('note_id')
        )
    except Exception as e:
        print(f"✗ 获取失败: {e}")
        return

    if not note_result:
        print("✗ 未找到今天的笔记")
        return

    print(f"✓ 找到笔记: {note_result.get('title', '未命名')}")

    # 4. 解析内容
    print("[4/6] 解析笔记内容...")
    content = note_result['content']

    if note_result.get('is_full_doc'):
        parser = ContentParser(content)
        today_section = parser.extract_today_section()

        if not today_section:
            print("✗ 在文档中未找到今天的日期标题")
            return

        content = today_section['content']
        print(f"✓ 提取成功: {today_section['date']}")

    # 清理HTML
    if '<' in content and '>' in content:
        parser = ContentParser(content)
        content = parser.clean_html(content)

    print(f"  内容长度: {len(content)} 字符")

    if len(content) < 50:
        print("⚠ 警告: 内容太短")
        return

    # 5. 调用LLM生成问答对
    print("[5/6] 调用LLM生成问答对...")
    generator = LLMGenerator(
        api_base=config['llm']['api_base'],
        api_key=config['llm']['api_key'],
        model=config['llm']['model'],
        temperature=config['llm']['temperature'],
        max_tokens=config['llm']['max_tokens']
    )

    try:
        qa_pairs = generator.generate_qa_pairs(
            note_content=content,
            num_cards=config['generation']['cards_per_day'],
            difficulty=config['generation']['difficulty'],
        )
        print(f"✓ 成功生成 {len(qa_pairs)} 个问答对")
    except Exception as e:
        print(f"✗ 生成失败: {e}")
        return


    # 显示预览
    print("\n生成的问答对预览：")
    print("-" * 50)

    for i, qa in enumerate(qa_pairs, 1):
        print(f"\n卡片{i}:")
        print(f"Q: {qa['question']}")
        answer_preview = qa['answer'][:100] + '...' if len(qa['answer']) > 100 else qa['answer']
        print(f"A: {answer_preview}")
    print("-" * 50)

    # 6. 自动添加到Anki
    print("\n[6/6] 添加到Anki...")
    exporter = AnkiExporter(
        deck_name=config['anki']['deck_name'],
        ankiconnect_url=config['anki']['ankiconnect_url'],
        model_name=config['anki']['model_name'],
        tags=config['anki']['tags']
    )

    try:
        stats = exporter.export(qa_pairs)

        print("\n" + "=" * 50)
        print("任务完成！")
        print("=" * 50)
        print(f"\n📊 统计信息:")
        print(f"  总卡片数: {stats['total']}")
        print(f"  ✓ 成功添加: {stats['added']}")
        print(f"  ⊘ 跳过重复: {stats['skipped']}")
        print(f"  ✗ 添加失败: {stats['failed']}")

        # 显示牌组信息
        deck_stats = exporter.get_deck_stats()
        print(f"\n📚 牌组 '{deck_stats['deck_name']}' 现有 {deck_stats['card_count']} 张卡片")

    except Exception as e:
        print(f"✗ 添加失败: {e}")
        print("\n请检查：")
        print("1. Anki是否已启动")
        print("2. AnkiConnect插件是否已安装")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()





