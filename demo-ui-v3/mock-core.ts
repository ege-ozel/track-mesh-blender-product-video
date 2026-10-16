import type { DesktopStatus, ProjectCard } from '@trackmesh/api';

// Synthetic Studio B status only. No Tauri backend, project files, identities or network peers.
// The page URL picks the state: ?state=idle | new | getting | done.
const state = new URLSearchParams(location.search).get('state') ?? 'idle';
const project = '11111111-2222-4333-8444-555555555555';
const local = 'bbbbbbbb-0000-4000-8000-000000000002';
const remote = 'aaaaaaaa-0000-4000-8000-000000000001';
const peer = 'synthetic-studio-a-peer';
const older = { snapshot_id: '4c1e' + '0'.repeat(60), author_device_id: remote, created_at: '2026-10-14T13:05:00Z',
  author_name: 'Studio A', metadata_status: 'REMOTE' as const, total_size: 186646528, changed_bytes: 0, file_count: 24 };
const newer = { ...older, snapshot_id: '7f31' + '0'.repeat(60), created_at: '2026-10-14T16:31:00Z', changed_bytes: 12582912 };
const got = state === 'done';
const ahead = state === 'new' || state === 'getting';
const connection = { online: true, route: 'DIRECT' as const, transport: 'QUIC' };
const now = () => Math.floor(Date.now() / 1000);

const card = (): ProjectCard => ({
  project: { project_id: project, name: 'Neon Forest', root: 'D:\\Music\\Neon Forest', latest_local_snapshot: (got ? newer : older).snapshot_id,
    last_verified_at: null, verified_peer_id: null, verified_snapshot_id: null, recovery_required: false, error: null },
  grant_problem: null, revoke_problem: false, missing_functions: [], root_available: true, root_empty: false, active_transfer: state === 'getting',
  local_snapshot: { ...(got ? newer : older), metadata_status: 'PUBLISHED' },
  peers: [{ device: { device_id: remote, name: 'Studio A', peer_id: peer }, announcement: ahead || got ? newer : older, history: [],
    known_lineage: ahead ? 'REMOTE_AHEAD' : 'EQUAL', offline_head: null }],
  pending_publications: 0, mailbox_enabled: false,
  transfer: state === 'getting' ? { transfer_id: 'demo-transfer', snapshot_id: newer.snapshot_id, source_device_id: remote, state: 'RECEIVING',
    completed_bytes: 8053063, total_bytes: 12582912, error: null } : null,
});

const status = (): DesktopStatus => ({
  presence: {}, daw_plugin_settings: [{ project_id: project, name: 'Neon Forest', auto_share: true }], plugin_handoff: null,
  pairing: { project_id: null, remaining_seconds: 0, requests: [] }, listen_port: 43101, configured_external_addresses: [],
  ready: true, closing: false, error: null, device: { device_id: local, name: 'Studio B', peer_id: 'synthetic-studio-b-peer' },
  data_directory: 'D:\\Demo\\TrackMesh', projects_location: 'D:\\Music',
  network: { addresses: [], error: null, peers: { [peer]: connection }, received_snapshots: [],
    port_mapping: { consent_enabled: true, state: 'MAPPED', tcp: 'MAPPED', udp: 'MAPPED', detail: null, external_ip_state: 'UNKNOWN' },
    reachability: { state: 'UNVERIFIED', peer: null, transport: null, at_unix_seconds: null } },
  peer_states: { [peer]: 'CONNECTED' }, port_status: 'UNVERIFIED',
  pairing_approvals: [{ project_id: project, device_id: remote, state: 'APPROVED' }],
  network_observation: { source: 'SYNTHETIC_DEMO', interfaces: [], default_gateways: [], wan_visible_ip: { state: 'UNKNOWN', source: 'SYNTHETIC_DEMO', value: null }, mappings: [] },
  firewall_observation: { state: 'UNKNOWN', profiles: [], tcp_rules: { allow: 'UNKNOWN', block: 'UNKNOWN' }, udp_rules: { allow: 'UNKNOWN', block: 'UNKNOWN' }, third_party_products: 'UNKNOWN' },
  page: { offset: 0, has_more: false, projects: [card()] },
  jobs: state === 'getting' ? [{ job_id: 'demo-get', project_id: project, label: "Get collaborator's version", running: true, outcome: null, error: null, completed_at: null }]
    : got ? [{ job_id: 'demo-get', project_id: project, label: "Get collaborator's version", running: false, outcome: { transfer_id: 'demo-transfer' }, error: null, completed_at: now() }]
    : [],
  checks: [],
  project_backends: { [project]: { backend: 'SUPABASE', supabase_url: 'https://synthetic-demo.supabase.co', supabase_anon_key: null } },
  default_supabase: null, supabase_states: { [project]: 'MEMBER' }, invite_pending: false, invite_needs_service_fields: false,
  upnp_mapping_asked: true, manual_public_endpoint: null,
});

export async function invoke<T>(command: string): Promise<T> {
  if (command === 'get_status') return status() as T;
  if (command === 'set_language') return undefined as T;
  throw new Error('Static synthetic demo: actions are disabled.');
}
