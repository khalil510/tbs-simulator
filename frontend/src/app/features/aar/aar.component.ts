import { Component, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe, JsonPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { SimSession } from '../../core/models';

/** After-action review: pick a session, inspect its event log.
 *  The animated map replay is milestone M5; v0.1 shows the raw timeline. */
@Component({
  selector: 'tbs-aar',
  standalone: true,
  imports: [FormsModule, DatePipe, DecimalPipe, JsonPipe],
  template: `
    <div class="wrap">
      <section>
        <h2>After-action review</h2>
        <select [(ngModel)]="sessionId" (ngModelChange)="loadEvents()">
          <option [ngValue]="null">-- select session --</option>
          @for (s of sessions(); track s.id) {
            <option [value]="s.id">{{ s.scenario_name }} — {{ s.state }} ({{ s.created_at | date: 'short' }})</option>
          }
        </select>
      </section>

      @if (events().length; as count) {
        <section>
          <h2>{{ count }} events</h2>
          <table>
            <thead><tr><th>t (s)</th><th>entity</th><th>kind</th><th>payload</th></tr></thead>
            <tbody>
              @for (e of events(); track e.id) {
                <tr>
                  <td>{{ e.t | number: '1.1-1' }}</td>
                  <td>{{ e.entity_id }}</td>
                  <td>{{ e.kind }}</td>
                  <td class="payload">{{ e.payload | json }}</td>
                </tr>
              }
            </tbody>
          </table>
        </section>
      } @else if (sessionId) {
        <p>No telemetry recorded for this session yet (the UE5 server posts events to /aar/ingest/).</p>
      }
    </div>
  `,
  styles: [`
    .wrap { padding: 20px; display: flex; flex-direction: column; gap: 18px; }
    section { display: flex; flex-direction: column; gap: 8px; }
    h2 { font-size: 15px; margin: 0; }
    select { max-width: 420px; padding: 7px; }
    table { border-collapse: collapse; font-size: 13px; }
    th, td { text-align: left; padding: 4px 12px 4px 0; }
    .payload { color: #64748b; max-width: 480px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  `],
})
export class AarComponent {
  private readonly api = inject(ApiService);

  sessions = signal<SimSession[]>([]);
  events = signal<{ id: number; t: number; entity_id: string; kind: string; payload: Record<string, unknown> }[]>([]);
  sessionId: string | null = null;

  constructor() {
    this.api.listSessions().subscribe((r) => this.sessions.set(r.results));
  }

  loadEvents(): void {
    if (!this.sessionId) {
      this.events.set([]);
      return;
    }
    this.api.listEvents(this.sessionId).subscribe((r) => this.events.set(r.results));
  }
}
