import { Component, inject, signal, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { Battlespace, Scenario, ScenarioEntity } from '../../core/models';
import { MapComponent } from '../../shared/map/map.component';

type Mode = 'aoi' | 'entity';

/**
 * Scenario planner: draw an AOI polygon, place entities, publish.
 * Autosave of full editor state is milestone M1 polish; v0.1 saves on button press.
 */
@Component({
  selector: 'tbs-planner',
  standalone: true,
  imports: [FormsModule, MapComponent],
  template: `
    <div class="planner">
      <aside class="panel">
        <section>
          <h2>Battlespace</h2>
          <input placeholder="New battlespace name" [(ngModel)]="newBsName" />
          <button (click)="createBattlespace()" [disabled]="!newBsName">Create</button>
          <select [(ngModel)]="selectedBsId" (ngModelChange)="loadScenarios()">
            <option [ngValue]="null">-- select --</option>
            @for (bs of battlespaces(); track bs.id) {
              <option [value]="bs.id">{{ bs.name }}</option>
            }
          </select>
        </section>

        <section>
          <h2>Mode</h2>
          <label><input type="radio" value="aoi" [(ngModel)]="mode" /> Draw AOI</label>
          <label><input type="radio" value="entity" [(ngModel)]="mode" /> Place entity</label>
          @if (mode === 'entity') {
            <label>Side
              <select [(ngModel)]="entitySide">
                <option value="blue">blue</option>
                <option value="red">red</option>
                <option value="green">green</option>
                <option value="neutral">neutral</option>
              </select>
            </label>
            <label>Kind
              <select [(ngModel)]="entityKind">
                <option value="infantry-squad">infantry-squad</option>
                <option value="infantry-soldier">infantry-soldier</option>
                <option value="team">team</option>
                <option value="spawn-point">spawn-point</option>
                <option value="marker">marker</option>
              </select>
            </label>
          }
          @if (mode === 'aoi' && aoiVertices().length >= 3) {
            <button (click)="finishAoi()">Finish AOI ({{ aoiVertices().length }} vertices)</button>
          }
        </section>

        <section>
          <h2>Scenario</h2>
          <input placeholder="New scenario name" [(ngModel)]="newScenarioName" />
          <button (click)="createScenario()" [disabled]="!selectedBsId || !newScenarioName">Create</button>
          <select [(ngModel)]="selectedScenarioId" (ngModelChange)="selectScenario()">
            <option [ngValue]="null">-- select --</option>
            @for (s of scenarios(); track s.id) {
              <option [value]="s.id">{{ s.name }} (v{{ s.version }}, {{ s.status }})</option>
            }
          </select>
          @if (selectedScenario(); as scenario) {
            <button (click)="publishScenario()" [disabled]="scenario.status === 'published'">
              Publish scenario
            </button>
          }
        </section>

        @if (message()) { <p class="msg">{{ message() }}</p> }
      </aside>

      <tbs-map class="map" (mapClick)="onMapClick($event)" [aoi]="aoiGeometry()" />
    </div>
  `,
  styles: [`
    .planner { display: flex; height: calc(100vh - 52px); }
    .panel { width: 300px; padding: 12px; overflow-y: auto; border-right: 1px solid #e2e8f0; display: flex; flex-direction: column; gap: 18px; }
    section { display: flex; flex-direction: column; gap: 8px; }
    h2 { font-size: 13px; text-transform: uppercase; color: #64748b; margin: 0; }
    input, select { padding: 7px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; }
    button { padding: 8px; border: 0; border-radius: 6px; background: #2563eb; color: #fff; cursor: pointer; font-size: 13px; }
    button:disabled { opacity: .5; }
    .map { flex: 1; }
    .msg { font-size: 13px; color: #047857; }
  `],
})
export class PlannerComponent {
  private readonly api = inject(ApiService);
  @ViewChild(MapComponent) map?: MapComponent;

  battlespaces = signal<Battlespace[]>([]);
  scenarios = signal<Scenario[]>([]);
  selectedBsId: string | null = null;
  selectedScenarioId: string | null = null;
  selectedScenario = signal<Scenario | null>(null);

  newBsName = '';
  newScenarioName = '';
  mode: Mode = 'aoi';
  entitySide: ScenarioEntity['side'] = 'blue';
  entityKind: ScenarioEntity['kind'] = 'infantry-squad';

  aoiVertices = signal<{ lon: number; lat: number }[]>([]);
  aoiGeometry = signal<{ type: string; coordinates: unknown } | null>(null);
  message = signal('');

  constructor() {
    this.api.listBattlespaces().subscribe((r) => this.battlespaces.set(r.results));
  }

  createBattlespace(): void {
    this.api.createBattlespace(this.newBsName, this.aoiGeometry() ?? { type: 'Polygon', coordinates: [[]] }).subscribe({
      next: (bs) => {
        this.battlespaces.update((list) => [bs, ...list]);
        this.selectedBsId = bs.id;
        this.newBsName = '';
        this.message.set(`Battlespace "${bs.name}" created.`);
      },
      error: () => this.message.set('Failed to create battlespace (draw an AOI first in a later build; empty polygon accepted now).'),
    });
  }

  loadScenarios(): void {
    if (!this.selectedBsId) return;
    this.api.listScenarios(this.selectedBsId).subscribe((r) => this.scenarios.set(r.results));
  }

  createScenario(): void {
    if (!this.selectedBsId) return;
    this.api.createScenario(this.selectedBsId, this.newScenarioName).subscribe((s) => {
      this.scenarios.update((list) => [s, ...list]);
      this.newScenarioName = '';
      this.selectedScenarioId = s.id;
      this.selectedScenario.set(s);
      this.message.set(`Scenario "${s.name}" created.`);
    });
  }

  selectScenario(): void {
    const found = this.scenarios().find((s) => s.id === this.selectedScenarioId) ?? null;
    this.selectedScenario.set(found);
  }

  publishScenario(): void {
    const scenario = this.selectedScenario();
    if (!scenario) return;
    this.api.publishScenario(scenario.id).subscribe({
      next: (s) => {
        this.scenarios.update((list) => list.map((x) => (x.id === s.id ? s : x)));
        this.selectedScenario.set(s);
        this.message.set(`Published "${s.name}" v${s.version}.`);
      },
      error: (err) => this.message.set(`Publish failed: ${JSON.stringify(err.error?.errors ?? err.error ?? err).slice(0, 200)}`),
    });
  }

  onMapClick(pos: { lon: number; lat: number }): void {
    if (this.mode === 'aoi') {
      this.aoiVertices.update((v) => [...v, pos]);
      this.map?.addPreviewPoint(pos.lon, pos.lat, '#3b82f6');
      return;
    }
    // place entity in the selected scenario
    const scenario = this.selectedScenario();
    if (!scenario) {
      this.message.set('Select a scenario before placing entities.');
      return;
    }
    this.api.createEntity({
      scenario: scenario.id,
      kind: this.entityKind,
      side: this.entitySide,
      position: { type: 'Point', coordinates: [pos.lon, pos.lat] },
    }).subscribe({
      next: (e) => {
        const color = { blue: '#2563eb', red: '#dc2626', green: '#16a34a', neutral: '#64748b' }[e.side];
        this.map?.addPreviewPoint(pos.lon, pos.lat, color);
        this.message.set(`Placed ${e.client_id} (${e.kind}/${e.side}).`);
      },
      error: () => this.message.set('Failed to place entity.'),
    });
  }

  finishAoi(): void {
    const ring = this.aoiVertices().map((p) => [p.lon, p.lat]);
    ring.push([...ring[0]]);
    this.aoiGeometry.set({ type: 'Polygon', coordinates: [ring] });
    this.message.set(`AOI set (${ring.length - 1} vertices).`);
  }
}
