# FastAPI Application

Django → FastAPI 마이그레이션 진행 중 (Phase 1)

## 🎯 현재 상태

### 완료된 기능
- ✅ GET /api/topics - 토픽 목록 조회
- ✅ GET /api/topics/{id} - 토픽 상세 조회
- ✅ GET /api/contexts - 컨텍스트 목록 조회
- ✅ GET /api/contexts/{id} - 컨텍스트 상세 조회
- ✅ GET /health - 헬스 체크

### 테스트
- Topics: 5/5 통과
- Contexts: 2/4 통과 (트랜잭션 격리 이슈 수정 필요)

## 🚀 실행 방법

### 로컬 개발
```bash
# FastAPI 서버 실행 (포트 8001)
uv run uvicorn api.main:app --reload --port 8001

# 브라우저에서 열기
# - API 문서: http://localhost:8001/docs
# - ReDoc: http://localhost:8001/redoc
```

### 테스트
```bash
# 모든 FastAPI 테스트 실행
uv run pytest api/tests/ -v

# 특정 테스트 파일 실행
uv run pytest api/tests/test_topics_poc.py -v
```

## 📁 디렉터리 구조

```
api/
├── __init__.py
├── main.py              # FastAPI 앱 엔트리포인트
├── config.py            # 설정 (Pydantic Settings)
├── models/              # SQLAlchemy 모델
│   ├── base.py         # Base, 세션 관리
│   ├── topic.py        # Topic 모델
│   └── context.py      # Context, ContextItem 모델
├── schemas/             # Pydantic 스키마
│   ├── topic.py        # Topic 스키마
│   └── context.py      # Context 스키마
├── routers/             # API 라우터
│   ├── topics.py       # Topics 엔드포인트
│   └── contexts.py     # Contexts 엔드포인트
└── tests/               # 테스트
    ├── test_topics_poc.py
    └── test_contexts.py
```

## 🔧 기술 스택

- **FastAPI**: 웹 프레임워크
- **SQLAlchemy 2.0**: ORM (Django ORM과 동일한 PostgreSQL DB 사용)
- **Pydantic**: 데이터 검증 및 직렬화
- **Uvicorn**: ASGI 서버
- **pytest**: 테스트 프레임워크

## 📝 주요 차이점 (Django vs FastAPI)

### Django ORM → SQLAlchemy
```python
# Django
class Topic(models.Model):
    name = models.CharField(max_length=200)

# SQLAlchemy
class Topic(Base):
    __tablename__ = "rag_topic"
    name: Mapped[str] = mapped_column(String(200))
```

### DRF Serializer → Pydantic Schema
```python
# DRF
class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name']

# Pydantic
class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
```

## 🔄 마이그레이션 진행 상황

현재 **Phase 1** 진행 중 (전체 8 단계 중)

- [x] Phase 1.1: POC - Topics 엔드포인트
- [x] Phase 1.2: Context/ContextItem 모델
- [x] Phase 1.3: ManyToMany 관계
- [x] Phase 1.4: Alembic 마이그레이션
- [ ] Phase 1.5: Docker 하이브리드 구성

자세한 내용: `docs/agents/tasks/django-to-fastapi-migration/`

## 🐛 알려진 이슈

1. **트랜잭션 격리**: Django ORM과 SQLAlchemy 간 트랜잭션 분리 필요
   - 테스트에서 Django로 생성한 데이터를 FastAPI가 즉시 읽지 못함
   - 해결 방법: `@pytest.mark.django_db(transaction=True)` + 명시적 커밋

2. **metadata 예약어**: SQLAlchemy에서 `metadata`는 예약어
   - 해결: `item_metadata`로 매핑하되 DB 컬럼명은 `metadata` 유지
