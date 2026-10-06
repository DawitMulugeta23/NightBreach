#!/usr/bin/env bash
# Live smoke test for the lab launch flow. Needs TOKEN and a running backend.
set -u
API=${API:-http://127.0.0.1:8000/api/v1}
AUTH="Authorization: Bearer ${TOKEN:?set TOKEN first}"
SLUG=linux-file-permissions
OBJ=permissions-flag-001
FAILED=0
pass() { echo "[PASS] $1"; }
fail() { echo "[FAIL] $1"; FAILED=1; }
jget() { python3 -c "import sys,json; print(json.load(sys.stdin)$1)"; }
post() { curl -s -X POST "$API$1" -H "$AUTH" -H "Content-Type: application/json" ${2:+-d "$2"}; }

RESP=$(post /sandbox/labs/$SLUG/launch)
ENV_ID=$(echo "$RESP" | jget '["environment_id"]' 2>/dev/null)
[ -n "$ENV_ID" ] || { echo "launch failed: $RESP"; exit 1; }
trap 'post /sandbox/environments/$ENV_ID/terminate >/dev/null 2>&1' EXIT
echo "environment: $ENV_ID"

[ "$(echo "$RESP" | jget '["state"]')" = "ready" ] && pass "launch returns ready" || fail "state: $RESP"
echo "$RESP" | python3 -c 'import sys,json; m={x["name"]:x for x in json.load(sys.stdin)["machines"]}; sys.exit(0 if m["attacker"]["address"] and m["target"]["address"] is None else 1)' \
  && pass "attacker address shown, target address hidden" || fail "address visibility"

SECOND=$(post /sandbox/labs/$SLUG/launch | jget '["environment_id"]' 2>/dev/null)
[ "$SECOND" = "$ENV_ID" ] && pass "relaunch is idempotent" || fail "relaunch returned $SECOND"

SUBNET=$(echo "$RESP" | jget '["network_subnet"]'); TARGET_IP="${SUBNET%0/24}20"
ATT=nb-env-$ENV_ID-machine-attacker; TGT=nb-env-$ENV_ID-machine-target
docker exec $ATT nmap -sn "$SUBNET" 2>&1 | grep -q "$TARGET_IP" && pass "attacker discovers target ($TARGET_IP)" || fail "nmap did not find $TARGET_IP"

verify() { post /sandbox/environments/$ENV_ID/objectives/$OBJ/verify "{\"submission\":\"$1\"}" | jget '["correct"]' 2>/dev/null; }
[ "$(verify 'NB{perm_0000000000000000}')" = "False" ] && pass "wrong flag rejected" || fail "wrong flag was not rejected"
FLAG=$(docker exec $TGT grep -o 'NB{[^}]*}' /srv/backups/db-backup.sql)
[ "$(verify "$FLAG")" = "True" ] && pass "real flag accepted" || fail "real flag rejected ($FLAG)"

post /sandbox/environments/$ENV_ID/reset >/dev/null
LIM=$(docker inspect $TGT --format '{{.HostConfig.Memory}} {{.HostConfig.PidsLimit}}')
[ "$LIM" = "268435456 128" ] && pass "reset keeps target limits" || fail "limits after reset: $LIM"
[ "$(docker exec $TGT grep -o 'NB{[^}]*}' /srv/backups/db-backup.sql)" = "$FLAG" ] && pass "flag survived reset" || fail "flag changed after reset"

post /sandbox/environments/$ENV_ID/terminate >/dev/null
LEFT=$(docker ps -a --filter name=nb-env-$ENV_ID -q; docker network ls --filter name=nb-env-$ENV_ID -q)
[ -z "$LEFT" ] && pass "terminate leaves nothing behind" || fail "leftovers: $LEFT"

echo; [ $FAILED = 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $FAILED
