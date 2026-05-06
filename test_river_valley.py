import json

# Simulate what the LLM would extract for 'River Valley resort'
query_name = 'River Valley resort'
print(f'User query: {query_name}')
print()

# Now check how it would match with the database
suffixes = [' resort', ' camp', ' stay', ' retreat', ' lodge', ' hotel']
query_name_processed = query_name.lower().strip()
for suffix in suffixes:
    if query_name_processed.endswith(suffix):
        query_name_processed = query_name_processed[:-len(suffix)].strip()
        
print(f'Processed query name: {query_name_processed}')

# Load actual resort
with open('data/json_files/resorts.json') as f:
    resorts = json.load(f)
    river_valley = [r for r in resorts if r['id'] == 81][0]
    resort_name = river_valley['name'].lower().strip()
    print(f'Actual resort name in DB: {resort_name}')
    print()
    print(f'Match check: "{query_name_processed}" in "{resort_name}" = {query_name_processed in resort_name}')
    print(f'Reverse check: "{resort_name}" in "{query_name_processed}" = {resort_name in query_name_processed}')
    print()
    print('✓ MATCH WILL SUCCEED!' if (query_name_processed in resort_name or resort_name in query_name_processed) else '✗ MATCH WILL FAIL!')
    print()
    print(f'River Valley Resort Details:')
    print(f'  Category: {river_valley["category"]}')
    print(f'  Location: {river_valley["location"]}')
    print(f'  Price: ₹{river_valley["price"]} per person per day')
    print(f'  Rating: {river_valley["rating"]} ({river_valley["review_count"]} reviews)')
    print(f'  Family Friendly: {river_valley["family_friendly"]}')
    print(f'  Romantic Couples: {river_valley["romantic_couples"]}')
