use crc32fast::hash;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyModule;

const STREAM_MAGIC: &[u8; 4] = b"ZXRS";
const STREAM_VERSION: u8 = 1;
const PACKET_MAGIC: &[u8; 3] = b"ZXR";
const FORMAT_VERSION: u8 = 1;
const FLAG_KEYFRAME: u8 = 0x01;
const NO_BACKUP_SEQ: u16 = 0xFFFF;
const TOTAL_JOINTS: usize = 52;
const MM_PER_METER: f32 = 1000.0;

type QVec3 = (i16, i16, i16);
type DeltaEntry = (u8, i8, i8, i8);

#[derive(Default)]
struct EncoderState {
    reference_q: Option<Vec<QVec3>>,
    last_primary_entries: Vec<DeltaEntry>,
    last_primary_seq: u16,
}

struct ParsedPacket {
    is_keyframe: bool,
    keyframe_q: Option<Vec<QVec3>>,
    current_entries: Vec<DeltaEntry>,
}

#[pyfunction]
#[pyo3(signature = (frames, frame_rate=90.0, keyframe_interval=45, deadband_mm=1, quant_step_mm=1.0, enable_backup=true))]
fn encode_sequence(
    frames: Vec<Vec<Vec<f32>>>,
    frame_rate: f32,
    keyframe_interval: u16,
    deadband_mm: i16,
    quant_step_mm: f32,
    enable_backup: bool,
) -> PyResult<Vec<u8>> {
    if frame_rate <= 0.0 || !frame_rate.is_finite() {
        return Err(PyValueError::new_err("frame_rate must be > 0"));
    }
    if keyframe_interval == 0 {
        return Err(PyValueError::new_err("keyframe_interval must be > 0"));
    }
    if deadband_mm < 0 {
        return Err(PyValueError::new_err("deadband_mm must be >= 0"));
    }
    if quant_step_mm <= 0.0 || !quant_step_mm.is_finite() {
        return Err(PyValueError::new_err("quant_step_mm must be > 0"));
    }

    let mut packets = Vec::with_capacity(frames.len());
    let mut state = EncoderState {
        last_primary_seq: NO_BACKUP_SEQ,
        ..EncoderState::default()
    };

    for (seq_index, frame) in frames.iter().enumerate() {
        let seq = u16::try_from(seq_index)
            .map_err(|_| PyValueError::new_err("frame count exceeds packet sequence capacity"))?;
        let q_actual = quantize_positions(frame, quant_step_mm)
            .map_err(PyValueError::new_err)?;
        let timestamp_ms = (((seq_index as f32) * 1000.0) / frame_rate).round() as u32;
        let packet = encode_frame(
            seq,
            timestamp_ms,
            &q_actual,
            &mut state,
            keyframe_interval,
            deadband_mm,
            enable_backup,
        )
        .map_err(PyValueError::new_err)?;
        packets.push(packet);
    }

    Ok(pack_stream(&packets))
}

#[pyfunction]
#[pyo3(signature = (data, quant_step_mm=1.0))]
fn decode_sequence(data: Vec<u8>, quant_step_mm: f32) -> PyResult<Vec<Vec<(f32, f32, f32)>>> {
    if quant_step_mm <= 0.0 || !quant_step_mm.is_finite() {
        return Err(PyValueError::new_err("quant_step_mm must be > 0"));
    }

    let packets = unpack_stream(&data).map_err(PyValueError::new_err)?;
    let mut decoded_q: Vec<Vec<QVec3>> = Vec::with_capacity(packets.len());

    for packet in packets {
        let parsed = parse_packet(packet).map_err(PyValueError::new_err)?;
        if parsed.is_keyframe {
            decoded_q.push(parsed.keyframe_q.unwrap_or_default());
            continue;
        }

        let previous = decoded_q
            .last()
            .ok_or_else(|| PyValueError::new_err("delta packet encountered before keyframe"))?;
        let next = apply_entries(previous, &parsed.current_entries).map_err(PyValueError::new_err)?;
        decoded_q.push(next);
    }

    let scale = quant_step_mm / MM_PER_METER;
    let decoded = decoded_q
        .into_iter()
        .map(|frame| {
            frame
                .into_iter()
                .map(|(x, y, z)| (x as f32 * scale, y as f32 * scale, z as f32 * scale))
                .collect()
        })
        .collect();
    Ok(decoded)
}

#[pyfunction]
fn version() -> &'static str {
    "0.3.0"
}

#[pymodule]
fn _kernel(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(encode_sequence, module)?)?;
    module.add_function(wrap_pyfunction!(decode_sequence, module)?)?;
    module.add_function(wrap_pyfunction!(version, module)?)?;
    Ok(())
}

fn pack_stream(packets: &[Vec<u8>]) -> Vec<u8> {
    let total_payload: usize = packets.iter().map(|packet| 4 + packet.len()).sum();
    let mut out = Vec::with_capacity(9 + total_payload);
    out.extend_from_slice(STREAM_MAGIC);
    out.push(STREAM_VERSION);
    out.extend_from_slice(&(packets.len() as u32).to_le_bytes());
    for packet in packets {
        out.extend_from_slice(&(packet.len() as u32).to_le_bytes());
        out.extend_from_slice(packet);
    }
    out
}

fn unpack_stream(data: &[u8]) -> Result<Vec<&[u8]>, String> {
    if data.len() < 9 {
        return Err("stream too short".to_string());
    }
    if &data[0..4] != STREAM_MAGIC {
        return Err("bad stream magic".to_string());
    }
    if data[4] != STREAM_VERSION {
        return Err(format!("unsupported stream version: {}", data[4]));
    }

    let count = u32::from_le_bytes([data[5], data[6], data[7], data[8]]) as usize;
    let mut cursor = 9usize;
    let mut packets = Vec::with_capacity(count);
    for _ in 0..count {
        if cursor + 4 > data.len() {
            return Err("truncated stream packet header".to_string());
        }
        let packet_len = u32::from_le_bytes([
            data[cursor],
            data[cursor + 1],
            data[cursor + 2],
            data[cursor + 3],
        ]) as usize;
        cursor += 4;
        let end = cursor
            .checked_add(packet_len)
            .ok_or_else(|| "stream packet length overflow".to_string())?;
        if end > data.len() {
            return Err("truncated stream packet body".to_string());
        }
        packets.push(&data[cursor..end]);
        cursor = end;
    }
    if cursor != data.len() {
        return Err("stream contains trailing bytes".to_string());
    }
    Ok(packets)
}

fn quantize_positions(frame: &[Vec<f32>], quant_step_mm: f32) -> Result<Vec<QVec3>, String> {
    if frame.len() != TOTAL_JOINTS {
        return Err(format!(
            "frame must contain {} joints, got {}",
            TOTAL_JOINTS,
            frame.len()
        ));
    }

    let scale = MM_PER_METER / quant_step_mm;
    frame
        .iter()
        .map(|joint| {
            if joint.len() != 3 {
                return Err("each joint must contain exactly 3 values".to_string());
            }
            let x = quantize_axis(joint[0], scale)?;
            let y = quantize_axis(joint[1], scale)?;
            let z = quantize_axis(joint[2], scale)?;
            Ok((x, y, z))
        })
        .collect()
}

fn quantize_axis(value: f32, scale: f32) -> Result<i16, String> {
    if !value.is_finite() {
        return Err("joint values must be finite".to_string());
    }
    let quantized = (value * scale).round();
    if quantized < i16::MIN as f32 || quantized > i16::MAX as f32 {
        return Err("quantized joint value exceeds i16 range".to_string());
    }
    Ok(quantized as i16)
}

fn encode_frame(
    seq: u16,
    timestamp_ms: u32,
    q_actual: &[QVec3],
    state: &mut EncoderState,
    keyframe_interval: u16,
    deadband_mm: i16,
    enable_backup: bool,
) -> Result<Vec<u8>, String> {
    let force_keyframe = state.reference_q.is_none()
        || seq % keyframe_interval == 0
        || q_actual.len() != TOTAL_JOINTS;

    if force_keyframe {
        state.reference_q = Some(q_actual.to_vec());
        state.last_primary_entries.clear();
        state.last_primary_seq = NO_BACKUP_SEQ;
        return Ok(build_keyframe_packet(seq, timestamp_ms, q_actual));
    }

    let reference_q = state
        .reference_q
        .as_ref()
        .ok_or_else(|| "missing encoder reference state".to_string())?;
    let (entries, updated_ref, overflow) = compute_delta_entries(q_actual, reference_q, deadband_mm);

    if overflow {
        state.reference_q = Some(q_actual.to_vec());
        state.last_primary_entries.clear();
        state.last_primary_seq = NO_BACKUP_SEQ;
        return Ok(build_keyframe_packet(seq, timestamp_ms, q_actual));
    }

    let (backup_seq, backup_entries) = if enable_backup {
        (state.last_primary_seq, state.last_primary_entries.clone())
    } else {
        (NO_BACKUP_SEQ, Vec::new())
    };

    let packet = build_delta_packet(seq, timestamp_ms, &entries, backup_seq, &backup_entries)?;
    state.reference_q = Some(updated_ref);
    state.last_primary_entries = entries;
    state.last_primary_seq = seq;
    Ok(packet)
}

fn compute_delta_entries(
    q_actual: &[QVec3],
    q_ref: &[QVec3],
    deadband_mm: i16,
) -> (Vec<DeltaEntry>, Vec<QVec3>, bool) {
    let mut entries = Vec::new();
    let mut updated_ref = q_ref.to_vec();
    let mut overflow = false;

    for (idx, (qa, qr)) in q_actual.iter().zip(q_ref.iter()).enumerate() {
        let dx = qa.0 as i32 - qr.0 as i32;
        let dy = qa.1 as i32 - qr.1 as i32;
        let dz = qa.2 as i32 - qr.2 as i32;

        if dx.abs().max(dy.abs()).max(dz.abs()) <= deadband_mm as i32 {
            continue;
        }
        if dx.abs().max(dy.abs()).max(dz.abs()) > 127 {
            overflow = true;
            break;
        }

        entries.push((idx as u8, dx as i8, dy as i8, dz as i8));
        updated_ref[idx] = (
            qr.0 + dx as i16,
            qr.1 + dy as i16,
            qr.2 + dz as i16,
        );
    }

    (entries, updated_ref, overflow)
}

fn build_keyframe_packet(seq: u16, timestamp_ms: u32, q_actual: &[QVec3]) -> Vec<u8> {
    let mut payload = Vec::with_capacity(15 + q_actual.len() * 6 + 4);
    payload.extend_from_slice(PACKET_MAGIC);
    payload.push(FORMAT_VERSION);
    payload.push(FLAG_KEYFRAME);
    payload.extend_from_slice(&seq.to_le_bytes());
    payload.extend_from_slice(&NO_BACKUP_SEQ.to_le_bytes());
    payload.extend_from_slice(&timestamp_ms.to_le_bytes());
    payload.push(0);
    payload.push(0);
    for (x, y, z) in q_actual {
        payload.extend_from_slice(&x.to_le_bytes());
        payload.extend_from_slice(&y.to_le_bytes());
        payload.extend_from_slice(&z.to_le_bytes());
    }
    append_checksum(payload)
}

fn build_delta_packet(
    seq: u16,
    timestamp_ms: u32,
    current_entries: &[DeltaEntry],
    backup_seq: u16,
    backup_entries: &[DeltaEntry],
) -> Result<Vec<u8>, String> {
    if current_entries.len() > u8::MAX as usize || backup_entries.len() > u8::MAX as usize {
        return Err("delta entry count exceeds packet header capacity".to_string());
    }

    let mut payload = Vec::with_capacity(15 + (current_entries.len() + backup_entries.len()) * 4 + 4);
    payload.extend_from_slice(PACKET_MAGIC);
    payload.push(FORMAT_VERSION);
    payload.push(0);
    payload.extend_from_slice(&seq.to_le_bytes());
    payload.extend_from_slice(&backup_seq.to_le_bytes());
    payload.extend_from_slice(&timestamp_ms.to_le_bytes());
    payload.push(current_entries.len() as u8);
    payload.push(backup_entries.len() as u8);
    for entry in current_entries.iter().chain(backup_entries.iter()) {
        payload.push(entry.0);
        payload.push(entry.1 as u8);
        payload.push(entry.2 as u8);
        payload.push(entry.3 as u8);
    }
    Ok(append_checksum(payload))
}

fn append_checksum(mut payload: Vec<u8>) -> Vec<u8> {
    let checksum = hash(&payload);
    payload.extend_from_slice(&checksum.to_le_bytes());
    payload
}

fn parse_packet(packet: &[u8]) -> Result<ParsedPacket, String> {
    if packet.len() < 19 {
        return Err("packet too short".to_string());
    }

    let payload_len = packet.len() - 4;
    let supplied_checksum = u32::from_le_bytes([
        packet[payload_len],
        packet[payload_len + 1],
        packet[payload_len + 2],
        packet[payload_len + 3],
    ]);
    let calc_checksum = hash(&packet[..payload_len]);
    if supplied_checksum != calc_checksum {
        return Err("checksum mismatch".to_string());
    }

    if &packet[0..3] != PACKET_MAGIC {
        return Err("bad packet magic".to_string());
    }
    if packet[3] != FORMAT_VERSION {
        return Err(format!("unsupported packet version: {}", packet[3]));
    }

    let flags = packet[4];
    let current_count = packet[13] as usize;
    let backup_count = packet[14] as usize;
    let body = &packet[15..payload_len];

    if (flags & FLAG_KEYFRAME) != 0 {
        let expected_len = TOTAL_JOINTS * 6;
        if body.len() != expected_len {
            return Err("keyframe body length mismatch".to_string());
        }
        let mut keyframe_q = Vec::with_capacity(TOTAL_JOINTS);
        let mut cursor = 0usize;
        while cursor < body.len() {
            let x = i16::from_le_bytes([body[cursor], body[cursor + 1]]);
            let y = i16::from_le_bytes([body[cursor + 2], body[cursor + 3]]);
            let z = i16::from_le_bytes([body[cursor + 4], body[cursor + 5]]);
            keyframe_q.push((x, y, z));
            cursor += 6;
        }
        return Ok(ParsedPacket {
            is_keyframe: true,
            keyframe_q: Some(keyframe_q),
            current_entries: Vec::new(),
        });
    }

    let expected_len = (current_count + backup_count) * 4;
    if body.len() != expected_len {
        return Err("delta body length mismatch".to_string());
    }

    let mut current_entries = Vec::with_capacity(current_count);
    for idx in 0..current_count {
        let offset = idx * 4;
        current_entries.push((
            body[offset],
            body[offset + 1] as i8,
            body[offset + 2] as i8,
            body[offset + 3] as i8,
        ));
    }

    Ok(ParsedPacket {
        is_keyframe: false,
        keyframe_q: None,
        current_entries,
    })
}

fn apply_entries(base_q: &[QVec3], entries: &[DeltaEntry]) -> Result<Vec<QVec3>, String> {
    let mut updated = base_q.to_vec();
    for (joint_index, dx, dy, dz) in entries {
        let index = *joint_index as usize;
        if index >= updated.len() {
            return Err("joint index out of range".to_string());
        }
        let (x, y, z) = updated[index];
        updated[index] = (
            x + *dx as i16,
            y + *dy as i16,
            z + *dz as i16,
        );
    }
    Ok(updated)
}
