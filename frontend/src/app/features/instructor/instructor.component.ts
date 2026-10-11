import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/api.service';
import { Scenario, SimSession } from '../../core/models';

/** Live session control: launch published scenarios, start/pause/end sessions. */
@Component({
  selector: 'tbs-instructor',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="wrap">
      <section>
        <h2>Launch a published scenario</h2>
        <select [(ngModel)]="scenarioId">
          <option [ngValue]="null">-- select --</option>
          @for (s of publishedScenarios(); track s.id) {
            <option [value]="s.id">{{ s.name }} (v{{ s.version }})</option>
          }
        </select>
        <button (click)="launch()" [disabled]="!scenarioId">Launch session</button>
      </section>

      <section>
        <h2>Sessions</h2>
        <table>
          <thead>
            <tr><th>Scenario</th><th>State</th><th>Instructor</th><th>Actions</th></tr>
          </thead>
          <tbody>
            @for (s of sessions(); track s.id) {
              <tr>
                <td>{{ s.scenario_name }}</td>
                <td><span class="pill" [class]="s.state">{{ s.state }}</span></td>
                <td>{{ s.instructor_name }}</td>
                <td class="actions">
                  <button (click)="act(s, 'start')" [disabled]="s.state !== 'lobby'">start</button>
                  <button (click)="act(s, 'pause')" [disabled]="s.state !== 'running'">pause</button>
                  <button (click)="act(s, 'resume')" [disabled]="s.state !== 'paused'">resume</button>
                  <button class="danger" (click)="act(s, 'end')" [disabled]="s.state === 'ended'">end</button>
                </td>
              </tr>
            }
          </tbody>
        </table>
        @if (message()) { <p class="msg">{{ message() }}</p> }
      </section>
    </div>
  `,
  styles: [`
    .wrap { padding: 20px; display: flex; flex-direction: column; gap: 24px; }
    section { display: flex; flex-direction: column; gap: 8px; max-width: 800px; }
    h2 { font-size: 15px; margin: 0; }
    select { max-width: 320px; padding: 7px; }
    button { padding: 6px 12px; border: 0; border-radius: 6px; background: #2563eb; color: #fff; cursor: pointer; }
    button:disabled { opacity: .4; }
    button.danger { background: #dc2626; }
    table { border-collapse: collapse; }
    th, td { text-align: left; padding: 6px 12px 6px 0; font-size: 14px; }
    .pill { padding: 2px 8px; border-radius: 999px; font-size: 12px; background: #e2e8f0; }
    .pill.running { background: #dcfce7; }
    .pill.paused { background: #fef9c3; }
    .pill.ended { background: #fee2e2; }
    .msg { color: #047857; font-size: 13px; }
  `],
})
export class InstructorComponent {
  private readonly api = inject(ApiService);

  sessions = signal<SimSession[]>([]);
  publishedScenarios = signal<Scenario[]>([]);
  scenarioId: string | null = null;
  message = signal('');

  constructor() {
    this.refresh();
    this.api.listScenarios().subscribe((r) =>
      this.publishedScenarios.set(r.results.filter((s) => s.status === 'published'))
    );
  }

  refresh(): void {
    this.api.listSessions().subscribe((r) => this.sessions.set(r.results));
  }

  launch(): void {
    if (!this.scenarioId) return;
    this.api.launchSession(this.scenarioId).subscribe({
      next: (s) => {
        this.sessions.update((list) => [s, ...list]);
        this.message.set(`Session ${s.id.slice(0, 8)}… created (lobby).`);
      },
      error: (err) => this.message.set(`Launch failed: ${JSON.stringify(err.error ?? err).slice(0, 160)}`),
    });
  }

  act(session: SimSession, action: 'start' | 'pause' | 'resume' | 'end'): void {
    this.api.sessionAction(session.id, action).subscribe({
      next: (updated) => {
        this.sessions.update((list) => list.map((s) => (s.id === updated.id ? updated : s)));
      },
      error: (err) => this.message.set(`${action} failed: ${JSON.stringify(err.error ?? err).slice(0, 160)}`),
    });
  }
}
