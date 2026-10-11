import { computed, inject, Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { User } from './models';

const TOKEN_KEY = 'tbs.access';
const REFRESH_KEY = 'tbs.refresh';

/**
 * JWT auth state. Tokens live in localStorage for scaffold simplicity;
 * move to httpOnly cookies (Django session auth) before any real deployment.
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);

  readonly accessToken = signal<string | null>(localStorage.getItem(TOKEN_KEY));
  readonly user = signal<User | null>(null);
  readonly isLoggedIn = computed(() => this.accessToken() !== null);
  readonly isStaff = computed(() => {
    const role = this.user()?.role;
    return role === 'admin' || role === 'planner' || role === 'instructor';
  });

  async login(username: string, password: string): Promise<void> {
    const resp = await firstValueFrom(
      this.http.post<{ access: string; refresh: string }>('/api/auth/token/', { username, password })
    );
    this.setTokens(resp.access, resp.refresh);
    await this.loadMe();
  }

  async loadMe(): Promise<void> {
    if (!this.isLoggedIn()) return;
    this.user.set(await firstValueFrom(this.http.get<User>('/api/auth/me/')));
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    this.accessToken.set(null);
    this.user.set(null);
  }

  private setTokens(access: string, refresh: string): void {
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
    this.accessToken.set(access);
  }
}
