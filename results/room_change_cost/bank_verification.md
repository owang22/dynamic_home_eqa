# Rebuilt banks vs `banks/baselines/fleet/`

The rebuild is deterministic and makes no LLM calls, so a rebuilt bank must differ from the current one ONLY by the two new header fields.

- households__generated__gpt-5.6-terra__hh_001_bank.jsonl: body identical; header adds receptacle_rooms (22 receptacles, 6 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_002_bank.jsonl: body identical; header adds receptacle_rooms (38 receptacles, 9 rooms) and home_base_room `living`
- households__generated__gpt-5.6-terra__hh_003_bank.jsonl: body identical; header adds receptacle_rooms (31 receptacles, 8 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_004_bank.jsonl: body identical; header adds receptacle_rooms (26 receptacles, 7 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_005_bank.jsonl: body identical; header adds receptacle_rooms (26 receptacles, 7 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_006_bank.jsonl: body identical; header adds receptacle_rooms (22 receptacles, 6 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_007_bank.jsonl: body identical; header adds receptacle_rooms (31 receptacles, 8 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_008_bank.jsonl: body identical; header adds receptacle_rooms (31 receptacles, 8 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_009_bank.jsonl: body identical; header adds receptacle_rooms (29 receptacles, 7 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_010_bank.jsonl: body identical; header adds receptacle_rooms (32 receptacles, 8 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_011_bank.jsonl: body identical; header adds receptacle_rooms (26 receptacles, 7 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_012_bank.jsonl: body identical; header adds receptacle_rooms (22 receptacles, 6 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_013_bank.jsonl: body identical; header adds receptacle_rooms (28 receptacles, 7 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_014_bank.jsonl: body identical; header adds receptacle_rooms (22 receptacles, 6 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_015_bank.jsonl: body identical; header adds receptacle_rooms (31 receptacles, 8 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_016_bank.jsonl: body identical; header adds receptacle_rooms (24 receptacles, 6 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_017_bank.jsonl: body identical; header adds receptacle_rooms (26 receptacles, 7 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_018_bank.jsonl: body identical; header adds receptacle_rooms (26 receptacles, 7 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_019_bank.jsonl: body identical; header adds receptacle_rooms (22 receptacles, 6 rooms) and home_base_room `kitchen`
- households__generated__gpt-5.6-terra__hh_020_bank.jsonl: body identical; header adds receptacle_rooms (23 receptacles, 6 rooms) and home_base_room `kitchen`

**Verdict: PASS.**
