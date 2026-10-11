import { Routes } from '@angular/router';
import { authGuard, staffGuard } from './core/auth.guard';

// Map-heavy routes are lazy-loaded so MapLibre stays out of the initial
// bundle (login screen must load fast on training-room networks).
export const routes: Routes = [
  { path: 'login', loadComponent: () => import('./features/login/login.component').then((m) => m.LoginComponent) },
  { path: '', loadComponent: () => import('./features/planner/planner.component').then((m) => m.PlannerComponent), canActivate: [staffGuard] },
  { path: 'instructor', loadComponent: () => import('./features/instructor/instructor.component').then((m) => m.InstructorComponent), canActivate: [staffGuard] },
  { path: 'aar', loadComponent: () => import('./features/aar/aar.component').then((m) => m.AarComponent), canActivate: [authGuard] },
  { path: '**', redirectTo: '' },
];
