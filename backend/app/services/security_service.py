"""安全审核服务 - 内容审核、敏感词检测、输出过滤"""
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class SecurityService:
    """安全审核服务"""
    
    # 敏感词库（示例，实际应用中应从数据库或配置文件加载）
    SENSITIVE_WORDS = {
        # 政治敏感
        'political': [
            '政治敏感词1', '政治敏感词2',  # 实际使用时替换为真实敏感词
        ],
        # 色情暴力
        'nsfw': [
            '色情', '暴力', '血腥',
        ],
        # 违法内容
        'illegal': [
            '毒品', '枪支', '爆炸',
        ],
        # 歧视内容
        'discrimination': [
            '种族歧视', '性别歧视',
        ],
        # 欺诈诈骗
        'fraud': [
            '诈骗', '传销', '非法集资',
        ]
    }
    
    # 敏感信息正则模式
    PATTERNS = {
        'phone': r'1[3-9]\d{9}',  # 手机号
        'id_card': r'\d{17}[\dXx]',  # 身份证号
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # 邮箱
        'credit_card': r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}',  # 信用卡号
        'ip_address': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP地址
        'url': r'https?://[^\s]+',  # URL
    }
    
    @staticmethod
    def check_sensitive_words(content: str) -> Dict:
        """
        检测敏感词
        
        Args:
            content: 待检测的内容
        
        Returns:
            {
                'is_safe': bool,
                'risk_level': str,  # 'safe', 'low', 'medium', 'high'
                'violations': [{'type': str, 'word': str, 'position': int}]
            }
        """
        violations = []
        risk_scores = {
            'political': 100,
            'nsfw': 80,
            'illegal': 100,
            'discrimination': 60,
            'fraud': 90
        }
        
        total_risk = 0
        
        for category, words in SecurityService.SENSITIVE_WORDS.items():
            for word in words:
                if word in content:
                    # 找到所有匹配位置
                    for match in re.finditer(re.escape(word), content):
                        violations.append({
                            'type': category,
                            'word': word,
                            'position': match.start()
                        })
                        total_risk += risk_scores.get(category, 50)
        
        # 判断风险等级
        if total_risk == 0:
            risk_level = 'safe'
            is_safe = True
        elif total_risk < 50:
            risk_level = 'low'
            is_safe = True
        elif total_risk < 100:
            risk_level = 'medium'
            is_safe = False
        else:
            risk_level = 'high'
            is_safe = False
        
        return {
            'is_safe': is_safe,
            'risk_level': risk_level,
            'risk_score': total_risk,
            'violations': violations
        }
    
    @staticmethod
    def detect_sensitive_info(content: str) -> Dict:
        """
        检测敏感信息（手机号、身份证等）
        
        Args:
            content: 待检测的内容
        
        Returns:
            {
                'has_sensitive_info': bool,
                'detected': [{'type': str, 'value': str, 'position': int}]
            }
        """
        detected = []
        
        for info_type, pattern in SecurityService.PATTERNS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                detected.append({
                    'type': info_type,
                    'value': match.group(0),
                    'position': match.start()
                })
        
        return {
            'has_sensitive_info': len(detected) > 0,
            'count': len(detected),
            'detected': detected
        }
    
    @staticmethod
    def mask_sensitive_info(content: str, mask_char: str = '*') -> Tuple[str, List[Dict]]:
        """
        脱敏处理敏感信息
        
        Args:
            content: 待脱敏的内容
            mask_char: 脱敏字符
        
        Returns:
            (脱敏后的内容, 脱敏记录列表)
        """
        masked_content = content
        masked_items = []
        
        # 脱敏手机号：保留前3位和后4位
        def mask_phone(match):
            phone = match.group(0)
            masked = phone[:3] + mask_char * 4 + phone[-4:]
            masked_items.append({
                'type': 'phone',
                'original': phone,
                'masked': masked
            })
            return masked
        
        # 脱敏身份证号：保留前6位和后4位
        def mask_id_card(match):
            id_card = match.group(0)
            masked = id_card[:6] + mask_char * 8 + id_card[-4:]
            masked_items.append({
                'type': 'id_card',
                'original': id_card,
                'masked': masked
            })
            return masked
        
        # 脱敏邮箱：保留@前的前2位和@后的域名
        def mask_email(match):
            email = match.group(0)
            if '@' in email:
                local, domain = email.split('@', 1)
                if len(local) > 2:
                    masked_local = local[:2] + mask_char * (len(local) - 2)
                else:
                    masked_local = local
                masked = f"{masked_local}@{domain}"
            else:
                masked = email
            masked_items.append({
                'type': 'email',
                'original': email,
                'masked': masked
            })
            return masked
        
        # 脱敏信用卡号：只显示后4位
        def mask_credit_card(match):
            card = match.group(0).replace(' ', '').replace('-', '')
            masked = mask_char * 12 + card[-4:]
            masked_items.append({
                'type': 'credit_card',
                'original': card,
                'masked': masked
            })
            return masked
        
        # 应用脱敏
        masked_content = re.sub(SecurityService.PATTERNS['phone'], mask_phone, masked_content)
        masked_content = re.sub(SecurityService.PATTERNS['id_card'], mask_id_card, masked_content)
        masked_content = re.sub(SecurityService.PATTERNS['email'], mask_email, masked_content)
        masked_content = re.sub(SecurityService.PATTERNS['credit_card'], mask_credit_card, masked_content)
        
        return masked_content, masked_items
    
    @staticmethod
    def content_audit(content: str, auto_mask: bool = False) -> Dict:
        """
        综合内容审核
        
        Args:
            content: 待审核的内容
            auto_mask: 是否自动脱敏
        
        Returns:
            完整的审核结果
        """
        # 敏感词检测
        sensitive_check = SecurityService.check_sensitive_words(content)
        
        # 敏感信息检测
        sensitive_info = SecurityService.detect_sensitive_info(content)
        
        # 脱敏处理
        masked_content = content
        masked_items = []
        if auto_mask and sensitive_info['has_sensitive_info']:
            masked_content, masked_items = SecurityService.mask_sensitive_info(content)
        
        # 综合判断
        is_approved = sensitive_check['is_safe'] and (
            not sensitive_info['has_sensitive_info'] or auto_mask
        )
        
        return {
            'is_approved': is_approved,
            'original_content': content,
            'masked_content': masked_content if auto_mask else content,
            'sensitive_words': sensitive_check,
            'sensitive_info': sensitive_info,
            'masked_items': masked_items,
            'audit_time': datetime.utcnow().isoformat(),
            'suggestions': SecurityService._generate_suggestions(
                sensitive_check,
                sensitive_info
            )
        }
    
    @staticmethod
    def _generate_suggestions(sensitive_check: Dict, sensitive_info: Dict) -> List[str]:
        """生成审核建议"""
        suggestions = []
        
        if not sensitive_check['is_safe']:
            suggestions.append(f"检测到敏感词违规（风险等级：{sensitive_check['risk_level']}），建议修改内容")
            for v in sensitive_check['violations']:
                suggestions.append(f"• 发现{v['type']}类敏感词：{v['word']}")
        
        if sensitive_info['has_sensitive_info']:
            suggestions.append(f"检测到{sensitive_info['count']}处敏感信息，建议脱敏处理")
            info_types = set(item['type'] for item in sensitive_info['detected'])
            for info_type in info_types:
                type_names = {
                    'phone': '手机号',
                    'id_card': '身份证号',
                    'email': '邮箱',
                    'credit_card': '信用卡号',
                    'ip_address': 'IP地址',
                    'url': 'URL'
                }
                suggestions.append(f"• 包含{type_names.get(info_type, info_type)}")
        
        if not suggestions:
            suggestions.append("内容审核通过，未发现安全问题")
        
        return suggestions
    
    @staticmethod
    def batch_audit(contents: List[str], auto_mask: bool = False) -> List[Dict]:
        """
        批量审核
        
        Args:
            contents: 内容列表
            auto_mask: 是否自动脱敏
        
        Returns:
            审核结果列表
        """
        results = []
        for idx, content in enumerate(contents):
            result = SecurityService.content_audit(content, auto_mask)
            result['index'] = idx
            results.append(result)
        
        return results
    
    @staticmethod
    def validate_prompt_safety(prompt_content: str) -> Tuple[bool, List[str]]:
        """
        验证Prompt安全性（快速检查）
        
        Returns:
            (是否安全, 错误信息列表)
        """
        errors = []
        
        # 敏感词检测
        check_result = SecurityService.check_sensitive_words(prompt_content)
        if not check_result['is_safe']:
            errors.append(f"Prompt包含敏感内容（风险等级：{check_result['risk_level']}）")
        
        # 长度检查
        if len(prompt_content) > 50000:
            errors.append("Prompt内容过长，可能存在安全风险")
        
        # 恶意代码检测（简单示例）
        dangerous_patterns = [
            r'<script.*?>',
            r'javascript:',
            r'eval\(',
            r'exec\(',
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, prompt_content, re.IGNORECASE):
                errors.append("检测到潜在的恶意代码")
                break
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_output_safety(output_content: str) -> Tuple[bool, Dict]:
        """
        验证AI输出安全性
        
        Returns:
            (是否安全, 详细结果)
        """
        audit_result = SecurityService.content_audit(output_content, auto_mask=False)
        
        is_safe = audit_result['is_approved']
        
        return is_safe, audit_result
    
    @staticmethod
    def add_custom_sensitive_word(word: str, category: str = 'custom'):
        """添加自定义敏感词（运行时）"""
        if category not in SecurityService.SENSITIVE_WORDS:
            SecurityService.SENSITIVE_WORDS[category] = []
        
        if word not in SecurityService.SENSITIVE_WORDS[category]:
            SecurityService.SENSITIVE_WORDS[category].append(word)
    
    @staticmethod
    def remove_custom_sensitive_word(word: str, category: str = 'custom'):
        """移除自定义敏感词（运行时）"""
        if category in SecurityService.SENSITIVE_WORDS:
            if word in SecurityService.SENSITIVE_WORDS[category]:
                SecurityService.SENSITIVE_WORDS[category].remove(word)
    
    @staticmethod
    def get_sensitive_words() -> Dict[str, List[str]]:
        """获取敏感词库"""
        return SecurityService.SENSITIVE_WORDS.copy()

