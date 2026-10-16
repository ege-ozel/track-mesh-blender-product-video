import type { DesktopStatus } from './api';

// Synthetic status fixture only. No Tauri backend, project files or network peers.
const project = '11111111-2222-4333-8444-555555555555';
const local = 'aaaaaaaa-0000-4000-8000-000000000001';
const remote = 'bbbbbbbb-0000-4000-8000-000000000002';
const peer = 'synthetic-studio-b-peer';
const snapshot = '7f31c8d2' + '0'.repeat(56);
const timestamp = '2026-10-13T17:30:00Z';
const info = { snapshot_id: snapshot, author_device_id: local, created_at: timestamp,
  author_name: 'Studio A', metadata_status: 'PUBLISHED' as const,
  total_size: 186646528, changed_bytes: 12582912, file_count: 24 };
const connection = { online: true, route: 'DIRECT' as const, transport: 'QUIC' };
export const fixture: DesktopStatus = {
  ready: true, closing: false, error: null, listen_port: 43101,
  configured_external_addresses: [], device: {device_id: local, name: 'Studio A', peer_id: 'synthetic-studio-a-peer'},
  data_directory: 'D:\\Demo\\TrackMesh', projects_location: 'D:\\Demo\\Projects',
  pairing: { project_id: null, remaining_seconds: 0, requests: [] },
  network: { addresses: [], error: null, peers: {[peer]: connection}, received_snapshots: [],
    port_mapping: {consent_enabled: false, state: 'NOT_ATTEMPTED', tcp: 'NOT_ATTEMPTED', udp: 'NOT_ATTEMPTED', detail: null, external_ip_state: 'UNKNOWN'},
    reachability: {state: 'UNVERIFIED', peer: null, transport: null, at_unix_seconds: null}},
  peer_states: {[peer]: 'CONNECTED'}, port_status: 'UNVERIFIED',
  pairing_approvals: [{project_id: project, device_id: remote, state: 'APPROVED'}],
  network_observation: {source: 'SYNTHETIC_DEMO', interfaces: [], default_gateways: [], wan_visible_ip: {state: 'UNKNOWN', source: 'SYNTHETIC_DEMO', value: null}, mappings: []},
  firewall_observation: {state: 'UNKNOWN', profiles: [], tcp_rules: {allow: 'UNKNOWN', block: 'UNKNOWN'}, udp_rules: {allow: 'UNKNOWN', block: 'UNKNOWN'}, third_party_products: 'UNKNOWN'},
  page: {offset: 0, has_more: false, projects: [{
    project: {project_id: project, name: 'Neon Forest Demo', root: 'D:\\Demo\\Projects\\Neon Forest Demo', latest_local_snapshot: snapshot,
      last_verified_at: timestamp, verified_peer_id: null, verified_snapshot_id: snapshot, recovery_required: false, mailbox_url: null, relay_address: null, error: null},
    grant_problem: null, revoke_problem: false, missing_functions: [], root_available: true, root_empty: false, active_transfer: false,
    local_snapshot: info, peers: [{device: {device_id: remote, name: 'Studio B', peer_id: peer}, announcement: {...info, metadata_status: 'REMOTE'}, history: [], known_lineage: 'EQUAL', offline_head: null}],
    pending_publications: 0, transfer: null
  }]},
  jobs: [], checks: [{device_id: remote, fresh: true, current_known: true, age_seconds: 0,
    result: {project_id: project, local_snapshot: snapshot, remote_snapshot: snapshot, lineage: 'EQUAL', connection_state: 'CONNECTED', snapshot_status: 'UP_TO_DATE', verified_equal: true, connection, last_verified_at: timestamp}}],
  project_backends: {[project]: {backend: 'SUPABASE', supabase_url: 'https://synthetic-demo.supabase.co', supabase_anon_key: null}},
  default_supabase: null, supabase_states: {[project]: 'CLAIMED'}, invite_pending: false, invite_needs_service_fields: false,
  upnp_mapping_asked: true, manual_public_endpoint: null
};

export async function invoke<T>(command: string): Promise<T> {
  if (command === 'get_status') return structuredClone(fixture) as T;
  throw new Error('Static synthetic demo: actions are disabled.');
}
