# Mission: Phase 2 - Service Expansion

## M1: Service Registry Expansion | status: completed

### T1.1: Add 8 New ServiceDefinitions to services.py | agent:Worker
- [x] S1.1.1: Add sqlite service (database, no port, sqlite_version) | size:S
- [x] S1.1.2: Add couchdb service (database, port 5984, http_get) | size:S
- [x] S1.1.3: Add kafka service (message_broker, port 9092, kafka_api_version) | size:S
- [x] S1.1.4: Add nats service (message_broker, port 4222, http_get) | size:S
- [x] S1.1.5: Add elasticsearch service (search, port 9200, http_get) | size:S
- [x] S1.1.6: Add meilisearch service (search, port 7700, http_get) | size:S
- [x] S1.1.7: Add typesense service (search, port 8108, http_get_with_api_key) | size:S
- [x] S1.1.8: Add minio service (storage, port 9000, http_get) | size:S

### T1.2: Fix mongo health check type | agent:Worker | depends:T1.1
- [x] S1.2.1: Change mongo health_check_type from tcp_port to mongo_ping | size:S

### T1.3: Reviewer Verification - Registry | agent:Reviewer | depends:T1.1,T1.2
- [x] S1.3.1: Verify 15 services registered | size:S

## M2: Verifier Health Checks | status: completed

### T2.1: Add health check functions to verifier.py | agent:Worker
- [x] S2.1.1: Add _http_get_check function (shared by couchdb, elasticsearch, meilisearch, minio) | size:S
- [x] S2.1.2: Add _http_get_with_api_key_check function (for typesense) | size:S
- [x] S2.1.3: Add _mongo_ping function (real mongosh check) | size:S
- [x] S2.1.4: Add _kafka_api_version function (broker API probe) | size:S
- [x] S2.1.5: Add _sqlite_version function (embedded DB check) | size:S
- [x] S2.1.6: Update HEALTH_CHECK_DISPATCH map with 5 new types | size:S
- [x] S2.1.7: Update _verify_service dispatch logic with new elif branches | size:S

### T2.2: Reviewer Verification - Verifier | agent:Reviewer | depends:T2.1
- [x] S2.2.1: Verify 9 health check types in dispatch map | size:S

## M3: Integration Verification | status: completed | depends:M1,M2

### T3.1: Final system verification | agent:Reviewer | depends:M1,M2
- [x] S3.1.1: Verify all 15 services load correctly | size:S
- [x] S3.1.2: Verify no regressions in existing 7 services | size:S
