from dotenv import load_dotenv
import logging
import os
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)

load_dotenv()

# Groq API key rotation for load balancing
# IMPORTANT: Set via environment variables (GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3)
# Do NOT hardcode API keys. Use .env file or system environment variables.
GROQ_API_KEYS = [
    os.getenv("GROQ_API_KEY_1", ""),
    os.getenv("GROQ_API_KEY_2", ""),
    os.getenv("GROQ_API_KEY_3", "")
]

# Gemini API key rotation for load balancing
# IMPORTANT: Set via environment variables (GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, GOOGLE_API_KEY_3)
# Do NOT hardcode API keys. Use .env file or system environment variables.
GEMINI_API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1", ""),
    os.getenv("GOOGLE_API_KEY_2", ""),
    os.getenv("GOOGLE_API_KEY_3", "")
]

# Fallback to legacy single keys if rotation keys not provided
if not any(GROQ_API_KEYS):
    legacy_groq = os.getenv("GROQ_API_KEY", "")
    if legacy_groq:
        GROQ_API_KEYS = [legacy_groq, legacy_groq, legacy_groq]
        logger.warning("Using legacy GROQ_API_KEY (should use GROQ_API_KEY_1/2/3)")

if not any(GEMINI_API_KEYS):
    legacy_gemini = os.getenv("GOOGLE_API_KEY", "")
    if legacy_gemini:
        GEMINI_API_KEYS = [legacy_gemini, legacy_gemini, legacy_gemini]
        logger.warning("Using legacy GOOGLE_API_KEY (should use GOOGLE_API_KEY_1/2/3)")

# Provider rotation: Alternates between Groq and Gemini
# Sequence: Groq#1 → Gemini#1 → Groq#2 → Gemini#2 → Groq#3 → Gemini#3 → repeat
PROVIDER_SEQUENCE = [
    ("groq", 0), ("gemini", 0), 
    ("groq", 1), ("gemini", 1), 
    ("groq", 2), ("gemini", 2)
]

# Initialize rotation counter (start at 0)
_api_call_counter = 0

# Validate API keys are available
valid_groq_keys = [k for k in GROQ_API_KEYS if k.strip()]
valid_gemini_keys = [k for k in GEMINI_API_KEYS if k.strip()]

if not valid_groq_keys:
    logger.error("❌ NO GROQ API KEYS SET! Set GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3 environment variables.")
    raise ValueError("Groq API keys not configured. Please set environment variables: GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3")

if not valid_gemini_keys:
    logger.error("❌ NO GEMINI API KEYS SET! Set GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, GOOGLE_API_KEY_3 environment variables.")
    raise ValueError("Gemini API keys not configured. Please set environment variables: GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, GOOGLE_API_KEY_3")

logger.info(f"✅ Groq API: {len(valid_groq_keys)} key(s) configured")
logger.info(f"✅ Gemini API: {len(valid_gemini_keys)} key(s) configured")

def get_next_groq_api():
    """Return next API key in round-robin rotation."""
    global _api_call_counter
    api_key = valid_groq_keys[_api_call_counter % len(valid_groq_keys)]
    _api_call_counter += 1
    logger.info(f"Using Groq API #{(_api_call_counter % len(valid_groq_keys)) or len(valid_groq_keys)} (rotation #{_api_call_counter})")
    return api_key

# Create multiple Groq instances with different API keys for load balancing
groq_llm_1 = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_retries=2, api_key=valid_groq_keys[0])
groq_llm_2 = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_retries=2, api_key=valid_groq_keys[1] if len(valid_groq_keys) > 1 else valid_groq_keys[0])
groq_llm_3 = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_retries=2, api_key=valid_groq_keys[2] if len(valid_groq_keys) > 2 else valid_groq_keys[0])

# List of all Groq instances for round-robin rotation
groq_instances = [groq_llm_1, groq_llm_2, groq_llm_3]

# High-capacity 70B model also with rotation
groq_70b_1 = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, max_retries=0, api_key=valid_groq_keys[0])
groq_70b_2 = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, max_retries=0, api_key=valid_groq_keys[1] if len(valid_groq_keys) > 1 else valid_groq_keys[0])
groq_70b_3 = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, max_retries=0, api_key=valid_groq_keys[2] if len(valid_groq_keys) > 2 else valid_groq_keys[0])

groq_70b_instances = [groq_70b_1, groq_70b_2, groq_70b_3]

# Create multiple Gemini instances with different API keys for load balancing
gemini_llm_1 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, max_retries=2, api_key=valid_gemini_keys[0])
gemini_llm_2 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, max_retries=2, api_key=valid_gemini_keys[1] if len(valid_gemini_keys) > 1 else valid_gemini_keys[0])
gemini_llm_3 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, max_retries=2, api_key=valid_gemini_keys[2] if len(valid_gemini_keys) > 2 else valid_gemini_keys[0])

# List of all Gemini instances for round-robin rotation
gemini_instances = [gemini_llm_1, gemini_llm_2, gemini_llm_3]

# Keep old references for compatibility
groq_llm = groq_llm_1
groq_70b = groq_70b_1
gemini_llm = gemini_llm_1

def prefer_groq_invoke(groq_runnable, gemini_runnable):
    """Invoke with Groq (with API rotation) first, then fallback to Gemini."""
    def invoke_wrapper(in_val):
        global _api_call_counter
        current_index = _api_call_counter % len(valid_groq_keys)
        try:
            logger.info(f"Attempting invoke with Groq API #{current_index + 1}")
            return groq_runnable.invoke(in_val)
        except Exception as e:
            logger.error(f"Groq LLM invoke failed: {type(e).__name__}: {str(e)}", exc_info=True)
            try:
                logger.info("Attempting fallback to Gemini LLM")
                return gemini_runnable.invoke(in_val)
            except Exception as fallback_e:
                logger.error(f"Gemini LLM fallback also failed: {type(fallback_e).__name__}: {str(fallback_e)}", exc_info=True)
                raise Exception(f"Both LLM providers failed. Groq: {str(e)} | Gemini: {str(fallback_e)}")
    
    async def ainvoke_wrapper(in_val):
        global _api_call_counter
        current_index = _api_call_counter % len(valid_groq_keys)
        _api_call_counter += 1  # Increment for next call
        try:
            logger.info(f"Attempting async invoke with Groq API #{current_index + 1}")
            return await groq_runnable.ainvoke(in_val)
        except Exception as e:
            logger.error(f"Groq LLM async failed: {type(e).__name__}: {str(e)}", exc_info=True)
            try:
                logger.info("Attempting async fallback to Gemini LLM")
                return await gemini_runnable.ainvoke(in_val)
            except Exception as fallback_e:
                logger.error(f"Gemini LLM async fallback also failed: {type(fallback_e).__name__}: {str(fallback_e)}", exc_info=True)
                raise Exception(f"Both LLM providers failed (async). Groq: {str(e)} | Gemini: {str(fallback_e)}")
            
    return RunnableLambda(invoke_wrapper, afunc=ainvoke_wrapper)

def get_rotated_groq_llm():
    """Get next Groq LLM instance in rotation."""
    global _api_call_counter
    index = _api_call_counter % len(groq_instances)
    _api_call_counter += 1
    logger.info(f"Returning Groq LLM #{index + 1} for request #{_api_call_counter}")
    return groq_instances[index]

def get_rotated_groq_70b():
    """Get next Groq 70B LLM instance in rotation."""
    global _api_call_counter
    index = _api_call_counter % len(groq_70b_instances)
    _api_call_counter += 1
    logger.info(f"Returning Groq 70B LLM #{index + 1} for request #{_api_call_counter}")
    return groq_70b_instances[index]

def get_rotated_gemini():
    """Get next Gemini LLM instance in rotation."""
    global _api_call_counter
    index = _api_call_counter % len(gemini_instances)
    _api_call_counter += 1
    logger.info(f"Returning Gemini LLM #{index + 1} for request #{_api_call_counter}")
    return gemini_instances[index]

def get_next_provider_pair():
    """Get next provider pair in alternating sequence (Groq→Gemini→Groq→Gemini...)."""
    global _api_call_counter
    provider_type, key_index = PROVIDER_SEQUENCE[_api_call_counter % len(PROVIDER_SEQUENCE)]
    _api_call_counter += 1
    
    if provider_type == "groq":
        llm = groq_instances[key_index]
        logger.info(f"Alternating to Groq API #{key_index + 1} (rotation #{_api_call_counter})")
    else:  # gemini
        llm = gemini_instances[key_index]
        logger.info(f"Alternating to Gemini API #{key_index + 1} (rotation #{_api_call_counter})")
    
    return llm, provider_type

def prefer_groq_invoke_alternating(groq_runnable, gemini_runnable):
    """Invoke with alternating Groq and Gemini for better load distribution."""
    def invoke_wrapper(in_val):
        global _api_call_counter
        primary_index = _api_call_counter % len(PROVIDER_SEQUENCE)
        try:
            provider_type, _ = PROVIDER_SEQUENCE[primary_index]
            logger.info(f"Attempting {provider_type.upper()} with alternating strategy")
            return groq_runnable.invoke(in_val) if provider_type == "groq" else gemini_runnable.invoke(in_val)
        except Exception as e:
            logger.error(f"Primary invoke failed: {type(e).__name__}: {str(e)}", exc_info=True)
            # Try the other provider as fallback
            try:
                fallback_type = "gemini" if provider_type == "groq" else "groq"
                logger.info(f"Attempting fallback to {fallback_type.upper()}")
                return gemini_runnable.invoke(in_val) if fallback_type == "gemini" else groq_runnable.invoke(in_val)
            except Exception as fallback_e:
                logger.error(f"Fallback invoke failed: {type(fallback_e).__name__}: {str(fallback_e)}", exc_info=True)
                raise Exception(f"Both {provider_type} and {'gemini' if provider_type == 'groq' else 'groq'} failed. {provider_type}: {str(e)} | Fallback: {str(fallback_e)}")
    
    async def ainvoke_wrapper(in_val):
        global _api_call_counter
        primary_index = _api_call_counter % len(PROVIDER_SEQUENCE)
        provider_type, _ = PROVIDER_SEQUENCE[primary_index]
        _api_call_counter += 1
        try:
            logger.info(f"Attempting async {provider_type.upper()} with alternating strategy")
            return await groq_runnable.ainvoke(in_val) if provider_type == "groq" else await gemini_runnable.ainvoke(in_val)
        except Exception as e:
            logger.error(f"Primary async invoke failed: {type(e).__name__}: {str(e)}", exc_info=True)
            # Try the other provider as fallback
            try:
                fallback_type = "gemini" if provider_type == "groq" else "groq"
                logger.info(f"Attempting async fallback to {fallback_type.upper()}")
                return await gemini_runnable.ainvoke(in_val) if fallback_type == "gemini" else await groq_runnable.ainvoke(in_val)
            except Exception as fallback_e:
                logger.error(f"Fallback async invoke failed: {type(fallback_e).__name__}: {str(fallback_e)}", exc_info=True)
                raise Exception(f"Both {provider_type} and {'gemini' if provider_type == 'groq' else 'groq'} failed (async). {provider_type}: {str(e)} | Fallback: {str(fallback_e)}")
    
    return RunnableLambda(invoke_wrapper, afunc=ainvoke_wrapper)

planner_prompt = (
    "You are an enthusiastic, local Dandeli Planner. "
    "Create a simple, grounded itinerary using only the resort and activity information in context. "
    "Do not invent attractions, amenities, or facility details that are not explicitly stated in the verified research. "
    "If you cannot answer accurately from the provided research, say so and ask for more details instead of guessing. "
    "Always recommend at least one specific resort from the provided research when the user asks for a stay. "
    "Keep the plan practical and realistic. "
    "Format the response clearly with Day 1 and Day 2 sections when relevant."
)

planner_agent = prefer_groq_invoke(create_react_agent(groq_llm, tools=[]), create_react_agent(gemini_llm, tools=[]))
