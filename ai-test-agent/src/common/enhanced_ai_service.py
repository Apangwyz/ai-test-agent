import os
import openai
import dashscope
from dotenv import load_dotenv
import logging
import time
import hashlib
import json
import builtins
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field

load_dotenv()

@dataclass
class ModelPerformance:
    """模型性能数据"""
    model_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    success_rate: float = 1.0
    last_call_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    
    def update_performance(self, success: bool, call_time: float):
        """更新性能数据"""
        self.total_calls += 1
        self.total_time += call_time
        
        if success:
            self.successful_calls += 1
            self.last_success_time = datetime.now()
        else:
            self.failed_calls += 1
            self.last_failure_time = datetime.now()
        
        self.last_call_time = datetime.now()
        self.average_time = self.total_time / self.total_calls
        self.success_rate = self.successful_calls / self.total_calls if self.total_calls > 0 else 0.0

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def access(self):
        """访问缓存条目"""
        self.access_count += 1
        self.last_accessed = datetime.now()

class EnhancedAIService:
    """增强的AI服务，支持智能路由和缓存"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # OpenAI configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
        
        # Qwen configuration
        self.qwen_api_key = os.getenv('QWEN_API_KEY')
        self.qwen_model = os.getenv('QWEN_MODEL_NAME', 'qwen-turbo')
        self.qwen_api_base = os.getenv('QWEN_API_BASE', 'https://api.dashscope.aliyuncs.com/api/v1')
        self.qwen_timeout = int(os.getenv('QWEN_TIMEOUT', '60'))
        
        # Initialize clients
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        if self.qwen_api_key:
            dashscope.api_key = self.qwen_api_key
        
        # Performance tracking
        self.model_performance: Dict[str, ModelPerformance] = {
            'qwen': ModelPerformance(model_name='qwen'),
            'openai': ModelPerformance(model_name='openai')
        }
        
        # Cache configuration
        self.cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache storage
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'size': 0
        }
        
        # Smart routing configuration
        self.routing_strategy = os.getenv('ROUTING_STRATEGY', 'performance')  # 'performance', 'cost', 'availability'
        self.load_balancing = os.getenv('LOAD_BALANCING', 'true').lower() == 'true'
        
        # Load performance data
        self._load_performance_data()
        self._load_cache()
    
    def generate(self, prompt: str, system_prompt: str, model_type: Optional[str] = None, 
                 temperature: float = 0.3, use_cache: bool = True) -> str:
        """
        生成内容，支持智能路由和缓存
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            model_type: 模型类型（可选，不指定则使用智能路由）
            temperature: 温度参数
            use_cache: 是否使用缓存
            
        Returns:
            生成的文本内容
        """
        try:
            # 智能路由选择模型
            if model_type is None:
                model_type = self._select_model(prompt, system_prompt)
            
            # 检查缓存
            if use_cache and self.cache_enabled:
                cached_result = self._get_from_cache(prompt, system_prompt, model_type, temperature)
                if cached_result:
                    self.logger.info(f"Cache hit for model {model_type}")
                    return cached_result
            
            # 调用模型生成内容
            start_time = time.time()
            
            if model_type == 'qwen' and self.qwen_api_key:
                try:
                    result = self._generate_with_qwen(prompt, system_prompt, temperature)
                    call_time = time.time() - start_time
                    self.model_performance['qwen'].update_performance(True, call_time)
                    
                    # 缓存结果
                    if use_cache and self.cache_enabled:
                        self._save_to_cache(prompt, system_prompt, model_type, temperature, result)
                    
                    return result
                except Exception as e:
                    self.logger.error(f"Qwen API error: {e}")
                    self.model_performance['qwen'].update_performance(False, time.time() - start_time)
                    
                    # 故障转移到OpenAI
                    if self.openai_api_key:
                        self.logger.info("Falling back to OpenAI")
                        return self._generate_with_openai(prompt, system_prompt, temperature)
                    else:
                        raise
            
            elif model_type == 'openai' and self.openai_api_key:
                try:
                    result = self._generate_with_openai(prompt, system_prompt, temperature)
                    call_time = time.time() - start_time
                    self.model_performance['openai'].update_performance(True, call_time)
                    
                    # 缓存结果
                    if use_cache and self.cache_enabled:
                        self._save_to_cache(prompt, system_prompt, model_type, temperature, result)
                    
                    return result
                except Exception as e:
                    self.logger.error(f"OpenAI API error: {e}")
                    self.model_performance['openai'].update_performance(False, time.time() - start_time)
                    
                    # 故障转移到Qwen
                    if self.qwen_api_key:
                        self.logger.info("Falling back to Qwen")
                        return self._generate_with_qwen(prompt, system_prompt, temperature)
                    else:
                        raise
            else:
                self.logger.warning(f"No API key configured for model type: {model_type}")
                return "Error: No API key configured"
                
        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            raise
    
    def _select_model(self, prompt: str, system_prompt: str) -> str:
        """智能选择模型"""
        try:
            # 根据路由策略选择模型
            if self.routing_strategy == 'performance':
                return self._select_by_performance()
            elif self.routing_strategy == 'cost':
                return self._select_by_cost(prompt)
            elif self.routing_strategy == 'availability':
                return self._select_by_availability()
            else:
                return self._select_by_performance()
        except Exception as e:
            self.logger.error(f"Error selecting model: {e}")
            # 默认返回Qwen
            return 'qwen' if self.qwen_api_key else 'openai'
    
    def _select_by_performance(self) -> str:
        """基于性能选择模型"""
        qwen_perf = self.model_performance['qwen']
        openai_perf = self.model_performance['openai']
        
        # 比较成功率和响应时间
        qwen_score = qwen_perf.success_rate * 0.6 + (1.0 / (qwen_perf.average_time + 0.1)) * 0.4
        openai_score = openai_perf.success_rate * 0.6 + (1.0 / (openai_perf.average_time + 0.1)) * 0.4
        
        if qwen_score > openai_score:
            return 'qwen' if self.qwen_api_key else 'openai'
        else:
            return 'openai' if self.openai_api_key else 'qwen'
    
    def _select_by_cost(self, prompt: str) -> str:
        """基于成本选择模型"""
        # Qwen通常成本更低，优先使用
        if self.qwen_api_key:
            return 'qwen'
        return 'openai'
    
    def _select_by_availability(self) -> str:
        """基于可用性选择模型"""
        qwen_available = self.qwen_api_key and self.model_performance['qwen'].success_rate > 0.8
        openai_available = self.openai_api_key and self.model_performance['openai'].success_rate > 0.8
        
        if qwen_available and openai_available:
            # 都可用时，选择成功率更高的
            if self.model_performance['qwen'].success_rate > self.model_performance['openai'].success_rate:
                return 'qwen'
            else:
                return 'openai'
        elif qwen_available:
            return 'qwen'
        elif openai_available:
            return 'openai'
        else:
            # 都不可用时，选择有API key的
            return 'qwen' if self.qwen_api_key else 'openai'
    
    def _generate_with_qwen(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """使用Qwen模型生成内容"""
        response = dashscope.Generation.call(
            model=self.qwen_model,
            prompt=prompt,
            system=system_prompt,
            temperature=temperature,
            max_tokens=2000,
            top_p=0.8
        )
        
        if response.status_code == 200 and response.output:
            return response.output.text
        else:
            error_msg = response.message if hasattr(response, 'message') else "Unknown error"
            raise Exception(f"Qwen API error: {error_msg}")
    
    def _generate_with_openai(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """使用OpenAI模型生成内容"""
        response = openai.ChatCompletion.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _get_cache_key(self, prompt: str, system_prompt: str, model_type: str, temperature: float) -> str:
        """生成缓存键"""
        cache_data = {
            'prompt': prompt,
            'system_prompt': system_prompt,
            'model_type': model_type,
            'temperature': temperature
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_from_cache(self, prompt: str, system_prompt: str, model_type: str, temperature: float) -> Optional[str]:
        """从缓存获取结果"""
        try:
            cache_key = self._get_cache_key(prompt, system_prompt, model_type, temperature)
            
            # 检查内存缓存
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if not entry.is_expired():
                    entry.access()
                    self.cache_stats['hits'] += 1
                    return entry.content
                else:
                    del self.memory_cache[cache_key]
            
            # 检查磁盘缓存
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                with builtins.open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                expires_at = datetime.fromisoformat(cache_data['expires_at']) if cache_data.get('expires_at') else None
                if expires_at is None or datetime.now() < expires_at:
                    entry = CacheEntry(
                        key=cache_key,
                        content=cache_data['content'],
                        created_at=datetime.fromisoformat(cache_data['created_at']),
                        expires_at=expires_at,
                        access_count=cache_data.get('access_count', 0)
                    )
                    entry.access()
                    self.memory_cache[cache_key] = entry
                    self.cache_stats['hits'] += 1
                    return entry.content
                else:
                    cache_file.unlink()
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting from cache: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def _save_to_cache(self, prompt: str, system_prompt: str, model_type: str, temperature: float, content: str):
        """保存结果到缓存"""
        try:
            cache_key = self._get_cache_key(prompt, system_prompt, model_type, temperature)
            expires_at = datetime.now() + timedelta(seconds=self.cache_ttl)
            
            # 保存到内存缓存
            entry = CacheEntry(
                key=cache_key,
                content=content,
                expires_at=expires_at
            )
            self.memory_cache[cache_key] = entry
            
            # 保存到磁盘缓存
            cache_file = self.cache_dir / f"{cache_key}.json"
            cache_data = {
                'key': cache_key,
                'content': content,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat(),
                'access_count': 0,
                'model_type': model_type,
                'temperature': temperature
            }
            
            with builtins.open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.cache_stats['size'] = len(self.memory_cache)
            
        except Exception as e:
            self.logger.error(f"Error saving to cache: {e}")
    
    def _load_cache(self):
        """加载磁盘缓存"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with builtins.open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    expires_at = datetime.fromisoformat(cache_data['expires_at']) if cache_data.get('expires_at') else None
                    if expires_at is None or datetime.now() < expires_at:
                        entry = CacheEntry(
                            key=cache_data['key'],
                            content=cache_data['content'],
                            created_at=datetime.fromisoformat(cache_data['created_at']),
                            expires_at=expires_at,
                            access_count=cache_data.get('access_count', 0)
                        )
                        self.memory_cache[cache_data['key']] = entry
                    else:
                        cache_file.unlink()
                except Exception as e:
                    self.logger.error(f"Error loading cache file {cache_file}: {e}")
            
            self.cache_stats['size'] = len(self.memory_cache)
            self.logger.info(f"Loaded {len(self.memory_cache)} cache entries")
            
        except Exception as e:
            self.logger.error(f"Error loading cache: {e}")
    
    def _load_performance_data(self):
        """加载性能数据"""
        try:
            perf_file = self.cache_dir / "performance.json"
            if perf_file.exists():
                with builtins.open(perf_file, 'r', encoding='utf-8') as f:
                    perf_data = json.load(f)
                
                for model_name, data in perf_data.items():
                    if model_name in self.model_performance:
                        perf = self.model_performance[model_name]
                        perf.total_calls = data.get('total_calls', 0)
                        perf.successful_calls = data.get('successful_calls', 0)
                        perf.failed_calls = data.get('failed_calls', 0)
                        perf.total_time = data.get('total_time', 0.0)
                        perf.average_time = data.get('average_time', 0.0)
                        perf.success_rate = data.get('success_rate', 1.0)
                
                self.logger.info("Loaded performance data")
        except Exception as e:
            self.logger.error(f"Error loading performance data: {e}")
    
    def _save_performance_data(self):
        """保存性能数据"""
        try:
            perf_data = {}
            for model_name, perf in self.model_performance.items():
                perf_data[model_name] = {
                    'total_calls': perf.total_calls,
                    'successful_calls': perf.successful_calls,
                    'failed_calls': perf.failed_calls,
                    'total_time': perf.total_time,
                    'average_time': perf.average_time,
                    'success_rate': perf.success_rate
                }
            
            perf_file = self.cache_dir / "performance.json"
            with builtins.open(perf_file, 'w', encoding='utf-8') as f:
                json.dump(perf_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info("Saved performance data")
        except Exception as e:
            self.logger.error(f"Error saving performance data: {e}")
    
    def clear_cache(self):
        """清空缓存"""
        try:
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.name != "performance.json":
                    cache_file.unlink()
            
            self.cache_stats = {
                'hits': 0,
                'misses': 0,
                'size': 0
            }
            
            self.logger.info("Cleared cache")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            **self.cache_stats,
            'hit_rate': self.cache_stats['hits'] / (self.cache_stats['hits'] + self.cache_stats['misses']) if (self.cache_stats['hits'] + self.cache_stats['misses']) > 0 else 0.0,
            'enabled': self.cache_enabled,
            'ttl': self.cache_ttl
        }
    
    def get_model_performance(self) -> Dict[str, Dict[str, Any]]:
        """获取模型性能统计"""
        performance_data = {}
        for model_name, perf in self.model_performance.items():
            performance_data[model_name] = {
                'model_name': perf.model_name,
                'total_calls': perf.total_calls,
                'successful_calls': perf.successful_calls,
                'failed_calls': perf.failed_calls,
                'total_time': perf.total_time,
                'average_time': perf.average_time,
                'success_rate': perf.success_rate,
                'last_call_time': perf.last_call_time.isoformat() if perf.last_call_time else None,
                'last_success_time': perf.last_success_time.isoformat() if perf.last_success_time else None,
                'last_failure_time': perf.last_failure_time.isoformat() if perf.last_failure_time else None
            }
        
        return performance_data
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            'cache_stats': self.get_cache_stats(),
            'model_performance': self.get_model_performance(),
            'routing_strategy': self.routing_strategy,
            'load_balancing': self.load_balancing,
            'last_updated': datetime.now().isoformat()
        }
    
    def __del__(self):
        """析构函数，保存性能数据"""
        try:
            self._save_performance_data()
        except Exception as e:
            self.logger.error(f"Error in destructor: {e}")

# 创建全局增强AI服务实例
enhanced_ai_service = EnhancedAIService()