"""Diff Service - 计算两个文本版本的差异"""
import difflib
from typing import List, Dict, Tuple


class DiffService:
    """计算两个文本版本的差异"""

    def compute_diff(self, old_content: str, new_content: str) -> dict:
        """
        计算两版本差异，返回结构化结果

        Returns:
            {
                "additions": int,   # 新增行数
                "deletions": int,   # 删除行数
                "segments": [       # 差异段落
                    {"type": "unchanged|added|deleted", "lines": [...]}
                ]
            }
        """
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()

        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

        segments = []
        additions = 0
        deletions = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                segments.append({
                    'type': 'unchanged',
                    'lines': old_lines[i1:i2]
                })
            elif tag == 'delete':
                segments.append({
                    'type': 'deleted',
                    'lines': old_lines[i1:i2]
                })
                deletions += (i2 - i1)
            elif tag == 'insert':
                segments.append({
                    'type': 'added',
                    'lines': new_lines[j1:j2]
                })
                additions += (j2 - j1)
            elif tag == 'replace':
                segments.append({
                    'type': 'deleted',
                    'lines': old_lines[i1:i2]
                })
                segments.append({
                    'type': 'added',
                    'lines': new_lines[j1:j2]
                })
                deletions += (i2 - i1)
                additions += (j2 - j1)

        return {
            'additions': additions,
            'deletions': deletions,
            'segments': segments
        }

    def compute_unified_diff(self, old_content: str, new_content: str,
                              fromfile: str = 'old', tofile: str = 'new') -> str:
        """
        生成标准 unified diff 格式

        用于前端显示或导出
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=fromfile, tofile=tofile,
            lineterm=''
        ))
        return ''.join(diff)

    def get_line_changes(self, old_content: str, new_content: str) -> List[Dict]:
        """
        获取每行的变更状态

        Returns:
            [
                {"line_no": 1, "old": "xxx", "new": None, "status": "deleted"},
                {"line_no": 2, "old": None, "new": "yyy", "status": "added"},
                ...
            ]
        """
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()

        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

        result = []
        old_idx = 0
        new_idx = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for i in range(i1, i2):
                    result.append({
                        'line_no': i + 1,
                        'old': old_lines[i],
                        'new': old_lines[i],
                        'status': 'unchanged'
                    })
                old_idx = i2
                new_idx = j2
            elif tag == 'delete':
                for i in range(i1, i2):
                    result.append({
                        'line_no': i + 1,
                        'old': old_lines[i],
                        'new': None,
                        'status': 'deleted'
                    })
                old_idx = i2
            elif tag == 'insert':
                for j in range(j1, j2):
                    result.append({
                        'line_no': None,
                        'old': None,
                        'new': new_lines[j],
                        'status': 'added'
                    })
                new_idx = j2
            elif tag == 'replace':
                for i in range(i1, i2):
                    result.append({
                        'line_no': i + 1,
                        'old': old_lines[i],
                        'new': None,
                        'status': 'deleted'
                    })
                for j in range(j1, j2):
                    result.append({
                        'line_no': None,
                        'old': None,
                        'new': new_lines[j],
                        'status': 'added'
                    })
                old_idx = i2
                new_idx = j2

        return result


# 全局实例
diff_service = DiffService()