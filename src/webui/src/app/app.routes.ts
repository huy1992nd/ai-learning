import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/landing-page/landing-page').then(
        (m) => m.LandingPage,
      ),
  },
  {
    path: 'appointment/register',
    loadComponent: () =>
      import('./features/appointment-register/appointment-register.component').then(
        (m) => m.AppointmentRegisterComponent,
      ),
  },
  {
    path: 'admin',
    loadChildren: () =>
      import('./features/admin/admin.routes').then((m) => m.adminRoutes),
  },
  { path: '**', redirectTo: '' },
];
