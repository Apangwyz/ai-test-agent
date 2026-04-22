import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import KnowledgeEntity, KnowledgeType, KnowledgeStatus
from .manager import knowledge_manager

class KnowledgeExtractor:
    """知识提取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.patterns = {
            'requirement': [
                r'需求[:：]\s*(.+)',
                r'功能[:：]\s*(.+)',
                r'需要[:：]\s*(.+)',
                r'应该[:：]\s*(.+)',
                r'必须[:：]\s*(.+)'
            ],
            'technical': [
                r'技术[:：]\s*(.+)',
                r'架构[:：]\s*(.+)',
                r'系统[:：]\s*(.+)',
                r'模块[:：]\s*(.+)'
            ],
            'constraint': [
                r'约束[:：]\s*(.+)',
                r'限制[:：]\s*(.+)',
                r'要求[:：]\s*(.+)',
                r'条件[:：]\s*(.+)'
            ],
            'business_rule': [
                r'规则[:：]\s*(.+)',
                r'业务[:：]\s*(.+)',
                r'流程[:：]\s*(.+)'
            ],
            'best_practice': [
                r'最佳实践[:：]\s*(.+)',
                r'建议[:：]\s*(.+)',
                r'推荐[:：]\s*(.+)'
            ]
        }
    
    def extract_from_document(self, document_data: Dict[str, Any]) -> List[KnowledgeEntity]:
        """从文档数据中提取知识"""
        entities = []
        
        try:
            content = document_data.get('content', '')
            sections = document_data.get('sections', [])
            requirements = document_data.get('requirements', [])
            constraints = document_data.get('constraints', [])
            
            self.logger.info(f"Extracting knowledge from document with {len(sections)} sections")
            
            # 从章节中提取知识
            for section in sections:
                section_entities = self._extract_from_section(section)
                entities.extend(section_entities)
            
            # 从需求中提取知识
            for req in requirements:
                req_entity = self._create_requirement_entity(req, document_data)
                if req_entity:
                    entities.append(req_entity)
            
            # 从约束中提取知识
            for constraint in constraints:
                constraint_entity = self._create_constraint_entity(constraint, document_data)
                if constraint_entity:
                    entities.append(constraint_entity)
            
            # 从内容中提取其他知识
            content_entities = self._extract_from_content(content)
            entities.extend(content_entities)
            
            self.logger.info(f"Extracted {len(entities)} knowledge entities")
            
        except Exception as e:
            self.logger.error(f"Error extracting knowledge from document: {e}")
        
        return entities
    
    def _extract_from_section(self, section: str) -> List[KnowledgeEntity]:
        """从章节中提取知识"""
        entities = []
        
        try:
            for knowledge_type, patterns in self.patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, section)
                    for match in matches:
                        content = match.group(1).strip()
                        if content and len(content) > 10:
                            entity = KnowledgeEntity(
                                type=KnowledgeType(knowledge_type),
                                title=f"{knowledge_type.title()} from section",
                                content=content,
                                source="document_section",
                                metadata={
                                    'extraction_method': 'pattern_matching',
                                    'pattern': pattern,
                                    'section': section[:100]
                                },
                                tags=[knowledge_type],
                                status=KnowledgeStatus.ACTIVE,
                                confidence_score=0.7
                            )
                            entities.append(entity)
        except Exception as e:
            self.logger.error(f"Error extracting from section: {e}")
        
        return entities
    
    def _create_requirement_entity(self, requirement: str, document_data: Dict[str, Any]) -> Optional[KnowledgeEntity]:
        """创建需求实体"""
        try:
            if not requirement or len(requirement) < 10:
                return None
            
            entity = KnowledgeEntity(
                type=KnowledgeType.REQUIREMENT,
                title=requirement[:50],
                content=requirement,
                source="document_requirements",
                metadata={
                    'document_source': document_data.get('source', 'unknown'),
                    'extraction_method': 'direct_extraction'
                },
                tags=['requirement', 'functional'],
                status=KnowledgeStatus.ACTIVE,
                confidence_score=0.9
            )
            return entity
        except Exception as e:
            self.logger.error(f"Error creating requirement entity: {e}")
            return None
    
    def _create_constraint_entity(self, constraint: str, document_data: Dict[str, Any]) -> Optional[KnowledgeEntity]:
        """创建约束实体"""
        try:
            if not constraint or len(constraint) < 10:
                return None
            
            entity = KnowledgeEntity(
                type=KnowledgeType.CONSTRAINT,
                title=constraint[:50],
                content=constraint,
                source="document_constraints",
                metadata={
                    'document_source': document_data.get('source', 'unknown'),
                    'extraction_method': 'direct_extraction'
                },
                tags=['constraint', 'non-functional'],
                status=KnowledgeStatus.ACTIVE,
                confidence_score=0.9
            )
            return entity
        except Exception as e:
            self.logger.error(f"Error creating constraint entity: {e}")
            return None
    
    def _extract_from_content(self, content: str) -> List[KnowledgeEntity]:
        """从内容中提取知识"""
        entities = []
        
        try:
            sentences = self._split_into_sentences(content)
            
            for sentence in sentences:
                if len(sentence) < 20 or len(sentence) > 500:
                    continue
                
                knowledge_type = self._classify_sentence(sentence)
                if knowledge_type:
                    entity = KnowledgeEntity(
                        type=knowledge_type,
                        title=sentence[:50],
                        content=sentence,
                        source="document_content",
                        metadata={
                            'extraction_method': 'sentence_classification',
                            'sentence_length': len(sentence)
                        },
                        tags=[knowledge_type.value],
                        status=KnowledgeStatus.ACTIVE,
                        confidence_score=0.6
                    )
                    entities.append(entity)
        except Exception as e:
            self.logger.error(f"Error extracting from content: {e}")
        
        return entities
    
    def _split_into_sentences(self, content: str) -> List[str]:
        """将内容分割成句子"""
        sentences = re.split(r'[。！？.!?]', content)
        return [s.strip() for s in sentences if s.strip()]
    
    def _classify_sentence(self, sentence: str) -> Optional[KnowledgeType]:
        """分类句子类型"""
        sentence_lower = sentence.lower()
        
        if any(keyword in sentence_lower for keyword in ['需要', '应该', '必须', '需求', '功能']):
            return KnowledgeType.REQUIREMENT
        elif any(keyword in sentence_lower for keyword in ['技术', '架构', '系统', '模块', '设计']):
            return KnowledgeType.TECHNICAL
        elif any(keyword in sentence_lower for keyword in ['约束', '限制', '要求', '条件']):
            return KnowledgeType.CONSTRAINT
        elif any(keyword in sentence_lower for keyword in ['规则', '业务', '流程']):
            return KnowledgeType.BUSINESS_RULE
        elif any(keyword in sentence_lower for keyword in ['最佳实践', '建议', '推荐']):
            return KnowledgeType.BEST_PRACTICE
        
        return None
    
    def extract_from_technical_document(self, tech_doc: Dict[str, Any]) -> List[KnowledgeEntity]:
        """从技术文档中提取知识"""
        entities = []
        
        try:
            architecture = tech_doc.get('architecture', '')
            tech_stack = tech_doc.get('tech_stack', {})
            modules = tech_doc.get('modules', [])
            
            # 提取架构知识
            if architecture:
                entity = KnowledgeEntity(
                    type=KnowledgeType.TECHNICAL,
                    title="System Architecture",
                    content=architecture,
                    source="technical_document",
                    metadata={
                        'extraction_method': 'architecture_extraction',
                        'document_type': 'technical'
                    },
                    tags=['architecture', 'technical'],
                    status=KnowledgeStatus.ACTIVE,
                    confidence_score=0.9
                )
                entities.append(entity)
            
            # 提取技术栈知识
            for tech_name, tech_info in tech_stack.items():
                entity = KnowledgeEntity(
                    type=KnowledgeType.TECHNICAL,
                    title=f"Technology: {tech_name}",
                    content=str(tech_info),
                    source="technical_document",
                    metadata={
                        'extraction_method': 'tech_stack_extraction',
                        'technology': tech_name
                    },
                    tags=['technology', 'technical', tech_name],
                    status=KnowledgeStatus.ACTIVE,
                    confidence_score=0.9
                )
                entities.append(entity)
            
            # 提取模块知识
            for module in modules:
                entity = KnowledgeEntity(
                    type=KnowledgeType.TECHNICAL,
                    title=f"Module: {module.get('name', 'Unknown')}",
                    content=str(module),
                    source="technical_document",
                    metadata={
                        'extraction_method': 'module_extraction',
                        'module_name': module.get('name', 'Unknown')
                    },
                    tags=['module', 'technical', 'architecture'],
                    status=KnowledgeStatus.ACTIVE,
                    confidence_score=0.9
                )
                entities.append(entity)
            
            self.logger.info(f"Extracted {len(entities)} knowledge entities from technical document")
            
        except Exception as e:
            self.logger.error(f"Error extracting from technical document: {e}")
        
        return entities
    
    def extract_from_solution(self, solution: Dict[str, Any]) -> List[KnowledgeEntity]:
        """从解决方案中提取知识"""
        entities = []
        
        try:
            problem = solution.get('problem', '')
            approach = solution.get('approach', '')
            implementation = solution.get('implementation', '')
            
            # 提取问题知识
            if problem:
                entity = KnowledgeEntity(
                    type=KnowledgeType.SOLUTION,
                    title=f"Problem: {problem[:50]}",
                    content=problem,
                    source="solution_document",
                    metadata={
                        'extraction_method': 'problem_extraction',
                        'solution_type': 'problem'
                    },
                    tags=['problem', 'solution'],
                    status=KnowledgeStatus.ACTIVE,
                    confidence_score=0.9
                )
                entities.append(entity)
            
            # 提取方法知识
            if approach:
                entity = KnowledgeEntity(
                    type=KnowledgeType.SOLUTION,
                    title=f"Approach: {approach[:50]}",
                    content=approach,
                    source="solution_document",
                    metadata={
                        'extraction_method': 'approach_extraction',
                        'solution_type': 'approach'
                    },
                    tags=['approach', 'solution', 'method'],
                    status=KnowledgeStatus.ACTIVE,
                    confidence_score=0.9
                )
                entities.append(entity)
            
            # 提取实现知识
            if implementation:
                entity = KnowledgeEntity(
                    type=KnowledgeType.SOLUTION,
                    title=f"Implementation: {implementation[:50]}",
                    content=implementation,
                    source="solution_document",
                    metadata={
                        'extraction_method': 'implementation_extraction',
                        'solution_type': 'implementation'
                    },
                    tags=['implementation', 'solution', 'code'],
                    status=KnowledgeStatus.ACTIVE,
                    confidence_score=0.9
                )
                entities.append(entity)
            
            self.logger.info(f"Extracted {len(entities)} knowledge entities from solution")
            
        except Exception as e:
            self.logger.error(f"Error extracting from solution: {e}")
        
        return entities
    
    def store_extracted_knowledge(self, entities: List[KnowledgeEntity]) -> List[str]:
        """存储提取的知识"""
        entity_ids = []
        
        for entity in entities:
            try:
                entity_id = knowledge_manager.add_entity(entity)
                entity_ids.append(entity_id)
            except Exception as e:
                self.logger.error(f"Error storing entity: {e}")
        
        self.logger.info(f"Stored {len(entity_ids)} knowledge entities")
        return entity_ids

# 创建全局知识提取器实例
knowledge_extractor = KnowledgeExtractor()