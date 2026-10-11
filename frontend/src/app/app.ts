import { Component, inject } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { AuthService } from './core/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  template: `
    <nav>
      <span class="brand">TBS</span>
      @if (auth.isLoggedIn()) {
        <a routerLink="/">Planner</a>
        @if (auth.isStaff()) {
          <a routerLink="/instructor">Instructor</a>
        }
        <a routerLink="/aar">AAR</a>
        <span class="spacer"></span>
        <span class="who">{{ auth.user()?.username }} ({{ auth.user()?.role }})</span>
        <button (click)="logout()">Sign out</button>
      } @else {
        <a routerLink="/login">Sign in</a>
      }
    </nav>
    <router-outlet />
  `,
  styles: [`
    nav {
      display: flex; align-items: center; gap: 16px;
      padding: 10px 16px; background: #0f172a; color: #e2e8f0; height: 32px;
    }
    .brand { font-weight: 700; letter-spacing: .06em; }
    a { color: #cbd5e1; text-decoration: none; font-size: 14px; }
    a:hover { color: #fff; }
    .spacer { flex: 1; }
    .who { font-size: 13px; color: #94a3b8; }
    button { padding: 4px 10px; border: 0; border-radius: 6px; background: #334155; color: #fff; cursor: pointer; font-size: 13px; }
  `],
})
export class App {
  readonly auth = inject(AuthService);

  constructor() {
    this.auth.loadMe();
  }

  logout(): void {
    this.auth.logout();
    location.assign('/login');
  }
}
