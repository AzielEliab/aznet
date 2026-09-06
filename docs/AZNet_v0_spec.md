# AZNet v0 spec (AZN-WP-0.1)

Machine-oriented companion to [whitepaper.md](whitepaper.md).

- Product: AZNet
- Version: 0.1.0
- Spec: AZN-WP-0.1
- Author: Aziel Eliab only
- License: Apache-2.0
- Marker: `Truth Is No Defense — .AZNet — AZ.`
- Pair: AZNet + AZBrowser both required
- Unlock: FragGate
- Time: StaticClock (advisory; not a scheduler)
- Worker: control-plane / demo garden
- Node: device-local silent verification

## Receipt kinds

`GARDEN` · `STAMP` · `MEMORIAL` · `PAIR` · `UNLOCK` · `WITNESS` · `WITHDRAW`

## Forced ABSENT fields

`payload` · `keys` · `user_content`

## Memorial reasons

`ui_altered` · `integrity_refuse` · `node_withdraw` · `pair_broken` · `witness_fail` · `isolation`

## Hash algorithm

SHA-256 of canonical UTF-8 JSON (sorted keys, no extra whitespace).
`receipt_hash` is excluded from the encoding. Genesis `prev_hash` is
64 zero hex characters.
