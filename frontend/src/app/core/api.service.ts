import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { AarEvent, Battlespace, GeoJsonGeometry, Scenario, ScenarioEntity, SimSession } from './models';

/** Thin typed wrapper over the Django REST API. */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);

  // --- battlespaces ---
  listBattlespaces(): Observable<{ results: Battlespace[] }> {
    return this.http.get<{ results: Battlespace[] }>('/api/battlespaces/');
  }

  createBattlespace(name: string, aoi: GeoJsonGeometry): Observable<Battlespace> {
    return this.http.post<Battlespace>('/api/battlespaces/', { name, description: '', aoi });
  }

  // --- scenarios ---
  listScenarios(battlespaceId?: string): Observable<{ results: Scenario[] }> {
    const url = battlespaceId ? `/api/scenarios/?battlespace=${battlespaceId}` : '/api/scenarios/';
    return this.http.get<{ results: Scenario[] }>(url);
  }

  createScenario(battlespaceId: string, name: string): Observable<Scenario> {
    return this.http.post<Scenario>('/api/scenarios/', {
      battlespace: battlespaceId,
      name,
      environment: { timeOfDay: '06:30', weather: 'clear' },
    });
  }

  publishScenario(id: string): Observable<Scenario> {
    return this.http.post<Scenario>(`/api/scenarios/${id}/publish/`, {});
  }

  // --- entities ---
  createEntity(entity: Partial<ScenarioEntity> & { scenario: string; position: GeoJsonGeometry }): Observable<ScenarioEntity> {
    return this.http.post<ScenarioEntity>('/api/scenario-entities/', entity);
  }

  // --- sessions ---
  listSessions(): Observable<{ results: SimSession[] }> {
    return this.http.get<{ results: SimSession[] }>('/api/sessions/');
  }

  launchSession(scenarioId: string): Observable<SimSession> {
    return this.http.post<SimSession>('/api/sessions/', { scenario: scenarioId });
  }

  sessionAction(id: string, action: 'start' | 'pause' | 'resume' | 'end'): Observable<SimSession> {
    return this.http.post<SimSession>(`/api/sessions/${id}/${action}/`, {});
  }

  // --- AAR ---
  listEvents(sessionId: string): Observable<{ results: AarEvent[] }> {
    return this.http.get<{ results: AarEvent[] }>(`/api/aar-events/?session=${sessionId}`);
  }
}
