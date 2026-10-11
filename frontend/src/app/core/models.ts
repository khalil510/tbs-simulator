// Types mirroring the Django REST API.

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'planner' | 'instructor' | 'trainee';
  organization: number | null;
  organization_name?: string;
}

export interface LngLat {
  lon: number;
  lat: number;
  alt?: number;
}

export interface GeoJsonGeometry {
  type: string;
  coordinates: unknown;
}

export interface Battlespace {
  id: string;
  name: string;
  description: string;
  aoi: GeoJsonGeometry | null;
  terrain_source: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export type ScenarioStatus = 'draft' | 'validated' | 'published';

export interface Scenario {
  id: string;
  battlespace: string;
  battlespace_name?: string;
  name: string;
  version: number;
  status: ScenarioStatus;
  environment: Record<string, unknown>;
  entities?: ScenarioEntity[];
  objectives?: unknown[];
  updated_at: string;
}

export interface ScenarioEntity {
  id: string;
  client_id: string;
  kind: 'infantry-soldier' | 'infantry-squad' | 'team' | 'spawn-point' | 'marker';
  side: 'blue' | 'red' | 'green' | 'neutral';
  position: GeoJsonGeometry;
  heading_deg: number;
  composition: Record<string, unknown>;
  waypoints: { lat: number; lon: number; speedMs?: number; action?: string }[];
}

export interface SimSession {
  id: string;
  scenario: string;
  scenario_name?: string;
  state: 'lobby' | 'running' | 'paused' | 'ended';
  instructor_name?: string;
  created_at: string;
}

export interface AarEvent {
  id: number;
  session: string;
  t: number;
  entity_id: string;
  kind: string;
  payload: Record<string, unknown>;
}
