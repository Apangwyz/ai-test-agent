import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from src.knowledge_base.models import KnowledgeEntity, KnowledgeRelation, KnowledgeQuery, KnowledgeResult, KnowledgeType, KnowledgeStatus
from src.knowledge_base.manager import KnowledgeBaseManager
from src.knowledge_base.extractor import KnowledgeExtractor
from src.knowledge_base.query_service import KnowledgeQueryService
from src.knowledge_base.vector_store import VectorStore, VectorEmbedder

class TestKnowledgeModels:
    """测试知识数据模型"""

    def test_knowledge_entity_creation(self):
        """测试知识实体创建"""
        entity = KnowledgeEntity(
            type=KnowledgeType.REQUIREMENT,
            title="测试需求",
            content="测试内容",
            source="test",
            tags=["test", "requirement"]
        )
        
        assert entity.type == KnowledgeType.REQUIREMENT
        assert entity.title == "测试需求"
        assert entity.content == "测试内容"
        assert "test" in entity.tags
        assert entity.status == KnowledgeStatus.ACTIVE

    def test_knowledge_entity_to_dict(self):
        """测试知识实体转换为字典"""
        entity = KnowledgeEntity(
            type=KnowledgeType.TECHNICAL,
            title="测试技术知识",
            content="测试内容"
        )
        entity_dict = entity.to_dict()
        
        assert entity_dict['type'] == 'technical'
        assert entity_dict['title'] == '测试技术知识'
        assert entity_dict['content'] == '测试内容'
        assert 'created_at' in entity_dict

    def test_knowledge_entity_from_dict(self):
        """测试从字典创建知识实体"""
        entity_dict = {
            'type': 'requirement',
            'title': '测试需求',
            'content': '测试内容',
            'tags': ['test', 'requirement']
        }
        entity = KnowledgeEntity.from_dict(entity_dict)
        
        assert entity.type == KnowledgeType.REQUIREMENT
        assert entity.title == '测试需求'
        assert 'test' in entity.tags

    def test_knowledge_relation_creation(self):
        """测试知识关系创建"""
        relation = KnowledgeRelation(
            source_entity_id="source1",
            target_entity_id="target1",
            relation_type="depends_on",
            strength=0.8
        )
        
        assert relation.source_entity_id == "source1"
        assert relation.target_entity_id == "target1"
        assert relation.relation_type == "depends_on"
        assert relation.strength == 0.8

    def test_knowledge_relation_to_dict(self):
        """测试知识关系转换为字典"""
        relation = KnowledgeRelation(
            source_entity_id="source1",
            target_entity_id="target1"
        )
        relation_dict = relation.to_dict()
        
        assert relation_dict['source_entity_id'] == 'source1'
        assert relation_dict['target_entity_id'] == 'target1'
        assert relation_dict['relation_type'] == 'related_to'

    def test_knowledge_query_creation(self):
        """测试知识查询创建"""
        query = KnowledgeQuery(
            query_text="测试查询",
            query_type="semantic",
            limit=5,
            threshold=0.6
        )
        
        assert query.query_text == "测试查询"
        assert query.query_type == "semantic"
        assert query.limit == 5
        assert query.threshold == 0.6

    def test_knowledge_result_creation(self):
        """测试知识结果创建"""
        entity = KnowledgeEntity(title="测试实体")
        result = KnowledgeResult(
            entity=entity,
            score=0.9,
            relevance="high"
        )
        
        assert result.entity.title == "测试实体"
        assert result.score == 0.9
        assert result.relevance == "high"

class TestKnowledgeBaseManager:
    """测试知识库管理器"""

    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = KnowledgeBaseManager(base_dir=self.temp_dir)

    def teardown_method(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)

    def test_add_entity(self):
        """测试添加知识实体"""
        entity = KnowledgeEntity(
            type=KnowledgeType.REQUIREMENT,
            title="测试需求",
            content="测试内容"
        )
        entity_id = self.manager.add_entity(entity)
        
        assert entity_id is not None
        assert entity_id in self.manager.entity_index

    def test_get_entity(self):
        """测试获取知识实体"""
        entity = KnowledgeEntity(
            type=KnowledgeType.REQUIREMENT,
            title="测试需求",
            content="测试内容"
        )
        entity_id = self.manager.add_entity(entity)
        
        retrieved_entity = self.manager.get_entity(entity_id)
        assert retrieved_entity is not None
        assert retrieved_entity.title == "测试需求"

    def test_update_entity(self):
        """测试更新知识实体"""
        entity = KnowledgeEntity(
            type=KnowledgeType.REQUIREMENT,
            title="测试需求",
            content="测试内容"
        )
        entity_id = self.manager.add_entity(entity)
        
        updates = {"title": "更新后的需求", "content": "更新后的内容"}
        success = self.manager.update_entity(entity_id, updates)
        
        assert success is True
        updated_entity = self.manager.get_entity(entity_id)
        assert updated_entity.title == "更新后的需求"
        assert updated_entity.content == "更新后的内容"

    def test_delete_entity(self):
        """测试删除知识实体"""
        entity = KnowledgeEntity(
            type=KnowledgeType.REQUIREMENT,
            title="测试需求"
        )
        entity_id = self.manager.add_entity(entity)
        
        success = self.manager.delete_entity(entity_id)
        assert success is True
        assert self.manager.get_entity(entity_id) is None

    def test_add_relation(self):
        """测试添加知识关系"""
        # 创建两个实体
        entity1 = KnowledgeEntity(title="实体1")
        entity2 = KnowledgeEntity(title="实体2")
        id1 = self.manager.add_entity(entity1)
        id2 = self.manager.add_entity(entity2)
        
        # 创建关系
        relation = KnowledgeRelation(
            source_entity_id=id1,
            target_entity_id=id2,
            relation_type="depends_on"
        )
        relation_id = self.manager.add_relation(relation)
        
        assert relation_id is not None
        assert relation_id in self.manager.relation_index

    def test_get_relations(self):
        """测试获取实体的关系"""
        # 创建两个实体
        entity1 = KnowledgeEntity(title="实体1")
        entity2 = KnowledgeEntity(title="实体2")
        id1 = self.manager.add_entity(entity1)
        id2 = self.manager.add_entity(entity2)
        
        # 创建关系
        relation = KnowledgeRelation(
            source_entity_id=id1,
            target_entity_id=id2
        )
        self.manager.add_relation(relation)
        
        # 获取关系
        relations = self.manager.get_relations(id1)
        assert len(relations) == 1
        assert relations[0].source_entity_id == id1
        assert relations[0].target_entity_id == id2

    def test_query_entities(self):
        """测试查询知识实体"""
        # 添加测试实体
        entity1 = KnowledgeEntity(
            type=KnowledgeType.REQUIREMENT,
            title="登录需求",
            content="用户登录功能",
            tags=["login", "requirement"]
        )
        entity2 = KnowledgeEntity(
            type=KnowledgeType.TECHNICAL,
            title="数据库设计",
            content="数据库架构设计",
            tags=["database", "technical"]
        )
        self.manager.add_entity(entity1)
        self.manager.add_entity(entity2)
        
        # 创建查询
        query = KnowledgeQuery(
            query_text="登录",
            limit=10,
            threshold=0.1
        )
        
        # 执行查询
        results = self.manager.query_entities(query)
        assert len(results) >= 1
        assert any(result.entity.title == "登录需求" for result in results)

    def test_get_entities_by_type(self):
        """测试按类型获取知识实体"""
        # 添加测试实体
        entity1 = KnowledgeEntity(type=KnowledgeType.REQUIREMENT, title="需求1")
        entity2 = KnowledgeEntity(type=KnowledgeType.TECHNICAL, title="技术1")
        entity3 = KnowledgeEntity(type=KnowledgeType.REQUIREMENT, title="需求2")
        self.manager.add_entity(entity1)
        self.manager.add_entity(entity2)
        self.manager.add_entity(entity3)
        
        # 按类型查询
        requirement_entities = self.manager.get_entities_by_type(KnowledgeType.REQUIREMENT)
        assert len(requirement_entities) == 2
        assert all(entity.type == KnowledgeType.REQUIREMENT for entity in requirement_entities)

    def test_get_entities_by_tags(self):
        """测试按标签获取知识实体"""
        # 添加测试实体
        entity1 = KnowledgeEntity(title="实体1", tags=["test", "tag1"])
        entity2 = KnowledgeEntity(title="实体2", tags=["test", "tag2"])
        entity3 = KnowledgeEntity(title="实体3", tags=["tag3"])
        self.manager.add_entity(entity1)
        self.manager.add_entity(entity2)
        self.manager.add_entity(entity3)
        
        # 按标签查询
        test_entities = self.manager.get_entities_by_tags(["test"])
        assert len(test_entities) == 2
        assert all("test" in entity.tags for entity in test_entities)

    def test_search_by_content(self):
        """测试按内容搜索知识实体"""
        # 添加测试实体
        entity1 = KnowledgeEntity(title="登录功能", content="用户登录系统")
        entity2 = KnowledgeEntity(title="注册功能", content="用户注册系统")
        self.manager.add_entity(entity1)
        self.manager.add_entity(entity2)
        
        # 搜索
        results = self.manager.search_by_content("登录")
        assert len(results) >= 1
        assert any("登录" in result.entity.title for result in results)

    def test_get_statistics(self):
        """测试获取知识库统计信息"""
        # 添加测试实体
        entity1 = KnowledgeEntity(type=KnowledgeType.REQUIREMENT, title="需求1")
        entity2 = KnowledgeEntity(type=KnowledgeType.TECHNICAL, title="技术1")
        self.manager.add_entity(entity1)
        self.manager.add_entity(entity2)
        
        # 获取统计信息
        stats = self.manager.get_statistics()
        assert stats['total_entities'] == 2
        assert 'requirement' in stats['type_distribution']
        assert 'technical' in stats['type_distribution']

    def test_export_import_entities(self):
        """测试导出和导入知识实体"""
        # 添加测试实体
        entity = KnowledgeEntity(type=KnowledgeType.REQUIREMENT, title="测试需求")
        self.manager.add_entity(entity)
        
        # 导出
        export_file = Path(self.temp_dir) / "export.json"
        success = self.manager.export_entities(str(export_file))
        assert success is True
        assert export_file.exists()
        
        # 导入
        new_manager = KnowledgeBaseManager(base_dir=tempfile.mkdtemp())
        success = new_manager.import_entities(str(export_file))
        assert success is True
        assert new_manager.get_statistics()['total_entities'] == 1

class TestKnowledgeExtractor:
    """测试知识提取器"""

    def setup_method(self):
        """设置测试环境"""
        self.extractor = KnowledgeExtractor()

    def test_extract_from_document(self):
        """测试从文档提取知识"""
        document_content = "# 登录功能需求\n用户需要通过用户名和密码登录系统。"
        entities = self.extractor.extract_from_document(document_content)
        
        assert isinstance(entities, list)
        assert len(entities) > 0

    def test_store_extracted_knowledge(self):
        """测试存储提取的知识"""
        entities = [{
            'type': 'requirement',
            'title': '测试需求',
            'content': '测试内容'
        }]
        with patch('src.knowledge_base.extractor.knowledge_manager') as mock_manager:
            mock_manager.add_entity.return_value = "entity_id"
            entity_ids = self.extractor.store_extracted_knowledge(entities)
            
            assert isinstance(entity_ids, list)
            assert len(entity_ids) == 1
            mock_manager.add_entity.assert_called_once()

class TestKnowledgeQueryService:
    """测试知识查询服务"""

    def setup_method(self):
        """设置测试环境"""
        self.query_service = KnowledgeQueryService()

    def test_query(self):
        """测试查询知识"""
        query = KnowledgeQuery(
            query_text="测试查询",
            query_type="semantic"
        )
        
        with patch('src.knowledge_base.query_service.knowledge_manager') as mock_manager:
            mock_result = Mock()
            mock_manager.query_entities.return_value = [mock_result]
            results = self.query_service.query(query)
            
            assert isinstance(results, list)
            mock_manager.query_entities.assert_called_once_with(query)

    def test_hybrid_query(self):
        """测试混合查询"""
        query_text = "测试查询"
        
        with patch('src.knowledge_base.query_service.knowledge_manager') as mock_manager:
            mock_result = Mock()
            mock_manager.search_by_content.return_value = [mock_result]
            results = self.query_service.hybrid_query(query_text)
            
            assert isinstance(results, list)
            mock_manager.search_by_content.assert_called_once()

class TestVectorStore:
    """测试向量存储"""

    def setup_method(self):
        """设置测试环境"""
        self.vector_store = VectorStore()

    def test_add_document(self):
        """测试添加文档"""
        document_id = "doc1"
        content = "测试文档内容"
        
        with patch('src.knowledge_base.vector_store.vector_embedder') as mock_embedder:
            mock_embedder.embed.return_value = [0.1, 0.2, 0.3]
            success = self.vector_store.add_document(document_id, content)
            
            assert success is True
            mock_embedder.embed.assert_called_once_with(content)

    def test_search(self):
        """测试搜索文档"""
        query = "测试查询"
        
        with patch('src.knowledge_base.vector_store.vector_embedder') as mock_embedder:
            mock_embedder.embed.return_value = [0.1, 0.2, 0.3]
            results = self.vector_store.search(query, top_k=5)
            
            assert isinstance(results, list)
            mock_embedder.embed.assert_called_once_with(query)

class TestVectorEmbedder:
    """测试向量嵌入器"""

    def setup_method(self):
        """设置测试环境"""
        self.embedder = VectorEmbedder()

    def test_embed(self):
        """测试文本嵌入"""
        text = "测试文本"
        embedding = self.embedder.embed(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(value, float) for value in embedding)

if __name__ == "__main__":
    pytest.main([__file__])
