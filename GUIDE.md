# Hướng Dẫn Toàn Diện — Day 12: Deployment AI Agent Lên Cloud

> **AICB-P1 · VinUniversity 2026**
> Tài liệu phân tích chuyên sâu toàn bộ repository, dành cho developer muốn hiểu và làm việc hiệu quả với dự án.

---

## 1. Tổng Quan Dự Án

### Mục đích

Repository này là **bộ tài liệu thực hành (lab)** cho buổi học Day 12 thuộc chương trình AICB-P1 tại VinUniversity. Mục tiêu chính là dạy sinh viên cách **đưa một AI Agent từ localhost lên cloud** — từ một ứng dụng "chỉ chạy trên máy mình" thành một service production-ready, có thể deploy lên Railway, Render hoặc GCP Cloud Run.

### Chức năng cốt lõi

- Xây dựng AI Agent (FastAPI) với nhiều cấp độ hoàn thiện (từ anti-patterns đến production-grade)
- Container hóa agent bằng Docker (single-stage → multi-stage build)
- Deploy lên cloud platforms (Railway, Render, GCP Cloud Run)
- Bảo vệ API (API Key, JWT Auth, Rate Limiting, Cost Guard)
- Scaling và đảm bảo reliability (Stateless architecture, Redis session, Nginx Load Balancer)

### Tech Stack

| Thành phần | Công nghệ | Phiên bản |
|-----------|-----------|-----------|
| Backend Framework | FastAPI | 0.115.0 |
| ASGI Server | Uvicorn | 0.30.0 |
| Validation | Pydantic | 2.9.0 |
| Authentication | PyJWT | 2.9.0 |
| Cache/Session | Redis | 5.1.0 |
| Monitoring | psutil | 6.0.0 |
| Container | Docker + Docker Compose | 3.9 |
| Load Balancer | Nginx | Alpine |
| Vector DB (demo) | Qdrant | v1.9.0 |
| Cloud | Railway, Render, GCP Cloud Run | — |
| Language | Python | 3.11+ |

---

## 2. Cấu Trúc Dự Án Chi Tiết

```
day12/
├── 01-localhost-vs-production/   ← Section 1: Hiểu sự khác biệt Dev ≠ Prod
│   ├── develop/
│   │   ├── app.py               ← Agent "kiểu localhost" — chứa 5 anti-patterns
│   │   ├── utils/mock_llm.py
│   │   └── requirements.txt
│   ├── production/
│   │   ├── app.py               ← Agent 12-Factor compliant (197 dòng)
│   │   ├── config.py            ← Centralized config management
│   │   ├── utils/mock_llm.py
│   │   └── requirements.txt
│   └── README.md
│
├── 02-docker/                   ← Section 2: Đóng gói bằng Docker
│   ├── develop/
│   │   ├── app.py               ← Agent đơn giản cho Docker demo
│   │   ├── Dockerfile           ← Single-stage (~800 MB)
│   │   └── requirements.txt
│   ├── production/
│   │   ├── main.py              ← Agent production trong Docker
│   │   ├── Dockerfile           ← Multi-stage (~160 MB), non-root user
│   │   ├── docker-compose.yml   ← Full stack: agent + redis + qdrant + nginx
│   │   └── requirements.txt
│   └── README.md
│
├── 03-cloud-deployment/         ← Section 3: Deploy lên Cloud
│   ├── railway/
│   │   ├── app.py               ← Agent Railway-ready (đọc PORT từ env)
│   │   ├── railway.toml         ← Config cho Railway platform
│   │   ├── utils/mock_llm.py
│   │   └── requirements.txt
│   ├── render/
│   │   └── render.yaml          ← Infrastructure as Code cho Render
│   ├── production-cloud-run/
│   │   ├── cloudbuild.yaml      ← CI/CD pipeline (test → build → push → deploy)
│   │   └── service.yaml         ← Cloud Run service definition (Knative)
│   └── README.md
│
├── 04-api-gateway/              ← Section 4: Bảo mật API
│   ├── develop/
│   │   ├── app.py               ← Agent với API Key authentication
│   │   ├── utils/mock_llm.py
│   │   └── requirements.txt
│   ├── production/
│   │   ├── app.py               ← Full security stack (203 dòng)
│   │   ├── auth.py              ← JWT module (create/verify token)
│   │   ├── rate_limiter.py      ← Sliding Window Counter algorithm
│   │   ├── cost_guard.py        ← Budget protection per user + global
│   │   ├── utils/mock_llm.py
│   │   └── requirements.txt
│   └── README.md
│
├── 05-scaling-reliability/      ← Section 5: Scale & Reliability
│   ├── develop/
│   │   ├── app.py               ← Health check + Graceful shutdown (200 dòng)
│   │   ├── utils/mock_llm.py
│   │   └── requirements.txt
│   ├── production/
│   │   ├── app.py               ← Stateless agent với Redis session (221 dòng)
│   │   ├── test_stateless.py    ← Test script chứng minh stateless hoạt động
│   │   ├── docker-compose.yml   ← 3 agent instances + Redis + Nginx LB
│   │   └── utils/mock_llm.py
│   └── (không có README riêng)
│
├── 06-lab-complete/             ← Lab cuối: Tổng hợp tất cả
│   ├── app/
│   │   ├── main.py              ← Entry point chính (286 dòng) — kết hợp toàn bộ
│   │   └── config.py            ← 12-Factor config với validation
│   ├── Dockerfile               ← Multi-stage, non-root, HEALTHCHECK
│   ├── docker-compose.yml       ← agent + redis
│   ├── railway.toml             ← Deploy Railway
│   ├── render.yaml              ← Deploy Render
│   ├── check_production_ready.py ← Script tự động kiểm tra production readiness
│   ├── .env.example             ← Template biến môi trường
│   ├── .dockerignore
│   ├── requirements.txt
│   └── README.md
│
├── utils/                       ← Shared utilities
│   └── mock_llm.py              ← Mock LLM — chạy offline, không cần API key
│
├── CODE_LAB.md                  ← Hướng dẫn lab chi tiết (3-4 giờ)
├── QUICK_START.md               ← Bắt đầu nhanh (5 phút)
├── QUICK_REFERENCE.md           ← Cheat sheet lệnh và patterns
├── TROUBLESHOOTING.md           ← Xử lý lỗi thường gặp
├── INSTRUCTOR_GUIDE.md          ← Hướng dẫn chấm điểm (cho giảng viên)
├── DAY12_DELIVERY_CHECKLIST.md  ← Checklist nộp bài
├── LEARNING_PATH.md             ← Lộ trình học
├── README.md                    ← Giới thiệu chung
└── .gitignore                   ← Bảo vệ secrets, cache, IDE files
```

### Vai trò của từng thành phần chính

| File/Folder | Vai trò |
|------------|---------|
| `utils/mock_llm.py` | **LLM giả lập** — trả về response mock dựa trên keywords, có delay mô phỏng latency thật. Toàn bộ project dùng module này thay vì gọi OpenAI/Anthropic thật. |
| `*/develop/` | Code **cơ bản** — hiểu concept, có thể chứa anti-patterns có chủ đích để so sánh. |
| `*/production/` | Code **chuyên sâu** — production-ready, áp dụng best practices. |
| `06-lab-complete/` | **Sản phẩm cuối** — kết hợp tất cả 5 section thành 1 project hoàn chỉnh. |
| `check_production_ready.py` | Script **tự động audit** — kiểm tra 18+ items (files, security, endpoints, Docker). |

---

## 3. Hướng Dẫn Cài Đặt (Từng Bước)

### Yêu cầu môi trường

```
Python 3.11+
Docker & Docker Compose
Git
(Tùy chọn) Railway CLI hoặc Render account
```

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd Vu-Duc-Duy-2A202600337-day-12
```

### Bước 2: Tạo virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# hoặc: .venv\Scripts\activate  # Windows
```

### Bước 3: Chạy Section đơn giản nhất (Section 1 — develop)

```bash
cd 01-localhost-vs-production/develop
pip install -r requirements.txt
python app.py
```

Truy cập: `http://localhost:8086` → Thấy response JSON từ agent.

### Bước 4: Chạy bản production (Section 1 — production)

```bash
cd ../production
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Kiểm tra:
- `http://localhost:8086/` → Thông tin app
- `http://localhost:8086/health` → Health check
- `http://localhost:8086/ready` → Readiness check

### Bước 5: Chạy bằng Docker (Section 2)

```bash
# Quay về root project
cd ../..

# Build single-stage (develop)
docker build -f 02-docker/develop/Dockerfile -t agent-develop .
docker run -p 8086:8086 agent-develop

# Build multi-stage (production) — image nhỏ hơn nhiều
docker build -f 02-docker/production/Dockerfile -t agent-production .
docker run -p 8086:8086 -e ENVIRONMENT=production agent-production

# So sánh size
docker images | grep agent
```

### Bước 6: Chạy full stack bằng Docker Compose (Section 6)

```bash
cd 06-lab-complete
cp .env.example .env.local
docker compose up
```

Kiểm tra:
```bash
curl http://localhost:8086/health

# Test endpoint được bảo vệ
curl -H "X-API-Key: dev-key-change-me-in-production" \
     -X POST http://localhost:8086/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is deployment?"}'
```

### Cấu hình chi tiết (`.env.example`)

| Biến | Mặc định | Mô tả |
|------|---------|-------|
| `HOST` | `0.0.0.0` | Bind address (0.0.0.0 cho container) |
| `PORT` | `8086` | Port server (cloud platform inject tự động) |
| `ENVIRONMENT` | `development` | development / staging / production |
| `DEBUG` | `true` | Bật/tắt debug mode và hot reload |
| `OPENAI_API_KEY` | (trống) | API key OpenAI — trống thì dùng mock LLM |
| `AGENT_API_KEY` | `dev-key-change-me` | API key cho client gọi agent |
| `JWT_SECRET` | `dev-jwt-secret` | Secret để ký JWT token |
| `RATE_LIMIT_PER_MINUTE` | `20` | Số request tối đa mỗi phút |
| `DAILY_BUDGET_USD` | `5.0` | Ngân sách LLM tối đa mỗi ngày (USD) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS allowed origins |

---

## 4. Code Hoạt Động Như Thế Nào

### 4.1. Mock LLM — Trái tim của toàn bộ demo

**File:** `utils/mock_llm.py` (44 dòng)

Đây là module được **mọi section** import. Thay vì gọi API OpenAI/Anthropic thật (tốn tiền, cần API key), hàm `ask()` trả về câu trả lời giả lập:

```python
def ask(question: str, delay: float = 0.1) -> str:
    time.sleep(delay + random.uniform(0, 0.05))  # giả lập latency
    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)
    return random.choice(MOCK_RESPONSES["default"])
```

**Logic:** Tìm keyword trong câu hỏi (`"docker"`, `"deploy"`, `"health"`) → trả response tương ứng. Nếu không match keyword nào → trả response mặc định ngẫu nhiên.

Hàm `ask_stream()` yield từng word một — mô phỏng streaming response của LLM thật.

### 4.2. Luồng xử lý request trong Production Agent (Section 06)

**File chính:** `06-lab-complete/app/main.py` (286 dòng)

```
Client Request
     │
     ▼
[CORS Middleware]     ← Kiểm tra origin có được phép không
     │
     ▼
[Request Middleware]  ← Đếm request, thêm security headers, log JSON structured
     │
     ▼
[API Key Auth]        ← Verify header X-API-Key (trả 401 nếu sai/thiếu)
     │
     ▼
[Rate Limiter]        ← Sliding window counter, 20 req/phút (trả 429 nếu vượt)
     │
     ▼
[Cost Guard]          ← Kiểm tra budget hàng ngày (trả 503 nếu hết budget)
     │
     ▼
[LLM Call]            ← Gọi mock_llm.ask() (hoặc OpenAI nếu có key)
     │
     ▼
[Record Usage]        ← Tính token cost, cộng dồn vào daily budget
     │
     ▼
[Response]            ← AskResponse(question, answer, model, timestamp)
```

### 4.3. Config Management (12-Factor Pattern)

**File:** `06-lab-complete/app/config.py` (56 dòng)

Sử dụng Python `dataclass` làm container cho config. Mọi giá trị đều đọc từ environment variables:

```python
@dataclass
class Settings:
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8086")))
    # ... các field khác

    def validate(self):
        if self.environment == "production":
            if self.agent_api_key == "dev-key-change-me":
                raise ValueError("AGENT_API_KEY must be set in production!")
        return self

settings = Settings().validate()  # Singleton — crash ngay nếu config sai
```

**Ý nghĩa:** Trong production, nếu quên set `AGENT_API_KEY` hoặc `JWT_SECRET`, app sẽ **crash ngay lập tức** (fail fast) thay vì chạy với config mặc định nguy hiểm.

### 4.4. Rate Limiter — Sliding Window Counter

**File:** `04-api-gateway/production/rate_limiter.py` (88 dòng)

```python
class RateLimiter:
    def __init__(self, max_requests=10, window_seconds=60):
        self._windows: dict[str, deque] = defaultdict(deque)

    def check(self, user_id: str) -> dict:
        now = time.time()
        window = self._windows[user_id]

        # Loại bỏ timestamps quá hạn
        while window and window[0] < now - self.window_seconds:
            window.popleft()

        # Kiểm tra limit
        if len(window) >= self.max_requests:
            raise HTTPException(status_code=429, ...)

        window.append(now)  # Ghi nhận request
```

**Algorithm:** Mỗi user có một `deque` chứa timestamps. Khi request đến: xóa các timestamp cũ hơn 60 giây → đếm còn lại → nếu ≥ limit thì block. Đây là **in-memory** — trong production thật nên dùng Redis-based rate limiter.

### 4.5. Cost Guard — Bảo vệ ngân sách LLM

**File:** `04-api-gateway/production/cost_guard.py` (129 dòng)

Tính chi phí dựa trên số token (mock):
- Input: `$0.15 / 1M tokens` (GPT-4o-mini pricing)
- Output: `$0.60 / 1M tokens`

Có **2 lớp bảo vệ:**
1. **Per-user budget:** $1/ngày — trả 402 nếu vượt
2. **Global budget:** $10/ngày — trả 503 nếu vượt (bảo vệ toàn hệ thống)

Cảnh báo khi user dùng 80% budget.

### 4.6. JWT Authentication

**File:** `04-api-gateway/production/auth.py` (76 dòng)

**Luồng:**
1. Client gọi `POST /auth/token` với `username` + `password`
2. Server verify, tạo JWT token (HS256, hết hạn 60 phút)
3. Client gửi token trong header `Authorization: Bearer <token>`
4. Server decode token → extract `username` + `role` → xử lý tiếp

Demo users:
- `student / demo123` → role `user` (10 req/phút)
- `teacher / teach456` → role `admin` (100 req/phút)

### 4.7. Stateless Architecture & Redis Session

**File:** `05-scaling-reliability/production/app.py` (221 dòng)

**Vấn đề:** Khi scale agent lên nhiều instances, nếu user gửi request 1 đến instance A, request 2 đến instance B → instance B không có session của user → bug.

**Giải pháp:** Lưu session vào Redis thay vì memory:

```python
def save_session(session_id, data, ttl_seconds=3600):
    if USE_REDIS:
        _redis.setex(f"session:{session_id}", ttl_seconds, json.dumps(data))
    else:
        _memory_store[f"session:{session_id}"] = data
```

Mỗi response trả về `served_by` cho thấy instance nào xử lý → chứng minh bất kỳ instance nào cũng đọc được session.

### 4.8. Docker Multi-Stage Build

**File:** `06-lab-complete/Dockerfile` (50 dòng)

```dockerfile
# Stage 1: Builder — cài dependencies
FROM python:3.11-slim AS builder
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime — chỉ copy những gì cần chạy
FROM python:3.11-slim AS runtime
RUN groupadd -r agent && useradd -r -g agent -d /app agent
COPY --from=builder /root/.local /home/agent/.local
COPY app/ ./app/
USER agent            # ← Non-root user (security best practice)
HEALTHCHECK ...       # ← Docker tự restart nếu health check fail
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8086", "--workers", "2"]
```

**Kết quả:** Image từ ~800 MB (single-stage) giảm xuống ~160 MB (multi-stage).

### 4.9. Production Readiness Checker

**File:** `06-lab-complete/check_production_ready.py` (143 dòng)

Script Python tự động audit project theo 18+ tiêu chí:

| Nhóm | Kiểm tra |
|------|---------|
| Files | Dockerfile, docker-compose.yml, .dockerignore, .env.example, requirements.txt, railway.toml/render.yaml |
| Security | .env trong .gitignore, không hardcode secrets |
| API | /health, /ready, authentication, rate limiting, SIGTERM, JSON logging |
| Docker | Multi-stage build, non-root user, HEALTHCHECK, slim base image |

Chạy: `python check_production_ready.py` → Output checklist ✅/❌ với phần trăm pass.

---

## 5. Hướng Dẫn Theo Nhiệm Vụ (Task-Based Guidance)

### 5.1. Cách thêm một endpoint mới vào Agent

**Bối cảnh:** Bạn muốn thêm endpoint `POST /summarize` để tóm tắt văn bản.

**Bước 1:** Mở `06-lab-complete/app/main.py`

**Bước 2:** Tạo Pydantic model cho request/response (gần dòng 165):

```python
class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=10000,
                      description="Text to summarize")

class SummarizeResponse(BaseModel):
    original_length: int
    summary: str
    timestamp: str
```

**Bước 3:** Thêm endpoint mới (sau endpoint `/ask`, khoảng dòng 228):

```python
@app.post("/summarize", response_model=SummarizeResponse, tags=["Agent"])
async def summarize(
    body: SummarizeRequest,
    request: Request,
    _key: str = Depends(verify_api_key),
):
    check_rate_limit(_key[:8])
    input_tokens = len(body.text.split()) * 2
    check_and_record_cost(input_tokens, 0)

    summary = llm_ask(f"Summarize: {body.text[:200]}")

    output_tokens = len(summary.split()) * 2
    check_and_record_cost(0, output_tokens)

    return SummarizeResponse(
        original_length=len(body.text),
        summary=summary,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
```

**Lưu ý quan trọng:**
- Luôn thêm `Depends(verify_api_key)` để bảo vệ endpoint
- Gọi `check_rate_limit()` và `check_and_record_cost()` trước khi gọi LLM
- Dùng Pydantic `Field` để validate input
- Thêm `tags` để nhóm trong Swagger docs

**Bước 4:** Test:
```bash
curl -H "X-API-Key: dev-key-change-me-in-production" \
     -X POST http://localhost:8086/summarize \
     -H "Content-Type: application/json" \
     -d '{"text": "Docker is a platform for developing, shipping, and running applications in containers..."}'
```

---

### 5.2. Cách thay Mock LLM bằng OpenAI thật

**Bước 1:** Cài thêm thư viện:
```bash
pip install openai
```

Thêm vào `requirements.txt`:
```
openai==1.40.0
```

**Bước 2:** Tạo file `utils/real_llm.py`:

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask(question: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": question}],
        max_tokens=int(os.getenv("MAX_TOKENS", "500")),
    )
    return response.choices[0].message.content
```

**Bước 3:** Sửa import trong `app/main.py`:

```python
# Thay dòng:
from utils.mock_llm import ask as llm_ask

# Bằng:
import os
if os.getenv("OPENAI_API_KEY"):
    from utils.real_llm import ask as llm_ask
else:
    from utils.mock_llm import ask as llm_ask
```

**Bước 4:** Set API key:
```bash
export OPENAI_API_KEY=sk-...
```

---

### 5.3. Cách deploy lên Railway

**Bước 1:** Cài Railway CLI:
```bash
npm i -g @railway/cli
```

**Bước 2:** Đăng nhập và khởi tạo:
```bash
cd 06-lab-complete
railway login
railway init
```

**Bước 3:** Set biến môi trường:
```bash
railway variables set OPENAI_API_KEY=sk-...
railway variables set AGENT_API_KEY=your-secret-key-here
railway variables set JWT_SECRET=your-jwt-secret-here
railway variables set ENVIRONMENT=production
```

**Bước 4:** Deploy:
```bash
railway up
railway domain   # Nhận public URL
```

**Bước 5:** Kiểm tra:
```bash
curl https://your-app.up.railway.app/health
```

Railway tự động đọc `railway.toml` để cấu hình start command, health check, và restart policy.

---

### 5.4. Cách debug khi Agent không phản hồi

**Bước 1: Kiểm tra Health Check**
```bash
curl http://localhost:8086/health
curl http://localhost:8086/ready
```

Nếu `/health` trả 200 nhưng `/ready` trả 503 → Agent đang khởi động hoặc shutting down.

**Bước 2: Xem logs**

Logs ở dạng JSON structured, dễ filter:
```bash
# Nếu chạy docker
docker compose logs agent

# Nếu chạy python
python app/main.py  # logs in ra stdout
```

Tìm events quan trọng:
- `{"event": "startup"}` — agent khởi động
- `{"event": "ready"}` — agent sẵn sàng
- `{"event": "request", ...}` — mỗi request
- `{"event": "shutdown"}` — đang tắt

**Bước 3: Kiểm tra Rate Limit**
```bash
curl http://localhost:8086/health
# Xem "total_requests" trong response
```

Nếu nhận 429 → đã vượt rate limit. Chờ 60 giây hoặc check `Retry-After` header.

**Bước 4: Kiểm tra Budget**

Gọi `/metrics` (cần API key):
```bash
curl -H "X-API-Key: <key>" http://localhost:8086/metrics
# Xem daily_cost_usd và budget_used_pct
```

Nếu `budget_used_pct` ≥ 100% → nhận 503 cho đến ngày mai.

**Bước 5: Kiểm tra Docker**
```bash
docker compose ps                  # Xem service status
docker compose logs --tail=50 agent # 50 dòng log gần nhất
docker compose restart agent        # Restart agent
```

---

### 5.5. Cách thêm lớp bảo mật mới

**Ví dụ:** Thêm IP whitelist middleware.

**Bước 1:** Thêm biến config trong `app/config.py`:

```python
ip_whitelist: list = field(
    default_factory=lambda: os.getenv("IP_WHITELIST", "").split(",")
)
```

**Bước 2:** Thêm middleware trong `app/main.py` (sau CORS middleware):

```python
@app.middleware("http")
async def ip_filter(request: Request, call_next):
    if settings.ip_whitelist and settings.ip_whitelist != [""]:
        client_ip = request.client.host if request.client else "unknown"
        if client_ip not in settings.ip_whitelist:
            raise HTTPException(403, "IP not allowed")
    return await call_next(request)
```

**Bước 3:** Set biến môi trường:
```bash
IP_WHITELIST=192.168.1.100,10.0.0.1
```

---

### 5.6. Cách chạy test stateless scaling

**Bước 1:** Đảm bảo Docker Compose đang chạy với nhiều instances:
```bash
cd 05-scaling-reliability/production
docker compose up --scale agent=3
```

**Bước 2:** Chạy test script:
```bash
python test_stateless.py
```

Script sẽ gửi 5 request liên tiếp và hiển thị:
- `served_by` khác nhau cho mỗi request (round-robin qua Nginx)
- Conversation history vẫn nhất quán (Redis đảm bảo)

---

### 5.7. Cách kiểm tra Production Readiness

```bash
cd 06-lab-complete
python check_production_ready.py
```

Output mẫu:
```
  📁 Required Files
  ✅ Dockerfile exists
  ✅ docker-compose.yml exists
  ✅ .dockerignore exists

  🔒 Security
  ✅ .env in .gitignore
  ✅ No hardcoded secrets in code

  🌐 API Endpoints
  ✅ /health endpoint defined
  ✅ /ready endpoint defined
  ✅ Authentication implemented

  🐳 Docker
  ✅ Multi-stage build
  ✅ Non-root user

  Result: 18/18 checks passed (100%)
  🎉 PRODUCTION READY! Deploy nào!
```

Nếu có item ❌ → sửa theo chỉ dẫn trước khi deploy.

---

## 6. Best Practices & Cảnh Báo

### Những lỗi thường gặp

| Lỗi | Hậu quả | Cách tránh |
|-----|---------|-----------|
| Hardcode API key trong code | Key bị lộ khi push GitHub | Luôn dùng `os.getenv()`, commit `.env.example` thay vì `.env` |
| Bind `localhost` thay vì `0.0.0.0` | Container không nhận kết nối từ bên ngoài | Luôn dùng `host="0.0.0.0"` |
| Quên endpoint `/health` | Cloud platform không biết agent bị crash | Luôn có `/health` trả 200 response |
| Port cứng `8086` | Railway/Render inject PORT khác | Luôn đọc `int(os.getenv("PORT", 8086))` |
| `reload=True` trong production | Tốn resource, không ổn định | Chỉ `reload` khi `DEBUG=true` |
| Lưu session trong memory | Bug khi scale nhiều instances | Dùng Redis cho shared state |
| Chạy container với root user | Rủi ro bảo mật cao | Tạo non-root user trong Dockerfile |
| Dùng `print()` thay vì `logging` | Khó parse trong log aggregator | Dùng structured JSON logging |

### Workflow phát triển khuyến nghị

```
1. Viết code mới → test local (python app.py)
2. Build Docker image → test trong container
3. Chạy docker compose → test full stack
4. Chạy check_production_ready.py → đảm bảo đạt 100%
5. Deploy staging (Railway/Render) → test public URL
6. Deploy production → monitor logs + /health
```

### Checklist trước khi deploy Production

- [ ] Mọi config từ environment variables (không hardcode)
- [ ] `.env` trong `.gitignore` (không commit secrets)
- [ ] Endpoint `/health` và `/ready` hoạt động
- [ ] Authentication (API Key hoặc JWT) trên mọi endpoint nhạy cảm
- [ ] Rate limiting đã cấu hình hợp lý
- [ ] Cost guard đã set budget
- [ ] Dockerfile multi-stage, non-root user
- [ ] Graceful shutdown xử lý SIGTERM
- [ ] Structured JSON logging
- [ ] CORS chỉ cho phép origins cần thiết
- [ ] Security headers (X-Content-Type-Options, X-Frame-Options)
- [ ] `check_production_ready.py` trả 100%

---

## 7. Tổng Kết

### Kiến thức chính đã học

1. **Dev ≠ Production** — Code chạy local khác xa code deploy thật. 12-Factor App là tiêu chuẩn vàng cho cloud-native applications.

2. **Docker là bắt buộc** — Multi-stage build giảm image từ 800 MB xuống 160 MB. Non-root user + HEALTHCHECK là security baseline.

3. **Cloud deployment đa dạng** — Railway/Render cho MVP nhanh (< 10 phút). GCP Cloud Run cho production (CI/CD tự động).

4. **Security là lớp** — Không có giải pháp bảo mật đơn lẻ. Cần kết hợp: Auth → Rate Limit → Input Validation → Cost Guard.

5. **Stateless để scale** — Agent không giữ state trong memory. Redis là giải pháp cho shared session/cache khi có nhiều instances.

6. **Observability quan trọng** — Health check, readiness probe, structured logging, metrics — giúp phát hiện và xử lý sự cố nhanh chóng.

### Lộ trình học khuyến nghị

```
Bước 1: Chạy 01-develop, đếm 5 anti-patterns
     ↓
Bước 2: Chạy 01-production, so sánh sự khác biệt
     ↓
Bước 3: Build Docker image (02-develop → 02-production)
     ↓
Bước 4: Deploy thử Railway/Render (03)
     ↓
Bước 5: Thêm security stack (04)
     ↓
Bước 6: Test scaling với Redis (05)
     ↓
Bước 7: Tự làm Lab 06 từ đầu trước khi xem solution
     ↓
Bước 8: Chạy check_production_ready.py → đạt 100%
```

---

> **Tác giả phân tích:** Tài liệu được tạo tự động dựa trên việc đọc và phân tích toàn bộ 25 file Python, 3 Dockerfile, 17 file cấu hình, và 8 file tài liệu Markdown trong repository.
