# CollegeProject Change Log

## 2026-03-23

### Change
Implemented strict budget handling in resort search.

### Reason
The assistant was treating a user's budget as if a resort only needed to start within that budget. This produced misleading recommendations where the maximum package price exceeded the user's stated limit.

### Files Touched
- `tools.py`

### Behavior Update
- User budget now defaults to a strict interpretation: `price_max <= budget`
- Phrases like `my budget is 3000`, `budget is 3000`, and `within 3000` are treated as strict budget limits
- If no resorts fully fit the budget, the system now clearly says so and offers fallback options that start within the user's budget

### Notes
- This change improves recommendation trustworthiness for startup-style user expectations
- Booking flow was left unchanged

## 2026-03-23

### Change
Replaced price ranges with a single simple `price` field across ingestion and search.

### Reason
The product needs a simpler and more predictable pricing model for chat-based recommendations. Instead of using `price_min` and `price_max`, the system now uses one normalized price value.

### Files Touched
- `ingest.py`
- `tools.py`
- `agents.py`

### Behavior Update
- Resort metadata now stores only `price`
- Search and budget filtering now work on a single price value
- Tool responses now display `price` as `INR per day per person`
- Researcher prompt now instructs the agent to use only this single-price model

### Notes
- The normalized `price` currently uses the original `price_min` value as the single simple price
- You must rerun `python ingest.py` before testing `python main.py` so the new metadata is written into Chroma and FAISS

## 2026-03-23

### Change
Converted the active resort dataset to store a single averaged `price` field and removed `price_min` / `price_max`.

### Reason
You wanted the source data itself simplified so the project uses one clear price value per resort instead of a range.

### Files Touched
- `data/json_files/resorts.json`
- `ingest.py`

### Behavior Update
- Each resort now has `price`
- `price` is the rounded average of the old min and max values
- `price_min` and `price_max` were removed from the active dataset
- Ingestion now reads `price` directly from the dataset

### Notes
- You must rerun `python ingest.py` before starting the app again

## 2026-03-23

### Change
Updated ingestion to read JSON files with UTF-8 BOM support.

### Reason
The rewritten dataset file was saved with a UTF-8 BOM, which caused `json.decoder.JSONDecodeError` during `python ingest.py`.

### Files Touched
- `ingest.py`

### Behavior Update
- Dataset loading now uses `utf-8-sig`
- `ingest.py` can read the current `resorts.json` file successfully

## 2026-03-23

### Change
Upgraded resort recommendations from raw result dumps to concierge-style top-match summaries.

### Reason
The search response was technically improving but still felt like backend output. You wanted the agent to return top options with fit reasons, estimated totals, and tradeoffs.

### Files Touched
- `tools.py`

### Behavior Update
- Queries asking for `best options`, `which one should I choose`, or `backup` now return a top-match summary
- The summary includes:
  - top 3 matches
  - `Why it fits`
  - `Tradeoff`
  - detailed match blocks below
- Group-size queries still include estimated total nightly cost

## 2026-03-23

### Change
Expanded recommendation summaries to include closest alternatives when exact matches are too few, and removed contact-detail overload from the first response.

### Reason
The assistant was still returning only one exact match for some queries. It needed to behave more like a concierge by offering backup options without dumping contact data too early.

### Files Touched
- `tools.py`

### Behavior Update
- Recommendation queries now show:
  - exact matches first
  - closest alternatives when fewer than 3 exact matches exist
- Contact details are hidden from the first recommendation response
- Detailed match blocks now focus on price, rating, fit, and summary context

## 2026-03-23

### Change
Removed internal agent and routing traces from the user-facing chat experience.

### Reason
The app still looked like an internal multi-agent demo because it printed `Researcher`, `Supervisor`, and load-balancer activity directly in the terminal.

### Files Touched
- `main.py`
- `agents.py`

### Behavior Update
- The chat now presents replies under a single `Assistant` voice
- `Supervisor` routing lines are no longer printed
- load-balancer debug prints are no longer shown in the terminal
- welcome text now matches a product-style assistant instead of an internal tourism agent label

## 2026-03-23

### Change
Added deterministic `best to worst` sorting for resort list queries.

### Reason
The assistant was filtering correctly for some list queries but still ranking results in a semantic order that did not match the user's explicit request to sort from best to worst.

### Files Touched
- `tools.py`

### Behavior Update
- Queries containing `sorted from best to worst`, `sort from best to worst`, or `best to worst` now sort results deterministically by:
  - rating descending
  - price ascending as tie-breaker
  - name ascending as final tie-breaker

## 2026-03-23

### Change
Fixed a query-sorting runtime bug in `search_resorts`.

### Reason
The first version of the deterministic sorting change referenced `normalized_query` before it was initialized, which caused a runtime error during `python main.py`.

### Files Touched
- `tools.py`

### Behavior Update
- `search_resorts` now initializes `normalized_query` before any sort-intent checks
- explicit sorting queries should run without raising that error

## 2026-03-23

### Change
Grounded itinerary planning in verified resort search results.

### Reason
The planner was producing attractive but generic and partially hallucinated itineraries. It needed to build plans from actual resort and activity data already available in the project.

### Files Touched
- `agents.py`

### Behavior Update
- `planner_node` now runs `search_resorts` on the latest user request before itinerary generation
- planner responses are prompted with verified resort research context
- planner prompt now explicitly forbids invented attractions, facilities, and wildlife claims
- itinerary responses should recommend specific stays and remain more factual

## 2026-03-23

### Change
Improved decision-style resort ranking and output for `which one should I choose` queries.

### Reason
The assistant was still over-weighting adventure keywords and could pick lower-rated resorts even when the user explicitly asked for a good rating and a best-choice recommendation.

### Files Touched
- `tools.py`

### Behavior Update
- Decision queries now strongly prioritize rating when the user mentions `good rating`
- Lower-rated resorts are penalized in decision-style recommendation flows
- `which one should I choose` responses now use:
  - `Best choice`
  - `Second-best backup`
  - optional third alternative when useful

## 2026-03-23

### Change
Improved casual-user query handling and suppressed retriever parser dumps from the chat experience.

### Reason
The system was performing better on structured prompts than on natural user phrasing like `around 4500 for the night` and was leaking LangChain parser errors into the terminal.

### Files Touched
- `tools.py`

### Behavior Update
- Casual budget phrases like `around 4500` and `about 4500` now map to budget filtering
- Soft recommendation prompts like `what do you suggest` now trigger recommendation-style responses
- Peaceful/calm/low-crowd wording now contributes to ranking
- Retriever parsing failures no longer print raw backend error dumps into the user-facing chat

## 2026-03-23

### Change
Fixed group-nightly budget parsing for casual user phrasing.

### Reason
The system failed to interpret queries like `we’re 4 people` with `around 4500 for the night` as a total group nightly budget, so it recommended resorts that were far above the intended budget.

### Files Touched
- `tools.py`

### Behavior Update
- Guest-count parsing now recognizes phrases like `we’re 4 people` and `we are 4 people`
- Total budget is converted to per-person budget only when the user clearly means a nightly group total, such as:
  - `for the night`
  - `per night`
  - `for one night`

## 2026-03-23

### Change
Expanded natural-language sort detection for `best first` style queries.

### Reason
The deterministic sort logic worked for `sorted from best to worst` but missed natural phrasing like `sort the best ones first`.

### Files Touched
- `tools.py`

### Behavior Update
- Deterministic rating-first sorting now also activates for:
  - `best ones first`
  - `show best first`
  - `top rated first`
  - `highest rated first`

## 2026-03-23

### Change
Relaxed booking date parsing for casual month-day date ranges.

### Reason
The booking flow was too strict for natural user phrasing like `for march 26 to march 28` and unnecessarily asked the user to restate dates in a more explicit format.

### Files Touched
- `agents.py`

### Behavior Update
- Booking date parsing now accepts month-day phrases without a year
- Inputs like `March 26 to March 28` are normalized to `March 26, 2026 to March 28, 2026`

## 2026-03-23

### Change
Added deterministic supervisor routing for planning and booking intents.

### Reason
The same casual user query could sometimes route to `Planner` and other times to `Researcher`, which made the product feel unstable and unreliable.

### Files Touched
- `agents.py`

### Behavior Update
- Obvious itinerary-style prompts now route directly to `Planner`
- Obvious booking prompts now route directly to `Booker`
- This reduces LLM routing randomness for repeated user requests

## 2026-03-24

### Change
Made booking confirmation deterministic and tightened planner wording against unsupported assumptions.

### Reason
The booking reply was too vague even after the WhatsApp message was sent, and the planner could still imply guided tours, restaurants, or facilities that were not clearly grounded in the retrieved context.

### Files Touched
- `agents.py`

### Behavior Update
- `booker_node` now:
  - detects the last recommended resort
  - extracts dates and contact
  - builds guest details from prior chat context
  - calls `book_resort` directly
- Booking replies now echo the actual booking details returned by the tool
- Planner prompt now avoids unsupported assumptions like guided tours, pools, and restaurant claims unless clearly grounded

## 2026-03-24

### Change
Cleaned wording and formatting in user-facing responses.

### Reason
The core behavior was strong, but the CLI still showed awkward text artifacts, backend-style phrasing, and booking confirmations that felt too technical.

### Files Touched
- `tools.py`
- `agents.py`

### Behavior Update
- Common mojibake text like `â€“` and `â€™` is cleaned before display
- Result formatting now uses cleaner names, locations, and descriptions
- Booking confirmations now:
  - avoid exposing the Twilio SID
  - sound more user-friendly
  - title-case normalized month names
- Planner wording is now guided toward a more natural, less theatrical tone

## 2026-03-24

### Change
Built the first FastAPI backend for the assistant.

### Reason
The assistant logic is now stable enough to expose over HTTP so the next step can be a real chat UI instead of only a terminal CLI.

### Files Touched
- `api.py`
- `requirements.txt`

### Behavior Update
- Added `GET /health`
- Added `POST /chat`
- Added `POST /sessions`
- Added `DELETE /sessions/{session_id}`
- Chat sessions are stored in memory so multi-turn conversation context is preserved per session ID

### Run Notes
- Start the API with:
  - `uvicorn api:app --reload`

## 2026-03-24

### Change
Built the first chat UI/frontend and connected it to the FastAPI backend.

### Reason
The assistant had moved beyond CLI-only usefulness. A simple web chat interface was needed to test the product like an actual travel assistant.

### Files Touched
- `frontend/index.html`
- `frontend/styles.css`
- `frontend/app.js`
- `api.py`

### Behavior Update
- Visiting `/` now serves a browser-based chat UI
- The frontend:
  - creates a session automatically
  - sends messages to `POST /chat`
  - preserves multi-turn session context
  - supports starting a new chat

### Run Notes
- Start the app with:
  - `python -m uvicorn api:app --reload`
- Open:
  - `http://127.0.0.1:8000/`

## 2026-03-24

### Change
Added a dedicated small-talk path for greetings and simple help messages.

### Reason
Messages like `Hi` were falling through into the search flow and returning resort lists, which is poor product behavior for a chat assistant.

### Files Touched
- `agents.py`

### Behavior Update
- Greetings like `Hi`, `Hello`, and `Hey` now return a short conversational assistant reply
- `Thanks`, `help`, and `what can you do` also route to the small-talk handler
- Small-talk no longer triggers resort search

## 2026-03-24

### Change
Broadened recommendation-intent detection for natural phrasing.

### Reason
The assistant was too literal about phrases like `what do you suggest` and missed equivalent user wording such as `what would you suggest`, which caused plain list output instead of recommendation-style replies.

### Files Touched
- `tools.py`

### Behavior Update
- Recommendation flow now also activates for natural phrases like:
  - `what would you suggest`
  - `what would you recommend`
  - `any suggestions`
  - `what are my options`
  - `show me options`

## 2026-03-24

### Change
Removed normal chat-turn dependence on supervisor LLM routing and hardened API error handling.

### Reason
The FastAPI app was still crashing on some chat turns because supervisor routing could call Groq, and the current Groq account is restricted. That made ordinary chat requests fail with `500 Internal Server Error`.

### Files Touched
- `agents.py`
- `api.py`

### Behavior Update
- Normal user turns now route deterministically:
  - greetings and help -> `SmallTalk`
  - booking requests -> `Booker`
  - itinerary-style prompts -> `Planner`
  - everything else from a user turn -> `Researcher`
- This avoids relying on provider-based supervisor routing for common user messages
- API chat failures now return a clean fallback reply instead of crashing the request
- Failed user turns are removed from session history so a bad provider call does not pollute later chat context

## 2026-03-24

### Change
Polished recommendation wording and shortened the first-response detail blocks.

### Reason
Recommendation replies were still too generic and too long. They used broad phrases like `family-friendly` and `good for bird watching` even when the user did not ask for those things, and the first web reply dumped too much detail.

### Files Touched
- `tools.py`
- `frontend/index.html`

### Behavior Update
- Fit reasons are now more context-aware:
  - couple trips no longer get `family-friendly`
  - bird watching is only mentioned when the user asks for it
  - peaceful/nature requests now get more relevant wording
- Recommendation replies now show compact `Quick details` instead of long `Detailed matches`
- The frontend example placeholder text was cleaned to remove encoding artifacts
- Tradeoff wording now uses the actual user budget when group-night pricing is involved

## 2026-03-24

### Change
Added streamed chat replies in the web UI and polished recommendation wording.

### Reason
Replies were still appearing all at once, which made the chat feel static. Recommendation copy also needed a more natural tone and less repetitive phrasing.

### Files Touched
- `api.py`
- `tools.py`
- `frontend/app.js`
- `frontend/styles.css`

### Behavior Update
- Added `POST /chat/stream` using server-sent events
- Web chat now renders assistant replies progressively instead of waiting for the full block
- Assistant bubbles show a subtle streaming caret while the reply is arriving
- Recommendation headings now sound more natural, for example:
  - `Best match for your request`
  - `Backup option`
  - `Closest alternatives if you want more options`

## 2026-03-24

### Change
Improved streamed reply formatting in the web chat.

### Reason
The first streaming version showed text continuously with weak spacing, so headings, numbered options, and detail lines did not feel readable in the UI.

### Files Touched
- `api.py`
- `frontend/app.js`
- `frontend/styles.css`

### Behavior Update
- Streamed chunks now preserve spaces and line breaks safely
- Assistant replies are rendered with structured formatting for:
  - section headings
  - numbered options
  - detail labels like `Why it fits`, `Tradeoff`, `Price`, and `Rating`
- The web chat should now look closer to a real product conversation instead of one long paragraph

## 2026-03-24

### Change
Added lightweight memory, hybrid retrieval, reranking, and a basic evaluation harness.

### Reason
The next meaningful product upgrades were not more UI tweaks, but stronger retrieval quality, conversational continuity, and a repeatable way to measure answer quality over time.

### Files Touched
- `api.py`
- `tools.py`
- `evaluate.py`
- `evaluation_cases.json`

### Behavior Update
- The assistant now injects lightweight conversation memory such as:
  - budget
  - likely group size
  - calm/nature preference
  - rafting/birdwatching preference
  - premium/luxury intent
  - last suggested resort
- Resort retrieval now combines:
  - dense retriever results
  - keyword-ranked matches
  - reranking heuristics based on query intent
- Premium/luxury queries now prioritize higher-price, higher-rated stays more directly
- Added `evaluate.py` and `evaluation_cases.json` so the project can be scored repeatedly against representative travel queries

## 2026-03-24

### Change
Strengthened evaluation checks and added booking ID plus status tracking.

### Reason
The first evaluation harness was too loose and could miss weak recommendation quality. Booking also needed to move beyond a one-way WhatsApp message into a trackable workflow.

### Files Touched
- `evaluate.py`
- `evaluation_cases.json`
- `tools.py`
- `agents.py`
- `data/json_files/bookings.json`

### Behavior Update
- Evaluation now supports:
  - required content checks
  - forbidden content checks
- This makes weak winners and bad recommendation output easier to catch
- Booking requests now persist locally with:
  - `booking_id`
  - resort
  - dates
  - guest details
  - customer contact
  - status
  - created timestamp
- Booking confirmations now include a booking ID like `BK-0001`
- The assistant can now check booking status when the user provides a booking ID

## 2026-03-24

### Change
Fixed multi-turn booking continuity for relative dates and plain resort-name replies.

### Reason
The booking flow was still breaking in natural conversation. After the user started a booking, follow-up messages like `tomorrow 12pm` or a plain resort name could fall back into search instead of continuing the booking flow.

### Files Touched
- `agents.py`
- `tools.py`

### Behavior Update
- Booking flow now stays inside the `Booker` path while a booking is in progress
- Relative booking dates like `tomorrow 12pm` and `day after tomorrow 12pm` are normalized into exact timestamps
- If the user sends only a resort name during booking, the assistant treats it as a selected resort instead of a fresh search

## 2026-03-24

### Change
Corrected the Twilio send channel to use WhatsApp addresses explicitly.

### Reason
The app said it sent bookings over WhatsApp, but the Twilio call was still using raw phone numbers. That could create false-positive success messages while the owner never actually received a WhatsApp message.

### Files Touched
- `tools.py`

### Behavior Update
- Booking sends now format both sender and receiver as `whatsapp:<number>`
- The channel now matches the user-facing message that says the owner was notified on WhatsApp

## 2026-03-24

### Change
Added Twilio delivery-status capture to booking sends.

### Reason
The app could say a booking was sent even when Twilio accepted the request but WhatsApp delivery did not actually complete.

### Files Touched
- `tools.py`

### Behavior Update
- Booking records now store:
  - Twilio message SID
  - Twilio message status
  - Twilio error code and message when available
- Booking replies now show the current Twilio status
- If Twilio reports `failed` or `undelivered`, the assistant now says delivery did not complete instead of claiming the owner was notified

## 2026-03-25

### Change
Isolated each booking into its own draft context and added explicit confirmation before sending.

### Reason
Starting a new booking could incorrectly reuse old dates, resort, and contact details from an earlier completed booking. That made repeat booking attempts dangerous and confusing.

### Files Touched
- `agents.py`

### Behavior Update
- A new booking intent now starts a fresh booking draft instead of reusing old completed booking details
- Booking extraction now uses only the current booking draft context
- Once resort, dates, guest details, and contact are available, the assistant asks for confirmation
- The booking is sent only after the user replies `confirm`

## 2026-03-25

### Change
Added booking cancellation handling and more forgiving confirmation recognition.

### Reason
During confirmation, replies like `cancel it` should stop the booking flow immediately. The flow was also too brittle for small confirmation typos.

### Files Touched
- `agents.py`

### Behavior Update
- `cancel`, `cancel it`, `stop`, and `never mind` now cancel the current booking draft
- common confirmation typos like `confiem` are now accepted
