import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';

import 'theme.dart';

const genesisPrev = '0000000000000000000000000000000000000000000000000000000000000000';
const absent = 'ABSENT';
const spec = 'AZN-WP-0.1';
const marker = 'Truth Is No Defense — .AZNet — AZ.';

void main() {
  runApp(const AZNetApp());
}

class AZNetApp extends StatelessWidget {
  const AZNetApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AZNet',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const GardenPage(),
    );
  }
}

String digest(Map<String, dynamic> fields) {
  final keys = fields.keys.toList()..sort();
  final raw = '{${keys.map((k) => '${jsonEncode(k)}:${jsonEncode(fields[k])}').join(',')}}';
  return sha256.convert(utf8.encode(raw)).toString();
}

class Receipt {
  Receipt(this.fields, this.hash);
  final Map<String, dynamic> fields;
  final String hash;
}

class GardenPage extends StatefulWidget {
  const GardenPage({super.key});

  @override
  State<GardenPage> createState() => _GardenPageState();
}

class _GardenPageState extends State<GardenPage> {
  String _pair = 'UNPAIRED';
  String _unlock = 'LOCKED';
  final _ledger = <Receipt>[];
  String _status = 'Pair AZBrowser, then FragGate unlock.';

  String _now() => DateTime.now().toUtc().toIso8601String().split('.').first + 'Z';

  Map<String, dynamic> _base({required String kind, required String prev}) {
    return {
      'actor': 'operator',
      'azbrowser': 'https://github.com/AzielEliab/azbrowser',
      'aznet_node': 'device-local',
      'date_stamp': _now().substring(0, 10),
      'event_kind': kind,
      'final_hash': null,
      'fraggate': _unlock == 'UNLOCKED' ? 'unlocked' : 'required',
      'genesis_hash': null,
      'hash_hex': null,
      'keys': absent,
      'label': null,
      'marker': marker,
      'note': '',
      'pair_status': _pair,
      'payload': absent,
      'prev_hash': prev,
      'reason': null,
      'spec': spec,
      'staticclock': null,
      'summary': null,
      'timestamp': _now(),
      'unlock_status': _unlock,
      'user_content': absent,
      'witness_hash': null,
      'zone': 'UTC',
    };
  }

  void _append(String kind, Map<String, dynamic> extra) {
    final prev = _ledger.isEmpty ? genesisPrev : _ledger.last.hash;
    final fields = _base(kind: kind, prev: prev)..addAll(extra);
    setState(() {
      _ledger.add(Receipt(fields, digest(fields)));
      _status = '$kind  ${_ledger.last.hash}';
    });
  }

  void _pairNow() {
    _pair = 'PAIRED';
    _append('PAIR', {'pair_status': 'PAIRED', 'unlock_status': 'LOCKED'});
  }

  void _unlockNow() {
    if (_pair != 'PAIRED') {
      setState(() => _status = 'AZNet + AZBrowser both required.');
      return;
    }
    _unlock = 'UNLOCKED';
    _append('UNLOCK', {'pair_status': 'PAIRED', 'unlock_status': 'UNLOCKED', 'fraggate': 'unlocked'});
  }

  void _stamp() {
    if (_pair != 'PAIRED' || _unlock != 'UNLOCKED') {
      setState(() => _status = 'Pair + FragGate unlock required.');
      return;
    }
    final hashHex = sha256.convert(utf8.encode('AZNet Gold Pages card 0 — verification without hosting')).toString();
    _append('STAMP', {'hash_hex': hashHex, 'pair_status': 'PAIRED', 'unlock_status': 'UNLOCKED'});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AZNet')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Verification without hosting. Presence without authority.',
            style: TextStyle(color: kGold, fontStyle: FontStyle.italic, fontSize: 16),
          ),
          const SizedBox(height: 8),
          const Text(marker, style: TextStyle(color: kGold)),
          const SizedBox(height: 8),
          const Text(
            'On-device silent node. Hashes only. AZNet + AZBrowser both required. '
            'Not an alt internet. Author Aziel Eliab.',
          ),
          const SizedBox(height: 16),
          Text('Pair: $_pair  Unlock: $_unlock', style: const TextStyle(color: kGold)),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              FilledButton(onPressed: _pairNow, child: const Text('Pair AZBrowser')),
              OutlinedButton(onPressed: _unlockNow, child: const Text('FragGate unlock')),
              OutlinedButton(onPressed: _stamp, child: const Text('Stamp')),
            ],
          ),
          const SizedBox(height: 12),
          Text(_status, style: const TextStyle(color: kGold)),
          const SizedBox(height: 16),
          for (var i = 0; i < _ledger.length; i++)
            Card(
              margin: const EdgeInsets.only(bottom: 10),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: SelectableText(
                  [
                    '#$i  ${_ledger[i].fields['event_kind']}',
                    'payload: ${_ledger[i].fields['payload']}',
                    'hash: ${_ledger[i].hash}',
                  ].join('\n'),
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 12, height: 1.4),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
