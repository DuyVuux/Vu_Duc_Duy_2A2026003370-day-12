# Day 12 Lab - Mission Answers

> **Student Name:** Vũ Đức Duy
> **Student ID:** 2A202600337
> **Date:** 17/04/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

Sau khi đọc file `01-localhost-vs-production/develop/app.py`, tìm được **5 anti-patterns** sau:

1. **Hardcode API key & secrets trong source code** (dòng 17-18):
   ```python
   OPENAI_API_KEY = "sk-hardcoded-fake-key-never-do-this"
   DATABASE_URL = "postgresql://admin:password123@localhost:5432/mydb"
   ```
   Nếu push lên GitHub, toàn bộ credentials bị lộ công khai.

2. **Không có config management** (dòng 21-22):
   ```python
   DEBUG = True
   MAX_TOKENS = 500
   ```
   Giá trị cấu hình cứng trong code, không thể thay đổi theo môi trường (dev/staging/prod) mà không sửa code.

3. **Dùng `print()` thay vì structured logging, và log ra secrets** (dòng 33-34):
   ```python
   print(f"[DEBUG] Got question: {question}")
   print(f"[DEBUG] Using key: {OPENAI_API_KEY}")
   ```
   `print()` không có log level, không có timestamp chuẩn, không thể parse bởi log aggregator (Datadog, Loki). Nghiêm trọng hơn, API key bị in ra log.

4. **Không có health check endpoint**:
   Không có `/health` hay `/ready` endpoint. Khi deploy lên cloud, platform không biết agent có đang hoạt động hay đã crash để tự động restart.

5. **Port cố định, bind `localhost`, và `reload=True` trong production** (dòng 49-54):
   ```python
   host="localhost",   # chỉ chạy được trên local, container bên ngoài không kết nối được
   port=8086,          # cứng port, cloud platform inject PORT khác qua env var
   reload=True         # tốn resource, không ổn định trong production
   ```

### Exercise 1.3: Comparison table

| Feature | Basic (`develop/app.py`) | Advanced (`production/app.py`) | Tại sao quan trọng? |
|---------|--------------------------|-------------------------------|----------------------|
| Config | Hardcode trực tiếp trong code (`DEBUG = True`, `OPENAI_API_KEY = "sk-..."`) | Đọc từ environment variables qua `config.py` (`settings.port`, `settings.debug`) | Cho phép thay đổi cấu hình theo môi trường mà không cần sửa code. Tránh lộ secrets khi push lên Git |
| Health check | Không có | Có `/health` (liveness) và `/ready` (readiness) | Cloud platform dùng endpoint này để biết khi nào cần restart container hoặc ngừng route traffic |
| Logging | `print()` — in ra cả secrets | Structured JSON logging (`logging` module) — không log secrets | JSON log dễ parse bởi log aggregator, hỗ trợ filter theo level, có timestamp chuẩn |
| Shutdown | Đột ngột — tắt ngay lập tức | Graceful — xử lý SIGTERM, hoàn thành request đang chạy rồi mới tắt | Tránh mất dữ liệu và request bị gián đoạn khi platform cần restart/redeploy |
| Host binding | `localhost` — chỉ truy cập từ máy local | `0.0.0.0` — nhận kết nối từ bên ngoài container | Container và cloud platform cần truy cập từ bên ngoài, `localhost` sẽ từ chối mọi external connection |
| Port | Cứng `8086` | Đọc từ `PORT` env var | Railway/Render tự inject PORT khác nhau, hardcode sẽ gây conflict |
| CORS | Không có | Có CORSMiddleware với origins được cấu hình | Bảo mật: chỉ cho phép frontend từ domain được phép gọi API |
| Reload | `reload=True` luôn | `reload` chỉ khi `DEBUG=true` | Hot reload tốn resource và không ổn định trong production |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. **Base image:** Base image trong Dockerfile là lớp nền tảng (image gốc) được chỉ định bởi câu lệnh `FROM`, đóng vai trò là hệ điều hành hoặc môi trường runtime cơ bản để xây dựng một Docker image mới. Ở đây là `python:3.11`.

2. **Working directory:** Là một chỉ thị (instruction) được sử dụng để thiết lập thư mục làm việc hiện tại cho các lệnh tiếp theo như `RUN`, `CMD`, `ENTRYPOINT`, `COPY`, và `ADD`. Ở đây là `/app`.

3. **Why copy `requirements.txt` first:** Để tận dụng cache của Docker. Nếu `requirements.txt` không thay đổi, Docker sẽ cache bước cài đặt dependencies, giúp build nhanh hơn khi chỉ thay đổi code. Và nếu không copy file `requirements.txt` trước, thì lệnh `pip install` sau sẽ không chạy được.

4. **CMD vs ENTRYPOINT:** `CMD` cung cấp lệnh mặc định có thể bị ghi đè khi chạy container, trong khi `ENTRYPOINT` xác định lệnh cố định không thể bị thay đổi. Sử dụng `ENTRYPOINT` giúp đảm bảo rằng ứng dụng luôn chạy đúng cách, bất kể tham số nào được truyền vào khi khởi động container.

### Exercise 2.3: Image size comparison

| Loại | Dung lượng |
|------|-----------|
| Develop (single-stage) | 1.67 GB |
| Production (multi-stage) | 262 MB |
| **Chênh lệch** | **84.68%** |

**Giải thích:** Multi-stage build chỉ copy những artifacts cần thiết (dependencies đã cài, source code) sang image runtime cuối cùng. Image không chứa build tools, compiler, cache — giảm đáng kể dung lượng và attack surface.

### Exercise 2.4: Docker Compose stack

**Services được start:**

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│    Nginx     │────▶│   Agent     │────▶│    Redis     │     │   Qdrant     │
│  (Port 80)  │     │ (Port 8086) │     │ (Port 6379)  │     │ (Port 6333)  │
│  Reverse    │     │  FastAPI    │     │   Cache /    │     │  Vector DB   │
│  Proxy / LB │     │  + Uvicorn  │     │   Session    │     │   (Demo)     │
└─────────────┘     └─────────────┘     └──────────────┘     └──────────────┘
```

- **Nginx:** Reverse proxy và load balancer, nhận traffic từ bên ngoài (port 80) và chuyển tiếp đến Agent
- **Agent:** FastAPI application chạy trên Uvicorn, xử lý business logic
- **Redis:** Lưu trữ session, rate limiting data, cost tracking — cho phép agent stateless
- **Qdrant:** Vector database dùng cho demo semantic search

Nginx communicate với Agent qua internal Docker network. Agent communicate với Redis và Qdrant cũng qua internal network.

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

- **Platform:** Render
- **URL:** https://ai-agent-production-xxxx.onrender.com *(deployed via Render Blueprint)*
- **Test:** Health check endpoint trả về `{"status": "ok"}`

### Exercise 3.2: So sánh `render.yaml` vs `railway.toml`

| Tiêu chí | `railway.toml` (TOML format) | `render.yaml` (YAML format) |
|----------|------------------------------|------------------------------|
| **Format** | TOML — key-value đơn giản | YAML — hỗ trợ nested structure phức tạp |
| **Builder** | `NIXPACKS` (auto-detect) | Chỉ định `runtime: python` hoặc `runtime: docker` |
| **Start command** | `startCommand` trong `[deploy]` | `startCommand` trong service definition |
| **Health check** | `healthcheckPath` + `healthcheckTimeout` | `healthCheckPath` (không có timeout config) |
| **Restart policy** | `restartPolicyType = "ON_FAILURE"`, `restartPolicyMaxRetries = 3` | Không có — Render tự quản lý |
| **Region** | Không chỉ định trong file | `region: singapore` |
| **Env vars** | Set qua CLI: `railway variables set KEY=VALUE` | Khai báo trực tiếp trong YAML: `envVars`, hỗ trợ `sync: false` và `generateValue: true` |
| **Auto deploy** | Mặc định khi push | `autoDeploy: true` — khai báo tường minh |
| **Multi-service** | Mỗi service cần file riêng | Một file `render.yaml` định nghĩa nhiều services (agent + Redis) |
| **Infrastructure as Code** | Chỉ config deploy | Đầy đủ IaC: services, databases, env vars trong 1 file |

**Nhận xét:** `render.yaml` mạnh hơn ở khả năng định nghĩa toàn bộ infrastructure trong 1 file (Blueprint), bao gồm cả Redis add-on. `railway.toml` đơn giản hơn nhưng cần set biến môi trường qua CLI/Dashboard riêng.

### Exercise 3.3: GCP Cloud Run (Optional)

**`cloudbuild.yaml` — CI/CD Pipeline:**
- Định nghĩa pipeline tự động: chạy test → build Docker image → push lên Container Registry → deploy lên Cloud Run
- Mỗi step là một container builder riêng biệt

**`service.yaml` — Knative Service Definition:**
- Định nghĩa Cloud Run service: container image, CPU/memory limits, scaling (min/max instances), concurrency, env vars
- Dạng declarative — khai báo trạng thái mong muốn, Cloud Run tự đảm bảo

---

## Part 4: API Security

### Exercise 4.1: API Key authentication

**Không có key:**
```json
{
    "detail": "Missing API key. Include header: X-API-Key: <your-key>"
}
```

**Có key:**
```json
{
    "question": "Hello",
    "answer": "Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé."
}
```

**Phân tích:**
- API key được kiểm tra qua header `X-API-Key` trong hàm `verify_api_key` (dependency injection của FastAPI)
- Nếu thiếu hoặc sai key → trả về HTTP 401 Unauthorized
- Để rotate key: thay đổi biến môi trường `AGENT_API_KEY` và restart service — không cần sửa code

### Exercise 4.2: JWT authentication

**Lấy token:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in_minutes": 60,
    "hint": "Include in header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
}
```

**Dùng token để gọi API:**
```json
{
    "question": "Explain JWT",
    "answer": "Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.",
    "usage": {
        "requests_remaining": 99,
        "budget_remaining_usd": 1.9e-05
    }
}
```

**JWT Flow:**
1. Client gọi `POST /auth/token` với `username` + `password`
2. Server verify credentials, tạo JWT token (HS256, hết hạn 60 phút)
3. Client gửi token trong header `Authorization: Bearer <token>`
4. Server decode token → extract `username` + `role` → xử lý request

### Exercise 4.3: Rate limiting

- **Algorithm:** Sliding Window Counter — dùng `deque` lưu timestamps của mỗi request, xoá các request cũ hơn window (60 giây), đếm số request còn lại
- **Limit:**
  - User thường: **10 requests/minute**
  - Admin: **100 requests/minute**
- **Bypass cho admin:** Không bypass hoàn toàn. Admin sử dụng `rate_limiter_admin` với limit cao hơn (100 req/phút) thay vì limiter của user (10 req/phút)

**Test output khi vượt limit:**
```json
{
    "detail": {
        "error": "Rate limit exceeded",
        "limit": 100,
        "window_seconds": 60,
        "retry_after_seconds": 12
    }
}
```

### Exercise 4.4: Cost guard implementation

**Approach:** Sử dụng 2 lớp bảo vệ budget:

1. **Per-user budget:** $1/ngày — trả HTTP 402 nếu user vượt ngưỡng
2. **Global budget:** $10/ngày — trả HTTP 503 nếu toàn hệ thống vượt ngưỡng

**Logic tính cost:**
- Input pricing: `$0.15 / 1M tokens` (GPT-4o-mini)
- Output pricing: `$0.60 / 1M tokens`
- Ước lượng tokens từ số words: `tokens ≈ words × 2`
- Cảnh báo khi user dùng 80% budget

**Implementation pattern:**
```python
def check_budget(user_id: str, estimated_cost: float) -> bool:
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    current = float(r.get(key) or 0)
    if current + estimated_cost > 10:
        return False
    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)
    return True
```

---

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

**1. Health Checks & Graceful Shutdown (Ex 5.1 & 5.2):**

- Endpoint `/health` để theo dõi liveness và `/ready` cho readiness
- Graceful shutdown thông qua tín hiệu `SIGTERM`, cho phép uvicorn hoàn thành các in-flight requests trước khi tắt

**Test Output:**
```bash
curl http://localhost:8000/health
# result: 200 OK

curl http://localhost:8000/ready
# result: 200 OK

curl http://localhost:8000/ask -X POST -H "Content-Type: application/json" \
  -d '{"question": "Long task"}' & sleep 1; kill -TERM 59709
# result:
# INFO:     Shutting down
# INFO:     Waiting for application shutdown.
# 2026-04-17 17:21:56 INFO 🔄 Graceful shutdown initiated...
# 2026-04-17 17:21:56 INFO ✅ Shutdown complete
# INFO:     Application shutdown complete.
# INFO:     Finished server process [59709]
# 2026-04-17 17:21:56 INFO Received signal 15 — uvicorn will handle graceful shutdown
```

**2. Stateless Design (Ex 5.3):**

Để scale ra nhiều instances mà không mất context (lịch sử chat) của user, trạng thái ứng dụng đã được tách khỏi bộ nhớ in-memory và lưu trữ tập trung tại Redis. Mỗi instance đều đọc/ghi cùng một Redis, đảm bảo tính nhất quán.

**3. Load Balancing (Ex 5.4):**

Nginx được sử dụng làm Load Balancer phân phối traffic round-robin đến các agent instances.

**Test Output:**
```bash
for i in {1..10}; do
  curl http://localhost:8080/chat -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "Request '$i'"}'
done

# Logs cho thấy traffic được phân phối giữa agent-1 và agent-2:
# agent-1  | INFO: "POST /chat HTTP/1.1" 200 OK
# agent-2  | INFO: "POST /chat HTTP/1.1" 200 OK
```

**4. Test Stateless (Ex 5.5):**

Chạy `docker compose up --scale agent=3` và `python test_stateless.py`:

```
Session ID: fb63959a-60f1-4f14-8181-14ede41e02a5

Request 1: [instance-9f25e6] Q: What is Docker?
Request 2: [instance-a59fad] Q: Why do we need containers?
Request 3: [instance-62d1d9] Q: What is Kubernetes?
Request 4: [instance-9f25e6] Q: How does load balancing work?
Request 5: [instance-a59fad] Q: What is Redis used for?

Total requests: 5
Instances used: {'instance-62d1d9', 'instance-a59fad', 'instance-9f25e6'}
✅ All requests served despite different instances!

--- Conversation History ---
Total messages: 10
✅ Session history preserved across all instances via Redis!
```

**Kết luận:** 3 instances khác nhau phục vụ 5 requests, nhưng conversation history vẫn nhất quán nhờ Redis làm shared state store.
