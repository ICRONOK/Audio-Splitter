# Audio Splitter Suite - AWS Serverless Architecture Proposal

> **Document Version:** 1.0
> **Date:** December 2025
> **Status:** Proposal
> **Target:** Production-Ready Serverless Deployment

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Analysis](#2-current-state-analysis)
3. [Architecture Overview](#3-architecture-overview)
4. [Detailed Component Design](#4-detailed-component-design)
5. [API Design](#5-api-design)
6. [Data Flow & Processing](#6-data-flow--processing)
7. [Multi-Frontend Support](#7-multi-frontend-support)
8. [Security Architecture](#8-security-architecture)
9. [Scalability Strategy](#9-scalability-strategy)
10. [Cost Optimization](#10-cost-optimization)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Monitoring & Observability](#12-monitoring--observability)
13. [Disaster Recovery](#13-disaster-recovery)
14. [Appendices](#14-appendices)

---

## 1. Executive Summary

### 1.1 Objective

Transform Audio Splitter Suite from a CLI application into a **cloud-native, serverless platform** deployed on AWS that:

- Scales from **zero to millions of users** with zero infrastructure management
- Optimizes costs through **pay-per-use pricing** (zero cost at zero usage)
- Supports **multiple frontends**: Web, Mobile, Desktop, API, MCP (Model Context Protocol)
- Maintains **professional-grade audio quality** with scientific validation
- Provides **global availability** with low latency

### 1.2 Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Serverless First** | Lambda, API Gateway, S3, DynamoDB as core services |
| **Event-Driven** | Asynchronous processing with SQS, SNS, EventBridge |
| **Pay-Per-Use** | Zero cost at zero usage, linear scaling with demand |
| **Multi-Tenant** | Isolated user data with shared infrastructure |
| **API-First** | Unified REST/GraphQL API for all frontends |
| **Stateless Processing** | State externalized to DynamoDB/S3 |

### 1.3 Expected Outcomes

| Metric | Target |
|--------|--------|
| Cold Start Latency | < 3 seconds |
| API Response Time (p99) | < 500ms |
| Processing Throughput | 10,000+ concurrent jobs |
| Availability | 99.95% (Multi-AZ) |
| Cost at Zero Usage | $0/month |
| Cost at 1M requests/month | ~$150-300/month |

---

## 2. Current State Analysis

### 2.1 Application Profile

| Aspect | Current State | Cloud Implication |
|--------|---------------|-------------------|
| **Architecture** | Monolithic CLI | Needs decomposition into microservices |
| **State Management** | In-memory | Requires external state store |
| **File Handling** | Local filesystem | Migrate to S3 with presigned URLs |
| **Processing Model** | Synchronous | Async with callbacks/webhooks |
| **Concurrency** | Single-threaded | Parallel Lambda invocations |
| **Monitoring** | Console output | CloudWatch + X-Ray |

### 2.2 Processing Characteristics

```
┌────────────────────────────────────────────────────────────────┐
│                    PROCESSING TIME ANALYSIS                     │
├────────────────────────────────────────────────────────────────┤
│ Operation          │ Duration    │ Memory    │ Lambda Suitable │
├────────────────────┼─────────────┼───────────┼─────────────────┤
│ Metadata Read      │ < 1s        │ 128MB     │ ✅ Perfect       │
│ Metadata Write     │ < 2s        │ 256MB     │ ✅ Perfect       │
│ Audio Split        │ 1-30s       │ 512MB-2GB │ ✅ Good          │
│ Quality Analysis   │ 2-60s       │ 1-3GB     │ ✅ Good          │
│ Spectrogram Gen    │ 5-120s      │ 1-2GB     │ ✅ Good          │
│ Format Conversion  │ 30s-10min   │ 2-4GB     │ ⚠️ With limits   │
│ Full Workflow      │ 2-15min     │ 3-6GB     │ ⚠️ Step Functions │
│ Batch (10+ files)  │ 10min-1hr   │ Variable  │ ❌ Use Batch/ECS  │
└────────────────────────────────────────────────────────────────┘
```

### 2.3 Migration Readiness Score

**Overall: 35% Ready** - Moderate refactoring required

| Area | Readiness | Effort |
|------|-----------|--------|
| Core Logic | 70% | Low - Well modularized |
| State Management | 10% | High - Needs DynamoDB integration |
| File I/O | 20% | High - Needs S3 streaming |
| API Layer | 0% | High - Needs complete implementation |
| Monitoring | 20% | Medium - Has logging, needs CloudWatch |

---

## 3. Architecture Overview

### 3.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     CLIENTS                                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   │
│   │   Web   │   │ Mobile  │   │ Desktop │   │   API   │   │   MCP   │   │   CLI   │   │
│   │  (SPA)  │   │  (iOS/  │   │(Electron│   │ (REST/  │   │  (LLM)  │   │(Local)  │   │
│   │         │   │ Android)│   │  /Tauri)│   │ GraphQL)│   │         │   │         │   │
│   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   │
│        │             │             │             │             │             │          │
└────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────┘
         │             │             │             │             │             │
         └─────────────┴─────────────┴──────┬──────┴─────────────┴─────────────┘
                                            │
┌───────────────────────────────────────────┴──────────────────────────────────────────────┐
│                                    EDGE LAYER                                             │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ┌────────────────────────────────────────────────────────────────────────────────┐    │
│   │                            AMAZON CLOUDFRONT                                    │    │
│   │                    (Global CDN + WAF + Edge Functions)                         │    │
│   │  • Static assets caching          • DDoS protection                            │    │
│   │  • API response caching           • Geographic routing                         │    │
│   │  • SSL termination                • Request/Response transformation            │    │
│   └────────────────────────────────────────────────────────────────────────────────┘    │
│                                            │                                             │
└────────────────────────────────────────────┼─────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┴─────────────────────────────────────────────┐
│                                    API LAYER                                              │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ┌─────────────────────────────────┐     ┌─────────────────────────────────┐           │
│   │       API GATEWAY (REST)        │     │     API GATEWAY (WebSocket)     │           │
│   │  ┌─────────────────────────┐    │     │  ┌─────────────────────────┐    │           │
│   │  │ /v1/audio/split         │    │     │  │ wss://api.../progress   │    │           │
│   │  │ /v1/audio/convert       │    │     │  │ Real-time job updates   │    │           │
│   │  │ /v1/audio/analyze       │    │     │  │ Processing progress     │    │           │
│   │  │ /v1/audio/metadata      │    │     │  │ Live notifications      │    │           │
│   │  │ /v1/workflows/*         │    │     │  └─────────────────────────┘    │           │
│   │  │ /v1/batch/*             │    │     └─────────────────────────────────┘           │
│   │  │ /v1/mcp/*  (LLM)        │    │                                                   │
│   │  └─────────────────────────┘    │     ┌─────────────────────────────────┐           │
│   │                                 │     │        AWS APPSYNC              │           │
│   │  Rate Limiting:                 │     │      (GraphQL - Optional)       │           │
│   │  • Free: 100 req/day            │     │  • Real-time subscriptions      │           │
│   │  • Pro: 10,000 req/day          │     │  • Complex queries              │           │
│   │  • Enterprise: Unlimited        │     │  • Offline sync                 │           │
│   └─────────────────────────────────┘     └─────────────────────────────────┘           │
│                                                                                           │
└────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┴─────────────────────────────────────────────┐
│                               AUTHENTICATION LAYER                                        │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │                              AMAZON COGNITO                                      │   │
│   │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐               │   │
│   │  │   User Pools     │  │  Identity Pools  │  │    API Keys      │               │   │
│   │  │  • Email/Pass    │  │  • Federated ID  │  │  • Rate limited  │               │   │
│   │  │  • Social Login  │  │  • Temp AWS creds│  │  • Usage plans   │               │   │
│   │  │  • MFA support   │  │  • Fine-grained  │  │  • Tier-based    │               │   │
│   │  │  • JWT tokens    │  │    permissions   │  │  • MCP access    │               │   │
│   │  └──────────────────┘  └──────────────────┘  └──────────────────┘               │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                           │
└────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┴─────────────────────────────────────────────┐
│                              COMPUTE LAYER                                                │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│   │                           AWS LAMBDA FUNCTIONS                                     │ │
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  │ │
│   │  │  api-handler   │  │ audio-splitter │  │audio-converter │  │quality-analyzer│  │ │
│   │  │  ───────────── │  │  ────────────  │  │  ────────────  │  │  ────────────  │  │ │
│   │  │  128MB-512MB   │  │  1GB-3GB       │  │  2GB-6GB       │  │  1GB-3GB       │  │ │
│   │  │  < 30s         │  │  < 5min        │  │  < 15min       │  │  < 5min        │  │ │
│   │  │  ARM64 (cost)  │  │  ARM64         │  │  x86_64+FFmpeg │  │  ARM64         │  │ │
│   │  └────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘  │ │
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  │ │
│   │  │metadata-editor │  │spectrogram-gen │  │ job-scheduler  │  │ notification   │  │ │
│   │  │  ────────────  │  │  ────────────  │  │  ────────────  │  │  ────────────  │  │ │
│   │  │  256MB-512MB   │  │  1GB-2GB       │  │  256MB         │  │  128MB         │  │ │
│   │  │  < 30s         │  │  < 3min        │  │  < 10s         │  │  < 5s          │  │ │
│   │  │  ARM64         │  │  ARM64         │  │  ARM64         │  │  ARM64         │  │ │
│   │  └────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘  │ │
│   └───────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                           │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│   │                          AWS STEP FUNCTIONS                                        │ │
│   │  ┌─────────────────────────────────────────────────────────────────────────────┐  │ │
│   │  │                     WORKFLOW ORCHESTRATION                                   │  │ │
│   │  │                                                                              │  │ │
│   │  │   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │  │ │
│   │  │   │ Validate │───▶│ Convert  │───▶│ Analyze  │───▶│ Notify   │             │  │ │
│   │  │   │  Input   │    │  Audio   │    │ Quality  │    │  User    │             │  │ │
│   │  │   └──────────┘    └──────────┘    └──────────┘    └──────────┘             │  │ │
│   │  │                                                                              │  │ │
│   │  │   Workflows: Podcast, Music Mastering, Audiobook, Custom                    │  │ │
│   │  └─────────────────────────────────────────────────────────────────────────────┘  │ │
│   └───────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                           │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│   │                    AWS BATCH + FARGATE (Heavy Processing)                          │ │
│   │  ┌─────────────────────────────────────────────────────────────────────────────┐  │ │
│   │  │  For files > 500MB or processing > 15 minutes                               │  │ │
│   │  │  • Spot Instances for cost optimization (70% savings)                       │  │ │
│   │  │  • Automatic scaling based on queue depth                                   │  │ │
│   │  │  • Docker containers with full FFmpeg + librosa                             │  │ │
│   │  └─────────────────────────────────────────────────────────────────────────────┘  │ │
│   └───────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                           │
└────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┴─────────────────────────────────────────────┐
│                              MESSAGING LAYER                                              │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐             │
│   │     AMAZON SQS      │  │     AMAZON SNS      │  │  AMAZON EVENTBRIDGE │             │
│   │  ───────────────    │  │  ───────────────    │  │  ─────────────────  │             │
│   │  Job Queues:        │  │  Topics:            │  │  Events:            │             │
│   │  • audio-jobs       │  │  • job-completed    │  │  • job.started      │             │
│   │  • batch-jobs       │  │  • job-failed       │  │  • job.completed    │             │
│   │  • priority-jobs    │  │  • user-notify      │  │  • job.failed       │             │
│   │                     │  │                     │  │  • quota.exceeded   │             │
│   │  Dead Letter:       │  │  Subscriptions:     │  │                     │             │
│   │  • dlq-audio-jobs   │  │  • Email            │  │  Rules:             │             │
│   │                     │  │  • SMS              │  │  • Trigger webhooks │             │
│   │  FIFO for order     │  │  • Webhooks         │  │  • Update analytics │             │
│   └─────────────────────┘  └─────────────────────┘  └─────────────────────┘             │
│                                                                                           │
└────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────┴─────────────────────────────────────────────┐
│                               STORAGE LAYER                                               │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐      │
│   │           AMAZON S3                 │  │         AMAZON DYNAMODB             │      │
│   │  ─────────────────────────────────  │  │  ─────────────────────────────────  │      │
│   │  Buckets:                           │  │  Tables:                            │      │
│   │  ┌───────────────────────────────┐  │  │  ┌───────────────────────────────┐  │      │
│   │  │ audio-uploads-{env}           │  │  │  │ Users                         │  │      │
│   │  │ • Presigned URL uploads       │  │  │  │ PK: USER#{id}                 │  │      │
│   │  │ • Lifecycle: 7 days → delete  │  │  │  │ SK: PROFILE | SETTINGS        │  │      │
│   │  │ • Multipart for large files   │  │  │  └───────────────────────────────┘  │      │
│   │  └───────────────────────────────┘  │  │  ┌───────────────────────────────┐  │      │
│   │  ┌───────────────────────────────┐  │  │  │ Jobs                          │  │      │
│   │  │ audio-processed-{env}         │  │  │  │ PK: JOB#{id}                  │  │      │
│   │  │ • Presigned URL downloads     │  │  │  │ SK: STATUS | STEP#{n}         │  │      │
│   │  │ • Lifecycle: 30d → IA → 90d → │  │  │  │ GSI: user-jobs-index          │  │      │
│   │  │   Glacier → 365d delete       │  │  │  │ GSI: status-created-index     │  │      │
│   │  └───────────────────────────────┘  │  │  └───────────────────────────────┘  │      │
│   │  ┌───────────────────────────────┐  │  │  ┌───────────────────────────────┐  │      │
│   │  │ audio-temp-{env}              │  │  │  │ ApiKeys                       │  │      │
│   │  │ • Intermediate processing     │  │  │  │ PK: KEY#{hash}                │  │      │
│   │  │ • Lifecycle: 24 hours delete  │  │  │  │ TTL for expiration            │  │      │
│   │  └───────────────────────────────┘  │  │  └───────────────────────────────┘  │      │
│   │                                     │  │                                     │      │
│   │  Encryption: SSE-S3 (default)       │  │  Billing: On-Demand (start)         │      │
│   │  Versioning: Disabled (cost)        │  │  → Provisioned at scale             │      │
│   │  Replication: Optional DR           │  │  Global Tables: Optional for DR     │      │
│   └─────────────────────────────────────┘  └─────────────────────────────────────┘      │
│                                                                                           │
│   ┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐      │
│   │       AMAZON ELASTICACHE            │  │         AMAZON EFS                  │      │
│   │  ─────────────────────────────────  │  │  ─────────────────────────────────  │      │
│   │  Redis (Optional - at scale):       │  │  (Optional - for Lambda layers):   │      │
│   │  • Session caching                  │  │  • Shared FFmpeg binaries           │      │
│   │  • Rate limiting counters           │  │  • Large model files                │      │
│   │  • Job progress cache               │  │  • Persistent /tmp extension        │      │
│   │  • API response cache               │  │                                     │      │
│   │                                     │  │  Use only if Lambda layers          │      │
│   │  Start: Serverless Redis            │  │  insufficient (250MB limit)         │      │
│   │  Scale: r6g.large cluster           │  │                                     │      │
│   └─────────────────────────────────────┘  └─────────────────────────────────────┘      │
│                                                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Request Flow Overview

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                            TYPICAL REQUEST FLOW                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘

1. FILE UPLOAD (Async Pattern)
   ┌────────┐     ┌────────────┐     ┌─────────┐     ┌─────────┐
   │ Client │────▶│ API Gateway│────▶│ Lambda  │────▶│   S3    │
   │        │     │            │     │(presign)│     │(upload) │
   └────────┘     └────────────┘     └─────────┘     └────┬────┘
                                                          │
                  ┌─────────────────────────────────────────┘
                  ▼
   ┌─────────────────┐     ┌─────────────┐     ┌─────────────┐
   │  S3 Event       │────▶│    SQS      │────▶│   Lambda    │
   │  Notification   │     │ (job queue) │     │ (processor) │
   └─────────────────┘     └─────────────┘     └─────────────┘

2. PROCESSING
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │   Lambda    │────▶│  DynamoDB   │────▶│  WebSocket  │
   │ (processor) │     │(job status) │     │ (progress)  │
   └──────┬──────┘     └─────────────┘     └─────────────┘
          │
          ▼
   ┌─────────────┐     ┌─────────────┐
   │     S3      │────▶│    SNS      │────▶ Notifications
   │  (output)   │     │  (notify)   │
   └─────────────┘     └─────────────┘

3. RESULT RETRIEVAL
   ┌────────┐     ┌────────────┐     ┌─────────┐     ┌─────────┐
   │ Client │────▶│ API Gateway│────▶│ Lambda  │────▶│   S3    │
   │        │     │            │     │(presign)│     │(download│
   └────────┘     └────────────┘     └─────────┘     └─────────┘
```

---

## 4. Detailed Component Design

### 4.1 Lambda Function Specifications

#### 4.1.1 API Handler Function

```yaml
Function: audio-splitter-api
Runtime: python3.12
Architecture: arm64
Memory: 256-512 MB
Timeout: 30 seconds
Concurrency: 1000 (reserved)

Purpose:
  - Handle all REST API requests
  - Generate presigned URLs for S3
  - CRUD operations on DynamoDB
  - Trigger async processing

Triggers:
  - API Gateway (REST)
  - API Gateway (WebSocket)

Environment:
  JOBS_TABLE: audio-jobs-{stage}
  UPLOAD_BUCKET: audio-uploads-{stage}
  PROCESSED_BUCKET: audio-processed-{stage}
  JOB_QUEUE_URL: https://sqs.../audio-jobs-{stage}
```

#### 4.1.2 Audio Processing Functions

```yaml
# Audio Splitter
Function: audio-splitter-split
Runtime: python3.12 (container)
Architecture: arm64
Memory: 1024-3072 MB
Timeout: 300 seconds (5 min)
Concurrency: 100

Container Image:
  Base: public.ecr.aws/lambda/python:3.12
  Size: ~450 MB
  Includes: librosa, soundfile, numpy, scipy

# Audio Converter
Function: audio-splitter-convert
Runtime: python3.12 (container)
Architecture: x86_64 (FFmpeg compatibility)
Memory: 2048-6144 MB
Timeout: 900 seconds (15 min)
Concurrency: 50

Container Image:
  Base: public.ecr.aws/lambda/python:3.12
  Size: ~600 MB
  Includes: FFmpeg, librosa, pydub

# Quality Analyzer
Function: audio-splitter-analyze
Runtime: python3.12 (container)
Architecture: arm64
Memory: 1024-3072 MB
Timeout: 300 seconds

Container Image:
  Includes: scipy (FFT), numpy, custom analyzers
```

### 4.2 Step Functions Workflow Definition

```yaml
# Podcast Production Workflow
StateMachine: PodcastProductionWorkflow

Definition:
  StartAt: ValidateInput
  States:
    ValidateInput:
      Type: Task
      Resource: arn:aws:lambda:...:audio-validator
      Next: ConvertToMP3
      Catch:
        - ErrorEquals: [ValidationError]
          Next: NotifyFailure

    ConvertToMP3:
      Type: Task
      Resource: arn:aws:lambda:...:audio-converter
      Parameters:
        format: mp3
        quality: 192k
        input.$: $.inputFile
      Next: AnalyzeQuality
      Retry:
        - ErrorEquals: [Lambda.ServiceException]
          IntervalSeconds: 2
          MaxAttempts: 3
          BackoffRate: 2

    AnalyzeQuality:
      Type: Task
      Resource: arn:aws:lambda:...:audio-analyzer
      Next: AddMetadata

    AddMetadata:
      Type: Task
      Resource: arn:aws:lambda:...:metadata-editor
      Next: GenerateSpectrogram

    GenerateSpectrogram:
      Type: Choice
      Choices:
        - Variable: $.generateVisual
          BooleanEquals: true
          Next: CreateSpectrogram
      Default: NotifySuccess

    CreateSpectrogram:
      Type: Task
      Resource: arn:aws:lambda:...:spectrogram-generator
      Next: NotifySuccess

    NotifySuccess:
      Type: Task
      Resource: arn:aws:lambda:...:notification-handler
      Parameters:
        status: completed
        userId.$: $.userId
        jobId.$: $.jobId
      End: true

    NotifyFailure:
      Type: Task
      Resource: arn:aws:lambda:...:notification-handler
      Parameters:
        status: failed
        error.$: $.error
      End: true
```

### 4.3 DynamoDB Table Design

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DYNAMODB TABLE: Jobs                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Table Name: audio-splitter-jobs-{env}                                              │
│  Billing: On-Demand (→ Provisioned at scale)                                        │
│                                                                                      │
│  ┌─────────────────┬────────────────────────────────────────────────────────────┐   │
│  │ Partition Key   │ PK (String) - "JOB#{jobId}" or "USER#{userId}"             │   │
│  │ Sort Key        │ SK (String) - "META" | "STEP#{stepNumber}" | "JOB#{jobId}" │   │
│  └─────────────────┴────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  Access Patterns:                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │ Pattern                      │ Key Condition                                │    │
│  ├─────────────────────────────────────────────────────────────────────────────┤    │
│  │ Get job by ID                │ PK = "JOB#{jobId}", SK = "META"              │    │
│  │ Get job steps                │ PK = "JOB#{jobId}", SK begins_with "STEP#"   │    │
│  │ Get user's jobs              │ PK = "USER#{userId}", SK begins_with "JOB#"  │    │
│  │ Get jobs by status           │ GSI: status-created-index                    │    │
│  │ Get recent jobs              │ GSI: created-at-index                        │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│  Global Secondary Indexes:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │ GSI Name              │ PK          │ SK              │ Projection         │    │
│  ├─────────────────────────────────────────────────────────────────────────────┤    │
│  │ status-created-index  │ status      │ createdAt       │ KEYS_ONLY          │    │
│  │ user-jobs-index       │ userId      │ createdAt       │ ALL                │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│  Item Examples:                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │ Job Metadata:                                                               │    │
│  │ {                                                                           │    │
│  │   "PK": "JOB#abc123",                                                       │    │
│  │   "SK": "META",                                                             │    │
│  │   "userId": "user-456",                                                     │    │
│  │   "status": "processing",                                                   │    │
│  │   "type": "podcast_workflow",                                               │    │
│  │   "inputFile": "s3://bucket/uploads/episode.wav",                           │    │
│  │   "outputFiles": [],                                                        │    │
│  │   "progress": 45,                                                           │    │
│  │   "createdAt": "2025-12-27T10:00:00Z",                                      │    │
│  │   "updatedAt": "2025-12-27T10:05:00Z",                                      │    │
│  │   "ttl": 1735689600                                                         │    │
│  │ }                                                                           │    │
│  │                                                                             │    │
│  │ Job Step:                                                                   │    │
│  │ {                                                                           │    │
│  │   "PK": "JOB#abc123",                                                       │    │
│  │   "SK": "STEP#001",                                                         │    │
│  │   "name": "ConvertToMP3",                                                   │    │
│  │   "status": "completed",                                                    │    │
│  │   "duration": 45.2,                                                         │    │
│  │   "output": { ... }                                                         │    │
│  │ }                                                                           │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. API Design

### 5.1 RESTful API Specification

```yaml
openapi: 3.0.3
info:
  title: Audio Splitter Suite API
  version: 1.0.0
  description: Professional audio processing as a service

servers:
  - url: https://api.audiosplitter.io/v1
    description: Production
  - url: https://api-staging.audiosplitter.io/v1
    description: Staging

security:
  - bearerAuth: []
  - apiKeyAuth: []

paths:
  # ============ UPLOAD & FILES ============
  /upload/presign:
    post:
      summary: Get presigned URL for file upload
      tags: [Files]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                filename:
                  type: string
                  example: "episode.wav"
                contentType:
                  type: string
                  example: "audio/wav"
                size:
                  type: integer
                  description: File size in bytes
      responses:
        200:
          description: Presigned upload URL
          content:
            application/json:
              schema:
                type: object
                properties:
                  uploadUrl:
                    type: string
                  fileId:
                    type: string
                  expiresAt:
                    type: string
                    format: date-time

  # ============ AUDIO OPERATIONS ============
  /audio/split:
    post:
      summary: Split audio file into segments
      tags: [Audio Processing]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SplitRequest'
      responses:
        202:
          description: Job accepted
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JobResponse'

  /audio/convert:
    post:
      summary: Convert audio format
      tags: [Audio Processing]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ConvertRequest'
      responses:
        202:
          $ref: '#/components/responses/JobAccepted'

  /audio/analyze:
    post:
      summary: Analyze audio quality
      tags: [Audio Processing]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AnalyzeRequest'
      responses:
        202:
          $ref: '#/components/responses/JobAccepted'

  /audio/metadata:
    post:
      summary: Read or update audio metadata
      tags: [Metadata]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MetadataRequest'
      responses:
        200:
          description: Metadata updated

  # ============ WORKFLOWS ============
  /workflows/podcast:
    post:
      summary: Execute podcast production workflow
      tags: [Workflows]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PodcastWorkflowRequest'
      responses:
        202:
          $ref: '#/components/responses/JobAccepted'

  /workflows/music-mastering:
    post:
      summary: Execute music mastering workflow
      tags: [Workflows]

  /workflows/audiobook:
    post:
      summary: Execute audiobook production workflow
      tags: [Workflows]

  # ============ JOBS ============
  /jobs:
    get:
      summary: List user's jobs
      tags: [Jobs]
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [pending, processing, completed, failed]
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: cursor
          in: query
          schema:
            type: string
      responses:
        200:
          description: List of jobs
          content:
            application/json:
              schema:
                type: object
                properties:
                  jobs:
                    type: array
                    items:
                      $ref: '#/components/schemas/Job'
                  nextCursor:
                    type: string

  /jobs/{jobId}:
    get:
      summary: Get job details
      tags: [Jobs]
      parameters:
        - name: jobId
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Job details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Job'

  /jobs/{jobId}/download:
    get:
      summary: Get presigned download URLs for job outputs
      tags: [Jobs]
      responses:
        200:
          description: Download URLs
          content:
            application/json:
              schema:
                type: object
                properties:
                  files:
                    type: array
                    items:
                      type: object
                      properties:
                        filename:
                          type: string
                        url:
                          type: string
                        expiresAt:
                          type: string

  # ============ MCP (Model Context Protocol) ============
  /mcp/tools:
    get:
      summary: List available MCP tools
      tags: [MCP]
      description: For LLM integration
      responses:
        200:
          description: Available tools

  /mcp/execute:
    post:
      summary: Execute MCP tool
      tags: [MCP]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                tool:
                  type: string
                  enum: [split, convert, analyze, metadata]
                arguments:
                  type: object

components:
  schemas:
    SplitRequest:
      type: object
      required: [fileId, segments]
      properties:
        fileId:
          type: string
        segments:
          type: array
          items:
            type: object
            properties:
              start:
                type: string
                example: "0:00"
              end:
                type: string
                example: "1:30"
              name:
                type: string
                example: "intro"
        options:
          type: object
          properties:
            enhanced:
              type: boolean
              default: true
            crossFade:
              type: boolean
              default: true
            qualityValidation:
              type: boolean
              default: false

    ConvertRequest:
      type: object
      required: [fileId, format]
      properties:
        fileId:
          type: string
        format:
          type: string
          enum: [mp3, flac, wav, m4a, ogg]
        quality:
          type: string
          enum: [low, medium, high, vbr_low, vbr_medium, vbr_high]
          default: high
        preserveMetadata:
          type: boolean
          default: true

    Job:
      type: object
      properties:
        id:
          type: string
        status:
          type: string
          enum: [pending, processing, completed, failed]
        type:
          type: string
        progress:
          type: integer
          minimum: 0
          maximum: 100
        steps:
          type: array
          items:
            $ref: '#/components/schemas/JobStep'
        inputFile:
          type: string
        outputFiles:
          type: array
          items:
            type: string
        qualityMetrics:
          $ref: '#/components/schemas/QualityMetrics'
        createdAt:
          type: string
          format: date-time
        completedAt:
          type: string
          format: date-time
        error:
          type: string

    QualityMetrics:
      type: object
      properties:
        level:
          type: string
          enum: [EXCELLENT, GOOD, ACCEPTABLE, POOR, FAILED]
        thdPlusN:
          type: number
          description: THD+N in dB
        snr:
          type: number
          description: SNR in dB
        dynamicRange:
          type: number
          description: Dynamic range percentage
        clippingDetected:
          type: boolean

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    apiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

  responses:
    JobAccepted:
      description: Job accepted for processing
      content:
        application/json:
          schema:
            type: object
            properties:
              jobId:
                type: string
              status:
                type: string
                default: pending
              estimatedDuration:
                type: integer
                description: Estimated processing time in seconds
```

### 5.2 WebSocket API for Real-Time Updates

```yaml
# WebSocket API Specification
WebSocket: wss://ws.audiosplitter.io

Routes:
  $connect:
    - Validate JWT/API key
    - Store connectionId in DynamoDB
    - Associate with userId

  $disconnect:
    - Remove connectionId from DynamoDB

  subscribe:
    Request:
      action: subscribe
      jobId: string
    Response:
      subscribed: true
      jobId: string

  unsubscribe:
    Request:
      action: unsubscribe
      jobId: string

Server Push Messages:
  jobProgress:
    type: progress
    jobId: string
    progress: number (0-100)
    currentStep: string
    message: string

  jobCompleted:
    type: completed
    jobId: string
    outputFiles:
      - filename: string
        url: string
    qualityMetrics: object

  jobFailed:
    type: failed
    jobId: string
    error: string
    step: string
```

### 5.3 Rate Limiting Tiers

```yaml
Rate Limits:
  Free Tier:
    requests_per_day: 100
    max_file_size_mb: 100
    max_concurrent_jobs: 2
    max_file_duration_min: 30
    workflows: [basic_split, basic_convert]
    retention_days: 7

  Pro Tier:
    requests_per_day: 10000
    max_file_size_mb: 500
    max_concurrent_jobs: 10
    max_file_duration_min: 180
    workflows: [all]
    retention_days: 30
    priority_queue: true

  Enterprise Tier:
    requests_per_day: unlimited
    max_file_size_mb: 2048
    max_concurrent_jobs: 100
    max_file_duration_min: 720
    workflows: [all]
    retention_days: 90
    priority_queue: true
    dedicated_capacity: optional
    sla: 99.9%

  MCP/API Tier:
    requests_per_minute: 60
    max_file_size_mb: 100
    special_endpoints: [/mcp/*]
    response_format: llm_optimized
```

---

## 6. Data Flow & Processing

### 6.1 File Upload Flow

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FILE UPLOAD SEQUENCE                                      │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────────┐
│  Client  │     │  API Gateway  │     │    Lambda    │     │   DynamoDB   │
│          │     │               │     │  (presign)   │     │              │
└────┬─────┘     └───────┬───────┘     └──────┬───────┘     └──────┬───────┘
     │                   │                    │                    │
     │  1. POST /upload/presign              │                    │
     │  {filename, size, type}               │                    │
     │──────────────────▶│                    │                    │
     │                   │                    │                    │
     │                   │  2. Invoke Lambda  │                    │
     │                   │───────────────────▶│                    │
     │                   │                    │                    │
     │                   │                    │  3. Create job record
     │                   │                    │───────────────────▶│
     │                   │                    │                    │
     │                   │                    │  4. Generate presigned URL
     │                   │                    │    (s3.createPresignedPost)
     │                   │                    │                    │
     │                   │  5. Return URLs    │                    │
     │                   │◀───────────────────│                    │
     │                   │                    │                    │
     │  6. {uploadUrl, fileId}               │                    │
     │◀──────────────────│                    │                    │
     │                   │                    │                    │
     │                   │                    │                    │
     │                   │                    │                    │
┌────┴─────┐     ┌───────┴───────┐     ┌──────┴───────┐     ┌──────┴───────┐
│  Client  │     │      S3       │     │     SQS      │     │    Lambda    │
│          │     │   (upload)    │     │  (job queue) │     │  (processor) │
└────┬─────┘     └───────┬───────┘     └──────┬───────┘     └──────┬───────┘
     │                   │                    │                    │
     │  7. PUT (multipart upload)            │                    │
     │──────────────────▶│                    │                    │
     │                   │                    │                    │
     │  8. Upload complete                   │                    │
     │◀──────────────────│                    │                    │
     │                   │                    │                    │
     │                   │  9. S3 Event       │                    │
     │                   │───────────────────▶│                    │
     │                   │                    │                    │
     │                   │                    │  10. Trigger       │
     │                   │                    │─────────────────  │
     │                   │                    │                    │
     │                   │                    │  11. Begin processing
     │                   │                    │                    │
     └───────────────────┴────────────────────┴────────────────────┘
```

### 6.2 Processing Pipeline Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AUDIO PROCESSING PIPELINE                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐
│  S3 Event   │
│  (upload)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              JOB ROUTER LAMBDA                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │  1. Parse S3 event                                                             │ │
│  │  2. Get job config from DynamoDB                                               │ │
│  │  3. Determine processing path based on:                                        │ │
│  │     - File size (< 500MB → Lambda, > 500MB → Batch)                           │ │
│  │     - Operation type (simple → Lambda, workflow → Step Functions)              │ │
│  │     - User tier (priority queue for Pro/Enterprise)                            │ │
│  │  4. Route to appropriate processor                                             │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
       │
       ├──────────────────────────────────────┬─────────────────────────────────┐
       │                                      │                                 │
       ▼                                      ▼                                 ▼
┌─────────────────┐                  ┌─────────────────┐               ┌─────────────────┐
│  LAMBDA PATH    │                  │ STEP FUNCTIONS  │               │   BATCH PATH    │
│  (Simple Ops)   │                  │    (Workflows)  │               │  (Heavy Ops)    │
├─────────────────┤                  ├─────────────────┤               ├─────────────────┤
│ • Split         │                  │ • Podcast       │               │ • Files > 500MB │
│ • Metadata      │                  │ • Music Master  │               │ • Batch convert │
│ • Quick convert │                  │ • Audiobook     │               │ • Long analysis │
│ • Spectrogram   │                  │ • Custom        │               │                 │
│                 │                  │                 │               │                 │
│ Timeout: 15min  │                  │ Timeout: 1 hour │               │ Timeout: 4 hours│
│ Memory: 3-6 GB  │                  │ Orchestrates    │               │ Spot Instances  │
│                 │                  │ multiple Lambda │               │                 │
└────────┬────────┘                  └────────┬────────┘               └────────┬────────┘
         │                                    │                                 │
         │                                    │                                 │
         ▼                                    ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              RESULT HANDLER                                          │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │  1. Upload output files to S3                                                  │ │
│  │  2. Update job status in DynamoDB                                              │ │
│  │  3. Generate presigned download URLs                                           │ │
│  │  4. Send WebSocket notification                                                │ │
│  │  5. Publish to SNS for external notifications                                  │ │
│  │  6. Emit EventBridge event for analytics                                       │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Step Functions Workflow Visualization

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     PODCAST PRODUCTION WORKFLOW (Step Functions)                        │
└────────────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │     START       │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ Download from S3│
                              │   to /tmp       │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ Validate Input  │
                              │  (format, size) │
                              └────────┬────────┘
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                          ▼                         ▼
                   ┌─────────────┐          ┌─────────────┐
                   │   VALID     │          │  INVALID    │
                   └──────┬──────┘          └──────┬──────┘
                          │                        │
                          │                        ▼
                          │               ┌─────────────────┐
                          │               │  Notify Error   │
                          │               │    → END        │
                          │               └─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Pre-Master      │
                 │ Quality Check   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Convert to MP3  │
                 │  (192kbps)      │◄─────── Retry x3
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Apply Metadata  │
                 │ (title, artist) │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Generate Visual?│
                 └────────┬────────┘
                          │
              ┌───────────┴───────────┐
              │ Yes                   │ No
              ▼                       │
     ┌─────────────────┐              │
     │ Mel Spectrogram │              │
     └────────┬────────┘              │
              │                       │
              └───────────┬───────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Post-Master     │
                 │ Quality Check   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Upload to S3    │
                 │ (processed)     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Update DynamoDB │
                 │ (completed)     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Send WebSocket  │
                 │ Notification    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │      END        │
                 └─────────────────┘
```

---

## 7. Multi-Frontend Support

### 7.1 Frontend Architecture Matrix

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           MULTI-FRONTEND ARCHITECTURE                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬─────────────────────────────────────────────────────────────────────────┐
│   Frontend   │                          Implementation                                  │
├──────────────┼─────────────────────────────────────────────────────────────────────────┤
│              │                                                                          │
│    WEB       │  ┌─────────────────────────────────────────────────────────────────┐    │
│   (SPA)      │  │  Technology: React/Next.js + TypeScript                         │    │
│              │  │  Hosting: S3 + CloudFront                                        │    │
│              │  │  Features:                                                       │    │
│              │  │  • Direct S3 upload with presigned URLs                         │    │
│              │  │  • WebSocket for real-time progress                             │    │
│              │  │  • Responsive design (mobile-first)                             │    │
│              │  │  • PWA support for offline capability                           │    │
│              │  │  Auth: Cognito Hosted UI + Amplify                              │    │
│              │  └─────────────────────────────────────────────────────────────────┘    │
│              │                                                                          │
├──────────────┼─────────────────────────────────────────────────────────────────────────┤
│              │                                                                          │
│   MOBILE     │  ┌─────────────────────────────────────────────────────────────────┐    │
│  (iOS/And)   │  │  Technology: React Native / Flutter                             │    │
│              │  │  Features:                                                       │    │
│              │  │  • Background upload support                                    │    │
│              │  │  • Push notifications via SNS                                   │    │
│              │  │  • Offline queue for jobs                                       │    │
│              │  │  • Native audio playback                                        │    │
│              │  │  Auth: Cognito + Biometric                                      │    │
│              │  │  SDK: AWS Amplify Mobile                                        │    │
│              │  └─────────────────────────────────────────────────────────────────┘    │
│              │                                                                          │
├──────────────┼─────────────────────────────────────────────────────────────────────────┤
│              │                                                                          │
│   DESKTOP    │  ┌─────────────────────────────────────────────────────────────────┐    │
│  (Electron   │  │  Technology: Electron or Tauri (Rust)                           │    │
│   /Tauri)    │  │  Features:                                                       │    │
│              │  │  • Local file system access                                     │    │
│              │  │  • Batch upload with resume                                     │    │
│              │  │  • System tray notifications                                    │    │
│              │  │  • Drag & drop support                                          │    │
│              │  │  • Offline processing (optional local mode)                     │    │
│              │  │  Auth: Secure token storage (keychain)                          │    │
│              │  └─────────────────────────────────────────────────────────────────┘    │
│              │                                                                          │
├──────────────┼─────────────────────────────────────────────────────────────────────────┤
│              │                                                                          │
│    API       │  ┌─────────────────────────────────────────────────────────────────┐    │
│  (Direct)    │  │  Access: REST API + API Key                                     │    │
│              │  │  Features:                                                       │    │
│              │  │  • SDKs: Python, JavaScript, Go, Rust                           │    │
│              │  │  • Webhooks for async notifications                             │    │
│              │  │  • Rate limiting per API key                                    │    │
│              │  │  • Batch operations endpoint                                    │    │
│              │  │  Auth: API Key (X-API-Key header)                               │    │
│              │  │  Docs: OpenAPI 3.0 + Swagger UI                                 │    │
│              │  └─────────────────────────────────────────────────────────────────┘    │
│              │                                                                          │
├──────────────┼─────────────────────────────────────────────────────────────────────────┤
│              │                                                                          │
│    MCP       │  ┌─────────────────────────────────────────────────────────────────┐    │
│   (LLM)      │  │  Protocol: Model Context Protocol (Anthropic)                   │    │
│              │  │  Features:                                                       │    │
│              │  │  • Tool definitions for Claude/ChatGPT                          │    │
│              │  │  • Streaming responses                                          │    │
│              │  │  • Context-aware prompts                                        │    │
│              │  │  • Auto-retry with exponential backoff                          │    │
│              │  │  Auth: MCP-specific API key                                     │    │
│              │  │  Response: Optimized for LLM context                            │    │
│              │  └─────────────────────────────────────────────────────────────────┘    │
│              │                                                                          │
├──────────────┼─────────────────────────────────────────────────────────────────────────┤
│              │                                                                          │
│    CLI       │  ┌─────────────────────────────────────────────────────────────────┐    │
│  (Terminal)  │  │  Access: REST API + CLI wrapper                                 │    │
│              │  │  Features:                                                       │    │
│              │  │  • Same commands as current CLI                                 │    │
│              │  │  • Progress bars and spinners                                   │    │
│              │  │  • Config file for credentials                                  │    │
│              │  │  • Hybrid mode: local or cloud                                  │    │
│              │  │  Auth: ~/.audiosplitter/credentials                             │    │
│              │  │  Distribution: pip install audio-splitter-cli                   │    │
│              │  └─────────────────────────────────────────────────────────────────┘    │
│              │                                                                          │
└──────────────┴─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 SDK Architecture

```python
# Python SDK Example
from audiosplitter import AudioSplitterClient

# Initialize client
client = AudioSplitterClient(
    api_key="ask_xxxxx",  # or use environment variable
    region="us-east-1"    # optional, for latency optimization
)

# Upload file (returns presigned URL, handles upload)
file_id = client.upload("episode.wav")

# Start processing
job = client.workflows.podcast(
    file_id=file_id,
    metadata={
        "title": "Episode 1",
        "artist": "My Podcast"
    },
    options={
        "quality": "professional",
        "generate_visual": True
    }
)

# Wait for completion (with progress callback)
result = job.wait(on_progress=lambda p: print(f"Progress: {p}%"))

# Download results
result.download_all("./output/")

# Or get presigned URLs
urls = result.get_download_urls()
```

### 7.3 MCP Tool Definitions

```json
{
  "tools": [
    {
      "name": "audio_split",
      "description": "Split an audio file into multiple segments with precision timing",
      "input_schema": {
        "type": "object",
        "required": ["file_url", "segments"],
        "properties": {
          "file_url": {
            "type": "string",
            "description": "URL or S3 path to the audio file"
          },
          "segments": {
            "type": "array",
            "description": "Array of segment definitions",
            "items": {
              "type": "object",
              "properties": {
                "start": {"type": "string", "description": "Start time (format: MM:SS or HH:MM:SS)"},
                "end": {"type": "string", "description": "End time"},
                "name": {"type": "string", "description": "Segment name for output file"}
              }
            }
          }
        }
      }
    },
    {
      "name": "audio_convert",
      "description": "Convert audio file to a different format with quality preservation",
      "input_schema": {
        "type": "object",
        "required": ["file_url", "target_format"],
        "properties": {
          "file_url": {"type": "string"},
          "target_format": {
            "type": "string",
            "enum": ["mp3", "flac", "wav", "m4a", "ogg"]
          },
          "quality": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "default": "high"
          }
        }
      }
    },
    {
      "name": "audio_analyze",
      "description": "Analyze audio quality with scientific metrics (THD+N, SNR)",
      "input_schema": {
        "type": "object",
        "required": ["file_url"],
        "properties": {
          "file_url": {"type": "string"},
          "metrics": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["thd_plus_n", "snr", "dynamic_range", "clipping", "all"]
            }
          }
        }
      }
    },
    {
      "name": "podcast_workflow",
      "description": "Complete podcast production: conversion, metadata, quality check",
      "input_schema": {
        "type": "object",
        "required": ["file_url"],
        "properties": {
          "file_url": {"type": "string"},
          "title": {"type": "string"},
          "artist": {"type": "string"},
          "mode": {
            "type": "string",
            "enum": ["quick", "standard", "professional"],
            "default": "standard"
          }
        }
      }
    }
  ]
}
```

---

## 8. Security Architecture

### 8.1 Security Layers

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY ARCHITECTURE                                      │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  EDGE SECURITY                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │ AWS WAF (Web Application Firewall)                                            │  │
│  │ • Rate limiting (per IP, per user)                                            │  │
│  │ • SQL injection protection                                                    │  │
│  │ • XSS protection                                                              │  │
│  │ • Geographic blocking (optional)                                              │  │
│  │ • Bot detection and mitigation                                                │  │
│  │ • Custom rules for API abuse                                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │ AWS Shield (DDoS Protection)                                                  │  │
│  │ • Standard: Automatic (free)                                                  │  │
│  │ • Advanced: For Enterprise tier (24/7 DDoS response)                          │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              AUTHENTICATION                                          │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │ Amazon Cognito                                                                │  │
│  │                                                                               │  │
│  │  User Pools:                      Identity Pools:                             │  │
│  │  ┌─────────────────────────┐     ┌─────────────────────────┐                 │  │
│  │  │ • Email/Password        │     │ • Federated identities  │                 │  │
│  │  │ • Social login          │     │ • Temporary AWS creds   │                 │  │
│  │  │   - Google              │     │ • S3 upload permissions │                 │  │
│  │  │   - Apple               │     │ • Per-user isolation    │                 │  │
│  │  │   - GitHub              │     │                         │                 │  │
│  │  │ • MFA (TOTP, SMS)       │     └─────────────────────────┘                 │  │
│  │  │ • Password policies     │                                                  │  │
│  │  │ • JWT tokens (1h exp)   │                                                  │  │
│  │  └─────────────────────────┘                                                  │  │
│  │                                                                               │  │
│  │  API Keys (for programmatic access):                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │ • Stored hashed in DynamoDB                                             │ │  │
│  │  │ • Associated with usage plan                                            │ │  │
│  │  │ • Revocable by user                                                     │ │  │
│  │  │ • Scoped permissions (read-only, full access)                           │ │  │
│  │  │ • Rate limiting enforcement                                             │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               AUTHORIZATION                                          │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │ IAM Policies (Least Privilege)                                                │  │
│  │                                                                               │  │
│  │  Lambda Execution Role:                                                       │  │
│  │  {                                                                            │  │
│  │    "Effect": "Allow",                                                         │  │
│  │    "Action": [                                                                │  │
│  │      "s3:GetObject",                                                          │  │
│  │      "s3:PutObject"                                                           │  │
│  │    ],                                                                         │  │
│  │    "Resource": "arn:aws:s3:::audio-*/${cognito-identity.amazonaws.com:sub}/*" │  │
│  │  }                                                                            │  │
│  │                                                                               │  │
│  │  User Upload Policy:                                                          │  │
│  │  • Can only upload to their own prefix (user-id/)                             │  │
│  │  • Can only read their own processed files                                    │  │
│  │  • Cannot list bucket contents                                                │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               DATA PROTECTION                                        │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │ Encryption                                                                    │  │
│  │                                                                               │  │
│  │  At Rest:                          In Transit:                                │  │
│  │  ┌─────────────────────────┐      ┌─────────────────────────┐                │  │
│  │  │ • S3: SSE-S3 (AES-256)  │      │ • TLS 1.3 (minimum 1.2) │                │  │
│  │  │ • DynamoDB: AWS managed │      │ • HTTPS only            │                │  │
│  │  │ • EBS: AES-256          │      │ • Certificate pinning   │                │  │
│  │  │ • CloudWatch Logs: SSE  │      │   (mobile apps)         │                │  │
│  │  └─────────────────────────┘      └─────────────────────────┘                │  │
│  │                                                                               │  │
│  │  Secrets Management:                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │ • AWS Secrets Manager for API keys, database credentials                │ │  │
│  │  │ • Automatic rotation (30-90 days)                                       │ │  │
│  │  │ • No secrets in code or environment variables                           │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Compliance Considerations

```yaml
Compliance Frameworks:
  SOC 2 Type II:
    - All AWS services used are SOC 2 compliant
    - Audit logging via CloudTrail
    - Access controls via IAM

  GDPR:
    - User data isolation by user ID
    - Data deletion API endpoint
    - 90-day automatic deletion for processed files
    - No data processing outside EU (optional regional deployment)

  HIPAA:
    - BAA available for Enterprise tier
    - Encryption at rest and in transit
    - Audit logging for all access
    - PHI handling requires dedicated deployment
```

---

## 9. Scalability Strategy

### 9.1 Scaling Dimensions

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              SCALABILITY MATRIX                                         │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┬──────────────────────────────────────────────────────────────────────┐
│   Component     │                    Scaling Characteristics                           │
├─────────────────┼──────────────────────────────────────────────────────────────────────┤
│                 │                                                                       │
│  API Gateway    │  • Auto-scales to 10,000 RPS per region (default)                   │
│                 │  • Increase via support request (100,000+ RPS)                       │
│                 │  • Throttling: 5,000 RPS burst, 10,000 steady                        │
│                 │  • Cost: $3.50 per million requests                                  │
│                 │                                                                       │
├─────────────────┼──────────────────────────────────────────────────────────────────────┤
│                 │                                                                       │
│  Lambda         │  • Default: 1,000 concurrent (per account/region)                   │
│                 │  • Request increase: 10,000+ concurrent                              │
│                 │  • Reserved concurrency for critical functions                       │
│                 │  • Provisioned concurrency to eliminate cold starts                  │
│                 │                                                                       │
│                 │  Scaling by function:                                                │
│                 │  ┌─────────────────────────────────────────────────────────────┐    │
│                 │  │ api-handler:       500 reserved, 50 provisioned            │    │
│                 │  │ audio-splitter:    200 reserved                             │    │
│                 │  │ audio-converter:   100 reserved (memory-heavy)              │    │
│                 │  │ quality-analyzer:  100 reserved                             │    │
│                 │  └─────────────────────────────────────────────────────────────┘    │
│                 │                                                                       │
├─────────────────┼──────────────────────────────────────────────────────────────────────┤
│                 │                                                                       │
│  DynamoDB       │  • On-Demand: Auto-scales to any traffic level                      │
│                 │  • Provisioned: Switch when traffic predictable (cost savings)      │
│                 │  • DAX (cache): Add at 10,000+ RPS for sub-ms latency               │
│                 │  • Global Tables: Multi-region for DR and latency                    │
│                 │                                                                       │
│                 │  Capacity planning:                                                  │
│                 │  ┌─────────────────────────────────────────────────────────────┐    │
│                 │  │ 0-10K users:     On-Demand ($1.25/million WCU)             │    │
│                 │  │ 10K-100K users:  Provisioned (~40% savings)                 │    │
│                 │  │ 100K+ users:     Provisioned + DAX                          │    │
│                 │  └─────────────────────────────────────────────────────────────┘    │
│                 │                                                                       │
├─────────────────┼──────────────────────────────────────────────────────────────────────┤
│                 │                                                                       │
│  S3             │  • Virtually unlimited (5 TB per object)                            │
│                 │  • 3,500 PUT/s, 5,500 GET/s per prefix                              │
│                 │  • Use random prefixes for high throughput                           │
│                 │  • Intelligent-Tiering for cost optimization                         │
│                 │                                                                       │
├─────────────────┼──────────────────────────────────────────────────────────────────────┤
│                 │                                                                       │
│  SQS            │  • Unlimited throughput (Standard queues)                           │
│                 │  • FIFO: 3,000 msg/s with batching                                  │
│                 │  • Auto-scales with no configuration                                 │
│                 │                                                                       │
├─────────────────┼──────────────────────────────────────────────────────────────────────┤
│                 │                                                                       │
│  Step Functions │  • 2,000 state transitions/s per account                            │
│                 │  • Express Workflows: 100,000/s (for short workflows)               │
│                 │  • Standard: Long-running, exactly-once                              │
│                 │                                                                       │
└─────────────────┴──────────────────────────────────────────────────────────────────────┘
```

### 9.2 Scaling Phases

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              SCALING PHASES                                             │
└────────────────────────────────────────────────────────────────────────────────────────┘

Phase 0: Launch (0 - 1K users)
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Infrastructure:                                                                      │
│ • Lambda: Default concurrency                                                        │
│ • DynamoDB: On-Demand                                                                │
│ • S3: Standard                                                                       │
│ • No caching layer                                                                   │
│                                                                                      │
│ Monthly Cost: $0 - $50                                                               │
│ Focus: Feature development, user feedback                                            │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
Phase 1: Growth (1K - 10K users)
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Changes:                                                                             │
│ • Lambda: Reserved concurrency (500)                                                 │
│ • Lambda: Provisioned concurrency for API (20)                                       │
│ • CloudFront: Enable caching                                                         │
│ • Monitoring: Full observability stack                                               │
│                                                                                      │
│ Monthly Cost: $50 - $500                                                             │
│ Focus: Performance optimization, reliability                                         │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
Phase 2: Scale (10K - 100K users)
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Changes:                                                                             │
│ • Lambda: Increase reserved (2000)                                                   │
│ • Lambda: Provisioned concurrency (100)                                              │
│ • DynamoDB: Switch to Provisioned capacity                                           │
│ • ElastiCache: Add Redis for rate limiting and caching                               │
│ • AWS Batch: For heavy processing (>15 min jobs)                                     │
│                                                                                      │
│ Monthly Cost: $500 - $5,000                                                          │
│ Focus: Cost optimization, global expansion                                           │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
Phase 3: Enterprise (100K - 1M+ users)
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Changes:                                                                             │
│ • Multi-region deployment                                                            │
│ • DynamoDB Global Tables                                                             │
│ • S3 Cross-Region Replication                                                        │
│ • Dedicated AWS Batch compute environment                                            │
│ • Custom Lambda limits (10,000+ concurrent)                                          │
│ • Enterprise support plan                                                            │
│                                                                                      │
│ Monthly Cost: $5,000 - $50,000+                                                      │
│ Focus: SLA guarantees, compliance, custom features                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Cost Optimization

### 10.1 Cost Model by Usage Tier

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MONTHLY COST BREAKDOWN BY TIER                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              ZERO USAGE (Idle)                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Service              │ Cost Reason                        │ Monthly Cost            │
├──────────────────────┼────────────────────────────────────┼─────────────────────────┤
│ Lambda               │ No invocations                     │ $0.00                   │
│ API Gateway          │ No requests                        │ $0.00                   │
│ DynamoDB (On-Demand) │ No reads/writes                    │ $0.00                   │
│ S3                   │ No storage                         │ $0.00                   │
│ CloudFront           │ No data transfer                   │ $0.00                   │
│ SQS                  │ No messages                        │ $0.00                   │
│ Step Functions       │ No executions                      │ $0.00                   │
├──────────────────────┼────────────────────────────────────┼─────────────────────────┤
│ TOTAL                │                                    │ $0.00/month             │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         STARTER (1,000 users, 10K jobs/month)                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Service              │ Usage                              │ Monthly Cost            │
├──────────────────────┼────────────────────────────────────┼─────────────────────────┤
│ Lambda               │ 10K invocations, 50K GB-seconds    │ ~$1.00                  │
│ API Gateway          │ 50K requests                       │ ~$0.18                  │
│ DynamoDB             │ 100K reads, 50K writes             │ ~$0.50                  │
│ S3                   │ 50 GB storage, 100 GB transfer     │ ~$3.50                  │
│ CloudFront           │ 100 GB transfer                    │ ~$8.50                  │
│ SQS                  │ 10K messages                       │ ~$0.01                  │
│ Step Functions       │ 5K state transitions               │ ~$0.13                  │
│ CloudWatch           │ Logs and metrics                   │ ~$5.00                  │
├──────────────────────┼────────────────────────────────────┼─────────────────────────┤
│ TOTAL                │                                    │ ~$20/month              │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        GROWTH (10,000 users, 100K jobs/month)                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Service              │ Usage                              │ Monthly Cost            │
├──────────────────────┼────────────────────────────────────┼─────────────────────────┤
│ Lambda               │ 100K invocations, 500K GB-sec      │ ~$10.00                 │
│ Lambda (Provisioned) │ 20 concurrent × 720 hours          │ ~$50.00                 │
│ API Gateway          │ 500K requests                      │ ~$1.75                  │
│ DynamoDB             │ 1M reads, 500K writes              │ ~$5.00                  │
│ S3                   │ 500 GB storage, 1 TB transfer      │ ~$35.00                 │
│ CloudFront           │ 1 TB transfer                      │ ~$85.00                 │
│ SQS                  │ 100K messages                      │ ~$0.10                  │
│ Step Functions       │ 50K state transitions              │ ~$1.25                  │
│ ElastiCache          │ cache.t3.micro (optional)          │ ~$15.00                 │
│ CloudWatch           │ Enhanced monitoring                │ ~$20.00                 │
├──────────────────────┼────────────────────────────────────┼─────────────────────────┤
│ TOTAL                │                                    │ ~$225/month             │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      SCALE (100,000 users, 1M jobs/month)                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Service              │ Usage                              │ Monthly Cost            │
├──────────────────────┼────────────────────────────────────┼─────────────────────────┤
│ Lambda               │ 1M invocations, 5M GB-seconds      │ ~$85.00                 │
│ Lambda (Provisioned) │ 100 concurrent × 720 hours         │ ~$250.00                │
│ API Gateway          │ 5M requests                        │ ~$17.50                 │
│ DynamoDB             │ 10M reads, 5M writes (provisioned) │ ~$65.00                 │
│ S3                   │ 5 TB storage, 10 TB transfer       │ ~$350.00                │
│ CloudFront           │ 10 TB transfer                     │ ~$850.00                │
│ SQS                  │ 1M messages                        │ ~$0.40                  │
│ Step Functions       │ 500K state transitions             │ ~$12.50                 │
│ AWS Batch            │ Spot instances for heavy jobs      │ ~$200.00                │
│ ElastiCache          │ r6g.large cluster                  │ ~$200.00                │
│ CloudWatch           │ Full observability                 │ ~$100.00                │
├──────────────────────┼────────────────────────────────────┼─────────────────────────┤
│ TOTAL                │                                    │ ~$2,150/month           │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Cost Optimization Strategies

```yaml
Cost Optimization Techniques:

1. Lambda Optimization:
   - Use ARM64 (Graviton2): 20% cheaper, same performance
   - Right-size memory: Profile and optimize
   - Use provisioned concurrency only during peak hours
   - Batch small operations to reduce invocations

2. S3 Optimization:
   - Lifecycle policies:
     - uploads → delete after 7 days
     - processed → Intelligent-Tiering after 30 days
     - Archive to Glacier after 90 days
   - Use S3 Select for metadata queries (avoid full file reads)
   - Compress outputs (FLAC > WAV)

3. DynamoDB Optimization:
   - Start with On-Demand (zero cost at zero usage)
   - Switch to Provisioned when >$100/month
   - Use TTL for automatic deletion
   - Sparse indexes (only index needed attributes)

4. Data Transfer Optimization:
   - CloudFront caching (reduce origin requests)
   - Same-region S3 to Lambda (free)
   - Use VPC endpoints for S3 access (no NAT costs)
   - Compress API responses (gzip)

5. Batch Processing Optimization:
   - Use Spot Instances (70% savings)
   - Schedule non-urgent jobs during off-peak
   - Batch small files together
   - Use step concurrency limits in Step Functions
```

### 10.3 Reserved Capacity Planning

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     RESERVED CAPACITY RECOMMENDATIONS                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘

At 50,000+ users (predictable workload):

┌─────────────────────┬────────────────┬────────────────┬────────────────┐
│ Service             │ On-Demand Cost │ Reserved Cost  │ Savings        │
├─────────────────────┼────────────────┼────────────────┼────────────────┤
│ DynamoDB            │ $150/month     │ $100/month     │ 33%            │
│ ElastiCache         │ $200/month     │ $130/month     │ 35%            │
│ Lambda Provisioned  │ $250/month     │ $175/month     │ 30%            │
├─────────────────────┼────────────────┼────────────────┼────────────────┤
│ Total               │ $600/month     │ $405/month     │ 32% overall    │
└─────────────────────┴────────────────┴────────────────┴────────────────┘

Commitment: 1-year reserved capacity with no upfront payment
Breakeven: ~4 months
```

---

## 11. Implementation Roadmap

### 11.1 Phased Implementation Plan

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           IMPLEMENTATION ROADMAP                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘

PHASE 1: Foundation (Weeks 1-3)
═══════════════════════════════════════════════════════════════════════════════════════

Week 1: Infrastructure Setup
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Set up AWS Organization and accounts (dev, staging, prod)                         │
│ □ Configure AWS CDK/Terraform for IaC                                               │
│ □ Create base VPC, subnets, security groups                                         │
│ □ Set up CI/CD pipeline (GitHub Actions → AWS)                                      │
│ □ Configure CloudWatch Log Groups and alarms                                        │
│ □ Set up AWS Secrets Manager                                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

Week 2: Core Services
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Create S3 buckets with lifecycle policies                                         │
│ □ Create DynamoDB tables (Jobs, Users, ApiKeys)                                     │
│ □ Set up Cognito User Pool and Identity Pool                                        │
│ □ Create API Gateway (REST + WebSocket)                                             │
│ □ Deploy initial Lambda functions (api-handler, job-scheduler)                      │
│ □ Configure SQS queues and dead-letter queues                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

Week 3: Authentication & Authorization
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Implement Cognito authentication flow                                              │
│ □ Create Lambda authorizers for API Gateway                                          │
│ □ Implement API key generation and validation                                        │
│ □ Set up IAM policies for user isolation                                             │
│ □ Configure presigned URL generation                                                 │
│ □ Test end-to-end auth flow                                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

PHASE 2: Core Processing (Weeks 4-6)
═══════════════════════════════════════════════════════════════════════════════════════

Week 4: Lambda Container Images
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Create base Docker image with Python + dependencies                               │
│ □ Package librosa, soundfile, scipy in container                                    │
│ □ Add FFmpeg to conversion container                                                │
│ □ Push to ECR, configure Lambda to use container                                    │
│ □ Test audio loading and basic operations                                           │
│ □ Optimize cold start time (<3 seconds target)                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

Week 5: Audio Processing Functions
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Implement audio-splitter Lambda (refactor from CLI)                               │
│ □ Implement audio-converter Lambda                                                   │
│ □ Implement quality-analyzer Lambda                                                  │
│ □ Implement metadata-editor Lambda                                                   │
│ □ Implement spectrogram-generator Lambda                                             │
│ □ Add S3 input/output handling                                                       │
│ □ Add DynamoDB status updates                                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

Week 6: Step Functions Workflows
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Define Podcast workflow state machine                                              │
│ □ Define Music Mastering workflow state machine                                      │
│ □ Define Audiobook workflow state machine                                            │
│ □ Implement error handling and retry logic                                           │
│ □ Add parallel processing for multi-output workflows                                 │
│ □ Test complete workflow execution                                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

PHASE 3: API & Integration (Weeks 7-8)
═══════════════════════════════════════════════════════════════════════════════════════

Week 7: REST API Implementation
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Implement all API endpoints from OpenAPI spec                                      │
│ □ Add request validation (JSON Schema)                                               │
│ □ Implement rate limiting                                                            │
│ □ Add CORS configuration                                                             │
│ □ Generate API documentation (Swagger/OpenAPI)                                       │
│ □ Deploy API to staging environment                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

Week 8: Real-time & Notifications
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Implement WebSocket API for progress updates                                       │
│ □ Set up SNS for email/webhook notifications                                         │
│ □ Configure EventBridge for event-driven processing                                  │
│ □ Implement webhook delivery system                                                  │
│ □ Add CloudFront distribution                                                        │
│ □ Test real-time updates end-to-end                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

PHASE 4: Frontend & SDKs (Weeks 9-10)
═══════════════════════════════════════════════════════════════════════════════════════

Week 9: Web Application
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Create React/Next.js application                                                   │
│ □ Implement authentication UI (Cognito)                                              │
│ □ Build file upload component with progress                                          │
│ □ Create job monitoring dashboard                                                    │
│ □ Implement WebSocket connection for live updates                                    │
│ □ Deploy to S3 + CloudFront                                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

Week 10: SDKs & MCP
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Create Python SDK package                                                          │
│ □ Create JavaScript/TypeScript SDK                                                   │
│ □ Implement MCP tool definitions                                                     │
│ □ Create CLI wrapper for cloud API                                                   │
│ □ Write SDK documentation                                                            │
│ □ Publish packages (PyPI, npm)                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

PHASE 5: Production Readiness (Weeks 11-12)
═══════════════════════════════════════════════════════════════════════════════════════

Week 11: Testing & Security
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Load testing (target: 1000 concurrent users)                                       │
│ □ Security audit (penetration testing)                                               │
│ □ Performance optimization                                                           │
│ □ Cost optimization review                                                           │
│ □ Configure AWS WAF rules                                                            │
│ □ Set up AWS Shield                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

Week 12: Launch Preparation
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ □ Final staging environment testing                                                  │
│ □ Production deployment                                                              │
│ □ Configure monitoring and alerting                                                  │
│ □ Set up on-call rotation                                                            │
│ □ Create runbooks for common issues                                                  │
│ □ Soft launch with beta users                                                        │
│ □ GA launch                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

TOTAL TIMELINE: 12 weeks (3 months)
```

### 11.2 MVP Definition

```yaml
MVP Scope (Week 8 Deliverable):

Features:
  - User registration and authentication
  - File upload (up to 500 MB)
  - Audio splitting
  - Format conversion (WAV, MP3, FLAC)
  - Metadata editing
  - Quality analysis
  - Podcast workflow
  - Basic web UI
  - REST API with API keys

Not in MVP (Post-Launch):
  - Mobile apps
  - Desktop apps
  - MCP integration
  - Music mastering workflow
  - Audiobook workflow
  - Batch processing (multiple files)
  - Real-time WebSocket updates
  - Advanced analytics dashboard
```

---

## 12. Monitoring & Observability

### 12.1 Monitoring Stack

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           OBSERVABILITY ARCHITECTURE                                    │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              METRICS (CloudWatch)                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Application Metrics:                    Infrastructure Metrics:                     │
│  ┌────────────────────────────────┐     ┌────────────────────────────────┐          │
│  │ • Jobs submitted (count)       │     │ • Lambda invocations           │          │
│  │ • Jobs completed (count)       │     │ • Lambda duration (p50, p99)   │          │
│  │ • Jobs failed (count)          │     │ • Lambda errors                │          │
│  │ • Processing time (histogram)  │     │ • Lambda throttles             │          │
│  │ • Queue depth                  │     │ • API Gateway latency          │          │
│  │ • File sizes (histogram)       │     │ • API Gateway 4xx/5xx          │          │
│  │ • Quality scores               │     │ • DynamoDB consumed capacity   │          │
│  └────────────────────────────────┘     │ • S3 request counts            │          │
│                                         └────────────────────────────────┘          │
│                                                                                      │
│  Custom Dashboards:                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │ • Operations Dashboard: Real-time job processing status                       │ │
│  │ • Business Dashboard: User signups, job volume, revenue                       │ │
│  │ • Performance Dashboard: Latency percentiles, error rates                     │ │
│  │ • Cost Dashboard: Daily/weekly/monthly spend by service                       │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               LOGGING (CloudWatch Logs)                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Log Groups:                                                                         │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │ /aws/lambda/audio-splitter-api         │ Retention: 30 days                   │ │
│  │ /aws/lambda/audio-splitter-split       │ Retention: 14 days                   │ │
│  │ /aws/lambda/audio-splitter-convert     │ Retention: 14 days                   │ │
│  │ /aws/apigateway/audio-splitter-api     │ Retention: 7 days                    │ │
│  │ /aws/stepfunctions/workflows           │ Retention: 30 days                   │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  Structured Logging Format:                                                          │
│  {                                                                                   │
│    "timestamp": "2025-12-27T10:00:00.000Z",                                          │
│    "level": "INFO",                                                                  │
│    "requestId": "abc-123",                                                           │
│    "userId": "user-456",                                                             │
│    "jobId": "job-789",                                                               │
│    "operation": "convert",                                                           │
│    "duration": 5432,                                                                 │
│    "fileSize": 104857600,                                                            │
│    "status": "success"                                                               │
│  }                                                                                   │
│                                                                                      │
│  Log Insights Queries:                                                               │
│  • Error rate by operation                                                           │
│  • Slow jobs (>5 minutes)                                                            │
│  • Failed jobs with error details                                                    │
│  • Usage patterns by user                                                            │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               TRACING (AWS X-Ray)                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Trace Flow:                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                              │   │
│  │  API Gateway ─── Lambda (API) ─── DynamoDB                                   │   │
│  │       │                │                                                     │   │
│  │       │                └─── SQS ─── Lambda (Processor) ─── S3               │   │
│  │       │                              │                                       │   │
│  │       │                              └─── Step Functions                     │   │
│  │       │                                        │                             │   │
│  │       │                                        ├─── Lambda (Convert)         │   │
│  │       │                                        ├─── Lambda (Analyze)         │   │
│  │       │                                        └─── Lambda (Notify)          │   │
│  │       │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  Sampling Rules:                                                                     │
│  • Default: 5% of requests                                                           │
│  • Errors: 100% of errors                                                            │
│  • Slow requests (>3s): 100%                                                         │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               ALERTING                                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Critical Alarms (PagerDuty/Slack):                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │ • Error rate > 5% for 5 minutes                                               │ │
│  │ • API latency p99 > 5 seconds for 5 minutes                                   │ │
│  │ • Lambda throttles > 100 in 5 minutes                                         │ │
│  │ • DLQ messages > 10                                                           │ │
│  │ • DynamoDB throttled requests > 0                                             │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
│  Warning Alarms (Slack only):                                                        │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │ • Error rate > 1% for 15 minutes                                              │ │
│  │ • Queue depth > 1000                                                          │ │
│  │ • Lambda concurrent executions > 80% limit                                    │ │
│  │ • Daily cost > $100                                                           │ │
│  └────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Disaster Recovery

### 13.1 Backup & Recovery Strategy

```yaml
Disaster Recovery Plan:

Recovery Objectives:
  RTO (Recovery Time Objective): 4 hours
  RPO (Recovery Point Objective): 1 hour

Backup Strategy:
  DynamoDB:
    - Point-in-time recovery: Enabled (35-day retention)
    - On-demand backups: Daily at 00:00 UTC
    - Cross-region backup: To us-west-2

  S3:
    - Versioning: Disabled (cost optimization)
    - Cross-region replication: Optional for Enterprise tier
    - Lifecycle: Processed files retained for 90 days

  Cognito:
    - User export: Monthly backup to S3
    - Password cannot be exported (users must reset)

  Secrets Manager:
    - Secrets replicated to DR region

  Infrastructure:
    - IaC (CDK/Terraform): Complete infrastructure as code
    - Can redeploy entire stack in <1 hour

Multi-Region Strategy (Enterprise):
  Primary: us-east-1
  Secondary: us-west-2 (warm standby)

  Active-Active:
    - API Gateway: Regional endpoints
    - DynamoDB: Global Tables
    - S3: Cross-region replication
    - Lambda: Deployed to both regions

  Failover:
    - Route 53 health checks
    - Automatic DNS failover
    - <5 minute failover time
```

---

## 14. Appendices

### 14.1 Technology Stack Summary

```yaml
Frontend:
  - React 18 / Next.js 14
  - TypeScript
  - TailwindCSS
  - AWS Amplify

Backend:
  - Python 3.12
  - Lambda (Container images)
  - API Gateway (REST + WebSocket)
  - Step Functions (Standard)
  - DynamoDB
  - S3
  - SQS / SNS / EventBridge

Infrastructure:
  - AWS CDK (TypeScript) or Terraform
  - Docker / ECR
  - CloudFront + WAF
  - Cognito

CI/CD:
  - GitHub Actions
  - AWS CodePipeline (optional)
  - Semantic versioning

Monitoring:
  - CloudWatch Logs/Metrics
  - X-Ray
  - CloudWatch Alarms → SNS → PagerDuty/Slack
```

### 14.2 Key AWS Service Limits

```yaml
Service Limits to Monitor:

Lambda:
  - Concurrent executions: 1,000 (default) → Request increase
  - Function timeout: 15 minutes (max)
  - Memory: 10,240 MB (max)
  - Container image size: 10 GB (max)
  - /tmp storage: 10,240 MB (max)

API Gateway:
  - Requests per second: 10,000 (default)
  - Payload size: 10 MB
  - WebSocket connections: 1,000,000 concurrent

DynamoDB:
  - Partition throughput: 3,000 RCU, 1,000 WCU
  - Item size: 400 KB
  - Query/Scan result: 1 MB

S3:
  - Object size: 5 TB
  - PUT requests per prefix: 3,500/s
  - GET requests per prefix: 5,500/s

Step Functions:
  - State transitions: 25,000 per execution
  - Execution history: 25,000 events
  - Concurrent executions: 1,000,000

SQS:
  - Message size: 256 KB
  - Retention: 14 days (max)
  - FIFO throughput: 3,000 msg/s with batching
```

### 14.3 Cost Calculator

```python
# Python function to estimate monthly costs
def estimate_monthly_cost(
    users: int,
    jobs_per_user: int = 10,
    avg_file_size_mb: int = 100,
    avg_processing_duration_sec: int = 60,
    avg_memory_mb: int = 2048
) -> dict:
    """
    Estimate monthly AWS costs for Audio Splitter Suite
    """
    total_jobs = users * jobs_per_user

    # Lambda costs
    lambda_gb_seconds = (avg_memory_mb / 1024) * avg_processing_duration_sec * total_jobs
    lambda_cost = (lambda_gb_seconds - 400_000) * 0.0000166667  # Free tier: 400K GB-s
    lambda_cost = max(0, lambda_cost)

    # API Gateway costs
    api_requests = total_jobs * 5  # ~5 API calls per job
    api_cost = (api_requests - 1_000_000) * 0.0000035  # Free tier: 1M
    api_cost = max(0, api_cost)

    # S3 costs
    storage_gb = (avg_file_size_mb / 1024) * total_jobs * 2  # input + output
    storage_cost = storage_gb * 0.023  # Standard storage
    transfer_cost = storage_gb * 0.09  # Data transfer out
    s3_cost = storage_cost + transfer_cost

    # DynamoDB costs (on-demand)
    writes = total_jobs * 10  # ~10 writes per job
    reads = total_jobs * 20   # ~20 reads per job
    dynamo_cost = (writes * 1.25 + reads * 0.25) / 1_000_000

    # CloudFront costs
    cloudfront_cost = storage_gb * 0.085  # Per GB transfer

    total = lambda_cost + api_cost + s3_cost + dynamo_cost + cloudfront_cost

    return {
        "lambda": round(lambda_cost, 2),
        "api_gateway": round(api_cost, 2),
        "s3": round(s3_cost, 2),
        "dynamodb": round(dynamo_cost, 2),
        "cloudfront": round(cloudfront_cost, 2),
        "total": round(total, 2)
    }

# Examples
print(estimate_monthly_cost(users=1000))      # ~$20-50
print(estimate_monthly_cost(users=10000))     # ~$200-300
print(estimate_monthly_cost(users=100000))    # ~$2,000-3,000
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 2025 | Architecture Team | Initial proposal |

---

**Next Steps:**
1. Review and approve architecture proposal
2. Finalize technology choices (CDK vs Terraform, React vs Next.js)
3. Create detailed technical specifications for Phase 1
4. Set up AWS Organization and initial infrastructure
5. Begin development sprint

---

*This document is a living document and will be updated as the implementation progresses.*
