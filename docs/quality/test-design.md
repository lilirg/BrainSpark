# 测试架构设计文档

> BrainSpark 项目测试策略与架构设计

## 概述

本文档定义 BrainSpark monorepo 项目的完整测试架构，覆盖单元测试、集成测试、E2E 测试、性能测试及测试数据管理，并与 CI/CD 流水线集成。

---

## 1. 单元测试

### 1.1 Vue 前端项目（Vitest）

**适用项目**: `apps/student-web`、`apps/parent-web`、`apps/teacher-web`

#### 配置示例

```json
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { vitest } from 'vitest'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80
      }
    }
  }
})
```

#### 组件测试示例

```typescript
// tests/components/StudentCard.spec.ts
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/vue'
import StudentCard from '../../src/components/StudentCard.vue'

describe('StudentCard', () => {
  it('渲染学生姓名', () => {
    render(StudentCard, {
      props: { name: '张三', score: 95 }
    })
    expect(screen.getByText('张三')).toBeTruthy()
  })

  it('显示正确分数等级', () => {
    render(StudentCard, {
      props: { name: '李四', score: 60 }
    })
    expect(screen.getByText('及格')).toBeTruthy()
  })
})
```

#### Pinia Store 测试

```typescript
// tests/stores/userStore.spec.ts
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '../../src/stores/user'

describe('useUserStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('正确初始化用户状态', () => {
    const store = useUserStore()
    expect(store.user).toBeNull()
  })

  it('登录成功更新用户信息', () => {
    const store = useUserStore()
    store.login({ id: 1, name: '张三', role: 'student' })
    expect(store.user?.name).toBe('张三')
  })
})
```

### 1.2 Java 后端（JUnit 5 + Mockito）

**适用项目**: `apps/backend-business`

#### 依赖配置

```xml
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

#### Controller 测试示例

```java
// src/test/java/com/brainspark/controller/UserControllerTest.java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void shouldReturnUserById() throws Exception {
        User user = new User(1L, "张三", "student");
        when(userService.findById(1L)).thenReturn(user);

        mockMvc.perform(get("/api/v1/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.name").value("张三"));
    }

    @Test
    void shouldCreateUser() throws Exception {
        CreateUserDTO dto = new CreateUserDTO("李四", "student");
        
        mockMvc.perform(post("/api/v1/users")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(dto)))
            .andExpect(status().isCreated());
    }
}
```

#### Service 层测试

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @InjectMocks
    private UserService userService;

    @Mock
    private UserRepository userRepository;

    @Test
    void shouldFindUserByEmail() {
        when(userRepository.findByEmail("test@example.com"))
            .thenReturn(Optional.of(new User(1L, "张三", "test@example.com")));

        User result = userService.findByEmail("test@example.com");
        assertNotNull(result);
    }

    @Test
    void shouldThrowWhenUserNotFound() {
        when(userRepository.findByEmail("unknown@example.com"))
            .thenReturn(Optional.empty());

        assertThrows(EntityNotFoundException.class, 
            () -> userService.findByEmail("unknown@example.com"));
    }
}
```

### 1.3 Go 网关（testing 包）

**适用项目**: `apps/backend-gateway`

#### Handler 测试示例

```go
// internal/handler/handler_test.go
package handler

import (
    "net/http"
    "net/http/httptest"
    "testing"
)

func TestHealthHandler(t *testing.T) {
    req := httptest.NewRequest("GET", "/health", nil)
    w := httptest.NewRecorder()

    HealthHandler(w, req)

    if w.Code != http.StatusOK {
        t.Errorf("expected status 200, got %d", w.Code)
    }
}
```

#### 中间件测试

```go
// internal/middleware/middleware_test.go
func TestAuthMiddleware(t *testing.T) {
    handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
    })

    middleware := AuthMiddleware(handler)
    req := httptest.NewRequest("GET", "/api/v1/users", nil)
    w := httptest.NewRecorder()

    middleware.ServeHTTP(w, req)

    if w.Code != http.StatusUnauthorized {
        t.Errorf("expected 401, got %d", w.Code)
    }
}
```

### 1.4 Python AI 服务（pytest）

**适用项目**: `apps/ai-service`

#### 配置示例

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

#### API 测试示例

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_assess_analysis():
    payload = {
        "student_id": 1,
        "subject": "math",
        "raw_data": {"scores": [85, 90, 78]}
    }
    response = client.post("/api/v1/analysis")
    assert response.status_code == 200
```

---

## 2. 集成测试

### 2.1 Java Spring Integration Tests

#### 配置

```java
// src/test/java/com/brainspark/BaseIntegrationTest.java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
@Transactional
class BaseIntegrationTest {
    // 测试结束后自动回滚，不污染数据库
}
```

#### 全栈集成测试

```java
@TestConfiguration
static class TestConfig {
    @Bean
    public WebTestClient webTestClient(WebHttpServerBuilder builder) {
        return WebTestClient.bindToServer()
            .baseUrl("http://localhost:" + port)
            .build();
    }
}

@Test
void shouldCreateAndGetUser() {
    UserDTO created = webTestClient.post()
        .uri("/api/v1/users")
        .bodyValue(newUser)
        .retrieve()
        .bodyToMono(UserDTO.class)
        .block();

    webTestClient.get()
        .uri("/api/v1/users/{id}", created.getId())
        .retrieve()
        .bodyToMono(UserDTO.class)
        .assertNext(u -> assertEquals(created.getName(), u.getName()));
}
```

#### 数据库测试容器策略

```java
@Testcontainers
class UserRepositoryIntegrationTest {

    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
        .withDatabaseName("brainspark_test")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", mysql::getJdbcUrl);
        registry.add("spring.datasource.username", mysql::getUsername);
        registry.add("spring.datasource.password", mysql::getPassword);
    }
}
```

### 2.2 FastAPI TestClient 集成测试

```python
# tests/integration/test_api_flow.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_analysis_workflow():
    # 1. 提交分析请求
    submit_response = client.post("/api/v1/analysis", json={
        "student_id": 1,
        "subject": "math",
        "raw_data": {"scores": [85, 90, 78]}
    })
    assert submit_response.status_code == 200
    task_id = submit_response.json()["data"]["task_id"]

    # 2. 查询任务状态
    status_response = client.get(f"/api/v1/analysis/{task_id}")
    assert status_response.status_code == 200

    # 3. 获取报告
    report_response = client.get(f"/api/v1/reports/{task_id}")
    assert report_response.status_code == 200
    assert "suggestions" in report_response.json()["data"]
```

### 2.3 数据库测试容器策略

| 中间件 | 测试容器 | 版本 |
|--------|----------|------|
| MySQL | `testcontainers/mysql` | 8.0 |
| Redis | `testcontainers/redis` | 7.0 |
| MongoDB | `testcontainers/mongodb` | 6.0 |

**策略**:
- 每个测试类启动独立的容器实例
- 使用 `@Transactional` 保证数据回滚（Java）
- 测试前执行 Schema 初始化（Flyway/Liquibase）
- 测试后自动销毁容器，释放资源

---

## 3. E2E 测试

### 3.1 Playwright 方案

#### 配置

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  fullyParallel: true,
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
})
```

#### 安装依赖

```json
// package.json
{
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "@types/playwright": "^1.40.0"
  }
}
```

### 3.2 关键路径用例清单

| 编号 | 用户角色 | 测试场景 | 关键步骤 |
|------|----------|----------|----------|
| E2E-001 | 学生 | 登录并进入学习仪表盘 | 输入账号密码 → 跳转首页 → 验证数据加载 |
| E2E-002 | 学生 | 完成一次测评任务 | 选择科目 → 答题 → 提交 → 查看报告 |
| E2E-003 | 家长 | 查看孩子学习报告 | 登录 → 选择学生 → 查看图表 → 下载PDF |
| E2E-004 | 教师 | 创建班级并管理学生 | 创建班级 → 添加学生 → 发布测评 |
| E2E-005 | 教师 | 查看班级分析报告 | 选择班级 → 查看聚合图表 → 导出报告 |
| E2E-006 | 管理员 | 用户权限管理 | 创建用户 → 分配角色 → 验证权限生效 |
| E2E-007 | 系统 |  WebSocket 实时消息 | 触发事件 → 验证客户端接收通知 |
| E2E-008 | 学生 | 离线数据同步 | 离线操作 → 恢复网络 → 验证同步成功 |

### 3.3 跨浏览器测试

**目标浏览器**:
- Chrome（最新稳定版）
- Firefox（最新稳定版）
- Safari（WebKit）

**执行策略**:
```bash
# 并行执行跨浏览器测试
npx playwright test --project=chromium --project=firefox --project=webkit
```

---

## 4. 性能测试

### 4.1 JMeter/k6 方案

#### k6 配置（推荐 Go 网关压测）

```javascript
// scripts/performance/gateway_load.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 100 },   // 爬坡到 100 VUs
    { duration: '1m', target: 100 },    // 稳态 100 VUs
    { duration: '30s', target: 500 },   // 峰值 500 VUs
    { duration: '1m', target: 500 },    // 稳态 500 VUs
    { duration: '30s', target: 0 },     // 降载
  ],
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],  // P95 < 200ms, P99 < 500ms
    http_req_failed: ['rate<0.01'],                   // 失败率 < 1%
  },
};

export default function () {
  const res = http.get(__ENV.BASE_URL + '/api/v1/health');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
  sleep(1);
}
```

#### JMeter 配置（后端业务接口压测）

**场景设计**:
1. 常规业务接口压测（用户、测评、报告）
2. 并发写入压测（测评提交）
3. 大数据量查询压测（报表聚合）

### 4.2 网关/AI 服务压测策略

| 服务 | 压测工具 | 关注指标 | 基准线 |
|------|----------|----------|--------|
| Go 网关 | k6 | P99 延迟、QPS、错误率 | P99 < 200ms, QPS > 5000 |
| AI 服务 | Locust | 推理延迟、吞吐量、GPU 利用率 | P95 < 5s, 并发 > 50 |
| 业务后端 | JMeter | 接口响应、连接池使用 | P95 < 500ms |

**压测环境**:
- 独立压测集群，与生产环境隔离
- 使用脱敏的生产数据副本
- 数据库使用 ClickHouse 测试实例

### 4.3 基准线定义

| 指标 | 优秀 | 合格 | 警戒 |
|------|------|------|------|
| 网关 P99 | < 100ms | < 200ms | > 500ms |
| 业务 API P95 | < 300ms | < 500ms | > 1000ms |
| AI 推理 P95 | < 3s | < 5s | > 10s |
| 错误率 | < 0.1% | < 1% | > 5% |
| CPU 使用率 | < 60% | < 80% | > 90% |

---

## 5. 测试数据

### 5.1 工厂模式策略

**Python 工厂（AI 服务）**:

```python
# tests/factories.py
from factory import BaseModel, faker
from app.models import Assessment, Report

class AssessmentFactory(BaseModel):
    class Meta:
        model = Assessment

    student_id = 1
    subject = 'math'
    scores = [85, 90, 78]
    created_at = faker.DateTime()

class ReportFactory(BaseModel):
    class Meta:
        model = Report

    assessment_id = 1
    suggestions = ['加强计算训练']
    generated_at = faker.DateTime()
```

**Java 工厂（业务后端）**:

```java
// src/test/java/com/brainspark/factory/TestDataFactory.java
public class TestDataFactory {

    public static User createUser(Long id, String name, String role) {
        User user = new User();
        user.setId(id);
        user.setName(name);
        user.setEmail(name + "@brainspark.edu");
        user.setRole(role);
        return user;
    }

    public static Assessment createAssessment(Long id, Long studentId) {
        Assessment assessment = new Assessment();
        assessment.setId(id);
        assessment.setStudentId(studentId);
        assessment.setSubject("math");
        assessment.setScores(Arrays.asList(85, 90, 78));
        return assessment;
    }
}
```

### 5.2 Mock 数据方案

#### Vue 组件 Mock

```typescript
// tests/mocks.ts
import { vi } from 'vitest'

export const mockUserStore = {
  user: { id: 1, name: '张三', role: 'student' },
  login: vi.fn(),
  logout: vi.fn(),
}

export const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  currentRoute: { path: '/dashboard' },
}
```

#### API Mock（MSW）

```typescript
// tests/setup.ts
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

const handlers = [
  http.get('/api/v1/users/:id', ({ params }) => {
    return HttpResponse.json({
      code: 200,
      data: { id: params.id, name: '张三', role: 'student' }
    })
  }),
]

export const server = setupServer(...handlers)
```

### 5.3 敏感数据脱敏

**测试数据规范**:
- 学生姓名使用假名（张三、李四）
- 邮箱使用固定测试域名（@brainspark.edu）
- 身份证号使用规则生成器
- 手机号使用 138xxxx0001 系列

**脱敏工具**:

```python
# tests/utils/anonymizer.py
import faker

fake = Faker('zh_CN')

def anonymize_student(data: dict) -> dict:
    """脱敏学生数据"""
    return {
        'name': fake.name(),
        'phone': fake.phone_number().replace('-', ''),
        'id_card': fake.ssn(length=18),
        'email': f'{fake.first_name()}@brainspark.edu',
    }
```

---

## 6. CI 集成

### 6.1 GitHub Actions 测试阶段

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package:
          [student-web, parent-web, teacher-web, backend-business, ai-service, backend-gateway]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - name: Install dependencies
        run: pnpm install

      - name: Run unit tests
        run: pnpm --filter @brainspark/${{ matrix.package }} test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          flags: ${{ matrix.package }}

  integration-tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_DATABASE: brainspark_test
          MYSQL_ROOT_PASSWORD: test
        ports:
          - 3306:3306
      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3

      - name: Run integration tests
        run: pnpm --filter @brainspark/backend-business test:integration
        env:
          SPRING_DATASOURCE_URL: jdbc:mysql://localhost:3306/brainspark_test
          SPRING_DATASOURCE_USERNAME: root
          SPRING_DATASOURCE_PASSWORD: test

  e2e-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Start dev server
        run: pnpm --filter @brainspark/student dev &
        env:
          CI: true

      - name: Run E2E tests
        run: npx playwright test --project=${{ matrix.browser }}

  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run k6 performance tests
        run: |
          k6 run scripts/performance/gateway_load.js
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
```

### 6.2 并行测试执行

**Turborepo 配置**:

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "test": {
      "dependsOn": ["^build"],
      "outputs": [],
      "cache": false
    },
    "test:coverage": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "test:integration": {
      "dependsOn": []
    }
  }
}
```

**并行执行命令**:

```bash
# 并行运行所有包的单元测试
pnpm test --parallel

# 带并发限制的并行测试
pnpm test --concurrency=4
```

### 6.3 测试报告与告警

| 指标 | 阈值 | 处理方式 |
|------|------|----------|
| 覆盖率下降 | > 5% | PR 检查失败 |
| 测试超时 | > 60s | 标记 flaky test |
| 失败率 | > 0% | 阻塞合并 |
| E2E 失败 | 任意 | 立即通知 |

---

## 附录

### A. 测试命令速查

| 项目 | 命令 | 说明 |
|------|------|------|
| Vue 前端 | `pnpm --filter @brainspark/student test` | 运行 Vitest |
| Vue 前端 | `pnpm --filter @brainspark/student test:coverage` | 覆盖率报告 |
| Java 后端 | `cd apps/backend-business && mvn test` | JUnit 单元测试 |
| Java 后端 | `cd apps/backend-business && mvn verify` | 包含集成测试 |
| Go 网关 | `cd apps/backend-gateway && go test ./...` | Go 测试 |
| Python AI | `cd apps/ai-service && pytest` | pytest 测试 |
| E2E | `npx playwright test` | Playwright E2E |
| 性能 | `k6 run scripts/performance/gateway_load.js` | k6 压测 |

### B. 参考链接

- [Vitest 官方文档](https://vitest.dev/)
- [JUnit 5 用户指南](https://junit.org/junit5/docs/current/user-guide/)
- [Playwright 文档](https://playwright.dev/)
- [k6 文档](https://k6.io/docs/)
- [Testcontainers 文档](https://java.testcontainers.org/)

---

> 文档版本: v1.0  
> 创建日期: 2026-05-19  
> 维护者: BrainSpark 工程团队
