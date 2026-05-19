# BrainSpark CI/CD 流水线设计

> 本文档详细描述 BrainSpark 项目的 CI/CD 流水线架构，包括代码检查、测试、构建、镜像推送、自动部署和回滚策略。

## 1. CI 流水线

### 1.1 代码检查阶段

在代码提交后立即触发静态分析，确保代码质量：

```yaml
lint-and-check:
  name: Lint & Type Check
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: "pnpm"
    
    - name: Install dependencies
      run: pnpm install --frozen-lockfile
    
    - name: Frontend Lint (Student Web)
      run: pnpm --filter @brainspark/student lint
    
    - name: Frontend Lint (Teacher Web)
      run: pnpm --filter @brainspark/teacher lint
    
    - name: Frontend Lint (Parent Web)
      run: pnpm --filter @brainspark/parent lint
    
    - name: TypeScript Type Check
      run: |
        pnpm --filter @brainspark/student type-check
        pnpm --filter @brainspark/teacher type-check
        pnpm --filter @brainspark/parent type-check
    
    - name: Java Checkstyle
      run: |
        cd apps/backend-business
        mvn checkstyle:check
    
    - name: Go Lint
      run: |
        cd apps/backend-gateway
        golangci-lint run ./...
    
    - name: Python Flake8
      run: |
        cd apps/ai-service
        pip install flake8
        flake8 app/ --max-line-length=120
```

| 检查工具 | 应用场景 | 配置位置 |
|---------|---------|---------|
| ESLint | Vue 3 前端代码规范 | `packages/eslint-config/` |
| Prettier | 代码格式化 | 根目录 `.prettierrc` |
| Checkstyle | Java 代码规范 | `apps/backend-business/pom.xml` |
| golangci-lint | Go 代码规范 | `apps/backend-gateway/.golangci.yml` |
| Flake8 | Python 代码规范 | `apps/ai-setup/pyproject.toml` |

### 1.2 单元测试阶段

使用 `pnpm turbo` 并行执行前端测试，后端使用各自测试框架：

```yaml
test:
  name: Run Tests
  runs-on: ubuntu-latest
  needs: lint-and-check
  services:
    mysql:
      image: mysql:8.0
      env:
        MYSQL_ROOT_PASSWORD: root
      ports:
        - 3306:3306
    redis:
      image: redis:7-alpine
      ports:
        - 6379:6379
    clickhouse:
      image: clickhouse/clickhouse-server:23.8
      ports:
        - 8123:8123
  steps:
    - uses: actions/checkout@v4
    
    - name: Install dependencies
      run: pnpm install --frozen-lockfile
    
    - name: Frontend Unit Tests
      run: pnpm turbo run test --filter=@brainspark/student --filter=@brainspark/teacher --filter=@brainspark/parent
    
    - name: Shared Packages Tests
      run: pnpm turbo run test --filter=@brainspark/shared-types --filter=@brainspark/api-client
    
    - name: Backend Java Unit Tests
      run: |
        cd apps/backend-business
        mvn test
      env:
        MYSQL_ROOT_PASSWORD: root
        REDIS_URI: localhost:6379
        CLICKHOUSE_HOST: localhost
    
    - name: Go Unit Tests
      run: |
        cd apps/backend-gateway
        go test ./...
    
    - name: Python Unit Tests
      run: |
        cd apps/ai-service
        pip install -r requirements.txt
        pytest tests/ --cov=app --cov-report=xml
```

| 测试类型 | 工具 | 覆盖范围 |
|---------|-----|---------|
| 前端单元测试 | Vitest | Vue 组件、Composables、工具函数 |
| 前端集成测试 | Playwright | 关键用户流程 |
| Java 单元测试 | JUnit 5 + Mockito | Service 层、工具类 |
| Go 单元测试 | testing | Handler、Middleware、Service |
| Python 单元测试 | pytest | RAG 服务、分析器 |

### 1.3 集成测试阶段

使用 Testcontainers 提供隔离的数据库环境：

```yaml
integration-test:
  name: Integration Tests
  runs-on: ubuntu-latest
  needs: test
  steps:
    - uses: actions/checkout@v4
    
    - name: Java Integration Tests (Testcontainers)
      run: |
        cd apps/backend-business
        mvn test -Pintegration
      env:
        TESTCONTAINERS_RYUK_DISABLED: true
    
    - name: Go Integration Tests
      run: |
        cd apps/backend-gateway
        go test -tags=integration ./...
    
    - name: Python Integration Tests
      run: |
        cd apps/ai-service
        pytest tests/integration/ --cov=app
```

| 组件 | 测试策略 |
|------|---------|
| MySQL | Testcontainers MySQL 8.0 |
| Redis | Testcontainers Redis 7 |
| ClickHouse | Testcontainers ClickHouse |
| Milvus | Docker Compose Milvus standalone |
| Kafka | Testcontainers Kafka |

### 1.4 构建阶段

使用 Turborepo 进行全量构建，利用缓存加速：

```yaml
build:
  name: Build All
  runs-on: ubuntu-latest
  needs: integration-test
  steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: "pnpm"
    
    - name: Install dependencies
      run: pnpm install --frozen-lockfile
    
    - name: Full Build with Turborepo
      run: pnpm turbo run build
    
    - name: Upload Build Artifacts
      uses: actions/upload-artifact@v4
      with:
        name: frontend-builds
        path: |
          apps/student-web/dist/
          apps/teacher-web/dist/
          apps/parent-web/dist/
        retention-days: 7
```

| 构建目标 | 输出目录 | 依赖 |
|---------|---------|------|
| student-web | `apps/student-web/dist/` | shared-types, eslint-config |
| teacher-web | `apps/teacher-web/dist/` | shared-types, eslint-config |
| parent-web | `apps/parent-web/dist/` | shared-types, eslint-config |
| backend-business | `apps/backend-business/target/*.jar` | shared-types (Maven) |
| backend-gateway | `apps/backend-gateway/server` | (Go binary) |
| ai-service | `apps/ai-service/` | (Python bundle) |

### 1.5 镜像推送阶段

构建 Docker 镜像并推送到 GitHub Container Registry：

```yaml
build-and-push:
  name: Build & Push Docker Images
  runs-on: ubuntu-latest
  needs: build
  if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release'))
  permissions:
    contents: read
    packages: write
  
  strategy:
    matrix:
      include:
        - app: backend-gateway
          context: apps/backend-gateway
          dockerfile: apps/backend-gateway/docker/Dockerfile
        - app: backend-business
          context: apps/backend-business
          dockerfile: apps/backend-business/docker/Dockerfile
        - app: ai-service
          context: apps/ai-service
          dockerfile: apps/ai-service/docker/Dockerfile
        - app: student-web
          context: apps/student-web
          dockerfile: apps/student-web/docker/Dockerfile
        - app: parent-web
          context: apps/parent-web
          dockerfile: apps/parent-web/docker/Dockerfile
        - app: teacher-web
          context: apps/teacher-web
          dockerfile: apps/teacher-web/docker/Dockerfile
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Login to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ghcr.io/brainspark/${{ matrix.app }}
        tags: |
          type=sha,prefix=
          type=ref,event=branch
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: ${{ matrix.context }}
        file: ${{ matrix.dockerfile }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

| 镜像 | 注册表 | 标签策略 |
|------|--------|---------|
| `ghcr.io/brainspark/backend-gateway` | GitHub Container Registry | `:sha`, `:latest` |
| `ghcr.io/brainspark/backend-business` | GitHub Container Registry | `:sha`, `:latest` |
| `ghcr.io/brainspark/ai-service` | GitHub Container Registry | `:sha`, `:latest` |
| `ghcr.io/brainspark/student-web` | GitHub Container Registry | `:sha`, `:latest` |
| `ghcr.io/brainspark/teacher-web` | GitHub Container Registry | `:sha`, `:latest` |
| `ghcr.io/brainspark/parent-web` | GitHub Container Registry | `:sha`, `:latest` |

## 2. CD 流水线

### 2.1 自动部署到 Staging 环境

当代码合并到 `main` 分支时，自动部署到 Staging 环境：

```yaml
deploy-staging:
  name: Deploy to Staging
  runs-on: ubuntu-latest
  needs: build-and-push
  if: github.ref == 'refs/heads/main'
  environment:
    name: staging
    url: https://brainspark.staging.example.com
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Helm
      uses: azure/setup-helm@v3
    
    - name: Configure Kubeconfig
      uses: azure/k8s-login-action@v1
      with:
        kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
    
    - name: Deploy via Helm
      run: |
        helm upgrade --install brainspark staging/infrastructure/helm/brainspark-core \
          --namespace staging \
          --set image.tag=${{ github.sha }} \
          --set environment=staging \
          --set replicaCount.business=1 \
          --set replicaCount.gateway=1 \
          --wait --timeout 10m
    
    - name: Run Smoke Tests
      run: |
        curl -f https://brainspark.staging.example.com/api/v1/health
        curl -f https://brainspark.staging.example.com/api/v1/student/health
```

### 2.2 人工审批到 Production

部署到 Production 需要人工审批：

```yaml
deploy-production:
  name: Deploy to Production
  runs-on: ubuntu-latest
  needs: deploy-staging
  if: github.ref == 'refs/heads/main'
  environment:
    name: production
    url: https://brainspark.example.com
  
  # 需要手动触发
  # 使用 GitHub Environments 的审批门禁
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Helm
      uses: azure/setup-helm@v3
    
    - name: Configure Kubeconfig
      uses: azure/k8s-login-action@v1
      with:
        kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
    
    - name: Deploy via Helm
      run: |
        helm upgrade --install brainspark production/infrastructure/helm/brainspark-core \
          --namespace production \
          --set image.tag=${{ github.sha }} \
          --set environment=production \
          --set replicaCount.business=3 \
          --set replicaCount.gateway=2 \
          --wait --timeout 15m
    
    - name: Verify Deployment
      run: |
        kubectl rollout status deployment/backend-business -n production --timeout=300s
        curl -f https://brainspark.example.com/api/v1/health
```

### 2.3 多环境部署策略

| 环境 | Namespace | 部署触发 | 副本数 | 数据库 | 外部 API Key |
|------|-----------|---------|--------|--------|-------------|
| `dev` | `dev` | 推送至 `develop` 分支 | 1 | Docker Compose 单实例 | 共享测试 Key |
| `staging` | `staging` | 合并到 `main` | 业务:1, 网关:1 | 单实例 (副本) | 测试环境 Key |
| `production` | `production` | 人工审批 | 业务:3, 网关:2 | 高可用集群 | 生产环境 Key |

```yaml
# infrastructure/helm/brainspark-core/values-staging.yaml
replicas:
  gateway: 1
  business: 1
  ai_service: 1
  web_app: 1

resources:
  gateway:
    cpu: 250m
    memory: 256Mi
  business:
    cpu: 500m
    memory: 512Mi

database:
  host: staging-mysql.internal
  name: brainspark_staging

externalKeys:
  llm: ${{ secrets.STAGING_LLM_API_KEY }}
  stripe: ${{ secrets.STAGING_STRIPE_KEY }}
```

```yaml
# infrastructure/helm/brainspark-core/values-production.yaml
replicas:
  gateway: 2
  business: 3
  ai_service: 2
  web_app: 3

resources:
  gateway:
    cpu: 500m
    memory: 512Mi
  business:
    cpu: 1000m
    memory: 1Gi

database:
  host: prod-mysql-cluster.internal
  name: brainspark_production

externalKeys:
  llm: ${{ secrets.PRODUCTION_LLM_API_KEY }}
  stripe: ${{ secrets.PRODUCTION_STRIPE_KEY }}
```

## 3. 回滚策略

### 3.1 GitTag 回退机制

通过 Git Tag 实现快速回滚：

```bash
# 查看已部署的版本
kubectl get pods -n production -o jsonpath='{.items[*].spec.containers[*].image}'

# 回滚到指定版本
helm upgrade brainspark infrastructure/helm/brainspark-core \
  --namespace production \
  --set image.tag=abc123 \
  --wait --timeout 10m

# 标记回滚版本
git tag -a v1.2.3-rollback -m "Rollback to abc123"
git push origin v1.2.3-rollback
```

### 3.2 Helm 历史回滚

使用 Helm 自带的能力回滚：

```bash
# 查看发布历史
helm history brainspark -n production

# 回滚到上一个版本
helm rollback brainspark 1 -n production

# 回滚到指定 revision
helm rollback brainspark 3 -n production
```

### 3.3 数据库 Migration 回滚

| 迁移方向 | 工具 | 命令 |
|---------|-----|------|
| 正向迁移 | Flyway (Java) | `mvn flyway:migrate` |
| 正向迁移 | TypeScript (前端) | `knex migrate:latest` |
| 反向回滚 | Flyway | `mvn flyway:undo` |
| 反向回滚 | TypeScript | `knex migrate:rollback` |

```yaml
# apps/backend-business/src/main/resources/db/migration/
V1__initial_schema.sql
V2__add_user_role.sql
V3__add_assessment_fields.sql

# Flyway 回滚命令
-- 回滚到最后一次迁移
Flyway undo V3

-- 验证回滚
Flyway info
```

## 4. 多环境

### 4.1 环境隔离

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Repository                     │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ develop   │  │ main     │  │ release/*             │  │
│  │ (Dev)     │  │ (Staging)│  │ (Pre-Production)     │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
│       │              │                  │                │
│       ▼              ▼                  ▼                │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ dev      │  │ staging  │  │ production            │  │
│  │ Namespace│  │ Namespace│  │ Namespace             │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 4.2 环境变量管理

| 变量 | dev | staging | production |
|------|-----|---------|------------|
| `NODE_ENV` | development | staging | production |
| `DATABASE_URL` | localhost:3306 | staging-mysql | prod-mysql-cluster |
| `REDIS_URL` | localhost:6379 | staging-redis | prod-redis-cluster |
| `LLM_API_KEY` | test-key | ${STAGING_LLM_KEY} | ${PROD_LLM_KEY} |
| `STRIPE_KEY` | test-sk_* | ${STAGING_STRIPE} | ${PROD_STRIPE} |

```bash
# .env.development
NODE_ENV=development
VITE_API_BASE_URL=http://localhost:8080/api/v1

# .env.staging
NODE_ENV=staging
VITE_API_BASE_URL=https://brainspark.staging.example.com/api/v1

# .env.production
NODE_ENV=production
VITE_API_BASE_URL=https://brainspark.example.com/api/v1
```

### 4.3 配置优先级

```
1. K8s Secrets (最高优先级 - 敏感信息)
2. K8s ConfigMaps (非敏感配置)
3. Helm values.yaml (环境默认值)
4. 容器环境变量 (部署时覆盖)
5. 应用默认配置 (最低优先级)
```

```yaml
# deployment.yaml 配置示例
env:
  - name: SPRING_DATASOURCE_URL
    valueFrom:
      secretKeyRef:
        name: business-db-secret
        key: datasource-url
  - name: NODE_ENV
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: node-env
  - name: LLM_API_KEY
    valueFrom:
      secretKeyRef:
        name: ai-secrets
        key: llm-key
```

## 5. 分支策略

### 5.1 Git Flow 流程

```
master (main)
├── develop (集成分支)
│   ├── feature/add-assessment
│   ├── feature/fix-login-bug
│   ├── feature/update-report-design
│   └── bugfix/correct-timeout
├── release/v1.2.0 (预发布)
│   └── hotfix/urgent-security-patch
└── main (生产环境)
```

| 分支类型 | 命名规范 | 部署目标 | 生命周期 |
|---------|---------|---------|---------|
| `main` | `main` | Staging | 永久 |
| `develop` | `develop` | Dev | 永久 |
| `feature` | `feature/<描述>` | 无 | 临时 |
| `release` | `release/<version>` | Staging | 短期 |
| `hotfix` | `hotfix/<描述>` | Production | 临时 |

### 5.2 PR 检查门禁

所有 PR 必须通过以下检查才能合并：

```yaml
# .github/pull_request_template.md
## PR 检查清单

- [ ] 代码已通过 ESLint / Checkstyle / golangci-lint
- [ ] 单元测试全部通过
- [ ] 新增功能已添加对应测试
- [ ] 已更新相关文档
- [ ] 无敏感信息泄露 (API Key, 密码)
- [ ] 数据库变更已编写 Migration 脚本
```

| 检查项 | 工具 | 失败处理 |
|-------|------|---------|
| 代码规范 | ESLint, Checkstyle, golangci-lint | 阻止合并 |
| 类型检查 | TypeScript `type-check` | 阻止合并 |
| 单元测试 | Vitest, JUnit, pytest | 阻止合并 |
| 集成测试 | Testcontainers | 告警 |
| 安全扫描 | Trivy, Semgrep | 阻止合并 |
| 文档更新 | 人工审查 | 告警 |

### 5.3 代码审查要求

| 规则 | 要求 |
|------|------|
| 最低审查人数 | 2 人 |
| 审查者资格 | 非 PR 作者的核心贡献者 |
| 自动分配 | 基于代码更改范围分配审查者 |
| LGTM 要求 | 所有评论已解决或被采纳 |
| 变更日志 | 重大变更需更新 CHANGELOG.md |

```yaml
# .github/CODEOWNERS
# 前端代码审查
/apps/student-web/ @brainspark/frontend-team @reviewer-1 @reviewer-2
/apps/teacher-web/ @brainspark/frontend-team @reviewer-1
/apps/parent-web/ @brainspark/frontend-team @reviewer-1
/packages/ @brainspark/core-team @reviewer-1 @reviewer-2

# 后端代码审查
/apps/backend-business/ @brainspark/backend-team @reviewer-3
/apps/backend-gateway/ @brainspark/gateway-team @reviewer-3
/apps/ai-service/ @brainspark/ai-team @reviewer-4

# 基础设施代码审查
/infra/ @brainspark/infra-team @reviewer-5
/docs/infrastructure/ @brainspark/infra-team @reviewer-5
```

---

> **总结**: BrainSpark 的 CI/CD 流水线通过 GitHub Actions 实现自动化，涵盖代码检查、测试、构建、镜像推送和部署全流程。通过多环境隔离和严格的分支策略，确保生产环境稳定性和代码质量。