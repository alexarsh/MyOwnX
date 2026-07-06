#!/bin/bash
# End-to-end smoke test in an ISOLATED throwaway stack: its postgres lives
# on tmpfs and the whole stack is destroyed afterwards, so no test data
# ever appears in the dev app.
set -e
cd "$(dirname "$0")/.."

COMPOSE="docker compose -p myownx-e2e -f docker-compose.yml -f docker-compose.e2e.yml"
$COMPOSE up -d --build >/dev/null 2>&1
trap '$COMPOSE down -v --remove-orphans >/dev/null 2>&1' EXIT

API=${API:-http://localhost:3100/api}
echo -n "waiting for stack"
for _ in $(seq 1 60); do
  if curl -fs -o /dev/null "$API/search?q=ping&type=users"; then break; fi
  echo -n "."
  sleep 1
done
echo " up"

SUFFIX=$RANDOM
ALICE_NAME="alice$SUFFIX"
BOB_NAME="bob$SUFFIX"

jget() { python3 -c "import sys,json;print(json.load(sys.stdin)$1)"; }
expect() { # expect <label> <want> <got>
  if [ "$2" != "$3" ]; then echo "FAIL $1: want $2, got $3"; exit 1; fi
  echo "ok   $1"
}

signup() {
  curl -s -X POST "$API/users/signup" -H 'content-type: application/json' \
    -d "{\"username\":\"$1\",\"display_name\":\"$2\",\"password\":\"password123\"}" \
    | jget "['access_token']"
}

ALICE=$(signup "$ALICE_NAME" "Alice")
BOB=$(signup "$BOB_NAME" "Bob Rock")
expect "signup issues tokens" "2" "$( [ -n "$ALICE" ] && [ -n "$BOB" ] && echo 2 )"

post() { # post <token> <text> [reply_to]
  local body="{\"text\":\"$2\"${3:+,\"reply_to_id\":$3}}"
  curl -s -X POST "$API/posts" -H "authorization: Bearer $1" \
    -H 'content-type: application/json' -d "$body" | jget "['id']"
}

P1=$(post "$BOB" "Hello world, rockets are go! $SUFFIX")
post "$BOB" "Coffee and code." >/dev/null
post "$ALICE" "Alice checking in." >/dev/null

CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$API/users/$BOB_NAME/follow" \
  -H "authorization: Bearer $ALICE")
expect "follow" 204 "$CODE"

COUNT=$(curl -s "$API/timeline" -H "authorization: Bearer $ALICE" | jget "['items'].__len__()")
expect "home timeline shows own + followed posts" 3 "$COUNT"

curl -s -o /dev/null -X POST "$API/posts/$P1/like" -H "authorization: Bearer $ALICE"
post "$ALICE" "Great post Bob!" "$P1" >/dev/null
THREAD=$(curl -s "$API/posts/$P1" -H "authorization: Bearer $ALICE")
expect "like counted" 1 "$(echo "$THREAD" | jget "['post']['like_count']")"
expect "liked_by_me" True "$(echo "$THREAD" | jget "['post']['liked_by_me']")"
expect "reply in thread" 1 "$(echo "$THREAD" | jget "['replies'].__len__()")"

HITS=$(curl -s "$API/search?q=rockets&type=posts" | jget "['posts'].__len__()")
expect "post search finds rockets" "$( [ "$HITS" -ge 1 ] && echo yes )" yes

USERS=$(curl -s "$API/search?q=$BOB_NAME&type=users" | jget "['users'][0]['username']")
expect "user search" "$BOB_NAME" "$USERS"

PROFILE=$(curl -s "$API/users/$BOB_NAME" -H "authorization: Bearer $ALICE")
expect "follower count" 1 "$(echo "$PROFILE" | jget "['followers']")"

CODE=$(curl -s -o /dev/null -w '%{http_code}' -X DELETE "$API/posts/$P1" \
  -H "authorization: Bearer $ALICE")
expect "cannot delete someone else's post" 403 "$CODE"

echo "E2E PASSED"
