# API Key Rotation System - Load Balancing & 24/7 Availability

## Overview

The system now uses **round-robin API key rotation** across 3 different Groq API keys to distribute load and ensure 24/7 availability.

## Architecture

### 3 API Keys (Round-Robin Rotation)

```
Request 1 → API #1 (GROQ_API_KEY_1)
Request 2 → API #2 (GROQ_API_KEY_2)
Request 3 → API #3 (GROQ_API_KEY_3)
Request 4 → API #1 (repeat cycle)
Request 5 → API #2
... and so on
```

**Note**: Set actual API keys in `.env` file or environment variables. Do NOT commit API keys to repository.

### Models with Rotation

- **8B Model** (`llama-3.1-8b-instant`): 3 instances, one per API key
- **70B Model** (`llama-3.3-70b-versatile`): 3 instances, one per API key
- **Fallback**: Gemini 2.5 Flash (no rotation, single key)

### Rate Limit Distribution

- **Before**: All traffic on 1 API → Hit 6000 TPM limit quickly
- **After**: Traffic distributed across 3 APIs → 3x capacity (18,000 TPM total)
- **Per API**: ~6,000 TPM per key (within safe limits)

## Implementation Details

### Global Counter

```python
_api_call_counter = 0  # Thread-safe increment on each call
```

- Increments on each request
- Uses modulo operator for round-robin: `counter % 3`
- Returns: API #1, #2, #3, #1, #2, #3, ...

### Functions

#### `get_rotated_groq_llm()`

Returns next Groq 8B instance in rotation

```python
llm = get_rotated_groq_llm()  # Returns groq_llm_1, groq_llm_2, or groq_llm_3
```

#### `get_rotated_groq_70b()`

Returns next Groq 70B instance in rotation

```python
llm = get_rotated_groq_70b()  # Returns groq_70b_1, groq_70b_2, or groq_70b_3
```

#### `prefer_groq_invoke(groq_runnable, gemini_runnable)`

Smart fallback chain with logging:

1. Try Groq with current API
2. If fails, try Gemini fallback
3. If both fail, raise detailed error

### Logging

Every request logs which API is being used:

```
INFO: Using Groq API #1 (rotation #1)
INFO: Using Groq API #2 (rotation #2)
INFO: Using Groq API #3 (rotation #3)
INFO: Using Groq API #1 (rotation #4)
```

## Benefits

✅ **Load Balancing**

- Distribute traffic across 3 APIs
- Avoid rate limit exhaustion on single key
- Better resource utilization

✅ **24/7 Availability**

- If 1 API key fails/limited, 2 others still available
- Automatic fallback to Gemini if all Groq keys fail
- Graceful degradation

✅ **Scalability**

- Easy to add more API keys: just append to `GROQ_API_KEYS`
- Automatic rotation handles new keys
- No code changes needed

✅ **Monitoring**

- Logs show which API is being used
- Easy to track API usage patterns
- Identify which keys are rate-limited

## Expected Impact

### Before (Single API)

- Token limit: 6,000 TPM
- Issues: Trip planning query = 8,034 tokens → Rate limit error

### After (3 APIs)

- Token limit: ~2,000 TPM per API (safe margin)
- Each API gets 1/3 of traffic
- Trip planning: Distributed across APIs → No more errors

### Rate Limit Recovery

- If 1 API hits limit at minute 5, it resets at minute 6
- Other 2 APIs still available during that minute
- System remains responsive

## Code Changes

**File**: `travel_agents/llms.py`

- Added: `GROQ_API_KEYS` array with 3 keys
- Added: `_api_call_counter` for rotation
- Added: `groq_llm_1`, `groq_llm_2`, `groq_llm_3` instances
- Added: `groq_70b_1`, `groq_70b_2`, `groq_70b_3` instances
- Updated: `prefer_groq_invoke()` with logging
- Added: `get_rotated_groq_llm()` helper
- Added: `get_rotated_groq_70b()` helper

## Backward Compatibility

✅ Maintained - Old code using `groq_llm` and `groq_70b` still works

- `groq_llm = groq_llm_1` (backward compatible)
- `groq_70b = groq_70b_1` (backward compatible)
- New code can use rotation functions for optimal distribution

## Testing

To verify rotation is working:

1. Check logs for "Using Groq API #1", "#2", "#3" pattern
2. Send multiple requests and verify round-robin in logs
3. Test rate limit recovery (should handle sustained traffic better)

## Future Enhancements

- Add metrics: API usage per key, response times
- Weighted routing: prefer faster APIs
- Automatic key management from environment variables
- Circuit breaker: temporarily disable slow/failing keys
