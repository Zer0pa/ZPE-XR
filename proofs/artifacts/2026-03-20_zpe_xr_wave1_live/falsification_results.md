# Falsification Results (Gate D)

## DT-XR-1
- Pass: `True`
- malformed_inputs: `6`
- handled_failures: `6`
- uncaught_crashes: `0`
- failure_signatures: `['Packet too short', 'Packet too short', 'Checksum mismatch', 'Checksum mismatch', 'Checksum mismatch', 'Checksum mismatch']`

## DT-XR-2
- Pass: `True`
- target_case: `{'loss_rate': 0.1, 'jitter_probability': 0.2, 'max_delay_frames': 1, 'seed': 1103, 'mpjpe_mm': 1.6366386724041315, 'pose_error_percent': 1.3638655603367764, 'pass_threshold_percent': 5.0, 'pass': True, 'delivery_stats': {'provided_packets': 1103, 'missing_packets': 397, 'total_frames': 1500}, 'decoder_stats': {'concealed_frames': 397, 'backup_recoveries': 284, 'parse_failures': 0}}`
- stress_case: `{'loss_rate': 0.3, 'jitter_probability': 0.3, 'max_delay_frames': 2, 'seed': 2207, 'mpjpe_mm': 5.471137417906396, 'pose_error_percent': 4.559281181588664, 'pass_threshold_percent': 5.0, 'pass': True, 'delivery_stats': {'provided_packets': 735, 'missing_packets': 765, 'total_frames': 1500}, 'decoder_stats': {'concealed_frames': 765, 'backup_recoveries': 368, 'parse_failures': 0}}`

## DT-XR-3
- Pass: `True`
- total_samples: `120`
- accuracy: `1.0`
- pass_threshold_accuracy: `0.9`
- confusion_matrix: `{'pinch': {'pinch': 20}, 'grip': {'grip': 20}, 'wave': {'wave': 20}, 'point': {'point': 20}, 'spread': {'spread': 20}, 'fist': {'fist': 20}}`

## DT-XR-4
- Pass: `True`
- required_consistent_runs: `5`
- consistent_runs: `5`
- runs: `[{'seed': 1103, 'packet_count': 700, 'first_hash': '9c66b028022e5e1630e0bfe06abe171049ea3cdcca6b842f12d07024a3ee9645', 'second_hash': '9c66b028022e5e1630e0bfe06abe171049ea3cdcca6b842f12d07024a3ee9645', 'hash_match': True}, {'seed': 2207, 'packet_count': 700, 'first_hash': 'e37a20e569909f6c0c060e150db9f4482c5f8651b71f2061caa6e8ebbc15ae98', 'second_hash': 'e37a20e569909f6c0c060e150db9f4482c5f8651b71f2061caa6e8ebbc15ae98', 'hash_match': True}, {'seed': 3301, 'packet_count': 700, 'first_hash': '596b7fd704594750d0d704246f32f59828d1892e9734b00487cb167a92d26ccd', 'second_hash': '596b7fd704594750d0d704246f32f59828d1892e9734b00487cb167a92d26ccd', 'hash_match': True}, {'seed': 4409, 'packet_count': 700, 'first_hash': '662165ec9a753978fc73c97e82c8e2eefa5336838671d6ebeeb5e8f39ce32f74', 'second_hash': '662165ec9a753978fc73c97e82c8e2eefa5336838671d6ebeeb5e8f39ce32f74', 'hash_match': True}, {'seed': 5501, 'packet_count': 700, 'first_hash': '561f0364c6f646b6d1e60a3a6de04c302253785b3e829cf0ab9589106e3e724a', 'second_hash': '561f0364c6f646b6d1e60a3a6de04c302253785b3e829cf0ab9589106e3e724a', 'hash_match': True}]`

## DT-XR-5
- Pass: `True`
- four_player: `{'avg_packet_bytes': 59.96, 'fps': 90, 'remote_players': 3, 'kbps_for_4_player_session': 15.809765624999999, 'pass_threshold_kbps': 40.0, 'pass': True}`
- eight_player: `{'avg_packet_bytes': 59.96, 'fps': 90, 'remote_players': 7, 'kbps_for_4_player_session': 36.889453124999996, 'pass_threshold_kbps': 40.0, 'pass': True}`

