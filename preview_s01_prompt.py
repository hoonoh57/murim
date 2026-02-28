#!/usr/bin/env python3
"""S01 프롬프트 미리보기"""

import sys
sys.path.insert(0, '.')

from src.pipeline.prompt_combiner import PromptCombiner

ep_dir = 'outputs/ep002_천마의_첫_하산__피로_물든_강호_첫걸음_20260228_114846'
combiner = PromptCombiner(ep_dir)

print("\n" + "=" * 70)
print("🎬 S01 Kling AI 프롬프트 미리보기")
print("=" * 70 + "\n")

result = combiner.format_for_tool('S01', 'kling')

print("📋 프롬프트:")
print("-" * 70)
print(result['prompt'])
print("-" * 70)
print()
print(f"🛠  도구: {result['tool']}")
print(f"⏱  지속시간: {result['duration']}초")
print(f"📹 포맷: {result['format']}")
print(f"🔗 웹사이트: {result['url']}")
print("\n" + "=" * 70)

# 5개 도구 모두 비교
print("\n📊 S01 모든 도구 프롬프트 길이 비교\n")
tools = ['kling', 'runway', 'pika', 'veo', 'haiper']
for tool in tools:
    res = combiner.format_for_tool('S01', tool)
    tool_name = res['tool'].split(' ')[0]
    prompt_len = len(res['prompt'])
    duration = res['duration']
    print(f"  {tool_name:12} | 길이: {prompt_len:4}자 | 지속시간: {duration}초")

print("\n" + "=" * 70)
