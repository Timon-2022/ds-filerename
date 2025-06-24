import requests
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek API 客户端，用于文本内容分析"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_content(self, content: str, analysis_type: str = "summary") -> Dict[str, Any]:
        """
        分析文本内容并返回分析结果
        
        Args:
            content: 要分析的文本内容
            analysis_type: 分析类型 ('summary', 'keywords', 'topic', 'custom')
        
        Returns:
            包含分析结果的字典
        """
        try:
            # 根据分析类型构建不同的提示词
            prompts = {
                "summary": f"""请分析以下文本内容，并提供一个简洁的摘要作为文件名建议。
要求：
1. 摘要应该简洁明了，适合作为文件名
2. 长度不超过50个字符
3. 不要包含特殊字符，只使用中文、英文、数字和下划线
4. 如果是代码文件，请包含主要功能描述
5. 如果是文档，请提取核心主题

文本内容：
{content[:2000]}

请只返回建议的文件名，不要其他解释：""",

                "keywords": f"""请从以下文本中提取3-5个最重要的关键词，用下划线连接作为文件名。
要求：
1. 关键词应该能代表文本的核心内容
2. 使用中文或英文
3. 用下划线连接关键词
4. 总长度不超过50个字符

文本内容：
{content[:2000]}

请只返回关键词组合，不要其他解释：""",

                "topic": f"""请识别以下文本的主要主题，并生成一个简洁的主题名称作为文件名。
要求：
1. 主题名称应该准确反映文本内容的核心
2. 长度不超过30个字符
3. 使用中文或英文
4. 不包含特殊字符

文本内容：
{content[:2000]}

请只返回主题名称，不要其他解释："""
            }
            
            prompt = prompts.get(analysis_type, prompts["summary"])
            
            # 调用 DeepSeek API
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                suggested_name = result["choices"][0]["message"]["content"].strip()
                
                return {
                    "success": True,
                    "suggested_name": suggested_name,
                    "analysis_type": analysis_type,
                    "original_length": len(content)
                }
            else:
                logger.error(f"DeepSeek API 错误: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API 调用失败: {response.status_code}",
                    "suggested_name": "未知文档"
                }
                
        except Exception as e:
            logger.error(f"DeepSeek API 调用异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "suggested_name": "分析失败"
            }
    
    def test_connection(self) -> bool:
        """测试API连接是否正常"""
        try:
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False 