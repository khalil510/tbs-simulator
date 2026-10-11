import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'tbs-login',
  standalone: true,
  imports: [FormsModule],
  template: `
    <form class="login" (ngSubmit)="submit()">
      <h1>Tactical Battlespace Simulator</h1>
      <label>
        Username
        <input name="username" [(ngModel)]="username" autocomplete="username" required />
      </label>
      <label>
        Password
        <input name="password" type="password" [(ngModel)]="password" autocomplete="current-password" required />
      </label>
      @if (error()) {
        <p class="error">{{ error() }}</p>
      }
      <button type="submit" [disabled]="busy()">Sign in</button>
      <p class="hint">No account? Ask an administrator to create one in Django admin (/admin/).</p>
    </form>
  `,
  styles: [`
    .login { max-width: 340px; margin: 12vh auto; display: flex; flex-direction: column; gap: 12px; }
    label { display: flex; flex-direction: column; gap: 4px; font-size: 14px; }
    input { padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; }
    button { padding: 10px; border-radius: 6px; border: 0; background: #2563eb; color: #fff; cursor: pointer; }
    button:disabled { opacity: .6; }
    .error { color: #dc2626; font-size: 14px; }
    .hint { color: #64748b; font-size: 12px; }
  `],
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  username = '';
  password = '';
  busy = signal(false);
  error = signal<string | null>(null);

  async submit(): Promise<void> {
    this.busy.set(true);
    this.error.set(null);
    try {
      await this.auth.login(this.username, this.password);
      this.router.navigateByUrl('/');
    } catch {
      this.error.set('Invalid credentials.');
    } finally {
      this.busy.set(false);
    }
  }
}
