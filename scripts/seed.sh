#!/bin/bash
# Seed the running dev stack with demo users, posts, follows and likes.
# Idempotent: re-running logs the users in instead of failing.
set -e
API=${API:-http://localhost:3000/api}
PASSWORD="demo-password-123"

jget() { python3 -c "import sys,json;print(json.load(sys.stdin)$1)"; }

token() { # token <username> <display name>
  local body="{\"username\":\"$1\",\"display_name\":\"$2\",\"password\":\"$PASSWORD\"}"
  local response
  response=$(curl -s -X POST "$API/users/signup" -H 'content-type: application/json' -d "$body")
  if echo "$response" | grep -q access_token; then
    echo "$response" | jget "['access_token']"
  else
    curl -s -X POST "$API/users/login" -H 'content-type: application/json' \
      -d "{\"username\":\"$1\",\"password\":\"$PASSWORD\"}" | jget "['access_token']"
  fi
}

post() { # post <token> <text> [reply_to] -> post id
  local body="{\"text\":\"$2\"${3:+,\"reply_to_id\":$3}}"
  curl -s -X POST "$API/posts" -H "authorization: Bearer $1" \
    -H 'content-type: application/json' -d "$body" | jget "['id']"
}

follow() { curl -s -o /dev/null -X POST "$API/users/$2/follow" -H "authorization: Bearer $1"; }
like() { curl -s -o /dev/null -X POST "$API/posts/$2/like" -H "authorization: Bearer $1"; }

echo "Seeding demo data into $API ..."
ADA=$(token ada "Ada Lovelace")
LINUS=$(token linus "Linus T.")
GRACE=$(token grace "Grace Hopper")

P1=$(post "$ADA" "The Analytical Engine weaves algebraic patterns just as the Jacquard loom weaves flowers and leaves.")
P2=$(post "$LINUS" "Talk is cheap. Show me the code.")
P3=$(post "$GRACE" "The most dangerous phrase in the language is: we have always done it this way.")
P4=$(post "$ADA" "Imagination is the discovering faculty, pre-eminently.")
post "$LINUS" "Nice thread!" "$P3" >/dev/null
post "$GRACE" "Strong agree." "$P2" >/dev/null

follow "$ADA" linus; follow "$ADA" grace
follow "$LINUS" ada; follow "$GRACE" ada; follow "$GRACE" linus

like "$LINUS" "$P1"; like "$GRACE" "$P1"; like "$ADA" "$P2"; like "$GRACE" "$P4"

echo "Done: 3 users (ada, linus, grace — password: $PASSWORD), 6 posts, follows and likes."
echo "Open http://localhost:3000 and log in as any of them."
