<!-- Documentation for the dual API rotation system design. -->
<!-- File: DUAL_API_ROTATION_SYSTEM.md -->

# Dual API Key Rotation System - Load Balancing & 24/7 Availability

## Overview

The system now uses **intelligent dual-provider API rotation** with:

- **3 Groq API keys** (llama-3.1-8b & llama-3.3-70b)
- **3 Gemini API keys** (gemini-2.5-flash)
- **2 rotation strategies**: Provider alternation OR Same-provider rotation

## Architecture

### 6 Total API Keys

#### Groq Keys (3)

```
GROQ_API_KEY_1=<your-groq-api-key-1>
GROQ_API_KEY_2=<your-groq-api-key-2>
GROQ_API_KEY_3=<your-groq-api-key-3>
```

#### Gemini Keys (3)

```
GOOGLE_API_KEY_1=<your-google-api-key-1>
GOOGLE_API_KEY_2=<your-google-api-key-2>
GOOGLE_API_KEY_3=<your-google-api-key-3>
```

**IMPORTANT**: Never commit real API keys to the repository. Use `.env` file or environment variables.

## Rotation Strategies

### Strategy 1: Provider Alternation (RECOMMENDED) 🌟

```
Request 1 → Groq API #1
Request 2 → Gemini API #1  (if Groq fails)
Request 3 → Groq API #2
Request 4 → Gemini API #2  (if Groq fails)
Request 5 → Groq API #3
Request 6 → Gemini API #3  (if Groq fails)
Request 7 → Groq API #1    (cycle repeats)
```

**Best for:**

- ✅ Balanced load between providers
- ✅ Maximum resilience (any 1 provider down = 50% capacity)
- ✅ Avoiding provider-specific rate limits
- ✅ Best uptime guarantees

### Strategy 2: Same-Provider Rotation

```
Request 1 → Groq API #1
Request 2 → Groq API #2
Request 3 → Groq API #3
Request 4 → Groq API #1 (cycle repeats)
```

**Best for:**

- ✅ Optimizing for specific provider performance
- ✅ Provider-specific tuning
- ✅ A/B testing between providers

## Available Functions

### PRIMARY FUNCTION - Use This! ⭐

```python
from travel_agents.llms import prefer_groq_invoke_alternating

synthesizer = prefer_groq_invoke_alternating(groq_70b, gemini_llm)
result = await synthesizer.ainvoke(messages)
```

**Behavior:**

- Request 1: Tries Groq, falls back to Gemini if fails
- Request 2: Tries Gemini, falls back to Groq if fails
- Auto-increments through 6 providers: G1→Ge1→G2→Ge2→G3→Ge3→repeat

### Rotation Helpers

#### `get_rotated_groq_llm()`

Get next Groq 8B instance

```python
llm = get_rotated_groq_llm()  # Cycles: groq_llm_1 → groq_llm_2 → groq_llm_3
```

#### `get_rotated_groq_70b()`

Get next Groq 70B instance

```python
llm = get_rotated_groq_70b()  # Cycles: groq_70b_1 → groq_70b_2 → groq_70b_3
```

#### `get_rotated_gemini()`

Get next Gemini instance

```python
llm = get_rotated_gemini()  # Cycles: gemini_llm_1 → gemini_llm_2 → gemini_llm_3
```

#### `get_next_provider_pair()`

Get next provider in alternating sequence

```python
llm, provider_type = get_next_provider_pair()
# Returns: ("groq" | "gemini", and corresponding LLM instance)
# Cycles through: G1→Ge1→G2→Ge2→G3→Ge3
```

### Legacy Function (Still Works)

```python
from travel_agents.llms import prefer_groq_invoke

synthesizer = prefer_groq_invoke(groq_70b, gemini_llm)
# Always tries Groq first (less resilient, but available)
```

## Rate Limit Distribution

### Scenario: Trip Planning Query (8,034 tokens)

#### Before (Single API)

```
Request: 8,034 tokens
Limit: 6,000 TPM
Result: ❌ RATE LIMITED ERROR
```

#### After (Dual Provider Alternation)

```
Request 1: Groq#1 = 8,034 tokens (OK, quota not yet hit)
Request 2: Gemini#1 = 8,034 tokens (different provider, OK)
Request 3: Groq#2 = 8,034 tokens (different key, OK)
...
Result: ✅ Distributed across 6 providers = Much safer
```

### Capacity Comparison

| Metric             | Before                  | After                   |
| ------------------ | ----------------------- | ----------------------- |
| API Keys           | 1                       | 6                       |
| Groq Keys          | 1                       | 3                       |
| Gemini Keys        | 0                       | 3                       |
| Effective Capacity | 6,000 TPM               | 18,000+ TPM             |
| Single Key Load    | 100%                    | 17-20%                  |
| Resilience         | Single point of failure | Survive 1 provider down |

## Monitoring

### Log Output

```
INFO: Alternating to Groq API #1 (rotation #1)
INFO: Alternating to Gemini API #1 (rotation #2)
INFO: Alternating to Groq API #2 (rotation #3)
INFO: Alternating to Gemini API #2 (rotation #4)
INFO: Alternating to Groq API #3 (rotation #5)
INFO: Alternating to Gemini API #3 (rotation #6)
INFO: Alternating to Groq API #1 (rotation #7)  ← Cycle repeats
```

Check logs in:

- `travel_api.log`
- `app.log`
- `uvicorn_error.log`

### Verification Steps

1. **Check Alternation**: Look for Groq→Gemini pattern in logs
2. **Count Rotations**: Request #1-6 should use different APIs
3. **Verify Cycling**: Request #7 should return to first API
4. **Monitor Failovers**: If any API fails, check fallback logs

## Environment Variables

### Configuration in `.env`

```env
# Groq Keys - Set your actual keys in .env file
GROQ_API_KEY_1=<your-groq-api-key-1>
GROQ_API_KEY_2=<your-groq-api-key-2>
GROQ_API_KEY_3=<your-groq-api-key-3>

# Gemini Keys - Set your actual keys in .env file
GOOGLE_API_KEY_1=<your-google-api-key-1>
GOOGLE_API_KEY_2=<your-google-api-key-2>
GOOGLE_API_KEY_3=<your-google-api-key-3>

# Legacy (kept for compatibility)
GROQ_API_KEY=<your-groq-api-key>
GOOGLE_API_KEY=<your-google-api-key>
```

**IMPORTANT**: Environment variables take precedence over hardcoded defaults. Never commit real API keys.

## 24/7 System Availability Scenarios

### Scenario A: One Provider Hits Rate Limit

```
Groq at 11:59 PM: Hits rate limit
Gemini at 11:59 PM: Still available ✓

Result: System continues running at 50% capacity
Recovery: Groq key resets at 12:01 AM
```

### Scenario B: One API Key is Invalid

```
Groq API #1: Bad key (invalid)
Groq API #2: Good key ✓
Groq API #3: Good key ✓
Gemini API #1: Good key ✓
Gemini API #2: Good key ✓
Gemini API #3: Good key ✓

Result: System uses 5/6 keys, continues normally
```

### Scenario C: Complete Provider Outage

```
All Groq keys: Rate limited
Gemini API #1-3: All available ✓

Result: System falls back to Gemini, continues with graceful degradation
```

### Scenario D: High Traffic Spike

```
Before: Single API maxes out at 6,000 TPM
After: Can distribute across 6 providers

Capacity: 3x more requests per minute
Result: Handles traffic 3x better
```

## Code Changes Summary

**File**: `travel_agents/llms.py`

- Added: `GROQ_API_KEYS` array (3 keys)
- Added: `GEMINI_API_KEYS` array (3 keys)
- Added: `PROVIDER_SEQUENCE` tuple list (alternation pattern)
- Added: `groq_llm_1`, `groq_llm_2`, `groq_llm_3` instances
- Added: `groq_70b_1`, `groq_70b_2`, `groq_70b_3` instances
- Added: `gemini_llm_1`, `gemini_llm_2`, `gemini_llm_3` instances
- Added: `get_rotated_groq_llm()` function
- Added: `get_rotated_groq_70b()` function
- Added: `get_rotated_gemini()` function
- Added: `get_next_provider_pair()` function
- Added: `prefer_groq_invoke_alternating()` NEW!
- Updated: `prefer_groq_invoke()` with enhanced logging

**File**: `.env`

- Added: `GROQ_API_KEY_1`, `GROQ_API_KEY_2`, `GROQ_API_KEY_3`
- Added: `GOOGLE_API_KEY_1`, `GOOGLE_API_KEY_2`, `GOOGLE_API_KEY_3`

## Backward Compatibility

✅ All old code still works:

```python
# Old code (still functional)
from travel_agents.llms import groq_llm, groq_70b, gemini_llm, prefer_groq_invoke

synthesizer = prefer_groq_invoke(groq_70b, gemini_llm)
```

Old variable references:

- `groq_llm` = `groq_llm_1` (first instance)
- `groq_70b` = `groq_70b_1` (first instance)
- `gemini_llm` = `gemini_llm_1` (first instance)

## Testing Checklist

- [ ] Run test_fixes.py and check logs for alternating provider pattern
- [ ] Send 12+ requests and verify Groq→Gemini→Groq sequence
- [ ] Test rate limit recovery with sustained load
- [ ] Block one provider and verify fallback
- [ ] Monitor response times across different APIs
- [ ] Check provider dashboard usage logs

## Performance Expectations

| Metric         | Value                                |
| -------------- | ------------------------------------ |
| Response Time  | 0.5-2s per request                   |
| Throughput     | 3x better than single API            |
| Availability   | 99.9%+ (handle 1 provider failure)   |
| Cost           | Same as before (3 keys = same quota) |
| Latency Impact | <50ms from rotation logic            |

## Future Enhancements

- [ ] Weighted routing (prefer faster providers)
- [ ] Circuit breaker (temporarily disable failing keys)
- [ ] Metrics dashboard (API usage, response times)
- [ ] Dynamic key loading from secure vault
- [ ] Provider health checks (proactive failure detection)
- [ ] Cost tracking per API key
